# CLAUDE.md

本文档为 Claude Code（claude.ai/code）在 MCP Memory Service 仓库中工作时提供操作指南与项目约定。

> **📝 个性化配置**：欢迎创建被 `.gitignore` 忽略的 `CLAUDE.local.md`，用于记录个人习惯、定制流程或特定环境说明。本主文件仅存放团队共享的规范。

> **提示**：完整项目上下文已存入记忆库，并以 `claude-code-reference` 标签归档。开发过程中可随时检索相关记忆以获得详细背景。

## 概览

MCP Memory Service 是一款模型上下文协议（Model Context Protocol，简称 MCP）服务器，为 Claude Desktop 提供语义记忆与持久化存储。系统支持 SQLite-vec、Cloudflare 以及混合后端模式。

> **🚨 v8.13.3**：**MCP 工具恢复** —— 修复 v8.12.0 回归导致的记忆操作中断，将 MemoryService 响应转换为规范的 MCP `TypedDict`。更新后请执行 `/mcp` 重新加载服务器。
>
> **🔄 v8.13.2**：**同步脚本恢复** —— 解决 `store_memory` API 迁移引发的后端同步失败，改用 `storage.store()` 正确创建 Memory 对象。
>
> **🔧 v8.13.1**：**并发访问修复** —— 零数据库锁回归；在打开数据库前设置连接超时，并跳过已初始化数据库的 DDL。
>
> **📊 v8.13.0**：**HTTP 集成测试** —— 32 个端到端测试覆盖启动验证、依赖注入、存储接口兼容性，防止生产回归。
>
> **🧠 v8.5.1**：**动态记忆权重调节** —— 根据记忆年龄与 git 活动自动调整权重，避免陈旧记忆主导上下文。
>
> **🆕 v8.4.0**：**记忆钩子时效优化** —— 最近 7 天的开发活动自动浮现，上下文准确率提升 80%。
>
> **🎉 v8.3.1**：**HTTP 服务管理** —— 跨平台自启脚本与健康检查，便于自然记忆触发器接入。
>
> **🧠 v7.1.0**：新增 **自然记忆触发器**，自动检索记忆，触发准确率超过 85%，支持多层性能优化。
>
> **🚀 v7.0.0**：支持 **OAuth 2.1 动态客户端注册** 与 **双协议记忆钩子**，可自动侦测 HTTP/MCP 协议。

## 常用命令

| Category | Command | Description |
|----------|---------|-------------|
| **Setup** | `python scripts/installation/install.py --storage-backend hybrid` | Install with hybrid backend (recommended) |
| | `uv run memory server` | Start server |
| | `pytest tests/` | Run tests |
| **Memory Ops** | `claude /memory-store "content"` | Store information |
| | `claude /memory-recall "query"` | Retrieve information |
| | `claude /memory-health` | Check service status |
| **Quality System** | `curl http://127.0.0.1:8000/api/quality/distribution` | Get quality analytics (v8.45.0+) |
| | `curl -X POST http://127.0.0.1:8000/api/quality/memories/{hash}/rate -d '{"rating":1}'` | Rate memory quality |
| | `curl http://127.0.0.1:8000/api/quality/memories/{hash}` | Get quality metrics |
| | `export MCP_QUALITY_BOOST_ENABLED=true` | Enable quality-boosted search |
| **Validation** | `python scripts/validation/validate_configuration_complete.py` | Comprehensive config validation |
| | `python scripts/validation/diagnose_backend_config.py` | Cloudflare diagnostics |
| **Maintenance** | `python scripts/maintenance/consolidate_memory_types.py --dry-run` | Preview type consolidation |
| | `python scripts/maintenance/find_all_duplicates.py` | Find duplicates |
| | `python scripts/sync/check_drift.py` | Check hybrid backend drift (v8.25.0+) |
| **Quality** | `bash scripts/pr/quality_gate.sh 123` | Run PR quality checks |
| | `bash scripts/pr/quality_gate.sh 123 --with-pyscn` | Comprehensive quality analysis (includes pyscn) |
| | `bash scripts/quality/track_pyscn_metrics.sh` | Track quality metrics over time |
| | `bash scripts/quality/weekly_quality_review.sh` | Generate weekly quality review |
| | `pyscn analyze .` | Run pyscn static analysis |
| **Consolidation** | `curl -X POST http://127.0.0.1:8000/api/consolidation/trigger -H "Content-Type: application/json" -d '{"time_horizon":"weekly"}'` | Trigger memory consolidation |
| | `curl http://127.0.0.1:8000/api/consolidation/status` | Check scheduler status |
| | `curl http://127.0.0.1:8000/api/consolidation/recommendations` | Get consolidation recommendations |
| **Backup** | `curl -X POST http://127.0.0.1:8000/api/backup/now` | Trigger manual backup (v8.29.0+) |
| | `curl http://127.0.0.1:8000/api/backup/status` | Check backup status and schedule |
| | `curl http://127.0.0.1:8000/api/backup/list` | List available backups |
| **Sync Controls** | `curl -X POST http://127.0.0.1:8000/api/sync/pause` | Pause hybrid backend sync (v8.29.0+) |
| | `curl -X POST http://127.0.0.1:8000/api/sync/resume` | Resume hybrid backend sync |
| **Service** | `systemctl --user status mcp-memory-http.service` | Check HTTP service status (Linux) |
| | `scripts/service/memory_service_manager.sh status` | Check service status |
| **Debug** | `curl http://127.0.0.1:8000/api/health` | Health check |
| | `npx @modelcontextprotocol/inspector uv run memory server` | MCP Inspector |

