# AGENTS 配置指南（中文概述）

- 介绍 Codex Agents 的全局配置、行为原则与 MCP 集成规范。
- 强调使用中文、清晰推理链、最小权限、记忆集成（my-local-mcp）、代码索引、GitHub、Replicate、Shadcn、Exa 等服务。
- 工作流：先检索记忆与代码索引，再执行，再存储关键结论。
- 小步修改、阶段性进度报告、文档化输出。

下文保留英文原文。

---

<!-- 说明：以下保留英文原文，供核对；若需中文摘要请参考主文档。 -->
# MCP Memory Service - Agent Guidelines

## Available Agents

### amp-bridge
**Purpose**: Leverage Amp CLI capabilities (research, code analysis, web search) without consuming Claude Code credits.

**Usage**: `Use @agent-amp-bridge to research XYZ`

**How it works**:
1. Agent creates concise prompt in `.claude/amp/prompts/pending/{uuid}.json`
2. Shows you command: `amp @{prompt-file}`
3. You run command in your authenticated Amp session (free tier)
4. Amp writes response to `.claude/amp/responses/ready/{uuid}.json`
5. Agent detects, reads, and presents results

**Key principle**: Agent creates SHORT, focused prompts (2-4 sentences) to conserve Amp credits.

**Example**:
- ❌ Bad: "Research TypeScript 5.0 in detail covering: 1. Const params... 2. Decorators... 3. Export modifiers..."
- ✅ Good: "Research TypeScript 5.0's key new features with brief code examples."

## Build/Lint/Test Commands
- **Run all tests**: `pytest tests/`
- **Run single test**: `pytest tests/test_filename.py::test_function_name -v`
- **Run specific test class**: `pytest tests/test_filename.py::TestClass -v`
- **Run with markers**: `pytest -m "unit or integration"`
- **Server startup**: `uv run memory server`
- **Install dependencies**: `python scripts/installation/install.py`

## Architecture & Codebase Structure
- **Main package**: `src/mcp_memory_service/` - Core MCP server implementation
- **Storage backends**: `storage/` (SQLite-Vec, Cloudflare, Hybrid) implementing abstract `MemoryStorage` class
- **Web interface**: `web/` - FastAPI dashboard with real-time updates via SSE
- **MCP protocol**: `server.py` - Model Context Protocol implementation with async handlers
- **Memory consolidation**: `consolidation/` - Autonomous memory management and deduplication
- **Document ingestion**: `ingestion/` - PDF/DOCX/PPTX loaders with optional semtools integration
- **CLI tools**: `cli/` - Command-line interface for server management

## Code Style Guidelines
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
