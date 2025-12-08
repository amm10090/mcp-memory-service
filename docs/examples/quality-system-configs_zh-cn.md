# 记忆质量系统示例配置

> **版本**：8.48.3  
> **更新**：2025-12-08  
> **参考**：[记忆质量指南](../guides/memory-quality-guide.md)，[评估报告](https://github.com/doobidoo/mcp-memory-service/wiki/Memory-Quality-System-Evaluation)

本文提供经过验证的配置示例，覆盖不同场景，并考虑 v8.48.3 中发现的 ONNX 模型限制。

---

## 配置 1：默认（推荐大多数用户）

**场景**：常规使用，但知晓模型限制

```bash
# .env
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=local           # 仅本地 ONNX
MCP_QUALITY_BOOST_ENABLED=false         # 质量增强保持可选
MCP_QUALITY_BOOST_WEIGHT=0.3            # 开启时用 30%

# 提醒：
# - 分数可能因自匹配产生偏置
# - 仅用于相对排序，不做绝对阈值
# - 做保留/删除前请人工确认
```

**原因**：零成本、隐私完整；分数可用于相对排序；避免过度依赖可能偏置的绝对分数。

**适用**：<10,000 记忆的小中型库、成本敏感、隐私优先。

---

## 配置 2：质量增强（大库）

**场景**：大规模库且质量差异大

```bash
# .env
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=local
MCP_QUALITY_BOOST_ENABLED=true          # 开启质量增强
MCP_QUALITY_BOOST_WEIGHT=0.3            # 质量 30%，语义 70%

# 备注：v8.48.3 实测排名提升 0-3%
# 更有价值的情况：
# - >10,000 条记忆
# - 质量差异显著
# - 查“最佳实践/权威”内容
```

**原因**：时延增加很小（+17%，约 6.5ms）；仍为零成本；大库中有小幅可测提升。

**适用**：>10k 记忆、质量层次多、重度文档/研究场景。

---

## 配置 3：隐私优先（无 AI 评分）

**场景**：最大隐私，仅用隐式信号

```bash
# .env
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=none            # 关闭所有 AI 评分
# 不下载模型，不发 API 请求

# 质量仅由隐式信号构成：
# - 访问频次 40%
# - 最近性 30%
# - 检索排名 30%
```

**原因**：无模型、无外部调用；仍可利用使用模式；开销极低。

**适用**：离线/隔离环境，严格隐私，资源受限。

---

## 配置 4：混合策略（Phase 2，计划中）

**场景**：用 ONNX + 隐式信号获得更可靠分数

```bash
# 未来配置（Issue #268）
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=local
MCP_QUALITY_HYBRID_ENABLED=true         # 启用混合评分

# 拟定公式：
# quality = 0.30*onnx + 0.25*access + 0.20*recency + 0.15*tags + 0.10*completeness
```

**为何更好**：降低对单模型依赖；纳入真实使用信号；缓解自匹配偏置。  
**状态**：计划中（Phase 2，约 1-2 周）。

---

## 配置 5：云端增强（可选）

**场景**：接受 API 成本，想要更好的质量判定

```bash
# .env
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=auto            # 逐层尝试
GROQ_API_KEY="your-groq-api-key"        # Groq 作为二层

# 行为：
# 1. 尝试本地 ONNX（约 99% 成功）
# 2. 失败回退 Groq
# 3. 最终回退隐式信号

# 费用：典型使用 ~$0.30-0.50/月
```

**原因**：本地优先，云端兜底；Groq 提升质量评估；API 调用需显式开启，隐私可控。

**适用**：商业/专业用户，有小额云预算，期望更准的质量评估。

---

## 配置 6：LLM 评审（Phase 3，计划中）

**场景**：为高价值记忆做“绝对质量”评审

```bash
# 未来配置（Issue #268）
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=llm_judge       # LLM 评审模式
GROQ_API_KEY="your-groq-api-key"

# LLM 按结构化提示评估：
# - 具体性、准确性、完整性、相关性/时效

# 成本：~$0.05-0.10 / 1000 条（批量评审）
```

**为何更好**：LLM 能理解上下文与细节；做绝对质量判定，无自匹配偏置。  
**状态**：计划中（Phase 3，1-3 个月）。

---

## 配置 7：保守保留（尽量不丢数据）

**场景**：宁可多留，不想错删有价值记忆

```bash
# .env
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=local

# 保守保留期
MCP_QUALITY_RETENTION_HIGH=730          # 高质量 2 年
MCP_QUALITY_RETENTION_MEDIUM=365        # 中质量 1 年
MCP_QUALITY_RETENTION_LOW_MIN=180       # 低质量最少 6 个月

# 提醒：因自匹配偏置，高分/低分都需谨慎
```

**原因**：在分数不可靠时更安全；延长保留窗口。  
**适用**：关键知识库、档案/研究项目、倾向“先保留后复查”。

---

## 配置 8：激进清理（最小化存储）

**场景**：只保留最优记忆

```bash
# .env
MCP_QUALITY_SYSTEM_ENABLED=true
MCP_QUALITY_AI_PROVIDER=local

# 激进保留期
MCP_QUALITY_RETENTION_HIGH=180          # 高质量 6 个月
MCP_QUALITY_RETENTION_MEDIUM=90         # 中质量 3 个月
MCP_QUALITY_RETENTION_LOW_MIN=30        # 低质量最少 1 个月

# ⚠️ 风险：自匹配偏置可能误删有用记忆
# 建议：归档前人工复核
# 可用 analyze_quality_distribution() 查看 Bottom 10
```

**风险点**：可能误删真正有用的记忆；ONNX 分数非绝对；缺少用户反馈验证。  
**适用**：存储极度受限、临时性知识；**仅在人工复核后使用**。

---

## 监控与验证

无论选哪种配置，做决定前都应**验证**质量分数。

### 1. 每周检查
```bash
analyze_quality_distribution()
# v8.48.3 期望输出：
# - 高 (≥0.7): 32.2%（含 ~25% 伪高分）
# - 中 (0.5-0.7): 27.4%
# - 低 (<0.5): 40.4%
```

### 2. 每月复盘
```bash
# 1) 核查 Top 10 是否真实有用
analyze_quality_distribution() | grep "Top 10"

# 2) 核查 Bottom 10 是否应归档
analyze_quality_distribution() | grep "Bottom 10"

# 3) 归档前手动标注
rate_memory(content_hash="...", rating=-1, feedback="Actually useful, ONNX scored wrong")
```

### 3. 季度审计
```bash
# 抽样各质量层级，人工打分
# 对比 AI 分数与人工相关性
# 目标相关性 >0.7；当前 ~0.5-0.6（受自匹配偏置影响）
```

---

## 迁移路径

### 从 v8.45.0 升级到 v8.48.3（当前）
- 增加 ONNX 限制说明；最佳实践加入人工验证；质量增强保持可选。  
- 兼容性：无需额外操作。

**建议**：阅读 [评估报告](https://github.com/doobidoo/mcp-memory-service/wiki/Memory-Quality-System-Evaluation)。

### 升级到 Phase 2（混合评分）
- 计划：ONNX + 隐式信号混合；用户反馈；A/B 测试框架。  
- 迁移：
```bash
export MCP_QUALITY_HYBRID_ENABLED=true
export MCP_QUALITY_USER_FEEDBACK_ENABLED=true
# 现有分数将按新公式重算
```

### 升级到 Phase 3（LLM 评审）
- 计划：LLM 绝对评估、质量驱动生命周期、改进查询生成。  
- 迁移：
```bash
export MCP_QUALITY_AI_PROVIDER=llm_judge
export GROQ_API_KEY="your-key"
# 可选择批量重新评估存量记忆
```

---

## 常见问题排查

### 问题 1：分数几乎都是 1.0
- **原因**：标签生成查询导致自匹配偏置。  
- **处理**：理解为已知现象；仅用于相对排序；结合隐式信号；等待 Phase 2 混合评分。

### 问题 2：平均分很低（0.469）
- **原因**：双峰分布（大量 1.0 与 0.0，中段少）。  
- **处理**：属模型限制，非 bug；Phase 2/3 会改进（Issue #268）。

### 问题 3：质量增强无明显提升
- **原因**：前排结果本身已高质量，实测差异 0-3%。  
- **处理**：保持默认关闭；仅在大库或特定查询时开启：
```bash
export MCP_QUALITY_BOOST_ENABLED=false
retrieve_with_quality_boost(query="best practices", quality_weight=0.5)
```

---

## 最佳实践摘要

1. 先用默认配置。  
2. 仅在需要时开启质量增强（>10k 记忆）。  
3. 归档前必须人工验证。  
4. 分数用于相对排序，不设硬阈值。  
5. 每月用 `analyze_quality_distribution()` 监控。  
6. 重要记忆提供人工评分。  
7. 持续关注 Issue #268 的 Phase 2/3 进展。

---

## 相关文档
- [记忆质量指南](../guides/memory-quality-guide.md)
- [评估报告](https://github.com/doobidoo/mcp-memory-service/wiki/Memory-Quality-System-Evaluation)
- [Issue #268](https://github.com/doobidoo/mcp-memory-service/issues/268) - 计划改进
- [CLAUDE.md](../../CLAUDE.md) - 快速参考

---
如有问题，请在 https://github.com/doobidoo/mcp-memory-service/issues 提交 Issue。
