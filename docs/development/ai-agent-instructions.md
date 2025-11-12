# AI Agent 指南

面向 MCP Memory Service 的 AI 编码代理说明——该项目实现 MCP 语义记忆服务，支持 SQLite-vec / Cloudflare 等多后端，适配 Claude Desktop、VS Code、Cursor、Continue 等 13+ 应用。

## 项目概览
- MCP Memory Service 提供语义检索与持久存储能力；
- MCP 接口 + HTTP API + Dashboard；
- 核心后端：SQLite-vec（默认）/ ChromaDB / Cloudflare D1+Vectorize。

## 环境与启动
```bash
# 必须使用 editable 安装，否则代码修改不会生效
pip install -e .          # 或 uv pip install -e .

# 确认安装位置（应指向源码目录）
pip show mcp-memory-service | grep Location

# 检查版本一致性，排查陈旧 venv
python scripts/validation/check_dev_setup.py

# 启动 MCP 服务
uv run memory server

# 使用 MCP Inspector 调试
npx @modelcontextprotocol/inspector uv run memory server

# 启动 HTTP（Dashboard: https://localhost:8443）
uv run memory server --http --port 8443
```
> 若版本输出与代码不符（如服务仍是 v8.5.3），执行 `pip install -e . --force-reinstall`。

## 测试
```bash
pytest tests/                       # 全量
pytest tests/test_server.py        # Server 相关
pytest tests/test_storage.py       # 存储层
pytest --cov=mcp_memory_service tests/
python scripts/validation/verify_environment.py
python scripts/database/db_health_check.py
```

## 代码规范
- Python 3.10+、全量类型标注；
- I/O 必须 async/await；
- Black（88 列）+ isort；
- Docstring 采用 Google 风格；
- 仅捕获特定异常，日志为结构化输出。

## 目录结构
```
src/mcp_memory_service/
├── server.py          # MCP Server 入口
├── mcp_server.py      # MCP 工具实现
├── storage/           # 存储后端
├── embeddings/        # 嵌入模型
├── consolidation/     # 记忆归并算法
└── web/               # FastAPI & Dashboard
```

## 关键文件
- `server.py`：服务初始化；
- `storage/base.py`：后端抽象；
- `web/app.py`：HTTP/仪表盘；
- `pyproject.toml`：依赖与配置；
- `install.py`：跨平台安装脚本。

## 常见任务
- **新增存储后端**：实现 `BaseStorage`，注册到 `STORAGE_BACKENDS`，补 `tests/test_storage.py`；
- **修改 MCP 工具**：编辑 `mcp_server.py`，用 MCP Inspector 验证，更新 `docs/api/tools.md`；
- **新增环境变量**：`config.py` 定义，README/CLAUDE/Docker/验证脚本同步；
- **迁移脚本**：使用 `scripts/migration/*.py` 运行验证。

## 性能要点
- 嵌入缓存全局复用；
- 多记录操作使用 Batch；
- 后端连接池 + Async；
- 自动检测 CUDA/MPS/DirectML/ROCm。

## 安全实践
- 不提交密钥，使用环境变量；
- 所有输入需校验；
- SQLite 使用参数化查询；
- HTTP API 需 API Key / OAuth；
- File 操作防止路径穿越；
- 日志不输出完整记忆内容。

## 调试
```bash
export LOG_LEVEL=DEBUG
curl https://localhost:8443/api/health
tail -f ~/.mcp-memory-service/logs/service.log
npx @modelcontextprotocol/inspector uv run memory server
sqlite3 ~/.mcp-memory-service/sqlite_vec.db ".tables"
```

## 发布流程（简版）
1. 更新 `pyproject.toml` 版本；
2. 更新 `CHANGELOG.md`；
3. `pytest tests/`；
4. `git tag -a vX.Y.Z` 并 `git push origin vX.Y.Z`；
5. GitHub Actions 自动发布 PyPI / Docker。

## 常见问题
- macOS SQLite 扩展失败 → 使用 Homebrew Python 或 pyenv `--enable-loadable-sqlite-extensions`；
- 模型下载慢 → 检查网络（约 25MB）；
- ImportError → 运行 `python install.py`；
- MCP 连接失败 → 重启 Claude Desktop；
- 记忆未持久化 → 检查 `~/.mcp-memory-service/` 权限。

## 贡献
- 遵循现有代码风格；
- 新特性必须附测试；
- API 变更更新文档；
- 语义化 commit；
- 提 PR 前跑完测试。

> 本文件遵循 [agents.md](https://agents.md/) 的 AI Agent 指令规范。
