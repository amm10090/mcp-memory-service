# 质量系统 UI 实施说明（前端 + API）

> 适用于 v8.45.0+，描述质量徽章/分布图/Top10 UI 的实现要点与接口契约。

## 目标
- 在 Web 控制台展示每条记忆的质量分与提供方。
- 提供分布、提供方占比、Top/Bottom 列表的可视化。
- 与后端质量 API 对齐，避免额外请求开销。

## 数据源
- `/api/quality/memories/{hash}`：单条质量详情。
- `/api/quality/distribution`：分布统计（高/中/低、均值、提供方分布）。
- `/api/quality/top` & `/api/quality/bottom`：Top/Bottom N（v8.45.0+）。
- `/api/search`：返回 `debug_info.quality_score`、`quality_provider`（开启质量增强时）。

## 前端展示
### 1) 记忆卡片
- 徽章：显示 `quality_score`（0.0-1.0），颜色梯度：
  - ≥0.7 绿色高亮
  - 0.5-0.7 蓝色
  - <0.5 灰/橙提示复核
- 提示气泡：显示 provider（ONNX / Groq / Gemini / Implicit）。
- 无分数时展示“未评分”，不阻塞页面。

### 2) 分布面板
- 饼/柱状：高/中/低占比；均值文本。
- 折线：时间序列（若后端返回历史窗口）。
- 提供方占比：ONNX、本地/云比例。

### 3) Top/Bottom 列表
- Top 10 / Bottom 10 按质量排序，显示摘要、标签、更新时间。
- 提供“手动评分”入口，写入 `rate_memory`。

## 交互与性能
- 首屏仅拉取分布接口；Top/Bottom 懒加载。
- 质量徽章数据从搜索结果的 `debug_info` 复用，避免重复请求。
- API 失败时降级显示“质量数据不可用”，不阻塞搜索结果。

## 错误与边界
- 如果 `quality_score` 缺失：显示“未评分”，但允许手动评分入口。
- 如果 provider 为 `ImplicitSignalsEvaluator`：提示“使用隐式信号（未启用 ONNX）”。
- 当质量增强关闭时（默认）：仍可显示已有分布，但不强制 rerank。

## 配置提示
- 开启质量增强：`export MCP_QUALITY_BOOST_ENABLED=true`，前端可显示“质量重排已启用”。
- 提示用户 ONNX 限制：在面板中加入警告文案，避免误用绝对阈值。

## 无障碍与国际化
- 所有颜色同时提供文字标签与数值。
- i18n key 使用 `quality.*` 命名；中文文案已覆盖，其他语言可复用。

## 测试清单
- `tests/test_quality_system.py` 覆盖 API 契约。
- 前端 E2E：
  1) 质量分存在时正确渲染徽章颜色/数值。
  2) 分布接口失败时安全降级。
  3) 手动评分后，列表与分布实时更新。

## 常见问题
- **为什么没有质量分？** 未触发评分或质量系统被禁用；检索一次或启用 `MCP_QUALITY_SYSTEM_ENABLED=true`。
- **分布全部 1.0？** 可能存在自匹配偏置（见质量指南）。
- **UI 卡顿？** 确认 Top/Bottom 懒加载未被提前触发，或缓存开启。

## 参考
- [记忆质量指南](./guides/memory-quality-guide.md)
- [质量示例配置](./examples/quality-system-configs.md)
- 后端 Issue：#260（规格）、#268（改进）
