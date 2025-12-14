# -*- coding: utf-8 -*-
"""
API 集成测试

测试 FastAPI 应用的 HTTP 接口。
"""

import pytest
from httpx import AsyncClient, ASGITransport

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app


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


class TestTranslateEndpointValidation:
    """翻译接口验证测试"""

    @pytest.mark.asyncio
    async def test_translate_empty_content_returns_error(self):
        """测试空内容返回错误"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/translate",
                json={
                    "content": "",
                    "direction": "product_to_dev"
                }
            )

        assert response.status_code == 422  # Pydantic 验证错误

    @pytest.mark.asyncio
    async def test_translate_short_content_returns_error(self):
        """测试过短内容返回错误"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/translate",
                json={
                    "content": "太短了",
                    "direction": "product_to_dev"
                }
            )

        assert response.status_code == 422  # Pydantic 验证错误 (min_length=10)

    @pytest.mark.asyncio
    async def test_translate_invalid_direction_returns_error(self):
        """测试无效翻译方向返回错误"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/translate",
                json={
                    "content": "这是一段足够长的测试内容",
                    "direction": "invalid_direction"
                }
            )

        assert response.status_code == 422  # Pydantic 验证错误

    @pytest.mark.asyncio
    async def test_translate_missing_direction_returns_error(self):
        """测试缺少翻译方向返回错误"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/translate",
                json={
                    "content": "这是一段足够长的测试内容"
                }
            )

        assert response.status_code == 422  # Pydantic 验证错误

    @pytest.mark.asyncio
    async def test_translate_missing_content_returns_error(self):
        """测试缺少内容返回错误"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/translate",
                json={
                    "direction": "product_to_dev"
                }
            )

        assert response.status_code == 422  # Pydantic 验证错误


class TestTranslateEndpointIntegration:
    """翻译接口集成测试

    注意：这些测试依赖于实际的 API 配置。
    如果没有配置 API Key，翻译请求会返回 500 错误或流式错误。
    """

    @pytest.mark.asyncio
    async def test_translate_endpoint_responds(self):
        """测试翻译接口能够响应请求"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/translate",
                json={
                    "content": "我们需要一个智能推荐功能，提升用户停留时长",
                    "direction": "product_to_dev"
                }
            )

        # 接口应该响应（可能是 200 流式响应或 500 配置错误）
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            # 如果成功，应该返回流式响应
            assert "text/event-stream" in response.headers.get("content-type", "")
        else:
            # 如果失败，应该返回错误信息
            data = response.json()
            assert "error_code" in data


class TestRootEndpoint:
    """首页接口测试"""

    @pytest.mark.asyncio
    async def test_root_returns_response(self):
        """测试首页返回响应"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")

        # 应该返回 HTML 页面（static/index.html 存在）
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_root_returns_html(self):
        """测试首页返回 HTML 内容"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")

        # 检查是否包含 HTML 内容
        content = response.text
        assert "<!DOCTYPE html>" in content or "沟通翻译助手" in content
