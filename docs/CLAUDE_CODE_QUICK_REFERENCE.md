# Claude Code 快速参考（MCP Memory Service）

**一页速查表，助你高效使用 Claude Code 开发 MCP Memory Service。**

---

## 🎯 关键快捷键

| 按键 | 功能 | 场景 |
| --- | --- | --- |
| `Shift+Tab` | 接受建议 | 快速应用 Claude 修改 |
| `Esc` | 取消操作 | 终止不需要的动作 |
| `Ctrl+R` | 详细输出 | 调试故障 |
| `#` | 创建记忆 | 记录重要决策 |
| `@` | 添加上下文 | 引入文件/目录（`@src/`、`@tests/`） |
| `!` | Bash 模式 | 直接执行 Shell 命令 |

---

## 🚀 常见任务

### 记忆操作
```bash
/memory-store "Hybrid backend uses SQLite primary + Cloudflare secondary"
/memory-recall "how to configure Cloudflare backend"
/memory-health
```

### 开发流程
```bash
@src/mcp_memory_service/storage/
@tests/test_storage.py
pytest tests/test_storage.py -v
/memory-store "Changed X because Y"
```

### 后端配置
```bash
python scripts/server/check_http_server.py -v
python scripts/validation/validate_configuration_complete.py
python scripts/validation/diagnose_backend_config.py
```

### 同步
```bash
python scripts/sync/sync_memory_backends.py --status
python scripts/sync/sync_memory_backends.py --dry-run
python scripts/sync/sync_memory_backends.py --direction bidirectional
```

---

## 🏗️ 项目上下文

### 常加文件
| 目的 | 推荐添加 |
| --- | --- |
| 存储后端 | `@src/mcp_memory_service/storage/`
| MCP 协议 | `@src/mcp_memory_service/server.py`
| Web | `@src/mcp_memory_service/web/`
| 配置 | `@.env.example`, `@src/mcp_memory_service/config.py`
| 测试 | `@tests/test_*.py`
| 脚本 | `@scripts/server/`, `@scripts/sync/`

### 调试套路
```bash
python scripts/server/check_http_server.py -v
python scripts/validation/diagnose_backend_config.py
python scripts/sync/sync_memory_backends.py --status
@http_server.log
```

---

## 📚 架构速览

### 存储后端
| 后端 | 性能 | 场景 | 环境变量 |
| --- | --- | --- | --- |
| Hybrid ⭐ | 5ms | 生产首选 | `MCP_MEMORY_STORAGE_BACKEND=hybrid`
| SQLite-vec | 5ms | 开发/单人 | `=sqlite_vec`
| Cloudflare | 视网络而定 | 纯云遗留 | `=cloudflare`

### 目录结构
```
src/mcp_memory_service/
├── server.py
├── storage/
├── web/
└── config.py
scripts/
tests/
```

---

## 🔧 环境变量（`.env`）
```bash
MCP_MEMORY_STORAGE_BACKEND=hybrid
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_D1_DATABASE_ID=...
CLOUDFLARE_VECTORIZE_INDEX=...
MCP_HYBRID_SYNC_INTERVAL=300
MCP_HYBRID_BATCH_SIZE=50
MCP_HYBRID_SYNC_ON_STARTUP=true
MCP_HTTP_ENABLED=true
MCP_HTTPS_ENABLED=true
MCP_API_KEY=...
```

---

## 🐛 排障清单

### HTTP Server
- `python scripts/server/check_http_server.py -v`
- 查看 `@http_server.log`
- `scripts/server/start_http_server.bat`
- `netstat -ano | findstr :8001`

### 后端配置
- `python scripts/validation/diagnose_backend_config.py`
- 检查 `.env`
- 校验 Cloudflare 凭据
- 观察启动日志

### 记忆缺失
- `python scripts/sync/sync_memory_backends.py --status`
- 对比云端与本地数量
- `--dry-run` 预演同步
- 检查内容哈希是否重复

### 性能
- Hybrid 读取应 ~5ms。
- 磁盘剩余足够（Litestream）。
- 查看 `http_server.log` 中的同步。
- 确认嵌入模型只加载一次。

---

## 💡 提示

### 上下文管理
```bash
@src/.../hybrid.py   # 精确
@src/.../storage/    # 扩展
Esc 取消多余上下文
```

### TodoWrite
- 复杂任务使用 TodoWrite 生成步骤。
- 示例：实现新后端 → 调研、实现、配置、测试、文档。

### 测试策略
```bash
pytest tests/test_storage.py::TestHybridBackend -v
pytest tests/ -v
pytest tests/ --cov=src/mcp_memory_service --cov-report=term
```

### Git 协作
```bash
git status
git diff
git commit -m "feat: add new backend support"
```

---

## 📖 额外资源
- `@CLAUDE.md`（项目指南）
- `~/.claude/CLAUDE.md`（全局规范）
- Wiki：https://github.com/doobidoo/mcp-memory-service/wiki
- 故障排除：Wiki 专章

**最后更新**：2025-10-08
