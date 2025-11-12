# 多客户端部署指南

本指南介绍如何为 MCP Memory Service 配置多客户端访问，使不同应用/设备共享同一记忆库。

## 概览
支持三类模式：
1. 🌟 **集成式安装**（推荐，安装时自动配置）；
2. 📁 **共享文件访问**（局域网共享存储）；
3. 🌐 **集中式 HTTP/SSE 服务器**（团队/云端场景）。

---

## 🌟 集成式安装（推荐）
```bash
python install.py            # 按提示选择 y 以启用多客户端
python install.py --setup-multi-client          # 无需交互
python install.py --skip-multi-client-prompt    # 跳过配置
```
**优势**：自动检测 Claude Desktop、VS Code、Continue、Cursor 等 MCP 客户端；无需手工改配置，后续升级无痛。

### 自动配置的客户端
- Claude Desktop：更新 `claude_desktop_config.json`；
- Continue / VS Code MCP 扩展 / Cursor；
- 通用 MCP 配置（`.mcp.json` 等）。

### 需手动调整
- 定制化或企业 MCP 实现（请参阅对应 IT 指南）。

---

## 📁 共享文件访问（局域网）
适合多台机器共用同一 SQLite 数据库。

1. 运行脚本：`python setup_multi_client_complete.py`
2. 设置共享路径：`export MCP_MEMORY_SQLITE_PATH="/shared/mcp/memory.db"`
3. 各客户端配置该路径、确保读写权限。

SQLite 默认启用 WAL（Write-Ahead Logging），允许多读一写并自动恢复。

Claude Desktop 示例：
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec",
        "MCP_MEMORY_SQLITE_PATH": "/shared/mcp/memory.db"
      }
    }
  }
}
```
要求：可靠的 NFS/SMB 共享、统一权限、网络稳定。

---

## 🌐 集中式 HTTP/SSE 服务器
### 优势
- 并发访问 + SSE 实时推送；
- 跨平台/跨地域；
- API Key + HTTPS；
- 云端友好，无文件锁问题。

### 部署
```bash
git clone https://github.com/doobidoo/mcp-memory-service.git
cd mcp-memory-service
python install.py --server-mode --storage-backend sqlite_vec

export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=8001
export MCP_API_KEY=your-secure-api-key
python scripts/run_http_server.py
```

### 客户端连接
- **Streamable HTTP**（优先）：
```json
{
  "mcpServers": {
    "memory": {
      "transport": "streamablehttp",
      "url": "http://server:8001/mcp",
      "headers": {"Authorization": "Bearer your-secure-api-key"}
    }
  }
}
```
- **mcp-proxy 桥接**（适用于仅支持 stdio 的客户端）：
```json
{
  "mcpServers": {
    "memory": {
      "command": "mcp-proxy",
      "args": ["http://server:8001/mcp", "--transport=streamablehttp"],
      "env": {"API_ACCESS_TOKEN": "your-secure-api-key"}
    }
  }
}
```

### 安全
```bash
export MCP_API_KEY=$(openssl rand -hex 32)
export MCP_HTTPS_ENABLED=true
export MCP_SSL_CERT_FILE=/path/cert.pem
export MCP_SSL_KEY_FILE=/path/key.pem
sudo ufw allow 8001/tcp
sudo ufw allow 8443/tcp
```

### Docker
```yaml
services:
  mcp-memory-service:
    build: .
    ports:
      - "8001:8001"
    environment:
      - MCP_HTTP_HOST=0.0.0.0
      - MCP_HTTP_PORT=8001
      - MCP_API_KEY=${MCP_API_KEY}
      - MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```
`docker-compose up -d` 即可。

---

## 环境变量参考（部分）
| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `MCP_HTTP_ENABLED` | `false` | 启用 HTTP 模式 |
| `MCP_HTTP_HOST` / `PORT` | `0.0.0.0` / `8001` | 监听地址/端口 |
| `MCP_API_KEY` | 无 | HTTP 认证（Bearer） |
| `MCP_MEMORY_STORAGE_BACKEND` | `sqlite_vec` | 也可选 `chroma` / `cloudflare` |
| `MCP_MEMORY_SQLITE_PATH` | 自动 | SQLite-vec DB 路径 |
| `MCP_MEMORY_SQLITE_PRAGMAS` | 无 | 如 `busy_timeout=15000,cache_size=20000` |
| `MCP_MDNS_ENABLED` | `true` | mDNS 广播/发现 |

旧版变量（`MCP_MEMORY_HTTP_HOST` 等）已弃用。

### 性能调优
```bash
# 推荐设置（v8.9.0+，HTTP + MCP 并发）
export MCP_MEMORY_SQLITE_PRAGMAS="busy_timeout=15000,cache_size=20000"
```
HTTP Server 可通过 `MCP_HTTP_WORKERS`、`MCP_HTTP_TIMEOUT` 等调整。

---

## 故障排查
- **database is locked**：提升 busy_timeout，确保 WAL 生效、文件权限正确；
- **无法连通**：`curl http://server:8001/api/health`、检查防火墙；
- **配置不一致**：各客户端确认相同 env/path。

诊断示例：
```bash
python scripts/test_multi_client.py
python -c "import os,sqlite3; db=os.getenv('MCP_MEMORY_SQLITE_PATH'); conn=sqlite3.connect(db); print('OK', db); conn.close()"
netstat -an | grep :8001
```

---

## 迁移
1. 备份：`python scripts/backup_memories.py`；
2. `python install.py --setup-multi-client --migrate-existing`；
3. 或使用 `python scripts/migrate_to_multi_client.py --source ... --target ...`。

相关文档：安装指南、Docker 部署、排障、HTTP/SSE 设计。

---

## 常见客户端示例
- **Codex**：`mcp-proxy` 桥接；
- **Cursor**：本地 stdio / mcp-proxy / Streamable HTTP；
- **Qwen/Gemini**：若原生支持 HTTP 直接配置，否则使用 `mcp-proxy`；
- 所有客户端确保 `Authorization: Bearer <MCP_API_KEY>`，如不支持 HTTP 则使用 `mcp-proxy`。

排障要点：确认使用 `/mcp`（Streamable HTTP），非 `/api/events`；服务器已设置 `MCP_API_KEY`；`curl` 验证健康；必要时使用 `mcp-proxy`。
