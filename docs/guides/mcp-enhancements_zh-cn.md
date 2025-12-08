# MCP 协议增强功能指南

本文介绍自 v4.1.0 起新增的 MCP（Model Context Protocol）能力，包括资源访问、引导式提示与进度跟踪。

## 目录
- [增强型资源](#增强型资源)
- [引导式提示](#引导式提示)
- [进度跟踪](#进度跟踪)
- [集成示例](#集成示例)
- [最佳实践](#最佳实践)
- [兼容性](#兼容性)
- [延伸阅读](#延伸阅读)

## 增强型资源

MCP Memory Service 现已通过 URI 形式暴露记忆集合，客户端可直接读取结构化数据。

### 可用资源

#### 1. Memory Statistics
```
URI: memory://stats
Returns: JSON object with database statistics
```

示例响应：
```json
{
  "total_memories": 1234,
  "storage_backend": "SqliteVecStorage",
  "status": "operational",
  "total_tags": 45,
  "storage_size": "12.3 MB"
}
```

#### 2. Available Tags
```
URI: memory://tags
Returns: List of all unique tags in the database
```

示例响应：
```json
{
  "tags": ["work", "personal", "learning", "project-x", "meeting-notes"],
  "count": 5
}
```

#### 3. Recent Memories
```
URI: memory://recent/{n}
Parameters: n = number of memories to retrieve
Returns: N most recent memories
```

示例：`memory://recent/10` 返回最近 10 条记忆。

#### 4. Memories by Tag
```
URI: memory://tag/{tagname}
Parameters: tagname = specific tag to filter by
Returns: All memories with the specified tag
```

示例：`memory://tag/learning` 返回所有带有 “learning” 标签的记忆。

#### 5. Dynamic Search
```
URI: memory://search/{query}
Parameters: query = search query
Returns: Search results matching the query
```

示例：`memory://search/python%20programming` 搜索与 Python 编程相关的记忆。

### 资源模板

服务端提供资源模板，便于动态生成 URI：

```json
[
  {
    "uriTemplate": "memory://recent/{n}",
    "name": "Recent Memories",
    "description": "Get N most recent memories"
  },
  {
    "uriTemplate": "memory://tag/{tag}",
    "name": "Memories by Tag",
    "description": "Get all memories with a specific tag"
  },
  {
    "uriTemplate": "memory://search/{query}",
    "name": "Search Memories",
    "description": "Search memories by query"
  }
]
```

## 引导式提示

交互式工作流可为常见的记忆操作提供结构化输入与输出。

### 可用提示

#### 1. Memory Review
针对指定时间段回顾并整理记忆。

**参数：**
- `time_period`（必填）：时间范围，如 “last week”“yesterday”。
- `focus_area`（选填）：关注领域，如 “work”“personal”。

**示例：**
```json
{
  "name": "memory_review",
  "arguments": {
    "time_period": "last week",
    "focus_area": "work"
  }
}
```

#### 2. Memory Analysis
分析记忆中的模式与主题。

**参数：**
- `tags`（选填）：逗号分隔的标签列表。
- `time_range`（选填）：分析的时间范围，如 “last month”。

**示例：**
```json
{
  "name": "memory_analysis",
  "arguments": {
    "tags": "learning,python",
    "time_range": "last month"
  }
}
```

#### 3. Knowledge Export
以多种格式导出记忆。

**参数：**
- `format`（必填）：导出格式（`json`、`markdown`、`text`）。
- `filter`（选填）：过滤条件（标签或搜索语句）。

**示例：**
```json
{
  "name": "knowledge_export",
  "arguments": {
    "format": "markdown",
    "filter": "project-x"
  }
}
```

#### 4. Memory Cleanup
识别并清理重复或过期记忆。

**参数：**
- `older_than`（选填）：删除早于指定时间的记忆。
- `similarity_threshold`（选填）：重复检测阈值（0.0-1.0）。

**示例：**
```json
{
  "name": "memory_cleanup",
  "arguments": {
    "older_than": "6 months",
    "similarity_threshold": "0.95"
  }
}
```

#### 5. Learning Session
以结构化方式记录学习笔记并自动分类。

**参数：**
- `topic`（必填）：学习主题。
- `key_points`（必填）：逗号分隔的要点。
- `questions`（选填）：后续要研究的问题。

**示例：**
```json
{
  "name": "learning_session",
  "arguments": {
    "topic": "Machine Learning Basics",
    "key_points": "supervised learning, neural networks, backpropagation",
    "questions": "How does gradient descent work?, What is overfitting?"
  }
}
```

## 进度跟踪

对于耗时操作，服务会通过 MCP 通知系统实时推送进度。

### 支持进度跟踪的操作

#### 1. 批量删除（`delete_by_tags`）
会输出逐步进度信息：

```
0% - Starting deletion of memories with tags: [tag1, tag2]
25% - Searching for memories to delete...
50% - Deleting memories...
90% - Deleted 45 memories
100% - Deletion completed: Successfully deleted 45 memories
```

### 操作 ID

每个长时任务都会生成唯一 ID：

```
Operation ID: delete_by_tags_a1b2c3d4
```

### 进度通知结构

通知遵循 MCP 协议格式：

```json
{
  "progress": 50,
  "progress_token": "operation_id_12345",
  "message": "Processing memories..."
}
```

## 集成示例

### 在 Claude Code 中访问资源

```python
# List available resources
resources = await mcp_client.list_resources()

# Read specific resource
stats = await mcp_client.read_resource("memory://stats")
recent = await mcp_client.read_resource("memory://recent/20")
```

### 调用引导式提示

```python
# Execute a memory review prompt
result = await mcp_client.get_prompt(
    name="memory_review",
    arguments={
        "time_period": "yesterday",
        "focus_area": "meetings"
    }
)
```

### 跟踪操作进度

```python
# Start operation and track progress
operation = await mcp_client.call_tool(
    name="delete_by_tags",
    arguments={"tags": ["temporary", "test"]}
)

# Progress notifications will be sent automatically
# Monitor via operation_id in the response
```

## 最佳实践

1. **资源**：用于只读场景快速获取记忆数据。
2. **引导式提示**：适合需要交互式输入/输出的工作流。
3. **进度跟踪**：处理耗时任务时持续监听操作 ID。
4. **错误处理**：所有操作都会返回结构化错误，便于定位问题。
5. **性能**：资源接口经过优化，可快速响应。

## 兼容性

所有增强功能与现有 MCP 客户端保持完全兼容；若客户端支持扩展能力，可获取更丰富的体验。

## 延伸阅读

- [MCP Specification](https://modelcontextprotocol.info/specification/2024-11-05/)
- [Memory Service API Documentation](../api/README.md)
- [Claude Code Integration Guide](./claude-code-integration.md)
