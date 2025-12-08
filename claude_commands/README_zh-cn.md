# README.md（中文说明）

Claude Code 命令总览，含存储/检索/导入等记忆操作示例。

---

# Claude Code 命令合集（适用于 MCP Memory Service）

本目录提供可在 Claude Desktop / Claude Code 中调用的记忆类命令，遵循 CCPlugins 风格的 Markdown 指令。下方保留英文原文便于对照。

## 可用命令（中文）
- `/session-start`：手动初始化会话，加载项目记忆（Windows 用于替代自动 SessionStart Bug #160）。
- `/memory-store`：写入记忆，自动补全标签/主机名。
- `/memory-recall`：按自然语言时间检索历史决策/对话。
- `/memory-search`：精确字符串搜索记忆。
- `/memory-context`：查看当前目录相关记忆上下文。
- `/memory-ingest`：导入单文件或 URL。
- `/memory-ingest-dir`：递归导入目录。
- `/memory-health`：检查 MCP Memory Service 安装与数据库健康。

### 使用示例
```bash
claude /session-start
claude /memory-store --tags "decision,architecture" "We chose SQLite-vec for performance"
claude /memory-recall "what did we decide about the database last week?"
claude /memory-ingest README.md
claude /memory-search "SQLite-vec"
```

---
# Claude Code Commands for MCP Memory Service (English original)

This directory contains conversational Claude Code commands that integrate memory functionality into your Claude Code workflow. These commands follow the CCPlugins pattern of markdown-based conversational instructions.

## Available Commands

### `/session-start` - Manual Session Initialization
Display session memory context manually by running the session-start hook. **Windows Workaround**: Required for Windows users due to SessionStart hook bug (#160). Works on all platforms.

**Usage:**
```bash
claude /session-start
```

**Why this exists:**
- Windows users cannot use automatic SessionStart hooks (causes Claude Code to hang)
- Provides same functionality as automatic session-start hook
- Safe manual alternative that works on all platforms (Windows, macOS, Linux)

**What it does:**
- Loads relevant project memories at session start
- Analyzes git history and recent changes
- Displays categorized memory context (recent work, current problems, additional context)

### `/memory-store` - Store Current Context
Store information in your MCP Memory Service with proper context and tagging. Automatically detects project context, applies relevant tags, and includes machine hostname for source tracking.

**Usage:**
```bash
claude /memory-store "Important architectural decision about database backend"
claude /memory-store --tags "decision,architecture" "We chose SQLite-vec for performance"
```

### `/memory-recall` - Time-based Memory Retrieval
Retrieve memories using natural language time expressions. Perfect for finding past conversations and decisions.

**Usage:**
```bash
claude /memory-recall "what did we decide about the database last week?"
```

