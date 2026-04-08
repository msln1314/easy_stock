"""
前端TypeScript API解析器
"""
import os
import re
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FrontendAPIInfo:
    """前端API信息"""
    function_name: str
    backend_path: str
    method: str
    file_name: str
    params: List[str]

class FrontendParser:
    """解析前端API模块文件"""

    def __init__(self, frontend_api_dir: str = "frontend/src/api"):
        self.frontend_api_dir = frontend_api_dir

    def parse_single_file(self, file_path: str) -> List[FrontendAPIInfo]:
        """解析单个TypeScript API文件"""
        apis = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return apis

        # 匹配request.get/post/put/delete/patch调用
        pattern = r"request\.(get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]"
        matches = re.findall(pattern, content)

        for method, path in matches:
            # 从上下文提取函数名
            func_pattern = rf'export\s+(?:async\s+)?function\s+(\w+)\s*\([^}]*request\.{method}\s*\(\s*[\'"`]{re.escape(path)}[\'"`]'
            func_match = re.search(func_pattern, content)
            func_name = func_match.group(1) if func_match else f"{method}_{path.replace('/', '_')}"

            apis.append(FrontendAPIInfo(
                function_name=func_name,
                backend_path=path,
                method=method.upper(),
                file_name=os.path.basename(file_path),
                params=[]
            ))

        return apis

    def extract_all_frontend_apis(self) -> Dict[str, List[FrontendAPIInfo]]:
        """扫描所有前端API文件"""
        all_apis = {}

        if not os.path.exists(self.frontend_api_dir):
            return all_apis

        for file_name in os.listdir(self.frontend_api_dir):
            if file_name.endswith('.ts'):
                file_path = os.path.join(self.frontend_api_dir, file_name)
                apis = self.parse_single_file(file_path)
                if apis:
                    all_apis[file_name] = apis

        return all_apis

    def get_all_api_paths(self) -> List[tuple]:
        """获取所有前端调用的路径"""
        all_apis = self.extract_all_frontend_apis()
        paths = []

        for file_name, apis in all_apis.items():
            for api in apis:
                paths.append((api.backend_path, api.method, api.function_name, file_name))

        return paths