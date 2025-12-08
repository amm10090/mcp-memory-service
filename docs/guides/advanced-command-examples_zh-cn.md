# 高级 Claude Code 命令实战示例

本指南展示如何利用 MCP Memory Service 的 Claude Code 命令，构建高级使用模式与现实工作流。

## 目录
- [开发工作流](#开发工作流)
- [项目管理](#项目管理)
- [学习与知识管理](#学习与知识管理)
- [团队协作](#团队协作)
- [调试与故障排查](#调试与故障排查)
- [高级搜索技巧](#高级搜索技巧)
- [自动化与脚本](#自动化与脚本)

---

## 开发工作流

### 全栈开发会话

**场景**：构建带有认证能力的 Web 应用

```bash
# Start development session with context capture
claude /memory-context --summary "Starting OAuth 2.0 integration for user authentication"

# Store architecture decisions as you make them
claude /memory-store --tags "architecture,oauth,security" \
  "Using Authorization Code flow with PKCE for mobile app security"

claude /memory-store --tags "database,schema" --type "reference" \
  "User table schema: id, email, oauth_provider, oauth_id, created_at, last_login"

# Store implementation details
claude /memory-store --tags "implementation,react" \
  "React auth context uses useReducer for state management with actions: LOGIN, LOGOUT, REFRESH_TOKEN"

# Store configuration details (marked as private)
claude /memory-store --tags "config,oauth" --type "reference" --private \
  "Auth0 configuration: domain=dev-xyz.auth0.com, audience=https://api.myapp.com"

# Later, recall decisions when working on related features
claude /memory-recall "what did we decide about OAuth implementation yesterday?"

# Search for specific implementation patterns
claude /memory-search --tags "react,auth" "state management patterns"

# End session with comprehensive context capture
claude /memory-context --summary "Completed OAuth integration - ready for testing" \
  --include-files --include-commits
```

### 缺陷修复流程

**场景**：追踪并解决复杂缺陷

```bash
# Store bug discovery
claude /memory-store --tags "bug,critical,payment" --type "task" \
  "Payment processing fails for amounts over $1000 - investigation needed"

# Store investigation findings
claude /memory-store --tags "bug,payment,stripe" \
  "Issue traced to Stripe API rate limiting on high-value transactions"

# Store attempted solutions
claude /memory-store --tags "bug,payment,attempted-fix" \
  "Tried increasing timeout from 5s to 30s - did not resolve issue"

# Store working solution
claude /memory-store --tags "bug,payment,solution" --type "decision" \
  "Fixed by implementing exponential backoff retry mechanism with max 3 attempts"

# Create searchable reference for future
claude /memory-store --tags "reference,stripe,best-practice" \
  "Stripe high-value transactions require retry logic - see payment-service.js line 245"

# Later, search for similar issues
claude /memory-search --tags "bug,stripe" "rate limiting payment"
```

### 代码评审与重构

**场景**：系统化的代码优化流程

```bash
# Store code review insights
claude /memory-store --tags "code-review,performance,database" \
  "N+1 query problem in user dashboard - fetching posts individually instead of batch"

# Store refactoring decisions
claude /memory-store --tags "refactoring,database,optimization" --type "decision" \
  "Replaced individual queries with single JOIN query - reduced DB calls from 50+ to 1"

# Store before/after metrics
claude /memory-store --tags "performance,metrics,improvement" \
  "Dashboard load time: Before=2.3s, After=0.4s (83% improvement)"

# Track technical debt
claude /memory-store --tags "technical-debt,todo" --type "task" \
  "TODO: Extract user dashboard logic into dedicated service class"

# Review improvements over time
claude /memory-recall "what performance improvements did we make this month?"
```

---

## 项目管理

### Sprint 规划与追踪

**场景**：借助记忆增强的敏捷开发流程

```bash
# Start of sprint
claude /memory-context --summary "Sprint 15 planning - Focus on user onboarding improvements"

# Store sprint goals
claude /memory-store --tags "sprint-15,goals,onboarding" --type "planning" \
  "Sprint 15 goals: Simplify signup flow, add email verification, implement welcome tour"

# Track daily progress
claude /memory-store --tags "sprint-15,progress,day-1" \
  "Completed signup form validation and error handling - 2 story points"

# Store blockers and risks
claude /memory-store --tags "sprint-15,blocker,email" --type "task" \
  "Email service integration blocked - waiting for IT to configure SendGrid account"

# Mid-sprint review
claude /memory-recall "what blockers did we identify this sprint?"
claude /memory-search --tags "sprint-15,progress"

# Sprint retrospective
claude /memory-store --tags "sprint-15,retrospective" --type "meeting" \
  "Sprint 15 retro: Delivered 18/20 points, email blocker resolved, team velocity improving"

# Cross-sprint analysis
claude /memory-search --tags "retrospective" --limit 5
claude /memory-recall "what patterns do we see in our sprint blockers?"
```

### 功能开发生命周期

**场景**：全流程跟踪功能交付

```bash
# Feature inception
claude /memory-store --tags "feature,user-profiles,inception" --type "planning" \
  "User profiles feature: Allow users to customize avatar, bio, social links, privacy settings"

# Requirements gathering
claude /memory-store --tags "feature,user-profiles,requirements" \
  "Requirements: Image upload (max 2MB), bio text (max 500 chars), 5 social links, public/private toggle"

# Technical design
claude /memory-store --tags "feature,user-profiles,design" --type "architecture" \
  "Design: New profiles table, S3 for image storage, React profile editor component"

# Implementation milestones
claude /memory-store --tags "feature,user-profiles,milestone" \
  "Milestone 1 complete: Database schema created and migrated to production"

# Testing notes
claude /memory-store --tags "feature,user-profiles,testing" \
  "Testing discovered: Large images cause timeout - need client-side compression"

# Launch preparation
claude /memory-store --tags "feature,user-profiles,launch" \
  "Launch checklist: DB migration ✓, S3 bucket ✓, feature flag ready ✓, docs updated ✓"

# Post-launch analysis
claude /memory-store --tags "feature,user-profiles,metrics" \
  "Week 1 metrics: 45% adoption rate, avg 3.2 social links per profile, 12% privacy toggle usage"

# Feature evolution tracking
claude /memory-search --tags "feature,user-profiles" --limit 20
```

---

## 学习与知识管理

### 技术调研与评估

**场景**：评估新技术是否适合引入

```bash
# Research session start
claude /memory-context --summary "Researching GraphQL vs REST API for mobile app backend"

# Store research findings
claude /memory-store --tags "research,graphql,pros" \
  "GraphQL benefits: Single endpoint, client-defined queries, strong typing, introspection"

claude /memory-store --tags "research,graphql,cons" \
  "GraphQL challenges: Learning curve, caching complexity, N+1 query risk, server complexity"

# Store comparison data
claude /memory-store --tags "research,performance,comparison" \
  "GraphQL latency vs REST benchmark data: GraphQL median 120ms vs REST 95ms"

# Decision making
claude /memory-store --tags "research,decision" --type "decision" \
  "Decision: Maintain REST for core API, pilot GraphQL for analytics dashboards"

# Later reference
claude /memory-search --tags "research,graphql"
```

### 学习笔记与知识库建设

**场景**：构建个人/团队知识库

```bash
# Capture learning topics
claude /memory-store --tags "learning,pytorch" \
  "Lesson: PyTorch Lightning simplifies training loops with Trainer class"

# Store tutorials or resources
claude /memory-store --tags "resource,redis" --type "reference" \
  "Redis cluster tutorial: https://developer.redis.com/howtos/cluster-tutorial/"

# Track learning progress
claude /memory-store --tags "learning,progress" --type "task" \
  "Goal: Complete Redis cluster certification - in progress"

# Summarize key takeaways
claude /memory-context --summary "Finished Redis cluster deep dive" --include-files
```

---

## 团队协作

### 会议与决策记录

**场景**：实时记录会议要点与行动项

```bash
# Start meeting capture
claude /memory-context --summary "Weekly architecture sync - 2024-03-15"

# Log discussion points
claude /memory-store --tags "meeting,architecture" --type "meeting" \
  "Discussed microservices migration plan - need phased rollout"

# Track action items
claude /memory-store --tags "meeting,action-item" --type "task" \
  "Action: Prepare migration risk assessment by next Monday"

# Capture decisions
claude /memory-store --tags "meeting,decision" --type "decision" \
  "Decision: Adopt service mesh for zero-downtime deployment"
```

### 交接与值守

**场景**：记录轮班、值守时的关键信息

```bash
# Start shift log
claude /memory-store --tags "oncall,shift" --type "status" \
  "On-call shift started: Monitoring services A, B, C"

# Record incidents
claude /memory-store --tags "oncall,incident" \
  "Incident #423 resolved - root cause: database connection pool exhaustion"

# Transfer shift knowledge
claude /memory-context --summary "Shift handoff notes" --include-logs
```

---

## 调试与故障排查

### 快速定位问题

**场景**：利用记忆查询追踪历史问题与解决方案

```bash
claude /memory-search --tags "incident,timeout" --limit 5
claude /memory-recall "How did we fix the API timeout in January?"
```

### 复盘与改进

```bash
# Store post-mortem summary
claude /memory-store --tags "postmortem,api" --type "analysis" \
  "API outage postmortem: Root cause was expired TLS certificate - implemented automated renewal"

# Track follow-up tasks
claude /memory-store --tags "postmortem,follow-up" --type "task" \
  "TODO: Add TLS expiry monitoring alert"
```

---

## 高级搜索技巧

### 标签与关键字组合

```bash
# Filter by tags and keywords
claude /memory-search --tags "architecture,decision" "microservices rollout"
```

### 时间范围查询

```bash
# Time-based search
claude /memory-search --tags "retrospective" --since "2024-01-01" --until "2024-03-31"
claude /memory-recall "what retrospectives did we complete last month?"
```

### 内容类型筛选

```bash
claude /memory-search --type "decision"
claude /memory-search --type "task" --limit 10
```

---

## 自动化与脚本

### Shell 脚本集成

```bash
#!/usr/bin/env bash

summary="$(git log -1 --pretty=%B)"
claude /memory-store --tags "git,commit" --type "implementation" \
  "Latest commit: $summary"
```

### CI/CD 记录

```bash
# Capture deployment context
claude /memory-store --tags "ci,deployment" --type "status" \
  "Deployed version 3.2.1 to production - passed all smoke tests"
```

### 自动化报告

```bash
# Generate weekly summary
claude /memory-recall "summaries for last week" --limit 7
```

---

通过以上示例，你可以将 MCP Memory Service 与 Claude Code 命令组合应用到日常开发、管理与协作场景中，沉淀结构化知识并快速复用历史经验。EOF
