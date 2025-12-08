# 快速配置：Cloudflare 后端（Claude Desktop + Claude Code）

本文提供最简流程，同时为 Claude Desktop 与 Claude Code 配置 Cloudflare 存储后端，保证两端共享同一记忆库。

## 🎯 目标

- Claude Desktop：✅ 使用 Cloudflare backend，含 1000+ 记忆。
- Claude Code：✅ 连接同一 Cloudflare backend。
- 健康检查中出现：`"backend": "cloudflare"` 与 `"storage_type": "CloudflareStorage"`。

## ⚡ 5 分钟上手

### 第 1 步：准备 Cloudflare 资源
```bash
npm install -g wrangler
wrangler login
wrangler vectorize create mcp-memory-index --dimensions=768 --metric=cosine
wrangler d1 create mcp-memory-db
```

### 第 2 步：创建 `.env`
```bash
cd C:/REPOSITORIES/mcp-memory-service
cat > .env <<'EOF_ENV'
MCP_MEMORY_STORAGE_BACKEND=cloudflare
CLOUDFLARE_API_TOKEN=your-api-token-here
CLOUDFLARE_ACCOUNT_ID=your-account-id-here
CLOUDFLARE_D1_DATABASE_ID=your-d1-database-id-here
CLOUDFLARE_VECTORIZE_INDEX=mcp-memory-index
MCP_MEMORY_BACKUPS_PATH=C:\Users\your-username\AppData\Local\mcp-memory\backups
MCP_MEMORY_SQLITE_PATH=C:\Users\your-username\AppData\Local\mcp-memory\backups\sqlite_vec.db
EOF_ENV
```

### 第 3 步：配置 Claude Desktop
编辑 `~/.claude.json`（或 `%APPDATA%\Claude\claude_desktop_config.json`）：
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["-m", "mcp_memory_service.server"],
      "cwd": "C:/REPOSITORIES/mcp-memory-service",
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "cloudflare",
        "CLOUDFLARE_API_TOKEN": "your-api-token-here",
        "CLOUDFLARE_ACCOUNT_ID": "your-account-id-here",
        "CLOUDFLARE_D1_DATABASE_ID": "your-d1-database-id-here",
        "CLOUDFLARE_VECTORIZE_INDEX": "mcp-memory-index",
        "MCP_MEMORY_BACKUPS_PATH": "C:\\Users\\your-username\\AppData\\Local\\mcp-memory\\backups",
        "MCP_MEMORY_SQLITE_PATH": "C:\\Users\\your-username\\AppData\\Local\\mcp-memory\\backups\\sqlite_vec.db"
      }
    }
  }
}
```

### 第 4 步：配置 Claude Code
```bash
cd C:/REPOSITORIES/mcp-memory-service
claude mcp add memory python \
  -e MCP_MEMORY_STORAGE_BACKEND=cloudflare \
  -e CLOUDFLARE_API_TOKEN=your-api-token-here \
  -e CLOUDFLARE_ACCOUNT_ID=your-account-id-here \
  -e CLOUDFLARE_D1_DATABASE_ID=your-d1-database-id-here \
  -e CLOUDFLARE_VECTORIZE_INDEX=mcp-memory-index \
  -e MCP_MEMORY_BACKUPS_PATH="C:\Users\your-username\AppData\Local\mcp-memory\backups" \
  -e MCP_MEMORY_SQLITE_PATH="C:\Users\your-username\AppData\Local\mcp-memory\backups\sqlite_vec.db" \
  -- -m mcp_memory_service.server
