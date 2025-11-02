# ChromaDB 迁移指南

> **ChromaDB 后端已在 v8.0.0 中移除**。本指南将帮助你迁移到现代存储后端。

## 快速迁移路径

### 方案一：混合后端（推荐）

最适合大多数场景——兼具本地高速读写与云端同步能力。

```bash
# 1. 备份 ChromaDB 数据（在 chromadb-legacy 分支上）
git checkout chromadb-legacy
python scripts/migration/migrate_chroma_to_sqlite.py --backup ~/chromadb_backup.json

# 2. 切换回主分支并配置混合后端
git checkout main
export MCP_MEMORY_STORAGE_BACKEND=hybrid

# 3. 配置 Cloudflare 凭据
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ACCOUNT_ID="your-account"
export CLOUDFLARE_D1_DATABASE_ID="your-d1-id"
export CLOUDFLARE_VECTORIZE_INDEX="mcp-memory-index"

# 4. 安装并验证
python install.py --storage-backend hybrid
python scripts/validation/validate_configuration_complete.py
```

### 方案二：SQLite-vec（纯本地）

适用于无需云同步的单设备场景。

```bash
# 1. 备份并迁移
git checkout chromadb-legacy
python scripts/migration/migrate_chroma_to_sqlite.py

# 2. 配置 SQLite-vec 后端
git checkout main
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec

# 3. 安装
python install.py --storage-backend sqlite_vec
```

### 方案三：Cloudflare（纯云端）

面向不需要本地数据库的云端部署需求。

```bash
# 1. 备份 ChromaDB 数据
git checkout chromadb-legacy
python scripts/migration/migrate_chroma_to_sqlite.py --backup ~/chromadb_backup.json

# 2. 切换到 Cloudflare 后端
git checkout main
export MCP_MEMORY_STORAGE_BACKEND=cloudflare

# 3. 配置 Cloudflare 凭据
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ACCOUNT_ID="your-account"
export CLOUDFLARE_D1_DATABASE_ID="your-d1-id"
export CLOUDFLARE_VECTORIZE_INDEX="mcp-memory-index"

# 4. 将数据迁移至 Cloudflare
python scripts/migration/legacy/migrate_chroma_to_sqlite.py
python scripts/sync/sync_memory_backends.py --source sqlite_vec --target cloudflare
```

## 后端对比

| 功能 | Hybrid ⭐ | SQLite-vec | Cloudflare | ChromaDB（已移除） |
|------|-----------|------------|------------|--------------------|
| **性能** | 本地 5ms | 5ms | 受网络影响 | 15ms |
| **多设备支持** | ✅ 支持 | ❌ 不支持 | ✅ 支持 | ❌ 不支持 |
| **离线可用** | ✅ 支持 | ✅ 支持 | ❌ 不支持 | ✅ 支持 |
| **云备份** | ✅ 自动 | ❌ 无 | ✅ 内置 | ❌ 无 |
| **依赖体量** | 轻量 | 极小 | 无额外 | 庞大（约 2GB） |
| **配置复杂度** | 中等 | 简单 | 中等 | 简单 |
| **状态** | **推荐使用** | 受支持 | 受支持 | **已移除** |

## 迁移脚本详解

### 使用保留的旧版迁移脚本

迁移脚本保存在 legacy 分支：

```bash
# 在 chromadb-legacy 分支
python scripts/migration/migrate_chroma_to_sqlite.py [OPTIONS]

Options:
  --source PATH       Path to ChromaDB data (default: CHROMA_PATH from config)
  --target PATH       Path for SQLite database (default: SQLITE_VEC_PATH)
  --backup PATH       Create JSON backup of ChromaDB data
  --validate          Validate migration integrity
  --dry-run           Show what would be migrated without making changes
```

### 手动迁移步骤

若希望完全手动控制：

1. **从 ChromaDB 导出**：
   ```bash
   git checkout chromadb-legacy
   python -c "
   from mcp_memory_service.storage.chroma import ChromaMemoryStorage
   import json
   storage = ChromaMemoryStorage(path='./chroma_db')
   memories = storage.get_all_memories()
   with open('export.json', 'w') as f:
       json.dump([m.to_dict() for m in memories], f)
   "
   ```

