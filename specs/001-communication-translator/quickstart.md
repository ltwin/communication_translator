# 快速开始指南: 沟通翻译助手

## 环境要求

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python 包管理器)
- DeepSeek API Key ([获取地址](https://platform.deepseek.com/))

## 安装步骤

### 1. 克隆项目并进入目录

```bash
cd communication_translator
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=your-api-key-here
```

### 4. 启动服务

```bash
uv run python src/app.py
```

或使用 uvicorn 直接启动：

```bash
uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问应用

打开浏览器访问: http://localhost:8000

---

## 使用说明

### 基本流程

1. **选择翻译方向**
   - 智能识别 (默认): 自动识别输入内容类型并选择翻译方向
   - 产品→开发: 将产品需求转化为技术语言
   - 开发→产品: 将技术方案转化为业务语言

2. **输入内容**
   - 在输入框中输入需要翻译的内容
   - 内容长度: 10-2000 字符

3. **点击翻译**
   - 系统将实时显示翻译结果（流式输出）
   - 智能识别模式下会显示识别结果和置信度

### 测试用例

#### 用例 1: 智能识别模式

**输入** (保持默认"智能识别"选项):
```
我们需要一个智能推荐功能，提升用户停留时长
```

**预期输出**:
- 显示识别结果: "🤖 智能识别: 产品需求 → 技术语言 (置信度: 95%)"
- 输出技术实现建议

#### 用例 2: 产品需求翻译

**输入** (选择"产品→开发"):
```
我们需要一个智能推荐功能，提升用户停留时长
```

**预期输出包含**:
- 推荐算法类型建议（协同过滤/内容推荐等）
- 数据来源和处理方式
- 性能和实时性要求
- 预估开发工作量

#### 用例 3: 技术方案翻译

**输入** (选择"开发→产品"):
```
我们优化了数据库查询，QPS提升了30%
```

**预期输出包含**:
- 对用户体验的实际影响
- 支持的业务增长空间
- 成本降低的商业价值

---

## 常见问题

### Q: 启动时提示 "API Key not configured"

A: 请确保已正确配置 `.env` 文件中的 `DEEPSEEK_API_KEY`。

### Q: 翻译结果加载很慢

A: 这取决于 DeepSeek API 的响应速度。首字节响应通常在 3 秒内，完整响应可能需要 10-30 秒。

### Q: 出现 "AI 服务暂时不可用" 错误

A: 请检查:
1. API Key 是否有效
2. 网络是否能访问 api.deepseek.com
3. DeepSeek 服务是否正常

---

## 项目结构

```
communication_translator/
├── src/
│   ├── app.py               # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── controllers/         # 控制器层 (API 路由)
│   │   ├── health.py        # 健康检查接口
│   │   └── translate.py     # 翻译接口
│   ├── services/            # 服务层 (业务逻辑)
│   │   ├── translator.py    # 翻译服务
│   │   └── intent_router.py # 意图路由器 (智能识别)
│   ├── clients/             # 客户端层 (外部服务)
│   │   └── deepseek.py      # DeepSeek API 客户端
│   ├── models/              # 数据模型层
│   │   ├── enums.py         # 枚举定义
│   │   ├── requests.py      # 请求模型
│   │   └── responses.py     # 响应模型
│   └── prompts/             # 提示词模板
│       └── templates.py     # 翻译提示词
├── static/
│   ├── index.html           # 前端页面
│   ├── style.css            # 样式
│   └── app.js               # 前端逻辑
├── tests/                   # 测试文件 (按分层组织)
├── requirements.txt         # Python 依赖
├── .env.example             # 环境变量示例
└── README.md                # 项目说明
```
