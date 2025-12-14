# Tasks: 沟通翻译助手 (Communication Translator)

**Input**: Design documents from `/specs/001-communication-translator/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/api.yaml ✅

**Tests**: 包含测试任务，基于 plan.md 中定义的测试结构

**Organization**: 任务按用户故事分组，支持独立实现和测试

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件，无依赖）
- **[Story]**: 所属用户故事（US1, US2, US3, US4）
- 描述中包含精确文件路径

---

## Phase 1: Setup (项目初始化)

**Purpose**: 创建项目基础结构和配置

- [x] T001 Create project directory structure (src/, static/, tests/)
- [x] T002 Create requirements.txt with dependencies (fastapi, uvicorn, openai, python-dotenv, pytest, pytest-asyncio)
- [x] T003 [P] Create .env.example with environment variable template
- [x] T004 [P] Create .gitignore for Python project

---

## Phase 2: Foundational (基础设施)

**Purpose**: 所有用户故事共享的核心基础设施

**⚠️ CRITICAL**: 此阶段必须完成后才能开始任何用户故事

- [x] T005 Implement configuration management in src/config.py (API Key, model settings, environment loading)
- [x] T006 Create Pydantic data models in src/models.py (TranslationDirection, TranslateRequest, ErrorResponse)
- [x] T007 [P] Create prompt templates in src/prompts.py (product_to_dev, dev_to_product system prompts)
- [x] T008 Create FastAPI application entry point in src/main.py (app instance, static files, CORS)
- [x] T009 Implement health check endpoint GET /api/health in src/main.py

**Checkpoint**: 基础设施就绪 - 可开始用户故事实现

---

## Phase 3: User Story 1 - 产品需求翻译为技术语言 (Priority: P1) 🎯 MVP

**Goal**: 产品经理输入需求描述，系统生成包含技术建议、数据需求、性能考量的翻译结果

**Independent Test**: 调用 POST /api/translate 接口，direction=product_to_dev，验证返回流式响应包含技术视角内容

### Tests for User Story 1

- [x] T010 [P] [US1] Create unit test for product_to_dev translation in tests/test_translator.py
- [x] T011 [P] [US1] Create API integration test for POST /api/translate (product_to_dev) in tests/test_api.py

### Implementation for User Story 1

- [x] T012 [US1] Implement DeepSeek API client initialization in src/translator.py (OpenAI compatible client)
- [x] T013 [US1] Implement translate_stream async generator in src/translator.py (product_to_dev direction)
- [x] T014 [US1] Implement POST /api/translate endpoint with SSE streaming in src/main.py
- [x] T015 [US1] Add input validation (content min/max length) and error handling in src/main.py

**Checkpoint**: 用户故事 1 可独立测试 - 后端 product_to_dev 翻译功能完整

---

## Phase 4: User Story 2 - 技术方案翻译为业务语言 (Priority: P1)

**Goal**: 开发工程师输入技术方案，系统生成包含用户体验影响、业务价值的翻译结果

**Independent Test**: 调用 POST /api/translate 接口，direction=dev_to_product，验证返回流式响应包含业务视角内容

### Tests for User Story 2

- [x] T016 [P] [US2] Create unit test for dev_to_product translation in tests/test_translator.py
- [x] T017 [P] [US2] Create API integration test for POST /api/translate (dev_to_product) in tests/test_api.py

### Implementation for User Story 2

- [x] T018 [US2] Extend translate_stream to support dev_to_product direction in src/translator.py
- [x] T019 [US2] Add dev_to_product prompt template in src/prompts.py (if not already complete)

**Checkpoint**: 用户故事 1 和 2 后端功能完整 - 双向翻译 API 可用

---

## Phase 5: User Story 3 - 翻译方向选择 (Priority: P2)

**Goal**: 用户可在界面上选择翻译方向，系统根据选择调整翻译策略

**Independent Test**: 打开网页，可看到翻译方向选择器，切换方向时界面相应更新

### Implementation for User Story 3

- [x] T020 [US3] Create HTML structure in static/index.html (direction selector, input textarea, output area, translate button)
- [x] T021 [US3] Create CSS styles in static/style.css (responsive layout, direction selector styling, input/output areas)
- [x] T022 [US3] Implement direction selection logic in static/app.js (radio buttons or toggle, state management)

**Checkpoint**: 用户故事 3 可独立测试 - 基本 UI 结构和交互完成

---

## Phase 6: User Story 4 - 流式输出体验 (Priority: P2)

**Goal**: 提交翻译请求后，用户能看到文字以打字机效果逐步显示

**Independent Test**: 在网页上提交翻译，观察结果区域文字逐渐出现，有视觉指示表明生成中

### Implementation for User Story 4

- [x] T023 [US4] Implement EventSource SSE client in static/app.js (connect to /api/translate)
- [x] T024 [US4] Implement streaming text display with typing cursor effect in static/app.js
- [x] T025 [US4] Add loading state indicator and disable controls during translation in static/app.js
- [x] T026 [US4] Handle SSE connection errors and display user-friendly messages in static/app.js
- [x] T027 [US4] Add [DONE] and [ERROR] marker handling in static/app.js

**Checkpoint**: 完整的前后端集成 - 用户可通过 Web 界面完成双向翻译

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 完善、测试验证、文档更新

- [x] T028 [P] Create README.md with project introduction, installation steps, and reference to specs/001-communication-translator/quickstart.md for test cases
- [x] T029 [P] Add comprehensive error handling for all edge cases in src/main.py and src/translator.py (empty input, content too short/long, API key invalid, AI service timeout with 30s limit, network errors)
- [x] T030 [P] Add structured logging (English) throughout the application in src/
- [x] T031 Run all tests and fix any failures
- [x] T032 Validate against quickstart.md test cases (product→dev and dev→product scenarios)
- [x] T033 Final code review and cleanup

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 无依赖 - 可立即开始
- **Foundational (Phase 2)**: 依赖 Setup 完成 - 阻塞所有用户故事
- **User Stories (Phase 3-6)**: 均依赖 Foundational 完成
  - US1 和 US2 可并行（后端翻译功能）
  - US3 可独立进行（前端 UI 结构）
  - US4 依赖 US1/US2（需要后端 API）和 US3（需要前端结构）
- **Polish (Phase 7)**: 依赖所有用户故事完成

### User Story Dependencies

```
US1 (P1) ─────┐
              ├──▶ US4 (P2) ──▶ Polish