2. **导入至新后端**：
   ```bash
   git checkout main
   python -c "
   from mcp_memory_service.storage.sqlite_vec import SqliteVecMemoryStorage
   import json
   storage = SqliteVecMemoryStorage(db_path='./memory.db')
   await storage.initialize()
   with open('export.json') as f:
       memories = json.load(f)
   for mem in memories:
       await storage.store(Memory.from_dict(mem))
   "
   ```

## 数据校验

迁移完成后，务必核对数据：

```bash
# 检查记忆数量
python -c "
from mcp_memory_service.storage.factory import create_storage_instance
storage = await create_storage_instance('./memory.db')
count = len(await storage.get_all_memories())
print(f'Migrated {count} memories')
"

# 与备份对比
python scripts/validation/validate_migration.py \
    --source ~/chromadb_backup.json \
    --target ./memory.db
```

## 故障排查

### 问题：找不到迁移脚本

**解决方案**：迁移脚本仅存在于 `chromadb-legacy` 分支。
```bash
git checkout chromadb-legacy
python scripts/migration/migrate_chroma_to_sqlite.py
```

### 问题：导入 ChromaMemoryStorage 时报错

**解决方案**：必须切换到 `chromadb-legacy` 分支才能使用 ChromaDB 相关代码。
```bash
git checkout chromadb-legacy  # 可访问 ChromaDB 代码
git checkout main             # v8.0.0+ 已移除 ChromaDB
```

### 问题：提示 “ChromaDB not installed”

**解决方案**：在 legacy 分支安装 chromadb 依赖。
```bash
git checkout chromadb-legacy
pip install chromadb>=0.5.0 sentence-transformers>=2.2.2
```

### 问题：迁移导致时间戳丢失

**解决方案**：运行脚本时添加 `--preserve-timestamps`。
```bash
python scripts/migration/migrate_chroma_to_sqlite.py --preserve-timestamps
```

### 问题：大型 ChromaDB 数据迁移缓慢

**解决方案**：使用批处理模式加速。
```bash
python scripts/migration/migrate_chroma_to_sqlite.py --batch-size 100
```

## 回滚方案

若确需回滚到 ChromaDB（不推荐）：

1. **停留在 v7.x 版本** —— 不要升级到 v8.0.0；
2. **参考 chromadb-legacy 分支**；
3. **从备份恢复**：
   ```bash
   git checkout chromadb-legacy
   python scripts/migration/restore_from_backup.py ~/chromadb_backup.json
   ```

## 迁移后检查清单

- [ ] 已完成备份
- [ ] 迁移脚本运行无报错
- [ ] 新旧后端的记忆数量一致
- [ ] 随机抽查查询结果正确
- [ ] 已更新 `MCP_MEMORY_STORAGE_BACKEND` 配置
- [ ] Legacy ChromaDB 数据目录妥善备份
- [ ] 校验脚本通过
- [ ] 应用/自动化测试通过
- [ ] Claude Desktop/Claude Code 集成正常

## 获取支持

- **迁移问题**：参见 [Issue #148](https://github.com/doobidoo/mcp-memory-service/issues/148)
- **Legacy 分支**： [chromadb-legacy](https://github.com/doobidoo/mcp-memory-service/tree/chromadb-legacy)
- **后端配置**：参见 [STORAGE_BACKENDS.md](./STORAGE_BACKENDS.md)

## 为什么移除 ChromaDB？

- **性能问题**：相较 SQLite-vec 慢约 3 倍（15ms vs 5ms）；
- **依赖体量**：需要下载约 2GB 的 PyTorch 依赖；
- **复杂度**：一次移除 2,841 行代码，降低维护成本；
- **更佳替代方案**：混合后端提供更高性能并支持云同步；
- **维护负担**：减少长期技术债务与升级压力。

移除 ChromaDB 使项目更易维护，同时通过现代后端获得更佳性能体验。
