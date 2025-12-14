# 变更提案：项目分层架构重构

## 变更概述

将当前平铺的项目结构重构为分层架构（Controller → Service → Client），提升代码组织性和可维护性。

## 动机

当前项目虽然简单，但存在以下问题：

1. **main.py 职责过重**：混合了 FastAPI 应用配置、路由定义和业务编排逻辑
2. **缺乏明确分层**：没有 controllers 目录，路由和业务逻辑混在一起
3. **测试结构与源码不匹配**：测试文件平铺在 tests/ 根目录
4. **扩展性受限**：随着功能增加，平铺结构会导致文件查找困难

## 目标架构

```
src/
├── __init__.py
├── app.py              # FastAPI 应用工厂
├── config.py           # 配置管理 (保持不变)
├── controllers/        # 控制器层：API 路由定义
│   ├── __init__.py
│   ├── health.py       # 健康检查路由
│   └── translate.py    # 翻译路由
├── services/           # 服务层：业务逻辑
│   ├── __init__.py
│   ├── translator.py   # 翻译服务
│   └── intent_router.py # 意图路由服务
├── models/             # 数据模型层
│   ├── __init__.py
│   ├── requests.py     # API 请求模型
│   ├── responses.py    # API 响应模型
│   └── enums.py        # 枚举定义
├── clients/            # 外部客户端层：AI API 调用
│   ├── __init__.py
│   └── deepseek.py     # DeepSeek API 客户端
└── prompts/            # 提示词模块
    ├── __init__.py
    └── templates.py    # 提示词模板

tests/
├── conftest.py         # 测试配置和共享 fixtures
├── controllers/        # 控制器层测试
│   ├── __init__.py
│   ├── test_health.py
│   └── test_translate.py
├── services/           # 服务层测试
│   ├── __init__.py
│   ├── test_translator.py
│   └── test_intent_router.py
└── models/             # 模型层测试
    ├── __init__.py
    └── test_requests.py
```

## 变更范围

### 新增文件
- `src/app.py` - 应用工厂，从 main.py 中提取 FastAPI 配置
- `src/controllers/__init__.py`, `health.py`, `translate.py`
- `src/services/__init__.py`, `translator.py`, `intent_router.py`
- `src/models/__init__.py`, `requests.py`, `responses.py`, `enums.py`
- `src/clients/__init__.py`, `deepseek.py`
- `src/prompts/__init__.py`, `templates.py`
- `tests/conftest.py`, `tests/controllers/`, `tests/services/`, `tests/models/`

### 删除文件
- `src/main.py` (重构为 app.py + controllers)
- `src/models.py` (拆分到 models/)
- `src/translator.py` (移动到 services/)
- `src/router.py` (重命名并移动到 services/intent_router.py)
- `src/prompts.py` (移动到 prompts/templates.py)
- `tests/test_api.py`, `tests/test_translator.py`, `tests/test_router.py` (重组)

### 保持不变
- `src/config.py` - 配置管理模块位置不变
- `static/` - 前端静态文件
- `openspec/` - OpenSpec 规范文件

## 兼容性考虑

1. **入口点**：`main.py` 改为 `app.py`，需更新启动命令
2. **导入路径**：所有内部导入需要更新
3. **测试运行**：pytest 配置无需修改，自动发现新目录结构

## 规范增量

本变更引入新规范 `project-structure`，定义分层架构的约束和约定。
