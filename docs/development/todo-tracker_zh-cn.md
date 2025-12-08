# TODO 追踪

- **更新时间**：2025-11-08 10:25:25
- **扫描目录**：`src`
- **TODO 数量**：5

| 优先级 | 数量 | 说明 |
| --- | --- | --- |
| CRITICAL (P0) | 1 | 安全 / 数据损坏 / 阻塞型缺陷 |
| HIGH (P1) | 2 | 性能 / 用户可见 / 未完成功能 |
| MEDIUM (P2) | 2 | 质量优化 / 技术债 |
| LOW (P3) | 0 | 文档 / 外观 / Nice-to-have |

---

## CRITICAL (P0)
- `src/mcp_memory_service/web/api/analytics.py:625` —— 周期过滤未实现，导致统计数据错误。

## HIGH (P1)
- `src/mcp_memory_service/storage/cloudflare.py:185` —— 缺少嵌入生成兜底，外部 API 故障会放大影响。
- `src/mcp_memory_service/web/api/manage.py:231` —— 查询低效，在大数据量下造成瓶颈。

## MEDIUM (P2)
- `src/mcp_memory_service/web/api/documents.py:592` —— 使用 FastAPI 旧式事件钩子，应迁移至 `lifespan`。
- `src/mcp_memory_service/web/api/analytics.py:213` —— `storage.get_stats()` 缺少字段，导致 API 不一致。

## LOW (P3)
- 无。

---

## 处理优先顺序
1. **P0**：立即修复，必要时阻止发布；
2. **P1**：纳入当前/下个迭代；
3. **P2**：加入技术债 Backlog，重构期处理；
4. **P3**：视情况顺手处理。

## 更新方式
运行 `bash scripts/maintenance/scan_todos.sh` 重新生成本列表。
