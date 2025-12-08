# 存储后端对比与选择指南

**MCP Memory Service** 目前支持两种存储后端，可针对不同硬件与场景进行优化配置。

## 快速对比

| 指标 | SQLite-vec 🪶 | ChromaDB 📦 |
| --- | --- | --- |
| **部署复杂度** | ⭐⭐⭐⭐⭐ 非常简易 | ⭐⭐⭐ 中等 |
| **启动时间** | ⭐⭐⭐⭐⭐ < 3 秒 | ⭐⭐ 15-30 秒 |
| **内存占用** | ⭐⭐⭐⭐⭐ < 150MB | ⭐⭐ 500-800MB |
| **性能表现** | ⭐⭐⭐⭐ 十分迅速 | ⭐⭐⭐⭐ 快速 |
| **功能完备度** | ⭐⭐⭐ 核心能力 | ⭐⭐⭐⭐⭐ 功能齐全 |
| **可扩展性** | ⭐⭐⭐⭐ 支持至 10 万条 | ⭐⭐⭐⭐⭐ 无上限 |
| **老旧硬件适配** | ⭐⭐⭐⭐⭐ 表现优秀 | ⭐ 一般 |
| **生产可用性** | ⭐⭐⭐⭐ 可用于生产 | ⭐⭐⭐⭐⭐ 成熟可靠 |

## 何时选择 SQLite-vec 🪶

### 适用场景

- **老旧硬件**：如 2015 款 MacBook Pro、较早的 Intel Mac；
- **资源受限**：内存 < 4GB 或 CPU 能力不足；
- **快速上手**：需要立即体验记忆能力；
- **单文件可移植**：便于备份或跨机器共享；
- **Docker/Serverless 部署**：镜像更轻量；
- **开发与测试**：快速迭代原型；
- **HTTP/SSE API**：新版 Web 控制台仅支持 SQLite-vec。

### 技术优势

- **冷启动极快**：2-3 秒即可就绪；
- **依赖最少**：仅需 SQLite + sqlite-vec 扩展；
- **低内存占用**：通常 < 150MB；
- **单文件数据库**：便于备份与迁移；
- **ACID 保障**：继承 SQLite 的可靠性；
- **零配置体验**：默认即可运行；
- **兼容 ONNX**：可在无 PyTorch 的环境运行。

### 示例场景

```bash
# 老旧 MacBook Pro
python install.py --legacy-hardware
# 结果：SQLite-vec + Homebrew PyTorch + ONNX

# Docker 部署
docker run -e MCP_MEMORY_STORAGE_BACKEND=sqlite_vec ...

# 快速开发环境
python install.py --storage-backend sqlite_vec --dev
```

## 何时选择 ChromaDB 📦

### 适用场景

- **现代硬件**：M1/M2/M3、更新的 Intel 平台；
- **GPU 加速**：支持 CUDA、MPS、DirectML；
- **大规模部署**：记忆量 > 1 万；
- **高级功能需求**：复杂过滤、元数据查询；
- **生产级使用**：稳定、生态完善；
- **研究/ML**：需要更先进的向量检索能力。

### 技术优势

- **高级向量检索**：支持多种距离度量与过滤；
- **丰富元数据**：可进行复杂查询；
- **大规模扩展**：可处理数百万向量；
- **生态完善**：广泛的工具与集成；
- **多样索引**：如 HNSW 等高性能索引结构；
- **多模态支持**：文本、图像等不同数据类型。

### 示例场景

```bash
# 支持 GPU 的现代 Mac
python install.py  # 安装程序会自动选择 ChromaDB

# 生产部署
python install.py --storage-backend chromadb --production

# 研究环境
python install.py --storage-backend chromadb --enable-advanced-features
```

## 硬件兼容矩阵

### macOS Intel（2013-2017）——遗留设备
```
推荐：SQLite-vec + Homebrew PyTorch + ONNX
备选：ChromaDB（可能安装失败）

配置示例：
- MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
- MCP_MEMORY_USE_ONNX=1
- MCP_MEMORY_USE_HOMEBREW_PYTORCH=1
```

### macOS Intel（2018+）——现代设备
```
推荐：ChromaDB（默认）或 SQLite-vec（轻量方案）

配置示例：
- MCP_MEMORY_STORAGE_BACKEND=chromadb
- 支持 CPU 或 MPS 加速
```

### macOS Apple Silicon（M1/M2/M3）
```
推荐：ChromaDB + MPS 加速
备选：SQLite-vec（资源占用更小）

配置示例：
- MCP_MEMORY_STORAGE_BACKEND=chromadb
- PYTORCH_ENABLE_MPS_FALLBACK=1
```

### Windows（含 CUDA GPU）
```
推荐：ChromaDB + CUDA 加速
备选：轻量化的 SQLite-vec
```

### Windows（仅 CPU）
```
推荐：SQLite-vec
备选：ChromaDB（资源要求更高）

可选配置：MCP_MEMORY_USE_ONNX=1
```

### Linux 服务器/无头环境
```
推荐：SQLite-vec（部署最简）
备选：ChromaDB（资源充足时）
```

## 性能对比

### 启动时间
```
SQLite-vec：2-3 秒     ████████████████████████████████
ChromaDB： 15-30 秒   ████████
```

### 空闲内存占用
```
SQLite-vec：约 150MB    ██████
ChromaDB： 约 600MB    ████████████████████████
```

