# 记忆整合系统操作指南

**版本**：8.23.0+ ｜ **更新**：2025-11-11 ｜ **状态**：可用于生产

## 快速参考
- 查看调度器状态：`curl http://127.0.0.1:8000/api/consolidation/status`
- 检查 HTTP 服务：`systemctl --user status mcp-memory-http.service`
- 手动触发（HTTP）：
```bash
curl -X POST http://127.0.0.1:8000/api/consolidation/trigger   -H "Content-Type: application/json"   -d '{"time_horizon": "weekly", "immediate": true}'
```

## 实测性能（v8.23.1，2495 条记忆）
| 后端 | 首次运行 | 说明 |
|------|---------|------|
| SQLite-vec | 5-25s | 本地最快 |
| Cloudflare | 2-4min | 受网络影响 |
| Hybrid | 4-6min | 本地 5ms + 云同步 ~150ms/条 |
> 结论：生产推荐 Hybrid，换取多端持久性。

## 报告生成 ⚠️
- 只有 **整合成功完成** 才会生成报告。
- 位置：`~/.local/share/mcp-memory-service/consolidation/reports/`
- 命名：`consolidation_{horizon}_{timestamp}.json`
- 未完成/失败/运行中/从未运行：不会生成。
- 校验：`curl .../status | jq '.jobs_executed'` >0 后，目录应有对应数量报告。

## 自动调度
| 频率 | 时间 | 作用 |
|------|------|------|
| 每日 | 02:00 | 处理近期记忆 |
| 每周 | 周日 03:00 | 发现模式/关联 |
| 每月 | 每月1日 04:00 | 长期整合与归档 |
- 首次定时可查看日志：
```bash
journalctl --user -u mcp-memory-http.service --since "2025-11-12 01:55" | grep consolidation
```

## 三种手动触发
1) **HTTP API**（最快）同上示例。  
2) **MCP 工具**：`mcp__memory__trigger_consolidation(time_horizon="daily", immediate=true)`。
3) **Code Execution API**（最省 tokens）：
```python
from mcp_memory_service.api import consolidate
consolidate('daily')
```
> 建议用 `daily` 做测试，数据量少。

## 监控整合过程
- 实时日志：`journalctl --user -u mcp-memory-http.service -f | grep consolidation`
- 混合后端常见日志：开始 → 处理 N 条 → 更新 metadata → Cloudflare POST 200 ...

## 常见失败原因与处理
- **网络中断/Cloudflare 429**：自动重试；多次失败会中断，本地数据保持，报告不生成。
- **R2/D1 凭据缺失**：检查环境变量与 `.env`。
- **SQLite 锁**：确保未有长事务；重试后仍失败可重启服务。

## 清理与维护
- 报告目录可定期备份或压缩归档。
- 若切换后端（如单机→Hybrid），建议首次手动触发一次 weekly，确保索引与元数据对齐。

## 相关文档
- [质量系统指南](./memory-quality-guide.md)
- [质量示例配置](../examples/quality-system-configs.md)
- [质量 UI 实施文档](../quality-system-ui-implementation.md)
