# Phase 2A: 安装包与依赖管理（摘要）

## 目标
- 降低初次安装失败率，统一依赖版本，支持 GPU/CPU 双路径。

## 安装路径
- 推荐：`uv sync`（锁定 `uv.lock`）。
- 备用：`python scripts/installation/install.py --storage-backend hybrid`。

## 关键依赖
- ONNX Runtime：
  - CPU: `pip install onnxruntime`
  - GPU: `pip install onnxruntime-gpu` 或 `onnxruntime-directml` (Win)
- 向量：`sqlite-vec`, `faiss-cpu` (可选)
- Web：`fastapi`, `uvicorn`, `sse-starlette`
- Cloudflare：`httpx`, `pydantic`, D1/Vectorize 客户端

## 平台注意
- macOS(MPS)：开启 `export MCP_QUALITY_LOCAL_DEVICE=mps`。
- Windows：避免 SessionStart 钩子全局匹配；DirectML 需最新驱动。
- Linux GPU：确保 CUDA 驱动与 onnxruntime-gpu 版本兼容。

## 常见错误与修复
- **onnxruntime 下载失败**：切换镜像或手动下载模型目录 `~/.cache/mcp_memory/onnx_models/`。
- **编译失败 (sqlite-vec)**：确保 `gcc`/`clang` 可用；或改用预编译 wheel。
- **Cloudflare 401/403**：检查 `CLOUDFLARE_API_TOKEN`、D1/Vectorize 权限。

## 验证命令
```bash
uv run memory server --check-config
pytest tests/unit/test_sqlite_vec_storage.py -q
pytest tests/integration/test_api_with_memory_service.py -q
```

## 交付物
- 更新 `install.py` 与文档，覆盖 GPU/CPU 分支与环境变量示例。
- 在 `CLAUDE.md` 补充安装 Troubleshooting（已完成）。
