# Gemini Context：MCP Memory Service

## 项目概览
- MCP Memory Service 为 Claude Desktop 等 AI 助手提供语义记忆层；
- 核心 `MemoryServer` 处理 MCP 工具调用，并具备“梦境式”记忆归并系统；
- 基于 FastAPI/Async 架构，支持 ChromaDB 与 SQLite-vec 后端；
- 配套脚本覆盖安装、测试、维护。

## 安装与运行
```bash
git clone https://github.com/doobidoo/mcp-memory-service.git
cd mcp-memory-service
python -m venv venv && source venv/bin/activate
python install.py                # 智能安装器
python -m mcp_memory_service.server   # 或直接运行 memory 脚本/uvicorn
```

## 测试
```bash
pytest tests/
```

## 开发规范
- Python 3.10+、广泛使用类型标注；
- 所有 I/O 使用 async/await；
- 遵循 PEP 8，使用 dataclass 与完整 docstring；
- 新特性必须附带测试确保无回归。
