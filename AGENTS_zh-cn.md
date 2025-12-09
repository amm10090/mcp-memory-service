# MCP Memory Service - Agent 指南（中文完整版）

[简体中文](AGENTS_zh-cn.md) | [English](AGENTS.md)

## 可用代理（Agents）

### amp-bridge
**用途**：调用 Amp CLI（研究、代码分析、网页搜索）而不消耗 Claude Code 配额。

**用法示例**：`Use @agent-amp-bridge to research XYZ`

**工作流程**：
1. 在 `.claude/amp/prompts/pending/{uuid}.json` 写入简短提示。
2. 显示待执行命令：`amp @{prompt-file}`。
3. 在已登录的 Amp 会话中运行该命令（免费版即可）。
4. Amp 输出结果到 `.claude/amp/responses/ready/{uuid}.json`。
5. Agent 读取并呈现结果。

**关键原则**：提示要短而聚焦（2–4 句），以节省 Amp 额度。

**反例/正例**：
- ❌ 过长：“Research TypeScript 5.0 in detail covering: 1. Const params... 2. Decorators... 3. Export modifiers...”
- ✅ 合理：“Research TypeScript 5.0's key new features with brief code examples.”

## 构建 / Lint / 测试命令
- 运行全部测试：`pytest tests/`
- 运行单个测试：`pytest tests/test_filename.py::test_function_name -v`
- 运行特定测试类：`pytest tests/test_filename.py::TestClass -v`
- 按标记运行：`pytest -m "unit or integration"`
- 启动服务器：`uv run memory server`
- 安装依赖：`python scripts/installation/install.py`

## 架构与代码结构
- 主包：`src/mcp_memory_service/` —— MCP 服务器核心实现
- 存储后端：`storage/`（SQLite-Vec、Cloudflare、Hybrid），实现抽象 `MemoryStorage`
- Web 界面：`web/` —— 基于 FastAPI，SSE 实时更新
- MCP 协议：`server.py` —— 异步处理器实现
- 记忆合并：`consolidation/` —— 自动去重与整合
- 文档摄取：`ingestion/` —— PDF/DOCX/PPTX 加载，可选 semtools
- CLI 工具：`cli/` —— 服务器管理命令行

## 代码风格指南
- `Imports`：优先绝对引用；可选依赖使用条件导入。
- `Types`：Python 3.10+ 类型注解，MCP 响应用 `TypedDict`。
- `Async/await`：所有 I/O 使用异步模式。
- `Naming`：函数/变量 `snake_case`，类 `PascalCase`，常量 `SCREAMING_SNAKE_CASE`。
- `Error handling`：使用针对性的 try/except 并记录日志。
- `Memory types`：使用 24 个核心记忆类型（note、reference、session、implementation 等）。
- `Documentation`：采用 NumPy 风格注释；项目约定详见 `CLAUDE.md`。

## 开发规则（源自 CLAUDE.md）
- 遵循 MCP 协议规范的工具 schema 与响应格式。
- 存储后端需继承抽象基类实现。
- 提交信息使用语义化、conventional commit 格式。
- Web 界面需在开启/关闭 OAuth 两种模式下测试。
- 校验搜索端点：语义搜索、标签搜索、时间搜索均需覆盖。
- **Imports**: Absolute imports preferred, conditional imports for optional dependencies
- **Types**: Python 3.10+ type hints throughout, TypedDict for MCP responses
- **Async/await**: All I/O operations use async/await pattern
- **Naming**: snake_case for functions/variables, PascalCase for classes, SCREAMING_SNAKE_CASE for constants
- **Error handling**: Try/except blocks with specific exceptions, logging for debugging
- **Memory types**: Use 24 core types from taxonomy (note, reference, session, implementation, etc.)
- **Documentation**: NumPy-style docstrings, CLAUDE.md for project conventions

## Development Rules (from CLAUDE.md)
- Follow MCP protocol specification for tool schemas and responses
- Implement storage backends extending abstract base class
- Use semantic commit messages with conventional commit format
- Test both OAuth enabled/disabled modes for web interface
- Validate search endpoints: semantic, tag-based, time-based queries
