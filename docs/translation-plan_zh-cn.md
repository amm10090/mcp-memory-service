# Markdown 翻译计划（zh-CN 分支）

> **更新时间：** 2025-11-11
> 
> 使用脚本 `python3 scripts/dev/find_untranslated_md.py`（下方附示例）统计，当前共有 **166** 个 Markdown 文件尚未包含任何中文字符，需逐步翻译。该计划仅针对本仓库文档，不含 `.venv/` 等第三方依赖。

## 1. 统计方法

```bash
python3 - <<'PY'
import os, re, json
regex=re.compile(r'[\u4e00-\u9fff]')
files=[]
for dp, _, fs in os.walk('.'):
    if '.git' in dp.split(os.sep):
        continue
    for fn in fs:
        if fn.lower().endswith('.md'):
            rel=os.path.relpath(os.path.join(dp, fn), '.')
            if rel.startswith('.venv/'):   # 排除第三方依赖
                continue
            try:
                data=open(rel,'r',encoding='utf-8',errors='ignore').read()
            except Exception:
                continue
            if not regex.search(data):
                files.append(rel)
print(json.dumps({'total_md_without_zh':len(files),'files':files},ensure_ascii=False,indent=2))
PY
```

## 2. 分目录任务概览

| 目录 | 待翻译数量 | 优先级 | 说明 |
| --- | --- | --- | --- |
| `docs/` | 75 | ⭐⭐⭐ | 主站文档（架构/部署/集成/教程/故障排查），用户最常访问，必须优先推进。 |
| `archive/` | 43 | ⭐ | 历史资料，需保留中文备份但可排在主文档之后。 |
| `claude_commands/` | 9 | ⭐⭐ | CLI 命令参考，翻译后方便中文用户快速查找指令。 |
| `claude-hooks/` | 6 | ⭐⭐ | Hook 配置/迁移指南，建议与 docs 同期完成。 |
| `.claude/agents/` | 5 | ⭐⭐ | 内置 Agent 使用手册，直接影响自动化流程。 |
| `scripts/` | 6 | ⭐ | 维护/同步/迁移脚本 README，主要供开发者参考。 |
| `.github/` | 6 | ⭐⭐ | Issue/PR 模板及 workflow 文档，翻译后方便团队成员按中文流程提交流程。 |
| 顶层规范（`AGENTS.md`、`CODE_OF_CONDUCT.md`、`SECURITY.md`、`ROADMAP.md` 等） | 8 | ⭐⭐ | 团队治理与安全规范，建议在主文档完成后立即翻译。 |
| 其他零散（`examples/README.md`、`src/mcp_memory_service/web/static/README.md`、`tests/README.md`、`.pytest_cache/README.md` 等） | 8 | ⭐ | 涉及示例、测试与缓存说明。 |

> **总计：166 个**（详见附录）。

## 3. 阶段性目标

1. **阶段 A（优先）**：`docs/` + `claude-hooks/` + `.github/` + `.claude/agents/`（共 92 项）。
2. **阶段 B**：`claude_commands/` + `scripts/` + 顶层规范 + 其他零散（约 30 项）。
3. **阶段 C**：`archive/` 全量翻译（43 项）——可在前两阶段完结后逐步推进。

每阶段完成后重新运行统计脚本，目标是 `total_md_without_zh` 逐步归零。

## 4. 阶段 A 进展（2025-11-11）

