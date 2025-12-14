# -*- coding: utf-8 -*-
"""
配置管理模块

负责加载和管理应用程序配置，包括 API Key、模型设置等。
配置优先级：YAML 文件 > 环境变量 > 默认值
"""

import logging
from pathlib import Path
from functools import lru_cache
from typing import Any

import yaml
from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

# 项目根目录
_PROJECT_ROOT = Path(__file__).parent.parent


def _read_version() -> str:
    """从 VERSION 文件读取版本号"""
    version_file = _PROJECT_ROOT / "VERSION"
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            version = f.read().strip()
            if version:
                return version
    # 如果文件不存在或为空，返回默认版本
    return "1.0.0"


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """从 YAML 文件加载配置的自定义 Source"""

    def __init__(self, settings_cls: type[BaseSettings]):
        super().__init__(settings_cls)
        self._yaml_data = self._load_yaml()

    def _load_yaml(self) -> dict:
        config_path = _PROJECT_ROOT / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        value = self._yaml_data.get(field_name.upper())
        return value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        return {
            field_name: self._yaml_data[field_name.upper()]
            for field_name in self.settings_cls.model_fields
            if field_name.upper() in self._yaml_data
        }


class Settings(BaseSettings):
    """应用程序配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 运行环境: dev/prod/test
    env: str = Field(default="prod")

    # DeepSeek API 配置
    deepseek_api_key: str = Field(default="")
    deepseek_base_url: str = Field(default="https://api.deepseek.com")
    deepseek_model: str = Field(default="deepseek-chat")

    # 服务配置
    port: int = Field(default=8080)
    log_level: str | None = Field(default=None)

    # 输入验证配置
    content_min_length: int = Field(default=10)
    content_max_length: int = Field(default=2000)

    # AI 服务超时配置 (秒)
    ai_timeout: int = Field(default=30)

    # 应用版本（从 VERSION 文件读取）
    version: str = Field(default_factory=_read_version)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """配置优先级：YAML > .env > 环境变量 > 默认值"""
        return (
            YamlConfigSettingsSource(settings_cls),
            dotenv_settings,
            env_settings,
        )

    def get_log_level(self) -> str:
        """获取日志级别，未设置则根据 ENV 返回默认值"""
        if self.log_level:
            return self.log_level.upper()
        return "DEBUG" if self.env.lower() == "dev" else "INFO"

    def validate_config(self) -> bool:
        """验证必需配置是否已设置"""
        if not self.deepseek_api_key:
            return False
        return True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 配置日志（模块加载时执行）
_settings = get_settings()
logging.basicConfig(
    level=_settings.get_log_level(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if not _settings.validate_config():
    logger.warning("Configuration validation failed - API Key not set")
