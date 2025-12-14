# -*- coding: utf-8 -*-
"""控制器层：API 路由定义"""

from src.controllers.health import router as health_router
from src.controllers.translate import router as translate_router

__all__ = ["health_router", "translate_router"]
