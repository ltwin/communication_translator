# -*- coding: utf-8 -*-
"""
翻译服务模块

负责调用 DeepSeek API 进行双向翻译，支持流式输出。
"""

import logging
import asyncio
from typing import AsyncGenerator
from functools import lru_cache

from openai import OpenAIError, APIConnectionError, AuthenticationError, RateLimitError

from src.config import get_settings
from src.prompts import get_system_prompt
from src.models import TranslationDirection
from src.clients import get_deepseek_client

logger = logging.getLogger(__name__)


class Translator:
    """翻译服务类"""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """初始化翻译器

        Args:
            api_key: DeepSeek API Key，默认从配置读取
            base_url: API 基础 URL，默认从配置读取
            model: 模型名称，默认从配置读取
        """
        settings = get_settings()
        self.model = model or settings.deepseek_model
        self.timeout = settings.ai_timeout

        # 使用共享的 DeepSeek 客户端
        deepseek_client = get_deepseek_client()
        self.client = deepseek_client.get_client()
        logger.info(f"Translator initialized, model={self.model}")

    async def translate_stream(
        self,
        content: str,
        direction: TranslationDirection
    ) -> AsyncGenerator[str, None]:
        """流式翻译

        Args:
            content: 待翻译的内容
            direction: 翻译方向

        Yields:
            翻译结果的文本片段，最后一个为 [DONE] 或 [ERROR] 标记
        """
        logger.info(f"Translation started, direction={direction.value}, content_length={len(content)}")

        try:
            # 获取对应方向的系统提示词
            system_prompt = get_system_prompt(direction.value)

            # 调用 DeepSeek API（OpenAI 兼容接口），设置超时
            stream = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content}
                    ],
                    stream=True,
                ),
                timeout=self.timeout
            )

            # 流式输出
            chunk_count = 0
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    chunk_count += 1
                    yield text

            # 完成标记
            logger.info(f"Translation completed successfully, chunks_sent={chunk_count}")
            yield "[DONE]"

        except AuthenticationError as e:
            logger.error(f"Authentication failed, api_key_valid=false, error={str(e)}")
            yield "[ERROR] API Key 无效，请检查配置"

        except RateLimitError as e:
            logger.warning(f"Rate limit exceeded, error={str(e)}")
            yield "[ERROR] 请求过于频繁，请稍后重试"

        except APIConnectionError as e:
            logger.error(f"API connection failed, error={str(e)}")
            yield "[ERROR] 网络连接异常，请检查网络后重试"

        except asyncio.TimeoutError:
            logger.error(f"Translation request timed out, timeout_seconds={self.timeout}")
            yield "[ERROR] AI 服务响应超时，请稍后重试"

        except OpenAIError as e:
            error_msg = str(e)
            logger.error(f"OpenAI API error, error_type={type(e).__name__}, error={error_msg}")
            yield "[ERROR] AI 服务暂时不可用，请稍后重试"

        except Exception as e:
            logger.exception(f"Unexpected error during translation, error_type={type(e).__name__}, error={str(e)}")
            yield "[ERROR] 翻译过程中发生错误，请稍后重试"


@lru_cache()
def get_translator() -> Translator:
    """获取翻译器实例（单例模式）"""
    return Translator()
