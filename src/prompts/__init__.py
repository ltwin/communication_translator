# -*- coding: utf-8 -*-
"""提示词模块"""

from src.prompts.templates import (
    INTENT_ROUTER_PROMPT,
    PRODUCT_TO_DEV_PROMPT,
    DEV_TO_PRODUCT_PROMPT,
    get_system_prompt,
)

__all__ = [
    "INTENT_ROUTER_PROMPT",
    "PRODUCT_TO_DEV_PROMPT",
    "DEV_TO_PRODUCT_PROMPT",
    "get_system_prompt",
]
