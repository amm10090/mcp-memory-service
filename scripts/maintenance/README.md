# 维护脚本说明（Maintenance Scripts）

> 本目录包含 MCP Memory Service 的维护与诊断脚本。以下按用途/性能/场景快速索引，详细用法见各节。

## 快速索引

| 脚本 | 作用 | 性能 | 适用场景 |
|------|------|------|-----------|
| [`check_memory_types.py`](#check_memory_typespy) | 查看类型分布 | <1s | 健康检查，整合前/后对比 |
| [`consolidate_memory_types.py`](#consolidate_memory_typespy) | 归并碎片类型 | ~5s/1000 更新 | 类型治理、降噪 |
| [`regenerate_embeddings.py`](#regenerate_embeddingspy) | 重算全部嵌入 | ~5min/2600 条 | 迁移后或嵌入损坏 |
| [`fast_cleanup_duplicates.sh`](#fast_cleanup_duplicatessh) | 快速去重 | <5s/100+ | 批量清理重复 |
| [`find_all_duplicates.py`](#find_all_duplicatespy) | 扫描近似重复 | <2s/2000 | 重复检测与分析 |
| [`find_duplicates.py`](#find_duplicatespy) | API 去重 | ~90s/条 | 需精细判定的重复 |
| [`repair_sqlite_vec_embeddings.py`](#repair_sqlite_vec_embeddingspy) | 修复嵌入损坏 | 视规模 | SQLite-vec 修复 |
| [`repair_zero_embeddings.py`](#repair_zero_embeddingspy) | 修复全零嵌入 | 视规模 | 嵌入异常修复 |
| [`cleanup_corrupted_encoding.py`](#cleanup_corrupted_encodingpy) | 修复编码问题 | 视规模 | 编码损坏修复 |

## 详细说明

### `check_memory_types.py`
**用途**：快速统计数据库中的记忆类型分布。  
**推荐时机**：整合前后对比、常规健康检查、排查类型碎片。  
**用法**：
```bash
python scripts/maintenance/check_memory_types.py
# macOS/Linux 如需修改脚本内数据库路径
```
**特性**：前 30 热门类型、总数/唯一数、空类型标记 `(empty/NULL)`，只读安全。

### `consolidate_memory_types.py`
**用途**：将碎片化类型归并到标准 24 类。  
**何时使用**：
- 同义类型混杂（bug-fix/bugfix/technical-fix 等）
- 大量仅 1-2 条的稀疏类型
- 外部导入后命名不一致
- 定期治理（建议月度）
**用法**：
```bash
# 预览（只读）
python scripts/maintenance/consolidate_memory_types.py --dry-run
# 执行
python scripts/maintenance/consolidate_memory_types.py
# 自定义映射
python scripts/maintenance/consolidate_memory_types.py --config custom_mappings.json
```
**性能**：约 5s/1000 更新（2025-11 实测 1,049 更新用时 5s）。  
**安全**：自动备份、dry-run、事务回滚、锁检测、HTTP 服务警告、磁盘空间检查。  
**标准 24 类**：
- 内容：`note`, `reference`, `document`, `guide`
- 活动：`session`, `implementation`, `analysis`, `troubleshooting`, `test`
- 产物：`fix`, `feature`, `release`, `deployment`
- 进度：`milestone`, `status`
- 基础设施：`configuration`, `infrastructure`, `process`, `security`, `architecture`
- 其他：`documentation`, `solution`, `achievement`, `technical`

### `regenerate_embeddings.py`
**用途**：重算全部嵌入（向量化）。  
**场景**：更换模型 / 余弦迁移后 / 嵌入损坏。  
**性能**：约 5 分钟处理 2600 条（依赖模型与硬件）。

### `fast_cleanup_duplicates.sh`
**用途**：快速删除明显重复。  
**场景**：批量清理，目标是“速度优先”。

### `find_all_duplicates.py`
**用途**：基于内容相似度寻找近似重复，速度快，适合初筛。  
**性能**：<2s/2000 条。

### `find_duplicates.py`
**用途**：通过 API 逐条确认的重复检测，精度高但慢（~90s/条）。

### `repair_sqlite_vec_embeddings.py`
**用途**：修复 sqlite-vec 嵌入损坏。  
**注意**：耗时随数据量变化，建议先备份。

### `repair_zero_embeddings.py`
**用途**：修复全零嵌入记录。  
**使用**：在发现 0 向量时运行。

### `cleanup_corrupted_encoding.py`
**用途**：修复文本编码损坏。  
**适用**：导入含异常编码的历史数据时。

## 通用前置
```bash
# 停止 HTTP 服务（如使用）
systemctl --user stop mcp-memory-http.service
# 断开 MCP 客户端（Claude Code /mcp）
# 确认磁盘空间 >= 数据库 2 倍
```

## 故障恢复
```bash
# 自动备份恢复
cp ~/.local/share/mcp-memory/sqlite_vec.db.backup-TIMESTAMP    ~/.local/share/mcp-memory/sqlite_vec.db
```

## 关联文档
- `scripts/maintenance/memory-types.md`
- `scripts/sync/check_drift.py`
- `docs/guides/memory-consolidation-guide.md`
- `docs/features/association-quality-boost.md`
