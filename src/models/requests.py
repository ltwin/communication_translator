# -*- coding: utf-8 -*-
"""
API 请求模型模块

定义 API 请求的 Pydantic 数据模型。
"""

from typing import Optional
from pydantic import BaseModel, Field, model_validator

from src.models.enums import TranslationDirection


class TranslateRequest(BaseModel):
    """翻译请求模型"""
    content: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="待翻译的原始内容"
    )
    direction: Optional[TranslationDirection] = Field(
        None,
        description="翻译方向，为空时根据 auto_detect 决定行为"
    )
    auto_detect: bool = Field(
        False,
        description="是否启用智能意图识别"
    )

    @model_validator(mode='after')
    def validate_direction_or_auto_detect(self):
        """验证：auto_detect=False 时 direction 必填"""
        if not self.auto_detect and self.direction is None:
            raise ValueError("当 auto_detect 为 false 时，必须指定 direction")
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "我们需要一个智能推荐功能，提升用户停留时长",
                    "direction": "product_to_dev",
                    "auto_detect": False
                },
                {
                    "content": "我们优化了数据库查询，QPS提升了30%",
                    "direction": "dev_to_product",
                    "auto_detect": False
                },
                {
                    "content": "我们需要一个实时聊天功能，支持万人在线",
                    "auto_detect": True
                }
            ]
        }
    }
