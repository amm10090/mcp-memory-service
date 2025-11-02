# SessionEnd Hook 故障排查指南

## 概览

SessionEnd Hook 会在退出 Claude Code 会话时自动整合对话结论。但许多用户对 **何时触发** 以及 **为何未生成记忆** 感到困惑。本文旨在澄清会话生命周期并给出常见问题排查方案。

---

## 关键概念：会话生命周期

Claude Code 区分 **暂停/挂起** 与 **终止**：

| 用户操作 | 会话状态 | 触发 Hook | 是否创建记忆 |
| --- | --- | --- | --- |
| **Ctrl+C（一次）** | 中断输入 | 无 | ❌ 否 |
| **Ctrl+C（两次）** | 挂起会话 | 无 | ❌ 否 |
| **恢复会话** | 继续已有会话 | `SessionStart:resume` | ❌ 否 |
| **`/exit` 命令** | 终止会话 | `SessionEnd` | ✅ 是 |
| **关闭终端窗口** | 终止会话 | `SessionEnd` | ✅ 是 |
| **Kill 进程** | 可能终止 | 若能优雅退出则触发 | ⚠️ 不确定 |

> **结论**：**Ctrl+C 不会触发 SessionEnd Hook**，它只是在挂起当前会话。只有真正终止（如 `/exit`）才会触发并写入记忆。

---

## 常见问题：未生成 Session 记忆

### 症状

使用 Ctrl+C 退出并稍后恢复，发现没有生成 `session-consolidation` 记忆。

### 原因

Ctrl+C 只是挂起会话，并未结束；恢复时会触发 `SessionStart:resume`，表示继续已有会话，因此不会执行 SessionEnd。

### 解决

希望记录会话总结时，请使用 `/exit`：

```bash
/exit
```

此操作会优雅终止会话并执行 SessionEnd Hook。

---

## 常见问题：连接失败

### 症状

SessionStart 时出现：
```
⚠️ Memory Connection → Failed to connect using any available protocol
💾 Storage → 💾 Unknown Storage (http://127.0.0.1:8000)
```

### 原因

Hook 配置的协议与服务器实际协议不匹配，例如服务器启用 HTTPS，而 Hook 使用 HTTP。

### 排查

1. **查看服务器协议**：
   ```bash
   systemctl --user status mcp-memory-http.service
   # 查看日志是否显示 https:// 或 http://
   curl -sk "https://localhost:8000/api/health"
   ```

2. **检查 Hook 配置**：
   ```bash
   grep endpoint ~/.claude/hooks/config.json
   # 确保与实际协议一致
   ```

### 解决

将 `~/.claude/hooks/config.json` 中的 `endpoint` 调整为正确的协议：

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

无需重启，Hook 下次运行会自动应用新配置。

---

## SessionEnd 触发后的必要条件

即便 SessionEnd 成功触发，记忆生成仍需要满足：

1. **会话长度 ≥ 100 字符**（默认，可在 `config.json` 的 `sessionAnalysis.minSessionLength` 中调整）；
2. **分析置信度 > 0.1**（对话内容需足够具体，否则视为无效）；
3. **已开启会话整合**：
   ```json
   {
     "memoryService": {
       "enableSessionConsolidation": true
     }
   }
   ```

### 提取内容包括

- **Topics**：例如 “implementation”、“debugging”；
- **Decisions**：如 “decided to”、“chose to”；
- **Insights**：如 “learned that”、“realized”；
- **Code Changes**：如 “implemented”、“refactored”；
- **Next Steps**：如 “next we need”、“TODO”。

若对话中缺少这些模式，则置信度可能过低而导致不生成记忆。

---

## 验证与调试

### 1. 检查近期 Session 记忆

```bash
curl -sk "https://localhost:8000/api/search/by-tag" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["session-consolidation"], "limit": 5}' | \
  python -m json.tool | grep created_at_iso
```

确认最近是否存在新记录。

### 2. 手动触发 Hook

```bash
node ~/.claude/hooks/core/session-end.js
```

期望输出：
- `[Memory Hook] Session ending - consolidating outcomes...`
- `[Memory Hook] Session analysis: ...`
- `[Memory Hook] Session consolidation stored successfully`

### 3. 检查配置

```bash
curl -sk "https://localhost:8000/api/health"
grep endpoint ~/.claude/hooks/config.json
```

---

## 其他注意事项

- 为避免误挂起，可在惯用流程中使用 `/exit`；
- 若在多终端/多客户端场景，确认所有客户端的 Hook 配置一致；
- 在记录高价值会话前，可手动执行 `memory` 工具进行存储，以防因条件不满足而遗漏。

---

如需进一步排查，可查看主仓库 `README`、`CLAUDE.md` 或执行诊断脚本：

```bash
python scripts/validation/diagnose_backend_config.py
```
