# NoneBot 用户插件 AI 编码指南

欢迎来到 `nonebot-plugin-user` 项目！本指南用于帮助 AI 编码代理快速理解项目结构、关键组件和开发工作流。

## 1. 项目概述

本项目是一个为 [NoneBot2](https://v2.nonebot.dev/) 框架开发的用户插件，用于在不同平台、不同会话中创建、查询和绑定统一的用户账号。

- **核心功能**: 为各平台用户创建统一的内部账号，并支持通过 `/user` 查看或修改用户信息。
- **账号绑定**: 通过 `/bind` 令牌流程将不同平台账号绑定到同一个内部用户 ID，并支持解除绑定回到初始账号。
- **命令系统**: 使用 `nonebot-plugin-alconna` 定义和解析 `/user`、`/bind` 等用户命令。
- **会话识别**: 使用 `nonebot-plugin-uninfo` 获取跨平台 `Session`、平台用户、场景类型和场景路径。
- **数据持久化**: 使用 `nonebot-plugin-orm` 和 SQLAlchemy 保存 `User`、`Bind` 等模型，并通过迁移脚本维护数据库结构。
- **插件适配**: 通过 `Annotated[..., Depends(...)]` 暴露 `User` 和 `UserSession` 依赖，方便其他 NoneBot 插件注入当前用户信息。

## 2. 关键模块与代码结构

理解以下文件是快速上手的关键：

- **`nonebot_plugin_user/__init__.py`**: 插件主入口。声明依赖的插件，定义 `PluginMetadata`，导出 `User`、`UserSession`、`get_user`、`get_user_by_id`、`get_user_platform_ids` 等公共 API，并加载 `matchers`。
- **`nonebot_plugin_user/matchers.py`**: 用户交互逻辑。这里注册 `/user` 和 `/bind` 命令，处理用户名、邮箱、绑定令牌、解除绑定等流程。绑定令牌保存在 `ExpiringDict` 中，默认 5 分钟过期。
- **`nonebot_plugin_user/models.py`**: 数据模型和用户会话对象。`User` 保存内部账号，`Bind` 保存平台账号到内部账号的映射，`UserSession` 包装 `nonebot-plugin-uninfo` 的 `Session` 与内部 `User`。
- **`nonebot_plugin_user/utils.py`**: 数据库读写和绑定核心逻辑。包括获取或创建用户、设置绑定、设置用户名/邮箱、解除绑定、查询平台 ID 列表等函数。
- **`nonebot_plugin_user/params.py`**: NoneBot 依赖注入函数。通过 `nonebot-plugin-uninfo` 的 `get_session` 获取当前会话，再调用 `utils.get_user_depends` 得到内部用户。
- **`nonebot_plugin_user/annotated.py`**: 对外暴露的依赖注入类型别名。其他插件可以直接声明 `user: User` 或 `session: UserSession`。
- **`nonebot_plugin_user/config.py`**: 插件配置模型。目前核心配置项是 `user_token_prefix`，用于控制绑定令牌前缀。
- **`nonebot_plugin_user/migrations/`**: 数据库迁移脚本。修改 `User`、`Bind` 等 ORM 模型时，需要同步维护迁移。
- **`tests/`**: 测试目录。使用 `nonebug` 模拟 NoneBot 事件和 matcher 流程，`tests/fake.py` 提供 OneBot V11/V12 事件构造工具。

## 3. 开发工作流

- **依赖管理**: 项目使用 `uv` 管理依赖，构建后端为 `uv_build`。运行时依赖和开发依赖都在 `pyproject.toml` 中定义，开发依赖位于 `[dependency-groups]`。
- **Python 版本**: 当前最低支持 Python 3.10。类型标注可使用 `str | None`、`list[str]`、`tuple[str, ...]` 等现代写法。
- **安装依赖**: 使用 `uv sync` 同步环境。
- **代码检查**: 使用 `uv run ruff check` 运行 lint，使用 `uv run ruff format --check` 检查格式。
- **测试**: 测试命令定义在 `pyproject.toml` 的 `[tool.poe.tasks]`。
  - 运行所有测试: `uv run poe test`
  - 单进程运行测试: `uv run poe test:single`
  - 运行指定测试文件: `uv run pytest tests/test_user.py`
- **数据库迁移**: CI 会执行 `uvx --from nb-cli nb orm upgrade`。如果修改 ORM 模型，应通过 `nb orm` CLI 创建迁移脚本，例如使用 `uvx --from nb-cli nb orm revision -m "描述"`，再补全并检查生成的 `nonebot_plugin_user/migrations/` 内容。不要绕过 CLI 直接新建迁移文件；确需手工调整时，也应基于 CLI 创建的迁移脚本小范围修正，并覆盖 SQLite、PostgreSQL、MySQL 相关场景。
- **提交与 PR**:
  - 提交信息和 PR 标题使用约定式提交格式，例如 `feat: 支持修改用户邮箱`。
  - PR 标题和正文使用中文，正文需说明变更内容、影响范围和验证命令。
  - 涉及用户可见功能、修复或行为变化时，在提交前同步维护 `CHANGELOG.md` 的 `Unreleased` 小节。

## 4. 重要模式与约定

- **命令处理与 Alconna**:

  - 用户命令使用 `Alconna`、`Option`、`Args`、`Match`、`Query` 进行结构化定义，不要改成手写字符串解析。
  - `/user` 负责展示和修改用户信息；`/bind` 负责绑定、二阶段群聊绑定和解除绑定。修改命令参数时，需要同步更新 README 和测试期望。

- **用户与会话识别**:

  - 跨平台身份来自 `nonebot-plugin-uninfo` 的 `Session`，平台名称优先使用 `session.scope`，平台用户 ID 使用 `session.user.id`。
  - 对外返回用户会话信息时使用 `UserSession`，其中 `session_id` 由 `session.scope` 和 `session.scene_path` 组合。
  - 保留已标记 deprecated 的旧属性时，应继续通过 `typing_extensions.deprecated` 标注，避免直接删除公共 API。

- **绑定流程**:

  - `Bind.original_id` 表示初始绑定账号，`Bind.bind_id` 表示当前绑定到的内部账号。解除绑定时只应将 `bind_id` 恢复为 `original_id`，不要删除绑定记录。
  - 群聊绑定是两阶段流程：第一阶段在原始平台验证令牌，第二阶段回到目标平台确认账号；私聊绑定可以直接完成。
  - 绑定令牌应保持短期有效，不要写入日志或持久化存储。测试中如需固定令牌，请 mock 令牌生成函数使用的随机源。

- **数据库访问与迁移**:

  - 普通数据库操作使用 `nonebot_plugin_orm.get_session()`。
  - 依赖注入链路中使用 `get_scoped_session()`，新创建的用户需要 merge 回 scoped session。
  - 创建用户和绑定记录时注意并发写入，当前实现通过 `_insert_mutex` 和 `IntegrityError` 兜底处理重复创建。
  - 查询用户时应通过 `Bind.platform` 和 `Bind.platform_id` 连接 `User`，不要只依赖平台用户 ID。
  - 修改 `models.py` 中的 ORM 模型后，使用 `nb orm` CLI 生成迁移，并在提交前执行 `uvx --from nb-cli nb orm upgrade` 验证迁移可应用。

- **Pydantic 兼容性**:

  - 当前依赖允许 Pydantic v1/v2 共存，模型中保留了 `PYDANTIC_V2` 分支。除非项目明确提升到 Pydantic v2-only，否则不要移除 v1 兼容代码。
  - `pyproject.toml` 中 pyright 定义了 `PYDANTIC_V2 = true`，但运行时仍可能处在兼容依赖范围内。

- **配置**:

  - 可变配置应添加到 `config.py` 的 `Config` 模型中，并提供合理默认值。
  - 新配置需要在 README 的配置项部分说明名称、类型、默认值和含义。

- **测试约定**:
  - matcher 流程测试使用 `nonebug`，优先复用 `tests/fake.py` 中的事件构造函数。
  - 测试中会注册 OneBot V11/V12 adapter，并用 `freezegun` 固定时间；涉及时间输出时要考虑本地时区转换。
  - 数据库测试结束后会清理 `User`、`Bind` 表，并在 PostgreSQL/MySQL 下重置自增序列。
  - 新增或修改数据库行为时，至少补充 SQLite 路径下的单元测试；涉及迁移或方言差异时，考虑 CI 中 PostgreSQL/MySQL 的行为。

在开始编码前，请确保你已熟悉 NoneBot2、Alconna、nonebot-plugin-uninfo 和 nonebot-plugin-orm 的基本概念。
