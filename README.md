# 沟通翻译助手 (Communication Translator)

帮助产品经理和开发工程师相互理解的 AI 翻译服务。

## 功能特性

- **双向翻译**：支持产品需求 → 技术语言、技术方案 → 业务语言两种翻译方向
- **流式输出**：采用 Server-Sent Events (SSE) 实现实时流式响应
- **响应式 UI**：简洁美观的 Web 界面，适配桌面和移动设备

## 环境要求

- Python 3.11+
- DeepSeek API Key ([获取地址](https://platform.deepseek.com/))

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=your-api-key-here
```

### 3. 启动服务

```bash
python src/main.py
```

或使用 uvicorn 直接启动：

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问应用

打开浏览器访问: http://localhost:8000

## 测试用例

详细测试用例请参考 [quickstart.md](specs/001-communication-translator/quickstart.md)。

### 产品需求翻译测试

**输入** (选择 "产品 → 开发")：
```
我们需要一个智能推荐功能，提升用户停留时长
```

**预期输出**：包含技术实现建议、数据需求分析、性能考量等技术视角内容。

### 技术方案翻译测试

**输入** (选择 "开发 → 产品")：
```
我们优化了数据库查询，QPS提升了30%
```

**预期输出**：包含用户体验影响、业务价值、商业意义等业务视角内容。

## 项目结构

```
communication_translator/
├── src/
│   ├── main.py          # FastAPI 应用入口
│   ├── config.py        # 配置管理
│   ├── translator.py    # 翻译服务
│   ├── prompts.py       # 提示词模板
│   └── models.py        # 数据模型
├── static/
│   ├── index.html       # 前端页面
│   ├── style.css        # 样式
│   └── app.js           # 前端逻辑
├── tests/               # 测试文件
├── specs/               # 规格文档
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量示例
└── README.md            # 项目说明
```

## 运行测试

```bash
pytest tests/ -v
```

## API 文档

启动服务后，访问 http://localhost:8000/docs 查看自动生成的 API 文档。

## 技术栈

- **后端**：Python 3.11+ / FastAPI / OpenAI SDK
- **前端**：HTML / CSS / JavaScript (原生)
- **AI**：DeepSeek V3 (OpenAI 兼容 API)

## License

MIT
