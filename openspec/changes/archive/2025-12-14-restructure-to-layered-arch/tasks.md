# 任务清单：项目分层架构重构

## 概述
将平铺的项目结构重构为 Controller → Service → Client 分层架构。

---

## 任务列表

### 阶段 1：准备工作

- [x] **T1**: 创建目录结构骨架
  - 创建 `src/controllers/`, `src/services/`, `src/models/`, `src/clients/`, `src/prompts/`
  - 创建 `tests/controllers/`, `tests/services/`, `tests/models/`
  - 添加所有 `__init__.py` 文件
  - **验证**: `ls -R src/ tests/` 确认目录结构

### 阶段 2：模型层重构

- [x] **T2**: 拆分 models.py 到 models/ 目录
  - 将 `TranslationDirection` 枚举移动到 `src/models/enums.py`
  - 将请求模型移动到 `src/models/requests.py`
  - 将响应模型移动到 `src/models/responses.py`
  - 在 `src/models/__init__.py` 中导出所有模型
  - **验证**: `from src.models import TranslateRequest, HealthResponse, TranslationDirection` 正常工作

- [x] **T3**: 迁移模型层测试
  - 从 `tests/test_api.py` 提取模型验证测试到 `tests/models/test_requests.py`
  - **验证**: `uv run pytest tests/models/ -v` 通过

### 阶段 3：外部客户端层

- [x] **T4**: 创建 DeepSeek API 客户端
  - 提取 `translator.py` 和 `router.py` 中共享的 OpenAI 客户端初始化逻辑
  - 创建 `src/clients/deepseek.py` 封装异步 OpenAI 客户端
  - 提供工厂方法 `get_deepseek_client()`
  - **验证**: 客户端可正常连接（依赖 API Key）

### 阶段 4：提示词模块重构

- [x] **T5**: 迁移提示词到 prompts/ 目录
  - 将 `src/prompts.py` 内容移动到 `src/prompts/templates.py`
  - 在 `src/prompts/__init__.py` 中导出 `get_system_prompt`, `INTENT_ROUTER_PROMPT`
  - **验证**: `from src.prompts import get_system_prompt` 正常工作

### 阶段 5：服务层重构

- [x] **T6**: 重构翻译服务
  - 将 `src/translator.py` 移动到 `src/services/translator.py`
  - 更新导入路径：使用 `src.clients.deepseek` 和 `src.prompts`
  - 更新 `src/services/__init__.py` 导出
  - **验证**: `from src.services import get_translator` 正常工作

- [x] **T7**: 重构意图路由服务
  - 将 `src/router.py` 重命名并移动到 `src/services/intent_router.py`
  - 更新导入路径
  - 更新 `src/services/__init__.py` 导出
  - **验证**: `from src.services import get_intent_router` 正常工作

- [x] **T8**: 迁移服务层测试
  - 将 `tests/test_translator.py` 移动到 `tests/services/test_translator.py`
  - 将 `tests/test_router.py` 移动到 `tests/services/test_intent_router.py`
  - 更新导入路径
  - **验证**: `uv run pytest tests/services/ -v` 通过

### 阶段 6：控制器层重构

- [x] **T9**: 创建健康检查控制器
  - 创建 `src/controllers/health.py`
  - 从 `main.py` 提取 `/api/health` 路由
  - 使用 FastAPI `APIRouter`
  - **验证**: 路由可挂载到 app

- [x] **T10**: 创建翻译控制器
  - 创建 `src/controllers/translate.py`
  - 从 `main.py` 提取 `/api/translate` 路由和业务编排逻辑
  - 使用 FastAPI `APIRouter`
  - **验证**: 路由可挂载到 app

- [x] **T11**: 迁移控制器层测试
  - 从 `tests/test_api.py` 提取 API 集成测试到 `tests/controllers/`
  - 创建 `tests/controllers/test_health.py` 和 `tests/controllers/test_translate.py`
  - **验证**: `uv run pytest tests/controllers/ -v` 通过

### 阶段 7：应用入口重构

- [x] **T12**: 创建应用工厂
  - 创建 `src/app.py` 作为新入口
  - 包含 FastAPI 实例创建、CORS 配置、静态文件挂载、lifespan 管理
  - 注册所有控制器路由
  - **验证**: `uv run python -c "from src.app import app; print(app.title)"` 正常输出

- [x] **T13**: 更新启动脚本和 __main__ 入口
  - 更新 `src/app.py` 中的 `if __name__ == "__main__"` 块
  - 确保 `uv run python src/app.py` 和 `uv run python -m src.app` 都能启动服务
  - **验证**: 服务可正常启动

### 阶段 8：清理旧文件

- [x] **T14**: 删除旧文件并验证
  - 删除 `src/main.py`
  - 删除 `src/models.py`
  - 删除 `src/translator.py`
  - 删除 `src/router.py`
  - 删除 `src/prompts.py`
  - 删除 `tests/test_api.py`, `tests/test_translator.py`, `tests/test_router.py`
  - **验证**: 无悬挂导入，`uv run pytest` 全部通过

### 阶段 9：最终验证

- [x] **T15**: 全面测试和文档更新
  - 运行全部测试：`uv run pytest -v`
  - 手动测试前端功能（翻译、主题切换）
  - 更新 README.md 中的项目结构说明（如有）
  - 更新 CLAUDE.md 或 project.md（如需要）
  - **验证**: 36 个测试全部通过，前端功能正常

---

## 依赖关系

```
T1 (目录结构) → T2-T5 (可并行)
T2 (模型层) → T6, T7
T4 (客户端层) → T6, T7
T5 (提示词) → T6, T7
T6, T7 (服务层) → T9, T10 (控制器层)
T9, T10 → T12 (应用入口)
T3, T8, T11 (测试迁移) 可在各自模块完成后并行执行
T12 → T13 → T14 → T15
```

## 风险点

1. **循环导入**: 分层后需注意避免跨层循环导入
2. **单例模式**: `get_translator()` 等使用 `@lru_cache` 的单例需确保在新模块位置正确工作
3. **测试 Mock**: 测试中的 Mock 路径需随源码路径更新

## 完成状态

**所有 15 个任务已完成** - 36 个测试全部通过
