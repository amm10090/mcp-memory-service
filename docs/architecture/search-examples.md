# 高级混合搜索：实战示例

## REST API 场景
- **项目排障**：POST `/api/search/advanced`，`search_mode:"hybrid"`，附 tags/time/metadata filters，可返回主记忆 + 解决方案/上下文/时间线；
- **知识整合**：`query:"user authentication security decisions"`，`consolidate_related:true`，获取 6 个月内的决策/笔记概览。

## MCP API
- `advanced_memory_search`：支持 `search_mode`、`consolidate_related`、`filters`、多信号排序；
- `consolidate_project_memories`：按项目名称生成总览、时间线、关键决策、未解决事项。

## Claude Code 集成
- Slash 命令：`claude /memory-search-advanced 
