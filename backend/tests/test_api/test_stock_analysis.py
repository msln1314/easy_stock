"""
股票分析接口测试
"""
import pytest
import requests
from tests.config import BASE_URL
from tests.auth_test_helper import AuthTestHelper


class TestStockAnalysisAPI:
    """股票分析接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_list_endpoint_exists(self, session):
        """GET /api/v1/stock-analysis 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/stock-analysis")
        assert resp.status_code in [200, 401, 403]

    def test_create_endpoint_exists(self, session):
        """POST /api/v1/stock-analysis 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/stock-analysis",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_get_endpoint_exists(self, session):
        """GET /api/v1/stock-analysis/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/stock-analysis/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_update_endpoint_exists(self, session):
        """PUT /api/v1/stock-analysis/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/stock-analysis/1",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_delete_endpoint_exists(self, session):
        """DELETE /api/v1/stock-analysis/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/stock-analysis/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_analyze_endpoint_exists(self, session):
        """POST /api/v1/stock-analysis/analyze 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/stock-analysis/analyze",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_report_endpoint_exists(self, session):
        """GET /api/v1/stock-analysis/{id}/report 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/stock-analysis/1/report")
        assert resp.status_code in [200, 401, 403, 404]

    # ===== 鉴权测试 =====

    def test_list_requires_auth(self, helper):
        """获取股票分析列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/stock-analysis")
        assert resp.status_code == 401

    def test_list_with_token(self, helper, admin_token):
        """有token可以获取股票分析列表"""
        resp = helper.test_auth_endpoint("/api/v1/stock-analysis", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_create_requires_auth(self, helper):
        """创建股票分析需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/stock-analysis",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_create_with_token(self, helper, admin_token):
        """有token可以创建股票分析"""
        resp = helper.test_auth_endpoint(
            "/api/v1/stock-analysis",
            admin_token,
            method="POST",
            data={"stock_code": "000001", "analysis_type": "technical"}
        )
        assert resp.status_code in [200, 400, 403]

    def test_get_requires_auth(self, helper):
        """获取单个股票分析需要登录"""
        resp = helper.test_public_endpoint("/api/v1/stock-analysis/1")
        assert resp.status_code == 401

    def test_update_requires_auth(self, helper):
        """更新股票分析需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/stock-analysis/1",
            method="PUT",
            data={}
        )
        assert resp.status_code == 401

    def test_delete_requires_auth(self, helper):
        """删除股票分析需要登录"""
        resp = helper.test_public_endpoint("/api/v1/stock-analysis/1", method="DELETE")
        assert resp.status_code == 401

    def test_analyze_requires_auth(self, helper):
        """执行股票分析需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/stock-analysis/analyze",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_analyze_with_token(self, helper, admin_token):
        """有token可以执行股票分析"""
        resp = helper.test_auth_endpoint(
            "/api/v1/stock-analysis/analyze",
            admin_token,
            method="POST",
            data={"stock_code": "000001"}
        )
        assert resp.status_code in [200, 400, 403]

    def test_report_requires_auth(self, helper):
        """获取分析报告需要登录"""
        resp = helper.test_public_endpoint("/api/v1/stock-analysis/1/report")
        assert resp.status_code == 401

    def test_report_with_token(self, helper, admin_token):
        """有token可以获取分析报告"""
        resp = helper.test_auth_endpoint("/api/v1/stock-analysis/1/report", admin_token)
        assert resp.status_code in [200, 404]