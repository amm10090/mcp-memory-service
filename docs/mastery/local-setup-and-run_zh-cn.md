# MCP Memory Service — 本地搭建与运行

按照以下步骤即可在本地运行服务、切换存储后端并验证基础功能。

## 1) 安装依赖

推荐使用 uv：

```
uv sync
```

如使用 pip：

```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

当使用 SQLite-vec 后端（推荐）时：

```
uv add sqlite-vec sentence-transformers torch
# 或
pip install sqlite-vec sentence-transformers torch
```

## 2) 选择存储后端

SQLite-vec（默认）：

```
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
# 可自定义数据库路径
export MCP_MEMORY_SQLITE_PATH="$HOME/.local/share/mcp-memory/sqlite_vec.db"
```

ChromaDB（已弃用）：

```
export MCP_MEMORY_STORAGE_BACKEND=chroma
export MCP_MEMORY_CHROMA_PATH="$HOME/.local/share/mcp-memory/chroma_db"
```

Cloudflare：

```
export MCP_MEMORY_STORAGE_BACKEND=cloudflare
export CLOUDFLARE_API_TOKEN=...
export CLOUDFLARE_ACCOUNT_ID=...
export CLOUDFLARE_VECTORIZE_INDEX=...
export CLOUDFLARE_D1_DATABASE_ID=...
```

## 3) 启动服务器

Stdio MCP 服务器（适配 Claude Desktop）：

```
uv run memory server
```

FastMCP HTTP 服务器（适配 Claude Code / 远程场景）：

```
uv run mcp-memory-server
```

Claude Desktop 配置示例（`~/.claude/config.json`）：

```
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-service", "run", "memory", "server"],
      "env": { "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec" }
    }
  }
}
```

## 4) 健康检查与基础操作

命令行查看状态：

```
uv run memory status
```

MCP 工具调用流程（在客户端中）：
- `store_memory` → `retrieve_memory` → `search_by_tag` → `delete_memory`

## 5) 运行测试

```
pytest -q
# 或
uv run pytest -q
```

更多信息参见 `docs/mastery/testing-guide.md` 与 `docs/sqlite-vec-backend.md`。
