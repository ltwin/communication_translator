# 数据模型: 沟通翻译助手

**日期**: 2025-12-14
**功能**: 001-communication-translator

## 概述

本文档定义沟通翻译助手的数据模型。由于是无状态应用，主要定义 API 请求/响应的数据结构。

---

## 核心实体

### 1. TranslationDirection (翻译方向)

表示翻译的源角色和目标角色。

```python
from enum import Enum

class TranslationDirection(str, Enum):
    """翻译方向枚举"""
    PRODUCT_TO_DEV = "product_to_dev"    # 产品→开发
    DEV_TO_PRODUCT = "dev_to_product"    # 开发→产品
```

**属性说明**:
| 值 | 含义 | 提示词策略 |
|----|------|-----------|
| `product_to_dev` | 将产品需求翻译为技术语言 | 技术架构师视角 |
| `dev_to_product` | 将技术方案翻译为业务语言 | 产品顾问视角 |

---

### 2. TranslateRequest (翻译请求)

用户提交的翻译任务。

```python
from pydantic import BaseModel, Field

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
```

**字段说明**:
| 字段 | 类型 | 必需 | 约束 | 说明 |
|------|------|------|------|------|
| `content` | string | 是 | 10-2000字符 | 待翻译的原始内容 |
| `direction` | TranslationDirection | 是 | 枚举值 | 翻译方向 |

**验证规则**:
- `content` 不能为空，最少10个字符，最多2000个字符
- `direction` 必须是有效的枚举值

---

### 3. TranslateResponse (翻译响应)

非流式场景下的完整响应（用于错误情况）。

```python
class TranslateResponse(BaseModel):
    """翻译响应模型（非流式）"""
    success: bool = Field(..., description="是否成功")
    content: str | None = Field(None, description="翻译结果")
    error: str | None = Field(None, description="错误信息")
```

**字段说明**:
| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `success` | bool | 是 | 请求是否成功 |
| `content` | string | 否 | 翻译结果（成功时） |
| `error` | string | 否 | 错误信息（失败时） |

---

### 4. StreamChunk (流式数据块)

SSE 流式输出的数据块格式。

```
data: <text_chunk>\n\n
```

**特殊标记**:
- `[DONE]` - 表示流式输出结束
- `[ERROR]` - 表示发生错误，后跟错误信息

---

### 5. ErrorResponse (错误响应)

API 错误响应格式。

```python
class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str = Field(..., description="错误详情")
    error_code: str = Field(..., description="错误代码")
```

**错误代码**:
| 错误代码 | HTTP 状态 | 说明 |
|----------|-----------|------|
| `EMPTY_CONTENT` | 400 | 输入内容为空 |
| `CONTENT_TOO_SHORT` | 400 | 输入内容过短 |
| `CONTENT_TOO_LONG` | 400 | 输入内容过长 |
| `INVALID_DIRECTION` | 400 | 无效的翻译方向 |
| `AI_SERVICE_ERROR` | 500 | AI 服务调用失败 |
| `TIMEOUT` | 504 | 请求超时 |

---

## 数据流图

```
┌─────────────┐     TranslateRequest      ┌─────────────┐
│   前端      │ ───────────────────────▶  │   后端      │
│  (Browser)  │                           │  (FastAPI)  │
│             │  ◀─────────────────────   │             │
│             │   StreamChunk (SSE)       │             │
└─────────────┘                           └──────┬──────┘
                                                 │
                                                 │ OpenAI API
                                                 ▼
                                          ┌─────────────┐
                                          │ DeepSeek V3 │
                                          │   (LLM)     │
                                          └─────────────┘
```

---

## 状态转换

翻译请求无复杂状态，但前端 UI 有以下状态：

```
[空闲] ──(用户输入)──▶ [已输入]
   │                      │
   │                 (点击翻译)
   │                      ▼
   │               [翻译中] ──(流式输出)──▶ [显示结果]
   │                   │                        │
   │              (出错/超时)              (用户清空)
   │                   ▼                        │
   │              [显示错误]                    │
   │                   │                        │
   └───────────────────┴────────────────────────┘
                  (重置/重试)
```

---

## 无持久化说明

本应用为无状态设计：
- 不保存翻译历史
- 不保存用户偏好
- 每次请求独立处理
- API Key 通过环境变量配置

这样设计的原因：
1. 简化实现，符合演示级别需求
2. 保护用户隐私，不存储敏感的沟通内容
3. 便于部署，无需数据库