See [scripts/README.md](scripts/README.md) for complete command reference.

> 以上命令与注释保持英文原样，避免执行歧义。以下文本提供中文解读。

## 架构

**核心组成：**

- **服务器层**：`src/mcp_memory_service/server.py` 实现 MCP 协议，包含异步处理器与全局缓存。
- **存储后端**：SQLite-vec（本地 5ms 级读取）、Cloudflare（边缘分发）、Hybrid（SQLite + Cloudflare 同步）。
- **Web 界面**：基于 FastAPI 的控制台，HTTP 端口 `http://127.0.0.1:8001/`，HTTPS 端口 `https://localhost:8443/`，并提供 REST API。
- **文档入库**：可插拔加载器支持 PDF、DOCX、PPTX、文本，亦可选用 semtools 增强解析。
- **双协议记忆钩子** 🆕：提供 HTTP + MCP 自动侦测与切换。
  - **HTTP 模式**：通过 `https://localhost:8443/api/*` 访问 Web 服务。
  - **MCP 模式**：使用 `uv run memory server` 直接通信。
  - **智能检测**：MCP 优先 → HTTP 回退 → 根据环境自动选择。
  - **统一接口**：`MemoryClient` 封装协议切换，对上层透明。

## 文档入库（v7.6.0+）📄

增强型解析框架，结合 semtools 提升精度。

### 支持格式

| 格式 | 内置解析器 | Semtools | 质量 |
| --- | --- | --- | --- |
| PDF | PyPDF2/pdfplumber | ✅ LlamaParse | 优秀（含 OCR/表格） |
| DOCX | ❌ 不支持 | ✅ LlamaParse | 优秀 |
| PPTX | ❌ 不支持 | ✅ LlamaParse | 优秀 |
| TXT/MD | ✅ 内置 | N/A | 完美 |

### Semtools 集成（可选）

```bash
claude /memory-ingest document.pdf --tags documentation
claude /memory-ingest-dir ./docs --tags knowledge-base
```

See [docs/document-ingestion.md](docs/document-ingestion.md) for full configuration and usage.

## Interactive Dashboard

Web interface at `http://127.0.0.1:8000/` with CRUD operations, semantic/tag/time search, real-time updates (SSE), mobile responsive. Performance: 25ms page load, <100ms search.

**API Endpoints:** `/api/search`, `/api/search/by-tag`, `/api/search/by-time`, `/api/events`, `/api/quality/*` (v8.45.0+)

## Memory Quality System 🆕 (v8.45.0+)

**AI-driven automatic quality scoring** with local-first design for zero-cost, privacy-preserving memory evaluation.

### Architecture

**Tier 1 (Primary)**: Local SLM via ONNX
- Model: `ms-marco-MiniLM-L-6-v2` cross-encoder (23MB)
- Cost: **$0** (runs locally, CPU/GPU)
- Latency: 50-100ms (CPU), 10-20ms (GPU with CUDA/MPS/DirectML)
- Privacy: ✅ Full (no external API calls)
- Offline: ✅ Works without internet
- **⚠️ Requires meaningful query-memory pairs** (designed for relevance ranking, not absolute quality)

**Tier 2-3 (Optional)**: Groq/Gemini APIs (user opt-in only)
**Tier 4 (Fallback)**: Implicit signals (access patterns)

