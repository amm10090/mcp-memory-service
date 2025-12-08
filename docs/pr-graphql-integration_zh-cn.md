# 基于 GraphQL 的 PR 线程管理

**状态**：✅ 已在 v8.20.0 实现  
**动机**：免去手动点击 “Mark as resolved”，降低评审摩擦  
**收益**：修复代码后自动结案线程

---

## 目录
1. [概览](#概览)  
2. [为什么选择 GraphQL](#为什么选择-graphql)  
3. [组件](#组件)  
4. [使用指南](#使用指南)  
5. [自动化集成](#自动化集成)  
6. [故障排查](#故障排查)  
7. [API 参考](#api-参考)

---

## 概览

该系统依赖 GitHub GraphQL API 实现 **PR 审查线程自动管理**：

1. **检测** 哪些代码改动响应了审查意见。
2. **自动解决** 已修复的线程。
3. **附加说明**（引用修复 commit）。
4. **跟踪线程状态**，贯穿多个审查回合。

### 痛点对比

**过去**：
```bash
1. Gemini 审查并生成 30 条行级评论
2. 你修复后 push
3. 在 GitHub UI 里手点 “Resolve” ×30
4. 运行 gh pr comment $PR --body "/gemini review"
5. 循环...
```

**现在**：
```bash
1. Gemini 审查
2. 你修复并 push
3. 一条命令：bash scripts/pr/resolve_threads.sh $PR HEAD --auto
4. 再次触发审查：gh pr comment $PR --body "/gemini review"
5. 循环...
```

或直接使用 `auto_review.sh`，每次修复后自动结案线程。

---

## 为什么选择 GraphQL

### REST API 限制

GitHub REST API **无法** 解决审查线程：
```bash
# ❌ 仅能列出评论，无法 resolve
gh api repos/OWNER/REPO/pulls/PR/comments

# ✅ GraphQL 可完全管理线程
gh api graphql -f query='mutation { resolveReviewThread(...) }'
```

### GraphQL 优势

| 能力 | REST | GraphQL |
| --- | --- | --- |
| 列出评论 | ✅ | ✅ |
| 获取线程状态 | ❌ | ✅ (`isResolved`/`isOutdated`) |
| 线程结案 | ❌ | ✅ (`resolveReviewThread`) |
| 添加回复 | ❌ | ✅ (`addPullRequestReviewThreadReply`) |
| 读取元数据 | ❌ | ✅ |

---

## 组件

### 1. GraphQL Helpers
- **位置**：`scripts/pr/lib/graphql_helpers.sh`
- **作用**：封装常用 GraphQL 操作。

主要方法：
```bash
get_review_threads <PR>
resolve_review_thread <THREAD_ID> [COMMENT]
add_thread_reply <THREAD_ID> <COMMENT>
was_line_modified <FILE> <LINE> <COMMIT>
get_thread_stats <PR>
count_unresolved_threads <PR>
check_graphql_support
```

核心查询示例：
```graphql
query($pr:Int!,$owner:String!,$repo:String!){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$pr){
      reviewThreads(first:100){
        nodes{ id isResolved isOutdated path line }
      }
    }
  }
}
```

```graphql
mutation($threadId:ID!){
  resolveReviewThread(input:{threadId:$threadId}){
    thread{ id isResolved }
  }
}
```

### 2. 智能线程结案工具
- **位置**：`scripts/pr/resolve_threads.sh`
- **用途**：识别修复的线程并自动 resolve。

```bash
bash scripts/pr/resolve_threads.sh <PR> [COMMIT]
# 自动模式
bash scripts/pr/resolve_threads.sh <PR> HEAD --auto
```

决策流程：
```
每个未结案线程：
  若文件在本次提交中被改动：
    若对应行发生变化 → 结案并添加说明
    否则 → 跳过
  若文件未改动但线程被 GitHub 标记为 outdated → 结案
  其余情况 → 跳过
```

自动评论模板：
```markdown
✅ Resolved: Line 123 in file.py was modified in commit abc1234
```

### 3. 线程状态展示
- **位置**：`scripts/pr/thread_status.sh`
- **命令**：
```bash
bash scripts/pr/thread_status.sh <PR> [--unresolved|--resolved|--outdated]
```
- **输出**：总览、统计、逐条详情。

### 4. auto_review.sh 集成
- 检查 GraphQL 能力。
- 每轮显示线程统计。
- push 后自动 resolve。

### 5. watch_reviews.sh 集成
- 启动时检测 GraphQL。
- 每轮轮询展示线程状态。
- 新审查抵达时输出未结案线程。

---

## 使用指南

### 基础流程
1. 查看线程：`bash scripts/pr/thread_status.sh 212`
2. 修复并 push。
3. 自动结案：`bash scripts/pr/resolve_threads.sh 212 HEAD --auto`
4. 触发新审查：`gh pr comment 212 --body "/gemini review"`

### 推荐流程

`auto_review.sh`：
```bash
bash scripts/pr/auto_review.sh 212 5 true
```

`watch_reviews.sh`：
```bash
bash scripts/pr/watch_reviews.sh 212 120
```

### 进阶
- 自定义评论：交互模式逐条输入。
- 程序化查询：`source scripts/pr/lib/graphql_helpers.sh` 后调用 `get_review_threads`。
- 针对某文件筛选：`get_unresolved_threads_for_file`。

---

## 自动化集成

### Gemini PR Automator
- **Phase 1**：创建 PR 后开启 watch 模式。
- **Phase 2**：`auto_review.sh` 自动修复 + resolve + 触发新审查。
- **Phase 3**：手动修复后同样运行 `resolve_threads.sh`。

### 未来：pre-commit 提醒
在 `.git/hooks/pre-commit` 中检测未结案线程，必要时阻止提交。

---

## 故障排查

| 问题 | 现象 | 解决 |
| --- | --- | --- |
| 缺少 helpers | `thread auto-resolution disabled` | 检查 `scripts/pr/lib` 是否存在，必要时从 main 拉取 |
| gh CLI 版本过低 | “GraphQL support requires v2.20.0+” | `gh upgrade` |
| resolve 失败 | `Failed to resolve` | 检查线程 ID、网络、权限 (`gh auth status`) |

更多排障命令：
```bash
gh api graphql -f query='query { viewer { login } }'
```

---

## API 参考

- `get_review_threads`：返回线程 JSON。
- `resolve_review_thread`：执行 GraphQL mutation。
- `add_thread_reply`：追加回复。
- `count_unresolved_threads`：统计未结案数量。

---

## 最佳实践

1. **谨慎自动结案**：仅在确认修复完成时使用。
2. **描述性评论**：用简洁句子解释修复（避免 “Done”）。
3. **先 dry run**：`resolve_threads.sh 212 HEAD` 预览，再 `--auto`。
4. **持续监控**：定期运行 `thread_status.sh`。

---

## 性能

- GraphQL 速率限制：5,000 point/小时；典型 PR（30 线程）仅 ~40 point。
- 单次 API 延迟 200-500ms；自动结案 30 线程约 1-2 秒。

---

## 未来增强

1. **批量线程操作**：一次 GraphQL mutation 结案多条线程。
2. **智能过滤**：按作者、时间、文件筛选。
3. **线程 Diff 视图**：自动展示改动前后差异。

---

通过 GraphQL，我们用自动化取代重复点击，让 PR 审查更高效、可靠。
