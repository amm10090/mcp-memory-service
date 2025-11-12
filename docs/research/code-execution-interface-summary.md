# 代码执行接口高管摘要
## Issue #206 实施指南

**结论**：提供 Python 代码接口，可在保持后向兼容的前提下节省 90-95% Token。先改造 Session Hook，即可立刻降低 75%（年省 1.09 亿 token）。

---

## 问题
当前 MCP 工具调用过于冗长：
- Session Hook：每次启动消耗 3,600-9,600 token。
- 检索 5 条：约 2,625 token。
- 文档摄取 50 PDF：57,400 token。
- 年浪费：1,700 万~3.79 亿 token。

## 方案
以 Python 接口替代 verbose 工具调用：
```python
# 之前（625 token）
await mcp.call_tool('retrieve_memory', {...})

# 之后（25 token）
from mcp_memory_service.api import search
results = search('architecture decisions', limit=5)
```

## 核心组件
1. **紧凑数据结构**（体积降 91%）。
2. **简洁同步 API**：`search/store/health`。
3. **Hook 集成**：JS 中优先 execSync，如失败再回退 MCP 工具。

## 影响
| 指标 | 现状 | 目标 | 提升 |
| --- | --- | --- | --- |
| Session Hook | 3,600-9,600 | 900-2,400 | -75% |
| 检索 5 条 | 2,625 | 385 | -85% |
| 写入 | 150 | 15 | -90% |
| 年节省（10 用户） | — | 1.095 亿 token | $16.43 |
| 年节省（100 用户） | — | 21.9 亿 token | $328.5 |

## roadmap
- **Week 1-2**：Compact 类型 + API + 测试。
- **Week 3**：Session Hook 改造（最高优先）。
- **Week 4-5**：搜索 Hook / Topic-change。
- **Week 6+**：完善与扩展。

目录结构新增 `src/mcp_memory_service/api/`，包含 `compact.py/search.py/storage.py/utils.py`。

## 研究 & 风险
- 对齐 Anthropic/CodeAgents 最新实践。
- NamedTuple 读取速度快、体积小。
- 风险低：并行运行、回退机制、<5ms 开销。

## 成功标准
- Phase1：API 可同步调用，节省≥85%，覆盖率≥90%。
- Phase2：Session Hook 生产节省≥75%，耗时<500ms，无用户投诉。
- Phase3：检索节省≥90%，有迁移文档与正向反馈。

## 下一步
1. 创建 `api/` 目录与 Compact 类型。
2. 实现 `search/store/health`。
3. 编写单测 + Token 基准。
4. 优先迁移 Session Hook。

完整研究参见 `docs/research/code-execution-interface-implementation.md`（架构、示例、迁移、指标）。

### Token 计算示例
```
当前：工具 Schema 125 + 820×5 = 4,225
新接口：导入 10 + 73×5 = 375
节省：91%
```

常用模式：
```python
from mcp_memory_service.api import search, search_by_tag, store, health
results = search("query", limit=5)
store("content", tags=['note'])
info = health()
```

**版本**：1.0（2025-11-06）— 准备实施，预期 2-3 周完成 Phase 1-2。
