# 标签标准化指南

面向 MCP Memory Service 的统一标签体系，确保知识资产可检索、可演进且具备专业一致性。

## 🎯 概述

标准化标签是知识管理的基石。本指南定义命名规范、分层策略与应用示例，用以把零散信息组织成结构化、可搜索的语义网络。

## 📋 核心原则

### 1. 一致性
- 严格遵循同一命名规范；
- 同类型内容沿用相同标签组合；
- 统一格式（小写、短横线等）。

### 2. 层级化
- 标签自上而下递进：先领域，再子系统；
- 组合多个类别，覆盖主题、技术、状态等维度；
- 标签分组须反映真实使用场景。

### 3. 实用性
- 标签的首要作用是提升检索效率；
- 设计标签时先想“如何被搜索”；
- 细节与可用性保持平衡。

### 4. 演进性
- 标签体系随项目演化迭代；
- 建立定期复盘机制，记录调整原因；
- 准备好合并、拆分与废弃策略。

## 🏷️ 标准化标签体系

### 类别 1：项目与代码仓库

**主项目：**
```
mcp-memory-service     # 核心记忆服务开发
memory-dashboard       # Dashboard 应用
github-integration     # GitHub 集成与自动化
mcp-protocol           # MCP 协议层开发
cloudflare-workers     # 边缘计算/Workers 集成
```

**项目组件：**
```
frontend               # 前端 / UI 组件
backend                # 后端 / 服务端实现
api                    # API 设计与落地
database               # 数据层与存储
infrastructure         # 部署与 DevOps
```

**示例：**
```javascript
{
  "tags": ["mcp-memory-service", "backend", "database", "chromadb"]
}
```

### 类别 2：技术与工具

**编程语言：**
```
python                # Python 开发
typescript            # TypeScript 开发
javascript            # JavaScript 开发
bash                  # Shell/脚本
sql                   # SQL/查询
```

**框架与库：**
```
react                 # React 生态
fastapi               # FastAPI 框架
chromadb              # ChromaDB 向量库
sentence-transformers # 句向量模型
pytest                # 测试框架
```

**工具与平台：**
```
git                   # 版本控制
docker                # 容器化
github                # 仓库/协作
aws                   # AWS 平台
npm                   # Node 包管理
```

**示例：**
```javascript
{
  "tags": ["python", "chromadb", "sentence-transformers", "pytest"]
}
```

### 类别 3：活动与流程

**开发活动：**
```
development           # 一般开发
implementation        # 功能落地
debugging             # 调试
testing               # 测试
refactoring           # 重构
optimization          # 性能优化
```

**文档活动：**
```
documentation         # 文档撰写
tutorial              # 教程
guide                 # 指南
reference             # 速查
examples              # 示例
```

**运维活动：**
```
deployment            # 部署/上线
monitoring            # 监控
backup                # 备份
migration             # 迁移
maintenance           # 维护
troubleshooting       # 故障排查
```

**示例：**
```javascript
{
  "tags": ["debugging", "troubleshooting", "testing", "verification"]
}
```

### 类别 4：内容类型与格式

**知识类型：**
```
concept               # 概念
architecture          # 架构
design                # 设计
best-practices        # 最佳实践
methodology           # 方法论
workflow              # 工作流
```

**文档形态：**
```
tutorial              # 步骤式教程
reference             # 参考
example               # 示例
template              # 模板
checklist             # 清单
summary               # 摘要
```

**技术内容：**
```
configuration         # 配置
specification         # 规格
analysis              # 分析
research              # 研究
review                # 评审
```

**示例：**
```javascript
{
  "tags": ["architecture", "design", "best-practices", "reference"]
}
```

### 类别 5：状态与进度

**研发状态：**
```
resolved              # 已完成并验证
in-progress           # 进行中
blocked               # 被阻塞
needs-investigation   # 待调研
planned               # 规划中
cancelled             # 已取消
```

**质量状态：**
```
verified              # 已验证
tested                # 已测试
reviewed              # 已 review
approved              # 已批准
experimental          # 实验阶段
deprecated            # 不再推荐
```

**优先级：**
```
urgent                # 立刻处理
high-priority         # 高优先级
normal-priority       # 普通
low-priority          # 低优先级
nice-to-have          # 可选增强
```

**示例：**
```javascript
{
  "tags": ["resolved", "verified", "high-priority", "production-ready"]
}
```

### 类别 6：上下文与时间

**时间标记：**
```
january-2025          # 指定月份
q1-2025               # 季度
milestone-v1          # 里程碑
release-candidate     # RC 阶段
sprint-3              # Sprint
```

**环境上下文：**
```
development           # 开发环境
staging               # 预发
production            # 生产
testing               # 测试
local                 # 本地
```

**范围与影响：**
```
breaking-change       # 破坏式变更
feature               # 新特性
enhancement           # 增强
hotfix                # 紧急修复
security              # 安全
performance           # 性能
```

**示例：**
```javascript
{
  "tags": ["june-2025", "production", "security", "hotfix", "critical"]
}
```

## 🎨 标签命名规范