### 4.1 已交付（55+ 篇）
- **部署主线**：`docs/deployment/production-guide.md`、`dual-service.md`、`systemd-service.md`、`docker.md` 已全量中文化并验证命令/脚本；
- **实现 / 性能 / 健康**：`docs/implementation/performance.md`、`docs/implementation/health_checks.md` 等实现类文档均已翻译；
- **测试 / Hooks / 架构**：`docs/testing/regression-tests.md`、`docs/hooks/phase2-code-execution-migration.md`、`docs/architecture/search-*.md` 等文件补全中文；
- **集成**：Gemini / Groq 系列桥接摘要已中文化，包含模型差异、认证与速查表；
- **标签体系**：`docs/api/tag-standardization.md`、`docs/technical/tag-storage.md` 建立标准化打标流程；
- **API / 元数据**：`docs/api/code-execution-interface.md`、`docs/api/memory-metadata-api.md`、`docs/api/PHASE1_IMPLEMENTATION_SUMMARY.md`、`docs/api/PHASE2_IMPLEMENTATION_SUMMARY.md`、`docs/api/PHASE2_REPORT.md` 均已完成中文版本；
- **教程**：`docs/tutorials/advanced-techniques.md`、`docs/tutorials/data-analysis.md`、`docs/tutorials/demo-session-walkthrough.md`、`docs/migration/code-execution-api-quick-start.md`；
- **开发 / 维护**：`docs/technical/development.md`、`docs/technical/memory-migration.md`、`docs/technical/migration-log.md`、`docs/technical/sqlite-vec-embedding-fixes.md`、`docs/maintenance/memory-maintenance.md` 已译；
- **示例 / 资源**：`docs/examples/maintenance-session-example.md`、`docs/assets/images/README.md` 提供中文说明；
- **当前统计**：2025-11-12 自检，`docs/` 目录剩余纯英文 Markdown **0** 篇，全仓 Markdown 未含中文的文件共 **85** 个（新增完成：`claude-hooks/CONFIGURATION.md` 已中文化）。

### 4.2 下一批建议（目标：阶段 A 列表 92 篇全部覆盖）
1. **验证节奏**：保持每次批量更新后运行脚本，维持 `docs` 目录全量中文化；
2. **向后推进**：阶段 B/C 文档（如 `archive/`、`scripts/` 等）可按优先级逐步启动；
3. **Schema 附注**：为 `docs/examples/tag-schema.json` 规划配套中文说明或 README，方便后续迁移；
4. **持续维护**：新增英文文档时同步加入翻译计划，避免回退。

## 5. 附录：完整待译列表（166 项）

<details>
<summary>展开查看</summary>

