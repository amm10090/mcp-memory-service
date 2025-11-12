# Hooks 故障排查速查表

## SessionEnd Hook
- 触发：`/exit`、终端/窗口关闭、正常退出；
- 不触发：单/双次 Ctrl+C（仅挂起）。

**没写入的常见原因：**
1. Ctrl+C 退出 → 使用 `/exit`；
2. 协议不一致 → `/exit` 时写入失败；
3. 会话内容不足（<100 字或置信度 <0.1）。

快速自检：
```bash
curl -sk https://localhost:8000/api/search/by-tag -d '{"tags":["session-consolidation"],"limit":5}'
node ~/.claude/hooks/core/session-end.js
```

## SessionStart Hook
**症状**：连续三次 “MCP Fallback”、`No relevant memories`。
**根因**：HTTP/HTTPS 配置与服务器不一致。

排查：
```bash
grep HTTPS_ENABLED .env
curl -s http://127.0.0.1:8000/api/health      # HTTP
curl -sk https://127.0.0.1:8000/api/health    # HTTPS
```
若服务器为 HTTPS，配置需改为 `https://...` 并重启会话。

## Windows SessionStart Bug
[#160] Claude 在 Windows 上启动时卡死，建议：
- 使用 `/session-start` 命令；
- 暂时禁用 SessionStart Hook；
- 改用 UserPromptSubmit Hook。

## 端口/协议同步
```bash
netstat -ano | findstr 8000    # Windows
lsof -i :8000                  # Linux/macOS
grep endpoint ~/.claude/hooks/config.json
```
端口不一致会导致连接超时、Hook 无响应。

## Schema 变更后缓存问题
PR 合并后需重启 MCP Server，否则客户端仍用旧 schema。
```bash
/mcp
systemctl --user restart mcp-memory-http.service
```

## 紧急调试
```bash
/mcp                                         # 查看活跃 MCP
python scripts/validation/diagnose_backend_config.py
rm -f .mcp.json                              # 清理冲突配置
tail -50 ~/Library/Logs/Claude/mcp-server-memory.log
```

更多细节：参阅 `docs/troubleshooting/session-end-hooks.md`、`docs/troubleshooting/pr162-schema-caching-issue.md`、`docs/http-server-management.md`。
