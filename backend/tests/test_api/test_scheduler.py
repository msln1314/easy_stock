"""
调度器接口测试
"""
import pytest
import requests
from test_config import BASE_URL
from auth_test_helper import AuthTestHelper


class TestSchedulerAPI:
    """调度器接口测试"""

    @pytest.fixture
    def helper(self, session):
        return AuthTestHelper(session)

    # ===== 连通性测试 =====

    def test_list_endpoint_exists(self, session):
        """GET /api/v1/scheduler 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/scheduler")
        assert resp.status_code in [200, 401, 403]

    def test_create_endpoint_exists(self, session):
        """POST /api/v1/scheduler 接口存在"""
        resp = session.post(
            f"{BASE_URL}/api/v1/scheduler",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403]

    def test_get_endpoint_exists(self, session):
        """GET /api/v1/scheduler/{id} 接口存在"""
        resp = session.get(f"{BASE_URL}/api/v1/scheduler/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_update_endpoint_exists(self, session):
        """PUT /api/v1/scheduler/{id} 接口存在"""
        resp = session.put(
            f"{BASE_URL}/api/v1/scheduler/1",
            json={}
        )
        assert resp.status_code in [200, 400, 401, 403, 404]

    def test_delete_endpoint_exists(self, session):
        """DELETE /api/v1/scheduler/{id} 接口存在"""
        resp = session.delete(f"{BASE_URL}/api/v1/scheduler/1")
        assert resp.status_code in [200, 401, 403, 404]

    def test_run_endpoint_exists(self, session):
        """POST /api/v1/scheduler/{id}/run 接口存在"""
        resp = session.post(f"{BASE_URL}/api/v1/scheduler/1/run")
        assert resp.status_code in [200, 401, 403, 404]

    def test_pause_endpoint_exists(self, session):
        """POST /api/v1/scheduler/{id}/pause 接口存在"""
        resp = session.post(f"{BASE_URL}/api/v1/scheduler/1/pause")
        assert resp.status_code in [200, 401, 403, 404]

    def test_resume_endpoint_exists(self, session):
        """POST /api/v1/scheduler/{id}/resume 接口存在"""
        resp = session.post(f"{BASE_URL}/api/v1/scheduler/1/resume")
        assert resp.status_code in [200, 401, 403, 404]

    # ===== 鉴权测试 =====

    def test_list_requires_auth(self, helper):
        """获取调度任务列表需要登录"""
        resp = helper.test_public_endpoint("/api/v1/scheduler")
        assert resp.status_code == 401

    def test_list_with_token(self, helper, admin_token):
        """有token可以获取调度任务列表"""
        resp = helper.test_auth_endpoint("/api/v1/scheduler", admin_token)
        assert resp.status_code == 200
        assert helper.validate_response_structure(resp)

    def test_create_requires_auth(self, helper):
        """创建调度任务需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/scheduler",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_create_with_token(self, helper, admin_token):
        """有token可以创建调度任务"""
        resp = helper.test_auth_endpoint(
            "/api/v1/scheduler",
            admin_token,
            method="POST",
            data={"name": "test_job", "cron": "0 0 * * *"}
        )
        assert resp.status_code in [200, 400, 403]

    def test_get_requires_auth(self, helper):
        """获取单个调度任务需要登录"""
        resp = helper.test_public_endpoint("/api/v1/scheduler/1")
        assert resp.status_code == 401

    def test_update_requires_auth(self, helper):
        """更新调度任务需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/scheduler/1",
            method="PUT",
            data={}
        )
        assert resp.status_code == 401

    def test_delete_requires_auth(self, helper):
        """删除调度任务需要登录"""
        resp = helper.test_public_endpoint("/api/v1/scheduler/1", method="DELETE")
        assert resp.status_code == 401

    def test_run_requires_auth(self, helper):
        """运行调度任务需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/scheduler/1/run",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_pause_requires_auth(self, helper):
        """暂停调度任务需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/scheduler/1/pause",
            method="POST",
            data={}
        )
        assert resp.status_code == 401

    def test_resume_requires_auth(self, helper):
        """恢复调度任务需要登录"""
        resp = helper.test_public_endpoint(
            "/api/v1/scheduler/1/resume",
            method="POST",
            data={}
        )
        assert resp.status_code == 401