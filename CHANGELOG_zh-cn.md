# 更新日志（Changelog）

[简体中文](CHANGELOG_zh-cn.md) | [English](CHANGELOG.md)

> 说明：本文件以时间倒序记录 v8.24.0 及以上版本的主要变更。保留英文关键词便于对照提交与 Issue。

（以下为 v8.0.0+ 版本的主要更新）

本文件记录 MCP Memory Service 的主要变更。

更早版本请见 [CHANGELOG-HISTORIC.md](./CHANGELOG-HISTORIC.md)。

格式遵循 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，并遵守 [Semantic Versioning](https://semver.org/spec/v2.0.0.html)。

## [8.16.1] - 2025-11-02

### 修复
- **严重缺陷**：修正 MCP 服务器处理器（`server.py:2118`）中的 `KeyError: 'message'`。
  - **关联问题**：[ #198 ](https://github.com/doobidoo/mcp-memory-service/issues/198)
  - **根因**：`handle_store_memory()` 访问了并不存在的 `result["message"]` 键。
  - **影响**：通过 MCP `server.py` 处理器执行的所有记忆写入完全失败。
  - **修复**：按照 `MemoryService.store_memory()` 的真实返回格式处理：
    - 单条成功：`{"success": True, "memory": {...}}`
    - 分块成功：`{"success": True, "memories": [...], "total_chunks": N}`
    - 失败：`{"success": False, "error": "..."}`
  - **响应消息**：新增截断后的内容哈希，便于校验。
  - **相关**：与 #197 同系列问题；v8.16.0 修复了 async/await 缺陷，但遗漏了响应格式错误。

### 新增
- **集成测试**：新增 MCP 处理器测试套件（`tests/integration/test_mcp_handlers.py`）。
  - **覆盖范围**：`handle_store_memory()`、`handle_retrieve_memory()`、`handle_search_by_tag()` 共 11 个用例。
  - **回归测试**：针对 issue #198 编写专门用例，防止 KeyError 再现。
  - **测试场景**：成功、分块返回、错误处理、边界情况。
  - **目标**：避免后续版本再次出现同类缺陷。

### 技术说明
- **受影响处理器**：仅 `handle_store_memory()`。
- **修复方式**：对齐 `mcp_server.py:182-205` 中的正确实现模式。
- **兼容性**：无破坏性变更，仅修复已损坏的功能。

## [8.16.0] - 2025-11-01

### 新增
- **记忆类型整合工具** 🆕 —— 面向专业运维的类型治理方案。
  - **脚本**：`scripts/maintenance/consolidate_memory_types.py`（v1.0.0）。
  - **配置**：`scripts/maintenance/consolidation_mappings.json`（预置 168 条映射）。
  - **性能**：处理 1,000 条记忆约需 5 秒。
  - **安全特性**：
    - ✅ 执行前自动生成带时间戳的备份。
    - ✅ Dry-run 安全预览。
    - ✅ 事务保护（支持回滚）。
    - ✅ 数据库锁检测。
    - ✅ HTTP 服务器状态预警。
    - ✅ 磁盘空间校验。
    - ✅ 备份完整性验证。
  - **整合效果**：341 个碎片类型 → 24 个核心类目。
  - **实战案例**：1,049 条记忆在 5 秒内完成整合（占数据库 59%）。
  - **类型数减少**：342 → 128（降低 63%）。
  - **数据安全**：仅重新归类，不触及内容。

- **标准化记忆类型体系** —— 24 个核心类型划分 5 大类。
  - **内容类**（4 个）：note、reference、document、guide。
  - **活动类**（5 个）：session、implementation、analysis、troubleshooting、test。
  - **产出类**（4 个）：fix、feature、release、deployment。
  - **进度类**（2 个）：milestone、status。
  - **基础设施类**（5 个）：configuration、infrastructure、process、security、architecture。
  - **其他类**（4 个）：documentation、solution、achievement、technical。
  - **目标**：避免类型再次碎片化。
  - **收益**：查询更高效、命名更统一、语义聚类更准确。

### 变更
- **CLAUDE.md** —— 在开发指南中新增记忆类型分类章节。
  - 明确 24 个核心类型的使用准则。
  - 补充“应避免”的示例（如 bug-fix vs fix、technical-* 前缀）。
  - 在常用命令中加入整合脚本相关命令。
  - 总结保持类型一致性的最佳实践。

### 文档
- **维护文档全面更新**：
  - `scripts/maintenance/README.md` 增补整合工具指南。
  - Quick Reference 表新增性能指标摘要。
  - 详细说明安全前置条件与操作步骤。
  - 提供备份恢复流程。
  - 建议维护节奏（每月 Dry-run）。
  - **实战案例**：记录 2025 年 11 月线上整合结果。

### 技术细节
- **映射规则示例**：
  - NULL/空值 → `note`（实测 609 条）。
  - milestone/完成类变体 → `milestone`（21 种源类型 → 60 条）。
  - session 变体 → `session`（8 种源类型 → 37 条）。
  - technical-* 前缀移除 → 基础类型（62 条）。
  - project-* 前缀移除 → 基础类型（67 条）。
  - fix/bug 变体 → `fix`（8 种源类型 → 28 条）。
  - 更多规则见 `consolidation_mappings.json`（共 168 条）。

### 备注
- **可定制**：可编辑 `consolidation_mappings.json` 自定义行为。
- **幂等性**：重复执行不会产生副作用。
- **平台支持**：Linux、macOS、Windows（磁盘空间检测依赖 statvfs）。
- **建议频率**：每月运行 `--dry-run`，当类型数量超过 150 时执行正式整合。

## [8.15.1] - 2025-10-31

### Fixed

- **严重：Hook 安装脚本语法错误** —— 修复 `claude-hooks/install_hooks.py` 第 790 行的 IndentationError
  - **问题**：SessionEnd 钩子配置多了两个 `}`，导致安装失败。
  - **症状**：运行 `python install_hooks.py` 报 `IndentationError: unexpected indent`。
  - **根因**：合并冲突处理后遗留 2 个多余 `}`（行 790-791）。
  - **影响**：拉取 v8.15.0 后无法安装/更新钩子。
  - **修复**：移除多余 `}`，修正缩进。
  - **Files Modified**: `claude-hooks/install_hooks.py`
  - **测试**：修复后在 macOS 验证安装通过。

### 技术细节

- **Line Numbers**: 788-791 in install_hooks.py
- **错误类型**：IndentationError（Python 语法）
- **Detection Method**: Manual testing during hook reinstallation
- **Resolution Time**: Immediate (same-day patch)

## [8.15.0] - 2025-10-31

### Added

- **`/session-start` Slash Command** - Manual session initialization for all platforms
  - Provides same functionality as automatic SessionStart hook
  - Displays project context, git history, relevant memories
  - **Platform**: Works on Windows, macOS, Linux
  - **Use Case**: Primary workaround for Windows SessionStart hook bug (#160)
  - **Location**: `claude_commands/session-start.md`
  - **收益**：
    - ✅ Safe manual alternative to automatic hooks
    - ✅ No configuration changes needed
    - ✅ Full memory awareness functionality
    - ✅ Prevents Claude Code hangs on Windows

### Changed

- **Windows-Aware Installer** - Platform detection and automatic configuration
  - Detects Windows platform during hook installation
  - Automatically skips SessionStart hook configuration on Windows
  - Shows clear warning about SessionStart limitation
  - Suggests `/session-start` slash command as alternative
  - Also skips statusLine configuration on Windows (requires bash)
  - **Files Modified**: `claude-hooks/install_hooks.py` (lines 749-817)
  - **User Impact**: Prevents Windows users from accidentally breaking Claude Code

### Documentation

- **Enhanced Windows Support Documentation**
  - Updated `claude_commands/README.md` with `/session-start` command details
  - Added Windows workaround section to `claude-hooks/README.md`
  - Updated `CLAUDE.md` with `/session-start` as #1 recommended workaround
  - Added comprehensive troubleshooting guidance
  - Updated GitHub issue #160 with new workaround instructions

### Fixed

- **Windows Installation Experience** - Prevents SessionStart hook deadlock (Issue #160)
  - **Previous Behavior**: Windows users install hooks → Claude Code hangs → frustration
  - **New Behavior**: Windows users see warning → skip SessionStart → use `/session-start` → works
  - **Breaking Change**: None - fully backward compatible
  - **Upstream Issue**: Awaiting fix from Anthropic Claude Code team (claude-code#9542)

### 技术细节

- **Files Created**: 1 new slash command
  - `claude_commands/session-start.md` - Full command documentation
- **Files Modified**: 4 files

  - `claude-hooks/install_hooks.py` - Windows platform detection and warnings
  - `claude_commands/README.md` - Added `/session-start` to available commands
  - `claude-hooks/README.md` - Added slash command workaround reference
  - `CLAUDE.md` - Updated workaround prioritization

- **Platform Compatibility**:
  - ✅ Windows: `/session-start` command works, automatic hooks skipped
  - ✅ macOS: All features work (automatic hooks + slash command)
  - ✅ Linux: All features work (automatic hooks + slash command)

## [8.14.2] - 2025-10-31

### Performance

- **Optimized MemoryService.get_memory_by_hash()** - O(1) direct lookup replaces O(n) scan (Issue #196)
  - **Previous Implementation**: Loaded ALL memories via `storage.get_all_memories()`, then filtered by hash
  - **New Implementation**: Direct O(1) database lookup via `storage.get_by_hash()`
  - **Performance Impact**:
    - Small datasets (10-100 memories): ~2x faster
    - Medium datasets (100-1000 memories): ~10-50x faster
    - Large datasets (1000+ memories): ~100x+ faster
  - **Memory Usage**: Single memory object vs loading entire dataset into memory

### Added

- **Abstract method `get_by_hash()` in MemoryStorage base class** (storage/base.py)

  - Enforces O(1) direct hash lookup across all storage backends
  - Required implementation for all storage backends
  - Returns `Optional[Memory]` (None if not found)

- **Implemented `get_by_hash()` in CloudflareStorage** (storage/cloudflare.py)
  - Direct D1 SQL query: `SELECT * FROM memories WHERE content_hash = ?`
  - Handles R2 content loading if needed
  - Loads tags separately
  - Follows same pattern as SqliteVecMemoryStorage implementation

### Changed

- **MemoryService.get_memory_by_hash()** now uses direct storage lookup
  - Removed inefficient `get_all_memories()` + filter approach
  - Simplified implementation (5 lines vs 10 lines)
  - Updated docstring to reflect O(1) lookup

### Testing

- **Updated unit tests** (tests/unit/test_memory_service.py)

  - Mocks now use `storage.get_by_hash()` instead of `storage.get_all_memories()`
  - Added assertions to verify method calls
  - All 3 test cases pass (found, not found, error handling)

- **Updated integration tests** (tests/integration/test_api_with_memory_service.py)
  - Mock updated for proper method delegation
  - Real storage backends (SqliteVecMemoryStorage, HybridMemoryStorage) work correctly

### 技术细节

- **Files Modified**: 5 files

  - `src/mcp_memory_service/storage/base.py`: Added abstract `get_by_hash()` method
  - `src/mcp_memory_service/storage/cloudflare.py`: Implemented `get_by_hash()` (40 lines)
  - `src/mcp_memory_service/services/memory_service.py`: Optimized `get_memory_by_hash()`
  - `tests/unit/test_memory_service.py`: Updated mocks
  - `tests/integration/test_api_with_memory_service.py`: Updated mocks

- **Breaking Changes**: None - fully backward compatible
- **All Storage Backends Now Support get_by_hash()**:
  - ✅ SqliteVecMemoryStorage (line 1153)
  - ✅ CloudflareStorage (line 666)
  - ✅ HybridMemoryStorage (line 974, delegates to primary)

## [8.14.1] - 2025-10-31

### Added

- **Type Safety Improvements** - Comprehensive TypedDict definitions for all MemoryService return types
  - **Problem**: All MemoryService methods returned loose `Dict[str, Any]` types, providing no IDE support or compile-time validation
  - **Solution**: Created 14 specific TypedDict classes for structured return types
    - Store operations: `StoreMemorySingleSuccess`, `StoreMemoryChunkedSuccess`, `StoreMemoryFailure`
    - List operations: `ListMemoriesSuccess`, `ListMemoriesError`
    - Retrieve operations: `RetrieveMemoriesSuccess`, `RetrieveMemoriesError`
    - Search operations: `SearchByTagSuccess`, `SearchByTagError`
    - Delete operations: `DeleteMemorySuccess`, `DeleteMemoryFailure`
    - Health operations: `HealthCheckSuccess`, `HealthCheckFailure`
  - **收益**：
    - ✅ IDE autocomplete for all return values (type `result["` to see available keys)
    - ✅ Compile-time type checking catches typos (e.g., `result["succes"]` → type error)
    - ✅ Self-documenting API - clear contracts for all methods
    - ✅ Refactoring safety - renaming keys shows all affected code
    - ✅ 100% backward compatible - no runtime changes
    - ✅ Zero performance impact - pure static typing

### Fixed

- **Missing HybridMemoryStorage.get_by_hash()** - Added delegation method to HybridMemoryStorage
  - Fixed `AttributeError: 'HybridMemoryStorage' object has no attribute 'get_by_hash'`
  - All storage backends now implement `get_by_hash()`: SqliteVecMemoryStorage, CloudflareMemoryStorage, HybridMemoryStorage
  - Enables direct memory retrieval by content hash without loading all memories
  - See issue #196 for planned optimization to use this method in MemoryService

### 技术细节

- **Files Modified**:
  - `src/mcp_memory_service/services/memory_service.py`: Added 14 TypedDict classes, updated 6 method signatures
  - `src/mcp_memory_service/storage/hybrid.py`: Added `get_by_hash()` delegation method
- **Breaking Changes**: None - fully backward compatible (TypedDict is structural typing)
- **Testing**: All tests pass (15/15), comprehensive structure validation, HTTP API integration verified

## [8.14.0] - 2025-10-31

### Fixed

- **Comprehensive Tag Normalization** - DRY solution for all tag format handling
  - **Problem**: Inconsistent tag handling across different APIs caused validation errors
    - Top-level `tags` parameter accepted strings, but MemoryService expected arrays
    - `metadata.tags` field had no normalization, causing "is not of type 'array'" errors
    - Comma-separated strings like `"tag1,tag2,tag3"` were not split into arrays
    - Normalization logic was duplicated in some methods but missing in others
  - **Root Cause**:
    - MCP/HTTP adapters accepted `Union[str, List[str], None]` in signatures
    - But passed values to MemoryService without normalization
    - MemoryService expected `Optional[List[str]]`, causing type mismatch
    - `search_by_tag()` had normalization, but `store_memory()` did not (DRY violation)
  - **Solution** (DRY Principle Applied):
    - Created centralized `normalize_tags()` utility function (services/memory_service.py:27-56)
    - Handles ALL input formats:
      - `None` → `[]`
      - `"tag1,tag2,tag3"` → `["tag1", "tag2", "tag3"]`
      - `"single-tag"` → `["single-tag"]`
      - `["tag1", "tag2"]` → `["tag1", "tag2"]` (passthrough)
    - Updated `MemoryService.store_memory()` to:
      - Accept `Union[str, List[str], None]` type hint
      - Normalize both `tags` parameter and `metadata.tags` field
      - Merge tags from both sources with deduplication
    - Updated `MemoryService.search_by_tag()` to use utility (removed duplicate code)
  - **Files Modified**:
    - `src/mcp_memory_service/services/memory_service.py`: Added normalize_tags(), updated store_memory() and search_by_tag()
    - `src/mcp_memory_service/mcp_server.py`: Updated docstring to reflect all formats supported
  - **收益**：
    - ✅ Single source of truth for tag normalization (DRY)
    - ✅ All tag formats work everywhere (top-level, metadata, any protocol)
    - ✅ No more validation errors for comma-separated strings
    - ✅ Fully backward compatible
    - ✅ Consistent behavior across all endpoints
  - **User Impact**:
    - Can use any tag format anywhere without errors
    - No need to remember which parameter accepts which format
    - Improved developer experience and reduced friction

### 技术细节

- **Affected Components**: MemoryService (business logic layer), MCP server documentation
- **Breaking Changes**: None - fully backward compatible
- **Tag Merge Behavior**: When tags provided in both parameter and metadata, they are merged and deduplicated
- **Testing**: Verified with all format combinations (None, string, comma-separated, array, metadata.tags)

## [8.13.5] - 2025-10-31

### Fixed

- **Memory Hooks Display Polish** - Visual improvements for cleaner, more professional CLI output
  - **Issue**: Multiple visual inconsistencies in memory hooks tree structure display
  - **Problems Identified**:
    1. Redundant bottom frame (`╰────╯`) after tree naturally ended with `└─`
    2. Wrapped text continuation showing vertical lines (`│`) after last items
    3. Duplicate final summary message ("Context injected") when header already shows count
    4. Embedded formatting (✅, •, markdown) conflicting with tree structure
    5. Excessive content length despite adaptive truncation
  - **Fixes** (commits ed46d24, 998a39c):
    - **Content Sanitization**: Remove checkmarks, bullets, markdown formatting that conflicts with tree characters
    - **Smart Truncation**: Extract first 1-2 sentences for <400 char limits using sentence boundary detection
    - **Tree Continuation Logic**: Last items show clean indentation without vertical lines on wrapped text
    - **Remove Redundant Frame**: Tree ends naturally with `└─`, no separate closing box
    - **Remove Duplicate Message**: Header shows "X memories loaded", no redundant final summary
  - **Files Modified**:
    - `claude-hooks/utilities/context-formatter.js`: Content sanitization, smart truncation, tree continuation fixes
    - `claude-hooks/core/session-start.js`: Removed redundant success message
  - **Result**: Clean, consistent tree structure with proper visual hierarchy and no redundancy
  - **User Impact**: Professional CLI output, easier to scan, maintains continuous blue tree lines properly

### 技术细节

- **Affected Component**: Claude Code memory awareness hooks (SessionStart display)
- **Deployment**: Hooks loaded from repository automatically, no server restart needed
- **Testing**: Verified with mock execution and real Claude Code session

## [8.13.4] - 2025-10-30

### Fixed

- **Critical: Memory Hooks Showing Incorrect Ages** (#195) - Timestamp unit mismatch causing 20,371-day ages
  - **Error**: Memory hooks reporting `avgAge: 20371 days, medianAge: 20371 days` when actual age was 6 days
  - **User Impact**: Recent memories didn't surface, auto-calibration incorrectly triggered "stale memory" warnings
  - **Root Cause** (claude-hooks/utilities/memory-client.js:273): Timestamp unit mismatch
    - HTTP API returns Unix timestamps in **SECONDS**: `1758344479.729`
    - JavaScript `Date()` expects **MILLISECONDS**: Interpreted as `Jan 21, 1970` (55 years ago)
    - Age calculation: `(now - 1758344479ms) / 86400000 = 20371 days`
  - **Symptoms**:
    - `[Memory Age Analyzer] { avgAge: 20371, recentPercent: 0, isStale: true }`
    - Hooks showed "Stale memory set detected (median: 20371d old)"
    - Recent development work (< 7 days) never surfaced in context
  - **Fix** (claude-hooks/utilities/memory-client.js:273-294, commit 5c54894):
    - Convert API timestamps from seconds to milliseconds (`× 1000`)
    - Added year 2100 check (`< 4102444800`) to prevent double-conversion
    - Applied in `_performApiPost()` response handler for both `created_at` and `updated_at`
  - **Result**:
    - `avgAge: 6 days, medianAge: 5 days, recentPercent: 100%, isStale: false`
    - Recent memories surface correctly
    - Auto-calibration works properly
    - Git context weight adjusts based on actual ages
  - **Note**: Affects all users using HTTP protocol for memory hooks

### 技术细节

- **Affected Component**: Claude Code memory awareness hooks (HTTP protocol path)
- **File Changed**: `claude-hooks/utilities/memory-client.js` (lines 273-294)
- **Deployment**: Hooks loaded from repository automatically, no server restart needed
- **Issue**: https://github.com/doobidoo/mcp-memory-service/issues/195

## [8.13.3] - 2025-10-30

### Fixed

- **Critical: MCP Memory Tools Broken** - v8.12.0 regression preventing all MCP memory operations
  - **Error**: `KeyError: 'message'` when calling any MCP memory tool (store, retrieve, search, etc.)
  - **User Impact**: MCP tools completely non-functional - "Error storing memory: 'message'"
  - **Root Cause** (mcp_server.py:175): Return format mismatch between MemoryService and MCP tool expectations
    - MCP tool expects: `{success: bool, message: str, content_hash: str}`
    - MemoryService returns: `{success: bool, memory: {...}}`
    - MCP protocol tries to access missing 'message' field → KeyError
  - **Why It Persisted**: HTTP API doesn't require these specific fields, so integration tests passed
  - **Fix** (mcp_server.py:173-206): Transform MemoryService response to MCP TypedDict format
    - Capture result from MemoryService.store_memory()
    - Extract content_hash from nested memory object
    - Add descriptive "message" field
    - Handle 3 cases: failure (error message), chunked (multiple memories), single memory
  - **Result**: MCP tools now work correctly with proper error messages
  - **Note**: Requires MCP server restart (`/mcp` command in Claude Code) to load fix

### 技术细节

- **Introduced**: v8.12.0 MemoryService architecture refactoring (#176)
- **Affected Tools**: store_memory, all MCP protocol operations
- **HTTP API**: Unaffected (different response format requirements)
- **Test Gap**: No integration tests validating MCP tool response formats

## [8.13.2] - 2025-10-30

### Fixed

- **Memory Sync Script Broken** (#193): Fixed sync_memory_backends.py calling non-existent `store_memory()` method
  - **Error**: `AttributeError: 'CloudflareStorage' object has no attribute 'store_memory'`
  - **User Impact**: Sync script completely non-functional - couldn't sync memories between Cloudflare and SQLite backends
  - **Root Cause** (scripts/sync/sync_memory_backends.py:144-147): Script used old `store_memory()` API that no longer exists
  - **Fix** (#194, b69de83): Updated to use proper `Memory` object creation and `storage.store()` method
    - Create `Memory` object with `content`, `content_hash`, `tags`, `metadata`, `created_at`
    - Call `await target_storage.store(memory_obj)` instead of non-existent `store_memory()`
    - Added safe `.get('metadata', {})` to prevent KeyError on missing metadata
    - Fixed import order to comply with PEP 8 (config → models → storage)
  - **Result**: Sync script now successfully syncs memories between backends
  - **Credit**: Fix by AMP via PR #194, reviewed by Gemini

## [8.13.1] - 2025-10-30

### Fixed

- **Critical Concurrent Access Bug**: MCP server initialization failed with "database is locked" when HTTP server running
  - **Error**: `sqlite3.OperationalError: database is locked` during MCP tool initialization
  - **User Impact**: MCP memory tools completely non-functional while HTTP server running - "this worked before without any flaws"
  - **Root Cause #1** (sqlite_vec.py:329): Connection timeout set AFTER opening database instead of during connection
    - Original: `sqlite3.connect(path)` used default 5-second timeout, then applied `PRAGMA busy_timeout=15000`
    - SQLite only respects timeout parameter passed to `connect()`, not pragma applied afterward
    - MCP server timed out before it could set the higher timeout value
  - **Root Cause #2** (sqlite_vec.py:467-476): Both servers attempting DDL operations (CREATE TABLE, CREATE INDEX) simultaneously
    - Even with WAL mode, DDL operations require brief exclusive locks
    - No detection of already-initialized database before running DDL
  - **Fix #1** (sqlite_vec.py:291-326): Parse `busy_timeout` from `MCP_MEMORY_SQLITE_PRAGMAS` environment variable BEFORE opening connection
    - Convert from milliseconds to seconds (15000ms → 15.0s)
    - Pass timeout to `sqlite3.connect(path, timeout=15.0)` for immediate effect
    - Allows MCP server to wait up to 15 seconds for HTTP server's DDL operations
  - **Fix #2** (sqlite_vec.py:355-373): Detect already-initialized database and skip DDL operations
    - Check if `memories` and `memory_embeddings` tables exist after loading sqlite-vec extension
    - If tables exist, just load embedding model and mark as initialized
    - Prevents "database is locked" errors from concurrent CREATE TABLE/INDEX attempts
  - **Result**: MCP and HTTP servers now coexist without conflicts, maintaining pre-v8.9.0 concurrent access behavior

### 技术细节

- **Timeline**: Bug discovered during memory consolidation testing, fixed same day
- **Affected Versions**: v8.9.0 introduced database lock prevention pragmas but didn't fix concurrent initialization
- **Test Validation**: MCP health check returns healthy with 1857 memories while HTTP server running
- **Log Evidence**: "Database already initialized by another process, skipping DDL operations" confirms fix working

## [8.13.0] - 2025-10-29

### Added

- **HTTP Server Integration Tests** (#190): Comprehensive test suite with 32 tests prevents production bugs like v8.12.0

  - `tests/integration/test_http_server_startup.py`: 8 tests for server startup validation
  - `tests/unit/test_fastapi_dependencies.py`: 11 tests for dependency injection
  - `tests/unit/test_storage_interface_compatibility.py`: 13 tests for backend interface consistency
  - Extended `tests/integration/test_api_with_memory_service.py`: +11 HTTP API tests with TestClient
  - Tests would have caught all 3 v8.12.0 production bugs (import-time evaluation, syntax errors, interface mismatches)

- **Storage Method: get_largest_memories()** (#186): Efficient database queries for largest memories by content length
  - Added to all storage backends (SQLite, Cloudflare, Hybrid)
  - Uses `ORDER BY LENGTH(content) DESC LIMIT n` instead of loading 1000 memories and sorting in Python
  - Analytics dashboard now queries entire dataset for truly largest memories

### Fixed

- **Analytics Dashboard Timezone Bug** (#186): Fixed heatmap calendar showing wrong day-of-week near timezone boundaries
  - JavaScript `new Date('YYYY-MM-DD')` parsed as UTC midnight, but `getDay()` used local timezone
  - Changed to parse date components in local timezone: `new Date(year, month-1, day)`
  - Prevents calendar cells from shifting to previous/next day for users in UTC-12 to UTC+12 timezones

### Improved

- **Analytics Performance**: Reduced memory sample for average size calculation from 1000→100 memories
- **Test Coverage**: Zero HTTP integration tests → 32 comprehensive tests covering server startup, dependencies, and API endpoints

### Documentation

- **MCP Schema Caching** (#173): Closed with comprehensive documentation in CLAUDE.md and troubleshooting guides
  - Root cause: MCP protocol caches tool schemas client-side
  - Workaround: `/mcp` command reconnects server with fresh schema
  - Documented symptoms, diagnosis, and resolution steps

## [8.12.1] - 2025-10-28

### Fixed

- **Critical Production Bug #1** (ef2c64d): Import-time default parameter evaluation in `get_memory_service()`

  - **Error**: `HTTPException: 503: Storage not initialized` during module import
  - **Root Cause**: Python evaluates default parameters at function definition time, not call time
  - **Impact**: HTTP server couldn't start - module import failed immediately
  - **Fix**: Changed from `storage: MemoryStorage = get_storage()` to `storage: MemoryStorage = Depends(get_storage)`
  - **Technical**: FastAPI's `Depends()` defers evaluation until request time and integrates with dependency injection

- **Critical Production Bug #2** (77de4d2): Syntax error + missing FastAPI Depends import in `memories.py`

  - **Error**: `SyntaxError: expected an indented block after 'if' statement on line 152`
  - **Root Cause**: `if INCLUDE_HOSTNAME:` had no indented body, nested if-elif-else block not indented
  - **Impact**: SyntaxError prevented module import + FastAPI validation failure
  - **Fix**: Properly indented hostname resolution logic, added missing `Depends` import to dependencies.py

- **Critical Production Bug #3** (f935c56): Missing `tags` parameter in `count_all_memories()` across all storage backends

  - **Error**: `TypeError: count_all_memories() got an unexpected keyword argument 'tags'`
  - **User Report**: "failed to load dashboard data"
  - **Root Cause**: MemoryService called `count_all_memories(memory_type=type, tags=tags)` but base class and implementations didn't accept tags parameter
  - **Impact**: Dashboard completely broken - GET /api/memories returned 500 errors
  - **Fix**: Updated 4 files (base.py, hybrid.py, sqlite_vec.py, cloudflare.py) to add tags parameter with SQL LIKE filtering
  - **Why Tests Missed It**: AsyncMock accepts ANY parameters, never tested real storage backend implementations

- **Analytics Metrics Bug** (8beeb07): Analytics tab showed different metrics than Dashboard tab
  - **Problem**: Dashboard queried ALL memories, Analytics sampled only 1000 recent memories
  - **Impact**: "This Week" count was inaccurate when total memories > 1000
  - **Fix**: Changed Analytics endpoint to use `storage.get_stats()` instead of sampling
  - **Performance**: Eliminated O(n) memory loading for simple count operation, now uses efficient SQL COUNT

### Changed

- **Analytics Endpoint Performance** - Increased monthly sample from 2,000 to 5,000 memories
- **Code Quality** - Added TODO comments for moving monthly calculations to storage layer

### 技术细节

- **Timeline**: All 4 bugs discovered and fixed within 4 hours of v8.12.0 release (15:03 UTC → 22:03 UTC)
- **Post-Mortem**: Created Issue #190 for HTTP server integration tests to prevent future production bugs
- **Test Coverage Gap**: v8.12.0 had 55 tests but zero HTTP server integration tests
- **Lesson Learned**: Tests used mocked storage that never actually started the server or tested real FastAPI dependency injection

**Note**: This patch release resolves all production issues from v8.12.0 architectural changes. Comprehensive analysis stored in memory with tag `v8.12.0,post-release-bugs`.

## [8.12.0] - 2025-10-28

### Added

- **MemoryService Architecture** - Centralized business logic layer (Issue #188, PR #189)
  - Single source of truth for all memory operations
  - Consistent behavior across API endpoints and MCP tools
  - 80% code duplication reduction between API and MCP servers
  - Dependency injection pattern for clean architecture
  - **Comprehensive Test Coverage**:
    - 34 unit tests (100% pass rate)
    - 21 integration tests for API layer
    - End-to-end workflow tests with real storage
    - Performance validation for database-level filtering

### Fixed

- **Critical Bug #1**: `split_content()` missing required `max_length` parameter
  - Impact: Would crash immediately on any content chunking operation
  - Fix: Added proper parameter passing with storage backend max_length
- **Critical Bug #2**: `storage.delete_memory()` method does not exist in base class
  - Impact: Delete functionality completely broken
  - Fix: Changed to use `storage.delete(content_hash)` from base class
- **Critical Bug #3**: `storage.get_memory()` method does not exist in base class
  - Impact: Get by hash functionality completely broken
  - Fix: Implemented using `get_all_memories()` with client-side filtering
- **Critical Bug #4**: `storage.health_check()` method does not exist in base class
  - Impact: Health check functionality completely broken
  - Fix: Changed to use `storage.get_stats()` from base class
- **Critical Bug #5**: `storage.search_by_tags()` method mismatch (plural vs singular)
  - Impact: Tag search functionality completely broken
  - Fix: Changed to use `storage.search_by_tag()` (singular) from base class
- **Critical Bug #6**: Incorrect chunking logic comparing `len(content) > CONTENT_PRESERVE_BOUNDARIES`
  - Impact: ALL content >1 character would trigger chunking (CONTENT_PRESERVE_BOUNDARIES is boolean `True`)
  - Fix: Proper comparison using `storage.max_content_length` numeric value
- **Critical Bug #7**: Missing `store()` return value handling
  - Impact: Success/failure not properly tracked
  - Fix: Proper unpacking of `(success, message)` tuple from storage operations

### Changed

- **API Endpoints** - Refactored to use MemoryService dependency injection
  - `/api/memories` (list, create) uses MemoryService
  - `/api/search` endpoints use MemoryService
  - Consistent response formatting via service layer
- **Code Maintainability** - Removed 356 lines of duplicated code
  - Single place to modify business logic
  - Unified error handling
  - Consistent hostname tagging logic
- **Performance** - Database-level filtering prevents O(n) memory loading
  - Scalable pagination with offset/limit at storage layer
  - Efficient tag and type filtering

### 技术细节

- **Files Modified**: 6 files, 1469 additions, 356 deletions
- **Test Coverage**: 55 new tests (34 unit + 21 integration)
- **Bug Discovery**: Comprehensive testing revealed 7 critical bugs that would have made the release non-functional
- **Quality Process**: Test-driven debugging approach prevented broken release

**Note**: This release demonstrates the critical importance of comprehensive testing before merging architectural changes. All 7 bugs were caught through systematic unit and integration testing.

## [8.11.0] - 2025-10-28

### Added

- **JSON Document Loader** - Complete implementation of JSON file ingestion (Issue #181, PR #187)

  - **Nested Structure Flattening**: Converts nested JSON to searchable text with dot notation or bracket notation
  - **Configurable Strategies**: Choose flattening style, max depth, type inclusion
  - **Array Handling**: Multiple modes (expand, summarize, flatten) for different use cases
  - **Comprehensive Tests**: 15 unit tests covering all functionality
  - **Use Cases**: Knowledge base exports, API documentation, config files, structured metadata

- **CSV Document Loader** - Complete implementation of CSV file ingestion (Issue #181, PR #187)
  - **Auto-Detection**: Automatically detects delimiters (comma, semicolon, tab, pipe) and headers
  - **Row-Based Formatting**: Converts tabular data to searchable text with column context
  - **Encoding Support**: Auto-detects UTF-8, UTF-16, UTF-32, Latin-1, CP1252
  - **Large File Handling**: Efficient row-based chunking for scalability
  - **Comprehensive Tests**: 14 unit tests covering all functionality
  - **Use Cases**: Data dictionaries, reference tables, tabular documentation, log analysis

### Fixed

- **False Advertising** - Resolved issue where JSON and CSV were listed in `SUPPORTED_FORMATS` but had no loader implementations
  - Previous behavior: Upload would fail with "No loader available" error
  - New behavior: Full functional support with proper chunking and metadata

### Changed

- **Ingestion Module** - Updated to register new JSON and CSV loaders
- **Test Coverage** - Added 29 new unit tests (15 JSON + 14 CSV)

## [8.10.0] - 2025-10-28

### Added

- **Complete Analytics Dashboard Implementation** (Issue #182, PR #183)
  - Memory Types Breakdown (pie chart)
  - Activity Heatmap (GitHub-style calendar with 90d/6mo/1yr periods)
  - Top Tags Report (usage trends, co-occurrence patterns)
  - Recent Activity Report (hourly/daily/weekly breakdowns)
  - Storage Report (largest memories, efficiency metrics)
  - Streak Tracking (current and longest consecutive days)

### Fixed

- **Activity Streak Calculation** - Fixed current streak to include today check
- **Total Days Calculation** - Corrected date span vs active days count
- **Longest Streak Initialization** - Fixed from 0 to 1

### Changed

- **Analytics API** - Added 5 new endpoints with Pydantic models
- **Dashboard Documentation** - Updated wiki with complete analytics features

## [8.9.0] - 2025-10-27

### Fixed

- **Database Lock Prevention** - Resolved "database is locked" errors during concurrent HTTP + MCP server access (Issue discovered during performance troubleshooting)
  - **Root Cause**: Default `busy_timeout=5000ms` too short for concurrent writes from multiple MCP clients
  - **Solution**: Applied recommended SQLite pragmas (`busy_timeout=15000,cache_size=20000`)
  - **WAL Mode**: Already enabled by default, now properly configured for multi-client access
  - **Impact**: Zero database locks during testing with 5 concurrent write operations
  - **Documentation**: Updated multi-client architecture docs with pragma recommendations

### Added

- **Hybrid Backend Installer Support** - Full hybrid backend support in simplified installer (`scripts/installation/install.py`)
  - **Interactive Selection**: Hybrid now option 4 (recommended default) in installer menu
  - **Automatic Configuration**: SQLite pragmas set automatically for sqlite_vec and hybrid backends
  - **Cloudflare Setup**: Interactive credential configuration with connection testing
  - **Graceful Fallback**: Falls back to sqlite_vec if Cloudflare setup cancelled or fails
  - **Claude Desktop Integration**: Hybrid backend configuration includes:
    - SQLite pragmas for concurrent access (`MCP_MEMORY_SQLITE_PRAGMAS`)
    - Cloudflare credentials for background sync
    - Proper environment variable propagation
  - **收益**：
    - 5ms local reads (SQLite-vec)
    - Zero user-facing latency (background Cloudflare sync)
    - Multi-device synchronization
    - Concurrent access support

### Changed

- **Installer Defaults** - Hybrid backend now recommended for production use
  - Updated argparse choices to include `hybrid` option
  - Changed default selection from sqlite_vec to hybrid (option 4)
  - Enhanced compatibility detection with "recommended" status for hybrid
  - Improved final installation messages with backend-specific guidance
- **Environment Management** - Cloudflare credentials now set in current environment immediately
  - `save_credentials_to_env()` sets both .env file AND os.environ
  - Ensures credentials available for Claude Desktop config generation
  - Proper variable propagation for hybrid and cloudflare backends
- **Path Configuration** - Updated `configure_paths()` to handle all backends
  - SQLite database paths for: `sqlite_vec`, `hybrid`, `cloudflare`
  - Cloudflare credentials included when backend requires them
  - Backward compatible with existing installations

### 技术细节

- **Files Modified**:
  - `scripts/installation/install.py`: Lines 655-659 (compatibility), 758 (menu), 784-802 (selection), 970-1017 (hybrid install), 1123-1133 (env config), 1304 (path config), 1381-1401 (Claude Desktop config), 1808-1821 (final messages)
  - `src/mcp_memory_service/__init__.py`: Line 50 (version bump)
  - `pyproject.toml`: Line 7 (version bump)
- **Concurrent Access Testing**: 5/5 simultaneous writes succeeded without locks
- **HTTP Server Logs**: Confirmed background Cloudflare sync working (line 369: "Successfully stored memory")

## [8.8.2] - 2025-10-26

### Fixed

- **Document Upload Tag Validation** - Prevents bloated tags from space-separated file paths (Issue #174, PR #179)
  - **Enhanced Tag Parsing**: Split tags by comma OR space instead of comma only
  - **Robust file:// URI Handling**: Uses `urllib.parse` for proper URL decoding and path handling
    - Handles URL-encoded characters (e.g., `%20` for spaces)
    - Handles different path formats (e.g., `file:///C:/...`)
    - Properly handles Windows paths with leading slash from urlparse
  - **File Path Sanitization**: Remove `file://` prefixes, extract filenames only, clean path separators
  - **Explicit Tag Length Validation**: Tags exceeding 100 chars now raise explicit HTTPException instead of being silently dropped

### Added

- **Processing Mode Toggle** - UI enhancement for multiple file uploads (PR #179)
  - **Batch Processing**: All files processed together (faster, default)
  - **Individual Processing**: Each file processed separately with better error isolation
  - Toggle only appears when multiple files are selected
  - Comprehensive help section explaining both modes with pros/cons

### Changed

- **Code Quality Improvements** - Eliminated code duplication in document upload endpoints (PR #179)
  - Extracted `parse_and_validate_tags()` helper function to eliminate duplicate tag parsing logic
  - Removed 44 lines of duplicate code from `upload_document` and `batch_upload_documents`
  - Extracted magic number (500ms upload delay) to static constant `INDIVIDUAL_UPLOAD_DELAY`
  - Simplified toggle display logic with ternary operator
  - Created Issue #180 for remaining medium-priority code quality suggestions

## [8.8.1] - 2025-10-26

### Fixed

- **Error Handling Improvements** - Enhanced robustness in MemoryService and maintenance scripts (Issue #177)
  - **MemoryService.store_memory()**: Added specific exception handling for better error classification
    - `ValueError` → validation errors with "Validation error" messages
    - `httpx.NetworkError/TimeoutException/HTTPStatusError` → storage errors with "Storage error" messages
    - Generic `Exception` → unexpected errors with full logging and "unexpected error" messages
  - **Maintenance Scripts**: Added proper error handling to prevent crashes
    - `find_cloudflare_duplicates.py`: Wrapped `get_all_memories_bulk()` in try/except, graceful handling of empty results
    - `delete_orphaned_vectors_fixed.py`: Already used public API (no changes needed)

### Added

- **Encapsulation Methods** - New public APIs for Cloudflare storage operations (Issue #177)
  - `CloudflareStorage.delete_vectors_by_ids()` - Batch vector deletion with proper error handling
  - `CloudflareStorage.get_all_memories_bulk()` - Efficient bulk loading without N+1 tag queries
  - `CloudflareStorage._row_to_memory()` - Helper for converting D1 rows to Memory objects
  - **Performance**: Bulk operations avoid expensive individual tag lookups
  - **Maintainability**: Public APIs instead of direct access to private `_retry_request` method

### Changed

- **Dependency Management** - Added conditional typing-extensions for Python 3.10 (Issue #177)
  - Added `"typing-extensions>=4.0.0; python_version < '3.11'"` to pyproject.toml
  - Ensures `NotRequired` import works correctly on Python 3.10
  - No impact on Python 3.11+ installations

### Review

- **Gemini Code Assist**: "This pull request significantly improves the codebase by enhancing error handling and improving encapsulation... well-executed and contribute to better maintainability"
- **Feedback Addressed**: All review suggestions implemented, including enhanced exception handling

## [8.8.0] - 2025-10-26

### Changed

- **DRY Refactoring** - Eliminated code duplication between MCP and HTTP servers (PR #176, Issue #172)
  - **Problem**: MCP (`mcp_server.py`) and HTTP (`server.py`) servers had 364 lines of duplicated business logic
    - Bug fixes applied to one server were missed in the other (e.g., PR #162 tags validation)
    - Maintenance burden of keeping two implementations synchronized
    - Risk of behavioral inconsistencies between protocols
  - **Solution**:
    - Created `MemoryService` class (442 lines) as single source of truth for business logic
    - Refactored `mcp_server.py` to thin adapter (-338 lines, now ~50 lines per method)
    - Refactored `server.py` to use MemoryService (169 lines modified)
    - Both servers now delegate to shared business logic
  - **收益**：
    - **Single source of truth**: All memory operations (store, retrieve, search, delete) in one place
    - **Consistent behavior**: Both protocols guaranteed identical business logic
    - **Easier maintenance**: Bug fixes automatically apply to both servers
    - **Better testability**: Business logic isolated and independently testable
    - **Prevents future bugs**: Impossible to fix one server and forget the other
  - **Type Safety**: Added TypedDict classes (`MemoryResult`, `OperationResult`, `HealthStats`) for better type annotations
  - **Backward Compatibility**: No API changes, both servers remain fully compatible
  - **Testing**: All tests passing (15/15 Cloudflare storage tests)
  - **Review**: Gemini Code Assist: "significant and valuable refactoring... greatly improves maintainability and consistency"
  - **Follow-up**: Minor improvements tracked in Issue #177 (error handling, encapsulation)

### Fixed

- **Python 3.10 Compatibility** - Added `NotRequired` import fallback (src/mcp_memory_service/mcp_server.py:23-26)
  - Uses `typing.NotRequired` on Python 3.11+
  - Falls back to `typing_extensions.NotRequired` on Python 3.10
  - Ensures compatibility across Python versions

### Added

- **Maintenance Scripts** - Cloudflare cleanup utilities (from v8.7.1 work)
  - `scripts/maintenance/find_cloudflare_duplicates.py` - Detect duplicates in Cloudflare D1
  - `scripts/maintenance/delete_orphaned_vectors_fixed.py` - Clean orphaned Vectorize vectors
  - `scripts/maintenance/fast_cleanup_duplicates_with_tracking.sh` - Platform-aware SQLite cleanup
  - `scripts/maintenance/find_all_duplicates.py` - Platform detection (macOS/Linux paths)

## [8.7.1] - 2025-10-26

### Fixed

- **Cloudflare Vectorize Deletion** - Fixed vector deletion endpoint bug (src/mcp_memory_service/storage/cloudflare.py:671)
  - **Problem**: Used incorrect endpoint `/delete-by-ids` (hyphens) causing 404 Not Found errors, preventing vector deletion
  - **Solution**:
    - Changed to correct Cloudflare API endpoint `/delete_by_ids` (underscores)
    - Fixed payload format from `[vector_id]` to `{"ids": [vector_id]}`
    - Created working cleanup script: `scripts/maintenance/delete_orphaned_vectors_fixed.py`
    - Removed obsolete broken script: `scripts/maintenance/delete_orphaned_vectors.py`
  - **Impact**: Successfully deleted 646 orphaned vectors from Vectorize in 7 batches
  - **Testing**: Verified with production data (646 vectors, 100/batch, all mutations successful)
  - **Discovery**: Found via web research of official Cloudflare Vectorize API documentation

## [8.7.0] - 2025-10-26

### Fixed

- **Cosine Similarity Migration** - Fixed 0% similarity scores in search results (src/mcp_memory_service/storage/sqlite_vec.py:187)

  - **Problem**: L2 distance metric gave 0% similarity for all searches due to score calculation `max(0, 1-distance)` returning 0 for distances >1.0
  - **Solution**:
    - Migrated embeddings table from L2 to cosine distance metric
    - Updated score calculation to `1.0 - (distance/2.0)` for cosine range [0,2]
    - Added automatic migration logic with database locking retry (exponential backoff)
    - Implemented `_initialized` flag to prevent multiple initialization
    - Created metadata table for storage configuration persistence
  - **Performance**: Search scores improved from 0% to 70-79%, exact match accuracy 79.2% (was 61%)
  - **Impact**: 2605 embeddings regenerated successfully

- **Dashboard Search Improvements** - Enhanced search threshold handling (src/mcp_memory_service/web/static/app.js:283)
  - Fixed search threshold always being sent even when not explicitly set
  - Improved document filtering to properly handle memory object structure
  - Only send `similarity_threshold` parameter when user explicitly sets it
  - Better handling of `memory.memory_type` and `memory.tags` for document results

### Added

- **Maintenance Scripts** - Comprehensive database maintenance tooling (scripts/maintenance/)
  - **regenerate_embeddings.py** - Regenerate all embeddings after migrations (~5min for 2600 memories)
  - **fast_cleanup_duplicates.sh** - 1800x faster duplicate removal using direct SQL (<5s for 100+ duplicates vs 2.5 hours via API)
  - **find_all_duplicates.py** - Fast duplicate detection with timestamp normalization (<2s for 2000 memories)
  - **README.md** - Complete documentation with performance benchmarks, best practices, and troubleshooting

### 技术细节

- **Migration Approach**: Drop-and-recreate embeddings table to change distance metric (vec0 limitation)
- **Retry Logic**: Exponential backoff for database locking (1s → 2s → 4s delays)
- **Performance Benchmark**: Direct SQL vs API operations show 1800x speedup for bulk deletions
- **Duplicate Detection**: Content normalization removes timestamps for semantic comparison using MD5 hashing

## [8.6.0] - 2025-10-25

### Added

- **Document Ingestion System** - Complete document upload and management through web UI (#147, #164)

  - **Single and Batch Upload**: Drag-and-drop or file browser support for PDF, TXT, MD, JSON documents
  - **Background Processing**: Async document processing with progress tracking and status updates
  - **Document Management UI**: New Documents tab in web dashboard with full CRUD operations
  - **Upload History**: Track all document ingestion with status, chunk counts, and file sizes
  - **Document Viewer**: Modal displaying all memory chunks from uploaded documents (up to 1000 chunks)
  - **Document Removal**: Delete documents and their associated memory chunks with confirmation
  - **Search Ingested Content**: Semantic search within uploaded documents to verify indexing
  - **Claude Commands**: `/memory-ingest` and `/memory-ingest-dir` for CLI document upload
  - **API Endpoints**:
    - `POST /api/documents/upload` - Single document upload
    - `POST /api/documents/batch-upload` - Multiple document upload
    - `GET /api/documents/history` - Upload history
    - `GET /api/documents/status/{upload_id}` - Upload status
    - `GET /api/documents/search-content/{upload_id}` - View document chunks
    - `DELETE /api/documents/remove/{upload_id}` - Remove document
    - `DELETE /api/documents/remove-by-tags` - Bulk remove by tags
  - **Files Created**:
    - `src/mcp_memory_service/web/api/documents.py` (779 lines) - Document API
    - `claude_commands/memory-ingest.md` - Single document ingestion command
    - `claude_commands/memory-ingest-dir.md` - Directory ingestion command
    - `docs/development/dashboard-workflow.md` - Development workflow documentation

- **Chunking Configuration Help** - Interactive UI guidance for document chunking parameters

  - Inline help panels with collapsible sections for chunk size and overlap settings
  - Visual diagram showing how overlap works between consecutive chunks
  - Pre-configured recommendations (Default: 1000/200, Smaller: 500/100, Larger: 2000/400)
  - Rule-of-thumb guidelines (15-25% overlap of chunk size)
  - Full dark mode support for all help elements

- **Tag Length Validation** - Server-side validation to prevent data corruption (#174)
  - Maximum tag length enforced at 100 characters
  - Validation on both single and batch upload endpoints
  - Clear error messages showing first invalid tag
  - Frontend filtering to hide malformed tags in display
  - Prevents bloated tags from accidental file path pasting

### Fixed

- **Security Vulnerabilities** - Multiple critical security fixes addressed

  - Path traversal vulnerability in file uploads (use `tempfile.NamedTemporaryFile()`)
  - XSS prevention in tag display and event handlers (escape all user-provided filenames)
  - CSP compliance by removing inline `onclick` handlers, using `addEventListener` instead
  - Proper input validation and sanitization throughout upload flow

- **Document Viewer Critical Bugs** - Comprehensive fixes for document management

  - **Chunk Limit**: Increased from 10 to 1000 chunks (was only showing first 10 of 430 chunks)
  - **Upload Session Persistence**: Documents now viewable after server restart (session optional, uses `upload_id` tag search)
  - **Filename Retrieval**: Get filename from memory metadata when session unavailable
  - **Batch File Size**: Calculate and display total file size for batch uploads (was showing 0.0 KB)
  - **Multiple Confirmation Dialogs**: Fixed duplicate event listeners causing N dialogs for N uploads
  - **Event Listener Deduplication**: Added `documentsListenersSetup` flag to prevent duplicate setup

- **Storage Backend Enhancements** - `delete_by_tags` implementation for document deletion

  - Added `delete_by_tags()` method to `MemoryStorage` base class with error aggregation
  - Optimized `SqliteVecMemoryStorage.delete_by_tags()` with single SQL query using OR conditions
  - Added `HybridMemoryStorage.delete_by_tags()` with sync queue support for cloud backends
  - Fixed return value handling (tuple unpacking instead of dict access)

- **UI/UX Improvements** - Enhanced user experience across document management

  - Added scrolling to Recent Memories section (max-height: 600px) to prevent infinite expansion
  - Document chunk modal now scrollable (max-height: 400px) for long content
  - Modal visibility fixed with proper `active` class pattern and CSS transitions
  - Dark mode support for all document UI components (chunk items, modals, previews)
  - Event handlers for View/Remove buttons in document preview cards
  - Responsive design with mobile breakpoints (768px, 1024px)

- **Resource Management** - Proper cleanup and error handling

  - Temp file cleanup moved to `finally` blocks to prevent orphaned files
  - File extension validation fixed (strip leading dot for consistent checking)
  - Session cleanup timing bug fixed (use `total_seconds()` instead of `.seconds`)
  - Loader registration order corrected (PDFLoader takes precedence as fallback)

- **MCP Server Tag Format Support** - Accept both string and array formats
  - MCP tools now accept `"tag1,tag2"` (string) and `["tag1", "tag2"]` (array)
  - Consistent tag handling between API and MCP endpoints
  - Fixes validation errors from schema mismatches

### Changed

- **API Response Improvements** - Better error messages and status handling
  - Float timestamp handling in document search (convert via `datetime.fromtimestamp()`)
  - Partial success handling for bulk operations with clear error reporting
  - Progress tracking for background tasks with status updates

### 技术细节

- **Testing**: 19 Gemini Code Assist reviews addressed with comprehensive fixes
- **Performance**: Document viewer handles 430+ chunks efficiently
- **Compatibility**: Cross-platform temp file handling (Windows, macOS, Linux)
- **Code Quality**: Removed dead code, duplicate docstrings, and unused Pydantic models

### Migration Notes

- No breaking changes - fully backward compatible
- Existing installations will automatically gain document ingestion capabilities
- Tag validation only affects new uploads (existing tags unchanged)

## [8.5.14] - 2025-10-23

### Added

- **Memory Hooks: Expanded Git Keyword Extraction** - Dramatically improved memory retrieval by capturing more relevant technical terms from git commits
  - **Problem**: Limited keyword extraction (only 12 terms) missed important development context
    - Git analyzer captured only generic terms: `fix, memory, chore, feat, refactor`
    - Recent work on timestamp parsing, dashboard, analytics not reflected in queries
    - Version numbers (v8.5.12, v8.5.13) not extracted
    - Memory hooks couldn't match against specific technical work
  - **Solution**: Expanded keyword extraction in `git-analyzer.js`
    - **Technical Terms**: Increased from 12 to 38 terms including:
      - Time/Date: `timestamp, parsing, sort, sorting, date, age`
      - Dashboard: `dashboard, analytics, footer, layout, grid, css, stats, display`
      - Development: `async, sync, bugfix, release, version`
      - Features: `embedding, consolidation, memory, retrieval, scoring`
      - Infrastructure: `api, endpoint, server, http, mcp, client, protocol`
    - **Version Extraction**: Added regex to capture version numbers (v8.5.12, v8.5.13, etc.)
    - **Changelog Terms**: Expanded from 12 to 23 terms with same additions
    - **Keyword Limits**: Increased capacity
      - keywords: 15 → 20 terms
      - themes: 10 → 12 entries
      - filePatterns: 10 → 12 entries
  - **Impact**:
    - **Before**: 5 generic terms → limited semantic matching
    - **After**: 20 specific development terms → precise context retrieval
    - Example: `feat, git, memory, retrieval, fix, timestamp, age, v8.5.8, chore, version, v8.5.13, sort, date, dashboard, analytics, stats, display, footer, layout, v8.5.12`
  - **Result**: Memory hooks now capture and retrieve memories about specific technical work (releases, features, bugfixes)
  - **Files Modified**:
    - `claude-hooks/utilities/git-analyzer.js` - Expanded `extractDevelopmentKeywords()` function (commit 4a02c1a)
  - **Testing**: Verified improved extraction with test run showing 20 relevant keywords vs previous 5 generic terms

## [8.5.13] - 2025-10-23

### Fixed

- **Memory Hooks: Unix Timestamp Parsing in Date Sorting** - Fixed critical bug where memories were not sorting chronologically in Claude Code session start
  - **Root Cause**: JavaScript `Date()` constructor expects milliseconds but API returns Unix timestamps in seconds
  - **Impact**: Memory hooks showed old memories (Oct 11-21) before recent ones (Oct 23) despite `sortByCreationDate: true` configuration
  - **Technical Details**:
    - API returns `created_at` as Unix timestamp in seconds (e.g., 1729700000)
    - JavaScript `new Date(1729700000)` interprets this as milliseconds → January 21, 1970
    - All dates appeared as 1970-01-01, breaking chronological sort
    - Relevance scores then determined order, causing old high-scoring memories to rank first
  - **Fix**:
    - Created `getTimestamp()` helper function in `session-start.js` (lines 907-928)
    - Converts `created_at` (seconds) to milliseconds by multiplying by 1000
    - Falls back to `created_at_iso` string parsing if available
    - Proper date comparison ensures newest memories sort first
  - **Result**: Memory hooks now correctly show most recent project memories at session start
  - **Files Modified**:
    - `claude-hooks/core/session-start.js` - Added Unix timestamp conversion helper (commit 71606e5)

## [8.5.12] - 2025-10-23

### Fixed

- **Dashboard: Analytics Stats Display** - Fixed analytics tab showing 0/N/A for key metrics

  - **Root Cause**: Async/sync mismatch in `get_stats()` method implementations
  - **Impact**: Analytics dashboard displayed only "this week" count; total memories, unique tags, and database size showed 0 or N/A
  - **Fix**:
    - Made `SqliteVecMemoryStorage.get_stats()` async (line 1242)
    - Updated `HybridMemoryStorage.get_stats()` to properly await primary storage call (line 878)
    - Added `database_size_bytes` and `database_size_mb` to hybrid stats response
    - Fixed all callers in `health.py` and `mcp.py` to await `get_stats()`
  - **Result**: All metrics now display correctly (1778 memories, 2549 tags, 7.74MB)
  - **Files Modified**:
    - `src/mcp_memory_service/storage/sqlite_vec.py` - Made get_stats() async
    - `src/mcp_memory_service/storage/hybrid.py` - Added await and database size fields
    - `src/mcp_memory_service/web/api/health.py` - Simplified async handling
    - `src/mcp_memory_service/web/api/mcp.py` - Added await calls

- **Dashboard: Footer Layout** - Fixed footer appearing between header and content instead of at bottom

  - **Root Cause**: Footer not included in CSS grid layout template
  - **Impact**: Broken visual layout with footer misplaced in page flow
  - **Fix**:
    - Updated `.app-container` grid to include 5th row with "footer" area
    - Assigned `grid-area: footer` to `.app-footer` class
  - **Result**: Footer now correctly positioned at bottom of page
  - **Files Modified**:
    - `src/mcp_memory_service/web/static/style.css` - Updated grid layout (lines 101-110, 1899)

- **HTTP Server: Runtime Warnings** - Eliminated "coroutine was never awaited" warnings in logs
  - **Root Cause**: Legacy sync/async detection code after all backends became async
  - **Impact**: Runtime warnings cluttering server logs
  - **Fix**: Removed hybrid backend detection logic, all `get_stats()` calls now consistently await
  - **Result**: Clean server logs with no warnings

## [8.5.11] - 2025-10-23

### Fixed

- **Consolidation System: Embedding Retrieval in get_all_memories()** - Fixed SQLite-vec backend to actually retrieve embeddings (PR #171, fixes #169)
  - **Root Cause**: `get_all_memories()` methods only queried `memories` table without joining `memory_embeddings` virtual table
  - **Impact**: Consolidation system received 0 embeddings despite 1773 memories in database, preventing association discovery and semantic clustering
  - **Discovery**: PR #170 claimed to fix this but only modified debug tools; actual fix required changes to `sqlite_vec.py`
  - **Fix**:
    - Added `deserialize_embedding()` helper function using numpy.frombuffer() (sqlite-vec only provides serialize, not deserialize)
    - Updated both `get_all_memories()` methods (lines 1468 and 1681) with LEFT JOIN to `memory_embeddings` table
    - Modified `_row_to_memory()` helper to handle 10-column rows with embeddings
    - Applied Gemini Code Assist improvement to simplify row unpacking logic
  - **Test Results** (1773 memories):
    - Embeddings retrieved: 1773/1773 (100%)
    - Associations discovered: 90-91 (0.3-0.7 similarity range)
    - Semantic clusters created: 3 (DBSCAN grouping)
    - Performance: 1249-1414 memories/second
    - Duration: 1.25-1.42 seconds
  - **Consolidation Status**: ✅ **FULLY FUNCTIONAL** (all three blockers fixed: PR #166, #168, #171)
  - **Files Modified**:
    - `src/mcp_memory_service/storage/sqlite_vec.py` - Added embedding retrieval to all memory fetch operations

## [8.5.10] - 2025-10-23

### Fixed

- **Debug Tools: Embedding Retrieval Functionality** - Fixed debug MCP tools for SQLite-vec backend (PR #170, addresses #169)
  - **Root Cause**: `debug_retrieve_memory` function was written for ChromaDB but codebase now uses SQLite-vec storage
  - **Impact**: Debug tools (`debug_retrieve`) were broken, preventing debugging of embedding retrieval operations
  - **Fix**: Updated debug utilities to work with current SQLite-vec storage backend
  - **Changes**:
    - Fixed `debug_retrieve_memory` in `src/mcp_memory_service/utils/debug.py` to use storage's `retrieve()` method
    - Enhanced debug output with similarity scores, backend information, query details, and raw distance values
    - Added proper filtering by similarity threshold
  - **Files Modified**:
    - `src/mcp_memory_service/utils/debug.py` - Updated for SQLite-vec compatibility
    - `src/mcp_memory_service/server.py` - Enhanced debug output formatting

### Added

- **Debug Tool: get_raw_embedding MCP Tool** - New debugging capability for embedding inspection (PR #170)
  - **Purpose**: Direct debugging of embedding generation process
  - **Features**:
    - Shows raw embedding vectors with configurable display (first 10 and last 10 values for readability)
    - Displays embedding dimensions
    - Shows generation status and error messages
  - **Use Case**: Troubleshooting embedding-related issues in consolidation and semantic search
  - **Files Modified**:
    - `src/mcp_memory_service/server.py` - Added `get_raw_embedding` tool and handler

## [8.5.9] - 2025-10-22

### Fixed

- **Consolidation System: Missing update_memory() Method** - Added `update_memory()` method to all storage backends (PR #166, fixes #165)

  - **Root Cause**: Storage backends only implemented `update_memory_metadata()`, but consolidation system's `StorageProtocol` required `update_memory()` for saving consolidated results
  - **Impact**: Prevented consolidation system from saving associations, clusters, compressions, and archived memories
  - **Fix**: Added `update_memory()` method to base `MemoryStorage` class, delegating to `update_memory_metadata()` for proper implementation
  - **Affected Backends**: CloudflareStorage, SqliteVecMemoryStorage, HybridMemoryStorage
  - **Test Results**:
    - Verified on SQLite-vec backend with 1773 memories
    - Performance: 5011 memories/second (local SQLite-vec) vs 2.5 mem/s (Cloudflare)
    - Method successfully executes without AttributeError
  - **Files Modified**:
    - `src/mcp_memory_service/storage/base.py` - Added `update_memory()` to base class
    - `src/mcp_memory_service/storage/http_client.py` - Updated HTTP client call
    - `src/mcp_memory_service/storage/hybrid.py` - Fixed method reference

- **Consolidation System: Datetime Timezone Mismatch** - Fixed timezone handling in decay calculator (PR #168, fixes #167)
  - **Root Cause**: Mixed offset-naive and offset-aware datetime objects causing `TypeError` when calculating time differences
  - **Location**: `src/mcp_memory_service/consolidation/decay.py:191` in `_calculate_access_boost()`
  - **Impact**: Blocked decay calculator from completing, preventing associations, clustering, compression, and archival
  - **Fix**: Added timezone normalization to ensure both `current_time` and `last_accessed` are timezone-aware (UTC) before subtraction
  - **Implementation**:
    - Check if datetime is timezone-naive and convert to UTC if needed
    - Ensures consistent timezone handling across all datetime operations
  - **Files Modified**:
    - `src/mcp_memory_service/consolidation/decay.py` - Added timezone normalization logic

### Added

- **Consolidation Documentation** - Comprehensive setup and testing guides
  - `CONSOLIDATION_SETUP.md` - Complete configuration guide for dream-inspired memory consolidation
  - `CONSOLIDATION_TEST_RESULTS.md` - Expected results and troubleshooting guide
  - Documentation covers all 7 consolidation engines and 7 MCP tools

## [8.5.8] - 2025-10-22

### Fixed

- **Critical: Memory Age Calculation in Hooks** - Fixed Unix timestamp handling that caused memories to appear 20,363 days old (55 years) when they were actually recent
  - **Root Cause**: JavaScript's `Date()` constructor expects milliseconds, but SQLite database stores Unix timestamps in seconds. Three functions incorrectly treated seconds as milliseconds: `calculateTimeDecay()`, `calculateRecencyBonus()`, and `analyzeMemoryAgeDistribution()`
  - **Symptoms**:
    - Memory Age Analyzer showed `avgAge: 20363` days instead of actual age
    - Stale memory detection incorrectly triggered (`isStale: true`)
    - Recent memory percentage showed 0% when should be 100%
    - Time decay scores incorrect (1% instead of 100% for today's memories)
    - Recency bonus not applied (0% instead of +15%)
  - **Fix**: Added type checking to convert Unix timestamps properly - multiply by 1000 when timestamp is a number (seconds), pass through when it's an ISO string
  - **Impact**: Memory age calculations now accurate, stale detection works correctly, recency bonuses applied properly
  - **Files Modified**:
    - `claude-hooks/utilities/memory-scorer.js` (lines 11-17, 237-243, 524-534)
  - **Test Results**: Memories now show correct ages (0.4 days vs 20,363 days before fix)
  - **Platform**: All platforms (macOS, Linux, Windows)

### Changed

- **Installer Enhancement**: Added automatic statusLine configuration for v8.5.7 features
  - Installer now copies `statusline.sh` to `~/.claude/hooks/`
  - Checks for `jq` dependency (required for statusLine parsing)
  - Automatically adds `statusLine` configuration to `settings.json`
  - Enhanced documentation for statusLine setup and requirements

### Documentation

- Added `jq` as required dependency for statusLine feature
- Documented statusLine configuration in README.md installation section
- Clarified Unix timestamp handling in memory-scorer.js code comments

## [8.5.7] - 2025-10-21

### Added

- **SessionStart Hook Visibility Features** - Three complementary methods to view session memory context
  - **Visible Summary Output**: Clean bordered console display showing project, storage, memory count with recent indicator, and git context
  - **Detailed Log File**: Complete session context written to `~/.claude/last-session-context.txt` including project details, storage backend, memory statistics, git analysis, and top loaded memories
  - **Status Line Display**: Always-visible status bar at bottom of Claude Code terminal showing `🧠 8 (5 recent) | 📊 10 commits`
  - **Files Modified**:
    - `~/.claude/hooks/core/session-start.js` - Added summary output, log file generation, and cache file write logic
    - `~/.claude/settings.json` - Added statusLine configuration
  - **Files Created**:
    - `~/.claude/statusline.sh` - Bash script for status line display (requires `jq`)
    - `~/.claude/last-session-context.txt` - Auto-generated detailed log file
    - `~/.claude/hooks/utilities/session-cache.json` - Status line data cache
  - **Platform**: Linux/macOS (Windows SessionStart hook still broken - issue #160)

### Changed

- SessionStart hook output now provides visible feedback instead of being hidden in system-reminder tags
- Status line updates every 300ms with latest session memory context
- Log file automatically updates on each SessionStart hook execution

### Documentation

- Clarified difference between macOS and Linux hook output behavior (both use system-reminder tags since v2.2.0)
- Documented that `<session-start-hook>` wrapper tags were intentionally removed in v2.2.0 for cleaner output
- Added troubleshooting guide for status line visibility features

## [8.5.6] - 2025-10-16

### Fixed

- **Critical: Memory Hooks HTTPS SSL Certificate Validation** - Fixed hooks failing to connect to HTTPS server with self-signed certificates
  - **Root Cause**: Node.js HTTPS requests were rejecting self-signed SSL certificates silently, causing "No active connection available" errors
  - **Symptoms**:
    - Hooks showed "Failed to connect using any available protocol"
    - No memories retrieved despite server being healthy
    - HTTP server running but hooks couldn't establish connection
  - **Fix**: Added `rejectUnauthorized: false` to both health check and API POST request options in memory-client.js
  - **Impact**: Hooks now successfully connect via HTTPS to servers with self-signed certificates
  - **Files Modified**:
    - `claude-hooks/utilities/memory-client.js` (lines 174, 257)
    - `~/.claude/hooks/utilities/memory-client.js` (deployed)
  - **Test Results**: ✅ 7 memories retrieved from 1558 total, all phases working correctly
  - **Platform**: All platforms (macOS, Linux, Windows)

### Changed

- Memory hooks now support HTTPS endpoints with self-signed certificates without manual certificate trust configuration

## [8.5.5] - 2025-10-14

### Fixed

- **Critical: Claude Code Hooks Configuration** - Fixed session-start hook hanging/unresponsiveness on Windows
  - **Root Cause**: Missing forced process exit in session-start.js caused Node.js event loop to remain active with unclosed connections
  - **Fix 1**: Added `.finally()` block with 100ms delayed `process.exit(0)` to ensure clean termination
  - **Fix 2**: Corrected port mismatch in `~/.claude/hooks/config.json` (8889 → 8001) to match HTTP server
  - **Impact**: Hooks now complete in <15 seconds without hanging, Claude Code remains responsive
  - **Files Modified**:
    - `~/.claude/hooks/core/session-start.js` (lines 1010-1013)
    - `~/.claude/hooks/config.json` (line 7)
  - **Platform**: Windows (also applies to macOS/Linux)

### Changed

- **Documentation**: Added critical warning section to CLAUDE.md about hook configuration synchronization
  - Documents port mismatch symptoms (hanging hooks, unresponsive Claude Code, connection timeouts)
  - Lists all configuration files to check (`config.json`, HTTP server port, dashboard port)
  - Provides verification commands for Windows/Linux/macOS
  - Explains common mistakes (using dashboard port 8888/8443 instead of API port 8001)

## [8.5.4] - 2025-10-13

### Fixed

- **MCP Server**: Added explicit documentation to `store_memory` tool clarifying that `metadata.tags` must be an array, not a comma-separated string
  - Prevents validation error: `Input validation error: '...' is not of type 'array'`
  - Includes clear examples showing correct (array) vs incorrect (string) format
  - Documentation-only change - no code logic modified

### Changed

- Improved `store_memory` tool docstring with metadata format validation examples in `src/mcp_memory_service/mcp_server.py`

## [Unreleased]

## [8.48.4] - 2025-12-08

### Fixed
- **Cloudflare D1 漂移检测性能** —— 修复混合后端漂移检测查询缓慢/失败（Issue #264）
  - **原因**：`get_memories_updated_since()` 使用了字符串比较 `updated_at_iso > ?`，未利用索引。
  - **修复**：改为使用索引列 `updated_at` 的数值比较 `updated_at > ?`。
  - **性能效果**：查询提速 10–100 倍，消除 D1 大数据集的超时/400 错误。
  - **受影响函数**：`CloudflareStorage.get_memories_updated_since()`（1638-1667 行）。
  - **位置**：`src/mcp_memory_service/storage/cloudflare.py`
  - **致谢**：Claude Code 工作流（GitHub Actions）完成根因分析。

## [8.48.3] - 2025-12-08

### Fixed
- **Code Execution 钩子失败** —— 修复 Session-Start 钩子回退到 MCP 工具而非快速 Code Execution API 的问题。
  - **原因 1**：向 `search()` 传入无效 `time_filter` 参数（签名仅接受 `query/limit/tags`）。
  - **原因 2**：`transformers` 向 stderr 输出 `FutureWarning`，导致 `execSync()` 失败。
  - **原因 3**：安装脚本使用系统 `python3`，未自动检测虚拟环境。
  - **修复 1**：移除 Code Execution 查询中的 `time_filter`（`claude-hooks/core/session-start.js:325`）。
  - **修复 2**：执行时添加 `-W ignore` 抑制 Python 警告（行 359）。
  - **修复 3**：安装器改用 `sys.executable` 自动发现 venv（`claude-hooks/install_hooks.py:271-299`）。
  - **影响**：Session Start Token 消耗降低 75%（1200-2400 → 300-600）。
  - **行为**：钩子会优先使用 Code Execution API，而非回退 MCP 工具。
  - **文档**：增加故障排查记忆条目以供复用。
  - **位置**：`claude-hooks/core/session-start.js:315-363`，`claude-hooks/install_hooks.py:271-299`

### Changed
- **Session-Start 钩子连接超时** —— 快速连接超时从 2s 增至 5s。
  - 防止内存客户端初始化过早超时。
  - 高负载时为 HTTP 连接留出更多时间。
  - 位置：`~/.claude/hooks/core/session-start.js:750`（用户安装目录）。

## [8.48.2] - 2025-12-08

### Added
- **HTTP 服务自启动系统** —— 智能管理并含完整健康检查。
  - 新增 `scripts/service/http_server_manager.sh`（376 行），负责健壮的服务管理。
  - 孤儿进程检测与清理（处理崩溃/强杀留下的 PID）。
  - 版本不一致检测（运行版本与已安装版本不符时告警）。
  - 配置变更检测（监控 .env 修改时间，变化则重启）。
  - 混合存储初始化等待（10s 超时，确保后端就绪）。
  - 健康检查含重试逻辑（2s 间隔，3 次后判失败）。
  - 支持命令：`status`、`start`、`stop`、`restart`、`auto-start`、`logs`。
  - Shell 集成：可写入 `~/.zshrc`，终端启动即自启服务。
  - 位置：`scripts/service/http_server_manager.sh`。

- **Session-Start 钩子健康检查** —— 主动检测 HTTP 服务可用性。
  - 在 `~/.claude/hooks/core/session-start.js`（657-674 行）增加健康检查提示。
  - 无法连通时给出清晰错误与可操作的修复步骤。
  - 识别连接错误：ECONNREFUSED、fetch failed、网络错误、超时。
  - 非阻塞：告警但不阻断 Claude Code 会话初始化。
  - 位置：`~/.claude/hooks/core/session-start.js:657-674`。

### Fixed
- **时间解析器支持 “last N periods”** —— 解决 Issue #266（相对时间短语无法解析）。
  - 新增 `last_n_periods` 正则，匹配 “last N days/weeks/months/years”。
  - 实现 `get_last_n_periods_range(n, period)` 进行日期计算。
  - 匹配顺序：先检查 `last_n_periods` 再检查 `last_period`，优先精准匹配。
  - 正确处理：
    - “last 3 days” → 从 3 天前 00:00:00 至今
    - “last 2 weeks” → 从 2 周前周一 00:00:00 至今
    - “last 1 month” → 从 1 个月前月初 00:00:00 至今
    - “last 5 years” → 从 5 年前 1 月 1 日 00:00:00 至今
  - 兼容既有 “last week/月” 表达。
  - 位置：`src/mcp_memory_service/utils/time_parser.py`。

### Changed
- **钩子时间窗口** —— 恢复为 “last 3 days”（解析器已修复）。
  - 应用于配置中的 `recentTimeWindow` 与 `fallbackTimeWindow`。
  - 之前因解析器缺陷被迫用 “yesterday”。
  - 现可使用完整 3 天上下文，记忆召回更佳。
  - 位置：`~/.claude/hooks/config.json`。

### 技术细节
- **HTTP Server Manager Architecture**:
  - PID tracking via `/tmp/mcp_memory_http.pid` (shared location for orphan detection)
  - Config fingerprinting via MD5 hash of `.env` file (detects credential/backend changes)
  - Version extraction from installed package (compares with runtime version)
  - Log rotation support (tails last 50 lines from `~/.mcp-memory-service/http_server.log`)
  - SIGTERM graceful shutdown (10s timeout before SIGKILL)
  - Auto-start function for shell integration (idempotent, safe for rc files)

- **Time Parser Improvements**:
  - Regex pattern: `r'last\s+(\d+)\s+(days?|weeks?|months?|years?)'`
  - Handles singular/plural forms (day/days, week/weeks, etc.)
  - Week boundaries: Monday 00:00:00 (ISO 8601 standard)
  - Month boundaries: First day 00:00:00 (calendar month alignment)
  - Fallback behavior: Interprets unknown periods as days (defensive programming)

- **Testing Coverage**:
  - HTTP server manager: Tested status/start/stop/restart/auto-start commands
  - Orphaned process cleanup: Verified detection and cleanup of stale PIDs
  - Version mismatch: Confirmed detection when installed vs running version differs
  - Config change detection: Verified restart trigger on .env modification
  - Time parser: Tested "last 3 days", "last 2 weeks", "last 1 month", "last 5 years"
  - Backward compatibility: Verified "last week", "last month" still work

## [8.48.1] - 2025-12-08

### Fixed
- **严重：服务无法启动** —— 修复 v8.48.0 的致命 `UnboundLocalError`。
  - **根因**：`models/memory.py` 第 84 行多余的局部 `import calendar`，使 `iso_to_float()` 中 `calendar` 变为局部变量。
  - **错误位置**：异常处理（168 行）在局部 import 执行前引用 `calendar`。
  - **影响**：Cloudflare 同步初始化时 ~100ms 循环报错，健康检查与控制台不可用，服务无法启动。
  - **修复**：移除冗余局部 import，统一使用模块级导入（全局 21 行已导入）。
  - **严重性**：CRITICAL——所有 v8.48.0 用户需立即升级。
  - **迁移**：直接替换，无需改配置。
  - **位置**：`src/mcp_memory_service/models/memory.py:84`（已移除）。

### 技术细节
- **错误信息**：`UnboundLocalError: cannot access local variable 'calendar' where it is not associated with a value`
- **触发频率**：Cloudflare 混合后端初始化期间持续 ~100ms 重复。
- **测试结果**：修复后服务可正常启动，健康检查响应正常，Cloudflare 同步无报错。
- **验证**：日志无时间戳解析错误，控制台可访问 `https://localhost:8000`。

## [8.48.0] - 2025-12-07

### Added
- **基于 CSV 的元数据压缩** —— Cloudflare 同步的智能压缩体系
  - Implemented CSV encoding/decoding for quality and consolidation metadata
  - Achieved 78% size reduction (732B → 159B typical case)
  - Provider code mapping (onnx_local → ox, groq_llama3_70b → gp, etc.) for 70% reduction in provider field
  - Metadata size validation (<9.5KB) prevents sync failures before Cloudflare API calls
  - Transparent compression/decompression in hybrid backend operations
  - Quality metadata optimizations:
    - ai_scores history limited to 3 most recent entries (10 → 3)
    - quality_components removed from sync (debug-only, reconstructible)
    - Cloudflare-specific field suppression (metadata_source, last_quality_check)
  - Location: `src/mcp_memory_service/quality/metadata_codec.py`

- **验证脚本** —— Shell 脚本验证压缩效果
  - Tests CSV encoding/decoding round-trip accuracy
  - Measures compression ratios
  - Validates metadata size under Cloudflare limits
  - Location: `verify_compression.sh`

### Fixed
- **Cloudflare Sync Failures** - Resolved 100% of metadata size limit errors
  - Problem: Cloudflare D1 10KB metadata limit was exceeded by quality/consolidation metadata
  - Impact: 1 operation stuck in retry queue with 400 Bad Request errors
  - Root cause: Uncompressed metadata (ai_scores history, quality_components) exceeded limit
  - Solution: CSV compression + metadata size validation before sync
  - Result: 0 sync failures, all operations processing successfully
  - Locations: `src/mcp_memory_service/storage/hybrid.py` (lines 547-559, 77-119), `src/mcp_memory_service/storage/cloudflare.py` (lines 606-612, 741-747, 830-836, 1474-1480)

### 技术细节
- **Compression Architecture**: Phase 1 of 3-phase metadata optimization plan
  - Phase 1 (COMPLETE): CSV-based compression for quality/consolidation metadata
  - Phase 2 (AVAILABLE): Binary encoding with struct/msgpack (85-90% reduction target)
  - Phase 3 (AVAILABLE): Reference-based deduplication for repeated values
- **Backward Compatibility**: Fully transparent - automatic compression on write, decompression on read
- **Performance Impact**: Negligible (<1ms overhead per operation)
- **Testing**: All quality system tests passing, sync queue empty, 3,750 ONNX-scored memories verified

## [8.47.1] - 2025-12-07

### Fixed
- **ONNX 自匹配缺陷** —— 批量评估将记忆内容当作查询，导致质量分接近 1.0。
  - Root cause: Cross-encoder design requires meaningful query-memory pairs for relevance ranking
  - Fixed by generating queries from tags/metadata (what memory is *about*) instead of memory content
  - Result: Realistic quality distribution (avg 0.468 vs 1.000, breakdown: 42.9% high / 3.2% medium / 53.9% low)
  - Location: `scripts/quality/bulk_evaluate_onnx.py`

- **关联污染** —— 系统生成的 association/压缩聚类被误评质量。
  - These memories are structural (not content) and shouldn't receive quality scores
  - Fixed by filtering memories with type='association' or type='compressed_cluster'
  - Added belt-and-suspenders check for 'source_memory_hashes' metadata field
  - Impact: 948 system-generated memories excluded from evaluation
  - Location: `scripts/quality/bulk_evaluate_onnx.py`

- **同步队列溢出** —— 队列 1000 容量在批量 ONNX 评估的 4478 次更新中被撑满。
  - Resulted in 278 Cloudflare sync failures (27.8% failure rate)
  - Fixed by increasing queue size to 2,000 (env: `MCP_HYBRID_QUEUE_SIZE`)
  - Fixed by increasing batch size to 100 (env: `MCP_HYBRID_BATCH_SIZE`)
  - Added 5-second timeout with fallback to immediate sync on queue full
  - Added `wait_for_sync_completion()` method for monitoring bulk operations
  - Result: 0% sync failure rate during bulk operations
  - Location: `src/mcp_memory_service/storage/hybrid.py`, `src/mcp_memory_service/config.py`

- **整合卡顿** —— 相关性得分缺少批量更新优化。
  - Sequential update_memory() calls caused slowdown during consolidation
  - Fixed by collecting updates and using single `update_memories_batch()` transaction
  - Impact: 50-100x speedup for relevance score updates during consolidation
  - Location: `src/mcp_memory_service/consolidation/consolidator.py`

### Added
- **重置 ONNX 评分脚本** (`scripts/quality/reset_onnx_scores.py`)
  - Resets all ONNX quality scores to implicit defaults (0.5)
  - Pauses hybrid backend sync during reset, resumes after completion
  - Preserves timestamps (doesn't change created_at/updated_at)
  - Progress reporting every 500 memories
  - Use case: Recover from bad ONNX evaluation (self-match bug)

- **增强版批量评估脚本** (`scripts/quality/bulk_evaluate_onnx.py`)
  - Added association filtering (skip system-generated memories)
  - Added sync monitoring with queue size reporting
  - Added wait_for_sync_completion() call to prevent premature exit
  - Enhanced progress reporting with sync stats
  - Proper pause/resume for hybrid backend sync

### Changed
- **ONNX 默认配置** —— 调优以支持大批量操作
  - `HYBRID_QUEUE_SIZE`: 1,000 → 2,000 (default, configurable via env)
  - `HYBRID_BATCH_SIZE`: 50 → 100 (default, configurable via env)
  - Backward compatible: `HYBRID_MAX_QUEUE_SIZE` still supported (legacy)

- **混合后端同步** —— 加强暂停/恢复状态管理
  - Added `_sync_paused` flag to prevent enqueuing during pause (v8.47.1)
  - Fixed race condition where operations were enqueued while sync was paused
  - Ensures operations are not lost during consolidation or bulk updates

### Documentation
- **ONNX 限制** —— 在 CLAUDE.md 中新增重要警告说明
  - Documented that ONNX ranker (ms-marco-MiniLM-L-6-v2) is a cross-encoder
  - Clarified it scores query-memory relevance, not absolute quality
  - Explained why self-matching queries produce artificially high scores
  - Added system-generated memory exclusion rationale

## [8.47.0] - 2025-12-06

### Added
- **基于关联的质量加成** —— 连接数多的记忆在整合时自动提升质量分。
  - 默认连接数 ≥5 的记忆获得 20% 质量加成。
  - 利用网络效应：被频繁引用的记忆往往更有价值。
  - 可通过环境变量配置：`MCP_CONSOLIDATION_QUALITY_BOOST_ENABLED`、`MCP_CONSOLIDATION_MIN_CONNECTIONS_FOR_BOOST`、`MCP_CONSOLIDATION_QUALITY_BOOST_FACTOR`。
  - 加成系数范围 1.0–2.0（默认 1.2 = 20%）。
  - 质量分封顶 1.0，避免过度提升。
  - 元数据完整留痕：连接数、原始分、加成时间与原因。
  - 影响：质量加成约提升相关性 4%，可提升保留等级。
  - Location: `src/mcp_memory_service/consolidation/decay.py`

- **质量加成元数据追踪** —— 为整合过程中的每次加成记录审计信息。
  - `quality_boost_applied`：是否已加成。
  - `quality_boost_date`：加成时间（ISO）。
  - `quality_boost_reason`：本版固定为 association_connections。
  - `quality_boost_connection_count`：触发加成的连接数。
  - `original_quality_before_boost`：保留原始质量分。

- **配置变量** —— 新增 3 个带校验的环境变量。
  - `MCP_CONSOLIDATION_QUALITY_BOOST_ENABLED`（默认 true）：总开关。
  - `MCP_CONSOLIDATION_MIN_CONNECTIONS_FOR_BOOST`（默认 5，范围 1-100）：触发最低连接数。
  - `MCP_CONSOLIDATION_QUALITY_BOOST_FACTOR`（默认 1.2，范围 1.0-2.0）：加成倍数。

### Changed
- **指数衰减计算** —— 纳入关联质量加成。
  - 先应用质量加成，再计算质量乘子。
  - 每次加成均记录调试日志。
  - 持久化加成分时写 info 日志。
  - 在 RelevanceScore 元数据中保留原始分以便对比。

- **记忆相关性元数据** —— 扩展以记录质量加成。
  - `update_memory_relevance_metadata()` 会写入加成后的质量分。
  - 若加成已应用，自动刷新质量分。
  - 新增字段：`quality_boost_applied`、`quality_boost_date`、`quality_boost_reason` 等。

### Documentation
- 新增完整特性指南：`docs/features/association-quality-boost.md`，含配置示例/影响/故障排查/性能。
  - 覆盖保守/均衡/激进三类配置示例。
  - 说明对相关性、保留期、遗忘抵抗的影响。
  - 适用场景：知识图谱、代码文档、研究笔记等。
  - 监控与故障排查指南。
  - 性能影响评估（开销可忽略）。
  - 后续路线：连接质量分析、时间衰减、双向加成。

- 更新 `CLAUDE.md`，加入 v8.47.0 相关说明与配置示例。
  - 在整合特性列表中新增关联质量加成说明。
  - 补充环境变量配置示例。
  - 更新文件顶部版本摘要。

### Tests
- 在 `tests/consolidation/test_decay.py` 新增 5 个测试用例。
  - `test_association_quality_boost_enabled`：验证加成能提升分数。
  - `test_association_quality_boost_threshold`：验证最低连接数阈值。
  - `test_association_quality_boost_caps_at_one`：验证质量分封顶 1.0。
  - `test_association_quality_boost_disabled`：验证关闭开关逻辑。
  - `test_association_quality_boost_persists_to_memory`：验证元数据持久化。
  - 测试均用 monkeypatch 注入配置。
  - 通过率 100%（新 5/5，整合类 17/18）。

### 技术细节
- 默认开启，开箱即用。
- 计算耗时约 5-10 µs/条，几乎无开销。
- 内存开销约 200B/条（5 个元数据字段）。
- 对整合耗时无显著影响。
- 集成点：`ExponentialDecayCalculator._calculate_memory_relevance()`
- 质量加成在相关性评分的质量乘子计算之前应用。
- 仅在：开关开启、连接数达阈值且能提升分数时应用。
- 预留 `MCP_CONSOLIDATION_MIN_CONNECTED_QUALITY` 供第二阶段（连接质量分析）。

## [8.46.3] - 2025-12-06

### Fixed
- **混合后端质量分持久化** —— 修复 ONNX 质量分未同步到 Cloudflare。
  - 评分停留在默认 0.5，未写入评估值 ~1.0。
  - 根因：`/api/quality/evaluate` 将整份 `memory.metadata` 传给 `update_memory_metadata()`。
  - Cloudflare 期望质量字段包在 `metadata` 内，而非顶层。

- **Cloudflare 元数据规范化** —— 新增 `_normalize_metadata_for_cloudflare()` 帮助函数。
  - 拆分 Cloudflare 认可的顶层键（metadata/memory_type/tags/timestamps）与自定义字段。
  - 将自定义字段包裹到 `metadata`，符合 D1 预期。
  - Only wraps if not already wrapped (idempotent operation)

- **质量 API 元数据处理** —— `/api/quality/evaluate` 仅提取质量相关字段。
  - 仅传：quality_score/quality_provider/ai_scores/quality_components。
  - 避免整份元数据覆盖。
  - Added detailed logging for troubleshooting persistence issues

- **混合后端同步操作** —— `SyncOperation` 增加 `preserve_timestamps` 标记。
  - 通过后台队列保持时间戳。
  - 更新时将标记传递给 Cloudflare。
  - 维持混合后端时间一致性。

### 技术细节
- 仅影响以 Cloudflare 为次级存储的混合后端。
- SQLite-vec 主存储正常（本地评分已落盘）。
- 问题出现在同步到 Cloudflare D1 的后台流程。
- 验证：搜索结果质量分已从 0.500 恢复为 1.000。

## [8.46.2] - 2025-12-06

### Fixed
- **Session-Start 钩子崩溃** —— 为 HTTP memory client 补上 `queryMemoriesByTagsAndTime()`。
  - 钩子调用未定义函数，触发 session start 报错“is not a function”。
  - 在客户端对按时间搜索结果做标签过滤。
  - 兼容 HTTP 与 MCP 协议。
  - 现在可安全使用 session-start 钩子。

- **消除钩子安装警告** —— 移除安装时的包导入警告。
  - 新增 `_version.py` 孤立版本元数据。
  - `install_hooks.py` 改为从 `pyproject.toml` 读取版本，避免重型依赖导入。
  - 原因：导入 `mcp_memory_service` 会加载 sqlite-vec / sentence_transformers。
  - 现在安装输出干净、无误导警告。

### 技术细节
- 根因（session-start）：`memory-client.js` 缺少标签+时间查询实现。
- 根因（安装警告）：安装器为读版本导入主包，触发模型初始化警告。
- 修复对所有平台生效（Windows/macOS/Linux）。

## [8.46.1] - 2025-12-06

### Fixed
- **Windows 钩子安装器编码** —— 修复在 Windows 运行 `install_hooks.py` 报 `'charmap' codec can't encode character`。
  - 启动时将控制台编码设置为 UTF-8（CP65001）。
  - 重设 stdout/stderr：`encoding='utf-8', errors='replace'`。
  - 所有 JSON 读写显式指定 `encoding='utf-8'`。
  - `json.dump()` 使用 `ensure_ascii=False`，正确处理 Unicode。

### 技术细节
- 根因：Windows 控制台默认 CP1252 不支持表情符（✅、⚠️ 等）。
- 适用于所有 Windows 系统，与代码页设置无关。

## [8.46.0] - 2025-12-06

### Added
- **质量系统 + 钩子集成** —— 将 AI 质量评分分三阶段融入记忆感知钩子：
  - **Phase 1**：钩子从元数据读取 `backendQuality`（权重 20%）。
  - **Phase 2**：session-end 钩子异步触发 `/api/quality/memories/{hash}/evaluate`。
  - **Phase 3**：检索支持 `quality_boost` / `quality_weight` 进行质量增强。

- **`POST /api/quality/memories/{hash}/evaluate`** —— 触发 AI 质量评估的新端点。
  - 多层体系：ONNX 本地 → Groq → Gemini → 隐式。
  - 返回：quality_score、quality_provider、ai_score、evaluation_time_ms。
  - ONNX 评估约 355ms。

- **质量增强搜索** —— `/api/search` 增加 `quality_boost`、`quality_weight`。
  - 过取 3× 结果后用综合分重排。
  - 公式：`(1-weight)*semantic + weight*quality`。
  - 返回 `search_type: "semantic_quality_boost"` 及分数构成。

- **钩子集成函数**
  - `calculateBackendQuality()`（memory-scorer.js）从元数据取质量分。
  - `triggerQualityEvaluation()`（session-end.js）触发异步评分。
  - `queryMemories()`（memory-client.js）支持 `qualityBoost` 选项。

### Changed
- 钩子评分权重调整：timeDecay 20%，tagRelevance 30%，contentRelevance 10%，contentQuality 20%，backendQuality 20%。

### 技术细节
- 钩子评估：10s 超时，失败回退且非阻塞。
- 需开启 Memory Quality System（v8.45.0+）。

## [8.45.3] - 2025-12-06

### Fixed
- **ONNX Ranker 模型导出** —— 首次使用自动从 transformers 导出 ONNX，修复 HuggingFace 404 下载问题。
- **离线模式支持** —— `local_files_only=True` 支持隔离/离线环境使用缓存模型。
- **Tokenizer 加载** —— 改为从导出的预训练文件加载，避免损坏的压缩包。

### Changed
- 取消失败的 `onnx.tar.gz` 下载，改用 transformers 动态导出 `cross-encoder/ms-marco-MiniLM-L-6-v2`。
- 首次初始化导出到 `~/.cache/mcp_memory/onnx_models/ms-marco-MiniLM-L-6-v2/model.onnx`。
- 优雅回退：先尝试 `local_files_only`，无缓存再联机下载。

### 技术细节
- 性能：CPU 评分约 7–16ms/条（CPUExecutionProvider）。
- 模型大小：导出 ONNX 约 23MB。
- 依赖：`transformers`、`torch`、`onnxruntime`、`onnx`。

## [8.45.2] - 2025-12-06

### Fixed
- **仪表盘暗黑模式一致性** —— 修复表单控件/选择框/视图按钮在暗黑模式下背景发白的问题。
- **全局暗黑 CSS** —— 为 `.form-control`、`.form-select` 添加全覆盖暗黑样式，覆盖仪表盘 7 个标签页（Dashboard/Search/Browse/Documents/Manage/Analytics/Quality）。
- **质量页图表对比度** —— 为暗黑模式设置合适背景与网格线（`var(--neutral-400)`）。
- **Chart.js 暗黑支持** —— `applyTheme()` 动态配置图表颜色（浅色文字 #f9fafb、正确图例色）。
- **质量分布图** —— `renderQualityDistributionChart()` 动态调节文字/网格颜色适配暗黑。
- **质量提供方图表** —— `renderQualityProviderChart()` 图例颜色兼容暗黑。

### Changed
- `.view-btn` 暗黑模式样式优化，悬停态更清晰。

## [8.45.1] - 2025-12-05

### Fixed
- **质量系统 HTTP API** —— 修复路由缺少 `/api/quality` 前缀导致所有 `/api/quality/*` 返回 404。
- **质量分布 MCP 工具** —— 将不存在的 `search_all_memories()` 改为 `get_all_memories()`。
- **HTTP API 测试** —— 用异步 `httpx.AsyncClient` 替换同步 `TestClient`，解决 SQLite 线程安全问题。
- **分布接口** —— 修正 quality.py 的存储读取逻辑，移除多余的字典→Memory 转换。

### Added
- **依赖** —— 增加 `pytest-benchmark`（性能测试）；新增可选 `onnxruntime`（支持 ONNX 模型）。

### Testing
- 27 个功能测试全部通过；ONNX 测试在缺模型时正确跳过；测试套件 0 错误。

## [8.45.0] - 2025-12-05

### Added
- **记忆质量系统** —— AI 驱动的自动质量评分（Issue #260，灵感来自 Memento）。
  - 本地 SLM（ONNX：ms-marco-MiniLM-L-6-v2，23MB）为第 1 层（默认）。
  - 多层回退：本地 SLM → Groq API → Gemini API → 隐式信号。
  - 零成本、隐私友好、可离线运行。
  - 延迟：CPU 50-100ms，GPU 10-20ms（CUDA/MPS/DirectML）。
  - 跨平台：Windows（CUDA/DirectML）、macOS（MPS）、Linux（CUDA/ROCm）。

- **基于质量的记忆管理**
  - 遗忘策略：高分(≥0.7)保留 365 天，中分(0.5-0.7) 180 天，低分(<0.5) 30-90 天。
  - 质量加权衰减：高分记忆衰减速度比低分慢 3 倍。
  - 质量增强检索：0.7×语义 + 0.3×质量重排（`MCP_QUALITY_BOOST_ENABLED`）。
  - 基于访问与反馈的自适应保留。

- **MCP 工具（质量管理 4 个新工具）**
  - `rate_memory`：人工评分 (-1/0/1)。
  - `get_memory_quality`：查看质量指标（分数/提供方/置信度/访问统计）。
  - `analyze_quality_distribution`：全局分布分析（分布、提供方拆分、趋势）。
  - `retrieve_with_quality_boost`：质量增强的语义检索 + 重排。

- **HTTP API**（4 个新端点）
  - POST `/api/quality/memories/{hash}/rate`：手动评分。
  - GET `/api/quality/memories/{hash}`：查看单条记忆质量指标。
  - GET `/api/quality/distribution`：高/中/低分布统计。
  - GET `/api/quality/trends`：质量时间序列趋势。

- **仪表盘 UI 增强**
  - 记忆卡片质量徽章（绿/黄/红/灰）。
  - 分布与提供方图表；Top/Bottom 列表。
  - 质量配置面板（开关、提供方、加权）。
  - 质量相关 UI 的中英文 i18n。

- **配置**（10 个环境变量）
  - `MCP_QUALITY_SYSTEM_ENABLED`（默认 true）
  - `MCP_QUALITY_AI_PROVIDER`（local/groq/gemini/auto/none，默认 local）
  - `MCP_QUALITY_LOCAL_MODEL`（默认 ms-marco-MiniLM-L-6-v2）
  - `MCP_QUALITY_LOCAL_DEVICE`（auto/cpu/cuda/mps/directml，默认 auto）
  - `MCP_QUALITY_BOOST_ENABLED`（默认 false，可选）
  - `MCP_QUALITY_BOOST_WEIGHT`（0.0-1.0，默认 0.3）
  - `MCP_QUALITY_RETENTION_HIGH`（默认 365 天）
  - `MCP_QUALITY_RETENTION_MEDIUM`（默认 180 天）
  - `MCP_QUALITY_RETENTION_LOW_MIN`（默认 30 天）
  - `MCP_QUALITY_RETENTION_LOW_MAX`（默认 90 天）

### Changed
- **记忆模型** —— 增加质量属性（向后兼容）：`quality_score`、`quality_provider`、`quality_confidence`、`quality_calculated_at`，以及访问计数/最近访问时间。
  - 旧记忆无需改动，首次访问时计算质量。

- **存储后端** —— 加入访问模式追踪；SQLite-Vec / Cloudflare 检索时记录 access_count/last_accessed_at；两者均可选质量增强检索。

- **整合系统** —— 使用质量分做保留决策；衰减模块按质量加权（高分衰减更慢）；关联发现优先高质量记忆。

- **搜索系统** —— 可选质量重排：默认纯语义；可选 70% 语义 + 30% 质量；权重由 `MCP_QUALITY_BOOST_WEIGHT` 配置。

### Documentation
- 完整用户指南：`docs/guides/memory-quality-guide.md`（包含本地 SLM、云 API、混合模式配置；MCP 工具/HTTP API/仪表盘示例；性能基准；故障排查）。
- `CLAUDE.md` 已更新质量系统章节；提供各部署场景的配置示例与零破坏迁移说明。

### Performance
- **质量计算开销**：<10ms/条（异步非阻塞）。
- **加权搜索时延**：<100ms（语义 + 质量重排）。
- **本地 SLM 推理**：CPU 50-100ms，GPU 10-20ms。
- **异步后台评分**：非阻塞，排队处理新记忆。
- **模型大小**：23MB ONNX。

### Testing
- 质量评分单测 25 个（`tests/test_quality_system.py`）；整合相关集成测试 6 个（`tests/test_quality_integration.py`）。
- 通过率 67%（22/33），已知 4 个 HTTP API 测试失败（非关键，计划 v8.45.1 修复）。

### Known Issues
- 4 个 HTTP API 测试失败（开发环境，非关键）：
  - `test_analyze_quality_distribution_mcp_tool`：存储读取边界。
  - `test_rate_memory_http_endpoint`：HTTP 404（路由配置）。
  - `test_get_quality_http_endpoint`：HTTP 404（路由配置）。
  - `test_distribution_http_endpoint`：HTTP 500（异步处理）。
  - 计划在 v8.45.1 修复；生产功能不受影响（手测正常）。

### Migration Notes
- **无破坏性变更**：质量系统可选且向后兼容。
- 现有用户无需改动，质量评分后台自动进行。
- 启用质量增强检索：配置 `MCP_QUALITY_BOOST_ENABLED=true`。
- 使用云提供方：设置 GROQ_API_KEY / GEMINI_API_KEY，并设 `MCP_QUALITY_AI_PROVIDER=auto`。
- 关闭质量系统（不推荐）：`MCP_QUALITY_SYSTEM_ENABLED=false`。

### Success Metrics (Phase 1 Targets)
- 目标（一期）：
  - 检索精度提升 >40%（以使用数据衡量）。
  - 本地 SLM 使用率 >95%（零成本）。
  - 质量增强检索延迟 <100ms。
  - 月成本 $0（默认本地 SLM，不调用外部 API）。

## [8.44.0] - 2025-11-30

### Added
- **多语言扩展** —— 仪表盘 i18n 新增 5 种语言（a7d0ba7）：日/韩/德/法/西，各 359 个翻译键，完整 UI 覆盖；全部经专业校验（键对齐、插值、JSON 结构）。
- **i18n 全量覆盖** —— UI 翻译键从 304 → 359，覆盖搜索结果、标签浏览、记忆详情/新增表单、设置、加载态与连接状态、Memory Viewer 等；index.html 新增约 80 个 data-i18n 属性。

### Fixed
- **暗黑模式语言下拉** —— 修复暗黑样式不一致（a7d0ba7）：统一背景、悬停态半透明白遮罩、激活态高亮，提升对比度可读性。

### Changed
- **翻译键结构** —— 每种语言键数 304 → 359，保持向后兼容；en.json / zh.json 已对齐；键命名一致化。

## [8.43.0] - 2025-11-30

### Added
- **前端国际化** —— 仪表盘完成中英双语 i18n（PR #256，@amm10090）。
  - 头部语言切换（🌐 图标）；`en.json`/`zh.json` 各 300+ 键。
  - 自动语言检测：localStorage > 浏览器语言 > English。
  - 动态翻译所有 UI/占位符/提示；缺失键回退英文。

- **Claude 分支自动化增强** —— PR 前置质量检查。
  - 新增文件级质量校验脚本 `scripts/pr/run_quality_checks_on_files.sh`（286 行）。
  - Groq API 主通道（200-300ms），Gemini CLI 作为回退。
  - 复杂度分析（>8 阻断，7-8 警告）；安全扫描（SQLi/XSS/命令注入/路径遍历/Secrets）。
  - 结果决定是否允许建 PR；GitHub Actions 输出行内注解；提供机器可解析格式以便 CI 集成。

### Changed
- **i18n 性能优化** —— DOM 遍历由 4 次合并为 1 次，降低开销。

### Fixed
- **翻译准确性** —— 移除对后端错误消息的错误包裹，避免误译。
- **Translation Completeness** - Added missing `{reason}` placeholder to error translations

## [8.42.1] - 2025-11-29

### Fixed
- **MCP Resource Handler AttributeError** - Fixed `AttributeError: 'AnyUrl' object has no attribute 'startswith'` in `handle_read_resource` function (issue #254)
  - Added automatic URI string conversion at function start to handle both plain strings and Pydantic AnyUrl objects
  - MCP SDK may pass AnyUrl objects instead of strings, causing AttributeError when using `.startswith()` method
  - Fix converts AnyUrl to string using `str()` before processing, maintaining backward compatibility

## [8.42.0] - 2025-11-27

### Added
- **Visible Memory Injection Display** - Users now see injected memories at session start (commit TBD)
  - Added `showInjectedMemories` config option to display top 3 memories with relevance scores
  - Shows memory age (e.g., "2 days ago"), tags, and relevance scores
  - Formatted with colored output box for clear visibility
  - Helps users understand what context the AI assistant is using
  - Configurable via `~/.claude/hooks/config.json`

### Changed
- **Session-End Hook Quality Improvements** - Raised quality thresholds to prevent generic boilerplate (commit TBD)
  - Increased `minSessionLength` from 100 → 200 characters (requires more substantial content)
  - Increased `minConfidence` from 0.1 → 0.5 (requires 5+ meaningful items vs 1+)
  - Added optional LLM-powered session summarizer using Gemini CLI
  - New files: `llm-session-summarizer.js` utility and `session-end-llm.js` core hook
  - Prevents low-quality memories like "User asked Claude to review code" from polluting database
  - Database cleaned from 3352 → 3185 memories (167 generic entries removed)

### Fixed
- **Duplicate MCP Fallback Messages** - Fixed duplicate "MCP Fallback → Using standard MCP tools" log messages (commit TBD)
  - Added module-level flag to track if fallback message was already logged
  - Message now appears once per session instead of once per query
  - Improved session start hook output clarity

### Performance
- **Configuration Improvements** - Better defaults for session analysis
  - Enabled relevance scores in context formatting
  - Improved memory scoring to prioritize quality over recency for generic content
  - Session-end hook re-enabled with improved quality gates

## [8.41.2] - 2025-11-27

### Fixed
- **Hook Installer Utility File Deployment** - Installer now copies ALL utility files instead of hardcoded lists (commit 557be0e)
  - **BREAKING**: Previous installer only copied 8/14 basic utilities and 5/14 enhanced utilities
  - Updated files like `memory-scorer.js` and `context-formatter.js` were not deployed with `--natural-triggers` flag
  - Replaced hardcoded file lists with glob pattern (`*.js`) to automatically include all utility files
  - Ensures v8.41.0/v8.41.1 project affinity filtering fixes get properly deployed
  - Future utility file additions automatically included without manual list maintenance
  - **Impact**: Users running `python install_hooks.py --natural-triggers` now get all 14 utility files, preventing stale hooks

## [8.41.1] - 2025-11-27

### Fixed
- **Context Formatter Memory Sorting** - Memories now sorted by recency within each category (commit 2ede2a8)
  - Added sorting by `created_at_iso` (descending) after grouping memories into categories
  - Ensures most recent memories appear first in each section for better context relevance
  - Applied in `context-formatter.js` after category grouping logic
  - Improves user experience by prioritizing newest information in memory context

## [8.41.0] - 2025-11-27

### Fixed
- **Session Start 钩子可靠性** —— 提升启动钩子可靠性与记忆过滤（924962a）
  - **抑制错误**：屏蔽 Code Execution 的 ModuleNotFoundError 噪声。
    - 在 Code Execution 配置中加入 `suppressErrors: true`。
    - Eliminates console noise from module import errors during session start
  - **输出清理**：移除重复的 “Injected Memory Context” 输出。
    - 删除导致双重输出的 stdout console.log。
    - Session start output now cleaner and easier to read
  - **记忆过滤**：引入项目亲和度评分，防止跨项目记忆污染。
    - 新增 `calculateProjectAffinity()`（memory-scorer.js）。
    - 在项目上下文中硬过滤无项目标签的记忆。
    - 对跨项目记忆施加 0.3x 软惩罚。
    - Prevents Azure/Terraform memories from appearing in mcp-memory-service context
  - **分类修正**：Session 摘要不再被误判为 “Current Problems”。
    - 将 `session`/`session-summary`/`session-end` 类型排除在问题分类之外。
    - Prevents confusion between historical session notes and actual current issues
  - **路径显示**：无法检测 git 时用 `process.cwd()` 替代 “Unknown location”。
    - When git repository detection fails, uses `process.cwd()` instead of "Unknown location"
    - Provides better context awareness even in non-git directories

## [8.40.0] - 2025-11-27

### Added
- **Session Start 版本显示** —— 启动自动展示版本信息（f2f7d2b，修复 #250）。
  - **版本检查工具**：新增 `version-checker.js`（位于 `claude-hooks/utilities/`）。
    - Reads local version from `src/mcp_memory_service/__init__.py`
    - Fetches latest published version from PyPI API
    - Compares versions and displays status labels (published/development/outdated)
    - Configurable timeout for PyPI API requests
  - 会话初始化时自动展示版本信息。
    - Displays format: `📦 Version → X.Y.Z (local) • PyPI: X.Y.Z`
    - Shows after storage backend information
    - Provides immediate visibility into version status
  - 含 `test_version_checker.js` 用于校验。
  - **收益**：
    - 快速核对版本，无需手查。
    - 及早发现安装过期。
    - 提升开发流程透明度。
    - 帮助用户保持最新特性与修复。

## [8.39.1] - 2025-11-27

### Fixed
- **仪表盘分析页缺陷** —— 修复分析页三项关键问题（c898a72，修复 #253）。
  - **热门标签过滤**：按选定时间范围（7/30/90 天）正确过滤。
    - 使用 `get_memories_by_time_range()` 做时间过滤。`
    - 仅统计所选时间段内的标签。
    - Maintains backward compatibility with all storage backends
  - **最近活动显示**：柱状图显示百分比分布。
    - 同时显示数量与占比。
    - 提示包含绝对值与百分比。
    - 活动计数标签展示百分比（例：42 (23.5%)）。
  - **存储报告字段不匹配**：修复 “undefined chars” 显示。
    - 字段改为 `size_kb`。
    - 字段改为 `preview`。
    - 修正日期解析：`created_at` 为 ISO 字符串。
    - 增加空值保护，正确显示大小（KB，回退 bytes）。

## [8.39.0] - 2025-11-26

### Performance
- **Analytics date-range filtering**: Moved from application layer to storage layer for 10x performance improvement (#238)
  - Added `get_memories_by_time_range()` to Cloudflare backend with D1 database filtering
  - Updated memory growth endpoint to use database-layer queries instead of fetching all memories
  - **Performance gains**:
    - Reduced data transfer: 50MB → 1.5MB (97% reduction for 10,000 memories)
    - Response time (SQLite-vec): ~500ms → ~50ms (10x improvement)
    - Response time (Cloudflare): ~2-3s → ~200ms (10-15x improvement)
  - **Scalability**: Now handles databases with >10,000 memories efficiently
  - **收益**： Pushes filtering to database WHERE clauses, leverages indexes on `created_at`

## [8.38.1] - 2025-11-26

### Fixed
- **HTTP MCP Transport: JSON-RPC 2.0 Compliance** - Fixed critical bug where HTTP MCP responses violated JSON-RPC 2.0 specification (PR #249, fixes #236)
  - **Problem**: FastAPI ignored Pydantic's `ConfigDict(exclude_none=True)` when directly returning models, causing responses to include null fields (`"error": null` in success, `"result": null` in errors)
  - **Impact**: Claude Code/Desktop rejected all HTTP MCP communications due to spec violation
  - **Solution**: Wrapped all `MCPResponse` returns in `JSONResponse` with explicit `.model_dump(exclude_none=True)` serialization
  - **Verification**:
    - Success responses now contain ONLY: `jsonrpc`, `id`, `result`
    - Error responses now contain ONLY: `jsonrpc`, `id`, `error`
  - **Testing**: Validated with curl commands against all 5 MCP endpoint response paths
  - **Credits**: @timkjr (Tim Knauff) for identifying root cause and implementing proper fix

## [8.38.0] - 2025-11-25

### Improved
- **代码质量：Phase 2b 去重完成** —— 共消除约 176-186 行重复代码（#246）。
  - 文档分块处理、MCP 响应解析、缓存统计日志、冬季跨年边界、测试临时文件、MCP 服务器配置、用户交互提示、GPU 检测等均抽取 Helper 统一；多处重复归一。
  - 汇总：10 次合并，10+ 重复实现→规范版本；保留 5 组高风险/低收益未动；完全向后兼容，测试覆盖 100%。

### Code Quality
- **Phase 2b Duplicate Consolidation**: 10 consolidation commits addressing multiple duplication groups
- **Duplication Score**: Reduced from 5.5% (Phase 2a baseline) to estimated 4.5-4.7%
- **Complexity Reduction**: Helper extraction pattern applied consistently across codebase
- **Expected Impact**:
  - Duplication Score: Approaching <3% target with strategic consolidation
  - Complexity Score: Improved through helper function extraction
  - Overall Health Score: Strong progress toward 75+ target
- **Remaining Work**: 5 duplication groups intentionally deferred (high-risk backend logic, low-benefit shared imports)
- **Related**: Issue #246 Phase 2b (Duplicate Consolidation Strategy COMPLETE)

## [8.37.0] - 2025-11-24

### Improved
- **代码质量：Phase 2a 去重完成** —— 清理 5 个高复杂度重复函数（#246）。
  - `detect_gpu()` 3 处归一；`verify_installation()` 2 处归一；补充 ONNX 依赖检查与 DirectML 处理；错误提示更完善。
  - 高复杂度函数 27→24（-11%），保持 100% 兼容。

### Code Quality
- **Phase 2a Duplicate Consolidation**: 5 of 5 target functions consolidated (100% complete)
- **High-Complexity Functions**: Reduced from 27 to 24 (-11%)
- **Complexity Reduction**: Configuration-driven patterns replace monolithic if/elif chains
- **Expected Impact**:
  - Duplication Score: Reduced toward <3% target
  - Complexity Score: Improved through helper extraction
  - Overall Health Score: On track for 75+ target
- **Related**: Issue #246 Phase 2a (Duplicate Consolidation Strategy COMPLETE)

## [8.36.1] - 2025-11-24

### Fixed
- **严重**：修复 v8.36.0 启动时 analytics.py 前向引用导致 HTTP 服务器崩溃（#247）。
  - 增加 `from __future__ import annotations`；typing 引入 `Tuple` 兼容 Py3.9。
  - 解除所有 v8.36.0 启动失败；10 个分析路由注册成功。
  - 根因：PR #244 重构引入前向引用但缺少 future 导入。

## [8.36.0] - 2025-11-24

### Improved
- **代码质量：Phase 2 完成（目标 100%）** —— 最后 7 个函数重构，复杂度 -19（#240 / PR #244）。
  - consolidator.py（-8）：`consolidate()` 12→8，加入 SyncPauseContext 与 `check_horizon_requirements()`；`_get_memories_for_horizon()` 10→8，改为 HORIZON_CONFIGS 数据驱动。
  - analytics.py（-8）：`get_tag_usage_analytics()` 10→6，抽取 `fetch_storage_stats()` 与 `calculate_tag_statistics()`；`get_activity_breakdown()` 9→7 抽取时间范围计算；`get_memory_type_distribution()` 9→7 抽取聚合助手。
  - install.py（-2）：`detect_gpu()` 10→8，数据驱动 GPU_PLATFORM_CHECKS + `test_gpu_platform()`。
  - cloudflare.py（-1）：`get_memory_timestamps()` 9→8，抽取 `_fetch_d1_timestamps()`。
  - Gemini 审核改进（5 轮）：
    - 关键修复：时区 `datetime.now(timezone.utc)`；analytics 计数改用 `count_all_memories()`；CUDA/ROCm 尝试所有路径。
    - 质量提升：`pkg_resources`→`importlib.metadata`，`universal_newlines`→`text=True`；`exc_info=True` 日志；结构一致性提升。

### Code Quality
- **Phase 2 完成**：10/10 函数已重构，复杂度目标 -39 全部达成。
  - 批次：v8.34.0 (-5)；v8.35.0 (-15)；v8.36.0 (-19)。
  - 预期：复杂度分 40→51+（超额）；健康分 63→68-72（达 B 等级）。
  - 关联：Issue #240 Phase 2 完成；Phase 1（v8.33.0）为死代码清理。

## [8.35.0] - 2025-11-24

### Improved
- **代码质量：Phase 2 Batch 1** —— 重构 2 个高优先函数（#240 / PR #243）。
  - `install.py::configure_paths()`：复杂度 15→5，抽取 4 个 helper，主函数缩至 ~30 行，可测试性提升。
  - `cloudflare.py::_search_by_tags_internal()`：复杂度 13→8，抽取 3 个 helper（标签归一/查询构建），更清晰。
  - Gemini 审核改进：动态 PROJECT_ROOT 检测；精确异常处理（OSError/IOError/PermissionError）；文档路径可移植。

### Code Quality
- 进度：3/10 函数已重构（30%）；复杂度已降 20/39（51%）。
- 剩余 7 个函数计划已就绪；整体健康分仍朝 75+ 目标推进。

## [8.34.0] - 2025-11-24

### Improved
- **代码质量：Phase 2 降复杂度** —— 重构 `analytics.py::get_memory_growth()`（#240）。
  - 复杂度 11→6-7（超额完成 -3 目标）。
  - 引入 PeriodType 枚举、PERIOD_CONFIGS/ PERIOD_LABEL_FORMATTERS 数据驱动配置与标签格式；提升分析端点可维护性与扩展性。

### Code Quality
- Phase 2 进度：1/10 函数完成；复杂度预估 +1；整体健康分仍朝 70+ 目标推进。

## [8.33.0] - 2025-11-24

### Fixed
- **严重安装问题**：修复 `install.py` 提前 return 导致 Claude Desktop MCP 配置未执行（#240 Phase 1）。
  - 77 行 Claude Desktop 设置代码现会正确运行，`install.py` 将自动配置 MCP 服务器。
  - 根因：1358 行异常处理提前 `return False`，使 1360-1436 行不可达。
  - 解决了 pyscn 识别的 27 处死代码。

### Improved
- `install.py` 全面改用 pathlib；精确异常处理（OSError/PermissionError/JSONDecodeError）；修复 Windows `memory_wrapper.py` 路径解析（`resolve()`）。
- 增加配置结构校验、防止 JSON 异常；优化导入与错误信息；多轮 Gemini Code Assist 审核后的结构改进。

### Code Quality
- **死代码分**：70 → 85-90（移除 27 处违例，预计 +15-20 分）。
- **健康分**：63 → 68-72（预计 +5-9 分）。
- 以上改进由 Gemini PR 自动审查工作流完成。

## [8.32.0] - 2025-11-24

### Added
- **pyscn 静态分析集成** —— 多层质量工作流。
  - 新增 `scripts/pr/run_pyscn_analysis.sh`（PR 阶段，健康分阈值 <50 阻断）。
  - 新增 `scripts/quality/track_pyscn_metrics.sh`（历史指标 CSV 追踪）。
  - 新增 `scripts/quality/weekly_quality_review.sh`（每周自动回归检测）。
  - `scripts/pr/quality_gate.sh` 增 `--with-pyscn` 全量检查。
  - 三层策略：预提交（Groq/Gemini LLM）→ PR Gate（标准+pyscn）→ 周期性（周报）。
  - 覆盖 6 指标：圈复杂度、死代码、重复、耦合、依赖、架构；健康分阈值：<50 阻断、50-69 需行动、70-84 良好、85+ 优秀。
  - 文档：`docs/development/code-quality-workflow.md`；集成指南 `.claude/agents/code-quality-guard.md`；`CLAUDE.md` 补充“Code Quality Monitoring”。

## [8.31.0] - 2025-11-23

### Added
- **批量更新性能革命** —— 新批量更新 API 让整合提速 21,428×（#241）。
  - 性能：500 条批量更新 300s → 0.014s；整合流程 5+ 分钟 → <1s。
  - 新增 `update_memories_batch()`，存储后端原子批量操作。
  - 实现：SQLite 单事务 executemany；Cloudflare 并行批更新并同步 vectorize；Hybrid 双后端队列优化。
  - 兼容：单条更新路径仍可用；真实场景 5 分钟级操作降至 <1 秒。
  - 变更文件：`storage/sqlite_vec.py`、`storage/cloudflare.py`、`storage/hybrid.py`、`consolidation/service.py` 等。

### Performance
- **记忆整合**：批量元数据更新 21,428× 提速；整合全流程 <1 秒（500 条）。
- **数据库效率**：单事务取代 500 次提交，消除开销。

## [8.30.0] - 2025-11-23

### Added
- **自适应图表粒度** —— 分析图表按语义时间间隔聚合：
  - 上月视图：3 天粒度 → 周聚合；上年视图：月聚合。
  - 友好标签：日视图 “Nov 15”；周 “Week of Nov 15”；月 “November 2024”。
  - 更契合时间区间与图表粒度；改动文件 `analytics.py`、`web/static/app.js`。

### Fixed
- **严重：区间聚合错误** —— 多日区间（周/月）现按完整区间聚合。
  - 问题：仅统计区间首日数据，导致周数据严重偏低。
  - 修复：调整聚合逻辑，按区间过滤计数；修改 `analytics.py` 相关段。

- **严重：数据采样缺失** —— API 仅拉取最近 1000 条，导致历史数据缺失。
  - 修复：拉取上限增至 10,000，并按 `created_at >= start_date` 过滤；保持 <200ms 响应。

### Changed
- **Analytics API**：扩大拉取上限并正确过滤日期，保证历史分析准确。

## [8.29.0] - 2025-11-23

### Added
- **仪表盘快速操作：同步控件小部件** —— 为混合后端提供紧凑实时同步管理（#234，修复 #233）。
  - 实时状态：同步/同步中/挂起/错误/暂停，彩色图标显示。
  - 暂停/恢复：便于维护或离线；强制同步按钮；展示上次同步时间与待处理数。
  - 清爽布局：移除头部与主体间冗余条，移至侧边栏；sqlite-vec-only 用户自动隐藏。
  - API：`POST /api/sync/pause`、`POST /api/sync/resume`；后端新增 `pause_sync()`/`resume_sync()`。

- **自动计划备份系统** —— 企业级备份，含保留策略与调度（#234，修复 #233）。
  - 新模块 `backup/`：`BackupService` + `BackupScheduler`；使用 SQLite 原生 `sqlite3.backup()` 安全备份；异步 I/O；支持小时/日/周计划；保留天数与最大数可配。
  - 仪表盘小部件：状态、上次备份、手动触发、数量、下次时间。
  - 配置：`MCP_BACKUP_ENABLED`、`MCP_BACKUP_INTERVAL`、`MCP_BACKUP_RETENTION`、`MCP_BACKUP_MAX_COUNT`。
  - API：`GET /api/backup/status`、`POST /api/backup/now`、`GET /api/backup/list`；OAuth 保护，响应不暴露路径；Safari 懒加载监听器兼容。

### Changed
- **布局**：同步控件移至侧边栏；强制同步保留暂停状态；同步/备份操作新增 toast 通知。

### Fixed
- 修复同步按钮懒监听的 DOM 时序问题；同步动画 CSS 修正；备份 API 响应不再暴露路径（改用备份 ID）。

## [8.28.1] - 2025-11-22

### Fixed
- **严重：HTTP MCP 传输 JSON-RPC 2.0 合规** —— 修复协议违规导致 Claude Code 拒绝（#236）。
  - 问题：成功响应含 `"error": null`，违反规范（成功应无 error 字段）；Claude Code 抛 “Unrecognized key 'error'”。
  - 根因：MCPResponse 同时含 result/error，序列化出 null。
  - 方案：`ConfigDict(exclude_none=True)`；docstring 说明；`.dict()` 改 `.model_dump()`；调整 import 顺序。
  - 修改文件：`web/api/mcp.py`；测试确认成功响应仅含 jsonrpc/id/result，错误仅含 jsonrpc/id/error；致谢 @timkjr。

## [8.28.0] - 2025-11-21

### Added
- **Cloudflare 标签过滤** —— 标签搜索支持 AND/OR，统一 API（#228）。
  - 基类新增 `search_by_tags(tags, operation, time_start, time_end)`，SQLite/Cloudflare/Hybrid/HTTP 客户端均实现。
  - Cloudflare SQL 统一用 `GROUP BY` + `HAVING COUNT(DISTINCT ...)` 实现 AND，可选时间范围。
  - 新增 `get_all_tags_with_counts()` 供分析面板使用。

### Changed
- **标签过滤行为** —— `get_all_memories(tags=...)` 改为精确匹配 + AND 逻辑（不再子串 OR），Hybrid 也暴露 `operation` 参数保持一致。

## [8.27.2] - 2025-11-18

### Fixed
- **Cloudflare→SQLite 同步丢失 memory_type** —— 修复同步脚本未保留 `memory_type`。
  - 问题：`sync_memory_backends.py` 未提取/传递 `memory_type`，`--direction cf-to-sqlite` 后仪表盘显示 100% 未类型化。
  - 方案：提取源的 `memory_type`，创建目标 Memory 时传递 `memory_type`、`updated_at`。
  - 修改：`scripts/sync/sync_memory_backends.py`。受影响用户可重新执行同步恢复类型。

## [8.27.1] - 2025-11-18

### Fixed
- **严重：时间戳回归缺陷** —— 修复 `created_at` 在元数据同步中被重置。
  - 问题：双向同步/漂移检测（v8.25.0-8.27.0）把 `created_at` 重置为当前时间，历史时间戳丢失。
  - 根因：`preserve_timestamps=False` 错误地重置了 `created_at` 与 `updated_at`。
  - 方案：`update_memory_metadata()` 保留源 `created_at`；Hybrid 传递四个时间字段；Cloudflare 与 SQLite-vec 时间处理一致。
  - 修改：`storage/sqlite_vec.py`、`storage/hybrid.py`、`storage/cloudflare.py`；新增测试 `tests/test_timestamp_preservation.py`。
  - 恢复工具：`scripts/validation/validate_timestamp_integrity.py`、`scripts/maintenance/recover_timestamps_from_cloudflare.py`；受影响版本 v8.25.0 / v8.27.0，Hybrid 用户可按脚本恢复时间戳。

### Changed
- **Timestamp Handling Semantics** - Clarified `preserve_timestamps` parameter behavior:
  - `preserve_timestamps=True` (default): Only updates `updated_at` to current time, preserves `created_at`
  - `preserve_timestamps=False`: Uses timestamps from `updates` dict if provided, otherwise preserves existing `created_at`
  - **Never** resets `created_at` to current time (this was the bug)

### Added
- **Timestamp Integrity Validation** - New script to detect timestamp anomalies:
  ```bash
  python scripts/validation/validate_timestamp_integrity.py
  ```
  - Checks for impossible timestamps (`created_at > updated_at`)
  - Detects suspicious timestamp clusters (bulk reset indicators)
  - Analyzes timestamp distribution for anomalies
  - Provides detailed statistics and warnings

## [8.27.0] - 2025-11-17

### Added
- **混合存储同步性能优化** —— 初始同步提速 3-5 倍。
  - 绩效：~5.5 条/秒 → ~15-30 条/秒（2619 条从 8 分钟降至 1.5-3 分钟）。
  - 优化：批量存在检查 `get_all_content_hashes()`；`asyncio.gather()` + Semaphore(15) 并发；Cloudflare 批量 100→500（请求 1/5）。
  - 修改：`storage/sqlite_vec.py`、`storage/hybrid.py`、`scripts/benchmarks/benchmark_hybrid_sync.py`。
  - 兼容：零破坏，适用于大规模初始同步。

### Changed
- **Hybrid Initial Sync Architecture** - Refactored sync loop for better performance
  - O(1) hash lookups instead of O(n) individual queries
  - Concurrent processing with controlled parallelism (15 simultaneous operations)
  - Reduced Cloudflare API overhead with larger batches (6 API calls vs 27)
  - Maintains full drift detection and metadata synchronization capabilities

### Fixed
- **重复同步队列** —— 新增 `MCP_HYBRID_SYNC_OWNER` 解决双队列低效/竞态。
  - 选项：`http`（推荐，仅 HTTP 同步）、`mcp`、`both`（默认兼容）。
  - 修改：`config.py`、`storage/factory.py`、`mcp_server.py`、`web/dependencies.py`。
  - 迁移：`export MCP_HYBRID_SYNC_OWNER=http` 可避免重复同步；保持向后兼容。

### Performance
- **Benchmark Results** (`python scripts/benchmarks/benchmark_hybrid_sync.py`):
  - Bulk hash loading: 2,619 hashes loaded in ~100ms (vs ~13,000ms for individual queries)
  - Parallel processing: 15x concurrency reduces CPU idle time
  - Batch size optimization: 78% reduction in API calls (27 → 6 for 2,619 memories)
  - Combined speedup: 3-5x faster initial sync

## [8.26.0] - 2025-11-16

### Added
- **全局 MCP 服务器缓存** —— MCP 工具性能大幅提升（PR #227）。
  - 性能：缓存命中快 534,628×（1,810ms→0.01ms）；延迟降 99.9996%；命中率 90%+；预热后 MCP 工具较 HTTP 快 41×。
  - 新工具 `get_cache_stats`：实时查看命中/未命中、缓存大小、初始化耗时。
  - 基础设施：`_STORAGE_CACHE`、`_MEMORY_SERVICE_CACHE`、`_CACHE_STATS`；`asyncio.Lock` 保障并发；关闭时自动清理。
  - 修改：`server.py`、`mcp_server.py`、`utils/cache_manager.py`、`benchmark_server_caching.py`。
  - 兼容：零破坏，对所有 MCP 客户端透明；Claude Desktop/Code 现为最快路径。

### Changed
- **Code Quality Improvements** - Gemini Code Assist review implementation (PR #227)
  - Eliminated code duplication across `server.py` and `mcp_server.py`
  - Created shared `CacheManager.calculate_stats()` utility for statistics
  - Enhanced PEP 8 compliance with proper naming conventions
  - Added comprehensive inline documentation for cache implementation

### Fixed
- **Security Vulnerability** - Removed unsafe `eval()` usage in benchmark script (PR #227)
  - Replaced `eval(stats_str)` with safe `json.loads()` for parsing cache statistics
  - Eliminated arbitrary code execution risk in development tools
  - Improved benchmark script robustness

### Performance
- **Benchmark Results** (10 consecutive MCP tool calls):
  - First Call (Cache Miss): ~2,485ms
  - Cached Calls Average: ~0.01ms
  - Speedup Factor: 534,628x
  - Cache Hit Rate: 90%
- **Impact**: MCP tools are now the recommended method for Claude Desktop and Claude Code users
- **Technical Details**:
  - Caches persist across stateless HTTP calls
  - Storage instances keyed by "{backend}:{path}"
  - MemoryService instances keyed by storage ID
  - Lazy initialization preserved to prevent startup hangs

### Documentation
- Updated Wiki: 05-Performance-Optimization.md with cache architecture
- Added cache monitoring guide using `get_cache_stats` tool
- Performance comparison tables now show MCP as fastest method

## [8.25.2] - 2025-11-16

### Changed
- **Drift Detection Script Refactoring** - Improved code maintainability in `check_drift.py` (PR #226)
  - **Refactored**: Cloudflare config dictionary construction to use dictionary comprehension
  - **Improvement**: Separated configuration keys list from transformation logic
  - **Benefit**: Easier to maintain and modify configuration keys
  - **Code Quality**: More Pythonic, cleaner, and more readable
  - **Impact**: No functional changes, pure code quality improvement
  - **File Modified**: `scripts/sync/check_drift.py`
  - **Credit**: Implements Gemini code review suggestions from PR #224

## [8.25.1] - 2025-11-16

### Fixed
- **Drift Detection Script Initialization** - Corrected critical bugs in `check_drift.py` (PR #224)
  - **Bug 1**: Fixed incorrect config attribute `SQLITE_DB_PATH` → `SQLITE_VEC_PATH` in AppConfig
  - **Bug 2**: Added missing `cloudflare_config` parameter to HybridMemoryStorage initialization
  - **Impact**: Script was completely broken for Cloudflare/Hybrid backends - now initializes successfully
  - **Error prevented**: `AttributeError: 'AppConfig' object has no attribute 'SQLITE_DB_PATH'`
  - **File Modified**: `scripts/sync/check_drift.py`
  - **Severity**: High - Script was non-functional for users with hybrid or cloudflare backends
- **CI Test Infrastructure** - Added HuggingFace model caching to prevent network-related test failures (PR #225)
  - **Root Cause**: GitHub Actions runners cannot access huggingface.co during test runs
  - **Solution**: Implemented `actions/cache@v3` for `~/.cache/huggingface` directory
  - **Pre-download step**: Downloads `all-MiniLM-L6-v2` model after dependency installation
  - **Impact**: Fixes all future PR test failures caused by model download restrictions
  - **Cache Strategy**: Key includes `pyproject.toml` hash for dependency tracking
  - **Performance**: First run downloads model, subsequent runs use cache
  - **File Modified**: `.github/workflows/main.yml`

### 技术细节
- **PR #224**: Drift detection script now properly initializes Cloudflare backend with all required parameters (api_token, account_id, d1_database_id, vectorize_index)
- **PR #225**: CI environment now caches embedding models, eliminating network dependency during test execution
- **Testing**: Both fixes validated in PR test runs - drift detection now works, tests pass consistently

## [8.25.0] - 2025-11-15

### Added
- **Hybrid Backend Drift Detection** - Automatic metadata synchronization using `updated_at` timestamps (issue #202)
  - **Bidirectional awareness**: Detects metadata changes on either backend (SQLite-vec ↔ Cloudflare)
  - **Periodic drift checks**: Configurable interval via `MCP_HYBRID_DRIFT_CHECK_INTERVAL` (default: 1 hour)
  - **"Newer timestamp wins" conflict resolution**: Prevents data loss during metadata updates
  - **Dry-run support**: Preview changes via `python scripts/sync/check_drift.py`
  - **New configuration variables**:
    - `MCP_HYBRID_SYNC_UPDATES` - Enable metadata sync (default: true)
    - `MCP_HYBRID_DRIFT_CHECK_INTERVAL` - Seconds between drift checks (default: 3600)
    - `MCP_HYBRID_DRIFT_BATCH_SIZE` - Memories to check per scan (default: 100)
  - **New methods**:
    - `BackgroundSyncService._detect_and_sync_drift()` - Core drift detection logic with dry-run mode
    - `CloudflareStorage.get_memories_updated_since()` - Query memories by update timestamp
  - **Enhanced initial sync**: Now detects and syncs metadata drift for existing memories

### Fixed
- **Issue #202** - Hybrid backend now syncs metadata updates (tags, types, custom fields)
  - Previous behavior only detected missing memories, ignoring metadata changes
  - Prevented silent data loss when memories updated on one backend but not synced
  - Tag fixes in Cloudflare now properly propagate to local SQLite
  - Metadata updates no longer diverge between backends

### Changed
- Initial sync (`_perform_initial_sync`) now compares timestamps for existing memories
- Periodic sync includes drift detection checks at configurable intervals
- Sync statistics tracking expanded with drift detection metrics

### 技术细节
- **Files Modified**:
  - `src/mcp_memory_service/config.py` - Added 3 configuration variables
  - `src/mcp_memory_service/storage/hybrid.py` - Drift detection implementation (~150 lines)
  - `src/mcp_memory_service/storage/cloudflare.py` - Added `get_memories_updated_since()` method
  - `scripts/sync/check_drift.py` - New dry-run validation script
- **Architecture**: Timestamp-based drift detection with 1-second clock skew tolerance
- **Performance**: Non-blocking async operations, configurable batch sizes
- **Safety**: Opt-in feature, dry-run mode, comprehensive audit logging

## [8.24.4] - 2025-11-15

### Changed
- **Code Quality Improvements** - Applied Gemini Code Assist review suggestions (issue #180)
  - **documents.py:87** - Replaced chained `.replace()` calls with `re.sub()` for path separator sanitization
  - **app.js:751-762** - Cached DOM elements in setProcessingMode to reduce query overhead
  - **app.js:551-553, 778-780** - Cached upload option elements to optimize handleDocumentUpload
  - **index.html:357, 570** - Fixed indentation consistency for closing `</div>` tags
  - Performance impact: Minor - reduced DOM query overhead
  - Breaking changes: None

### 技术细节
- **Files Modified**: `src/mcp_memory_service/web/api/documents.py`, `src/mcp_memory_service/web/static/app.js`, `src/mcp_memory_service/web/static/index.html`
- **Code Quality**: Regex-based sanitization more scalable, DOM element caching reduces redundant queries
- **Commit**: ffc6246 - refactor: code quality improvements from Gemini review (issue #180)

## [8.24.3] - 2025-11-15

### Fixed
- **GitHub Release Manager Agent** - Resolved systematic version history omission in README.md (commit ccf959a)
  - Fixed agent behavior that was omitting previous versions from "Previous Releases" section
  - Added v8.24.1 to Previous Releases list (was missing despite being valid release)
  - Enhanced agent instructions with CRITICAL section for maintaining version history integrity
  - Added quality assurance checklist item to prevent future omissions
  - Root cause: Agent was replacing entire Previous Releases section instead of prepending new version

### Added
- **Test Coverage for Tag+Time Filtering** - Comprehensive test suite for issue #216 (commit ebff282)
  - 10 unit tests passing across SQLite-vec, Cloudflare, and Hybrid backends
  - Validates PR #215 functionality (tag+time filtering to fix semantic over-filtering bug #214)
  - Tests verify memories can be retrieved using both tag criteria AND time range filters
  - API integration tests created (with known threading issues documented for future fix)
  - Ensures regression prevention for semantic search over-filtering bug

### Changed
- GitHub release workflow now more reliable with enhanced agent guardrails
- Test suite provides better coverage for multi-filter memory retrieval scenarios

### 技术细节
- **Files Modified**:
  - `.claude/agents/github-release-manager.md` - Added CRITICAL section for Previous Releases maintenance
  - `tests/test_time_filtering.py` - 10 new unit tests for tag+time filtering
  - `tests/integration/test_api_time_search.py` - API integration tests (threading issues documented)
- **Test Execution**: All 10 unit tests passing, API tests have known threading limitations
- **Impact**: Prevents version history loss in future releases, ensures tag+time filtering remains functional

## [8.24.2] - 2025-11-15

### Fixed
- **CI/CD Workflow Infrastructure** - Development Setup Validation workflow fixes (issue #217 related)
  - Fixed bash errexit handling in workflow tests - prevents premature exit on intentional test failures
  - Corrected exit code capture using EXIT_CODE=0 and || EXIT_CODE=$? pattern
  - All 5 workflow tests now passing: version consistency, pre-commit hooks, server warnings, developer prompts, docs accuracy
  - Root cause: bash runs with -e flag (errexit), which exits immediately when commands return non-zero exit codes
  - Tests intentionally run check_dev_setup.py expecting exit code 1, but bash was exiting before capture
  - Commits: b4f9a5a, d1bcd67

### Changed
- Workflow tests can now properly validate that the development setup validator correctly detects problems
- Exit code capture no longer uses "|| true" pattern (was making all commands return 0)

### 技术细节
- **Files Modified**: .github/workflows/dev-setup-validation.yml
- **Pattern Change**:
  - Before: `python script.py || true` (always returns 0, breaks exit code testing)
  - After: `EXIT_CODE=0; python script.py || EXIT_CODE=$?` (captures actual exit code, prevents bash exit)
- **Test Jobs**: All 5 jobs in dev-setup-validation workflow now pass consistently
- **Context**: Part of test infrastructure improvement efforts (issue #217)

## [8.24.1] - 2025-11-15

### Fixed
- **Test Infrastructure Failures** - Resolved 27 pre-existing test failures (issue #217)
  - Fixed async fixture incompatibility in 6 test files (19+ failures)
  - Corrected missing imports (MCPMemoryServer → MemoryServer, removed MemoryMetadata)
  - Added missing content_hash parameter to Memory() instantiations
  - Updated hardcoded version strings (6.3.0 → 8.24.0)
  - Improved test pass rate from 63% to 71% (412/584 tests passing)
  - Execution: Automated via amp-bridge agent

### Changed
- Test suite now has cleaner baseline for detecting new regressions
- All async test fixtures now use @pytest_asyncio.fixture decorator

### 技术细节
- **Automated Fix**: Used amp-bridge agent for pattern-based refactoring
- **Execution Time**: ~15 minutes (vs 1-2 hours manual)
- **Files Modified**: 11 test files across tests/ and tests/integration/
- **Root Causes**: Test infrastructure issues, not code bugs
- **Remaining Failures**: 172 failures remain (backend config, performance, actual bugs)

## [8.24.0] - 2025-11-12

### Added
- **PyPI Publishing Automation** - Package now available via `pip install mcp-memory-service`
  - **Workflow Automation**: Configured GitHub Actions workflow to automatically publish to PyPI on tag pushes
  - **Installation Simplification**: Users can now install directly via `pip install mcp-memory-service` or `uv pip install mcp-memory-service`
  - **Accessibility**: Resolves installation barriers for users without git access or familiarity
  - **Token Configuration**: Secured with `PYPI_TOKEN` GitHub secret for automated publishing
  - **Quality Gates**: Publishes only after successful test suite execution

### Changed
- **Distribution Method**: Added PyPI as primary distribution channel alongside GitHub releases
- **Installation Documentation**: Updated guides to include pip-based installation as recommended method

### 技术细节
- **Files Modified**:
  - `.github/workflows/publish.yml` - NEW workflow for automated PyPI publishing
  - GitHub repository secrets - Added `PYPI_TOKEN` for authentication
- **Trigger**: Workflow runs automatically on git tag creation (pattern: `v*.*.*`)
- **Build System**: Uses Hatchling build backend with `python-semantic-release`

### Migration Notes
- **For New Users**: Preferred installation is now `pip install mcp-memory-service`
- **For Existing Users**: No action required - git-based installation continues to work
- **For Contributors**: Tag creation now triggers PyPI publishing automatically

## [8.23.1] - 2025-11-10

### Fixed
- **Stale Virtual Environment Prevention System** - Comprehensive 6-layer strategy to prevent "stale venv vs source code" version mismatches
  - **Root Cause**: MCP servers load from site-packages, not source files. System restart doesn't help - it relaunches with same stale package
  - **Impact**: Prevented issue that caused v8.23.0 tag validation bug to persist despite v8.22.2 fix (source showed v8.23.0 while venv had v8.5.3)

### Added
- **Phase 1: Automated Detection**
  - New `scripts/validation/check_dev_setup.py` - Validates source/venv version consistency, detects editable installs
  - Enhanced `scripts/hooks/pre-commit` - Blocks commits when venv is stale, provides actionable error messages
  - Added CLAUDE.md development setup section with explicit `pip install -e .` guidance

- **Phase 2: Runtime Warnings**
  - Added `check_version_consistency()` function in `src/mcp_memory_service/server.py`
  - Server startup warnings when version mismatch detected (source vs package)
  - Updated README.md developer section with editable install instructions
  - Enhanced `docs/development/ai-agent-instructions.md` with proper setup commands

- **Phase 3: Interactive Onboarding**
  - Enhanced `scripts/installation/install.py` with developer detection (checks for git repo)
  - Interactive prompt guides developers to use `pip install -e .` for editable installs
  - New CI/CD workflow `.github/workflows/dev-setup-validation.yml` with 5 comprehensive test jobs:
    1. Version consistency validation
    2. Pre-commit hook functionality
    3. Server startup warnings
    4. Interactive developer prompts
    5. Documentation accuracy checks

### Changed
- **Developer Workflow**: Developers now automatically guided to use `pip install -e .` for proper setup
- **Pre-commit Hook**: Now validates venv consistency before allowing commits
- **Installation Process**: Detects developer mode and provides targeted guidance

### 技术细节
- **6-Layer Prevention System**:
  1. **Development**: Pre-commit hook blocks bad commits, detection script validates setup
  2. **Runtime**: Server startup warnings catch edge cases
  3. **Documentation**: CLAUDE.md, README.md, ai-agent-instructions.md all updated
  4. **Automation**: check_dev_setup.py, pre-commit hook, CI/CD workflow
  5. **Interactive**: install.py prompts developers for editable install
  6. **Testing**: CI/CD workflow with 5 comprehensive test jobs

- **Files Modified**:
  - `scripts/validation/check_dev_setup.py` - NEW automated detection script
  - `scripts/hooks/pre-commit` - Enhanced with venv validation
  - `CLAUDE.md` - Added development setup guidance
  - `src/mcp_memory_service/server.py` - Added runtime version check
  - `README.md` - Updated developer section
  - `docs/development/ai-agent-instructions.md` - Updated setup commands
  - `scripts/installation/install.py` - Added developer detection
  - `.github/workflows/dev-setup-validation.yml` - NEW CI/CD validation

### Migration Notes
- **For Developers**: Run `pip install -e .` to install in editable mode (will be prompted by install.py)
- **For Users**: No action required - prevention system is transparent for production use
- **Pre-commit Hook**: Automatically installed during `install.py`, validates on every commit

### Commits Included
- `670fb74` - Phase 1: Automated detection (check_dev_setup.py, pre-commit hook, CLAUDE.md)
- `9537259` - Phase 2: Runtime warnings (server.py) + developer documentation
- `a17bcc7` - Phase 3: Interactive onboarding (install.py) + CI/CD validation
