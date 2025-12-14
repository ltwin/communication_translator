# -*- coding: utf-8 -*-
"""
FastAPI 应用入口模块

提供 Web API 服务，包括翻译接口和静态文件服务。
"""

import json
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models import HealthResponse, TranslateRequest, ErrorResponse
from .translator import get_translator
from .router import get_intent_router

# 获取配置
settings = get_settings()

# 配置日志
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Application starting up")
    logger.info(f"Version: {settings.VERSION}")
    if not settings.DEEPSEEK_API_KEY:
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
    version=settings.VERSION,
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

# 静态文件目录
STATIC_DIR = Path(__file__).parent.parent / "static"

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


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health_check():
    """健康检查接口"""
    logger.info("Health check requested")
    return HealthResponse(
        status="healthy",
        version=settings.VERSION
    )


@app.post("/api/translate", tags=["translate"])
async def translate(request: TranslateRequest):
    """执行翻译（流式输出）

    将输入内容根据指定方向进行翻译，返回 Server-Sent Events 流式响应。

    流式数据格式：
    - 元数据（智能模式）: `data: [META] {"detected_direction": "...", "confidence": 0.92}\\n\\n`
    - 正常数据: `data: <text_chunk>\\n\\n`
    - 结束标记: `data: [DONE]\\n\\n`
    - 错误标记: `data: [ERROR] <message>\\n\\n`
    """
    # 检查 API Key 配置
    if not settings.DEEPSEEK_API_KEY:
        logger.error("API Key not configured")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                detail="服务配置错误，请联系管理员",
                error_code="AI_SERVICE_ERROR"
            ).model_dump()
        )

    # 确定翻译方向
    direction = request.direction
    intent_meta = None  # 用于存储意图识别元数据

    # 智能模式：当 auto_detect=True 且 direction=None 时，调用意图识别
    if request.auto_detect and request.direction is None:
        logger.info("Auto-detect mode enabled, detecting intent...")
        intent_router = get_intent_router()
        intent_result = await intent_router.detect_intent(request.content)

        # 检查置信度
        if intent_result.confidence < 0.5:
            # 置信度过低，返回错误提示用户手动选择
            logger.warning(f"Intent detection confidence too low: {intent_result.confidence}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    detail=f"无法确定内容类型（置信度: {intent_result.confidence:.0%}），请手动选择翻译方向",
                    error_code="LOW_CONFIDENCE"
                ).model_dump()
            )

        direction = intent_result.direction
        intent_meta = {
            "detected_direction": direction.value,
            "confidence": intent_result.confidence,
            "reasoning": intent_result.reasoning
        }
        logger.info(f"Intent detected: {direction.value}, confidence: {intent_result.confidence:.2f}")

    logger.info(f"Translation request received, direction: {direction.value}, auto_detect: {request.auto_detect}")

    # 获取翻译器并执行流式翻译
    translator = get_translator()

    async def generate_sse():
        """生成 SSE 格式的流式响应"""
        # 如果是智能模式，先发送元数据
        if intent_meta:
            yield f"data: [META] {json.dumps(intent_meta, ensure_ascii=False)}\n\n"

            # 中等置信度时添加提示
            if intent_meta["confidence"] < 0.8:
                yield "data: > ⚠️ 系统自动识别翻译方向，如有误请手动选择\n\n"
                yield "data: \n\n"

        # 流式翻译输出
        async for chunk in translator.translate_stream(request.content, direction):
            yield f"data: {chunk}\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )
