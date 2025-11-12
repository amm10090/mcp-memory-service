# HTTP/SSE + SQLite-vec 实施计划

**日期**：2025-07-25  
**状态**：摘自历史规划会议  
**背景**：Issue #57 - 为 MCP Memory Service 增加 HTTP/SSE 接口

## 摘要

在保留全部 MCP 能力的前提下，引入 HTTP REST API 与 Server-Sent Events（SSE）接口，并使用现有的 sqlite-vec 后端取代 ChromaDB，打造轻量、易部署、适合边缘环境的方案。

## 关键决策

选择 **HTTP/SSE + sqlite-vec** 的组合（而非 ChromaDB），原因：

- 部署简单（单文件数据库）。
- 性能更优（操作快 10 倍）。
- 适合边缘部署（Cloudflare Workers、Vercel）。
- 无外部依赖。
- 借助 SQLite 触发器即可即时推送 SSE。

## 实施阶段

### 阶段 1：基础（第 1 周）
- ✅ 从 sqlite-vec-backend 分支创建 Feature Branch。
- ✅ 创建 PROJECT_STATUS.md。
- [ ] 验证 sqlite-vec 功能。
- [ ] 添加 FastAPI 依赖。
- [ ] 完成开发环境搭建。

### 阶段 2：HTTP（第 2 周）
- [ ] 构建 Web Server 结构。
- [ ] 健康检查端点。
- [ ] 记忆 CRUD。
- [ ] 搜索端点。
- [ ] OpenAPI 文档。

### 阶段 3：SSE（第 3 周）
- [ ] 设计 SSE 事件架构。
- [ ] SQLite 触发器。
- [ ] `/events` 端点。
- [ ] 连接管理。
- [ ] 实时更新测试。

### 阶段 4：Dashboard（第 4 周）
- [ ] 轻量 UI（Vanilla JS）。
- [ ] 记忆可视化。
- [ ] SSE 连接管理。
- [ ] 搜索界面。
- [ ] 响应式设计。

## 技术架构

```
src/mcp_memory_service/
├── web/
│   ├── app.py        # FastAPI 应用
│   ├── sse.py        # SSE 处理
│   ├── api/
│   │   ├── memories.py  # CRUD
│   │   ├── search.py    # 检索
│   │   └── health.py    # 健康
│   └── static/
│       ├── index.html
│       ├── app.js
│       └── style.css
├── storage/
│   ├── sqlite_vec.py
│   └── sqlite_sse.py   # 新增：触发器
```

### 运行模式
1. MCP 模式：原生 stdio（保持不变）。
2. HTTP 模式：FastAPI + SSE。
3. Hybrid：两种协议同时开启。

### SSE 事件
- `memory_stored`
- `memory_deleted`
- `search_completed`
- `backup_status`
- `health_update`

### API 端点
- `GET /api/health`
- `GET /api/memories`
- `POST /api/memories`
- `GET /api/memories/{id}`
- `DELETE /api/memories/{id}`
- `POST /api/search`
- `POST /api/search/by-tag`
- `POST /api/search/by-time`
- `GET /events`

## 依赖
```
fastapi>=0.115.0
uvicorn>=0.30.0
python-multipart>=0.0.9
sse-starlette>=2.1.0
aiofiles>=23.2.1
```

## 配置
```python
HTTP_ENABLED = 'MCP_HTTP_ENABLED'
HTTP_PORT = 'MCP_HTTP_PORT'  # 默认 8001
HTTP_HOST = 'MCP_HTTP_HOST'  # 默认 0.0.0.0
CORS_ORIGINS = 'MCP_CORS_ORIGINS'
SSE_HEARTBEAT_INTERVAL = 'MCP_SSE_HEARTBEAT'  # 默认 30s
API_KEY = 'MCP_API_KEY'  # 可选
```

## 性能指标
- 写入 <50ms（ChromaDB 约 500ms）。
- 1M 记忆检索 <100ms。
- SSE 延迟 <10ms。
- 启动 <1s（ChromaDB 需 5-10s）。

## 测试策略
- HTTP 端点单测。
- SSE 集成测试。
- 与 ChromaDB 的性能对比。
- 浏览器兼容性。
- 边缘部署验证。

## 安全
- 可选 API Key 认证。
- CORS 配置。
- 限流。
- 输入校验。
- SSL/TLS 文档。

## 迁移
- 原 MCP 用户：无需变更。
- ChromaDB 用户：提供迁移脚本。
- 新用户：HTTP 模式默认 sqlite-vec。

## 收益
- 简洁：单文件数据库。
- 性能：数量级提升。
- 便携：可运行在任意 Python 环境。
- 稳定：依赖 SQLite。
- 现代：HTTP/SSE/REST。
- 高效：资源占用低。
- 边缘友好：可部署到 CDN Edge。

## 后续可能
- 搭配 Litestream 的分布式 SQLite。
- Cloudflare Workers + D1。
- 基于 WASM 的离线 PWA。
- 多实例联邦。

## 成功标准
- HTTP/SSE 满足性能目标。
- Dashboard 提供直观管理体验。
- 文档指导部署无障碍。
- ChromaDB 迁移顺畅。
- 边缘部署可在主流平台运行。

---

该计划在保持向后兼容的同时，带来显著架构升级。