```

### 第 5 步：验证
- **Claude Desktop**：重启 → 新对话 → “Check memory health”。
- **Claude Code**：`claude mcp list` 应显示 memory 服务已连接。

## 🔧 模板

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["-m", "mcp_memory_service.server"],
      "cwd": "C:/REPOSITORIES/mcp-memory-service",
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "cloudflare",
        "CLOUDFLARE_API_TOKEN": "YOUR_TOKEN_HERE",
        "CLOUDFLARE_ACCOUNT_ID": "YOUR_ACCOUNT_ID_HERE",
        "CLOUDFLARE_D1_DATABASE_ID": "YOUR_D1_DATABASE_ID_HERE",
        "CLOUDFLARE_VECTORIZE_INDEX": "mcp-memory-index",
        "MCP_MEMORY_BACKUPS_PATH": "C:\\Users\\USERNAME\\AppData\\Local\\mcp-memory\\backups",
        "MCP_MEMORY_SQLITE_PATH": "C:\\Users\\USERNAME\\AppData\\Local\\mcp-memory\\backups\\sqlite_vec.db"
      }
    }
  }
}
```

### `.env`
```bash
MCP_MEMORY_STORAGE_BACKEND=cloudflare
CLOUDFLARE_API_TOKEN=YOUR_TOKEN_HERE
CLOUDFLARE_ACCOUNT_ID=YOUR_ACCOUNT_ID_HERE
CLOUDFLARE_D1_DATABASE_ID=YOUR_D1_DATABASE_ID_HERE
CLOUDFLARE_VECTORIZE_INDEX=mcp-memory-index
CLOUDFLARE_R2_BUCKET=mcp-memory-content
CLOUDFLARE_EMBEDDING_MODEL=@cf/baai/bge-base-en-v1.5
CLOUDFLARE_LARGE_CONTENT_THRESHOLD=1048576
CLOUDFLARE_MAX_RETRIES=3
CLOUDFLARE_BASE_DELAY=1.0
MCP_MEMORY_BACKUPS_PATH=C:\Users\USERNAME\AppData\Local\mcp-memory\backups
MCP_MEMORY_SQLITE_PATH=C:\Users\USERNAME\AppData\Local\mcp-memory\backups\sqlite_vec.db
LOG_LEVEL=INFO
```

## ✅ 验证命令
```bash
cd C:/REPOSITORIES/mcp-memory-service
python -c "from src.mcp_memory_service.config import STORAGE_BACKEND; print(STORAGE_BACKEND)"
python scripts/validation/diagnose_backend_config.py
```

### 健康检查示例
```json
{
  "statistics": {
    "backend": "cloudflare",
    "storage_backend": "cloudflare",
    "total_memories": 1073,
    "vectorize_index": "mcp-memory-index",
    "d1_database_id": "f745e9b4-ba8e-4d47-b38f-12af91060d5a"
  },
  "performance": {
    "server": { "storage_type": "CloudflareStorage" }
  }
}
```

若看到 `sqlite-vec`，说明回退到本地，需要重新检查。

## 🚨 故障排查

| 现象 | 可能原因 | 解决 |
| --- | --- | --- |
| 健康检查显示 sqlite-vec | env 未加载 | 确认 `cwd`、`env`、重启应用 |
| 提示缺少变量 | `.env` 或系统变量未生效 | 使用 `python -c` 检查 os.getenv |
| 双端计数不一致 | 使用不同后端 | 重新配置，确保均指向 Cloudflare |
| 连接失败 | Token 权限不足 / ID 错误 | 调用 Cloudflare API 验证 Token、列出资源 |

## 🔄 从 SQLite-vec 迁移
```bash
python scripts/export_sqlite_vec.py --output cloudflare_export.json
# 切换后端
python scripts/import_to_cloudflare.py --input cloudflare_export.json
```

## 📝 配置策略

- 单一真源：Claude Desktop config + `.env`。
- 优先级：MCP server `env` > 系统变量 > `.env` > 默认值。

## 🎯 成功判定

- `backend=cloudflare`。
- `storage_type=CloudflareStorage`。
- Claude Desktop / Claude Code 记忆数一致。
- D1 / Vectorize ID 相同。

完成后，两端记忆自动保持同步。
