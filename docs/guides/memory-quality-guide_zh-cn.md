# 记忆质量系统指南

> **版本**：8.48.3  
> **状态**：可用于生产（存在已知限制）  
> **特性**：受 Memento 启发的质量系统（Issue #260）  
> **评估**：[质量系统评估报告](https://github.com/doobidoo/mcp-memory-service/wiki/Memory-Quality-System-Evaluation)

## 概览

**Memory Quality System** 将 MCP Memory Service 从“静态存储”提升为“会学习的记忆系统”。它会自动为记忆打分，并将分数用于提高检索精准度、整合效率与整体智能。

### 关键收益

- ✅ **检索精准度提升 40-70%**（Top-5 有用率：50% → 70-85%）
- ✅ **本地 SLM 零成本**（隐私、离线均可）
- ✅ **更聪明的整合**：高质量记忆保留更久
- ✅ **质量增强搜索**：结果优先展示高分记忆
- ✅ **自动学习**：根据使用模式持续优化

## 工作原理

### 多层级 AI 评分（本地优先）

系统通过多层回退链为记忆打 0.0-1.0 的质量分：

| 层级 | 提供方 | 成本 | 时延 | 隐私 | 默认 |
|------|--------|------|------|------|------|
| **1** | **本地 SLM (ONNX)** | **$0** | **50-100ms** | ✅ 完全本地 | ✅ 默认 |
| 2 | Groq API | ~$0.30/月 | 900ms | ❌ 外部 | ❌ 需开启 |
| 3 | Gemini API | ~$0.40/月 | 2000ms | ❌ 外部 | ❌ 需开启 |
| 4 | 隐式信号 | $0 | 10ms | ✅ 完全本地 | 回退 |

**默认配置**：仅用本地 SLM（零成本、隐私、无外部请求）。

### 质量分组成

```
quality_score = (
    local_slm_score × 0.50 +      # 交叉编码器评价
    implicit_signals × 0.50       # 使用模式
)

implicit_signals = (
    access_frequency × 0.40 +     # 被检索频率
    recency × 0.30 +              # 最近访问时间
    retrieval_ranking × 0.30      # 结果排名平均位置
)
```

## ⚠️ ONNX 模型限制（重要，v8.48.3 更新）

基于 4,762 条记忆的评估，我们确认本地 ONNX 模型存在显著限制。

### 模型原始定位

ONNX 模型 `ms-marco-MiniLM-L-6-v2` 是**用于查询-文档相关性排序的交叉编码器**，而非绝对质量评估模型。

**适用场景**：
```python
# ✅ 适合：给搜索结果做相关性排序
query = "How to fix hook connection?"
results = search(query)
ranked = onnx_model.rank(query, results)  # 相对排序
```

**不适用**：
```python
# ❌ 问题：用于“绝对质量”打分
memory = get_memory("abc123...")
quality = onnx_model.evaluate(memory)  # 可能产生偏置
```

### 已知问题

#### 1. 自匹配偏置

- **现象**：评估时如果从标签生成查询，查询会与记忆内容高度重合，导致分数虚高（常见 1.0）。
- **影响**：约 **25%** 的记忆因自匹配得到满分。

#### 2. 双峰分布

- **观察**：分数集中在 1.0 或 0.0，平均值 **0.469**（期望 0.6-0.7）。
- **原因**：模型为相关性排序训练，用于绝对评估时呈现“二值化”倾向。

#### 3. 缺少真实标注

- **问题**：没有用户反馈就无法确认高分是否真的高质量。
- **结果**：无法区分“真正高质量”与“自匹配伪高分”。

### 使用建议

✅ 适合：
- 结果内的**相对排序**（质量重排）
- **对比分析**（哪条记忆更好）
- **趋势观察**（质量随时间是否提升）
- **组合评分**（质量 + 访问频次 + 时序）

❌ 不建议：
- 以绝对阈值做删除/归档（如“<0.5 全部归档”）
- 仅靠质量分做关键决策而无人工验证
- 将分数视作真实标签

### 应对方案

**短期（立即）**
1. 质量增强保持“可选”并默认关闭：
   ```bash
   export MCP_QUALITY_BOOST_ENABLED=false
   ```
2. 与隐式信号混合使用：
   ```python
   final_score = 0.3 * onnx_score + 0.4 * access_count + 0.3 * recency
   ```
3. 重要决策前手工核查底部/顶部样本。

**中期（1-2 周，Issue #268）**
4. 实施混合评分：ONNX + 访问模式 + 新鲜度 + 完整度。
5. 增加用户反馈（👍/👎），权重 2-3 倍于 AI 分数。

**长期（1-3 个月）**
6. 评估 LLM-as-judge（Groq/Gemini）用于绝对质量。
7. 改进查询生成，减少自匹配偏置。

### 性能影响（实测）

**A/B（5 个查询，v8.48.3）：**
- 标准搜索：38.2ms
- 质量增强 0.3：44.7ms（+17%）
- 质量增强 0.5：45.7ms（+20%）

**质量提升**：当本身结果已较好时，排名改进 0-3%。

**建议**：仅在以下场景开启质量增强：
- 10,000+ 规模的大库
- “最佳实践 / 权威”类查询
- 质量差异显著的数据集

### 本地 SLM（一级）

- **模型**：`ms-marco-MiniLM-L-6-v2`（23MB）
- **架构**：交叉编码器（query+memory 同时输入）
- **性能**：CPU 50-100ms；GPU 10-20ms
- **GPU 自动加速**：CUDA / CoreML(MPS) / DirectML，失败则回退 CPU。

## 安装与配置

### 1. 基础安装（仅本地 SLM）

```bash
pip install mcp-memory-service
# 质量系统默认启用，无需 API Key，无外部请求
```

### 2. 可选云端（需手动开启）

```bash
# Groq（快、便宜）
export GROQ_API_KEY="your-groq-api-key"
export MCP_QUALITY_AI_PROVIDER=groq   # 或 auto 逐层回退

# Gemini（Google）
export GOOGLE_API_KEY="your-gemini-api-key"
export MCP_QUALITY_AI_PROVIDER=gemini
```

### 3. 配置项

```bash
# 核心
export MCP_QUALITY_SYSTEM_ENABLED=true         # 默认 true
export MCP_QUALITY_AI_PROVIDER=local           # local|groq|gemini|auto|none

# 本地 SLM
export MCP_QUALITY_LOCAL_MODEL=ms-marco-MiniLM-L-6-v2
export MCP_QUALITY_LOCAL_DEVICE=auto           # auto|cpu|cuda|mps|directml

# 质量增强搜索（可选）
export MCP_QUALITY_BOOST_ENABLED=false         # 默认 false
export MCP_QUALITY_BOOST_WEIGHT=0.3            # 质量权重 0-1

# 基于质量的保留（整合）
export MCP_QUALITY_RETENTION_HIGH=365          # 质量 ≥0.7 保留天数
export MCP_QUALITY_RETENTION_MEDIUM=180        # 0.5-0.7
export MCP_QUALITY_RETENTION_LOW_MIN=30        # <0.5 最短
export MCP_QUALITY_RETENTION_LOW_MAX=90        # <0.5 最长
```

## 使用质量系统

### 1. 自动评分

记忆被检索时后台自动打分：

```bash
claude /memory-recall "what did I work on yesterday"
# 分数写入 metadata，异步非阻塞
```

### 2. 手工评分（可选）

```bash
rate_memory(
    content_hash="abc123...",
    rating=1,  # -1/0/1
    feedback="This was very helpful!"
)
# 手工评分权重 60%，AI 分数 40%
```

HTTP API：
```bash
curl -X POST http://127.0.0.1:8000/api/quality/memories/{hash}/rate   -H "Content-Type: application/json"   -d '{"rating": 1, "feedback": "Helpful!"}'
```

### 3. 质量增强搜索

**全局配置**：
```bash
export MCP_QUALITY_BOOST_ENABLED=true
claude /memory-recall "search query"
```

**按次调用（MCP 工具）**：
```bash
retrieve_with_quality_boost(
    query="search query",
    n_results=10,
    quality_weight=0.3
)
```

**算法**：
1) 过量提取 3× 候选  
2) 重新排序：`0.7 × 语义 + 0.3 × 质量`  
3) 返回前 N

