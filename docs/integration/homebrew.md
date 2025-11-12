# Homebrew PyTorch 集成指南

本指南介绍如何让 MCP Memory Service 使用 Homebrew 安装的 PyTorch，避免虚拟环境冲突并减轻安装负担。默认采用 SQLite-vec + ONNX Runtime（CPU 优化）。

## 核心组件
- **SQLite-vec**：轻量向量数据库；
- **ONNX Runtime**：CPU 推理；
- **子进程隔离**：防止 import 冲突；
- **自定义集成层**：连接 MCP 与 Homebrew 环境。

## 快速开始
```bash
brew install pytorch
python install.py --use-homebrew-pytorch --storage-backend sqlite_vec
./scripts/run_with_homebrew_pytorch.sh    # 运行服务
```
Claude Desktop 配置示例：
```json
{
  "mcpServers": {
    "memory": {
      "command": "/path/to/scripts/run_with_homebrew_pytorch.sh",
      "env": {
        "MCP_MEMORY_USE_HOMEBREW_PYTORCH": "true",
        "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec"
      }
    }
  }
}
```

## 详细步骤
1. **验证 Homebrew PyTorch**：`brew list | grep pytorch`；`python -c "import torch; print(torch.__version__)"`；
2. **安装服务**：创建 venv → `python install.py --use-homebrew-pytorch --skip-pytorch`；
3. **环境变量**：
```bash
export MCP_MEMORY_USE_HOMEBREW_PYTORCH=true
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
export MCP_MEMORY_USE_ONNX=true
export MCP_MEMORY_SQLITE_PATH="$HOME/.mcp_memory_sqlite/memory.db"
```
4. **测试**：`python scripts/verify_environment.py`、`python scripts/homebrew/homebrew_server.py --test`。

## 技术实现
- 通过子进程调用 Homebrew Python，隔离依赖；
- 运行时替换 Storage 选择逻辑；
- MCP handler 包装器确保协议输出；
- 自动探测 `/opt/homebrew/lib/python3.11/site-packages` 等路径的 PyTorch。

子进程示例：
```python
result = subprocess.run([sys.executable, '-c', script], capture_output=True, env=homebrew_env)
embeddings = json.loads(result.stdout)
```

## 诊断命令
```bash
python -c "import torch; print(torch.__version__)"
python scripts/homebrew/homebrew_server.py --health-check
env | grep MCP_MEMORY
sqlite3 ~/.mcp_memory_sqlite/memory.db ".schema"
```
常见问题：
- 导入冲突 → 重新创建 venv；
- 子进程超时 → 手动运行 `subprocess.run` 检查；
- DB 权限 → 确认 `.mcp_memory_sqlite/` 可写；
- MCP 协议异常 → `echo '{"jsonrpc":...}' | python scripts/homebrew/homebrew_server.py --stdin`。

## 环境变量
| 变量 | 说明 |
| --- | --- |
| `MCP_MEMORY_USE_HOMEBREW_PYTORCH` | 启用 Homebrew 集成 |
| `MCP_MEMORY_STORAGE_BACKEND` | 强制使用 SQLite-vec |
| `MCP_MEMORY_USE_ONNX` | ONNX 推理 |
| `MCP_MEMORY_SQLITE_PATH` | 数据库路径 |
| `MCP_MEMORY_HOMEBREW_PYTHON_PATH` | 自定义 Homebrew 路径 |
| `MCP_MEMORY_DEBUG` | 调试日志 |

## 性能
- 子进程按需加载模型，避免主进程泄漏；
- ONNX CPU 推理 + Batch 支持；
- SQLite-vec 低内存占用。

## 高级配置
```bash
export MCP_MEMORY_SENTENCE_TRANSFORMER_MODEL="all-MiniLM-L6-v2"
export MCP_MEMORY_ONNX_MODEL_PATH="/path/model.onnx"
python install.py --use-homebrew-pytorch --multi-client
```

## 开发与测试
```bash
pytest tests/homebrew/ -v
python tests/performance/test_homebrew_performance.py
```
扩展时：遵循子进程隔离、保持 MCP 协议兼容、补充文档与调试命令。

相关文档：安装指南、存储后端对比、排障、macOS Intel 安装等。