**⚠️ IMPORTANT ONNX Limitations (v8.48.3 Evaluation):**
- The ONNX ranker (`ms-marco-MiniLM-L-6-v2`) is a cross-encoder trained for document relevance ranking, NOT absolute quality assessment
- **Self-matching bias**: Tag-generated queries produce artificially high scores (~1.0) for ~25% of memories
- **Bimodal distribution**: Average score 0.469 (expected: 0.6-0.7) with clustering at 1.0 and 0.0
- **No ground truth**: Cannot validate if high scores represent actual quality without user feedback
- **Use for relative ranking only** - Do not use for absolute quality thresholds or archival decisions
- **Full evaluation**: [Memory Quality System Evaluation Wiki](https://github.com/doobidoo/mcp-memory-service/wiki/Memory-Quality-System-Evaluation)
- **Improvements planned**: [Issue #268](https://github.com/doobidoo/mcp-memory-service/issues/268) (Hybrid scoring, user feedback, LLM-as-judge)

### Key Features

1. **Automatic Quality Scoring**
   - Evaluates every retrieved memory (0.0-1.0 score)
   - Combines AI evaluation + usage patterns
   - Non-blocking (async background scoring)

2. **Quality-Boosted Search**
   - Reranks results: `0.7 × semantic + 0.3 × quality`
   - Over-fetches 3×, returns top N by composite score
   - Opt-in via `MCP_QUALITY_BOOST_ENABLED=true`

3. **Quality-Based Forgetting**
   - High quality (≥0.7): Preserved 365 days inactive
   - Medium (0.5-0.7): Preserved 180 days inactive
   - Low (<0.5): Archived 30-90 days inactive

4. **Dashboard Integration**
   - Quality badges on all memory cards (color-coded)
   - Analytics view with distribution charts
   - Top/bottom performers lists

### Configuration

```bash
# Quality System (Local-First Defaults)
export MCP_QUALITY_SYSTEM_ENABLED=true         # Default: enabled
export MCP_QUALITY_AI_PROVIDER=local           # local|groq|gemini|auto|none
export MCP_QUALITY_LOCAL_MODEL=ms-marco-MiniLM-L-6-v2
export MCP_QUALITY_LOCAL_DEVICE=auto           # auto|cpu|cuda|mps|directml

# Quality-Boosted Search (Opt-In)
export MCP_QUALITY_BOOST_ENABLED=false         # Default: disabled (opt-in)
export MCP_QUALITY_BOOST_WEIGHT=0.3            # 0.3 = 30% quality, 70% semantic

# Quality-Based Retention
export MCP_QUALITY_RETENTION_HIGH=365          # Days for quality ≥0.7
export MCP_QUALITY_RETENTION_MEDIUM=180        # Days for 0.5-0.7
export MCP_QUALITY_RETENTION_LOW_MIN=30        # Min days for <0.5
```

### MCP Tools

- `rate_memory(content_hash, rating, feedback)` - Manual quality rating (-1/0/1)
- `get_memory_quality(content_hash)` - Retrieve quality metrics
- `analyze_quality_distribution(min_quality, max_quality)` - System-wide analytics
- `retrieve_with_quality_boost(query, n_results, quality_weight)` - Quality-boosted search

### Success Metrics (Phase 1 Results - v8.48.3)

**Achieved:**
- ✅ **<100ms search latency** with quality boost (45ms avg, +17% overhead)
- ✅ **$0 monthly cost** (local SLM default, zero API calls)
- ✅ **75% local SLM usage** (3,570 of 4,762 memories)
- ✅ **95% quality score coverage** (4,521 of 4,762 memories scored)

**Challenges Identified:**
- ⚠️ Average quality score 0.469 (target: 0.6+)
- ⚠️ Self-matching bias affects ~25% of scores
- ⚠️ Quality boost provides minimal ranking improvement (0-3%)
- ⚠️ No user feedback validation

**Next Phase:** See [Issue #268](https://github.com/doobidoo/mcp-memory-service/issues/268) for improvements (hybrid scoring, user feedback, LLM-as-judge)

### Hooks Integration (v8.45.3+)

Quality scoring is now integrated with memory awareness hooks:

**Phase 1: Backend Quality in Hooks**
- `memory-scorer.js` reads `quality_score` from memory metadata
- Weight: 20% of hook scoring (reduces contentQuality/contentRelevance)
- Graceful fallback to 0.5 if quality_score not available

**Phase 2: Async Quality Evaluation**
- Session-end hook triggers `/api/quality/memories/{hash}/evaluate`
- Non-blocking: 10s timeout, doesn't delay session end
- ONNX ranker provides ~355ms evaluation time

**Phase 3: Quality-Boosted Retrieval**
```bash
# Search with quality boost
curl -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "...", "quality_boost": true, "quality_weight": 0.3}'
```

**Complete Flow:**
```
Session End → Store Memory → Trigger /evaluate (async)
                                    ↓
                            ONNX Ranker (355ms)
                                    ↓
                            Update metadata.quality_score
                                    ↓
Next Session → Hook Retrieval → backendQuality = 20% weight
```

### Documentation

**Updated for v8.48.3** - See [docs/guides/memory-quality-guide.md](docs/guides/memory-quality-guide.md) for:
- Comprehensive user guide
- Configuration examples
- Troubleshooting
- Best practices
- Performance benchmarks

## Memory Consolidation System 🆕

**Dream-inspired memory consolidation** with automatic scheduling and Code Execution API (v8.23.0+).

### Architecture

**Consolidation Scheduler Location**: HTTP Server (v8.23.0+)
- Runs 24/7 with HTTP server (independent of MCP server/Claude Desktop)
- Uses APScheduler for automatic scheduling
- Accessible via both HTTP API and MCP tools
- **Benefits**: Persistent, reliable, no dependency on Claude Desktop being open

**Code Execution API** (token-efficient operations):
```python
from mcp_memory_service.api import consolidate, scheduler_status

# Trigger consolidation (15 tokens vs 150 MCP tool - 90% reduction)
result = consolidate('weekly')

# Check scheduler (10 tokens vs 125 - 92% reduction)
status = scheduler_status()
```

### HTTP API Endpoints

| Endpoint | Method | Description | Response Time |
|----------|--------|-------------|---------------|
| `/api/consolidation/trigger` | POST | Trigger consolidation | ~10-30s |
| `/api/consolidation/status` | GET | Scheduler status | <5ms |
| `/api/consolidation/recommendations/{horizon}` | GET | Get recommendations | ~50ms |

**Example Usage:**
```bash
# Trigger weekly consolidation
curl -X POST http://127.0.0.1:8000/api/consolidation/trigger \
  -H "Content-Type: application/json" \
  -d '{"time_horizon": "weekly"}'

# Check scheduler status
curl http://127.0.0.1:8000/api/consolidation/status

# Get recommendations
curl http://127.0.0.1:8000/api/consolidation/recommendations/weekly
```

### 配置

```bash
# Enable consolidation (default: true)
export MCP_CONSOLIDATION_ENABLED=true

# Association-based quality boost (v8.47.0+)
export MCP_CONSOLIDATION_QUALITY_BOOST_ENABLED=true   # Enable boost (default: true)
export MCP_CONSOLIDATION_MIN_CONNECTIONS_FOR_BOOST=5  # Min connections (default: 5)
export MCP_CONSOLIDATION_QUALITY_BOOST_FACTOR=1.2     # Boost multiplier (default: 1.2 = 20%)

### 使用示例

```bash
# Ingest a single document
claude /memory-ingest document.pdf --tags documentation

# Ingest directory
claude /memory-ingest-dir ./docs --tags knowledge-base

# Via Python
from mcp_memory_service.ingestion import get_loader_for_file

loader = get_loader_for_file(Path("document.pdf"))
async for chunk in loader.extract_chunks(Path("document.pdf")):
    await store_memory(chunk.content, tags=["doc"])
```

### 主要特性

- ✅ 自动格式检测，择优选用加载器。
- ✅ 智能分块，遵循段落/句子边界。
- ✅ 元数据增强，保留文件信息、解析方式与页码。
- ✅ 优雅回退，缺少 semtools 时自动使用内置解析。
- ✅ 进度追踪，实时报告处理进度。

## 交互式控制面板（v7.2.2+）🎉

生产级 Web 控制台，性能经过全面验证。

### ✅ 核心功能

- **完整 CRUD**：界面化创建、读取、更新、删除记忆。
- **高级搜索**：支持语义检索、标签过滤、时间范围查询。
- **实时更新**：Server-Sent Events（SSE）心跳 30 秒一次。
- **移动兼容**：针对 768px 与 1024px 断点优化。
- **安全防护**：前端统一使用 `escapeHtml()` 抵御 XSS。
- **OAuth 集成**：根据启用状态动态加载模块。

### 📊 性能基准（v7.2.2 实测）

| 组件 | 目标 | 实测 | 状态 |
| --- | --- | --- | --- |
| 页面加载 | <2s | 25ms | ✅ 极佳 |
| 记忆操作 | <1s | 26ms | ✅ 极佳 |
| 标签检索 | <500ms | <100ms | ✅ 极佳 |
| 大数据集 | 1000+ | 已测 994+ | ✅ 极佳 |

### 🔍 搜索 API 端点

**No action required** - Consolidation automatically runs in HTTP server if enabled.

**For users without HTTP server:**
```bash
# Enable HTTP server in .env
export MCP_HTTP_ENABLED=true

# Restart service
systemctl --user restart mcp-memory-http.service
```

### 🎯 使用方式

- **面板入口**：HTTP 默认 `http://127.0.0.1:8001/`，启用 HTTPS 后 `https://localhost:8443/`。
- **API 基准路径**：`/api/`。
- **SSE 事件源**：`/api/events`。
- **端口复用**：HTTP/HTTPS API 与 MCP 协议使用同一端口（默认 8001）。
- **静态资源**：`src/mcp_memory_service/web/static/`（index.html、app.js、style.css）。

## 环境变量

**核心配置：**

```bash
# Storage Backend (Hybrid is RECOMMENDED for production)
export MCP_MEMORY_STORAGE_BACKEND=hybrid  # hybrid|cloudflare|sqlite_vec

# Cloudflare Configuration (REQUIRED for hybrid/cloudflare backends)
export CLOUDFLARE_API_TOKEN="your-token"      # Required for Cloudflare backend
export CLOUDFLARE_ACCOUNT_ID="your-account"   # Required for Cloudflare backend
export CLOUDFLARE_D1_DATABASE_ID="your-d1-id" # Required for Cloudflare backend
export CLOUDFLARE_VECTORIZE_INDEX="mcp-memory-index" # Required for Cloudflare backend

# Web Interface (Optional)
export MCP_HTTP_ENABLED=true                  # Enable HTTP server
export MCP_HTTPS_ENABLED=true                 # Enable HTTPS (production)
export MCP_API_KEY="$(openssl rand -base64 32)" # Generate secure API key
```

- **优先级**：环境变量 > `.env` > Claude 全局配置 > 默认值。
- **自动加载（v6.16.0+）**：服务会读取 `.env` 并遵循优先级，CLI 默认值不再覆盖环境设置。
- **注意事项**：使用 hybrid/cloudflare 后端时务必设置 Cloudflare 凭据；若健康检查显示 `sqlite-vec`，说明配置未生效。
- **平台支持**：macOS（MPS/CPU）、Windows（CUDA/DirectML/CPU）、Linux（CUDA/ROCm/CPU）。

## Claude Code 钩子配置 🆕

> **🚨 Windows 重要提示**：`matchers: ["*"]` 的 SessionStart 钩子会让 Claude Code 在 Windows 上无限挂起（Issue #160）。请禁用该钩子或改用 UserPromptSubmit，详见后文。

### 自然记忆触发器 v7.1.0

智能语义检索与多档性能调节：

```bash
# Installation (Zero-restart required)
cd claude-hooks && python install_hooks.py --natural-triggers

# CLI Management
node ~/.claude/hooks/memory-mode-controller.js status
node ~/.claude/hooks/memory-mode-controller.js profile balanced
node ~/.claude/hooks/memory-mode-controller.js sensitivity 0.7
node ~/.claude/hooks/test-natural-triggers.js
```

**主要能力：**

- ✅ 触发准确率超过 85%。
- ✅ 三层处理：50ms 即时 → 150ms 快速 → 500ms 深度。
- ✅ CLI 管理支持实时热调。
- ✅ Git 感知增强上下文相关性。
- ✅ 根据使用偏好自适应调整。

**配置文件（`~/.claude/hooks/config.json`）：**

```json
{
  "naturalTriggers": {
    "enabled": true,
    "triggerThreshold": 0.6,
    "cooldownPeriod": 30000,
    "maxMemoriesPerTrigger": 5
  },
  "performance": {
    "defaultProfile": "balanced",
    "enableMonitoring": true,
    "autoAdjust": true
  }
}
```

**性能档位：**

- `speed_focused`：<100ms，仅即时层，追求极致速度。
- `balanced`：<200ms，即时 + 快速层，推荐默认。
- `memory_aware`：<500ms，全层开启，适合复杂任务。
- `adaptive`：依据使用模式与反馈自动调节。

### 上下文提供器集成 🆕

规则驱动的上下文管理体系，与自然触发器互补：

```bash
# Context-Provider Commands
mcp context list                                # List available contexts
mcp context status                             # Check session initialization status
mcp context optimize                           # Get optimization suggestions
```

#### 可用上下文

**1. Python MCP Memory Service 上下文（`python_mcp_memory`）**

- 聚焦 FastAPI、MCP 协议、存储后端模式。
- 自动存储：协议调整、后端配置、性能优化等关键事件。
- 自动检索：排障、搭建、实现范例。
- 智能标签：自动识别 fastapi、cloudflare、sqlite-vec、hybrid 等术语。

**2. Release Workflow 上下文 🆕（`mcp_memory_release_workflow`）**

- **PR 评审循环**：Gemini Code Assist 工作流（修复 → 评论 → `/gemini review` → 等待 → 重复）。
- **版本管理**：同步更新 `__init__.py`、`pyproject.toml`、`uv.lock`。
- **CHANGELOG 流程**：格式规范、冲突合并指南。
- **文档矩阵**：明确何时更新 CHANGELOG、Wiki、CLAUDE.md 及代码注释。
- **发布流程**：合并 → 打标签 → 推送 → 校验（Docker Publish、Publish and Test、HTTP-MCP Bridge）。
- **Issue 管理** 🆕：自动跟踪 `fixes #`、`closes #`、`resolves #`，并生成上下文完整的关闭评论与分类。

**自动存储模式**：

- **技术**：`MCP protocol`、`tool handler`、`storage backend switch`、`25ms page load`、`embedding cache`。
- **配置**：`cloudflare configuration`、`hybrid backend setup`、`oauth integration`。
- **发布** 🆕：`merged PR`、`gemini review`、`created tag`、`CHANGELOG conflict`、`version bump`。
- **文档** 🆕：`updated CHANGELOG`、`wiki page created`、`CLAUDE.md updated`。
- **Issue** 🆕：`fixes #`、`closed issue #` 等模式自动识别。

**自动检索模式**：

- **排障**：`cloudflare backend error`、`MCP client connection`、`storage backend failed`。
- **配置**：`backend configuration`、`environment setup`、`claude desktop config`。
- **开发**：`MCP handler example`、`API endpoint pattern`、`async error handling`。
- **发布** 🆕：`how to release`、`PR workflow`、`version bump procedure`、`where to document`。
- **Issue 管理** 🆕：`review open issues`、`issue status`、`which issues resolved`。

**文档决策矩阵：**

| 变更类型 | CHANGELOG | CLAUDE.md | Wiki | 代码注释 |
| --- | --- | --- | --- | --- |
| Bug 修复 | ✅ 必写 | 影响工作流时 | 复杂或需长期引用 | ✅ 解释非显然逻辑 |
| 新功能 | ✅ 必写 | 新增命令/流程 | ✅ 重大功能 | ✅ API 变化 |
| 性能优化 | ✅ 必写 | 需说明指标 | >20% 提升时 | 说明原因 |
| 配置变更 | ✅ 必写 | ✅ 用户可见 | 涉及迁移时 | 校验逻辑 |
| 故障排查 | 视情况 | 常见问题时 | ✅ 详细步骤 | 供维护查看 |

**集成收益：**

- 结构化规则与 AI 触发协同管理记忆。
- 捕捉项目专属术语与协作流程。
- 规范提交信息、分支命名与迭代节奏。
- 发布流程自动化，避免遗忘版本号或 CHANGELOG。
- 积累 PR 评审经验与问题记录。
- Issue 自动回收并生成上下文完整的关闭说明。
- 轻量级规则执行，对性能影响极小。

### 双协议记忆钩子（传统）

```json
{
	"memoryService": {
		"protocol": "auto",
		"preferredProtocol": "mcp",
		"fallbackEnabled": true,
		"http": {
			"endpoint": "https://localhost:8443",
			"apiKey": "your-api-key",
			"healthCheckTimeout": 3000,
			"useDetailedHealthCheck": true
		},
		"mcp": {
			"serverCommand": ["uv", "run", "memory", "server", "-s", "cloudflare"],
			"serverWorkingDir": "/Users/yourname/path/to/mcp-memory-service",
			"connectionTimeout": 5000,
			"toolCallTimeout": 10000
		}
	}
}
```

**协议选项：**

- `"auto"`：优先 MCP，其次 HTTP，再根据环境回退。
- `"http"`：仅使用 HTTP（`https://localhost:8443`）。
- `"mcp"`：仅使用 MCP 进程直连。

**优势：**可靠性提升、性能可调、灵活适配本地或远程部署，并兼容旧版配置。

## 存储后端

| 后端 | 性能 | 适用场景 | 安装方式 |
| --- | --- | --- | --- |
| **Hybrid** ⚡ | **5ms 读取** | **🌟 生产推荐** | `install.py --storage-backend hybrid` |
| **Cloudflare** ☁️ | 取决于网络 | 纯云端部署 | `install.py --storage-backend cloudflare` |
| **SQLite-Vec** 🪶 | 5ms 读取 | 本地单用户/开发环境 | `install.py --storage-backend sqlite_vec` |

### ⚠️ 数据库锁防护（v8.9.0+）

为 `.env` 添加 `MCP_MEMORY_SQLITE_PRAGMAS` 后，**必须重启所有服务**：

- HTTP 服务器：`kill <PID>` 后使用 `uv run python scripts/server/run_http_server.py` 重启。
- MCP 服务器：在 Claude Code 中运行 `/mcp` 重新连接，或重启 Claude Desktop。
- 验证方法：日志中应出现 `Custom pragma from env: busy_timeout=15000`。

SQLite pragma **针对连接生效**，不会全局持久化。长时间运行的服务若未重启不会读取新配置。

**缺少 pragma 的症状**：

- 仍出现 “database is locked”。
- `PRAGMA busy_timeout` 返回 `0` 而非 `15000`。
- HTTP 与 MCP 并发访问失败。

### 🚀 混合后端（v6.21.0+ 推荐）

```bash
# Enable hybrid backend
export MCP_MEMORY_STORAGE_BACKEND=hybrid

# Hybrid-specific configuration
export MCP_HYBRID_SYNC_INTERVAL=300    # Background sync every 5 minutes
export MCP_HYBRID_BATCH_SIZE=50        # Sync 50 operations at a time
export MCP_HYBRID_SYNC_ON_STARTUP=true # Initial sync on startup

# Drift detection configuration (v8.25.0+)
export MCP_HYBRID_SYNC_UPDATES=true              # Enable metadata sync (default: true)
export MCP_HYBRID_DRIFT_CHECK_INTERVAL=3600      # Seconds between drift checks (default: 1 hour)
export MCP_HYBRID_DRIFT_BATCH_SIZE=100           # Memories to check per scan (default: 100)

# Requires Cloudflare credentials (same as cloudflare backend)
export CLOUDFLARE_API_TOKEN="your-token"
export CLOUDFLARE_ACCOUNT_ID="your-account"
export CLOUDFLARE_D1_DATABASE_ID="your-d1-id"
export CLOUDFLARE_VECTORIZE_INDEX="mcp-memory-index"
```

**优势**：

- ✅ SQLite-vec 速度，读写约 5ms。
- ✅ 后台同步，用户无感延迟。
- ✅ 多设备共享，同步自动完成。
- ✅ 离线时优雅降级，恢复后自动同步。
- ✅ Cloudflare 不可用时自动退回 SQLite。

**架构概览**：

- 主存储：SQLite-vec 处理全部实时请求。
- 次存储：Cloudflare 负责后台同步与持久化。
- 后台服务：异步队列 + 重试逻辑 + 健康监控。

**安装程序（v6.16.0+）增强**：交互式后端选择、自动生成 `.env` 与凭据校验、安装期即验证连接、出错时优雅回退本地模式。

## 开发指南

### 🧠 记忆与文档

- 使用 `claude /memory-store` 记录决策，系统会自动处理重复（基于内容哈希）。
- 时间解析支持自然语言（例如 “yesterday”“last week”）。
- 提交信息建议使用语义化格式，方便版本管理。

#### 记忆类型分类（2025 年 11 月更新）

数据库已由 342 个碎片类型整合为 128 个规范类型，请使用以下 24 个核心类型：

**内容类**：
- `note` —— 一般备注、总结。
- `reference` —— 参考资料、知识库条目。
- `document` —— 正式文档、代码片段。
- `guide` —— 指南、教程、故障排查步骤。

**活动类**：
- `session` —— 工作/开发会话。
- `implementation` —— 实现、集成任务。
- `analysis` —— 分析、调查、报告。
- `troubleshooting` —— 调试与修复。
- `test` —— 测试与验证。

**成果类**：
- `fix` —— 缺陷修复。
- `feature` —— 新功能或增强。
- `release` —— 版本发布与说明。
- `deployment` —— 部署记录。

**进度类**：
- `milestone` —— 里程碑、阶段成果。
- `status` —— 状态更新。
- `todo` —— 待办事项。
- `decision` —— 决策结论。

**支持类**：
- `workflow` —— 流程与最佳实践。
- `config` —— 配置说明。
- `hook` —— 钩子或自动化。
- `issue` —— 问题追踪与处理。
- `insight` —— 经验或洞察。
- `performance` —— 性能优化记录。
- `security` —— 安全事项。

### 🏗️ 架构与测试

- 重要改动需覆盖单元测试与集成测试，尤其是存储接口与网络层。
- 运行 `pytest` 并关注并发访问相关测试。
- 通过 `uv run memory server --http` 验证 HTTP 服务器启动与健康检查。
- 对变更后的 hooks、CLI 命令执行端到端测试。

### 🚀 版本管理最佳实践

- 版本号需同步更新 `src/mcp_memory_service/__init__.py`、`pyproject.toml`、`uv.lock`。
- CHANGELOG 条目需包含日期、版本号、类别（Added/Fixed/etc）。
- 发布前确认：Docker Publish、Publish and Test、HTTP-MCP Bridge 三个工作流均通过。
- 使用 `git tag` 创建版本标签，并推送远程。

### 🔧 配置与部署

- 使用 `python scripts/validation/verify_environment.py` 校验环境。
- Hybrid/Cloudflare 模式需配置环境变量并运行 `python scripts/validation/diagnose_backend_config.py`。
- Linux 建议使用 systemd 管理 HTTP 服务（`scripts/service/install_http_service.sh`）。
- Windows 可用 `start_http_server.bat` 或 `start_http_debug.bat` 调试。

## 关键端点

### 🌐 Web 界面

- 健康检查：`GET /api/health`
- 仪表板：`GET /`
- SSE 流：`GET /api/events`

### 📋 记忆管理

- 创建记忆：`POST /api/memories`
- 获取详情：`GET /api/memories/{id}`
- 更新记忆：`PUT /api/memories/{id}`
- 删除记忆：`DELETE /api/memories/{id}`

### 🔍 搜索 API

- 语义搜索：`POST /api/search`
- 标签搜索：`POST /api/search/by-tag`
- 时间搜索：`POST /api/search/by-time`

### 📚 文档相关

- 入库任务：`POST /api/documents`
- 入库状态：`GET /api/documents/{id}`
- 文档列表：`GET /api/documents`

## 配置管理

```bash
# Proactive usage - invokes automatically on feature completion
# Manual usage - invoke @agent when ready to release
@agent github-release-manager "Check if we need a release"
@agent github-release-manager "Create release for v8.20.0"
```

**单一可信配置源：**

- **全局配置**：`~/.claude.json`（所有项目共享的权威来源）。
- **项目环境**：`.env`（通常只存放 Cloudflare 凭据）。
- **禁止本地覆盖**：项目根目录下的 `.mcp.json` 不应写入记忆服务器配置。

**常见配置问题（v6.16.0 之前）：**

- ✅ 已修复：CLI 默认值覆盖环境变量。
- ✅ 已修复：需手动加载 `.env`。
- ⚠️ 多后端冲突：SQLite/Cloudflare 配置混搭。
- ⚠️ 凭据冲突：旧路径或缺失 Cloudflare 信息。
- ⚠️ 缓存问题：需重启 Claude Code 以刷新 MCP 连接。

**v6.16.0+ 配置优势：**自动加载 `.env`、严格遵循优先级、并提供更清晰的错误信息。

**Cloudflare 后端排障：**

- 查看 Claude Desktop 日志中的关键标记：
  - 🚀 SERVER INIT —— 服务器主初始化流程。
  - ☁️ Cloudflare 专属初始化步骤。
  - ✅ 每个阶段的成功标记。
  - ❌ 具体错误堆栈。
  - 🔍 存储类型校验，用于确认最终后端。
- 常见现象：
  - 静默回退到 SQLite-vec：通常因初始化超时或 API 错误，应检查日志。
  - 配置校验：启动阶段会打印环境变量。
  - 网络超时：增强的错误信息会指出具体 Cloudflare API 失败点。

**双环境设置（Claude Desktop + Claude Code）：**

```bash
# 快速检查组合环境，详见 docs/quick-setup-cloudflare-dual-environment.md
python scripts/validation/diagnose_backend_config.py  # Validate Cloudflare configuration
claude mcp list                             # Check Claude Code MCP servers
```

**健康检查显示错误后端时：**

```bash
# 若期望 cloudflare/hybrid 却显示 sqlite-vec
python scripts/validation/diagnose_backend_config.py
claude mcp remove memory && claude mcp add memory \
  python -e MCP_MEMORY_STORAGE_BACKEND=cloudflare \
         -e CLOUDFLARE_API_TOKEN=your-token -- -m mcp_memory_service.server
```

**Hook 未能检索记忆时：**

```bash
# 检查 HTTP 服务是否运行
systemctl --user status mcp-memory-http.service  # Linux
# 或
uv run python scripts/server/check_http_server.py

# 确认 hooks 配置的端口
cat ~/.claude/hooks/config.json | grep endpoint
# 预期返回 http://127.0.0.1:8001（避免使用 8889 等端口）
```

### ⚠️ Hook 配置同步

所有配置文件中的 HTTP 端点必须一致：

1. `~/.claude/hooks/config.json`（默认端口 8001）。
2. `scripts/server/run_http_server.py` 中的 HTTP 服务器端口。
3. 仪表板端口：HTTP 8001，HTTPS 8443。

**常见错误：**

- 端口不一致（配置文件写 8889，服务实际使用 8001）。
- 将仪表板端口（8001/8443）误用为 API 端口。
- `settings.json` 与 hooks 配置端口不同。

**快速核查：**

```bash
# Windows
netstat -ano | findstr "8001"

# Linux/macOS
lsof -i :8001

grep endpoint ~/.claude/hooks/config.json
```

若端口不匹配，将导致 SessionStart 挂起、启动无响应或日志出现连接超时。

### PR 合并后仍出现模式校验错误

**现象**：合并更改工具 Schema 的 PR 后仍出现 `Input validation error`。

**根因**：MCP 客户端会缓存工具 Schema；若 MCP 服务器未重启，仍会发布旧 Schema。

**排查步骤：**

```bash
# 1. 查看 PR 合并时间
gh pr view <PR_NUMBER> --json mergedAt,title

# 2. 查看服务器进程启动时间
ps aux | grep "memory.*server" | grep -v grep

# 3. 若进程早于合并时间，说明仍运行旧代码
```

**解决方案：**

```bash
/mcp  # 在 Claude Code 中重连 MCP
# 会终止旧进程、启动最新代码、重新获取 Schema 并清理缓存

# HTTP 服务需单独重启：
systemctl --user restart mcp-memory-http.service
```

**案例**：PR #162 解决逗号分隔标签问题，但旧服务器仍缓存旧 Schema，需 `/mcp` 重连。

更多细节参见 `docs/troubleshooting/pr162-schema-caching-issue.md`。

### 紧急排障工具

```bash
/mcp                                         # 查看当前连接的 MCP 服务器
python scripts/validation/diagnose_backend_config.py  # 环境自检
rm -f .mcp.json                             # 移除冲突的本地配置
python debug_server_initialization.py       # 测试初始化流程（v6.15.1+）
tail -50 ~/Library/Logs/Claude/mcp-server-memory.log | \
  grep -E "(🚀|☁️|✅|❌)"  # 解析增强日志
```

### ⚠️ 意外生成数据库

若发现项目目录下出现 `data/memory.db`：

- 并非配置中的数据库位置（可能是外部工具创建）。
- 可安全删除：`rm -rf data/`（该目录已忽略）。
- 正确位置：macOS 默认 `~/Library/Application Support/mcp-memory/sqlite_vec.db`。
- 可通过 `curl http://localhost:8001/api/health` 验证实际使用的后端与记录数。

### SessionEnd 钩子故障排查

**常见误解**：按下 Ctrl+C 并不会触发 SessionEnd。Claude Code 仅在会话真正结束时调用该钩子。

#### 🔍 SessionEnd 实际触发场景

- ✅ `/exit` 命令：正常终止会话。
- ✅ 关闭终端/窗口：进程结束。
- ✅ 正常退出 Claude Code：会话优雅关闭。
- ❌ Ctrl+C（一次）：仅中断输入。
- ❌ Ctrl+C（两次）：挂起会话，稍后恢复仍视作继续。

> 若恢复后看到 `SessionStart:resume hook success`，说明会话仅被暂停，没有触发 SessionEnd。

#### 🐛 常见问题：未生成 `session-consolidation` 记忆

- **症状**：使用 Ctrl+C 退出并稍后恢复，未看到对应记忆。
- **原因**：Ctrl+C 只是暂停，未结束会话。
- **解决办法**：希望生成记忆时请使用 `/exit` 正常结束。

#### 🔌 常见问题：连接失败

- **症状**：日志显示
  ```
  ⚠️ Memory Connection → Failed to connect using any available protocol
  💾 Storage → 💾 Unknown Storage (http://127.0.0.1:8000)
  ```
- **原因**：Hook 配置的协议与服务器不一致。
- **排查**：
  ```bash
  systemctl --user status mcp-memory-http.service  # 查看服务器协议
  grep endpoint ~/.claude/hooks/config.json        # 检查端点
  ```
- **修复**：更新 `~/.claude/hooks/config.json`，确保 `endpoint` 与服务器协议一致，例如：
  ```json
  {
    "memoryService": {
      "http": {
        "endpoint": "https://localhost:8000",
        "apiKey": "your-api-key"
      }
    }
  }
  ```

#### 📋 SessionEnd 记忆生成条件

1. 会话文本长度 ≥100 字符（可配置）。
2. 置信度 >0.1。
3. 已启用 `enableSessionConsolidation: true`。

**提取内容包括**：主题、决策、洞察、代码变更、下一步计划等。

#### 🔧 快速验证

```bash
# 检索最近的会话整合记忆
curl -sk "https://localhost:8000/api/search/by-tag" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["session-consolidation"], "limit": 5}' | \
  python -m json.tool | grep created_at_iso

# 手动触发 SessionEnd 钩子
node ~/.claude/hooks/core/session-end.js

# 检查服务健康度
curl -sk "https://localhost:8000/api/health"
```

更多诊断步骤参见 `docs/troubleshooting/session-end-hooks.md`。

### Windows SessionStart 钩子问题

**🚨 严重缺陷**：`matchers: ["*"]` 的 SessionStart 钩子会导致 Claude Code 在 Windows 上无限挂起。

- **问题编号**：[Issue #160](https://github.com/doobidoo/mcp-memory-service/issues/160)
- **表现**：启动即无响应，钩子执行但进程不退出，需强制关闭终端。
- **根因**：Windows 子进程管理存在缺陷，Node.js 钩子即使调用 `process.exit(0)` 仍可能保留句柄。
- **无效尝试**：重复 `process.exit(0)`、`finally` 强制退出、最小化脚本、批处理包装、增大超时等。

**推荐替代方案**：

1. **手动命令 `/session-start`**（推荐）
   ```bash
   claude /session-start
   ```
   - 功能等同自动 SessionStart。
   - 跨平台可用。
   - 安装程序会在 Windows 默认跳过自动配置。
   - 详见 `claude_commands/session-start.md`。

2. **禁用 SessionStart 钩子**：
   ```json
   {
   	"hooks": {
   		"SessionStart": []
   	}
   }
   ```

3. **改用 UserPromptSubmit 钩子**：
   ```json
   {
   	"hooks": {
   		"UserPromptSubmit": [
   			{
   				"matchers": ["*"],
   				"hooks": [
   					{
   						"type": "command",
   						"command": "node ~/.claude/hooks/core/mid-conversation.js",
   						"timeout": 8
   					}
   				]
   			}
   		]
   	}
   }
   ```

4. **手动执行脚本**（高级）：`node C:\Users\username\.claude\hooks\core\session-start.js`

**平台状态**：macOS ✅，Linux ✅，Windows ❌，在官方修复前需使用以上替代方案。

---

> 如需更多架构、部署与排障信息：
> - **后端配置问题**：参阅 [Wiki Troubleshooting Guide](https://github.com/doobidoo/mcp-memory-service/wiki/07-TROUBLESHOOTING#backend-configuration-issues)。
> - **历史上下文**：检索带 `claude-code-reference` 标签的记忆。
> - **快速自检**：执行 `python scripts/validation/diagnose_backend_config.py`。
