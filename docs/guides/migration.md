# ChromaDB 迁移至 SQLite-vec 指南

本文将指导你把既有的 ChromaDB 记忆数据迁移到全新的 SQLite-vec 后端。

> **⚠️ 重要更新（v5.0.1）**：我们已修复 v5.0.0 迁移脚本中的关键问题。如在 v5.0.0 遇到故障，请使用增强迁移脚本或升级至 v5.0.1 版本。

## 为什么要迁移？

与 ChromaDB 相比，SQLite-vec 在 MCP Memory Service 场景下具备以下优势：

- **更轻量**：单文件数据库，无外部依赖；
- **更快启动**：无需初始化集合，冷启动时间短；
- **更好的性能**：针对中小规模数据进行优化；
- **部署更简单**：不再维护持久化目录；
- **跨平台一致**：在不同操作系统上表现稳定；
- **HTTP/SSE 支持**：新 Web 控制台仅兼容 SQLite-vec。

## 迁移方式

### 方法一：自动迁移脚本（推荐）

```bash
# 运行迁移脚本
python scripts/migrate_chroma_to_sqlite.py
```

脚本将：

- ✅ 检查现有 ChromaDB 数据；
- ✅ 统计待迁移的记忆数量；
- ✅ 迁移前提示确认；
- ✅ 分批迁移并显示进度；
- ✅ 多次运行时跳过重复数据；
- ✅ 验证迁移结果；
- ✅ 提示后续操作。

### 方法二：手动切换配置

若希望直接启用 SQLite-vec 并重新开始（注意：旧记忆不会自动迁移）：

```bash
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
export MCP_MEMORY_SQLITE_PATH=/path/to/your/memory.db  # 可选
# 重启 MCP Memory Service
```

## 逐步迁移流程

### 1. 备份数据（强烈推荐）

```bash
cp -r ~/.mcp_memory_chroma ~/.mcp_memory_chroma_backup
```

### 2. 执行迁移脚本

```bash
cd /path/to/mcp-memory-service
python scripts/migrate_chroma_to_sqlite.py
```

**示例输出：**
```
🚀 MCP Memory Service - ChromaDB to SQLite-vec Migration
============================================================

📂 ChromaDB source: /Users/you/.mcp_memory_chroma
📂 SQLite-vec destination: /Users/you/.mcp_memory/memory_migrated.db

🔍 Checking ChromaDB data...
✅ Found 1,247 memories in ChromaDB

⚠️  About to migrate 1,247 memories from ChromaDB to SQLite-vec
📝 Destination file: /Users/you/.mcp_memory/memory_migrated.db

Proceed with migration? (y/N): y

🔌 Connecting to ChromaDB...
🔌 Connecting to SQLite-vec...
📥 Fetching all memories from ChromaDB...
🔄 Processing batch 1/25 (50 memories)...
✅ Batch 1 complete. Progress: 50/1,247

... (migration progress) ...

🎉 Migration completed successfully!

📊 MIGRATION SUMMARY
====================================
Total memories found:     1,247
Successfully migrated:    1,247
Duplicates skipped:       0
Failed migrations:        0
Migration duration:       45.32 seconds
```

### 3. 更新配置

```bash
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
export MCP_MEMORY_SQLITE_PATH=/path/to/memory_migrated.db
```

**永久化配置（示例）：**
```bash
echo 'export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec' >> ~/.bashrc
echo 'export MCP_MEMORY_SQLITE_PATH=/path/to/memory_migrated.db' >> ~/.bashrc
```

### 4. 重启并验证

```bash
# 重启 Claude Desktop 或 MCP 服务器
python scripts/verify_environment.py
```

### 5. （可选）启用 HTTP/SSE 控制台

```bash
export MCP_HTTP_ENABLED=true
export MCP_HTTP_PORT=8001
python scripts/run_http_server.py
# 浏览器访问 http://localhost:8001
```

## 配置参考

### 环境变量

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `MCP_MEMORY_STORAGE_BACKEND` | 存储后端（`chroma` 或 `sqlite_vec`） | `chroma` |
| `MCP_MEMORY_SQLITE_PATH` | SQLite-vec 数据库路径 | `~/.mcp_memory/sqlite_vec.db` |
| `MCP_HTTP_ENABLED` | 是否启用 HTTP/SSE | `false` |
| `MCP_HTTP_PORT` | HTTP 端口 | `8001` |

### Claude Desktop 配置示例

```json
{
	"mcpServers": {
		"memory": {
			"command": "uv",
			"args": ["--directory", "/path/to/mcp-memory-service", "run", "memory"],
			"env": {
				"MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec",
				"MCP_MEMORY_SQLITE_PATH": "/path/to/memory_migrated.db"
			}
		}
	}
}
```

## 故障排查

