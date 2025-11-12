# SQLite-vec 后端指南

## 概览

SQLite-vec 为 MCP Memory Service 提供轻量且高性能的向量数据库，具有：
- 单文件、无额外依赖。
- 向量操作快、索引高效。
- 易于备份/复制/共享。
- 基于 SQLite，具 ACID 可靠性。
- 内存占用小，适合中小规模记忆库。

## 安装
```bash
pip install sqlite-vec        # 或 uv add sqlite-vec
```
验证：
```python
try:
    import sqlite_vec
    print("✅ sqlite-vec 可用")
except ImportError:
    print("❌ 尚未安装")
```

## 配置
```bash
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
export MCP_MEMORY_SQLITE_PATH=/path/to/memory.db   # 可选
```

### 平台路径建议
- macOS：`~/Library/Application Support/mcp-memory/sqlite_vec.db`
- Windows：`%LOCALAPPDATA%\mcp-memory\sqlite_vec.db`
- Linux：`~/.local/share/mcp-memory/sqlite_vec.db`

Claude Desktop：
```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-service", "run", "memory"],
      "env": { "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec" }
    }
  }
}
```

## 从 ChromaDB 迁移
```bash
python migrate_to_sqlite_vec.py
# 或
python scripts/migrate_storage.py \
  --from chroma --to sqlite_vec \
  --source-path ~/.local/share/mcp-memory/chroma_db \
  --target-path ~/.local/share/mcp-memory/sqlite_vec.db \
  --backup
```
迁移后运行 `python scripts/verify_environment.py` 验证。

## 性能特性
- RAM 使用量较 ChromaDB 下降约 75%。
- 语义检索性能接近，标签/元数据查询更快。
- 启动时间快 2-3 倍。
- 单 `.db` 文件，磁盘占用更小。

## 高级配置

### 自定义嵌入模型
```python
storage = SqliteVecMemoryStorage(
    db_path="memory.db",
    embedding_model="all-mpnet-base-v2"
)
```

### 多客户端访问

- **Phase 1：WAL**（默认）—— 启用 WAL、busy_timeout=5s、`synchronous=NORMAL`。
- **Phase 2：HTTP 协调**—— 自动检测：
  - 存在 HTTP 服务器 → `http_client`。
  - 无服务器且端口空闲 → `http_server`。
  - 端口冲突 → `direct`（WAL）。

常用环境变量：
```bash
export MCP_HTTP_ENABLED=true
export MCP_HTTP_PORT=8001
export MCP_HTTP_HOST=localhost
export MCP_MEMORY_SQLITE_PRAGMAS="busy_timeout=15000,cache_size=20000"
```

Claude Desktop 模式：
1. **自动协调**（推荐）
```json
"env": {"MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec", "MCP_HTTP_ENABLED": "true"}
```
2. **手动 HTTP**：先运行 `python scripts/run_http_server.py`，配置 `MCP_HTTP_ENABLED=false`。
3. **仅 WAL**：`"MCP_MEMORY_SQLITE_PRAGMAS": "busy_timeout=10000"`。

### 数据库优化
```bash
python -c "
import asyncio
from src.mcp_memory_service.storage.sqlite_vec import SqliteVecMemoryStorage
async def main():
    s = SqliteVecMemoryStorage('path/to/db')
    await s.initialize()
    count, _ = await s.cleanup_duplicates()
    print('Removed', count)
    s.conn.execute('VACUUM')
    s.close()
asyncio.run(main())
"
```

### 备份 / 恢复
```bash
cp memory.db memory_backup.db
python scripts/migrate_storage.py --restore backup.json --to sqlite_vec --target-path restored.db
```

## 故障排查
- **ImportError**：安装 `sqlite-vec`。
- **database is locked**：v8.9.0 已自动应用推荐 PRAGMA；如仍冲突，可增加 `busy_timeout`、清理旧 `-wal/-shm` 文件、确认无僵尸进程。
- **HTTP 协调失败**：启用 `LOG_LEVEL=DEBUG` 查看 `detect_server_coordination_mode()` 输出；必要时手动启动 HTTP 服务或关闭 HTTP 回退 WAL。
- **权限问题**：确保 `.db` 文件可写。

## ChromaDB vs SQLite-vec

| 项目 | ChromaDB | SQLite-vec | 推荐 |
| --- | --- | --- | --- |
| 部署复杂度 | 中 | 低 | SQLite-vec |
| 内存占用 | 高 | 低 | SQLite-vec |
| 查询性能 | 优 | 很好 | 视需求 |
| 可移植性 | 差 | 优 | SQLite-vec |
| 备份 | 复杂 | 简单 | SQLite-vec |
| 并发 | 好 | 优（HTTP+WAL） | SQLite-vec |
| 生态 | 丰富 | 成长中 | ChromaDB |

## 最佳实践
- **适用 SQLite-vec**：<10 万条、需多客户端/易备份/资源有限。
- **适用 ChromaDB**：>10 万条、极致性能、需要其高级功能。
- **监控协调模式**：开启 `LOG_LEVEL=INFO` 观察 “Detected coordination mode”。
- **定期优化**：运行 `python scripts/optimize_sqlite_vec.py`、`VACUUM`、批量写入。

## API 兼容性
与 ChromaDB 实现相同 `MemoryStorage` 接口：`store`、`retrieve`、`search_by_tag`、`delete` 等方法无需改动。

## 贡献
- 运行 `pytest tests/test_sqlite_vec_storage.py`。
- 性能测试：`python tests/performance/test_sqlite_vec_perf.py`。
- 新特性遵循 `MemoryStorage` 接口并更新本文档。

## 支持
- 查阅 [sqlite-vec 文档](https://github.com/asg017/sqlite-vec)。
- 复查本文故障排查章节。
- 在仓库提 Issue 并附带日志。
