# 双协议记忆 Hook（Legacy）

> 已被 Natural Memory Triggers v7.1.3+ 取代，此文档仅作存档。

Dual Protocol Hooks (v7.0.0+) 会自动选择 MCP ↔ HTTP ↔ 环境兜底，配置示例：
```json
{
  "memoryService": {
    "protocol": "auto",
    "preferredProtocol": "mcp",
    "fallbackEnabled": true,
    "http": {
      "endpoint": "https://localhost:8443",
      "apiKey": "your-api-key",
      "healthCheckTimeout": 3000,
      "useDetailedHealthCheck": true
    },
    "mcp": {
      "serverCommand": ["uv", "run", "memory", "server", "-s", "cloudflare"],
      "serverWorkingDir": "/path/to/mcp-memory-service",
      "connectionTimeout": 5000,
      "toolCallTimeout": 10000
    }
  }
}
```

## 协议策略
- `auto`：MCP → HTTP → 环境兜底；
- `http`：仅 HTTP；
- `mcp`：仅直接 MCP。

## 特性回顾
- 多协议兜底提高可靠性；
- 本地可走 MCP，远端可走 HTTP；
- 与旧配置兼容。

## 迁移建议
建议迁移到 Natural Memory Triggers v7.1.3+，获得：85%+ 触发准确率、多层性能管理、CLI 设置、Git 感知与自适应学习。详见主 `CLAUDE.md`。
