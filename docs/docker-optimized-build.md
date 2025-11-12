# Docker 优化构建指南

## 概览

Docker 镜像现默认使用 **sqlite_vec** + 轻量 **ONNX** 嵌入，移除 ChromaDB / PyTorch / sentence-transformers 等重依赖，实现：
- 构建速度提升 70-80%。
- 镜像减小 1-2 GB。
- 内存占用更低，启动更快。

## 构建方式

```bash
docker build -f tools/docker/Dockerfile -t mcp-memory-service:latest .
# 或 docker-compose
docker-compose -f tools/docker/docker-compose.yml build
```
> 默认包含 SQLite-vec + ONNX Runtime（依赖约 100MB）。

**Slim**：
```bash
docker build -f tools/docker/Dockerfile.slim -t mcp-memory-service:slim .
```
仅含核心服务，约 50MB 依赖。

**Full ML**：
```bash
docker build -f tools/docker/Dockerfile -t mcp-memory-service:full \
  --build-arg INSTALL_EXTRA="[sqlite-ml]"
```
加入 PyTorch + sentence-transformers 等（≈2GB）。

## 运行
```bash
docker run -it \
  -e MCP_MEMORY_STORAGE_BACKEND=sqlite_vec \
  -v ./data:/app/data \
  mcp-memory-service:latest
```
或 docker-compose up/down/logs。

## 存储后端
default：`sqlite_vec`。如需 ChromaDB：
```dockerfile
RUN pip install -e .          # 仅 SQLite-vec
RUN pip install -e .[sqlite]  # 轻量 ONNX 嵌入
RUN pip install -e .[sqlite-ml]  # 完整 ML
RUN pip install -e .[chromadb]   # 启用 ChromaDB
```
本地脚本：`python scripts/installation/install.py --with-ml/--with-chromadb`，再构建。

## 环境变量示例
```yaml
environment:
  - MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
  - MCP_MEMORY_SQLITE_PATH=/app/data/sqlite_vec.db
  - MCP_MEMORY_BACKUPS_PATH=/app/data/backups
  - MCP_MEMORY_USE_ONNX=1
  - LOG_LEVEL=INFO
```

## 多架构构建
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f tools/docker/Dockerfile \
  -t mcp-memory-service:latest \
  --push .
```

## 体积/时间对比

| 类型 | 含 ChromaDB | 仅 SQLite-vec |
| --- | --- | --- |
| 镜像 | ~2.5GB | ~0.8GB |
| Slim | — | ~0.4GB |
| 构建时间 | 10-15 分钟 | 2-3 分钟 |
| Slim | — | 1-2 分钟 |

## 迁移
1. `docker exec mcp-memory-chromadb python scripts/backup/backup_memories.py`
2. 启动新容器 `docker-compose ... up -d`
3. `docker exec mcp-memory-sqlite python scripts/backup/restore_memories.py`

## 常见问题
- 需要 ML/Chroma：重新安装 `--with-ml` 或 `--with-chromadb` 并重建。
- `ImportError: chromadb ...`：提示按需安装或改用 sqlite_vec。

## 最佳实践
1. 优先使用轻量默认镜像。
2. 仅在需要语义检索时增加 `[ml]` 依赖。
3. 单机部署 → sqlite_vec；生产多端 → Cloudflare；特殊需求 → ChromaDB。
4. 利用 Docker layer cache。
5. 生产环境使用 slim 版减少攻击面。

## CI/CD
```yaml
- name: Build optimized Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    file: ./tools/docker/Dockerfile
    platforms: linux/amd64,linux/arm64
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    build-args: |
      SKIP_MODEL_DOWNLOAD=true
```
`SKIP_MODEL_DOWNLOAD=true` 可进一步减少构建时间。
