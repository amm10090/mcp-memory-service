# 代码质量工作流（简版）

> 面向贡献者的统一质量管线：静态分析（pyscn）、测试、质量门、回归检查。适用于 v8.45.0+。

## 目标
- 将“质量”作为发布门槛：可读性、复杂度、死代码、回归测试覆盖。
- 降低审查成本：自动化报告 + 最小人工介入。
- 兼顾成本/时延：本地优先，可选云端。

## 总览
1) 本地预检：格式、lint、单测。
2) 质量分析（可选）：`pyscn analyze .` + ONNX 质量评估（如启用）。
3) PR 质量门：GitHub Actions 运行 lint + tests + 关键集成测试。
4) 周期性回顾：周度/双周质量报告。

## 快速命令
```bash
# 安装依赖
uv sync

# 基本检查
pytest tests/unit -q
pytest tests/integration/test_api_with_memory_service.py -q

# 质量脚本（按需）
bash scripts/pr/quality_gate.sh <PR_NUMBER>        # CI 同步脚本
bash scripts/pr/run_quality_checks_on_files.sh      # 变更文件快速检查
pyscn analyze .                                     # 静态分析
```

## 质量信号
- **复杂度**：函数圈复杂度、嵌套层级。
- **死代码**：未引用函数、恒 false/true 分支。
- **风格一致性**：命名、注释、文档字符串。
- **测试覆盖**：关键路径（存储、Web API、同步、质量系统）。

## PR 前置清单
- [ ] 单测通过（至少变更相关的 unit/integration）。
- [ ] 若改动存储/协议，更新契约文档与 API 规格。
- [ ] 若引入新配置，补充 `CLAUDE.md` 与对应指南。
- [ ] 文档更新保持中英文同步。

## pyscn 使用
- 入口脚本：`scripts/pr/run_pyscn_analysis.sh`
- 输出：HTML 报告位于 `.pyscn/reports/`，CI 可作为 Artifact。
- 典型阈值（可在脚本中调）：
  - 圈复杂度 >10 警告
  - 过长函数 >80 行警告
  - 重复代码块 >30 行警告

## 质量门（CI）
- GitHub Actions：`publish-and-test.yml` / `main.yml`
- 阶段：
  1) 安装依赖
  2) Lint / 静态检查（可选）
  3) 单测 + 核心集成测试
  4) （可选）pyscn 报告
- 失败即阻塞合并。

## 回归与监控
- 周报/双周报：质量得分、Top 问题、趋势。
- 关注高风险目录：`storage/`, `web/api/`, `consolidation/`, `quality/`。

## 常见问题
- **CI 很慢**：优先运行变更相关测试；使用 `pytest -k <pattern>`。
- **质量门误报**：在报告中添加注释/抑制规则前，先评估重构成本。
- **pyscn 报告为空**：检查 `.pyscn` 目录权限或日志输出。

## 参考
- `scripts/pr/quality_gate.sh`
- `scripts/pr/run_quality_checks_on_files.sh`
- `scripts/quality/phase1_dead_code_analysis.md`
- `CLAUDE.md`（质量章节）
