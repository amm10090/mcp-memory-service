# 双服务部署（FastMCP + HTTP Dashboard）

## 架构概览
1. **FastMCP 服务**（端口 8001）：面向 Claude 等 MCP 客户端，JSON-RPC over SSE；
2. **HTTP Dashboard**（端口 8080）：Web 控制台与 REST API。

## 快速部署
```bash
./deploy_dual_services.sh
```
或手动：复制 systemd 单元 → `systemctl enable/start mcp-memory mcp-http-dashboard`。

## 访问
- MCP：`http://SERVER_IP:8001/mcp`
- Dashboard：`http://SERVER_IP:8080/`
- API：`/api/health`、`/api/memories`、`/api/search`

## 管理
```bash
sudo systemctl status|start|stop|restart mcp-memory mcp-http-dashboard
sudo journalctl -u mcp-memory -f
sudo journalctl -u mcp-http-dashboard -f
```

## mDNS
```bash
avahi-browse -t _http._tcp
avahi-browse -t _mcp._tcp
```
Advertise：`MCP Memory Dashboard._http._tcp.local.` / `MCP Memory FastMCP._mcp._tcp.local.`

## 依赖
`mcp`、`fastapi`、`uvicorn`、`zeroconf`、`aiohttp`、`sqlite-vec`、`sentence-transformers`。

## 配置
- `MCP_MEMORY_STORAGE_BACKEND=sqlite_vec`
- `MCP_MDNS_ENABLED=true`
- `MCP_HTTP_ENABLED=true`
- `MCP_SERVER_PORT=8001`
- `MCP_HTTP_PORT=8080`
- 数据库共用 `~/.local/share/mcp-memory/sqlite_vec.db`。

## 故障排查
- 无法访问：检查服务状态、端口监听、IP/防火墙；
- mDNS 失效：确认 `avahi-daemon` 与 `zeroconf` 依赖；
- FastMCP 异常：确保访问 `/mcp`，客户端支持 SSE/JSON-RPC。

## 客户端
- Claude：配置 MCP URL 为 `http://SERVER_IP:8001/mcp`；
- curl 示例：`curl http://SERVER_IP:8080/api/health`、POST `/api/memories`、`/api/search`。

✅ 纯 Python 实现，规避 Node SSL；✅ MCP + HTTP 双协议；✅ systemd/ mDNS 生产可用。EOF
