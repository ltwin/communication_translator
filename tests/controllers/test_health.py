# -*- coding: utf-8 -*-
"""
健康检查控制器测试
"""

import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app


class TestHealthEndpoint:
    """健康检查接口测试"""

    @pytest.mark.asyncio
    async def test_health_check_returns_healthy(self):
        """测试健康检查返回正常状态"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_health_check_returns_version(self):
        """测试健康检查返回版本号"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/health")

        data = response.json()
        assert data["version"] == "1.0.0"
