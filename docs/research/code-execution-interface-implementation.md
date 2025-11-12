# 代码执行接口实施研究
## Issue #206：实现 90-95% Token 降耗的路线

- **研究日期**：2025-11-06  
- **目标**：为 mcp-memory-service 提供 Python 代码 API，将 token 消耗降低 90%-95%  
- **状态**：架构研究阶段

---

## 执行摘要
本报告结合业界趋势、内部代码架构与实验数据，给出将 MCP 工具调用迁移至“代码执行接口”的完整方案。研究表明：
1. 通过代码执行可稳定削减 75%-90% token；
2. Anthropic 在 2025-11 正式宣告 MCP 代码执行能力，与本项目方向一致；
3. Python interpreter MCP、CodeAgents 等实践证明该模式可行；
4. 现有代码层次清晰，可平滑并行旧接口与新接口。

---

## 1. 现状分析
- **工具数量**：33 个 MCP 工具，每次调用约附加 125 token 的 schema；
- **Session Hook**：单次启动 3,600-9,600 token；
- **检索 5 条**：约 2,625 token；
- **PDF 摄取 50 份**：约 57,400 token；
- **年度浪费**：1,700 万～3.79 亿 token（不同用户规模）。

架构优势：`MemoryStorage` 抽象、异步实现、丰富后端（SQLite-vec/Cloudflare/Hybrid）、HTTP Client 等已有模式，为新增 API 奠定基础。

---

## 2. 研究最佳实践
1. **结构化代码** 取代自然语言：Typed 结构、控制流、函数复用可大幅压缩 token；
2. **紧凑数据类型**：使用 `NamedTuple` 返回必要字段，可将单条记忆从 500-800 token 降至 70 左右；
3. **渐进迁移**：从 Session Hook 等高收益场景起步；保持向后兼容，提供 feature flag、文档与度量。

---

## 3. 架构建议
```
src/mcp_memory_service/
├── api/                 # 新增代码执行接口
│   ├── compact.py       # CompactMemory 等类型
│   ├── search.py        # search/search_by_tag/recall
│   ├── storage.py       # store/delete/update
│   └── utils.py         # health/expand_memory 等
├── models/
│   ├── memory.py        # 现有完整模型
│   └── compact.py       # 新的轻量类型
└── server.py            # 继续保留，兼容 MCP
```

### 3.1 紧凑类型示例
```python
class CompactMemory(NamedTuple):
    hash: str
    preview: str
    tags: tuple[str, ...]
    created: float
    score: float = 0.0
```
- 仅约 73 token（对比完整 Memory 约 820 token，缩减 91%）；
- 不变性确保 Hook 并发安全；
- 提供 `CompactSearchResult`、`CompactStorageInfo` 等衍生类型。

### 3.2 API 入口
`api/__init__.py` 统一导出：
```python
from mcp_memory_service.api import search, search_by_tag, recall,
    store, delete, update, health, expand_memory
```
- 导入成本约 10 token，仅首次执行；
- 同步封装隐藏 asyncio；
- `_get_storage()` 重用连接，初始化一次即可。

---

## 4. 相关项目的佐证
- **MCP Python Interpreter（2024）**：以代码执行替代多工具暴露，具备沙箱与读写能力；
- **CodeAgents 框架**：通过 typed 变量、可复用子程序等方式展示 70% 以上的节省；
- **Anthropic 官方示例**：同样建议以 `from ... import ...` 替代工具 schema。

---

## 5. 潜在挑战与对策
| 挑战 | 说明 | 缓解措施 |
| --- | --- | --- |
| Async/Sync 不匹配 | 后端 async，Hook 多为同步 | 提供 `asyncio.run()` 封装，同步 API |
| 连接复用 | 频繁创建实例浪费资源 | `_storage_instance` 缓存一次初始化 |
| 兼容老用户 | 现有 MCP 工具仍在使用 | 并行运行、fallback、文档迁移 |
| 紧凑模式调试 | 字段少，定位困难 | `expand_memory()`、`health()` 等调试工具 |
| 大结果集性能 | 批量转换成本高 | `search_iter()` 流式迭代，提前截断 |

---

## 6. 推荐工具
- **Type 校验**：可选 Pydantic v2；API 内部仍以 NamedTuple 保持轻量；
- **测试**：`pytest-asyncio` + tiktoken 统计 token；
- **文档**：Sphinx autodoc，Docstring 直接嵌入 token/性能信息；
- **日志**：structlog 记录时延、token 估算等指标。

---

## 7. 渐进式迁移
1. **Phase 1（周 1-2）**：搭建 `api/` 模块、Compact 类型、`search/store/health` 等函数；完成 90%+ 覆盖率测试与基准数据。
2. **Phase 2（周 3）**：Session Hook 率先改造，启用 Python exec，失败回退 MCP。目标：token 降 75%，Hook 耗时 <500ms。
3. **Phase 3（周 4-5）**：中途检索/Topic-change Hook，补充 `search_by_tag/recall`、流式检索。
4. **Phase 4（周 6+）**：批量写入、文档摄取、记忆合并等拓展 API。

---

## 8. 成功指标
| 操作 | 现状 | 目标 | 降幅 |
| --- | --- | --- | --- |
| Session Hook | 3,600-9,600 | 900-2,400 | 75% |
| 5 条检索 | 2,625 | 385 | 85% |
| Store | 150 | 15 | 90% |
| Health | 125 | 20 | 84% |
| 50 PDF 摄取 | 57,400 | 8,610 | 85% |

年度节省（保守）10 用户：1.095 亿 token；100 用户可达 21.9 亿（约 $328/年，按 $0.15/M token）。

---

## 9. 时间线（摘要）
```
Week 1-2：API 基础、测试、文档草案
Week 3：Session Hook 改造 + Beta 验证
Week 4-5：其它 Hook / 检索场景迁移
Week 6+：扩展 API、性能优化、开发者工具
```

---

## 10. 总结性建议
1. 立即创建 `api/` 模块并实现 Compact 类型 + 核心函数；
2. 以 `NamedTuple + 同步封装` 保持简单与高效；
3. Session Hook 作为首个生产用例，提供回退机制；
4. 持续记录 token/性能指标，输出迁移指引。

预期结果：Session Hook token 降 75%，检索降 85% 以上，年度节省 1,300 万～1.8 亿 token，且与现有 MCP 工具 100% 兼容。

---

## 11. 参考资料
- Anthropic《Code execution with MCP》《Claude Code Best Practices》；
- arXiv《CodeAgents: A Token-Efficient Framework for Codified Multi-Agent Reasoning》；
- Python 类型与性能对比（dataclass vs NamedTuple）；
- MCP python-interpreter / LangChain Compact patterns 等开源实现；
- 项目内文件：`storage/base.py`、`models/memory.py`、`server.py`、`claude-hooks/core/session-start.js`。

---

## 结束语
研究表明：在保持兼容的前提下，通过“代码执行接口 + 紧凑类型”即可实现显著 token 降耗与成本收益。建议立即执行 Phase 1 任务，并以 Session Hook 作为首个落地场景，快速验证与迭代。

