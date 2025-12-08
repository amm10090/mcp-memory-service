# Phase 2A: 索引策略（摘要）

## 目标
- 减少质量/搜索相关索引的瓶颈，确保 Hybrid 模式下同步稳定。

## 关键调整
- SQLite-vec 索引：
  - 确保标签、时间字段索引存在。
  - 写入批量事务化，降低锁竞争。
- Cloudflare D1：
  - 增加 `tags(name)` 索引与 `memory_tags` 复合索引。
  - 查询使用 `JOIN + GROUP BY`，支持 AND/OR 与时间过滤。
- 向量索引：保持与内存表一致的内容哈希，避免重复写入。

## 操作指引
- 迁移/初始化脚本应包含索引检查：
```sql
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_memory_tags_id ON memory_tags(memory_id, tag_id);
```
- Hybrid 模式写顺序：先本地，再 Cloudflare；失败时记录补偿任务。

## 验收标准
- 常见查询（标签 AND/OR + 时间范围）P95 < 120ms（本地） / < 300ms（Hybrid）。
- 写入冲突率下降（以 24h 错误日志计）。

## 风险
- 过多索引影响写入性能：保持最小必需集合。
- 跨端不一致：开启 drift 检查脚本 `scripts/sync/check_drift.py`。
