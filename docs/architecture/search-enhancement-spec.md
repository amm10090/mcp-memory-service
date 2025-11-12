# 高级混合搜索增强规格

- **版本**：1.0（2025-09-20，设计阶段，优先级高）
- 目标：将 MCP Memory Service 从基础搜索升级为企业级知识整合系统，融合语义向量 + 关键词 + 内容关系。

## 现状与局限
- 仅支持单一检索模式；无内容关系与智能扩展；排序简单；缺乏归并。

## 改进目标
1. **混合搜索**：语义 + 关键词双引擎；
2. **内容归并**：自动聚合相关记忆形成主题；
3. **智能排序**：语义/关键词/新鲜度/元数据多信号排序；
4. **关系映射**：构建问题→方案、时间线、上下文连接；
5. **智能查询**：扩展/意图识别/过滤建议。

## 架构要点
- 服务层新增 `enhanced_search`、`build_content_relationships`、`intelligent_query_expansion`、`consolidate_project_content`；
- 存储层需提供 `keyword_search`、`combined_search`、`get_related_memories`（SQLite-vec 用 FTS5+BM25，Chroma / Cloudflare 分别利用原生能力）；
- 新 REST：`/api/search/advanced`、`/api/search/consolidate`、`/api/projects/{id}/overview` 等；
- MCP 工具新增 `advanced_memory_search`。

## 实施路线
### Phase 1（4-6 周）
- 后端实现关键词检索、混合得分；
- 服务层融合算法与查询分析；
- 暴露高级搜索 API/MCP。

### Phase 2（3-4 周）
- 内容关系检测、时间线/问题-方案映射；
- 归并摘要与可视化数据。

### Phase 3（3-4 周）
- 查询扩展、实体/意图识别、过滤建议；
- 项目级整合/多轮搜索策略。

### Phase 4（2-3 周）
- 多信号排序、个性化与 A/B；
- 性能优化/缓存/可观测性并准备上线。

## 性能指标
- 响应 <100ms（混合搜索），归并 <200ms；
- 额外内存 <500MB；
- 支持 100K+ 记忆仍保持亚秒级；
- 兼容所有后端与客户端。

## 成功标准 & QA
- 90%+ 用户满意度、95% 响应 P95<200ms、85% 归并准确率；
- 单测/集成/性能/用户验收全覆盖。

## 上线策略
- Alpha → Beta → 分批放量，配 Feature Flag + fallback；
- 监控延迟/资源，异常自动退回基础搜索。

## 未来扩展
- Learning-to-Rank、推荐、搜索 Analytics、用户行为洞察。

该增强将提供企业级混合搜索、内容关系与智能排名能力，是后续 AI 驱动功能的基础。
