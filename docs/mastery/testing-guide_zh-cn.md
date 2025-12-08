# MCP Memory Service — 测试指南

本文介绍如何运行、理解与扩展测试套件。

## 前置条件

- Python ≥ 3.10（推荐 3.12；3.13 可能缺少预编译的 `sqlite-vec` wheel）；
- 安装依赖（推荐 uv）：
  - `uv sync`（遵循 `pyproject.toml` 与 `uv.lock`），或
  - `pip install -e .` 并按需安装附加包；
- 若需运行 SQLite-vec 相关测试：
  - 需预装 `sqlite-vec` 与 `sentence-transformers`/`torch`；
  - 某些 OS/Python 组合需要支持加载 sqlite 扩展（见 Troubleshooting）。

## 测试结构

- `tests/README.md`：整体概览；
- 目录划分：
  - 单元测试：`tests/unit/`（例如标签、mDNS、Cloudflare stub 等）；
  - 集成测试：`tests/integration/`（跨组件流程）；
  - 性能测试：`tests/performance/`；
  - 后端专项：如 `test_sqlite_vec_storage.py`、`test_time_parser.py`、`test_memory_ops.py` 等顶层脚本。

## 执行方式

运行全部测试：

```
pytest
```

按类别运行：

```
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```

单个文件/测试：

```
pytest tests/test_sqlite_vec_storage.py::TestSqliteVecStorage::test_store_memory -q
```

结合 uv：

```
uv run pytest -q
```

## 关键行为与跳过策略

- SQLite-vec 测试在 `sqlite-vec` 不可用时会自动跳过：
  - 参见 `tests/test_sqlite_vec_storage.py` 中的 `pytestmark = pytest.mark.skipif(...)`；
- 部分测试通过将 `SENTENCE_TRANSFORMERS_AVAILABLE=False` 来模拟无嵌入模型场景，以验证回退逻辑；
- 测试使用临时目录隔离数据库文件，清理阶段会关闭连接。

## 覆盖的核心领域

- 存储 CRUD 与向量检索（`test_sqlite_vec_storage.py`）；
- 时间解析与时间戳回溯（`test_time_parser.py`、`test_timestamp_recall.py`）；
- 标签与元数据语义（`test_tag_storage.py`、`unit/test_tags.py`）；
- 健康检查与数据库初始化（`test_database.py`）；
- Cloudflare 适配器通过单元测试模拟网络行为（`unit/test_cloudflare_storage.py`）。

## 编写新增测试

- 对于存储 API，优先使用 `pytest.mark.asyncio`；
- 每个测试使用 `tempfile.mkdtemp()` 创建独立数据库路径；
- 利用 `src.mcp_memory_service.models.memory.Memory` 与 `generate_content_hash` 辅助函数；
- 后端特定行为的测试，应与对应后端测试文件放在一起，并通过可用性标志控制执行；
- 若测试 MCP 工具接口，推荐在独立进程或 `lifespan` 上下文中使用 FastMCP 服务器（`mcp_server.py`）。

## 本地 MCP/服务验证

Stdio 服务器：

```
uv run memory server
```

FastMCP HTTP 服务器：

```
uv run mcp-memory-server
```

使用任意 MCP 客户端（Claude Desktop/Code），依次调用 `store`、`retrieve`、`search_by_tag`、`delete`、`health` 等工具即可完成手动验证。

## 调试与日志

- 设置 `LOG_LEVEL=INFO` 以获取更多日志；
- Claude Desktop 环境下 stdout 会被抑制以保持 JSON 传输干净，可查看 stderr / warning；LM Studio 会在 stdout 输出更详细诊断信息；
- 常见 sqlite-vec 错误会附带处理建议，可参考 Troubleshooting 章节。
