# Issue 管理指南

定义 GitHub Issue 从创建到关闭的完整生命周期，统一分诊、跟踪与解决流程。

```
Open → Triage → Assigned → Fix → Closed
     ↘────────────── Not Planned ───────────↗
```

**时间预期**：
- 分诊：48 小时内；
- 分配：优先级高的 1 周内；
- 修复：Critical 24-48h，常规 1-4 周；
- 关闭：发布验证后立即完成。

---

## 1. 分诊流程（48 小时内）
1. **信息完整性**：
   - Bug：复现步骤、环境、日志；
   - Feature：使用场景、期望行为；
   - 性能：指标、数据规模、环境；
2. **标签体系**：`bug/feature/docs/performance/...`、`critical/high/...`、`storage/mcp/http-api/...`、`triage/needs-info/...`；
3. **优先级评估**：Critical（安全/数据损坏）、High（主功能不可用）、Medium（常规需求）、Low（Nice-to-have）；
4. **需要补充信息时**使用模板请求版本、后端类型、堆栈等。

**重复检测**：`gh issue list --search "keyword in:title,body"`，若重复：关闭 + `duplicate` 标签并链接原 Issue。

---

## 2. Issue 与 PR 的联动
- 提交或 PR 描述中使用 `Fixes #123 / Closes #123 / Resolves #123` 自动关闭；
- PR 打开时在 Issue 回复“Fix in progress via #PR”；加 `in-progress` 标签；
- PR 合并后不要立刻关闭 Issue，先加 `fixed-in-main`，待发版确认再收尾。

---

## 3. 关闭准则与模板

| 类型 | 核心条件 |
| --- | --- |
| Bug | 修复在发布中验证、添加测试、防回归；
| Feature | 功能实现 + 文档/示例同步；
| 问题 | 回答完毕，7 天无新回复；
| Not Planned | 超出范围/重复/无法复现/60 天无响应。

**模板示例**：
- **Resolved**：说明发布版本、变更概要、CHANGELOG 链接；
- **Feature Implemented**：附使用说明、文档链接；
- **Not Planned**：解释原因 + 替代方案；
- **Cannot Reproduce**：列举尝试步骤，邀请补充信息；
- **Duplicate**：引用原 Issue，关闭。

关闭后：添加 `released`、移除 `in-progress`、更新 Milestone、链接 CHANGELOG、确认 open 计数刷新。

---

## 4. 发布后的 Issue 清理
1. `gh issue list --label fixed-in-main --state open` 找到已修复待发布的 Issue；
2. 发布后逐条验证 → 使用模板关闭 → 加 `released`；
3. 若涉及文档/FAQ/已知问题列表，及时更新；
4. 编写 Post-Release Checklist（示例已附）。

---

## 5. 标签系统

- **Type**：`bug/feature/enhancement/docs/performance/question`；
- **Priority**：`critical/high/medium/low`；
- **Component**：`storage/mcp/http-api/dashboard/hooks/docs/testing`；
- **Status**：`triage/needs-info/in-progress/fixed-in-main/released/blocked/duplicate/wontfix`；
- **特殊**：`breaking-change/needs-release-notes/good-first-issue/help-wanted/regression`。

示例：Critical Bug → `bug, critical, storage, triage`；低优先级 Feature → `feature, low, http-api, help-wanted`；性能问题 → `performance, high, storage, needs-info`。

---

## 6. GitHub CLI 自动化
```bash
# 查询
gh issue list --label bug,critical
gh issue list --label triage

# 批量加/删标签
gh issue edit 123 456 --add-label released

# 批量关闭
gh issue close 123 456 --comment "Resolved in v8.x.x"

# 创建 Issue
gh issue create --title "Bug..." --body "$(cat bug.md)" --label bug,critical
```

---

## 7. 特殊情形
- **长期 Issue (>30 天)**：每周更新、拆分子任务、加入 Project Board、必要时重新指派；
- **Needs Info**：使用模板请求补充，14 天无回复则提醒、60 天无反馈自动关闭；
- **Stale**：关闭时说明尝试过的步骤，并邀请重新开单。

---

## 8. 与发布流程的衔接
- 发布前 1-2 周：复盘 `in-progress`、确保 PR 合并、标记 `fixed-in-main`；
- 发布时：Issue 引用写入 CHANGELOG/Release Notes；
- 发布后：集中关闭，打 `released` 标签，并监控 1 周内是否有回归。

---

## 9. 沟通准则
- **响应时间**：Critical 24h、High 48h、Medium/Low 1 周、Question 2-3 天；
- **语气**：感谢/具体/透明，避免指责式语言；
- **升级路径**：需架构决策 → 标 `needs-discussion` + 开 Discussion；超出范围 → 解释原因并提供替代方案。

---

## 10. 指标与监控
- **健康阈值**：`triage` <10%、无标签 Issue <20、Bug 平均关闭时间 <30 天、重复率 <5%；
- **月度复盘命令**：统计标签分布、无标签 Issue、Open Issue 平均年龄、当月关闭数量等（示例命令与 jq 已列出）。

---

**最后更新**：2025-11-05  
**相关文档**：[PR Review Guide](pr-review-guide.md) · [Release Checklist](release-checklist.md) · [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
