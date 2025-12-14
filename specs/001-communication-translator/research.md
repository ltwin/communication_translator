# 技术研究: 沟通翻译助手

**日期**: 2025-12-14
**功能**: 001-communication-translator

## 研究摘要

本文档记录了沟通翻译助手实现过程中的技术研究和决策。

---

## 1. DeepSeek V3 API 集成

### 决策
使用 DeepSeek V3 模型，通过 OpenAI 兼容 API 进行调用。

### 理由
- **成本优势**: DeepSeek V3 价格远低于 GPT-4，适合演示和小规模使用
- **兼容性**: 提供 OpenAI 兼容 API，可直接使用 openai Python SDK
- **中文能力**: 对中文理解和生成能力优秀，适合产品/技术沟通场景
- **流式支持**: 支持 Server-Sent Events (SSE) 流式输出

### 替代方案考虑
| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| OpenAI GPT-4 | 质量最高 | 成本高 | 放弃 |
| OpenAI GPT-3.5 | 成本适中 | 中文能力一般 | 放弃 |
| 通义千问 | 阿里云生态 | API 不兼容 OpenAI | 放弃 |
| DeepSeek V3 | 低成本、OpenAI 兼容、中文优秀 | 相对较新 | **采用** |

### 集成方式
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-deepseek-api-key",
    base_url="https://api.deepseek.com"
)
```

---

## 2. FastAPI 流式响应实现

### 决策
使用 FastAPI 的 `StreamingResponse` 配合 Server-Sent Events (SSE) 格式实现流式输出。

### 理由
- **原生支持**: FastAPI 原生支持异步流式响应
- **浏览器兼容**: SSE 被所有现代浏览器原生支持 (EventSource API)
- **简单实现**: 无需 WebSocket，单向数据流足够满足需求
- **自动重连**: EventSource 内置断线重连机制

### 替代方案考虑
| 方案 | 优点 | 缺点 | 决策 |
|------|------|------|------|
| WebSocket | 双向通信 | 过于复杂，单向流足够 | 放弃 |
| Long Polling | 兼容性最好 | 实现复杂，效率低 | 放弃 |
| SSE (EventSource) | 简单、原生支持、自动重连 | 仅单向 | **采用** |

### 实现模式
```python
from fastapi.responses import StreamingResponse

async def generate_stream():
    async for chunk in ai_response:
        yield f"data: {chunk}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/api/translate")
async def translate(request: TranslateRequest):
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
```

---

## 3. 提示词设计策略

### 决策
为两个翻译方向设计专门的系统提示词，明确定义角色视角差异和输出结构。

### 理由
- **角色区分**: 产品和开发关注点完全不同，需要专门的提示词
- **结构化输出**: 通过提示词引导 AI 生成结构化的翻译结果
- **一致性**: 统一的输出格式便于用户理解和比较

### 提示词设计要点

#### 产品→开发方向
- 系统角色: 资深技术架构师，擅长将业务需求转化为技术方案
- 输出结构:
  1. **技术实现建议**: 推荐的技术方案和算法
  2. **数据需求分析**: 需要什么数据，从哪里获取
  3. **性能考量**: 实时性要求、并发量、响应时间
  4. **工作量评估**: 大致的开发周期和复杂度
  5. **潜在风险**: 技术挑战和需要澄清的问题

#### 开发→产品方向
- 系统角色: 产品技术顾问，擅长解释技术成果的业务价值
- 输出结构:
  1. **用户体验影响**: 对用户有什么直接感知
  2. **业务价值**: 支撑什么业务目标
  3. **商业意义**: 成本节约、效率提升等
  4. **里程碑意义**: 技术能力建设的意义
  5. **下一步建议**: 基于此可以做什么

---

## 4. 前端流式显示实现

### 决策
使用原生 JavaScript EventSource API 接收流式数据，逐步渲染到页面。

### 理由
- **无依赖**: 不需要引入额外的 JavaScript 框架
- **原生支持**: 现代浏览器原生支持 EventSource
- **简单直接**: 代码量小，易于理解和维护

### 实现模式
```javascript
const eventSource = new EventSource('/api/translate');
eventSource.onmessage = (event) => {
    if (event.data === '[DONE]') {
        eventSource.close();
        return;
    }
    outputElement.textContent += event.data;
};
```

### 用户体验增强
- 显示打字机效果的光标
- 翻译进行中禁用输入和提交按钮
- 完成后自动移除光标，启用按钮

---

## 5. 错误处理策略

### 决策
分层错误处理：API 层捕获并转换为用户友好消息，前端统一显示。

### 错误类型及处理

| 错误类型 | HTTP 状态码 | 用户提示 |
|----------|-------------|----------|
| 输入为空 | 400 | "请输入需要翻译的内容" |
| 输入过短 | 400 | "输入内容过短，请提供更多上下文" |
| API Key 无效 | 500 | "服务配置错误，请联系管理员" |
| AI 服务超时 | 504 | "AI 服务响应超时，请稍后重试" |
| 网络错误 | 500 | "网络连接异常，请检查网络后重试" |

### 日志规范
- 错误日志使用英文，包含请求ID、错误类型、详细信息
- 日志级别: DEBUG (请求详情), INFO (正常流程), WARN (可恢复错误), ERROR (严重错误)

---

## 6. 配置管理

### 决策
使用环境变量管理敏感配置，python-dotenv 加载 .env 文件。

### 配置项

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| API Key | DEEPSEEK_API_KEY | - | DeepSeek API 密钥 (必需) |
| API Base URL | DEEPSEEK_BASE_URL | https://api.deepseek.com | API 地址 |
| 模型名称 | DEEPSEEK_MODEL | deepseek-chat | 使用的模型 |
| 服务端口 | PORT | 8000 | Web 服务端口 |
| 日志级别 | LOG_LEVEL | INFO | 日志输出级别 |

---

## 研究结论

所有技术选型已确定，无需进一步澄清。可以进入 Phase 1 设计阶段。
