"""
前后端接口对比验证器
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
from tests.api_extractor import APIExtractor, APIInfo, AuthLevel
from tests.frontend_parser import FrontendParser, FrontendAPIInfo

@dataclass
class ComparisonResult:
    """对比结果"""
    backend_path: str
    backend_method: str
    frontend_path: str
    frontend_func: str
    frontend_file: str
    match_status: str  # "matched", "mismatch_path", "mismatch_method", "missing_frontend", "missing_backend"
    auth_level: AuthLevel
    note: str

class InterfaceValidator:
    """前后端接口对比验证"""

    def __init__(self, backend_url: str, frontend_dir: str):
        self.api_extractor = APIExtractor(backend_url)
        self.frontend_parser = FrontendParser(frontend_dir)

    def normalize_path(self, path: str) -> str:
        """标准化路径，去除baseURL差异"""
        # 前端路径通常以/v1开头，后端以/api/v1开头
        if path.startswith("/api/v1"):
            return path.replace("/api/v1", "/v1")
        return path

    def compare_backend_frontend(self) -> List[ComparisonResult]:
        """对比前后端接口定义"""
        backend_apis = self.api_extractor.extract_all_apis()
        frontend_apis = self.frontend_parser.get_all_api_paths()

        results = []

        # 构建前端路径映射
        frontend_map = {}
        for path, method, func_name, file_name in frontend_apis:
            normalized_path = self.normalize_path(path)
            frontend_map[(normalized_path, method)] = (func_name, file_name, path)

        # 构建后端路径映射
        backend_map = {}
        for api in backend_apis:
            normalized_path = self.normalize_path(api.path)
            backend_map[(normalized_path, api.method)] = api

        # 对比每个后端接口
        for api in backend_apis:
            normalized_backend_path = self.normalize_path(api.path)
            key = (normalized_backend_path, api.method)

            if key in frontend_map:
                func_name, file_name, original_frontend_path = frontend_map[key]
                results.append(ComparisonResult(
                    backend_path=api.path,
                    backend_method=api.method,
                    frontend_path=original_frontend_path,
                    frontend_func=func_name,
                    frontend_file=file_name,
                    match_status="matched",
                    auth_level=api.auth_level,
                    note="✅ 完全匹配"
                ))
            else:
                # 后端有但前端没有
                results.append(ComparisonResult(
                    backend_path=api.path,
                    backend_method=api.method,
                    frontend_path="-",
                    frontend_func="-",
                    frontend_file="-",
                    match_status="missing_frontend",
                    auth_level=api.auth_level,
                    note="⚠️ 前端未调用此接口"
                ))

        # 检查前端有但后端没有的接口
        for path, method, func_name, file_name in frontend_apis:
            normalized_frontend_path = self.normalize_path(path)
            key = (normalized_frontend_path, method)

            if key not in backend_map:
                results.append(ComparisonResult(
                    backend_path="-",
                    backend_method="-",
                    frontend_path=path,
                    frontend_func=func_name,
                    frontend_file=file_name,
                    match_status="missing_backend",
                    auth_level=AuthLevel.PUBLIC,
                    note="⚠️ 后端未实现此接口"
                ))

        return results

    def generate_html_report(self, results: List[ComparisonResult], output_path: str):
        """生成HTML对比报告"""
        # 统计
        matched_count = sum(1 for r in results if r.match_status == "matched")
        mismatch_count = sum(1 for r in results if "mismatch" in r.match_status)
        missing_frontend_count = sum(1 for r in results if r.match_status == "missing_frontend")
        missing_backend_count = sum(1 for r in results if r.match_status == "missing_backend")

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>前后端接口对比报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 10px; text-align: left; }}
        th {{ background: #34495e; color: white; }}
        .matched {{ background-color: #d4edda; }}
        .mismatch {{ background-color: #f8d7da; }}
        .missing-frontend {{ background-color: #fff3cd; }}
        .missing-backend {{ background-color: #d1ecf1; }}
    </style>
</head>
<body>
    <h1>前后端接口对比报告</h1>

    <h2>统计摘要</h2>
    <div class="summary">
        <p>后端接口总数: {len(results)}</p>
        <p>完全匹配: {matched_count} ✅</p>
        <p>路径不匹配: {mismatch_count} ❌</p>
        <p>前端缺少对应后端: {missing_frontend_count} ⚠️</p>
        <p>后端未被前端调用: {missing_backend_count} ⚠️</p>
    </div>

    <h2>详细对比结果</h2>
    <table>
        <tr>
            <th>后端路径</th>
            <th>方法</th>
            <th>前端函数</th>
            <th>前端文件</th>
            <th>匹配状态</th>
            <th>鉴权级别</th>
            <th>备注</th>
        </tr>
"""

        for result in results:
            status_class = result.match_status.replace("_", "-")
            auth_display = result.auth_level.value if result.auth_level != AuthLevel.PUBLIC else "-"

            html_content += f"""        <tr class="{status_class}">
            <td>{result.backend_path}</td>
            <td>{result.backend_method}</td>
            <td>{result.frontend_func}</td>
            <td>{result.frontend_file}</td>
            <td>{result.match_status}</td>
            <td>{auth_display}</td>
            <td>{result.note}</td>
        </tr>
"""

        html_content += """    </table>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def run_comparison_and_generate_report(self, output_path: str) -> List[ComparisonResult]:
        """执行对比并生成报告"""
        results = self.compare_backend_frontend()
        self.generate_html_report(results, output_path)
        return results