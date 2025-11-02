# MCP Memory Service — API 参考

本文档汇总通过 MCP 服务器公开的可用 API，并对请求/响应模式进行说明。

## MCP（FastMCP HTTP）工具

在 `src/mcp_memory_service/mcp_server.py` 中使用 `@mcp.tool()` 定义：

- `store_memory(content, tags=None, memory_type="note", metadata=None, client_hostname=None)`

  - 写入一条记忆；标签与元数据可选。若设置 `INCLUDE_HOSTNAME=true`，将额外附加 `source:<hostname>` 标签与 `hostname` 元数据。
  - 响应：`{ success: bool, message: str, content_hash: str }`。

- `retrieve_memory(query, n_results=5, min_similarity=0.0)`

  - 基于语义检索的查询，返回最多 `n_results` 条匹配记忆。
  - 响应：`{ memories: [{ content, content_hash, tags, memory_type, created_at, similarity_score }...], query, total_results }`。

- `search_by_tag(tags, match_all=False)`

  - 按标签搜索，可传入单个或多个标签；当 `match_all=true` 时要求所有标签同时匹配，否则任意匹配即可。
  - 响应：`{ memories: [{ content, content_hash, tags, memory_type, created_at }...], search_tags: [...], match_all, total_results }`。

- `delete_memory(content_hash)`

  - 依据内容哈希删除对应记忆。
  - 响应：`{ success: bool, message: str, content_hash }`。

- `check_database_health()`
  - 获取当前后端的健康状态与统计信息。
  - 响应：`{ status: "healthy"|"error", backend, statistics: { total_memories, total_tags, storage_size, last_backup }, timestamp? }`。

传输方式：`mcp.run("streamable-http")`，默认监听地址 `0.0.0.0`，端口默认为 `8001`，亦可通过 `MCP_SERVER_PORT`/`MCP_SERVER_HOST` 配置。

## MCP（stdio）服务器工具与提示

在 `src/mcp_memory_service/server.py` 中由 `mcp.server.Server` 定义。相较核心 FastMCP 工具，stdio 服务提供更丰富的工具与 prompt。

重点能力：

- 核心记忆操作：存储、检索/搜索、按标签搜索、删除、`delete_by_tag`、`cleanup_duplicates`、更新元数据、基于时间的回溯等；
- 分析/导出：`knowledge_analysis`、`knowledge_export`（支持 `format: json|markdown|text` 及可选过滤条件）；
- 维护：`memory_cleanup`（重复检测启发式）、健康/统计、标签列表；
- 记忆整合（可选）：在启用时提供关联、聚类、压缩、遗忘任务与调度能力。

注意：stdio 服务器会根据多客户端场景动态选择存储模式（直接使用 SQLite-vec WAL 或通过 HTTP 协调），在 Claude Desktop 环境抑制 stdout 输出，在 LM Studio 环境提供更详细的诊断日志。

## HTTP 接口

- 对于 FastMCP，HTTP 仅作为 MCP 协议的传输层；路由由 FastMCP 层处理，并非面向公共 REST API；
- 在部分发行版中，`src/mcp_memory_service/web/` 提供独立的 HTTP API 与可视化面板。本仓库中 HTTP 协调仅用于内部，推荐的外部访问方式仍为 MCP。

## 错误模型与日志

- MCP 工具的错误将以 `{ success: false, message: <details> }` 或附带 `error` 字段返回；
- 日志级别 WARNING 及以上会输出到 stderr（Claude Desktop 的严格模式），info/debug 仅在 LM Studio 等环境输出到 stdout；可通过 `LOG_LEVEL` 控制详细程度。

## 示例

存储记忆：

```
tool: store_memory
args: { "content": "Refactored auth flow to use OAuth 2.1", "tags": ["auth", "refactor"], "memory_type": "note" }
```

按查询检索：

```
tool: retrieve_memory
args: { "query": "OAuth refactor", "n_results": 5 }
```

按标签搜索：

```
tool: search_by_tag
args: { "tags": ["auth", "refactor"], "match_all": true }
```

根据哈希删除：

```
tool: delete_memory
args: { "content_hash": "<hash>" }
```
