# 脚本功能总览

本文汇总 `scripts/` 目录下常用脚本及其用途，便于快速查阅。

## 核心脚本

### 服务器管理
- `run_memory_server.py`：启动记忆服务主进程
  ```bash
  python scripts/run_memory_server.py
  ```

### 环境校验
- `verify_environment.py`：检查安装环境与依赖是否完整
  ```bash
  python scripts/verify_environment.py
  ```

### 安装验证
- `test_installation.py`：验证安装流程与基础功能
  ```bash
  python scripts/test_installation.py
  ```

### 记忆维护
- `validate_memories.py`：校验已存记忆的完整性
  ```bash
  python scripts/validate_memories.py
  ```
- `repair_memories.py`：修复损坏或不合法的记忆记录
  ```bash
  python scripts/repair_memories.py
  ```
- `list-collections.py`：列出全部记忆集合
  ```bash
  python scripts/list-collections.py
  ```

## 迁移相关
- `mcp-migration.py`：处理 MCP 相关数据迁移
  ```bash
  python scripts/mcp-migration.py
  ```
- `memory-migration.py`：处理记忆数据迁移
  ```bash
  python scripts/memory-migration.py
  ```

## 故障排查
- `verify_pytorch_windows.py`：在 Windows 环境检查 PyTorch 安装
  ```bash
  python scripts/verify_pytorch_windows.py
  ```
- `verify_torch.py`：通用的 PyTorch 校验脚本
  ```bash
  python scripts/verify_torch.py
  ```

## 使用注意事项
- 大部分脚本可直接通过 Python 运行；
- 部分脚本可能依赖特定的环境变量，使用前请先阅读脚本顶部注释；
- 建议在完成安装或重大升级后运行验证脚本；
- 迁移脚本需谨慎使用，确保事先做好数据备份。

## 依赖说明
- Python 3.10 及以上版本；
- `requirements.txt` 中列出的依赖包；
- 迁移相关脚本可能还需要 `requirements-migration.txt` 中的额外依赖。
