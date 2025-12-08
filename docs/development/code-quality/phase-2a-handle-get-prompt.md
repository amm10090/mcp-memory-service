# Phase 2A: getPrompt 处理方案（摘要）

## 问题
- 某些客户端在调用 `getPrompt` 时遇到质量评分缺失或延迟，导致上下文不稳定。

## 目标
- 确保 `getPrompt` 返回的上下文已包含最新质量元数据。
- 降低调用时延，避免阻塞主流程。

## 方案要点
1) **异步质量评分**：保持后台评分，不阻塞 `getPrompt`；若无分数则回退 0.5。
2) **缓存**：在内存中缓存最近的质量分与 provider，TTL 可配置（默认 5 分钟）。
3) **幂等更新**：重复调用不重复触发评分任务。
4) **调试标记**：`debug_info` 返回质量来源与是否重排。

## 实施步骤
- API 层：`getPrompt` 增加质量元数据字段（score/provider/updated_at）。
- 服务层：添加轻量缓存，命中则直接返回；未命中触发异步评分任务。
- 错误处理：评分失败时记录日志，不影响主响应。

## 配置
```bash
export MCP_QUALITY_PROMPT_CACHE_TTL_SECONDS=300
export MCP_QUALITY_PROMPT_FALLBACK_SCORE=0.5
```

## 验收
- `getPrompt` 在无分数时返回 fallback，后续评分写回。
- 调试信息可看到是否使用缓存、是否触发重排。
- 时延对比：启用缓存后 P95 < 80ms。

## 后续
- 与混合评分（Phase 2B）对接，统一质量来源。
- 在 UI 中暴露“质量准备状态”以提升可观测性。
