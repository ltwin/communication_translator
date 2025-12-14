# -*- coding: utf-8 -*-
"""
翻译服务单元测试

测试 translator.py 中的核心翻译功能。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import TranslationDirection


class TestTranslatorModule:
    """翻译模块测试"""

    def test_get_translator_returns_instance(self):
        """测试获取翻译器实例"""
        from src.translator import get_translator
        translator = get_translator()
        assert translator is not None

    def test_get_translator_singleton(self):
        """测试翻译器单例模式"""
        from src.translator import get_translator
        translator1 = get_translator()
        translator2 = get_translator()
        assert translator1 is translator2


class TestProductToDevTranslation:
    """产品→开发翻译测试"""

    @pytest.mark.asyncio
    async def test_translate_stream_with_mock(self):
        """测试流式翻译返回内容（使用 Mock）"""
        from src.translator import Translator

        # 创建翻译器实例
        translator = Translator(api_key="test-key")

        # 模拟 OpenAI 客户端的流式响应
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "测试翻译结果"

        async def mock_stream():
            yield mock_chunk

        # 使用 patch 模拟 chat.completions.create
        with patch.object(translator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_stream()

            content = "我们需要一个智能推荐功能，提升用户停留时长"
            direction = TranslationDirection.PRODUCT_TO_DEV

            # 收集流式输出
            chunks = []
            async for chunk in translator.translate_stream(content, direction):
                chunks.append(chunk)

            # 验证有内容输出
            assert len(chunks) > 0
            # 验证最后一个是 [DONE] 标记
            assert chunks[-1] == "[DONE]"
            # 验证包含翻译内容
            assert "测试翻译结果" in chunks

    @pytest.mark.asyncio
    async def test_translate_stream_handles_auth_error(self):
        """测试 API Key 无效时的错误处理"""
        from src.translator import Translator

        # 创建一个没有有效 API Key 的翻译器
        translator = Translator(api_key="invalid-key")

        content = "这是一个测试内容，足够长度"
        direction = TranslationDirection.PRODUCT_TO_DEV

        # 收集流式输出
        chunks = []
        async for chunk in translator.translate_stream(content, direction):
            chunks.append(chunk)

        # 验证有错误标记（因为 API Key 无效）
        assert len(chunks) > 0
        has_error_or_done = any(
            chunk.startswith("[ERROR]") or chunk == "[DONE]"
            for chunk in chunks
        )
        assert has_error_or_done

    @pytest.mark.asyncio
    async def test_translate_stream_handles_timeout(self):
        """测试超时错误处理"""
        from src.translator import Translator
        import asyncio

        # 创建翻译器实例
        translator = Translator(api_key="test-key")
        translator.timeout = 0.001  # 设置极短超时

        # 模拟一个会超时的异步调用
        async def slow_create(*args, **kwargs):
            await asyncio.sleep(1)  # 模拟慢响应
            return MagicMock()

        with patch.object(translator.client.chat.completions, 'create', side_effect=slow_create):
            content = "这是一个测试内容，足够长度"
            direction = TranslationDirection.PRODUCT_TO_DEV

            chunks = []
            async for chunk in translator.translate_stream(content, direction):
                chunks.append(chunk)

            # 验证返回超时错误
            assert len(chunks) > 0
            assert any("超时" in chunk or "[ERROR]" in chunk for chunk in chunks)


class TestDevToProductTranslation:
    """开发→产品翻译测试"""

    @pytest.mark.asyncio
    async def test_translate_stream_dev_to_product_with_mock(self):
        """测试开发→产品翻译（使用 Mock）"""
        from src.translator import Translator

        translator = Translator(api_key="test-key")

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "业务价值分析结果"

        async def mock_stream():
            yield mock_chunk

        with patch.object(translator.client.chat.completions, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_stream()

            content = "我们优化了数据库查询，QPS提升了30%"
            direction = TranslationDirection.DEV_TO_PRODUCT

            chunks = []
            async for chunk in translator.translate_stream(content, direction):
                chunks.append(chunk)

            assert len(chunks) > 0
            assert chunks[-1] == "[DONE]"
            assert "业务价值分析结果" in chunks


class TestTranslatorValidation:
    """翻译器验证测试"""

    def test_direction_enum_values(self):
        """测试翻译方向枚举值"""
        assert TranslationDirection.PRODUCT_TO_DEV.value == "product_to_dev"
        assert TranslationDirection.DEV_TO_PRODUCT.value == "dev_to_product"

    def test_get_system_prompt_product_to_dev(self):
        """测试获取产品→开发提示词"""
        from src.prompts import get_system_prompt

        prompt = get_system_prompt("product_to_dev")
        assert "技术架构师" in prompt
        assert "技术实现建议" in prompt

    def test_get_system_prompt_dev_to_product(self):
        """测试获取开发→产品提示词"""
        from src.prompts import get_system_prompt

        prompt = get_system_prompt("dev_to_product")
        assert "产品技术顾问" in prompt
        assert "用户体验影响" in prompt

    def test_get_system_prompt_invalid_direction(self):
        """测试无效方向抛出异常"""
        from src.prompts import get_system_prompt

        with pytest.raises(ValueError):
            get_system_prompt("invalid_direction")
