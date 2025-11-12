# Docker 部署指南

## 概览
支持多种模式：标准（供 MCP 客户端）、Standalone（测试/防止 boot loop）、HTTP/SSE、多副本生产等。

## 先决条件
Docker 20.10+、Docker Compose 2.0+、足够磁盘空间。

## 快速开始
```bash
git clone https://github.com/doobidoo/mcp-memory-service.git
cd mcp-memory-service
docker-compose up -d
```
`docker-compose.yml` 默认使用 Chromadb 后端并挂载 `./data/chroma_db`、`./data/backups`。

## 常用 Compose 变体
- `docker-compose.standalone.yml`：`MCP_STANDALONE_MODE=1`，映射 `8001`，适合测试/HTTP；
- `docker-compose.uv.yml`：启用 UV 包管理；
- `docker-compose.pythonpath.yml`：自定义 PYTHONPATH；
- `docker-compose.logging.yml`：配置日志滚动；
- `docker-compose.monitoring.yml`：暴露 metrics、接入 Prometheus。

## 手动 Docker
```bash
docker build -t mcp-memory-service .
mkdir -p data/chroma_db data/backups
# 标准模式
docker run -d --name memory-service \
  -v $(pwd)/data/chroma_db:/app/chroma_db \
  -v $(pwd)/data/backups:/app/backups \
  -e MCP_MEMORY_STORAGE_BACKEND=chromadb \
  --stdin --tty mcp-memory-service
# Standalone/HTTP
docker run -d -p 8001:8001 --name memory-service \
  -v $(pwd)/data:/app/data \
  -e MCP_STANDALONE_MODE=1 -e MCP_HTTP_HOST=0.0.0.0 -e MCP_HTTP_PORT=8001 \
  --stdin --tty mcp-memory-service
```

## 环境变量
- `MCP_MEMORY_STORAGE_BACKEND`（chromadb/sqlite_vec）；
- `MCP_HTTP_HOST/PORT`、`MCP_STANDALONE_MODE`；
- `MCP_API_KEY`（认证）；
- Docker 特有：`DOCKER_CONTAINER`、`UV_ACTIVE`、`PYTHONPATH` 等。

## 生产部署
- Docker Compose + `restart: unless-stopped` 或 Swarm/K8s；
- 示例 `docker-stack.yml`、`k8s-deployment.yml` 展示副本、资源限制、Secret/Volume 配置；
- 建议使用命名卷或 PVC 持久化数据；
- 时常备份：`docker run --rm -v volume:/data ... tar czf backup.tar.gz /data`。

## 监控与日志
- `healthcheck`：`curl -f http://localhost:8001/health`；
- 日志：`docker-compose logs -f` 或配置 json-file 滚动；
- Prometheus：通过环境变量开启 metrics 并暴露端口。

## 常见问题
1. **容器秒退**：未开启 Standalone／缺少 TTY → `stdin_open: true`、`tty: true`；
2. **权限**：`chown -R 1000:1000 ./data` 或使用 `--user`；
3. **存储错误**：改用 SQLite-vec 并挂载 `/app/sqlite_data`；
4. **网络不可达**：确认端口映射、`curl http://localhost:8001/health`；
5. **模型下载失败**：预下载 HuggingFace 模型并挂载 `~/.cache/huggingface`，或设置代理/离线变量。

## 诊断命令
```bash
docker ps -a
docker logs memory-service
docker exec -it memory-service bash
curl http://localhost:8001/health
```
验证模型缓存：挂载 `~/.cache/huggingface` 并在容器运行 `SentenceTransformer('all-MiniLM-L6-v2')`。

## 安全
- 设置 `MCP_API_KEY=$(openssl rand -hex 32)`；
- HTTPS：挂载证书并设置 `MCP_HTTPS_ENABLED=true`、`MCP_SSL_CERT_FILE/KEY_FILE`；
- 容器限制：`--security-opt no-new-privileges:true --cap-drop ALL --read-only --tmpfs /tmp`。

## 性能
- Compose/Swarm/K8s 配置 CPU/Mem 限制；
- 多阶段 Dockerfile 降低镜像体积；
- 开发模式：`docker-compose.dev.yml` + 实时日志；
- 构建多架构镜像：`docker buildx build --platform linux/amd64,linux/arm64 ...`。

更多细节请参阅安装指南、Multi-Client 配置及平台特定部署文档。