```
CODE_OF_CONDUCT.md
CONSOLIDATION_TEST_RESULTS.md
INSTALLATION_v8.5.3.md
CHANGELOG-HISTORIC.md
ROADMAP.md
AGENTS.md
CONSOLIDATION_SETUP.md
SPONSORS.md
SECURITY.md
tools/README.md
tools/docker/README.md
tools/docker/DEPRECATED.md
archive/investigations/MACOS_HOOKS_INVESTIGATION.md
archive/docs-root-cleanup-2025-08-23/DOCUMENTATION_CONSOLIDATION_COMPLETE.md
archive/docs-root-cleanup-2025-08-23/PYTORCH_DOWNLOAD_FIX.md
archive/docs-root-cleanup-2025-08-23/AWESOME_LIST_SUBMISSION.md
archive/docs-root-cleanup-2025-08-23/README-ORIGINAL-BACKUP.md
archive/docs-root-cleanup-2025-08-23/CLOUDFLARE_IMPLEMENTATION.md
archive/docs-root-cleanup-2025-08-23/DOCUMENTATION_ANALYSIS.md
archive/docs-root-cleanup-2025-08-23/lm_studio_system_prompt.md
archive/docs-root-cleanup-2025-08-23/LITESTREAM_SETUP_GUIDE.md
archive/docs-root-cleanup-2025-08-23/DOCUMENTATION_CLEANUP_PLAN.md
archive/release-notes/release-notes-v7.1.4.md
archive/docs-removed-2025-08-23/authentication.md
archive/docs-removed-2025-08-23/claude-code-compatibility.md
archive/docs-removed-2025-08-23/UBUNTU_SETUP.md
archive/docs-removed-2025-08-23/claude_integration.md
archive/docs-removed-2025-08-23/ubuntu.md
archive/docs-removed-2025-08-23/complete-setup-guide.md
archive/docs-removed-2025-08-23/distributed-sync.md
archive/docs-removed-2025-08-23/claude-code-integration.md
archive/docs-removed-2025-08-23/windows.md
archive/docs-removed-2025-08-23/macos-intel.md
archive/docs-removed-2025-08-23/mcp-client-configuration.md
archive/docs-removed-2025-08-23/master-guide.md
archive/docs-removed-2025-08-23/windows-setup.md
archive/docs-removed-2025-08-23/invocation_guide.md
archive/docs-removed-2025-08-23/claude-code-quickstart.md
archive/docs-removed-2025-08-23/claude-desktop-setup.md
archive/docs-removed-2025-08-23/service-installation.md
archive/docs-removed-2025-08-23/multi-client-server.md
archive/docs-removed-2025-08-23/database-synchronization.md
archive/docs-removed-2025-08-23/development/multi-client-architecture.md
archive/docs-removed-2025-08-23/development/CLEANUP_PLAN.md
archive/docs-removed-2025-08-23/development/autonomous-memory-consolidation.md
archive/docs-removed-2025-08-23/development/mcp-milestone.md
archive/docs-removed-2025-08-23/development/hybrid-slm-memory-consolidation.md
archive/docs-removed-2025-08-23/development/TIMESTAMP_FIX_SUMMARY.md
archive/docs-removed-2025-08-23/development/CLEANUP_SUMMARY.md
archive/docs-removed-2025-08-23/development/CLEANUP_README.md
archive/docs-removed-2025-08-23/development/test-results.md
archive/docs-removed-2025-08-23/development/dream-inspired-memory-consolidation.md
archive/docs-removed-2025-08-23/sessions/MCP_ENHANCEMENT_SESSION_MEMORY_v4.1.0.md
archive/setup-development/README.md
archive/setup-development/STARTUP_SETUP_GUIDE.md
.pytest_cache/README.md
tests/README.md
.claude/agents/gemini-pr-automator.md
.claude/agents/amp-pr-automator.md
.claude/agents/github-release-manager.md
.claude/agents/code-quality-guard.md
.claude/agents/amp-bridge.md
docs/remote-configuration-wiki-section.md
docs/glama-deployment.md
docs/oauth-setup.md
docs/architecture.md
docs/enhancement-roadmap-issue-14.md
docs/document-ingestion.md
docs/integrations.md
docs/README.md
docs/IMPLEMENTATION_PLAN_HTTP_SSE.md
docs/pr-graphql-integration.md
docs/CLAUDE_CODE_QUICK_REFERENCE.md
docs/quick-setup-cloudflare-dual-environment.md
docs/DOCUMENTATION_AUDIT.md
docs/http-server-management.md
docs/LM_STUDIO_COMPATIBILITY.md
docs/cloudflare-setup.md
docs/HOOK_IMPROVEMENTS.md
docs/ide-compatability.md
docs/IMAGE_RETENTION_POLICY.md
docs/testing-cloudflare-backend.md
docs/sqlite-vec-backend.md
docs/docker-optimized-build.md
docs/amp-cli-bridge.md
docs/research/code-execution-interface-summary.md
docs/research/code-execution-interface-implementation.md
docs/statistics/REPOSITORY_STATISTICS.md
docs/archive/obsolete-workflows/load_memory_context.md
docs/archive/obsolete-workflows/README.md
docs/images/dashboard-placeholder.md
docs/development/dashboard-workflow.md
docs/development/pr-review-guide.md
docs/development/issue-management.md
docs/development/release-checklist.md
docs/development/todo-tracker.md
docs/development/refactoring-notes.md
docs/development/ai-agent-instructions.md
docs/integration/multi-client.md
docs/integration/homebrew.md
docs/natural-memory-triggers/installation-guide.md
docs/natural-memory-triggers/performance-optimization.md
docs/natural-memory-triggers/cli-reference.md
docs/legacy/dual-protocol-hooks.md
docs/troubleshooting/hooks-quick-reference.md
docs/integrations/groq-bridge.md
docs/integrations/groq-model-comparison.md
docs/integrations/groq-integration-summary.md
docs/integrations/gemini.md
docs/testing/regression-tests.md
docs/architecture/search-enhancement-spec.md
docs/architecture/search-examples.md
docs/deployment/production-guide.md
docs/deployment/dual-service.md
docs/deployment/systemd-service.md
docs/deployment/docker.md
docs/hooks/phase2-code-execution-migration.md
docs/examples/maintenance-session-example.md
docs/implementation/performance.md
docs/implementation/health_checks.md
docs/api/tag-standardization.md
docs/api/memory-metadata-api.md
docs/api/PHASE1_IMPLEMENTATION_SUMMARY.md
docs/api/code-execution-interface.md
docs/api/PHASE2_REPORT.md
docs/api/PHASE2_IMPLEMENTATION_SUMMARY.md
docs/tutorials/advanced-techniques.md
docs/tutorials/demo-session-walkthrough.md
docs/tutorials/data-analysis.md
docs/maintenance/memory-maintenance.md
docs/assets/images/README.md
docs/migration/code-execution-api-quick-start.md
docs/technical/migration-log.md
docs/technical/tag-storage.md
docs/technical/sqlite-vec-embedding-fixes.md
docs/technical/memory-migration.md
docs/technical/development.md
claude_commands/memory-search.md
claude_commands/memory-ingest-dir.md
claude_commands/memory-store.md
claude_commands/README.md
claude_commands/memory-recall.md
claude_commands/session-start.md
claude_commands/memory-ingest.md
claude_commands/memory-context.md
claude_commands/memory-health.md
examples/README.md
scripts/README.md
scripts/maintenance/memory-types.md
scripts/maintenance/README.md
scripts/sync/README.md
scripts/sync/litestream/README.md
scripts/migration/TIMESTAMP_CLEANUP_README.md
.github/pull_request_template.md
.github/workflows/README_OPTIMIZATION.md
.github/workflows/SECRET_CONDITIONAL_FIX.md
.github/workflows/CACHE_FIX.md
.github/workflows/WORKFLOW_FIXES.md
.github/workflows/LATEST_FIXES.md
claude-hooks/README-phase2.md
claude-hooks/MIGRATION.md
claude-hooks/WINDOWS-SESSIONSTART-BUG.md
claude-hooks/README.md
claude-hooks/CONFIGURATION.md
claude-hooks/README-NATURAL-TRIGGERS.md
src/mcp_memory_service/web/static/README.md
```

