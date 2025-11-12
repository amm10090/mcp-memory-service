# Claude Code 会话 Hook 改进

## 概览
会话启动 Hook 现已优先返回近期记忆，并提供更丰富的上下文，提升 Claude Code 体验。

## 关键改动

1. **多阶段检索**：
   - 阶段 1：最近 7 天，占 60%。
   - 阶段 2：带关键标签（architecture/decisions）。
   - 阶段 3：不足时回退至项目上下文。

2. **强化时序权重**：
   - 近期记忆优先。
   - 指示符：🕒 今日、📅 本周、日期表示更久。
   - 支持 `last-week`、`last-2-weeks`、`last-month`。

3. **分类优化**：
   - 新增 “Recent Work”。
   - 顺序：Recent → Decisions → Architecture → Insights → Features → Context。

4. **语义查询增强**：
   - 注入 Git 信息（分支、提交）。
   - 框架/语言上下文。
   - 结合用户输入。

5. **配置项**：
```json
{
  "memoryService": {
    "recentFirstMode": true,
    "recentMemoryRatio": 0.6,
    "recentTimeWindow": "last-week",
    "fallbackTimeWindow": "last-month"
  },
  "output": {
    "showMemoryDetails": true,
    "showRecencyInfo": true,
    "showPhaseDetails": true
  }
}
```

6. **可视化反馈**：
   - 分阶段日志。
   - 时序标记。
   - 得分展示带时间旗标。
   - 去重提示。

## 效果对比
- 过去：单次查询、无时序、上下文少、分类粗略。
- 现在：多阶段时序优先、Git/框架感知、显示 “Recent Work” 分类及完整上下文。

## 使用说明
默认开启，向后兼容。如需关闭：
```json
{
  "memoryService": {
    "recentFirstMode": false
  }
}
```

## 关联文件
1. `claude-hooks/core/session-start.js`
2. `claude-hooks/utilities/context-formatter.js`
3. `claude-hooks/config.json`
4. `test-hook.js`

## 测试
运行 `node test-hook.js`，可验证：
- 项目识别与上下文构建。
- 多阶段记忆检索。
- 分类与显示。
- Git 上下文注入。
- 时间窗口配置。

## 结果
会话 Hook 现在能优先呈现近期工作，又不遗漏重要架构与历史决策，确保上下文连续性。
