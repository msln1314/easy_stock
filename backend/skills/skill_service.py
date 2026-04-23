"""
Skills服务
管理Skills的发现、匹配和执行
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger

from .base_skill import BaseSkill, discover_skills


class SkillService:
    """Skills管理服务"""

    def __init__(self, skills_dir: str = None):
        """
        初始化Skills服务

        Args:
            skills_dir: Skills目录路径，默认为backend/skills
        """
        if skills_dir is None:
            # 获取backend目录下的skills目录
            backend_dir = Path(__file__).parent.parent
            skills_dir = str(backend_dir / "skills")

        self.skills_dir = skills_dir
        self.skills: Dict[str, BaseSkill] = {}
        self._initialized = False

    def discover_skills(self) -> None:
        """
        发现并加载所有Skills
        """
        skills = discover_skills(self.skills_dir)

        for skill in skills:
            self.skills[skill.name] = skill
            logger.info(f"加载Skill: {skill.name} - {skill.description}")

        self._initialized = True
        logger.info(f"Skills服务初始化完成，共加载 {len(self.skills)} 个技能")

    def match_skill(self, message: str) -> Optional[BaseSkill]:
        """
        根据消息匹配Skill

        Args:
            message: 用户消息

        Returns:
            匹配的Skill，无匹配返回None
        """
        if not self._initialized:
            self.discover_skills()

        # 按优先级匹配（可以扩展为按匹配度排序）
        for skill in self.skills.values():
            if skill.matches(message):
                logger.info(f"消息匹配Skill: {skill.name}")
                return skill

        return None

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """
        获取指定名称的Skill

        Args:
            name: Skill名称

        Returns:
            Skill对象，不存在返回None
        """
        return self.skills.get(name)

    def list_skills(self) -> List[Dict[str, Any]]:
        """
        获取所有Skills列表

        Returns:
            Skills信息列表
        """
        if not self._initialized:
            self.discover_skills()

        return [skill.to_dict() for skill in self.skills.values()]

    def get_all_tools_for_skill(self, skill_name: str, all_tools: List[Dict]) -> List[Dict]:
        """
        获取指定Skill关联的工具

        Args:
            skill_name: Skill名称
            all_tools: 所有工具定义

        Returns:
            该Skill的工具列表
        """
        skill = self.get_skill(skill_name)
        if skill:
            return skill.get_tools(all_tools)
        return all_tools

    def get_system_prompt_for_skill(self, skill_name: str) -> str:
        """
        获取指定Skill的系统提示词

        Args:
            skill_name: Skill名称

        Returns:
            系统提示词
        """
        skill = self.get_skill(skill_name)
        if skill:
            return skill.get_system_prompt()
        # 默认提示词
        return """你是一个专业的股票交易助手。你可以帮助用户：
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


# 全局Skills服务实例
skill_service = SkillService()