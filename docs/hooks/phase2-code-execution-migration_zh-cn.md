# Phase 2：Session Hook 迁移至代码执行 API

- **状态**：✅ 完成
- **Issue**：[#206](https://github.com/doobidoo/mcp-memory-service/issues/206)
- **分支**：`feature/code-execution-api`

## 概述
Session Hook 已从 MCP 工具调用切换为 Python 代码执行，平均节省 75% token，并保持 100% 兼容。

## 成果摘要
- Session Start 由 3,600 → 900 token（75%）；
- Git/Recent/Tagged 查询平均降至 385 token；
- Cold start ~3.4s（加载模型），Warm 执行 Phase 3 再优化；
- 全部 10 项测试通过。

## 实现
- `claude-hooks/core/session-start.js`：新增 `queryMemoryServiceViaCode` 与 fallback；
- 配置新增 `codeExecution.enabled|timeout|fallbackToMCP|pythonPath|enableMetrics`；
- `claude-hooks/tests/test-code-execution.js`：验证成功率、fallback、token 计算、错误处理等。

## 使用
```json
"codeExecution": {
  "enabled": true,
  "timeout": 5000,
  "fallbackToMCP": true,
  "pythonPath": "python3"
}
```
默认启用，失败自动回退 MCP；设置 `enabled:false` 即回到旧模式。令牌节省会在日志输出。

## 架构
1. Hook 调用 `queryMemoryService()`；
2. 若启用代码执行，则调用 `python -c "from mcp_memory_service.api import search"`；
3. 失败时记录并回退 MCP 工具；
4. 结果以 Compact 类型返回（75% token 减少）。

## 测试
`node claude-hooks/tests/test-code-execution.js` → 10/10 通过。亦可单测 Python API 与配置。

## 兼容性
| 模式 | 代码执行 | MCP Fallback |
| --- | --- | --- |
| 默认 | ✅ | ✅ |
| MCP-only | ❌ | — |
| Code-only | ✅ | ❌（失败报错） |
| 无配置 | ✅ | ✅ |

## 性能 & 局限
- Cold start 需加载模型；
- 无 Streaming，批量仅支持 8 条；
- 错误详情暂仅日志显示。

## 安全
- 所有输入进行转义；
- Python 脚本固定，无动态代码；
- Timeout 默认 5s。

## 下一步（Phase 3）
- 长驻 Python 进程（Warm <100ms）；
- 扩展 `search_by_tag/recall/update`；
- 批量/Streaming/更详尽错误；
- 性能 Profiling。

## 结论
- 75%+ token 减少目标达成；
- 0 Breaking Change；
- 可直接合入主分支，下一阶段聚焦 Warm 性能与更多 API。
