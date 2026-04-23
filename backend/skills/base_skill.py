"""
Skill基类定义
定义Skill的标准结构和行为
"""
import os
import re
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class BaseSkill:
    """Skill基类"""
    name: str
    description: str
    trigger_keywords: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    workflow: str = ""
    file_path: str = ""

    def matches(self, message: str) -> bool:
        """
        检查消息是否匹配该Skill的触发关键词

        Args:
            message: 用户消息

        Returns:
            是否匹配
        """
        message_lower = message.lower()
        for keyword in self.trigger_keywords:
            if keyword.lower() in message_lower:
                return True
        return False

    def get_tools(self, all_tools: List[Dict]) -> List[Dict]:
        """
        获取该Skill关联的工具定义

        Args:
            all_tools: 所有可用工具的完整定义

        Returns:
            该Skill需要的工具列表
        """
        # 如果没有指定工具，返回所有工具
        if not self.tools:
            return all_tools

        # 过滤出该Skill需要的工具
        tool_names = set(self.tools)
        return [t for t in all_tools if t.get("function", {}).get("name") in tool_names]

    def get_system_prompt(self) -> str:
        """
        获取该Skill的系统提示词

        Returns:
            系统提示词
        """
        base_prompt = """你是一个专业的股票交易助手。你可以帮助用户：
1. 查询股票行情（如：平安银行现在多少钱）
2. 查看持仓（如：我的持仓）
3. 查看账户资金（如：账户余额）
4. 买入股票（如：买入平安银行100股）
5. 卖出股票（如：卖出000001的100股）

注意事项：
- 买入数量必须是100的整数倍
- 交易时间：工作日9:30-11:30, 13:00-15:00
- 如果用户没有指定价格，买入默认使用涨停价（快速成交），卖出使用跌停价
- 股票代码6开头是上海，0/3开头是深圳

请用简洁的中文回复。"""

        # 如果有workflow，添加workflow指导
        if self.workflow:
            skill_prompt = f"\n\n当前激活技能：{self.name}\n描述：{self.description}\n\n执行流程：\n{self.workflow}"
            return base_prompt + skill_prompt

        return base_prompt

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "trigger_keywords": self.trigger_keywords,
            "tools": self.tools,
            "workflow": self.workflow,
            "file_path": self.file_path
        }


def parse_skill_file(file_path: str) -> Optional[BaseSkill]:
    """
    解析SKILL.md文件

    Args:
        file_path: SKILL.md文件路径

    Returns:
        解析后的Skill对象，失败返回None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析YAML frontmatter
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return None

        frontmatter = yaml.safe_load(match.group(1))
        workflow_content = match.group(2).strip()

        skill = BaseSkill(
            name=frontmatter.get("name", ""),
            description=frontmatter.get("description", ""),
            trigger_keywords=frontmatter.get("trigger_keywords", []),
            tools=frontmatter.get("tools", []),
            workflow=workflow_content,
            file_path=file_path
        )

        return skill

    except Exception as e:
        print(f"解析Skill文件失败: {file_path}, {e}")
        return None


def discover_skills(skills_dir: str) -> List[BaseSkill]:
    """
    发现并加载所有Skill

    Args:
        skills_dir: Skills目录路径

    Returns:
        发现的Skill列表
    """
    skills = []
    skills_path = Path(skills_dir)

    if not skills_path.exists():
        return skills

    # 遍历所有子目录，查找SKILL.md文件
    for item in skills_path.iterdir():
        if item.is_dir():
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                skill = parse_skill_file(str(skill_file))
                if skill:
                    skills.append(skill)

    return skills