# 远程服务器配置（Wiki 章节）

本节可直接放入 Wiki 的 **03 Integration Guide** 页面，在 “1. Claude Desktop Integration” 章节下作为远程部署指引。

---

## 远程服务器配置

当希望让 Claude Desktop 或 Cursor 连接远程运行的 MCP Memory Service（例如 VPS、独立服务器或另一台电脑）时，可以使用仓库附带的 HTTP-to-MCP Bridge（HTTP→MCP 网桥）。

### 快速上手

MCP Memory Service 内置一个 Node.js 网桥，将 HTTP API 调用转换为 MCP 协议消息，从而允许远程客户端接入。

**Claude Desktop 示例配置：**

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["/path/to/mcp-memory-service/examples/http-mcp-bridge.js"],
      "env": {
        "MCP_HTTP_ENDPOINT": "https://your-server:8000/api",
        "MCP_MEMORY_API_KEY": "your-secure-api-key"
      }
    }
  }
}
```

### 配置选项

#### 手动指定端点（推荐：远程服务器）

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["/path/to/mcp-memory-service/examples/http-mcp-bridge.js"],
      "env": {
        "MCP_HTTP_ENDPOINT": "https://your-server:8000/api",
        "MCP_MEMORY_API_KEY": "your-secure-api-key",
        "MCP_MEMORY_AUTO_DISCOVER": "false",
        "MCP_MEMORY_PREFER_HTTPS": "true"
      }
    }
  }
}
```

#### 自动发现（适用于局域网）

```json
{
  "mcpServers": {
    "memory": {
      "command": "node",
      "args": ["/path/to/mcp-memory-service/examples/http-mcp-bridge.js"],
      "env": {
        "MCP_MEMORY_AUTO_DISCOVER": "true",
        "MCP_MEMORY_PREFER_HTTPS": "true",
        "MCP_MEMORY_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 步骤化设置指南

1. **下载 HTTP 网桥**
   - 将 [`examples/http-mcp-bridge.js`](https://github.com/doobidoo/mcp-memory-service/blob/main/examples/http-mcp-bridge.js) 复制到本地。

2. **更新配置文件**
   - 打开 Claude Desktop 配置：
     - **macOS**：`~/Library/Application Support/Claude/claude_desktop_config.json`
     - **Windows**：`%APPDATA%\Claude\claude_desktop_config.json`
   - 按上文示例添加远程配置。
   - 将 `/path/to/mcp-memory-service/examples/http-mcp-bridge.js` 替换为本机实际路径。
   - 将 `https://your-server:8001/api` 替换为远程服务器地址。
   - 将 `your-secure-api-key` 替换为真实的 API Key。

3. **验证连接**
   - 重启 Claude Desktop。
   - 运行一次简单的 memory 操作测试连接。
   - 查看网桥日志，排查潜在连接问题。

### 网桥特性概览

HTTP-to-MCP Bridge 支持以下能力：

- ✅ **手动端点配置**：直接指向远程服务器。
- ✅ **API Key 认证**：确保内外网访问安全。
- ✅ **自签名证书 HTTPS**：兼容开发环境 SSL。
- ✅ **mDNS 自动发现**：可在本地网络自动发现服务。
- ✅ **重试与错误处理**：提升连接稳定性。
- ✅ **详细日志**：方便排障与审计。

### 环境变量参考

| 变量 | 说明 | 默认值 | 示例 |
| --- | --- | --- | --- |
| `MCP_HTTP_ENDPOINT` | 远程服务器 API 端点（流式 HTTP 位于 `/mcp`，REST 位于 `/api`） | `http://localhost:8001/api` | `https://myserver.com:8001/api` |
| `MCP_MEMORY_API_KEY` | 客户端网桥使用的认证 Token（服务器端键为 `MCP_API_KEY`） | 无 | `abc123xyz789` |
| `MCP_MEMORY_AUTO_DISCOVER` | 是否启用 mDNS 服务发现 | `false` | `true` |
| `MCP_MEMORY_PREFER_HTTPS` | 服务发现时优先使用 HTTPS | `true` | `false` |

### 远程连接故障排查

#### Connection Refused（连接被拒绝）

- **现象**：网桥无法连接远程服务器。
- **解决方案**：
  - 确认服务器已启动且能被访问。
  - 检查防火墙是否放行 8001 端口。
  - 再次确认端点 URL 是否正确。
  - 使用 `curl https://your-server:8001/api/health` 测试健康检查。

#### SSL Certificate Issues（证书问题）

- **现象**：HTTPS 连接出现 SSL 报错。
- **解决方案**：
  - 网桥默认接受自签名证书，可直接使用。
  - 确认服务器启用了 HTTPS。
  - 检查服务器日志，排查证书配置。

#### API Key Authentication Failed（认证失败）

- **现象**：服务器返回 401 Unauthorized。
- **解决方案**：
  - 确认服务端已正确设置 API Key。
  - 检查网桥环境变量中的 Key 是否一致。
  - 确保 Key 字符串无额外空格或换行。

#### Service Discovery Not Working（服务发现失败）

- **现象**：自动发现无法找到服务。
- **解决方案**：
  - 改用手动端点配置。
  - 确认两台设备处于同一网络。
  - 检查网络是否开启 mDNS/Bonjour。

#### Bridge Logs Not Appearing（日志缺失）

- **现象**：看不到网桥日志。
- **解决方案**：
  - 网桥日志输出到 Claude Desktop 控制台 / stderr。
  - macOS 使用 Console.app 读取日志。
  - Windows 通过 Event Viewer，或命令行启动 Claude Desktop 查看输出。

### 完整示例文件

如需完整示例，请参考：

- [`examples/claude-desktop-http-config.json`](https://github.com/doobidoo/mcp-memory-service/blob/main/examples/claude-desktop-http-config.json)：完整配置模板。
- [`examples/http-mcp-bridge.js`](https://github.com/doobidoo/mcp-memory-service/blob/main/examples/http-mcp-bridge.js)：带注释的网桥实现。