### 1,000 条数据的搜索性能
```
SQLite-vec：50-200ms    ███████████████████████████
ChromaDB： 100-300ms   ██████████████████
```

### 存储效率
```
SQLite-vec：单一 .db 文件，体积约小 50%
ChromaDB：目录结构，完整元数据
```

## 功能对比

### 共同特性

- ✅ 语义记忆存储与检索；
- ✅ 标签管理；
- ✅ 自然语言时间检索；
- ✅ 全文搜索；
- ✅ 自动备份；
- ✅ 健康监控；
- ✅ 重复检测。

### SQLite-vec 专属

- ✅ 单文件可移植；
- ✅ 支持 HTTP/SSE API；
- ✅ 兼容 ONNX；
- ✅ 集成 Homebrew PyTorch；
- ✅ 启动极快；
- ✅ 占用资源极低。

### ChromaDB 专属

- ✅ 高级元数据过滤；
- ✅ 多种距离度量；
- ✅ 集合管理；
- ✅ 持久化客户端；
- ✅ 多样索引结构；
- ✅ 丰富的生态集成。

## 后端迁移

### ChromaDB → SQLite-vec

适用于老旧硬件升级或简化部署：

```bash
python scripts/migrate_chroma_to_sqlite.py
python install.py --migrate-from-chromadb --storage-backend sqlite_vec
```

**迁移将保留：**
- 记忆内容与嵌入；
- 标签与元数据；
- 时间戳与关联；
- 搜索能力。

### SQLite-vec → ChromaDB

当需要使用高级特性时：

```bash
python scripts/export_sqlite_memories.py
python scripts/import_to_chromadb.py
```

## 智能推荐逻辑

安装器会根据系统自动决策：

```python
def recommend_backend(system_info, hardware_info):
    if is_legacy_mac(system_info):
        return "sqlite_vec"
    if hardware_info.memory_gb < 4:
        return "sqlite_vec"
    if system_info.is_macos_intel_problematic:
        return "sqlite_vec"
    if hardware_info.has_gpu and hardware_info.memory_gb >= 8:
        return "chromadb"
    return "chromadb"
```

## 配置示例

### SQLite-vec

```bash
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
export MCP_MEMORY_SQLITE_PATH="$HOME/.mcp-memory/memory.db"
export MCP_MEMORY_USE_ONNX=1  # 可选
```

```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-service", "run", "memory"],
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec",
        "MCP_MEMORY_SQLITE_PATH": "/path/to/memory.db"
      }
    }
  }
}
```

### ChromaDB（本地，已弃用）

⚠️ 建议迁移至 SQLite-vec。
```bash
export MCP_MEMORY_STORAGE_BACKEND=chromadb
export MCP_MEMORY_CHROMA_PATH="$HOME/.mcp-memory/chroma_db"
```

### ChromaDB（远程/托管）

```bash
export MCP_MEMORY_STORAGE_BACKEND=chromadb
export MCP_MEMORY_CHROMADB_HOST="chroma.example.com"
export MCP_MEMORY_CHROMADB_PORT="8000"
export MCP_MEMORY_CHROMADB_SSL="true"
export MCP_MEMORY_CHROMADB_API_KEY="your-api-key-here"
export MCP_MEMORY_COLLECTION_NAME="my-collection"
```

```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-service", "run", "memory"],
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "chromadb",
        "MCP_MEMORY_CHROMADB_HOST": "chroma.example.com",
        "MCP_MEMORY_CHROMADB_PORT": "8000",
        "MCP_MEMORY_CHROMADB_SSL": "true",
        "MCP_MEMORY_CHROMADB_API_KEY": "your-api-key-here",
        "MCP_MEMORY_COLLECTION_NAME": "my-collection"
      }
    }
  }
}
```

**托管方案：**
- **Chroma Cloud**：官方托管服务（早期访问，可获 $5 免费额度）；
- **Elest.io**、AWS、Cloud Run、Docker 等可自建。

```bash
# Docker 自建示例
docker run -p 8001:8001 \
  -e CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER="chromadb.auth.token.TokenConfigServerAuthCredentialsProvider" \
  -e CHROMA_SERVER_AUTH_PROVIDER="chromadb.auth.token.TokenAuthServerProvider" \
  -e CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER="X_CHROMA_TOKEN" \
  -e CHROMA_SERVER_AUTH_CREDENTIALS="test-token" \
  -v /path/to/chroma-data:/chroma/chroma \
  chromadb/chroma
```

## 决策流程

```
Start
├─ 是否为遗留硬件？是 → SQLite-vec
├─ 内存 <4GB？是 → SQLite-vec
├─ 是否需要 HTTP/SSE API？是 → SQLite-vec
├─ 是否追求极简部署？是 → SQLite-vec
├─ 是否需要高级向量检索？是 → ChromaDB
├─ 是否具备现代 GPU 硬件？是 → ChromaDB
└─ 默认推荐 → ChromaDB
```

## 获取帮助

### 问题标签
- SQLite-vec 相关：`sqlite-vec`
- ChromaDB 相关：`chromadb`
- 迁移相关：`migration`

### 社区资源
- 后端对比讨论：GitHub Discussions；
- 性能基准：社区 Wiki；
- 硬件兼容：兼容性矩阵。

### 文档索引
- [SQLite-vec 后端指南](../sqlite-vec-backend.md)
- [迁移指南](migration.md)
- [老旧硬件指南](../platforms/macos-intel.md)
- [安装总览](../installation/master-guide.md)
