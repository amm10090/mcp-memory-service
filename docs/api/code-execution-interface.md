# 代码执行接口（Code Execution Interface）API 文档

## 概述

代码执行接口提供一个面向 Python 的轻量 API，可直接操作记忆数据，相比传统 MCP 工具调用节省 85%-95% 的 Token 消耗。

- **版本**：1.0.0
- **阶段**：Phase 1（核心操作）
- **关联 Issue**：[ #206 ](https://github.com/doobidoo/mcp-memory-service/issues/206)

## Token 效率

| 操作 | MCP 工具 | 代码执行 | 节省幅度 |
|-----------|-----------|------------|-----------|
| search（5 条结果） | ≈ 2,625 tokens | ≈ 385 tokens | **85%** |
| store | ≈ 150 tokens | ≈ 15 tokens | **90%** |
| health | ≈ 125 tokens | ≈ 20 tokens | **84%** |

**年度保守节省：**
- 10 名用户 × 5 次会话/天 × 365 天 × 6,000 tokens ≈ 1.095 亿 tokens/年
- 以 $0.15 / 百万 tokens 计，约 **$16.43 / 10 用户 / 年**

## 安装

v8.18.2 及以上版本已内置该 API，无需额外安装。

```bash
# 确认使用最新版本
pip install --upgrade mcp-memory-service
```

## 快速上手

```python
from mcp_memory_service.api import search, store, health

# 写入记忆（≈15 tokens）
hash = store("Implemented OAuth 2.1 authentication", tags=["auth", "feature"])
print(f"Stored: {hash}")  # 输出：Stored: abc12345

# 检索记忆（5 条结果 ≈385 tokens）
results = search("authentication", limit=5)
print(f"Found {results.total} memories")
for m in results.memories:
    print(f"  {m.hash}: {m.preview[:50]}... (score: {m.score:.2f})")

# 健康检查（≈20 tokens）
info = health()
print(f"Backend: {info.backend}, Status: {info.status}, Count: {info.count}")
```

## API 参考

### 核心操作

#### `search()`

语义搜索，返回紧凑结果。

```python
def search(
    query: str,
    limit: int = 5,
    tags: Optional[List[str]] = None
) -> CompactSearchResult:
    """
    使用语义相似度检索记忆。

    Args:
        query: 自然语言查询
        limit: 返回数量（默认 5）
        tags: 可选标签过滤

    Returns:
        CompactSearchResult，包含结果列表、总数与原查询

    Raises:
        ValueError: query 为空或 limit 非法
        RuntimeError: 存储后端不可用

    Token Cost: ≈25 tokens + ≈73 tokens * 每条结果

    Example:
        >>> results = search("recent architecture decisions", limit=3)
        >>> for m in results.memories:
        ...     print(f"{m.hash}: {m.preview}")
    """
```

**性能：**
- 首次调用：≈50ms（包含存储初始化）
- 后续调用：≈5-10ms（复用连接）

#### `store()`

写入新的记忆对象。

```python
def store(
    content: str,
    tags: Optional[Union[str, List[str]]] = None,
    memory_type: str = "note"
) -> str:
    """
    写入新记忆。

    Args:
        content: 记忆内容
        tags: 单个或多个标签
        memory_type: 记忆类型（默认 note）

    Returns:
        8 位内容哈希

    Raises:
        ValueError: content 为空
        RuntimeError: 存储操作失败

    Token Cost: ≈15 tokens
    """
```

**性能：**
- 首次调用：≈50ms
- 后续调用：≈10-20ms（包含嵌入生成）

#### `health()`

获取服务健康状态。

```python
def health() -> CompactHealthInfo:
    """返回服务状态、记忆数量与后端类型（≈20 tokens）。"""
```

**性能：**
- 首次：≈50ms
- 后续：≈5ms（缓存统计）

### 数据类型

#### `CompactMemory`

最小化记忆结构（比完整对象减少 91% Token）。

```python
class CompactMemory(NamedTuple):
    hash: str           # 8 位哈希
    preview: str        # 前 200 字符
    tags: tuple[str]
    created: float      # Unix 时间戳
    score: float        # 0.0-1.0 相关度
```

**Token Cost：**≈73 tokens（完整对象约 820 tokens）

#### `CompactSearchResult`

```python
class CompactSearchResult(NamedTuple):
    memories: tuple[CompactMemory]
    total: int
    query: str
```

#### `CompactHealthInfo`

```python
class CompactHealthInfo(NamedTuple):
    status: str         # 'healthy' | 'degraded' | 'error'
    count: int
    backend: str        # 'sqlite_vec' | 'cloudflare' | 'hybrid'
```

## 使用示例

### 基础搜索

```python
results = search("authentication", limit=5)
results = search("database", limit=10, tags=["architecture"])
```

### 批量写入

```python
for change in changes:
    hash_val = store(change, tags=["changelog", "auth"])
```

### 健康监控

```python
info = health()
if info.status != 'healthy':
    ...
```

### 错误处理

```python
try:
    hash_val = store(content, tags=["test"])
    results = search("query", limit=5)
except ValueError as e:
    ...
```

## 性能优化

- **连接复用**：内部自动缓存存储连接，首次约 50ms，之后 5-20ms。
- **控制 limit**：`limit=3` 约 240 tokens，`limit=20` 约 1,470 tokens，可按场景取舍。

## 向后兼容

代码执行 API 与现有 MCP 工具可并存：
- MCP 工具继续可用，无需迁移；
- 可渐进式改造；
- 当代码执行失败时仍可回退至工具。

## 迁移示例

**Before：**MCP 工具（Node.js）调用 `retrieve_memory`。

**After：**Python 直接调用 `search('architecture', limit=5)`，Token 从 2,625 降至 385。

## 故障排查

### 存储初始化失败

```python
info = health()
if info.status == 'error':
    print(f"Storage backend {info.backend} not available")
```
- 检查 `DATABASE_PATH`、权限、后端配置。

### ImportError

```bash
pip list | grep mcp-memory-service
python - <<'PY'
import mcp_memory_service
print(mcp_memory_service.__version__)
PY
```

### 性能异常

```python
start = time.perf_counter()
results = search("query", limit=5)
```
- 超过 100ms 时检查是否冷启动、数据库规模或模型缓存。

## 路线图

### Phase 2
- `search_by_tag()`
- `recall()`
- `delete()`
- `update()`

### Phase 3
- `store_batch()`
- `search_iter()`
- 文档采集 API
- 记忆归并触发器

## 相关文档
- `docs/research/code-execution-interface-implementation.md`
- `docs/research/code-execution-interface-summary.md`
- Issue #206、`CLAUDE.md`

## 支持
- GitHub Issues：https://github.com/doobidoo/mcp-memory-service/issues
- 文档 Wiki：https://github.com/doobidoo/mcp-memory-service/wiki

## 许可
Copyright 2024 Heinrich Krupp · Apache 2.0 License
