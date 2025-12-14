# 任务列表：智能意图路由

## 任务依赖关系

```
T1 ──┬──▶ T2 ──▶ T3 ──▶ T4 ──▶ T5
     │
     └──▶ T6 ──▶ T7

T5 + T7 ──▶ T8 ──▶ T9
```

---

## Phase 1: 后端核心实现

### T1: 新增意图识别提示词
- **文件**: `src/prompts.py`
- **工作内容**:
  - 新增 `INTENT_ROUTER_PROMPT` 提示词常量
  - 提示词应指导 LLM 返回 JSON 格式的意图识别结果
  - 包含判断依据说明（产品需求特征 vs 技术方案特征）
- **验证**: 单元测试 prompt 格式正确性
- **可并行**: 否（基础任务）

### T2: 新增意图路由器模块
- **文件**: `src/router.py` (新增)
- **工作内容**:
  - 创建 `IntentResult` 数据模型（direction, confidence, reasoning）
  - 创建 `IntentRouter` 类
  - 实现 `detect_intent(content: str) -> IntentResult` 方法
  - 调用 LLM 并解析 JSON 响应
- **依赖**: T1
- **验证**: 单元测试（mock LLM 响应）

### T3: 修改请求模型
- **文件**: `src/models.py`
- **工作内容**:
  - 修改 `TranslateRequest`，将 `direction` 改为 `Optional[TranslationDirection]`
  - 新增 `auto_detect: bool = False` 字段
  - 添加验证逻辑：`auto_detect=False` 时 `direction` 必填
- **依赖**: T2
- **验证**: 单元测试模型验证逻辑

### T4: 修改翻译 API 接口
- **文件**: `src/main.py`
- **工作内容**:
  - 修改 `/api/translate` 端点逻辑
  - 当 `auto_detect=True` 且 `direction=None` 时，调用 IntentRouter
  - 在 SSE 流开头添加 `[META]` 元数据（智能模式下）
  - 根据置信度决定是否添加提示信息
- **依赖**: T3
- **验证**: API 集成测试

### T5: 后端单元测试
- **文件**: `tests/test_router.py` (新增), `tests/test_api.py` (修改)
- **工作内容**:
  - IntentRouter 单元测试（mock LLM）
  - 测试各种意图识别场景
  - 测试 API 在不同参数组合下的行为
- **依赖**: T4
- **验证**: pytest 全部通过

---

## Phase 2: 前端实现

### T6: 修改前端翻译方向选择
- **文件**: `static/index.html`
- **工作内容**:
  - 新增"智能识别"单选选项（作为第一个选项）
  - 调整现有"产品→开发"、"开发→产品"选项
  - 更新 UI 布局和样式
- **依赖**: T1（可与后端并行开发）
- **验证**: 手动 UI 测试

### T7: 修改前端 JS 逻辑
- **文件**: `static/app.js`
- **工作内容**:
  - 修改 `getSelectedDirection()` 函数，支持返回 null（智能模式）
  - 修改请求构建逻辑，根据选择设置 `auto_detect` 和 `direction`
  - 修改 `processSSEChunk()` 解析 `[META]` 标记
  - 新增 `displayIntentMeta()` 函数显示识别结果
- **依赖**: T6
- **验证**: 手动功能测试

---

## Phase 3: 集成与验证

### T8: 端到端集成测试
- **文件**: `tests/test_e2e.py` (新增)
- **工作内容**:
  - 测试智能模式完整流程
  - 测试手动模式向后兼容
  - 测试置信度阈值行为
  - 测试错误处理
- **依赖**: T5, T7
- **验证**: pytest 全部通过

### T9: 文档更新
- **文件**: `README.md`
- **工作内容**:
  - 更新 API 使用说明
  - 添加智能模式使用示例
  - 更新功能特性列表
- **依赖**: T8
- **验证**: 文档审核

---

## 任务清单

| ID | 任务 | 预估复杂度 | 依赖 | 状态 |
|----|------|-----------|------|------|
| T1 | 新增意图识别提示词 | 低 | - | ✅ 已完成 |
| T2 | 新增意图路由器模块 | 中 | T1 | ✅ 已完成 |
| T3 | 修改请求模型 | 低 | T2 | ✅ 已完成 |
| T4 | 修改翻译 API 接口 | 中 | T3 | ✅ 已完成 |
| T5 | 后端单元测试 | 中 | T4 | ✅ 已完成 |
| T6 | 修改前端翻译方向选择 | 低 | T1 | ✅ 已完成 |
| T7 | 修改前端 JS 逻辑 | 中 | T6 | ✅ 已完成 |
| T8 | 端到端集成测试 | 中 | T5, T7 | ⏭️ 跳过 (手动测试验证) |
| T9 | 文档更新 | 低 | T8 | ✅ 已完成 |

---

## 并行开发说明

- **后端线 (T1→T2→T3→T4→T5)** 和 **前端线 (T6→T7)** 可以并行开发
- T1 完成后，前端 T6 即可开始（无需等待后端全部完成）
- T8 集成测试需要前后端都完成后进行
