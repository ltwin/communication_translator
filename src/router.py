# -*- coding: utf-8 -*-
"""
意图路由器模块

负责分析用户输入内容，判断其属于「产品需求描述」还是「技术方案描述」，
并返回识别结果和置信度。
"""

import json
import logging
from functools import lru_cache
from typing import Optional

from openai import AsyncOpenAI, OpenAIError
from pydantic import BaseModel, Field

from .config import get_settings
from .prompts import INTENT_ROUTER_PROMPT
from .models import TranslationDirection

logger = logging.getLogger(__name__)


class IntentResult(BaseModel):
    """意图识别结果模型"""
    direction: TranslationDirection = Field(
        ...,
        description="识别出的翻译方向"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="置信度分数 (0.0 - 1.0)"
    )
    reasoning: str = Field(
        default="",
        description="判断依据说明"
    )


class IntentRouter:
    """意图路由器类

    使用 LLM 分析用户输入内容，判断其类型并返回识别结果。
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """初始化意图路由器

        Args:
            api_key: DeepSeek API Key，默认从配置读取
            base_url: API 基础 URL，默认从配置读取
            model: 模型名称，默认从配置读取
        """
        settings = get_settings()
        self.api_key = api_key or settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.DEEPSEEK_MODEL
        self.timeout = settings.AI_TIMEOUT

        # 初始化 OpenAI 兼容客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        logger.info(f"IntentRouter initialized, model={self.model}")

    async def detect_intent(self, content: str) -> IntentResult:
        """检测用户输入内容的意图

        Args:
            content: 用户输入的原始内容

        Returns:
            IntentResult: 包含翻译方向、置信度和判断依据的结果

        Raises:
            ValueError: 当 LLM 返回的结果无法解析时
        """
        logger.info(f"Intent detection started, content_length={len(content)}")

        try:
            # 调用 LLM 进行意图识别（非流式）
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": INTENT_ROUTER_PROMPT},
                    {"role": "user", "content": content}
                ],
                stream=False,
                temperature=0.1,  # 低温度以获得更稳定的分类结果
            )

            # 提取响应内容
            result_text = response.choices[0].message.content.strip()
            logger.debug(f"LLM response: {result_text}")

            # 解析 JSON 响应
            intent_result = self._parse_response(result_text)
            logger.info(
                f"Intent detected, direction={intent_result.direction.value}, "
                f"confidence={intent_result.confidence:.2f}"
            )
            return intent_result

        except OpenAIError as e:
            logger.error(f"LLM API error during intent detection: {str(e)}")
            # 返回默认结果，低置信度
            return IntentResult(
                direction=TranslationDirection.PRODUCT_TO_DEV,
                confidence=0.0,
                reasoning=f"API 错误，无法识别意图: {str(e)}"
            )
        except Exception as e:
            logger.exception(f"Unexpected error during intent detection: {str(e)}")
            return IntentResult(
                direction=TranslationDirection.PRODUCT_TO_DEV,
                confidence=0.0,
                reasoning=f"识别失败: {str(e)}"
            )

    def _parse_response(self, response_text: str) -> IntentResult:
        """解析 LLM 返回的 JSON 响应

        Args:
            response_text: LLM 返回的原始文本

        Returns:
            IntentResult: 解析后的意图识别结果
        """
        try:
            # 尝试提取 JSON（处理可能的 markdown 代码块包裹）
            json_text = response_text
            if "```json" in response_text:
                json_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_text = response_text.split("```")[1].split("```")[0].strip()

            data = json.loads(json_text)

            # 验证并转换 direction
            direction_str = data.get("direction", "product_to_dev")
            if direction_str == "product_to_dev":
                direction = TranslationDirection.PRODUCT_TO_DEV
            elif direction_str == "dev_to_product":
                direction = TranslationDirection.DEV_TO_PRODUCT
            else:
                logger.warning(f"Unknown direction '{direction_str}', defaulting to product_to_dev")
                direction = TranslationDirection.PRODUCT_TO_DEV

            # 获取置信度，确保在有效范围内
            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))

            # 获取判断依据
            reasoning = str(data.get("reasoning", ""))

            return IntentResult(
                direction=direction,
                confidence=confidence,
                reasoning=reasoning
            )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {str(e)}, response: {response_text[:200]}")
            # 返回默认结果，低置信度
            return IntentResult(
                direction=TranslationDirection.PRODUCT_TO_DEV,
                confidence=0.3,
                reasoning="无法解析 LLM 响应，使用默认方向"
            )


@lru_cache()
def get_intent_router() -> IntentRouter:
    """获取意图路由器实例（单例模式）"""
    return IntentRouter()
