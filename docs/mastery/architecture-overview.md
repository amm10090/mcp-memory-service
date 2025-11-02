# MCP Memory Service — 架构概览

本文总结了 Memory Service 的整体架构、组件构成、数据流以及 MCP 集成方式。

## 高层设计

- 客户端：Claude Desktop/Code、VS Code、Cursor、Continue 及其他兼容 MCP 的客户端；
- 协议层：
  - MCP stdio 服务器：`src/mcp_memory_service/server.py`（基于 `mcp.server.Server`）；
  - FastAPI MCP 服务器：`src/mcp_memory_service/mcp_server.py`（通过 `FastMCP` 提供可流式的 HTTP 访问能力）；
- 核心领域：
  - 数据模型：`src/mcp_memory_service/models/memory.py` 中定义的 `Memory`、`MemoryQueryResult`；
  - 工具集：哈希、时间解析、系统检测、HTTP 协调等辅助模块；
- 存储抽象：
  - 接口：`src/mcp_memory_service/storage/base.py` 中的 `MemoryStorage` 抽象类；
  - 后端实现：
    - SQLite-vec：`src/mcp_memory_service/storage/sqlite_vec.py`（推荐默认方案）；
    - ChromaDB：`src/mcp_memory_service/storage/chroma.py`（已弃用，提供迁移路径）；
    - Cloudflare：`src/mcp_memory_service/storage/cloudflare.py`（Vectorize + D1 + 可选 R2）；
    - HTTP 客户端：`src/mcp_memory_service/storage/http_client.py`（面向多客户端协调）；
- CLI：
  - 入口命令：`memory`、`memory-server`、`mcp-memory-server`（PyProject 定义的脚本）；
  - 实现：`src/mcp_memory_service/cli/main.py`（服务器、状态、入库等子命令）；
- 配置与环境：
  - 中央化配置：`src/mcp_memory_service/config.py`（路径、后端选择、HTTP/HTTPS、mDNS、记忆整合、主机名标记、Cloudflare 设置等）；
- 记忆整合（可选）：关联、聚类、压缩、遗忘等功能在启用时按需懒加载。

## 数据流

1. 客户端通过 MCP（stdio 或 FastMCP HTTP）调用工具/提示；
2. 服务器通过 `config.py` 解析后端配置，并按需初始化存储；
3. 当使用 SQLite-vec 时：
   - 由 `sentence-transformers`（或启用 ONNX 的轻量路径）生成向量，与内容及元数据一同写入 SQLite；查询通过 `vec0` 虚拟表完成；
   - 采用 WAL 模式 + busy timeout 以支持并发；多客户端场景下可通过 HTTP 协调；
4. 使用 ChromaDB 时：依赖 DuckDB + Parquet 持久化及 HNSW 设置（已弃用，会提示迁移）；
5. 使用 Cloudflare 时：向量存储于 Vectorize，元数据在 D1，大对象可用 R2；通过 HTTPx 调用 API；
6. 结果映射回 `Memory`/`MemoryQueryResult`，再返回给 MCP 客户端。

## MCP 集成模式

- Stdio MCP（`server.py`）：
  - 基于 `mcp.server.Server` 注册记忆操作、诊断、分析等工具与提示；
  - 采用 `DualStreamHandler` 识别客户端：在 Claude Desktop 中保持 stdout 干净（仅输出 JSON），在 LM Studio 等环境输出更详尽日志；
  - 协调逻辑：检测是否需要启动 HTTP 辅助以支持多客户端访问，并按需启用 `HTTPClientStorage`。

- FastMCP（`mcp_server.py`）：
  - 通过 `lifespan` 管理存储生命周期，使用 `@mcp.tool()` 暴露核心工具（`store_memory`、`retrieve_memory`、`search_by_tag`、`delete_memory`、`check_database_health` 等）；
  - 旨在支持远程/HTTP 访问，兼容 Claude Code 的 `streamable-http` 传输模式。

## 存储层抽象

- `MemoryStorage` 接口定义了 `initialize`、存储、检索/搜索、按标签搜索、删除、`delete_by_tag`、`cleanup_duplicates`、`update_memory_metadata`、`get_stats` 等方法，并可扩展标签/时间范围相关辅助函数；
- 不同后端遵循此接口，可通过 `MCP_MEMORY_STORAGE_BACKEND` 自由切换。

## 配置管理

- 路径：基础目录及各后端的存储路径（自动创建并检查可写性）；
- 后端选择：`MCP_MEMORY_STORAGE_BACKEND` ∈ `{sqlite_vec, chroma, cloudflare}`；
- HTTP/HTTPS 服务、CORS、API Key、SSE 心跳；
- mDNS 发现开关及超时设置；
- 记忆整合：启用标志、归档路径、衰减/关联/聚类/压缩/遗忘参数、APScheduler 定时策略；
- 主机名标记：`MCP_MEMORY_INCLUDE_HOSTNAME` 自动附加来源主机信息；
- Cloudflare：令牌、账户、Vectorize 索引、D1 数据库、可选 R2、重试策略。

## 依赖与职责

- `mcp`：提供 MCP 协议服务器/运行时；
- `sqlite-vec`：SQLite 向量索引，实现 `vec0` 虚拟表；
- `sentence-transformers`、`torch`：负责嵌入生成，可通过配置禁用；
- `chromadb`：遗留后端（DuckDB + Parquet）；
- `fastapi`、`uvicorn`、`sse-starlette`、`aiofiles`、`aiohttp/httpx`：HTTP 传输与 Cloudflare/外部 API 支持；
- `psutil`、`zeroconf`：客户端检测与 mDNS 服务发现。

## 日志与诊断

- 客户端感知型日志处理器避免在 Claude 中输出多余 stdout（保持 JSON 纯净），对 LM Studio 等环境提供 info 级别日志；
- 可通过 `LOG_LEVEL` 环境变量设置根日志级别（默认 WARNING）；除非启用 `DEBUG_MODE`，性能敏感的第三方日志默认提升至 WARNING。

## 性能与并发

- SQLite-vec 默认启用 WAL、`busy_timeout`、`synchronous=NORMAL`、`cache_size`、`temp_store` 等设置；
- 可通过 `MCP_MEMORY_SQLITE_PRAGMAS` 注入自定义 pragma；
- 嵌入模型缓存并仅加载一次；启用 ONNX 时可减轻依赖；
- 维护平均查询耗时、异步操作以及可选的整合调度器。
