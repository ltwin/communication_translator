# -*- coding: utf-8 -*-
"""
健康检查控制器

提供服务健康状态检查的 API 端点。
"""

import logging

from fastapi import APIRouter

from src.config import get_settings
from src.models import HealthResponse

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api", tags=["health"])

# 获取配置
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        version=settings.VERSION
    )
