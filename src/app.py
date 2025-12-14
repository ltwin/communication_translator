# -*- coding: utf-8 -*-
"""
FastAPI 应用入口模块

提供 Web API 服务，包括翻译接口和静态文件服务。
"""

import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.controllers import health_router, translate_router

# 获取配置
settings = get_settings()

# 配置日志
logger = logging.getLogger(__name__)

# 静态文件目录
STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Application starting up")
    logger.info(f"Version: {settings.version}")
    logger.info(f"Environment: {settings.env}, Log Level: {settings.get_log_level()}")
    if not settings.deepseek_api_key:
        logger.warning("DEEPSEEK_API_KEY is not configured - translation will fail")
    else:
        logger.info("API Key configured successfully")

    yield

    # 关闭时
    logger.info("Application shutting down")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="沟通翻译助手 API",
    description="帮助产品经理和开发工程师相互理解的 AI 翻译服务",
    version=settings.version,
    lifespan=lifespan,
)

# 配置 CORS（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册控制器路由
app.include_router(health_router)
app.include_router(translate_router)

# 挂载静态文件服务（如果目录存在）
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """首页 - 返回前端页面"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Welcome to Communication Translator API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    is_dev = settings.env == "dev"

    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=settings.port,
        reload=is_dev,
        log_level=settings.get_log_level().lower(),
    )
