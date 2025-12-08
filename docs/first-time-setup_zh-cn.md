# 首次运行指南

本文档说明首次启动 MCP Memory Service 时会发生什么，以及如何判断服务是否正常工作。

## 🎯 首次启动会看到什么

第一次启动服务时，终端会输出若干警告与提示。**这些都是初始化过程中的正常现象**，表示服务正在下载必需组件并完成配置。

## 📋 常见的首次启动警告

### 1. Snapshots 目录警告
```
WARNING:mcp_memory_service.storage.sqlite_vec:Failed to load from cache: No snapshots directory
```

**含义：**
- 服务会检查是否已有下载过的嵌入向量模型；
- 首次运行尚无缓存，因此会提示找不到目录；
- 随后服务会自动下载模型。

**是否正常：** ✅ 首次运行必然出现。

### 2. TRANSFORMERS_CACHE 警告
```
WARNING: Using TRANSFORMERS_CACHE is deprecated
```

**含义：**
- 来自 Hugging Face 库的信息性提示；
- 不影响服务功能；
- 服务内部会自行处理缓存。

**是否正常：** ✅ 可忽略。

### 3. 模型下载提示
```
Downloading model 'all-MiniLM-L6-v2'...
```

**含义：**
- 服务正在下载嵌入模型（约 25MB）；
- 仅首次运行需要下载；
- 在普通网络环境下约 1-2 分钟完成。

**是否正常：** ✅ 一次性操作。

## 🚦 成功启动的关键信息

若一切顺利，可看到类似日志：
```
INFO: SQLite-vec storage initialized successfully with embedding dimension: 384
INFO: Memory service started on port 8443
INFO: Ready to accept connections
```

## 📊 首次启动时间线

| 步骤 | 耗时 | 说明 |
| --- | --- | --- |
| 1. 启动服务 | 即时 | 加载配置 |
| 2. 检查缓存 | 1-2 秒 | 查找已下载模型 |
| 3. 下载模型 | 1-2 分钟 | 获取嵌入模型（约 25MB） |
| 4. 加载模型 | 5-10 秒 | 将模型载入内存 |
| 5. 初始化数据库 | 2-3 秒 | 创建数据库结构 |
| 6. 准备就绪 | - | 服务可正常使用 |

**首次启动总耗时约 2-3 分钟。**

## 🔄 后续启动

完成首次运行后：
- 不再出现下载相关警告；
- 模型从缓存加载，仅需 5-10 秒；
- 整体启动时间缩短至约 10-15 秒。

## 🐍 Python 3.13 兼容性

### 已知问题
使用 Python 3.13 时，**sqlite-vec** 可能因为缺乏预编译 wheel 而安装失败。安装脚本已内置多种回退策略：

1. **自动重试**：尝试多种安装方式；
2. **源码构建**：若无 wheel，则尝试从源码编译；
3. **GitHub 安装**：直接从仓库安装；
4. **后端切换**：必要时可切换至 ChromaDB 后端。

### 推荐解决方案
若你在 Python 3.13 上遇到 sqlite-vec 安装失败：

**方案 1：改用 Python 3.12（推荐）**
```bash
# macOS
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
python install.py

# Ubuntu/Linux
sudo apt install python3.12 python3.12-venv
python3.12 -m venv .venv
source .venv/bin/activate
python install.py
```

**方案 2：切换 ChromaDB 后端**
```bash
python install.py --storage-backend chromadb
```

**方案 3：手动安装 sqlite-vec**
```bash
# 从源码构建
pip install --no-binary :all: sqlite-vec

# 或直接从 GitHub 安装
pip install git+https://github.com/asg017/sqlite-vec.git#subdirectory=python
```

## 🍎 macOS SQLite 扩展问题

### 常见报错：`AttributeError: 'sqlite3.Connection' object has no attribute 'enable_load_extension'`

发生在 **使用系统自带 Python 的 macOS** 上，因为默认编译参数未开启 SQLite 扩展。

**原因：**
- macOS 系统自带 Python 未启用 `--enable-loadable-sqlite-extensions`；
- 随附的 SQLite 不允许加载扩展；
- 这是出于安全策略的默认配置。

**解决方案：**

**方案 1：Homebrew Python（推荐）**
```bash
brew install python
hash -r
python3 --version  # 确认已切换到 Homebrew Python
python3 install.py
```

**方案 2：使用 pyenv 并开启扩展**
```bash
brew install pyenv
PYTHON_CONFIGURE_OPTS="--enable-loadable-sqlite-extensions" pyenv install 3.12.0
pyenv local 3.12.0
python3 -c "import sqlite3; conn=sqlite3.connect(':memory:'); conn.enable_load_extension(True); print('Extensions supported!')"
```

**方案 3：改用 ChromaDB 后端**
```bash
python3 install.py --storage-backend chromadb
```

**扩展支持自检：**
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect(':memory:')
print('✅ Extension support available' if hasattr(conn, 'enable_load_extension') else '❌ No extension support')
"
```

## 🐧 Ubuntu/Linux 注意事项

### 依赖安装
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev python3-pip
sudo apt install build-essential libblas3 liblapack3 liblapack-dev libblas-dev gfortran
```

### 推荐流程
```bash
python3 -m venv venv
source venv/bin/activate
python install.py
uv run memory server
```

## 🔧 首次运行常见问题

### 问题：下载失败
**解决方案：**
- 检查网络连接；
- 确认防火墙/代理设置；
- 清理缓存后重试：`rm -rf ~/.cache/huggingface`。

### 问题：提示 `No module named 'sentence_transformers'`
**解决方案：**
```bash
pip install sentence-transformers torch
```

### 问题：权限不足
**解决方案：**
```bash
chmod +x scripts/*.sh
sudo chown -R $USER:$USER ~/.mcp_memory_service/
```

### 问题：下载完成后服务仍无法启动
**解决方案：**
1. 查看调试日志：`uv run memory server --debug`
2. 运行环境检查：`python scripts/verify_environment.py`
3. 清理后重启：
   ```bash
   rm -rf ~/.mcp_memory_service
   uv run memory server
   ```

## ✅ 验证服务是否可用

```bash
# 健康检查
curl -k https://localhost:8443/api/health

# CLI 方式
uv run memory health
```

期望响应：
```json
{
  "status": "healthy",
  "storage_backend": "sqlite_vec",
  "model_loaded": true
}
```

## 🎉 恭喜完成初始化！

当你看到成功日志且后续启动不再出现首次下载提示时，说明 MCP Memory Service 已就绪。

### 下一步：
- [配置 Claude Desktop](../README.md#claude-desktop-集成)
- [写入第一条记忆](../README.md#基础用法)
- [探索 API 与更深入的文档](https://github.com/doobidoo/mcp-memory-service/wiki)

## 📝 额外说明

- 模型下载仅需执行一次；
- 模型缓存位于 `~/.cache/huggingface/`；
- 服务数据库位于 `~/.mcp_memory_service/`；
- 首次启动出现的警告均为预期行为；
- 若出现其他错误（非警告），请查阅 [Troubleshooting Guide](troubleshooting/general.md)。

---

请牢记：**首次运行时的警告属于正常现象**，它们表明服务正在为高性能运行做好准备。祝使用顺利！
