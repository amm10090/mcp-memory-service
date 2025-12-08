# MCP Memory Service 集成目录

本文档收录可扩展 MCP Memory Service 功能的官方与社区工具。

## 官方集成

### [MCP Memory Dashboard](https://github.com/doobidoo/mcp-memory-dashboard)（进行中）

基于 Web 的仪表盘，可用于：
- 浏览 / 搜索记忆
- 查看元数据与标签
- 删除不需要的条目
- 运行语义检索
- 监控系统健康

## 社区集成

### [Claude Memory Context](https://github.com/doobidoo/claude-memory-context)

使 Claude 在每次对话开始时就了解 MCP Memory Service 中的重要主题与记忆。

特性：
- 查询最近且关键的记忆。
- 提取主题与内容摘要。
- 组装结构化上下文片段。
- 自动更新 Claude 项目说明。

该工具仅依赖 Claude 的项目说明能力，无需改动 MCP 协议，可按计划任务周期执行，确保 Claude 获取最新记忆。安装与使用方法请参见仓库 README。

---

## 添加你的集成

若你开发了新的集成，欢迎通过 PR 补充：

1. 集成名称与仓库链接。
2. 2-3 句简介。
3. 关键特性列表。
4. 安装说明或特殊依赖。

所有条目需可用、文档完善并保持维护。
