"""
系统监控接口测试
"""
import pytest
import requests
from tests.config import BASE_URL
from tests.auth_test_helper import AuthTestHelper


class TestMonitorAPI:
    """系统监控接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_status_endpoint_exists(self, session):
        """GET /api/v1/monitor/status 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/monitor/status")
        assert resp.status_code in [200, 401, 403]

    def test_health_endpoint_exists(self, session):
        """GET /api/v1/monitor/health 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/monitor/health")
        assert resp.status_code in [200, 401, 403]

    def test_metrics_endpoint_exists(self, session):
        """GET /api/v1/monitor/metrics 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/monitor/metrics")
        assert resp.status_code in [200, 401, 403]

    def test_logs_endpoint_exists(self, session):
        """GET /api/v1/monitor/logs 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/monitor/logs")
        assert resp.status_code in [200, 401, 403]

    def test_performance_endpoint_exists(self, session):
        """GET /api/v1/monitor/performance 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/monitor/performance")
        assert resp.status_code in [200, 401, 403]

    # ===== 鉴权测试 =====

    def test_status_requires_auth(self, helper):
        """获取系统状态需要登录"""
        resp = helper.test_public_endpoint("/api/v1/monitor/status")
        assert resp.status_code == 401

    def test_status_with_token(self, helper, admin_token):
        """有token可以获取系统状态"""
        resp = helper.test_auth_endpoint("/api/v1/monitor/status", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_health_requires_auth(self, helper):
        """获取健康检查需要登录"""
        resp = helper.test_public_endpoint("/api/v1/monitor/health")
        assert resp.status_code == 401

    def test_health_with_token(self, helper, admin_token):
        """有token可以获取健康检查"""
        resp = helper.test_auth_endpoint("/api/v1/monitor/health", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_metrics_requires_auth(self, helper):
        """获取系统指标需要登录"""
        resp = helper.test_public_endpoint("/api/v1/monitor/metrics")
        assert resp.status_code == 401

    def test_metrics_with_token(self, helper, admin_token):
        """有token可以获取系统指标"""
        resp = helper.test_auth_endpoint("/api/v1/monitor/metrics", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_logs_requires_auth(self, helper):
        """获取系统日志需要登录"""
        resp = helper.test_public_endpoint("/api/v1/monitor/logs")
        assert resp.status_code == 401

    def test_logs_with_token(self, helper, admin_token):
        """有token可以获取系统日志"""
        resp = helper.test_auth_endpoint("/api/v1/monitor/logs", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_performance_requires_auth(self, helper):
        """获取性能指标需要登录"""
        resp = helper.test_public_endpoint("/api/v1/monitor/performance")
        assert resp.status_code == 401

    def test_performance_with_token(self, helper, admin_token):
        """有token可以获取性能指标"""
        resp = helper.test_auth_endpoint("/api/v1/monitor/performance", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)