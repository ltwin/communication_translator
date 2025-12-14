# -*- coding: utf-8 -*-
"""
意图路由器单元测试
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.intent_router import IntentRouter, IntentResult, get_intent_router
from src.models import TranslationDirection


class TestIntentResult:
    """IntentResult 模型测试"""

    def test_valid_intent_result(self):
        """测试有效的意图识别结果"""
        result = IntentResult(
            direction=TranslationDirection.PRODUCT_TO_DEV,
            confidence=0.92,
            reasoning="包含业务需求描述"
        )
        assert result.direction == TranslationDirection.PRODUCT_TO_DEV
        assert result.confidence == 0.92
        assert result.reasoning == "包含业务需求描述"

    def test_confidence_bounds(self):
        """测试置信度边界值"""
        # 最小值
        result_min = IntentResult(
            direction=TranslationDirection.DEV_TO_PRODUCT,
            confidence=0.0,
            reasoning=""
        )
        assert result_min.confidence == 0.0

        # 最大值
        result_max = IntentResult(
            direction=TranslationDirection.DEV_TO_PRODUCT,
            confidence=1.0,
            reasoning=""
        )
        assert result_max.confidence == 1.0

    def test_invalid_confidence_below_zero(self):
        """测试置信度低于0应该失败"""
        with pytest.raises(ValueError):
            IntentResult(
                direction=TranslationDirection.PRODUCT_TO_DEV,
                confidence=-0.1,
                reasoning=""
            )

    def test_invalid_confidence_above_one(self):
        """测试置信度高于1应该失败"""
        with pytest.raises(ValueError):
            IntentResult(
                direction=TranslationDirection.PRODUCT_TO_DEV,
                confidence=1.1,
                reasoning=""
            )


class TestIntentRouter:
    """IntentRouter 类测试"""

    @pytest.mark.asyncio
    async def test_detect_intent_product_to_dev(self):
        """测试识别产品需求"""
        router = IntentRouter(api_key="test-key")

        # Mock LLM 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "direction": "product_to_dev",
            "confidence": 0.95,
            "reasoning": "内容描述了用户需求和业务目标"
        }
        '''

        with patch.object(router.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await router.detect_intent("我们需要一个智能推荐功能，提升用户停留时长")

            assert result.direction == TranslationDirection.PRODUCT_TO_DEV
            assert result.confidence == 0.95
            assert "用户需求" in result.reasoning or "业务目标" in result.reasoning

    @pytest.mark.asyncio
    async def test_detect_intent_dev_to_product(self):
        """测试识别技术方案"""
        router = IntentRouter(api_key="test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "direction": "dev_to_product",
            "confidence": 0.88,
            "reasoning": "内容涉及技术实现和性能指标"
        }
        '''

        with patch.object(router.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await router.detect_intent("我们优化了数据库索引，查询QPS提升了30%")

            assert result.direction == TranslationDirection.DEV_TO_PRODUCT
            assert result.confidence == 0.88

    @pytest.mark.asyncio
    async def test_detect_intent_with_markdown_json(self):
        """测试解析带 markdown 代码块的 JSON 响应"""
        router = IntentRouter(api_key="test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        ```json
        {
            "direction": "product_to_dev",
            "confidence": 0.75,
            "reasoning": "混合内容，但偏向业务描述"
        }
        ```
        '''

        with patch.object(router.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await router.detect_intent("测试内容")

            assert result.direction == TranslationDirection.PRODUCT_TO_DEV
            assert result.confidence == 0.75

    @pytest.mark.asyncio
    async def test_detect_intent_invalid_json(self):
        """测试处理无效 JSON 响应"""
        router = IntentRouter(api_key="test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这不是有效的JSON"

        with patch.object(router.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await router.detect_intent("测试内容")

            # 应该返回默认值，低置信度
            assert result.direction == TranslationDirection.PRODUCT_TO_DEV
            assert result.confidence == 0.3
            assert "无法解析" in result.reasoning

    @pytest.mark.asyncio
    async def test_detect_intent_api_error(self):
        """测试处理 API 错误"""
        router = IntentRouter(api_key="test-key")

        from openai import OpenAIError

        with patch.object(router.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = OpenAIError("API connection failed")

            result = await router.detect_intent("测试内容")

            # 应该返回默认值，零置信度
            assert result.direction == TranslationDirection.PRODUCT_TO_DEV
            assert result.confidence == 0.0
            assert "API 错误" in result.reasoning

    @pytest.mark.asyncio
    async def test_detect_intent_clamps_confidence(self):
        """测试置信度被限制在 0-1 范围内"""
        router = IntentRouter(api_key="test-key")

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''
        {
            "direction": "product_to_dev",
            "confidence": 1.5,
            "reasoning": "超出范围的置信度"
        }
        '''

        with patch.object(router.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_response

            result = await router.detect_intent("测试内容")

            # 置信度应该被限制为 1.0
            assert result.confidence == 1.0


class TestGetIntentRouter:
    """get_intent_router 单例测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        # 清除缓存
        get_intent_router.cache_clear()

        router1 = get_intent_router()
        router2 = get_intent_router()

        assert router1 is router2
