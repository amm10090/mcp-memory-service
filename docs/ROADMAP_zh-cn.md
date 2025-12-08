# 项目路线图（简版）

> 面向 MCP Memory Service 的高层计划，执行以 Issue / PR 为准。

## Q4 2025 重点
- ✅ 质量系统 Phase 1（v8.48.3）：完成 ONNX 评估与限制披露。
- ⏳ 质量系统 Phase 2：混合评分（ONNX + 隐式信号 + 用户反馈），预计 1-2 周。
- ⏳ 质量系统 Phase 3：LLM 评审（Judge 模式）与批量复评，预计 1-3 个月。
- ⏳ 混合后端性能优化：Cloudflare 同步与冲突回避（Issue #245）。
- ✅ 文档本地化：zh-CN 主干持续更新。

## 质量系统里程碑
- **Phase 1｜完成**：本地 ONNX 默认开启，评估报告发布，质量增强保持可选。
- **Phase 2｜进行中**：
  - 混合评分：ONNX + 访问频次 + 最近性 + 标签/完整度。
  - 用户反馈：👍/👎 权重 2-3× AI 分数。
  - 监测：A/B 对照与分布仪表盘。
- **Phase 3｜规划**：
  - LLM-as-Judge 批量评审（Groq/Gemini），面向高价值记忆。
  - 改进查询生成，降低自匹配偏置。
  - 质量驱动的生命周期（自动复评、动态阈值）。

## 存储与同步
- Hybrid：降低双写冲突与延迟；提供 `safe_cloudflare_update.sh` 防漂移脚本。
- SQLite-vec：默认本地后端，确保 <100ms 查询。
- Cloudflare：加强标签/时间过滤与索引健康检查。

## Web / UX
- 已有：质量徽章、分布图、Top/Bottom 列表。
- 计划：质量评分调试面板、批量复评入口。

## 工程质量
- `pyscn` 静态分析管道（按需）。
- PR 质量门：lint + 单测 + 关键路径集成测试。
- 周期性文档审计，保持中英一致。

## 联系
- 提案/问题：https://github.com/doobidoo/mcp-memory-service/issues
- 紧急修复：标记 `priority/critical` 并 @maintainers。
