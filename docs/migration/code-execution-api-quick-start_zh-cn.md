# Code Execution API：5 分钟极速上手

**5 分钟内从 “MCP 工具可用” 迁移到 “全面启用代码执行”。**

---

## 为何要迁移？（30 秒）

Code Execution API 相比 MCP 工具调用可节省 **75-90% Token**，显著降低成本：

| 用户数 | 会话/日 | 年度 Token 节省 | 年度成本节省* |
|--------|---------|-----------------|----------------|
| 10 | 5 | 1.095 亿 | $16.43 |
| 50 | 8 | 8.76 亿 | $131.40 |
| 100 | 10 | 21.9 亿 | $328.50 |

**核心收益**：
- **无需改代码**，现有工作流原样使用；
- **自动回退 MCP**，失败也不会中断；
- **功能一致**，成本骤降；
- **执行更快**，冷启动 50ms vs MCP 250ms。

\* 以 Claude Opus 输入价 $0.15 / 百万 tokens 估算。

---

## 前置条件（30 秒）

- 已安装 mcp-memory-service（任意版本）；
- Python ≥ 3.10；
- 5 分钟空闲时间。

```bash
python --version  # 或 python3 --version
```

---

## 快速开始

### A. 全新安装（2 分钟）

```bash
git clone https://github.com/doobidoo/mcp-memory-service.git
cd mcp-memory-service
git pull  # 已克隆时更新

python scripts/installation/install.py  # v8.19.0+ 默认启用代码执行
```

> 安装器会自动在 Claude Code hooks 中启用代码执行，无需额外配置。

### B. 既有安装（3 分钟）

```bash
cd /path/to/mcp-memory-service
git pull
pip install -e .
python --version  # 确认 >=3.10
```

若未自动开启，编辑 `~/.claude/hooks/config.json`：
```json
{
  "codeExecution": {
    "enabled": true,
    "timeout": 8000,
    "fallbackToMCP": true,
    "enableMetrics": true,
    "pythonPath": "python3"  // Windows 可写 "python"
  }
}
```

v8.19.0+ 默认开启，旧版本升级后安装器会提示是否启用。

---

## 验证（1 分钟）

```bash
python -c "from mcp_memory_service.api import search, health; print(health())"
```

期望输出：`CompactHealthInfo(status='healthy', count=1247, backend='sqlite_vec')`

Hook 日志应出现：
```
✅ Using code execution (75% token reduction)
📊 search() returned 5 results (385 tokens vs 2,625 MCP tokens)
```

---

## 迁移后发生了什么？

- Session hook 自动调用 Python API，**会话 Token -75%**；
- MCP 工具保留，失败时自动回退；
- 原有流程、搜索质量、存储行为完全一致。

```
Before: Claude Code → MCP → Memory Server （5 条结果 2,625 tokens）
After : Claude Code → Python API → Memory Server （5 条结果 385 tokens）
```

---

## 常见问题（1 分钟）

### “⚠️ Code execution failed, falling back to MCP”
- 检查 Python ≥3.10：`python --version`
- 确保 API 已安装：
  ```bash
  python -c "import mcp_memory_service.api" || pip install -e .
  ```
- 校验配置：`grep -A5 codeExecution ~/.claude/hooks/config.json`

### `ModuleNotFoundError`
```bash
cd /path/to/mcp-memory-service
pip install -e .
```

### 超时
在配置中增大 `timeout`，例如 15000ms。

### Token 未下降
- 再次确认 `enabled=true`；
- 重启 Claude Code；
- 查看日志是否出现 “Using code execution”。

---

## 性能基准

| 操作 | MCP Tokens | Code Tokens | 节省 |
|------|------------|-------------|------|
| search(5) | 2,625 | 385 | 85% |
| store | 150 | 15 | 90% |
| health | 125 | 20 | 84% |
| Session hook | 3,600 | 900 | 75% |

执行耗时：
- 冷启动：MCP 250ms → Code 50ms；
- 暖调用：MCP 100ms → Code 5-10ms。

---

## 成本计算

- **个人（10 会话/日）**：9.86M tokens/年，≈$1.48；
- **小团队（5 人 × 8 会话）**：39.42M tokens/年，≈$5.91；
- **50 人团队（10 会话）**：492.75M tokens/年，≈$73.91；
- **500 人组织（12 会话）**：5.91B tokens/年，≈$886.50。

---

## 下一步

1. **开启指标**：`"enableMetrics": true`，日志会输出每次节省的 Token；
2. **深入使用 API**：
   ```python
   from mcp_memory_service.api import search, store, health
   hash = store("memory", tags=["note"], memory_type="reminder")
   results = search("architecture", limit=10, tags=["important"])
   print(health())
   ```
3. **阅读文档**：`docs/api/code-execution-interface.md`、`docs/hooks/phase2-code-execution-migration.md`；
4. **关注 Issue #206** 获取更新。

---

## 回滚

```json
"codeExecution": { "enabled": false }
```
重启 Claude Code，确保日志出现 “Using MCP tools”。仍可在 GitHub Issue #206 提交问题。

---

## FAQ（精选）

- **需要改代码吗？** 不需要。
- **失败会怎样？** 自动回退 MCP，最多多用些 Token。
- **能同时用 MCP 和 Code Execution 吗？** 可以，两者并存。
- **如何量化节省？** 启用 metrics，查看 Hook 日志。
- **Windows 支持？** 有，`pythonPath` 设为 `python`。
- **能先试后用吗？** 可以，启用后跑一场会话，再视情况关闭。

---

## 成功判据

- 日志出现 “Using code execution”；
- 每次会话 Token ≈ 900，而非 3,600；
- Hook 更快（<100ms 冷启动）；
- 无错误或回退警告。

**示例**：
```
🔧 Session start hook: 900 tokens, 50ms
💡 Saved 2,700 tokens vs MCP tools
```

---

## 支持

- 文档：`docs/api/`、`docs/hooks/`
- GitHub：提交 Issue（附日志 & 配置）
- 项目 Wiki：<https://github.com/doobidoo/mcp-memory-service/wiki>
