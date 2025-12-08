# MCP Memory Service 开发指南

## 常用命令
- 启动 Memory Server：`python scripts/run_memory_server.py`
- 运行测试：`pytest tests/`
- 单测示例：`pytest tests/test_memory_ops.py::test_store_memory -v`
- 环境检测：`python scripts/verify_environment_enhanced.py`
- Windows 安装脚本：`python scripts/install_windows.py`
- 打包发布：`python -m build`

## 安装指引
- 始终使用虚拟环境：`python -m venv venv`
- 建议通过 `install.py` 跨平台安装；
- Windows 需手动安装匹配版本的 PyTorch：
  ```bash
  pip install torch==2.1.0 torchvision==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
  ```
- 遇到 recursion 错误时执行：`python scripts/fix_sitecustomize.py`

## 代码风格
- Python 3.10+，全面使用类型注解；
- 数据模型优先使用 dataclass（参考 `models/memory.py`）；
- 模块/函数 docstring 使用三引号；
- 所有 I/O 采用 async/await；
- 错误处理需抛出具体异常并附带信息；
- 根据严重程度设置日志级别；
- Commit 遵循 `type(scope): message` 语义化格式。

## 项目结构速览
- `src/mcp_memory_service/`
  - `models/`：数据模型
  - `storage/`：存储抽象与实现
  - `utils/`：工具方法
  - `server.py`：MCP 协议实现
- `scripts/`：辅助脚本
- `memory_wrapper.py`：Windows 启动包装器
- `install.py`：跨平台安装脚本

## 依赖
- ChromaDB 0.5.23（向量库）
- sentence-transformers ≥2.2.2（嵌入模型）
- PyTorch（根据平台单独安装）
- MCP protocol ≥1.0.0 ＜2.0.0

## 常见问题排查

### 一般性
- Windows 安装：优先运行 `scripts/install_windows.py`；
- Apple Silicon：务必使用 ARM64 的 Python 3.10+；
- CUDA：通过 `torch.cuda.is_available()` 检查；
- MCP 协议异常：确认 `server.py` 中必要方法已实现。

### MCP Server 配置

#### 缺少 `http_server_manager`
- **症状**：`No module named 'mcp_memory_service.utils.http_server_manager'`、Claude Code 显示 server failed；
- **诊断**：
  1. `python -m src.mcp_memory_service.server --debug`；
  2. 观察是否在存储初始化阶段报错；
  3. 检查 HTTP 协调模式检测逻辑。
- **修复**：补齐 `http_server_manager.py`，实现 `auto_start_http_server_if_needed()`、端口检测与 `port_detection.py` 集成。

#### 存储后端异常
- **症状**：`vec0 constructor error: Unknown table option`（sqlite-vec 过旧）等；
- **诊断**：分别测试 Chroma / SQLite-vec：
  ```bash
  python scripts/run_memory_server.py --debug
  MCP_MEMORY_STORAGE_BACKEND=sqlite_vec python -m src.mcp_memory_service.server --debug
  ```
  并通过 MCP 工具调用 `check_database_health`。
- **解决**：更新 sqlite-vec，确保两种后端均可独立运行；HTTP 协调失败时 SQLite-vec 会自动切换本地模式。

#### MCP 配置清理
1. 备份：`cp .mcp.json .mcp.json.backup`
2. 从 `.mcp.json` 移除异常服务，只保留可用项；
3. 分别测试各后端；
4. 通过 MCP 工具验证后再重新启用。

### 与 Claude Code 协同排障

建议以“开发者 + Claude Code”双视角协作：
1. 开发者描述症状；
2. Claude Code 执行系统化诊断（运行 MCP 工具、查看日志、检查配置与 git 记录）；
3. 共同制定 Todo：
   - 开发者：给出限制/目标；
   - Claude Code：拆分任务、创建清单、逐项验证；
4. 修复流程：备份→局部修改→回归测试→记录；
5. 将排障过程写入记忆，形成可复用知识。

**收益**：覆盖全面、知识可追溯、避免遗漏、团队共享。

## 使用 MCP-Inspector 调试

可借助 [MCP-Inspector](https://modelcontextprotocol.io/docs/tools/inspector) 定位问题：
```bash
MCP_MEMORY_CHROMA_PATH="/path/to/chroma_db" \
MCP_MEMORY_BACKUPS_PATH="/path/to/backups" \
npx @modelcontextprotocol/inspector uv --directory /path/to/mcp-memory-service run memory
```
