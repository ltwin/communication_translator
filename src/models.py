# -*- coding: utf-8 -*-
"""
数据模型模块

定义 API 请求/响应的 Pydantic 数据模型。
"""

from enum import Enum
from pydantic import BaseModel, Field


class TranslationDirection(str, Enum):
    """翻译方向枚举"""
    PRODUCT_TO_DEV = "product_to_dev"    # 产品需求 → 技术语言
    DEV_TO_PRODUCT = "dev_to_product"    # 技术方案 → 业务语言


class TranslateRequest(BaseModel):
    """翻译请求模型"""
    content: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="待翻译的原始内容"
    )
    direction: TranslationDirection = Field(
        ...,
        description="翻译方向"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "我们需要一个智能推荐功能，提升用户停留时长",
                    "direction": "product_to_dev"
                },
                {
                    "content": "我们优化了数据库查询，QPS提升了30%",
                    "direction": "dev_to_product"
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str = Field(..., description="用户友好的错误描述")
    error_code: str = Field(..., description="错误代码")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "请输入需要翻译的内容",
                    "error_code": "EMPTY_CONTENT"
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="API 版本号")