US2 (P1) ─────┤
              │
US3 (P2) ─────┘
```

- **US1 (产品→开发翻译)**: Foundational 完成后可开始，无其他依赖
- **US2 (开发→产品翻译)**: Foundational 完成后可开始，可与 US1 并行
- **US3 (方向选择 UI)**: Foundational 完成后可开始，可与 US1/US2 并行
- **US4 (流式输出体验)**: 依赖 US1/US2 的后端 API 和 US3 的前端结构

### Within Each User Story

- 测试任务先行（TDD）
- 模型/配置 → 服务逻辑 → 接口/UI
- 核心功能 → 错误处理 → 日志

### Parallel Opportunities

- T003, T004 可并行（不同配置文件）
- T007 可与 T005, T006 并行（不同源文件）
- T010, T011 可并行（不同测试文件）
- T016, T017 可并行（不同测试范围）
- US1 和 US2 的后端实现可并行
- US3 的前端工作可与 US1/US2 并行

---

## Parallel Example: Phase 3 (User Story 1)

```bash
# 并行执行测试任务:
Task: "Create unit test for product_to_dev translation in tests/test_translator.py"
Task: "Create API integration test for POST /api/translate in tests/test_api.py"

# 测试完成后，顺序执行实现任务:
Task: "Implement DeepSeek API client initialization in src/translator.py"
Task: "Implement translate_stream async generator in src/translator.py"
...
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (product_to_dev backend)
4. **STOP and VALIDATE**: 通过 curl 或 Postman 测试 API
5. 可演示后端翻译能力

### Incremental Delivery

1. Setup + Foundational → 基础就绪
2. US1 → 测试 → 后端 product→dev 功能 (MVP!)
3. US2 → 测试 → 后端双向翻译完整
4. US3 → 测试 → 前端 UI 结构完成
5. US4 → 测试 → 完整的用户体验
6. Polish → 文档、清理、最终验证

### Recommended Execution Order (单人开发)

1. T001 → T002 → T003, T004 (并行)
2. T005 → T006 → T007 (并行) → T008 → T009
3. T010, T011 (并行) → T012 → T013 → T014 → T015
4. T016, T017 (并行) → T018 → T019
5. T020 → T021 → T022
6. T023 → T024 → T025 → T026 → T027
7. T028, T029, T030 (并行) → T031 → T032 → T033

---

## Summary

| Phase | Task Count | Parallel Opportunities |
|-------|------------|----------------------|
| Phase 1: Setup | 4 | T003, T004 |
| Phase 2: Foundational | 5 | T007 |
| Phase 3: US1 (MVP) | 6 | T010, T011 |
| Phase 4: US2 | 4 | T016, T017 |
| Phase 5: US3 | 3 | - |
| Phase 6: US4 | 5 | - |
| Phase 7: Polish | 6 | T028, T029, T030 |
| **Total** | **33** | **9 parallel groups** |

---

## Notes

- 所有源文件注释使用中文
- 日志输出使用英文
- 代码标识符使用英文
- 每个 checkpoint 后可暂停验证
- 使用 Context7 MCP 工具检索 FastAPI、OpenAI SDK 文档
