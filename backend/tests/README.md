# API接口自动化测试框架

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

确保后端服务正在运行:

```bash
cd backend
python main.py
# 或使用已运行的服务 http://localhost:8030
```

### 3. 配置测试账号

编辑 `test_config.py` 修改测试账号配置，确保账号存在:

```python
ADMIN_USERNAME = "admin"      # 管理员账号
ADMIN_PASSWORD = "admin123"   # 管理员密码
```

### 4. 运行测试

```bash
cd backend/tests
PYTHONPATH=. pytest test_api/ --html=reports/test_report.html -v
# 打开 reports/test_report.html 查看测试报告
```

### 5. 运行单个模块测试

```bash
PYTHONPATH=. pytest test_api/test_auth.py -v
```

## 测试配置

编辑 `test_config.py` 修改测试配置:

```python
BASE_URL = "http://localhost:8030"  # 后端服务地址
ADMIN_USERNAME = "admin"            # 管理员账号
ADMIN_PASSWORD = "admin123"         # 管理员密码
```

## 测试类型

每个API模块包含三类测试:

1. **连通性测试** - 验证接口存在且能正常响应
2. **鉴权测试** - 验证PUBLIC/LOGIN_REQUIRED/ADMIN_REQUIRED分级正确
3. **参数验证测试** - 验证必填参数缺失返回400

## 报告说明

### interface_report.html

前后端接口对比报告，显示:
- 完全匹配的接口 ✅
- 路径不匹配的接口 ❌
- 前端未调用的后端接口 ⚠️
- 后端未实现的前端接口 ⚠️

### test_report.html

pytest测试执行报告，显示:
- 测试通过/失败统计
- 每个测试用例的详细结果
- 失败原因和错误堆栈

## 添加新测试

为新API模块添加测试文件:

```python
# backend/tests/test_api/test_new_module.py
import pytest
from tests.auth_test_helper import AuthTestHelper
from tests.config import BASE_URL

class TestNewModuleAPI:
    """新模块接口测试"""

    @pytest.fixture
    def helper(self):
        return AuthTestHelper()

    def test_endpoint_exists(self):
        """验证接口存在"""
        resp = requests.get(f"{BASE_URL}/api/v1/new-module")
        assert resp.status_code in [200, 401, 403, 400]
```

## 问题修复流程

1. 运行测试生成报告
2. 审核报告中的问题
3. 确认需要修复的问题
4. 执行修复
5. 重新运行测试验证

## 维护建议

- 每次新增API接口时，同步添加测试文件
- 定期运行测试，确保接口质量
- 将测试报告纳入版本控制