**性能**：<100ms（搜索 50ms + 重排 20ms + 质量评分 30ms）。

### 4. 查看质量指标

MCP 工具：
```bash
get_memory_quality(content_hash="abc123...")
```
HTTP：
```bash
curl http://127.0.0.1:8000/api/quality/memories/{hash}
```

### 5. 质量分析

MCP 工具：
```bash
analyze_quality_distribution(min_quality=0.0, max_quality=1.0)
```

控制台 (http://127.0.0.1:8000/) 显示质量徽章、分布图、提供方占比、Top/Bottom 列表。

## 基于质量的记忆管理

### 1. 整合中的保留策略

| 质量层级 | 区间 | 保留期 |
|----------|------|--------|
| 高 | ≥0.7 | 365 天未访问仍保留 |
| 中 | 0.5-0.7 | 180 天 |
| 低 | <0.5 | 30-90 天（按分数缩放） |

### 2. 质量加权衰减

```
decay_multiplier = 1.0 + (quality_score × 0.5)
final_relevance = base_relevance × decay_multiplier
```

高分记忆衰减更慢，搜索中保持更长时间的相关性。

## 隐私与成本

| 模式 | 配置 | 隐私 | 成本 |
|------|------|------|------|
| 本地 | MCP_QUALITY_AI_PROVIDER=local | ✅ 完全本地 | $0 |
| 混合 | MCP_QUALITY_AI_PROVIDER=auto  | ⚠️ 云回退 | ~$0.30/月 |
| 云端 | MCP_QUALITY_AI_PROVIDER=groq  | ❌ 外部 | ~$0.30/月 |
| 仅隐式 | MCP_QUALITY_AI_PROVIDER=none | ✅ 本地 | $0 |

**建议**：默认本地 SLM（零成本、隐私、快）。

## 性能基准

| 操作 | 时延 | 说明 |
|------|------|------|
| 本地 SLM（CPU） | 50-100ms | 单条评分 |
| 本地 SLM（GPU） | 10-20ms | CUDA/MPS/DirectML |
| 质量增强搜索 | <100ms | 过量提取 + 重排 |
| 隐式信号 | <10ms | 始终快速 |
| 质量元数据写入 | <5ms | 存储写入 |

目标：质量计算开销 <10ms；带增强的搜索 <100ms；全程异步不阻塞用户。

## 故障排查

### 本地 SLM 未生效
- 现象：`quality_provider` 显示 `ImplicitSignalsEvaluator`
- 排查：
  1. `pip install onnxruntime`
  2. 检查模型缓存 `~/.cache/mcp_memory/onnx_models/ms-marco-MiniLM-L-6-v2/`
  3. 查看日志 `tail -f logs/mcp_memory_service.log | grep quality`

### 分数总是 0.5
- 说明：尚未触发评分；先检索触发。

### GPU 未被使用
- 安装 GPU 版 onnxruntime（cuda/mps/directml），或 `export MCP_QUALITY_LOCAL_DEVICE=cuda`。

### 质量增强无效
- 确认已开启：`echo $MCP_QUALITY_BOOST_ENABLED`
- 使用 MCP 工具测试：`retrieve_with_quality_boost(..., quality_weight=0.5)`
- 检查 `debug_info['reranked']`、`debug_info['quality_score']`。

## 最佳实践（v8.48.3）

1. **从默认开始**：本地 SLM + 隐式信号混合，不要单独依赖 ONNX 分数。
2. **逐步开启质量增强**：先关闭收集数据，再低权重试用（0.2），有效再调到 0.3。
3. **监控分布但保持怀疑**：当前分布高分里含 ~25% 自匹配伪高分，重大操作前人工核查。
4. **关键记忆人工标注**：手动 👍/👎，权重 60%。
5. **月度复盘**：检查分布、手工验证 Top/Bottom 10、提供方占比（目标 75%+ 本地）、平均分（当前 0.469，目标 0.6+），关注 Issue #268 进展。

## 高级配置

- **保留策略**：可将高质量保留 2 年，或将低质量最短 2 周。调整 `MCP_QUALITY_RETENTION_*`。
- **质量权重**：`MCP_QUALITY_BOOST_WEIGHT` 0.3（默认）→ 0.5（平衡）→ 0.7（质量优先）。
- **混合云**：`MCP_QUALITY_AI_PROVIDER=auto`，本地失败再用 Groq/Gemini；最后回退隐式信号。

## 成功指标（Phase 1 目标与现状）

| 指标 | 目标 | 现状/测量 |
|------|------|-----------|
| 检索精准度 | Top-5 >70% | 已达 70-85%（测试集） |
| 质量覆盖率 | >30% 记忆有分数 | 当前 95%（4521/4762） |
| 质量分布 | 高质 20-30% | 当前高质 32.2%（含 25% 偏置） |
| 搜索时延 | <100ms（含增强） | 45ms 平均 (+17%) |
| 月成本 | <$0.50 或 0 | 本地默认 $0 |
| 本地 SLM 使用率 | >95% | 当前 75%（其余因模型不可用或云回退） |

## FAQ

- **需要 API Key 吗？** 默认不需要。本地 SLM 零配置。  
- **费用？** 本地 $0；云端约 $0.3-0.5/月。  
- **会变慢吗？** 后台异步；质量重排额外 <20ms。  
- **能关闭吗？** `MCP_QUALITY_SYSTEM_ENABLED=false`。  
- **准确性？** 与人工质量相关性 80%+，适合排序与保留决策（需结合隐式信号）。  
- **模型下载失败？** 自动回退隐式信号，服务不中断。  
- **自定义模型？** 实现 `QualityEvaluator` 并配置 `MCP_QUALITY_AI_PROVIDER`。  
- **离线可用？** 是，本地 SLM 完全离线。

## 相关文档
- [Issue #260](https://github.com/doobidoo/mcp-memory-service/issues/260) - 质量系统规格
- [Issue #261](https://github.com/doobidoo/mcp-memory-service/issues/261) - 路线图
- [记忆整合指南](./memory-consolidation-guide.md)
- [质量 API 参考](../api/quality-endpoints.md)

## 更新记录

**v8.48.3（2025-12-08）**
- 新增 ONNX 限制说明，自匹配偏置与双峰分布
- 补充最佳实践：人工校验、高分谨慎使用
- 加入 4,762 条记忆评测性能数据
- 链接评估报告与 Issue #268（Phase 2 计划）

**v8.45.0**
- 初版质量系统：本地 ONNX、质量驱动整合、质量增强搜索、控制台质量徽章、完整 MCP/HTTP API

---
如需帮助，请在 https://github.com/doobidoo/mcp-memory-service/issues 提交 Issue。
