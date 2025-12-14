# -*- coding: utf-8 -*-
"""
DeepSeek API 客户端模块

封装异步 OpenAI 兼容客户端，为翻译和意图识别服务提供统一的 API 调用接口。
"""

import logging
from functools import lru_cache

from openai import AsyncOpenAI

from src.config import get_settings

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """DeepSeek API 客户端类

    封装 OpenAI 兼容的异步客户端，提供配置管理和客户端实例。
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """初始化 DeepSeek 客户端

        Args:
            api_key: DeepSeek API Key，默认从配置读取
            base_url: API 基础 URL，默认从配置读取
            model: 模型名称，默认从配置读取
        """
        settings = get_settings()
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.DEEPSEEK_MODEL
        self.timeout = settings.AI_TIMEOUT

        # 初始化 OpenAI 兼容客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        logger.info(f"DeepSeekClient initialized, model={self.model}, base_url={self.base_url}")

    def get_client(self) -> AsyncOpenAI:
        """获取底层 AsyncOpenAI 客户端实例"""
        return self.client


@lru_cache()
def get_deepseek_client() -> DeepSeekClient:
    """获取 DeepSeek 客户端实例（单例模式）"""
    return DeepSeekClient()
