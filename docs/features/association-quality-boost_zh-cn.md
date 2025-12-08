# 基于关联的质量加权（v8.47.0+）

> 通过“连接数”提升记忆质量分，利用网络效应让高关联记忆获得更长保留与更高权重。

## 概览
- 整合（consolidation）阶段统计每条记忆的关联边数（默认 ≥5）。
- 满足阈值则按倍率提升质量分：`boosted = min(1.0, quality * FACTOR)`。
- 直觉：被多条记忆引用/关联的节点通常更有价值、上下文更充分。

## 公式与默认值
```python
if connection_count >= MIN_CONNECTIONS_FOR_BOOST:
    boosted_quality = min(1.0, quality_score * QUALITY_BOOST_FACTOR)
```
- `MIN_CONNECTIONS_FOR_BOOST`：5（连接数阈值）
- `QUALITY_BOOST_FACTOR`：1.2（提升 20%）
- 质量分封顶 1.0

## 配置
```bash
# 开启/关闭（默认开）
export MCP_CONSOLIDATION_QUALITY_BOOST_ENABLED=true
# 触发阈值（建议 3-10）
export MCP_CONSOLIDATION_MIN_CONNECTIONS_FOR_BOOST=5
# 提升系数（1.0-2.0）
export MCP_CONSOLIDATION_QUALITY_BOOST_FACTOR=1.2
```
**调优示例**
- 保守：`MIN=10`, `FACTOR=1.1`
- 默认：`MIN=5`, `FACTOR=1.2`
- 激进：`MIN=3`, `FACTOR=1.3`

## 对生命周期的影响
1) **相关性计算**：质量进入 `quality_multiplier = 1 + quality*0.5`，提升后可让综合相关性小幅上升（示例：0.5→0.6 约 +4%）。
2) **保留策略**：
   - 高质(≥0.7)：365 天；中质(0.5-0.7)：180 天；低质(<0.5)：30-90 天。
   - 20% 提升可让 0.6→0.72 跨入高质档，延长保留。
3) **抗遗忘**：同上阈值用于判定归档；提升后更难被归档。

## 数据持久化
- 提升后的质量分写入 metadata，随同步/备份保存。
- 控制台与 API 中可见最新分值。

## 监控与验证
- 每周查看分布：`analyze_quality_distribution()`，留意高分比例是否因偏置过高。
- 手动抽查 Top/Bottom 10，必要时人工评分矫正。

## 建议与限制
- 仅对“关联度高”的记忆生效，避免对孤立节点误判。
- 与 ONNX 质量分一样，只适合相对排序；重要归档前需人工确认。
- 过高的 FACTOR 或过低的阈值会放大噪声，建议从默认值开始逐步调整。

## 常见问题
- **为何分数突然升高？** 关联数超过阈值被加权；可调大 `MIN_CONNECTIONS_FOR_BOOST`。
- **会不会误伤？** 质量分受上限 1.0 控制且只加不减；谨慎使用高倍率。
- **如何关闭？** `export MCP_CONSOLIDATION_QUALITY_BOOST_ENABLED=false`。