</details>

---
若需将此计划导入任务系统（如 Shrimp Task Manager），可按阶段拆分任务卡片并附上上方脚本结果，定期复用脚本验证剩余数量。

## 5. 翻译流程与质量门槛

1. **准备与认领**：运行上方脚本拿到最新列表，按照阶段优先级在协作渠道登记认领，避免多人重复翻译同一文件。
2. **翻译执行**：遵循“先结构后内容”原则，先维护原文标题层级 / 表格 / 列表，再逐段翻译；遇到专业名词时采用“中文译名（英文原词）”格式以便检索。
3. **术语统一**：沿用既有术语表（`docs/glossary.zh-cn.md`，若缺失则在 PR 中补充），保证 Cloudflare、Hook、Shrimp 等关键词在整库内保持一致译法。
4. **技术内容处理**：代码、命令与配置键值默认保留英文原文，只在段落说明里补充中文解释，确保读者能复制执行。
5. **校对要求**：提交前必须自行 diff 校对一次，重点检查（a）中英夹杂、（b）未翻译段落、（c）Markdown 语法破坏；复杂文档建议邀请第二人复核后再合并。

## 6. 状态跟踪与复盘

- **周度更新**：每周一（太平洋时间）在翻译频道同步阶段完成度，例如“阶段 A 完成 18/92，当前处理中：docs/integrations/*”。
- **脚本复验**：每完成一个阶段或合并 20+ 条文档翻译 PR，重新运行统计脚本并在记录中附上新的 `total_md_without_zh` 数，确保存量实时透明。
- **问题归档**：若遇到无法直接翻译的文件（如自动生成或示例数据），在 `docs/translation-exceptions.md`（如尚未存在则新建）追加条目，说明跳过原因与后续动作。
- **经验沉淀**：阶段结束后在团队会议纪要中记录本阶段最佳实践（工具、术语、评审流程等），并回填到此计划或相关指引中，方便下一阶段复用。

（完）
