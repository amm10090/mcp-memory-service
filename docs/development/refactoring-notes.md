# Memory Service 重构总结

## 2025-02 Duplication Review
- **响应序列化重复**：`web/api/memories.py:86` 与 `services/memory_service.py:83` 维护两套字段映射，改为统一调用 `MemoryService.format_memory_response`；
- **搜索辅助逻辑漂移**：`web/api/search.py` 中的 helpers 已与 `MemoryService.retrieve_memory/search_by_tag` 重叠，旧的 `parse_time_query` / `is_within_time_range`（行 365+）应直接委托或删除；
- **MCP Tool vs HTTP Bridge**：`mcp_server.py` 与 `web/api/mcp.py` 对 `store/retrieve/search/delete/health/...` 实现重复，易出现分页/过滤差异。

## 问题
`list_memories` 在 API 与 MCP 工具之间存在严重不一致：
1. **分页顺序**：API 先过滤再分页；MCP 工具反之导致数据丢失；
2. **标签过滤**：API 使用存储层搜索，MCP 工具在内存中过滤；
3. **统计错误**：MCP 工具返回的 `total_found` 不准；
4. **维护成本**：同一逻辑散落三处，极易漂移。

## 解决方案
1. **统一服务层**：新增 `services/memory_service.py` 作为唯一业务入口，负责分页/过滤/错误处理；
2. **全面接入**：`web/api/memories.py`、`mcp_server.py`、`web/api/mcp.py` 均调用 `MemoryService.list_memories()`。

## 效益
- ✅ **一致性**：分页、过滤、错误返回一致；
- ✅ **可维护性**：逻辑集中，修改一次即可；
- ✅ **可靠性**：准确统计、统一标签/类型过滤；
- ✅ **可测试性**：服务层可单测，接口层只负责 I/O。

## 架构
```
API Endpoint / MCP Tool / MCP API
           │
           └── MemoryService（共享业务逻辑）
                     │
              Storage / Adapters
```

## 待重构清单（节选）
| 功能 | 优先级 | 当前状态 | 需要的 Service 方法 | 涉及文件 |
| --- | --- | --- | --- | --- |
| `store_memory` | 高 | ✅ 已完成 | `store_memory()` | `mcp_server.py`，`web/api/memories.py`，`web/api/mcp.py` |
| `retrieve_memory` | 高 | ✅ 已完成 | `retrieve_memory()` | 同上 |
| `search_by_tag` | 高 | ✅ 已完成 | `search_by_tag()` | 同上 |
| `delete_memory` | 高 | ✅ 已完成 | `delete_memory()` | 同上 |
| `search_by_time` | 中 | ✅ 已完成 | `search_by_time()` | `mcp_server.py`，`web/api/mcp.py` |
| `search_similar` | 中 | ✅ 已完成 | `search_similar()` | 同上 |
| `check_database_health` | 低 | ✅ 已完成 | `check_database_health()` | `mcp_server.py`，`web/api/mcp.py` |

## Phase 2A 进度
- ✅ `MemoryService.store_memory()`：主机名优先级（Client→Header→Server）、哈希生成、错误日志；
- ✅ MCP/HTTP/MCP API 全部切换到服务层；
- 剩余任务：确保旧 helper 已移除、补齐集成测试、更新文档（已跟踪）。

