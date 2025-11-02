# MCP Memory Service — 配置指南

所有配置均通过环境变量驱动，默认值在 `src/mcp_memory_service/config.py` 中解析。

## 基础路径

- `MCP_MEMORY_BASE_DIR`：服务数据根目录。不同操作系统默认指向对应的应用数据路径，若不存在会自动创建。
- 自动派生（若未覆盖同样会创建）：
  - Chroma 路径：`${BASE_DIR}/chroma_db`；
  - 备份路径：`${BASE_DIR}/backups`。

可覆盖项：

- `MCP_MEMORY_CHROMA_PATH` / `mcpMemoryChromaPath`：ChromaDB 目录；
- `MCP_MEMORY_BACKUPS_PATH` / `mcpMemoryBackupsPath`：备份目录。

## 存储后端选择

- `MCP_MEMORY_STORAGE_BACKEND`：取值 `sqlite_vec`（默认）、`chroma` 或 `cloudflare`。
  - `sqlite-vec` 会被归一化为 `sqlite_vec`；
  - 未知值将回退到 `sqlite_vec` 并输出警告。

SQLite-vec 相关：

- `MCP_MEMORY_SQLITE_PATH` / `MCP_MEMORY_SQLITEVEC_PATH`：`.db` 文件路径，默认 `${BASE_DIR}/sqlite_vec.db`；
- `MCP_MEMORY_SQLITE_PRAGMAS`：自定义 pragma 的 CSV，例如 `busy_timeout=15000,cache_size=20000`（v8.9.0+ 推荐用于并发访问）。

Chroma 相关：

- `MCP_MEMORY_CHROMADB_HOST`：远程 Chroma 主机；
- `MCP_MEMORY_CHROMADB_PORT`：端口（默认 8001）；
- `MCP_MEMORY_CHROMADB_SSL`：`true|false`，是否启用 HTTPS；
- `MCP_MEMORY_CHROMADB_API_KEY`：远程访问时的 API key；
- `MCP_MEMORY_COLLECTION_NAME`：集合名称（默认 `memory_collection`）。

Cloudflare 相关（除非注明均为必填）：

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_VECTORIZE_INDEX`
- `CLOUDFLARE_D1_DATABASE_ID`
- `CLOUDFLARE_R2_BUCKET`（可选，大文件使用）
- `CLOUDFLARE_EMBEDDING_MODEL`（默认 `@cf/baai/bge-base-en-v1.5`）
- `CLOUDFLARE_LARGE_CONTENT_THRESHOLD`（字节数，默认 1,048,576）
- `CLOUDFLARE_MAX_RETRIES`（默认 3）
- `CLOUDFLARE_BASE_DELAY`（秒，默认 1.0）

## 嵌入模型

- `MCP_EMBEDDING_MODEL`：模型名称（默认 `all-MiniLM-L6-v2`）；
- `MCP_MEMORY_USE_ONNX`：`true|false`，是否启用 ONNX 路径。

## HTTP/HTTPS 接口

- `MCP_HTTP_ENABLED`：`true|false`，是否启用 HTTP；
- `MCP_HTTP_HOST`：绑定地址（默认 `0.0.0.0`）；
- `MCP_HTTP_PORT`：端口（默认 `8001`）；
- `MCP_CORS_ORIGINS`：逗号分隔的允许 Origin（默认 `*`）；
- `MCP_SSE_HEARTBEAT`：SSE 心跳间隔（秒，默认 30）；
- `MCP_API_KEY`：可选 HTTP 接口密钥。

TLS 相关：

- `MCP_HTTPS_ENABLED`：`true|false`；
- `MCP_SSL_CERT_FILE`、`MCP_SSL_KEY_FILE`：证书与私钥路径。

## mDNS 服务发现

- `MCP_MDNS_ENABLED`：`true|false`（默认 `true`）；
- `MCP_MDNS_SERVICE_NAME`：服务展示名称（默认 `MCP Memory Service`）；
- `MCP_MDNS_SERVICE_TYPE`：服务类型（默认 `_mcp-memory._tcp.local.`）；
- `MCP_MDNS_DISCOVERY_TIMEOUT`：发现超时时长（秒，默认 5）。

## 记忆整合（可选）

- `MCP_CONSOLIDATION_ENABLED`：`true|false`；
- 归档路径：`MCP_CONSOLIDATION_ARCHIVE_PATH` / `MCP_MEMORY_ARCHIVE_PATH`（默认 `${BASE_DIR}/consolidation_archive`）。
- 配置项：
  - 衰减：`MCP_DECAY_ENABLED`，类型保留策略：`MCP_RETENTION_CRITICAL`、`MCP_RETENTION_REFERENCE`、`MCP_RETENTION_STANDARD`、`MCP_RETENTION_TEMPORARY`；
  - 关联：`MCP_ASSOCIATIONS_ENABLED`、`MCP_ASSOCIATION_MIN_SIMILARITY`、`MCP_ASSOCIATION_MAX_SIMILARITY`、`MCP_ASSOCIATION_MAX_PAIRS`；
  - 聚类：`MCP_CLUSTERING_ENABLED`、`MCP_CLUSTERING_MIN_SIZE`、`MCP_CLUSTERING_ALGORITHM`；
  - 压缩：`MCP_COMPRESSION_ENABLED`、`MCP_COMPRESSION_MAX_LENGTH`、`MCP_COMPRESSION_PRESERVE_ORIGINALS`；
  - 遗忘：`MCP_FORGETTING_ENABLED`、`MCP_FORGETTING_RELEVANCE_THRESHOLD`、`MCP_FORGETTING_ACCESS_THRESHOLD`。
- 调度（兼容 APScheduler）：`MCP_SCHEDULE_DAILY`（默认 `02:00`）、`MCP_SCHEDULE_WEEKLY`（默认 `SUN 03:00`）、`MCP_SCHEDULE_MONTHLY`（默认 `01 04:00`）、`MCP_SCHEDULE_QUARTERLY`（默认 `disabled`）、`MCP_SCHEDULE_YEARLY`（默认 `disabled`）。

## 机器标识

- `MCP_MEMORY_INCLUDE_HOSTNAME`：`true|false`，设置后会为记忆附加 `source:<hostname>` 标签并写入 `hostname` 元数据。

## 日志与性能

- `LOG_LEVEL`：根日志级别（默认 `WARNING`）；
- `DEBUG_MODE`：若未设置，服务会将 `chromadb`、`sentence_transformers`、`transformers`、`torch`、`numpy` 等性能敏感库的日志级别提升到 WARNING。

## 各后端推荐默认值

- SQLite-vec：默认启用 WAL、busy_timeout、优化缓存；可借助 `MCP_MEMORY_SQLITE_PRAGMAS` 定制。多客户端场景下，服务会自动检测并按需开启 HTTP 协调；
- ChromaDB：默认 HNSW 参数兼顾性能与准确率，并提示其退场信息，建议迁移至 SQLite-vec；
- Cloudflare：若缺少必需变量，服务会直接退出并提供明确的待配置清单。
