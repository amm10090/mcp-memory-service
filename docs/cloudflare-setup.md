# Cloudflare 后端配置指南

## 概览

MCP Memory Service 原生支持 Cloudflare：
- **Vectorize**：存放 768 维向量，负责语义检索。
- **D1**：SQLite 兼容数据库，记录元数据。
- **Workers AI**：调用 `@cf/baai/bge-base-en-v1.5` 生成向量。
- **R2（可选）**：存储大对象。

该方案具备全球分发、自动扩缩、按使用计费等优势。

## 🚀 快速上手

### 前提
1. Cloudflare 账号（需开通 Workers/D1/Vectorize）。
2. API Token，包含：Vectorize Edit、D1 Edit、（可选）R2 Edit、Workers AI Read。

### 命令
```bash
pip install httpx>=0.24.0
wrangler vectorize create mcp-memory-index --dimensions=768 --metric=cosine
wrangler d1 create mcp-memory-db
wrangler r2 bucket create mcp-memory-content   # 可选

export MCP_MEMORY_STORAGE_BACKEND=cloudflare
export CLOUDFLARE_API_TOKEN=...
export CLOUDFLARE_ACCOUNT_ID=...
export CLOUDFLARE_VECTORIZE_INDEX=mcp-memory-index
export CLOUDFLARE_D1_DATABASE_ID=...
export CLOUDFLARE_R2_BUCKET=mcp-memory-content  # 可选

python -m src.mcp_memory_service.server
```
> ⚠️ 不要使用 `scripts/memory_offline.py`（会禁用 Workers AI）。

## 步骤 1：创建资源

```bash
npm install -g wrangler
wrangler login
wrangler vectorize create mcp-memory-index --dimensions=768 --metric=cosine
wrangler d1 create mcp-memory-db
wrangler r2 bucket create mcp-memory-content  # 可选
```

## 步骤 2：API Token
- Dashboard → Profile → API Tokens → Create Token。
- 权限：Account Read、Vectorize Edit、D1 Edit、（可选）R2 Edit、Workers AI Read。
- 记录 Account ID。
- 可在 Dashboard / API 手动创建 Vectorize、D1、R2（见原命令示例）。

## 步骤 3：环境变量
```bash
export MCP_MEMORY_STORAGE_BACKEND=cloudflare
export CLOUDFLARE_API_TOKEN=...
export CLOUDFLARE_ACCOUNT_ID=...
export CLOUDFLARE_VECTORIZE_INDEX=mcp-memory-index
export CLOUDFLARE_D1_DATABASE_ID=...
export CLOUDFLARE_R2_BUCKET=mcp-memory-content
export CLOUDFLARE_EMBEDDING_MODEL=@cf/baai/bge-base-en-v1.5
export CLOUDFLARE_LARGE_CONTENT_THRESHOLD=1048576
export CLOUDFLARE_MAX_RETRIES=3
export CLOUDFLARE_BASE_DELAY=1.0
```
`.env` 示例同上。

## 步骤 4：依赖
```bash
pip install -r requirements-cloudflare.txt
# 或 pip install httpx>=0.24.0
```

## 步骤 5：初始化与测试
```bash
python -m src.mcp_memory_service.server
```
日志应包含 `Using Cloudflare backend...` 等信息。

### 基础测试
- `python scripts/test_cloudflare_backend.py`
- 或使用 `curl` 访问 `/api/memories`、`/api/stats`。
- 也可运行 `python scripts/setup_cloudflare_resources.py` 自动化检查。

## 架构亮点
- 小内容（<1MB）直接写 D1，大内容写 R2 并于 D1 建索引。
- 内容 → Workers AI → 向量 → Vectorize 存储。
- 元数据与标签保存在 D1。
- 采用连接池、嵌入缓存、批量操作与指数退避等优化。

## 迁移
```bash
python scripts/export_sqlite_vec.py --output cloudflare.json
export MCP_MEMORY_STORAGE_BACKEND=cloudflare
python scripts/import_to_cloudflare.py --input cloudflare.json
```
ChromaDB 同理（先导出再导入）。

## 故障排查

| 现象 | 解决 |
| --- | --- |
| 401/缺变量 | 检查 env，确认 Token 权限。|
| 404 资源不存在 | 核对 Index/DB 名称是否正确。|
| 向量存储 400 | 确认维度为 768、NDJSON 格式、元数据序列化。|
| D1 初始化失败 | 核对 DB ID、Token 权限。|
| 429 速率限制 | 调大 `CLOUDFLARE_MAX_RETRIES`、`CLOUDFLARE_BASE_DELAY`，监控使用量。|

调试：`LOG_LEVEL=DEBUG python -m src.mcp_memory_service.server --debug`。

健康检查：
```bash
curl http://localhost:8001/api/health
curl http://localhost:8001/api/stats
```

## 限制与规划
- 当前固定使用 BGE 模型（768 维）。
- >1MB 内容需 R2。
- 受 Cloudflare 速率限制影响。
- 计划支持本地嵌入、自定义模型、增强缓存、批量导入工具等。

## 🔄 多机双向同步（v6.13.7+）

- 适用场景：替代故障服务器、多机开发、团队共享、备份策略。
- 架构：各机本地 sqlite_vec 做备份，Cloudflare 作主库。
- 步骤：导出旧数据→导入 Cloudflare→每台机器配置相同 env（含 `MCP_MEMORY_SQLITE_PATH`）。
- 注意：v6.13.7 修复 Vectorize ID 长度问题；旧版需升级。

## 性能
- 存储：约 200ms（含嵌入生成）。
- 检索：5 条结果约 100ms。
- 批量：100 条约 50ms/条。
- 全球延迟：<100ms。

提升建议：批量接口、R2 存大内容、开启嵌入缓存、复用连接、部署在靠近用户的区域。

## 支持渠道
- 阅读本指南与 API 文档。
- GitHub 提 Issue。
- Cloudflare 官方支持（服务相关问题）。
- 社区交流渠道。
