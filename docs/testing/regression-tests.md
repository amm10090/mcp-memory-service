# 回归测试手册

目的：确保关键缺陷不复发、性能优化不退步、跨平台问题提前捕获，并验证 MCP/HTTP/存储后端等集成点。

## 测试类别
1. 数据库锁与并发
2. 存储后端完整性
3. Dashboard 性能
4. 标签过滤正确性
5. MCP 协议兼容性

### 示例：并发启动
- 前置：`.env` 写入 `MCP_MEMORY_SQLITE_PRAGMAS=busy_timeout=15000,journal_mode=WAL`；
- 步骤：同时启动 3 个 Claude 实例、运行 `/mcp` 并各执行写入；
- 预期：无 “database is locked”，健康检查通过；
- 证据：`grep -i "database is locked" ~/Library/Logs/Claude/mcp-server-memory.log`，`sqlite3 ... "PRAGMA busy_timeout;"` 等。

文档中依次列出 Test1~Test10 的步骤、预期、证据收集及判断标准。执行时按照“Setup → Execution → Expected → Evidence → Pass/Fail”格式记录，结合脚本或命令行收集日志/统计数据。

附推荐频率：
- 发布前：完整回归；
- PR 合并后：运行受影响模块的测试；
- 周例：自动化性能/标签测试；
- 月例：全套回归并产出报告。

运行建议：
```bash
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
python scripts/database/reset_database.py --confirm
pytest tests/unit/test_exact_tag_matching.py
```

如发现失败，创建带 `regression` 标签的 Issue，附复现步骤、证据与关联 PR/Commit。

**最后更新**：2025-11-05 · 版本 1.0 · 相关：`docs/development/release-checklist.md`、`docs/development/pr-review-guide.md`
