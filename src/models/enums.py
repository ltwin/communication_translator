# -*- coding: utf-8 -*-
"""
枚举定义模块

定义业务相关的枚举类型。
"""

from enum import Enum


class TranslationDirection(str, Enum):
    """翻译方向枚举"""
    PRODUCT_TO_DEV = "product_to_dev"    # 产品需求 → 技术语言
    DEV_TO_PRODUCT = "dev_to_product"    # 技术方案 → 业务语言
