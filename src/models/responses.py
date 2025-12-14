# -*- coding: utf-8 -*-
"""
API 响应模型模块

定义 API 响应的 Pydantic 数据模型。
"""

from pydantic import BaseModel, Field


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
