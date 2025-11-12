# Glama 部署指南

本文档介绍如何在 Glama 平台上部署 MCP Memory Service。

## 概览

MCP Memory Service 已发布在 Glama： https://glama.ai/mcp/servers/bzvl3lz34o

Glama 是一个 MCP 服务器目录，帮助用户快速发现并部署所需服务。

## Glama 专用 Docker 配置

### 主 Dockerfile

仓库提供了针对 Glama 优化的 Dockerfile：

- `Dockerfile`：主生产镜像。
- `Dockerfile.glama`：面向 Glama 的版本，附带增强标签与健康检查。

### 关键特性

1. **多平台支持**：兼容 x86_64 与 ARM64 架构。
2. **健康检查**：内置容器状态监控。
3. **数据持久化**：为 ChromaDB 与备份预设卷挂载。
4. **环境配置**：优化默认性能参数。
5. **安全性**：基于精简 Python 镜像，攻击面更小。

### Glama 快速启动

用户可直接使用 Glama 提供的配置：

```bash
# 使用 Glama 预设配置
docker run -d -p 8001:8001 \
  -v $(pwd)/data/chroma_db:/app/chroma_db \
  -v $(pwd)/data/backups:/app/backups \
  doobidoo/mcp-memory-service:latest
```

### 环境变量

以下环境变量已默认配置：

| 变量 | 值 | 作用 |
| --- | --- | --- |
| `MCP_MEMORY_CHROMA_PATH` | `/app/chroma_db` | ChromaDB 存储目录 |
| `MCP_MEMORY_BACKUPS_PATH` | `/app/backups` | 备份目录 |
| `DOCKER_CONTAINER` | `1` | 标记容器环境 |
| `CHROMA_TELEMETRY_IMPL` | `none` | 关闭 ChromaDB 遥测 |
| `PYTORCH_ENABLE_MPS_FALLBACK` | `1` | 允许 Apple Silicon 使用 MPS 回退 |

### 独立模式

若需要在没有 MCP 客户端时运行，可启用独立模式：

```bash
docker run -d -p 8001:8001 \
  -e MCP_STANDALONE_MODE=1 \
  -v $(pwd)/data/chroma_db:/app/chroma_db \
  -v $(pwd)/data/backups:/app/backups \
  doobidoo/mcp-memory-service:latest
```

## Glama 平台集成

### 服务器校验

该 Dockerfile 已通过 Glama 的所有服务器校验：

- ✅ Dockerfile 语法有效
- ✅ 合规基础镜像
- ✅ 遵循安全最佳实践
- ✅ 实施健康检查
- ✅ 配置数据卷
- ✅ 正确暴露端口

### 用户体验

Glama 用户可获得：

1. **一键部署**：直接在 Glama 界面启动。
2. **预配置参数**：开箱即用。
3. **集成文档**：包含快速设置说明。
4. **社区反馈**：可查看评分与评论。
5. **版本追踪**：获知更新与通知。

### 监控与健康状态

Docker 镜像内置健康检查，用于确认：

- Python 运行环境可用。
- MCP Memory Service 可成功导入。
- 依赖完整且加载正常。

## 维护

### 更新

满足以下条件时，Glama 列表会自动同步：

1. GitHub 仓库打出新的 tag。
2. Docker 镜像发布到 Docker Hub。
3. 相关文档发生更新。

### 支持

遇到 Glama 相关问题时，可按顺序排查：

1. 查看 Glama 平台文档。
2. 确认 Docker 配置正确。
3. 读取容器日志定位报错。
4. 切换到独立模式排查调试。

## 参与贡献

若希望改进 Glama 集成，可以：

1. 在不同平台测试部署流程。
2. 反馈安装体验与问题。
3. 提出 Docker 配置优化建议。
4. 报告特定平台的兼容性问题。

目标：让 6 万+ Glama 月活用户都能方便地访问 MCP Memory Service。
