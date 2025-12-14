# -*- coding: utf-8 -*-
"""
请求模型单元测试
"""

import pytest

from src.models import TranslateRequest, TranslationDirection


class TestTranslateRequest:
    """TranslateRequest 模型测试"""

    def test_valid_request_with_direction(self):
        """测试有效的请求（指定方向）"""
        request = TranslateRequest(
            content="这是一段足够长的测试内容，用于验证请求模型",
            direction=TranslationDirection.PRODUCT_TO_DEV,
            auto_detect=False
        )
        assert request.content == "这是一段足够长的测试内容，用于验证请求模型"
        assert request.direction == TranslationDirection.PRODUCT_TO_DEV
        assert request.auto_detect is False

    def test_valid_request_with_auto_detect(self):
        """测试有效的请求（自动检测模式）"""
        request = TranslateRequest(
            content="这是一段足够长的测试内容，用于验证请求模型",
            auto_detect=True
        )
        assert request.auto_detect is True
        assert request.direction is None

    def test_invalid_content_too_short(self):
        """测试内容过短应该失败"""
        with pytest.raises(ValueError):
            TranslateRequest(
                content="太短了",
                direction=TranslationDirection.PRODUCT_TO_DEV,
                auto_detect=False
            )

    def test_invalid_missing_direction_without_auto_detect(self):
        """测试缺少方向且未启用自动检测应该失败"""
        with pytest.raises(ValueError):
            TranslateRequest(
                content="这是一段足够长的测试内容，用于验证请求模型",
                auto_detect=False
            )

    def test_direction_enum_values(self):
        """测试翻译方向枚举值"""
        assert TranslationDirection.PRODUCT_TO_DEV.value == "product_to_dev"
        assert TranslationDirection.DEV_TO_PRODUCT.value == "dev_to_product"
