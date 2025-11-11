# MCP Memory Service

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub stars](https://img.shields.io/github/stars/doobidoo/mcp-memory-service?style=social)](https://github.com/doobidoo/mcp-memory-service/stargazers)
[![Production Ready](https://img.shields.io/badge/Production-Ready-brightgreen?style=flat&logo=checkmark)](https://github.com/doobidoo/mcp-memory-service#-in-production)

[![Works with Claude](https://img.shields.io/badge/Works%20with-Claude-blue)](https://claude.ai)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-orange)](https://cursor.sh)
[![MCP Protocol](https://img.shields.io/badge/MCP-Compatible-4CAF50?style=flat)](https://modelcontextprotocol.io/)
[![Multi-Client](https://img.shields.io/badge/Multi--Client-13+%20Apps-FF6B35?style=flat)](https://github.com/doobidoo/mcp-memory-service/wiki)

> 想阅读英文原版？请切换至 `main` 分支并参考原始文档。
>
> **中文翻译分支**：当前 `zh-CN` 分支提供简体中文内容，整体进度可查阅《[翻译进度追踪](docs/translation-progress.zh-cn.md)》。

**生产级的模型上下文协议记忆服务**，具备**零数据库锁**、**混合后端**（高速本地 + 云端同步）以及为 **AI 助手** 提供的**智能记忆检索**。内建 **v8.9.0 自动配置** 支持多客户端访问，后台 Cloudflare 同步让本地读取稳定在 **5ms**，并通过 **自然记忆触发器** 实现 85% 以上命中率，兼容 **OAuth 2.1 团队协作**。已在 **Claude Desktop、VS Code、Cursor、Continue 等 13+ AI 应用** 中验证。

<img width="240" alt="MCP Memory Service" src="https://github.com/user-attachments/assets/eab1f341-ca54-445c-905e-273cd9e89555" />

## 🚀 快速开始（约 2 分钟）

### 🆕 最新版本：**v8.23.1**（2025 年 11 月 10 日）

**陈旧虚拟环境防护体系** 🛡️🔧 —— 6 层流水线从开发、运行到 CI 全面阻断 “源代码已更新但虚拟环境仍旧” 的错位风险。

**本次新增**：
- 🛡️ **自动检测**：预提交钩子 + `scripts/validation/check_dev_setup.py` 会在虚拟环境落后时直接拒绝提交。
- ⚠️ **运行期告警**：`uv run memory server` 启动时比对源码与安装包版本，第一时间提示不一致。
- 📚 **开发指引**：CLAUDE.md、README 与 ai-agent 指南均要求使用 `pip install -e .` 可编辑安装。
- 🤖 **交互式引导**：`scripts/installation/install.py` 能识别 git 工作区，并自动提示改用可编辑安装模式。
- 🔄 **CI/CD 校验**：新增 `.github/workflows/dev-setup-validation.yml`，覆盖检测脚本、钩子、运行期告警及文档准确性五类检查。

**近期版本回顾**：
- **v8.23.0** —— 通过 Code Execution API 运行整合调度器，令记忆整合任务节省 88% 令牌。
- **v8.22.x** —— 全量修复标签校验与文档导入流程。
- **v8.21.0** —— Amp PR 自动化与记忆钩子稳定性改进。

**📖 详情**：参见 [CHANGELOG.md](CHANGELOG.md#8231---2025-11-10) ｜ [全部发行列表](https://github.com/doobidoo/mcp-memory-service/releases)

### 🔁 上一重点版本：**v8.16.0**（2025 年 11 月 1 日）

**数据库维护与类型整合** —— 面向生产环境的记忆数据库健康管理工具。

**本次更新亮点**：
- 🧹 **记忆类型整合工具**：将 300+ 分散的类型统一压缩为 24 个标准类型。
- 🛡️ **全景安全体系**：自动备份、锁检测、磁盘空间校验全覆盖。
- ⚡ **5 秒级性能**：可在数秒内整合 1,000+ 条记忆。
- 📊 **24 类分类法**：统一命名体系避免后续再次碎片化。
- 🔧 **可定制映射**：JSON 配置内置 168 条整合规则，可按需调整。
- 📚 **生产实战验证**：真实场景 1,049 条记忆，类型减少 63%，零数据丢失。

**Windows 专项增强（v8.15.0）**：
- ✨ **新增 `/session-start` 斜杠命令**：跨平台手动初始化会话。
- 🪟 **Windows 感知安装程序**：自动识别平台，预防配置错误。
- 📚 **强化文档**：补充完整的 Windows 故障排查与替代方案。
- 🛡️ **安全安装**：避免 Windows 上 SessionStart 钩子死锁（#160）。

**平台支持矩阵**：
- Windows：支持 `/session-start` 命令与 UserPromptSubmit 钩子 ✅
- macOS：包含自动 SessionStart 钩子在内的全部功能 ✅
- Linux：包含自动 SessionStart 钩子在内的全部功能 ✅

**数据库健康成效**：
- 调整前：342 个碎片化类型，609 条 NULL/空记录。
- 调整后：128 个规范类型，所有记忆均正确分类。
- 效果：查询效率显著提升，命名统一，语义分组更准确。

**📖 更多详情**：查看 [CHANGELOG.md](CHANGELOG.md#8160---2025-11-01)｜[维护指南](scripts/maintenance/README.md#consolidate_memory_typespy-new)｜[Issue #160](https://github.com/doobidoo/mcp-memory-service/issues/160)

---

```bash
# One-command installation with auto-configuration
git clone https://github.com/doobidoo/mcp-memory-service.git
cd mcp-memory-service && python install.py

# Choose option 4 (Hybrid - RECOMMENDED) when prompted
# Installer automatically configures:
#   ✅ SQLite pragmas for concurrent access
#   ✅ Cloudflare credentials for cloud sync
#   ✅ Claude Desktop integration

# Done! Fast local + cloud sync with zero database locks
```

### PyPI 安装（最简）

**通过 PyPI 安装：**

```bash
# Install latest version from PyPI
pip install mcp-memory-service

# Or with uv (faster)
uv pip install mcp-memory-service
```

**随后配置 Claude Desktop**，在 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）或其他平台的对应位置添加：

```json
{
	"mcpServers": {
		"memory": {
			"command": "memory",
			"args": ["server"],
			"env": {
				"MCP_MEMORY_STORAGE_BACKEND": "hybrid"
			}
		}
	}
}
```

若需使用交互式安装程序进行高级配置，请克隆仓库并运行 `python scripts/installation/install.py`。

### 传统部署选项

### 🛠️ 开发者环境（贡献指南）

在本地开发或贡献代码时，请按照以下流程搭建环境，确保源码改动能立即生效：

```bash
# 克隆仓库
git clone https://github.com/doobidoo/mcp-memory-service.git
cd mcp-memory-service

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate

# 关键：以可编辑模式安装，源码变更即时生效
pip install -e .

# 验证安装位置（应指向本地 src 目录而非 site-packages）
pip show mcp-memory-service | grep Location

# 启动开发服务器
uv run memory server
```

> ⚠️ **必须使用 `-e`**：否则 MCP 服务器会继续加载旧的 site-packages 版本，即使源码更新也不会生效。

**版本一致性校验：**

```bash
python scripts/validation/check_dev_setup.py
```

更多开发规范详见 [CLAUDE.md](CLAUDE.md#development-setup-critical)。

### 传统部署选项

**通用安装程序（兼容性最佳）：**

```bash
# Clone and install with automatic platform detection
git clone https://github.com/doobidoo/mcp-memory-service.git
cd mcp-memory-service

# Lightweight installation (SQLite-vec with ONNX embeddings - recommended)
python install.py

# Add full ML capabilities (torch + sentence-transformers for advanced features)
python install.py --with-ml

# Install with hybrid backend (SQLite-vec + Cloudflare sync)
python install.py --storage-backend hybrid
```

**📝 安装选项说明：**

- **默认（推荐）**：SQLite-vec + ONNX 嵌入向量，体积小、离线可用，依赖 <100MB。
- **`--with-ml`**：额外安装 PyTorch 与 sentence-transformers，适合高级 ML 场景。
- **`--storage-backend hybrid`**：启用混合后端，兼顾本地与多设备云同步。

**Docker（最快体验）：**

```bash
# For MCP protocol (Claude Desktop)
docker-compose up -d

# For HTTP API + OAuth (Team Collaboration)
docker-compose -f docker-compose.http.yml up -d
```

**Smithery（Claude Desktop 专用）：**

```bash
# Auto-install for Claude Desktop
npx -y @smithery/cli install @doobidoo/mcp-memory-service --client claude
```

## ⚠️ v6.17.0+ 脚本迁移提示

**从旧版本升级？** 新版将脚本目录重新整理以提升可维护性：

- **推荐方案**：在 Claude Desktop 配置中使用 `python -m mcp_memory_service.server`（无需硬编码路径）。
- **方案 1**：搭配 UV 工具执行 `uv run memory server`。
- **方案 2**：将脚本路径从 `scripts/run_memory_server.py` 调整为 `scripts/server/run_memory_server.py`。
- **向后兼容**：旧路径仍可使用，但会提示迁移信息。

## ⚠️ 首次运行预期行为

首次启动出现以下提示属于**正常现象**：

- **"WARNING: Failed to load from cache: No snapshots directory"** —— 服务在检查模型缓存（首次启动时尚未生成）。
- **"WARNING: Using TRANSFORMERS_CACHE is deprecated"** —— 信息提示，对功能无影响。
- **模型下载中** —— 服务会自动下载约 25MB 的嵌入向量模型，耗时约 1-2 分钟。

首次成功运行后，上述警告即会消失。详情请参考我们的[首次安装指南](docs/first-time-setup.md)。

### 🐍 Python 3.13 兼容性说明

**sqlite-vec** 在 Python 3.13 上可能尚无预编译轮子，安装失败时可：

- 依赖安装程序自动尝试多种回退方式；
- 或使用 `brew install python@3.12` 切换到 Python 3.12 以获得最佳体验；
- 选择 `--storage-backend cloudflare` 启用 Cloudflare 后端；
- 查看 [Troubleshooting Guide](docs/troubleshooting/general.md#python-313-sqlite-vec-issues) 获取详细排查步骤。

### 🍎 macOS SQLite Extension Support

**macOS 用户** 在使用 sqlite-vec 时可能遇到 `enable_load_extension` 错误：

- **系统自带 Python** 默认不支持加载 SQLite 扩展；
- **解决方案**：通过 Homebrew 安装 Python：`brew install python && rehash`；
- **可选方案**：使用 pyenv：`PYTHON_CONFIGURE_OPTS='--enable-loadable-sqlite-extensions' pyenv install 3.12.0`；
- **回退策略**：切换至 Cloudflare 或混合后端：`--storage-backend cloudflare` 或 `--storage-backend hybrid`；
- 详见 [Troubleshooting Guide](docs/troubleshooting/general.md#macos-sqlite-extension-issues) 获取说明。

## 🎯 记忆感知示例

**智能上下文注入** —— 自然记忆触发器会在会话开始时自动推送最相关的项目背景：

<img src="docs/assets/images/memory-awareness-hooks-example.png" alt="Memory Awareness Hooks in Action" width="100%" />

**画面解读：**
- 🧠 **自动记忆注入**：在 2,526 条记忆中筛选出 8 条最相关信息。
- 📂 **智能分栏**：按 “近期工作 / 当前问题 / 额外上下文” 分类展示。
- 📊 **Git 语义分析**：自动提取最近提交与关键词。
- 🎯 **相关性评分**：最高 100%（今日）、89%（8 天前）、84%（今日）。
- ⚡ **极速检索**：SQLite-vec 后端 5ms 读取延迟。
- 🔄 **后台同步**：混合后端持续与 Cloudflare 同步。

**效果**：Claude 每次会话都自动带入最新作业背景，无需手动补充提示。

## 📚 完整文档索引

**👉 访问我们内容丰富的 [Wiki](https://github.com/doobidoo/mcp-memory-service/wiki)，获取更细致的图文指南：**

### 🧠 v7.1.3 自然记忆触发器（最新版）

- **[Natural Memory Triggers v7.1.3 指南](https://github.com/doobidoo/mcp-memory-service/wiki/Natural-Memory-Triggers-v7.1.0)** —— 自动化记忆唤醒系统
  - ✅ **85%+ 触发准确率**，依托语义模式匹配。
  - ✅ **多档性能曲线**（50ms 即时 → 150ms 快速 → 500ms 深度）。
  - ✅ **CLI 管理面板**，实时调整灵敏度与性能档位。
  - ✅ **Git 感知上下文**，结合最近提交与关键词。
  - ✅ **零重启部署**，钩子可动态加载。

### 🆕 v7.0.0 OAuth 与团队协作

- **[🔐 OAuth 2.1 配置指南](https://github.com/doobidoo/mcp-memory-service/wiki/OAuth-2.1-Setup-Guide)** —— **全新** 的 OAuth 2.1 动态客户端注册流程
- **[🔗 集成指南](https://github.com/doobidoo/mcp-memory-service/wiki/03-Integration-Guide)** —— 覆盖 Claude Desktop、**Claude Code HTTP 传输**、VS Code 等平台
- **[🛡️ 高级配置](https://github.com/doobidoo/mcp-memory-service/wiki/04-Advanced-Configuration)** —— **已更新** 的 OAuth 安全与企业功能

### 🚀 安装与部署

- **[📋 安装指南](https://github.com/doobidoo/mcp-memory-service/wiki/01-Installation-Guide)** —— 涵盖所有平台与使用场景的完整步骤
- **[🖥️ 平台配置指南](https://github.com/doobidoo/mcp-memory-service/wiki/02-Platform-Setup-Guide)** —— Windows、macOS、Linux 优化方案
- **[⚡ 性能优化](https://github.com/doobidoo/mcp-memory-service/wiki/05-Performance-Optimization)** —— 查询提速、资源优化与扩展策略

### 🧠 高阶主题

- **[👨‍💻 开发者参考](https://github.com/doobidoo/mcp-memory-service/wiki/06-Development-Reference)** —— Claude Code 钩子、API 参考、调试技巧
- **[🔧 故障排查指南](https://github.com/doobidoo/mcp-memory-service/wiki/07-TROUBLESHOOTING)** —— **更新** 的 OAuth 故障处理与常见问题
- **[❓ FAQ](https://github.com/doobidoo/mcp-memory-service/wiki/08-FAQ)** —— 常见问题解答
- **[📝 示例库](https://github.com/doobidoo/mcp-memory-service/wiki/09-Examples)** —— 实用示例与工作流

### 📂 仓库内部文档

- **[📊 仓库统计](docs/statistics/REPOSITORY_STATISTICS.md)** —— 10 个月的研发指标与活动洞察
- **[🏗️ 架构规范](docs/architecture/)** —— 检索增强的设计与规范文档
- **[👩‍💻 开发文档](docs/development/)** —— AI Agent 指南、发布检查表、重构记录
- **[🚀 部署指南](docs/deployment/)** —— Docker、双服务与生产部署方案
- **[📚 其他指南](docs/guides/)** —— 存储后端、迁移流程、mDNS 发现

## ✨ 核心特性

### 🏆 **生产可用的可靠性** 🆕 v8.9.0

- **混合后端** —— 5ms 级本地 SQLite + 后台 Cloudflare 同步（推荐默认值）
  - 云端操作对用户零感知延迟
  - 自动完成多设备同步
  - 离线场景下优雅降级
- **零数据库锁** —— HTTP 与 MCP 服务并发访问稳定运行
  - 自动配置 SQLite pragma（`busy_timeout=15000,cache_size=20000`）
  - WAL 模式配合多客户端协调
  - 实测：5/5 并发写入全部成功，无错误
- **自动配置** —— 安装程序全程托管
  - 为并发访问优化 SQLite 设置
  - 校验 Cloudflare 凭据并测试连通性
  - 与混合后端的 Claude Desktop 集成
  - 云端初始化失败时自动回退至 sqlite_vec

### 📄 **文档入库系统** v8.6.0

- **交互式 Web UI** —— 支持拖拽上传并实时显示进度
- **多格式支持** —— PDF、TXT、MD、JSON，自动智能分块
- **文档浏览器** —— 查看分块、元数据与全文搜索
- **智能标签** —— 自动打标签并校验长度（最长 100 字符）
- **可选 semtools** —— 借助 LlamaParse 增强 PDF/DOCX/PPTX 解析
- **安全强化** —— 阻止路径遍历、防范 XSS、验证输入
- **新增 7 个端点** —— 完整的文档管理 REST API

### 🔐 **企业级认证与团队协作**

- **OAuth 2.1 动态客户端注册** —— 符合 RFC 7591 与 RFC 8414
- **Claude Code HTTP 传输** —— 零配置的团队协作入口
- **JWT 认证** —— 带范围校验的企业级安全方案
- **自动发现端点** —— 客户端注册与授权顺滑衔接
- **多重认证支持** —— 同时支持 OAuth、API Key 与可选匿名访问

### 🧠 **智能记忆管理**

- 通过嵌入向量实现**语义搜索**
- 支持**自然语言时间查询**（如“昨天”“上周”）
- **标签化归档** 配合智能分类
- **记忆整合** 采用梦境启发式算法
- **文档感知搜索** —— 同时查询上传文档与手工记忆

### 🔗 **全场景兼容性**

- **Claude Desktop** —— 原生 MCP 集成
- **Claude Code** —— **HTTP 传输** + 记忆感知型开发钩子
  - 🪟 **Windows 支持**：使用 `/session-start` 命令手动初始化会话（Issue #160 的解决方案）
  - 🍎 **macOS/Linux**：自动 SessionStart 钩子 + 斜杠命令齐备
- **VS Code、Cursor、Continue** —— IDE 扩展生态
- **13+ AI 应用** —— REST API 兼容接入

### 💾 **弹性存储选项**

- **混合模式** 🌟（推荐）—— 本地 SQLite + Cloudflare 后台同步（v8.9.0 默认）
  - 本地读取 5ms，用户无感延迟
  - 多设备实时同步
  - 自动配置 pragma，确保零锁
  - 自动备份与云端持久化
- **SQLite-vec** —— 本地存储（轻量 ONNX 嵌入向量，5ms 读取）
  - 适合单用户离线场景
  - 无需依赖云端
- **Cloudflare** —— 云端存储（基于 D1 + Vectorize 的全球边缘分发）
  - 性能取决于网络状况

> **提示**：为显著缩短构建时间与镜像体积，PyTorch、sentence-transformers 等大型 ML 依赖现为可选组件。默认的 SQLite-vec 会使用轻量 ONNX 嵌入向量；若需要完整 ML 能力，请在安装时加上 `--with-ml`。

### 🚀 **生产部署成熟度**

- **跨平台** —— 同时支持 Windows、macOS、Linux
- **服务安装** —— 后台自启动，方便守护进程运行
- **HTTPS/SSL** —— 配合 OAuth 2.1 提供安全传输
- **Docker 支持** —— 适合团队部署与快速落地
- **交互式控制台** —— 通过 http://127.0.0.1:8888/ 进行全栈管理

## 💡 基础用法

### 📄 **文档入库**（v8.6.0+）

```bash
# Start server with web interface
uv run memory server --http

# Access interactive dashboard
open http://127.0.0.1:8888/

# Upload documents via CLI
curl -X POST http://127.0.0.1:8888/api/documents/upload \
  -F "file=@document.pdf" \
  -F "tags=documentation,reference"

# Search document content
curl -X POST http://127.0.0.1:8888/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication flow", "limit": 10}'
```

### 🔗 **基于 OAuth 的团队协作**（v7.0.0+）

```bash
# Start OAuth-enabled server for team collaboration
export MCP_OAUTH_ENABLED=true
uv run memory server --http

# Claude Code team members connect via HTTP transport
claude mcp add --transport http memory-service http://your-server:8001/mcp
# → Automatic OAuth discovery, registration, and authentication
```

### 🧠 **记忆操作**

```bash
# Store a memory
uv run memory store "Fixed race condition in authentication by adding mutex locks"

# Search for relevant memories
uv run memory recall "authentication race condition"

# Search by tags
uv run memory search --tags python debugging

# Check system health (shows OAuth status)
uv run memory health
```

## 🔧 配置

### Claude Desktop 集成

**推荐方式** —— 在 Claude Desktop 配置文件（`~/.claude/config.json`）中添加：

```json
{
	"mcpServers": {
		"memory": {
			"command": "python",
			"args": ["-m", "mcp_memory_service.server"],
			"env": {
				"MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec"
			}
		}
	}
}
```

**其他可选方案：**

```json
// Option 1: UV tooling (if using UV)
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-service", "run", "memory", "server"],
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec"
      }
    }
  }
}

// Option 2: Direct script path (v6.17.0+)
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["/path/to/mcp-memory-service/scripts/server/run_memory_server.py"],
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "sqlite_vec"
      }
    }
  }
}
```

### 环境变量

**混合后端（v8.9.0+，推荐）：**

```bash
# Hybrid backend with auto-configured pragmas
export MCP_MEMORY_STORAGE_BACKEND=hybrid
export MCP_MEMORY_SQLITE_PRAGMAS="busy_timeout=15000,cache_size=20000"

# Cloudflare credentials (required for hybrid)
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ACCOUNT_ID="your-account"
export CLOUDFLARE_D1_DATABASE_ID="your-db-id"
export CLOUDFLARE_VECTORIZE_INDEX="mcp-memory-index"

# Enable HTTP API
export MCP_HTTP_ENABLED=true
export MCP_HTTP_PORT=8001

# Security
export MCP_API_KEY="your-secure-key"
```

**仅 SQLite-vec（本地模式）：**

```bash
# Local-only storage
export MCP_MEMORY_STORAGE_BACKEND=sqlite_vec
export MCP_MEMORY_SQLITE_PRAGMAS="busy_timeout=15000,cache_size=20000"
```

## 🏗️ 架构概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Clients    │    │  MCP Memory     │    │ Storage Backend │
│                 │    │  Service v8.9   │    │                 │
│ • Claude Desktop│◄──►│ • MCP Protocol  │◄──►│ • Hybrid 🌟     │
│ • Claude Code   │    │ • HTTP Transport│    │   (5ms local +  │
│   (HTTP/OAuth)  │    │ • OAuth 2.1 Auth│    │    cloud sync)  │
│ • VS Code       │    │ • Memory Store  │    │ • SQLite-vec    │
│ • Cursor        │    │ • Semantic      │    │ • Cloudflare    │
│ • 13+ AI Apps   │    │   Search        │    │                 │
│ • Web Dashboard │    │ • Doc Ingestion │    │ Zero DB Locks ✅│
│   (Port 8888)   │    │ • Zero DB Locks │    │ Auto-Config ✅  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ 开发

### 项目结构

```
mcp-memory-service/
├── src/mcp_memory_service/    # Core application
│   ├── models/                # Data models
│   ├── storage/               # Storage backends
│   ├── web/                   # HTTP API & dashboard
│   └── server.py              # MCP server
├── scripts/                   # Utilities & installation
├── tests/                     # Test suite
└── tools/docker/              # Docker configuration
```

### 参与贡献

1. Fork 仓库。
2. 创建特性分支。
3. 编写并通过测试后提交改动。
4. 发起 Pull Request。

详细规范请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 🆘 支持渠道

- **📖 文档中心**：访问 [Wiki](https://github.com/doobidoo/mcp-memory-service/wiki) 获取完整指南。
- **🐛 问题反馈**：通过 [GitHub Issues](https://github.com/doobidoo/mcp-memory-service/issues) 提交 Bug。
- **💬 社区讨论**：参与 [GitHub Discussions](https://github.com/doobidoo/mcp-memory-service/discussions)。
- **🔧 故障排查**：参考 [Troubleshooting Guide](https://github.com/doobidoo/mcp-memory-service/wiki/07-TROUBLESHOOTING)。
- **✅ 配置校验**：运行 `python scripts/validation/validate_configuration_complete.py` 检查本地设置。
- **🔄 后端同步工具**：查看 [scripts/README.md](scripts/README.md#backend-synchronization) 获取 Cloudflare ↔ SQLite 同步指引。

## 📊 生产环境实绩

**活跃部署环境的真实指标：**

- **1700+ 条记忆** 被团队持续使用。
- **5ms 本地读取**（混合后端，v8.9.0）。
- **零数据库锁**（HTTP + MCP 并发访问，v8.9.0）。
  - 实测：5/5 并发写入全部成功。
  - 自动配置的 pragma 有效避免锁冲突。
- **<500ms 语义搜索响应时间**（本地与 HTTP 传输）。
- **令牌消耗降低 65%**（结合 OAuth 协作的 Claude Code 会话）。
- **上下文准备提速 96.7%**（15 分钟 → 30 秒）。
- **知识留存率 100%**，跨会话与团队共享一致。
- **零配置成功率 98.5%**（OAuth + 混合后端）。

## 🏆 认可与推荐

- [![Smithery](https://smithery.ai/badge/@doobidoo/mcp-memory-service)](https://smithery.ai/server/@doobidoo/mcp-memory-service) **MCP 服务器验证通过**
- [![Glama AI](https://img.shields.io/badge/Featured-Glama%20AI-blue)](https://glama.ai/mcp/servers/bzvl3lz34o) **Glama AI 推荐工具**
- **在 13+ AI 应用中通过生产验证**
- **社区驱动**，不断吸收真实反馈迭代

## 📄 许可协议

Apache License 2.0 —— 详情参见 [LICENSE](LICENSE)。

---

**准备好强化你的 AI 工作流了吗？** 🚀

👉 **[从安装指南开始](https://github.com/doobidoo/mcp-memory-service/wiki/01-Installation-Guide)**，或浏览 **[Wiki](https://github.com/doobidoo/mcp-memory-service/wiki)** 获取完整文档。

_让你的 AI 对话转化为可持续增长、可检索的知识资产。_
