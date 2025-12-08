# MCP Memory Service — 故障排查指南

列举本地或 CI 运行时常见问题及解决方案。

## 无法加载 sqlite-vec 扩展

**症状：**

- 报错提示 `SQLite extension loading not supported`、`enable_load_extension not available`；
- 日志出现 `Failed to load sqlite-vec extension`。

**原因：**

- 当前 Python 内置的 `sqlite3` 未开启可加载扩展（macOS 系统自带 Python 最常见）。

**解决方案：**

- macOS：
  - 使用 Homebrew Python：`brew install python`；
  - 或通过 pyenv 启用扩展：`PYTHON_CONFIGURE_OPTS='--enable-loadable-sqlite-extensions' pyenv install 3.12.x`。
- Linux：
  - 安装开发头文件：`apt install python3-dev sqlite3`；
  - 确保 Python 编译时启用 `--enable-loadable-sqlite-extensions`。
- Windows：
  - 优先使用 python.org 官方安装包或 conda 发行版。
- 备选方案：切换后端 `export MCP_MEMORY_STORAGE_BACKEND=chromadb`（详见迁移说明）。

## 缺少 `sentence-transformers` / `torch`

**症状：**

- 日志提示未找到嵌入模型，语义检索结果为空。

**解决方案：**

- 安装 ML 依赖：`pip install sentence-transformers torch`（或使用 `uv add`）；
- 对资源受限环境，可先安装依赖后再进行语义检索；若未安装，标签/元数据操作仍可使用。

## 首次运行模型下载

**症状：**

- 日志出现 `Using TRANSFORMERS_CACHE is deprecated`、`No snapshots directory` 等警告。

**状态说明：**

- 首次运行会下载 `all-MiniLM-L6-v2`（约 25MB），属于预期行为；后续运行将直接使用缓存。

## Cloudflare 后端启动失败

**症状：**

- 服务启动即退出并提示 `Missing required environment variables for Cloudflare backend`。

**解决方案：**

- 设置以下环境变量：`CLOUDFLARE_API_TOKEN`、`CLOUDFLARE_ACCOUNT_ID`、`CLOUDFLARE_VECTORIZE_INDEX`、`CLOUDFLARE_D1_DATABASE_ID`，可选 `CLOUDFLARE_R2_BUCKET`；
- 通过 Wrangler 或 Cloudflare 控制台核实资源配置，详见 `docs/cloudflare-setup.md`。

## 端口或协同冲突

**症状：**

- 多客户端模式无法启动 HTTP 协调服务，或退回到 direct 模式。

**说明 / 解决方案：**

- 服务器会自动检测并尝试：`http_client`（连接）、`http_server`（启动）或 `direct`（WAL）。如果协调端口被占用，会回退到 direct；可更换端口或停止占用服务。

## 路径权限或写入失败

**症状：**

- 在 `BASE_DIR` 或备份目录进行写入测试时失败。

**解决方案：**

- 确保 `MCP_MEMORY_BASE_DIR` 指向可写路径；服务会自动创建目录，并通过 `.write_test` 文件进行写入验证（带重试）。

## 查询缓慢或 CPU 占用高

**排查清单：**

- 确认嵌入模型已成功加载（首次调用后具备预热效果）；
- 低内存或 Windows + CUDA 场景可尝试：
  - `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128`
  - 调整模型缓存，参考 `server.py` 中的 `configure_environment()`；
- 通过 `MCP_MEMORY_SQLITE_PRAGMAS` 微调 SQLite 参数。
