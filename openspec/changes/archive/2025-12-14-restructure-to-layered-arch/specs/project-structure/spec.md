# project-structure Specification

## Purpose
定义项目的分层架构规范，确保代码组织清晰、职责分明。

## 新增需求

### 需求：分层目录结构

项目**必须**采用 Controller → Service → Client 的分层架构组织代码。

#### 场景：源码目录结构

**假设** 开发者查看 src/ 目录
**当** 列出目录内容时
**则** 应包含以下子目录：controllers/, services/, models/, clients/, prompts/

#### 场景：控制器层职责

**假设** 开发者在 controllers/ 目录中创建文件
**当** 定义 API 端点时
**则** 应仅包含路由定义、请求解析和响应格式化，业务逻辑应委托给 services/

#### 场景：服务层职责

**假设** 开发者在 services/ 目录中创建文件
**当** 实现业务逻辑时
**则** 应编排业务流程，调用 clients/ 获取外部数据，不直接处理 HTTP 请求/响应

#### 场景：客户端层职责

**假设** 开发者在 clients/ 目录中创建文件
**当** 封装外部 API 调用时
**则** 应提供简洁的接口，隐藏底层 HTTP 客户端细节，处理重试和错误转换

---

### 需求：测试目录结构

测试文件**必须**与源码层级结构保持一致。

#### 场景：测试目录镜像

**假设** src/ 下存在 controllers/, services/, models/ 子目录
**当** 组织测试文件时
**则** tests/ 下应存在对应的 controllers/, services/, models/ 子目录

#### 场景：测试文件命名

**假设** 开发者为 src/services/translator.py 编写测试
**当** 创建测试文件时
**则** 应命名为 tests/services/test_translator.py

---

### 需求：模块导出约定

每个包目录的 `__init__.py` **必须**导出该包的公共 API。

#### 场景：模型包导出

**假设** 开发者需要使用数据模型
**当** 执行 `from src.models import TranslateRequest` 时
**则** 应成功导入，无需指定具体子模块路径

#### 场景：服务包导出

**假设** 开发者需要使用翻译服务
**当** 执行 `from src.services import get_translator` 时
**则** 应成功导入工厂函数

---

### 需求：应用入口

应用**必须**通过 `src/app.py` 作为唯一入口点。

#### 场景：启动应用

**假设** 运维人员需要启动服务
**当** 执行 `python src/app.py` 或 `uvicorn src.app:app` 时
**则** 服务应正常启动并监听配置端口

#### 场景：路由注册

**假设** app.py 创建 FastAPI 实例
**当** 应用启动时
**则** 应自动注册所有 controllers/ 下定义的 APIRouter
