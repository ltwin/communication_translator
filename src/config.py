# -*- coding: utf-8 -*-
"""
配置管理模块

负责加载和管理应用程序配置，包括 API Key、模型设置等。
所有敏感配置通过环境变量加载。
"""

import os
import logging
from functools import lru_cache

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 环境检测：dev/prod/test
_ENV = os.getenv("ENV", "prod").lower()

# 根据环境设置默认日志级别
def _get_log_level() -> str:
    """获取日志级别，优先使用环境变量，否则根据 ENV 设置默认值"""
    explicit_level = os.getenv("LOG_LEVEL")
    if explicit_level:
        return explicit_level.upper()
    # dev 环境默认 DEBUG，其他环境默认 INFO
    return "DEBUG" if _ENV == "dev" else "INFO"

# 配置日志
logging.basicConfig(
    level=_get_log_level(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class Settings:
    """应用程序配置类"""

    # 运行环境: dev/prod/test
    ENV: str = _ENV

    # DeepSeek API 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # 服务配置
    PORT: int = int(os.getenv("PORT", "8080"))
    LOG_LEVEL: str = _get_log_level()

    # 输入验证配置
    CONTENT_MIN_LENGTH: int = 10
    CONTENT_MAX_LENGTH: int = 2000

    # AI 服务超时配置 (秒)
    AI_TIMEOUT: int = 30

    # 应用版本
    VERSION: str = "1.0.0"

    def validate(self) -> bool:
        """验证必需配置是否已设置"""
        if not self.DEEPSEEK_API_KEY:
            logger.error("DEEPSEEK_API_KEY is not configured")
            return False
        return True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    settings = Settings()
    if not settings.validate():
        logger.warning("Configuration validation failed - API Key not set")
    return settings