### v5.0.0 常见问题

> 如遇到 v5.0.0 的迁移问题，请使用增强脚本：
> ```bash
> python scripts/migrate_v5_enhanced.py --help
> ```

#### 问题 1：自定义数据路径未被识别

```bash
python scripts/migrate_chroma_to_sqlite.py \
  --chroma-path /your/custom/chroma/path \
  --sqlite-path /your/custom/sqlite.db

export MCP_MEMORY_CHROMA_PATH=/your/custom/chroma/path
export MCP_MEMORY_SQLITE_PATH=/your/custom/sqlite.db
python scripts/migrate_chroma_to_sqlite.py
```

#### 问题 2：`content_hash` 相关报错

- 出现 “NOT NULL constraint failed: memories.content_hash”；
- 请升级至 v5.0.1，并使用增强迁移脚本。

#### 问题 3：标签格式被破坏

- 标签迁移后呈现 `['tag1','tag2']`；
- 使用增强脚本中的标签校验修复：
  ```bash
  python scripts/validate_migration.py /path/to/sqlite.db
  python scripts/migrate_v5_enhanced.py --force
  ```

#### 问题 4：迁移似乎卡住

- 使用详尽模式和批量参数：
  ```bash
  pip install tqdm
  python scripts/migrate_v5_enhanced.py --verbose --batch-size 10
  ```

#### 问题 5：依赖冲突

```bash
pip uninstall chromadb sentence-transformers -y
pip install --upgrade chromadb sentence-transformers
export REQUESTS_CA_BUNDLE=""
export SSL_CERT_FILE=""
```

### 校验与恢复

#### 迁移后校验

```bash
python scripts/validate_migration.py
python scripts/validate_migration.py --compare --chroma-path ~/.mcp_memory_chroma
```

#### 恢复选项

```bash
# 从备份恢复
python scripts/restore_memories.py migration_backup.json

# 临时回退到 ChromaDB
export MCP_MEMORY_STORAGE_BACKEND=chroma

# 清理目标库并重跑增强脚本
rm /path/to/sqlite_vec.db
python scripts/migrate_v5_enhanced.py \
  --chroma-path /path/to/chroma \
  --sqlite-path /path/to/new.db \
  --backup backup.json
```

### 获取帮助

1. 使用 `--verbose` 查看详细日志；
2. 运行 `scripts/validate_migration.py` 检查数据；
3. 在 [GitHub Issues](https://github.com/doobidoo/mcp-memory-service/issues) 反馈问题；
4. 如需应急回退，可直接恢复到 ChromaDB，原数据不会被修改。

### 迁移最佳实践

1. **务必先备份**：`cp -r ~/.mcp_memory_chroma ~/.mcp_memory_chroma_backup`
2. **先执行 Dry-run**：`python scripts/migrate_v5_enhanced.py --dry-run`
3. **迁移后立刻校验**：`python scripts/validate_migration.py`
4. **保留 ChromaDB 数据**：至少保留一周，确认无误再删除。

出现 “Migration verification failed” 表示部分记忆未成功迁移，可根据报告重新执行。

### 运行时常见问题

- **“Storage backend not found”**：确认 `MCP_MEMORY_STORAGE_BACKEND=sqlite_vec`，并安装 SQLite-vec 依赖；
- **“Database file not found”**：检查 `MCP_MEMORY_SQLITE_PATH` 路径与文件权限。

### 性能对比

| 指标 | ChromaDB | SQLite-vec |
| --- | --- | --- |
| 启动耗时 | 约 2-3 秒 | 约 0.5 秒 |
| 内存占用 | 约 100-200MB | 约 20-50MB |
| 存储结构 | 目录 + 多文件 | 单个文件 |
| 依赖 | chromadb、sqlite 等 | 仅 sqlite-vec |
| 扩展能力 | 更适合 >10k 记忆 | 最优于 <10k 规模 |

## 回退方案

```bash
export MCP_MEMORY_STORAGE_BACKEND=chroma
unset MCP_MEMORY_SQLITE_PATH
# 重启服务
```

原始 ChromaDB 数据在迁移过程中保持不变。

## 后续步骤

1. ✅ 测试存储、检索、搜索操作；
2. ✅ 尝试 HTTP/SSE 控制台；
3. ✅ 更新脚本或工具中的路径引用；
4. ✅ 定期备份新的 SQLite-vec 数据库；
5. ✅ 确认成功后再删除旧 ChromaDB 数据。

## 支持

- 检查迁移日志与错误提示；
- 确认环境变量配置正确；
- 建议先用小数据集演练；
- 参考日志定位问题。

迁移后将保留全部数据，包括：

- 记忆内容与元数据；
- 标签与时间戳；
- 内容哈希（用于去重）；
- 语义向量（将按同一模型重新生成）。
