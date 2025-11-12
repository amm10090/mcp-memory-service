# HTTP 服务器管理指南

MCP Memory Service 的 HTTP 服务器是 **Claude Code Hooks（Natural Memory Triggers）正常工作的前提**。本指南说明如何检查、启动与自动化该服务器。

## 为什么需要 HTTP 服务器？

启用 **Natural Memory Triggers** 时：
- 会话启动 Hook 需通过 HTTP 服务拉取相关记忆。
- 若 HTTP 未运行，Hook 会静默失败，记忆无法注入。
- 通过 HTTP 协议可避免与 Claude Code 内置 MCP 服务冲突。

## 检查运行状态

```bash
uv run python scripts/server/check_http_server.py      # 默认：详细输出
uv run python scripts/server/check_http_server.py -q   # 仅返回码，适合脚本
```

**运行中示例：**
```
[OK] HTTP server is running
   Version: 8.3.0
   Endpoint: http://localhost:8000/api/health
   Status: healthy
```

**未运行示例：**
```
[ERROR] HTTP server is NOT running
To start the HTTP server, run:
   uv run python scripts/server/run_http_server.py
   MCP_HTTPS_ENABLED=true uv run python scripts/server/run_http_server.py
Error: [WinError 10061] ...
```

## 启动服务器

```bash
uv run python scripts/server/run_http_server.py                   # HTTP (8001)
MCP_HTTPS_ENABLED=true uv run python scripts/server/run_http_server.py   # HTTPS (8443)
```

### 自动脚本
- Unix/macOS：`./scripts/server/start_http_server.sh`
- Windows：`scripts\server\start_http_server.bat`

特性：
- 启动前先检测已运行实例。
- 后台/新窗口执行，并校验成功。
- 输出日志位置与状态。

## 常见问题

### Hook 未注入记忆
1. `uv run python scripts/server/check_http_server.py`
2. 若未运行：`uv run python scripts/server/run_http_server.py`
3. 重启 Claude Code 触发 session-start hook。

### 端口/地址错误
- 默认 HTTP：`http://localhost:8001`。
- 若配置端口不一致，需统一 `hooks` 配置或调整 `.env` 中 `MCP_HTTP_PORT`。

```bash
# Hooks 配置检查
cat ~/.claude/hooks/config.json | grep -A5 "http"
```

### 启动失败
- 端口占用：`lsof -i :8001` / `netstat -ano | findstr :8001`。
- 依赖缺失/配置错误：查看日志 `tail -f /tmp/mcp-http-server.log` 或窗口输出。

## 与 Hooks 的协作

Claude Code session-start hook 会：
1. 优先连接 HTTP。
2. 若失败，回退 MCP。
3. 若仍失败，仅使用环境上下文。

推荐配置（`~/.claude/hooks/config.json`）：
```json
{
  "memoryService": {
    "protocol": "http",
    "preferredProtocol": "http",
    "http": {
      "endpoint": "http://localhost:8001",
      "healthCheckTimeout": 3000
    }
  }
}
```

## 自动化

### macOS launchd
创建 `~/Library/LaunchAgents/com.mcp.memory.http.plist`（路径替换为仓库真实路径）：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mcp.memory.http</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/repository/scripts/server/start_http_server.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### Windows 任务计划
- 触发：登录时。
- 操作：启动 `scripts\server\start_http_server.bat`。

### Shell 快捷命令
```bash
alias claude-code='/path/to/repository/scripts/server/start_http_server.sh && claude'
```

### Linux systemd（推荐）
```bash
bash scripts/service/install_http_service.sh
systemctl --user start mcp-memory-http.service
systemctl --user enable mcp-memory-http.service
loginctl enable-linger $USER
```

常用命令：
```bash
systemctl --user status mcp-memory-http.service
journalctl --user -u mcp-memory-http.service -f
curl http://127.0.0.1:8001/api/health
```

## 参考
- [Claude Code Hooks 配置](../CLAUDE.md#claude-code-hooks-configuration-)
- [Natural Memory Triggers](../CLAUDE.md#natural-memory-triggers-v710-latest)
- [Wiki 故障排查](https://github.com/doobidoo/mcp-memory-service/wiki/07-TROUBLESHOOTING)
