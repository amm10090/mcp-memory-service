# MCP Memory Service 故障排查指南

本文汇总常见问题及对应解决方案，便于在本地或 CI 环境使用 MCP Memory Service 时快速定位故障。

## 首次启动警告（正常现象）

### 常见提示

以下日志在首次运行时属于**正常行为**：

#### “No snapshots directory” 警告
```
WARNING:mcp_memory_service.storage.sqlite_vec:Failed to load from cache: No snapshots directory
```
- **状态**：✅ 正常——服务在检查模型缓存；
- **处理**：无需操作，模型会自动下载；
- **出现频次**：仅首次运行。

#### “TRANSFORMERS_CACHE deprecated” 警告
```
WARNING: Using TRANSFORMERS_CACHE is deprecated
```
- **状态**：✅ 正常——来自 Hugging Face 的信息提示；
- **处理**：无需操作，不影响功能；
- **出现频次**：可能每次运行都出现，可忽略。

#### 模型下载日志
```
Downloading model 'all-MiniLM-L6-v2'...
```
- **状态**：✅ 正常——首次运行需要下载约 25MB 模型；
- **处理**：等待 1-2 分钟；
- **出现频次**：首次运行。

更多信息见 [首次运行指南](../first-time-setup.md)。

## Python 3.13 + sqlite-vec 安装失败

**报错示例**：`Failed to install SQLite-vec: Command ... returned non-zero exit status 1`

**原因**：sqlite-vec 尚未提供 Python 3.13 的 wheel，且 PyPI 上暂时没有源码包。

**解决方案**：

1. **自动回退（v6.13.2+）**：安装脚本会尝试 uv pip、pip、源码构建、GitHub 安装；若全部失败，会提示切换 ChromaDB。
2. **推荐**：使用 Python 3.12。
3. **切换后端**：`python install.py --storage-backend chromadb`。
4. **手动尝试**：
   ```bash
   pip install --no-binary :all: sqlite-vec
   pip install git+https://github.com/asg017/sqlite-vec.git#subdirectory=python
   pip install pysqlite3-binary
   ```
5. **反馈问题**：关注 https://github.com/asg017/sqlite-vec/issues 获取最新进展。

## macOS 无法启用 sqlite 扩展

**报错**：`AttributeError: 'sqlite3.Connection' object has no attribute 'enable_load_extension'`

**原因**：macOS 系统自带 Python 未启用 `--enable-loadable-sqlite-extensions`。

**解决方案**：

1. **Homebrew Python（推荐）**：`brew install python`，并使用该版本重装服务；
2. **pyenv + 扩展支持**：使用 `PYTHON_CONFIGURE_OPTS='--enable-loadable-sqlite-extensions'` 安装；
3. **切换 ChromaDB 后端**：不需要 sqlite 扩展；
4. **检测命令**：参考指南中提供的 `python -c` 测试脚本判断扩展是否启用。

## 安装相关

若遇到路径权限、依赖缺失、安装脚本失败等问题，请参考主安装文档中的故障排查章节（内容与此处一致，为避免重复此处略）。

## MCP 协议问题

### “Method not found” 错误

- **症状**：Claude Desktop 日志出现 “Method not found” 或 JSON 错误弹窗；
- **原因**：服务器未实现必需 MCP 方法（如 resources/list 等）；
- **解决**：升级至最新版本或参考 `MCP_PROTOCOL_FIX.md` 补全接口实现。

## Windows 平台问题

- **JSON 编码/解码异常**、**路径权限问题** 等，请参见 `WINDOWS_JSON_FIX.md` 及相关章节。

## 性能优化

- 包括内存占用高、查询缓慢以及硬件加速配置，详见安装文档中“性能优化”章节。

## Debug 工具

- 推荐使用 `python scripts/validation/diagnose_backend_config.py` 获取环境诊断；
- 其他调试手段见安装文档“Debugging Tools”章节。

## 获取帮助

- 运行检测脚本：`python scripts/validation/diagnose_backend_config.py`；
- 查看 GitHub Issues；
- 查阅主仓库 README 与 `CLAUDE.md`；
- 若仍无法定位问题，建议在 Issue 中附带完整日志与配置信息。