### 基础格式
- 使用小写字母；
- 空格使用短横线替代：`memory-service`；
- 描述精准但保持简洁；
- 除非行业通用，否则避免缩写；
- 优先使用单数形式。

**多词标签示例：**
```
✅ memory-service, github-integration, best-practices
❌ memoryservice, GitHub_Integration, bestPractices
```

**版本与日期：**
```
✅ v1-2-0, january-2025, q1-2025
❌ v1.2.0, Jan2025, Q1/2025
```

**状态标签：**
```
✅ in-progress, needs-investigation, high-priority
❌ inProgress, needsInvestigation, highPriority
```

### 层级命名

- 标签可按“泛化 → 细分”逐级书写：
```
project → mcp-memory-service → backend → database
testing → integration-testing → api-testing
issue → bug → critical-bug → data-corruption
```

**示例演进：**
```javascript
{"tags": ["testing", "verification"]}
{"tags": ["testing", "unit-testing", "python", "pytest"]}
{"tags": ["testing", "unit-testing", "memory-storage", "chromadb", "pytest"]}
```

## 📊 标签应用模式

### 多类别组合

建议每条记忆使用 3-6 个类别：
```javascript
{
  "tags": [
    "mcp-memory-service", "backend",
    "python", "chromadb",
    "debugging", "troubleshooting",
    "troubleshooting-guide",
    "resolved",
    "june-2025", "production"
  ]
}
```

### 内容特定模式

**缺陷/问题：**
```javascript
{
  "tags": [
    "issue-7",
    "timestamp-corruption",
    "critical-bug",
    "mcp-memory-service",
    "chromadb",
    "resolved"
  ]
}
```

**文档类：**
```javascript
{
  "tags": [
    "documentation",
    "memory-maintenance",
    "best-practices",
    "tutorial",
    "mcp-memory-service",
    "reference"
  ]
}
```

**里程碑：**
```javascript
{
  "tags": [
    "milestone",
    "v1-2-0",
    "production-ready",
    "mcp-memory-service",
    "feature-complete",
    "june-2025"
  ]
}
```

**研究/概念：**
```javascript
{
  "tags": [
    "concept",
    "memory-consolidation",
    "architecture",
    "research",
    "cognitive-processing",
    "system-design"
  ]
}
```

## 🔍 标签挑选流程

1. **确定主语境**：涉及哪个项目/域？
2. **补充技术细节**：依赖哪些语言、框架、平台？
3. **描述活动**：这是调试、实现还是测试？
4. **归类内容类型**：文档、决策、脚本还是报告？
5. **标注状态**：当前进度、优先级、风险？
6. **添加时间/环境**：关联哪个版本、Sprint 或环境？

### 示例

**示例 1：调试记录**
- 内容：“修复生产环境中 ChromaDB 连接超时问题”；
- 标签组合：
```javascript
{
  "tags": [
    "mcp-memory-service", "backend",
    "chromadb", "connection-timeout", "production",
    "debugging", "troubleshooting",
    "solution", "hotfix",
    "resolved", "critical"
  ]
}
```

**示例 2：规划文档**
- 内容：“2025 Q2 记忆服务路线图”；
- 标签组合：
```javascript
{
  "tags": [
    "mcp-memory-service", "planning",
    "roadmap", "improvements",
    "strategy", "planning-document",
    "q2-2025", "quarterly",
    "future-work", "enhancement"
  ]
}
```

## 🛠️ 标签治理工具

### 质量检测
```javascript
// 排查同义标签
retrieve_memory({"query": "debugging troubleshooting", "n_results": 10})
search_by_tag({"tags": ["debug"]})
```
```javascript
// 检查是否需要补充标签
retrieve_memory({"query": "issue bug problem", "n_results": 15})
search_by_tag({"tags": ["test"]})
```

### 分析脚本
```javascript
// 统计使用频次
check_database_health()
search_by_tag({"tags": ["frequent-tag"]})
```
```javascript
// 校验模式一致性
const patterns = ["mcp-memory-service", "debugging", "issue-", "resolved"];
```

## 📈 体系演进

### 定期复盘
- **月度**：新增类别？命名是否统一？是否需要合并/拆分？
- **季度**：统计使用、找出空白、记录更新、形成提案并实施。

### 版本化管理
```javascript
store_memory({
  "content": "Tag Schema Update v2.1: Added security-related tags...",
  "metadata": {
    "tags": ["tag-schema", "version-2-1", "schema-update", "documentation"],
    "type": "schema-documentation"
  }
})
```

## 🎯 最佳实践

**Do**
- ✅ 保持一致；
- ✅ 覆盖多个类别；
- ✅ 严格遵守命名规范；
- ✅ 以检索需求为导向；
- ✅ 记录决策；
- ✅ 定期复查与迭代。

**Don't**
- ❌ 不要过度或不足打标签（建议 4-8 个）；
- ❌ 不要混用大小写和字符；
- ❌ 不要创建冗余标签；
- ❌ 不要忽视上下文；
- ❌ 不要“一次性设置后就放任不管”。

---

持续应用以上原则，可让 MCP Memory Service 构建专业、可维护且可量化的知识图谱。
