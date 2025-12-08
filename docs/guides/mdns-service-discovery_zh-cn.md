# mDNS 服务发现指南

本文介绍 MCP Memory Service 自 v2.1.0 引入的 mDNS（Multicast DNS）自动发现能力，帮助你实现零配置网络接入。

## 概览

借助 mDNS，MCP Memory Service 可以：

- **自动广播** 服务信息到本地网络；
- **自动发现** 可用实例，无需手动填写地址；
- **优先使用安全连接**（HTTPS 优先于 HTTP）；
- **连接前先行校验健康状态**，确保服务可用。

## 快速上手

### 1. 启动启用 mDNS 的服务

```bash
# 基础运行（默认启用 mDNS）
python scripts/run_http_server.py

# 启用 HTTPS（自动生成证书）
export MCP_HTTPS_ENABLED=true
python scripts/run_http_server.py

# 自定义服务名称
export MCP_MDNS_SERVICE_NAME="Team Memory Service"
python scripts/run_http_server.py
```

### 2. 配置客户端自动发现

**Claude Desktop 配置示例：**

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

完成上述配置后，客户端即可自动发现并连接可用服务。

## 配置参考

### 服务器端

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MCP_MDNS_ENABLED` | `true` | 是否启用 mDNS 广播 |
| `MCP_MDNS_SERVICE_NAME` | `"MCP Memory Service"` | 在网络中的展示名称 |
| `MCP_MDNS_SERVICE_TYPE` | `"_mcp-memory._tcp.local."` | 符合 RFC 的服务类型 |
| `MCP_MDNS_DISCOVERY_TIMEOUT` | `5` | 客户端发现超时时间（秒） |

### 客户端

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MCP_MEMORY_AUTO_DISCOVER` | `false` | 是否启用自动发现 |
| `MCP_MEMORY_PREFER_HTTPS` | `true` | 是否优先选择 HTTPS |
| `MCP_HTTP_ENDPOINT` | （无） | 回退的手动指定端点 |
| `MCP_MEMORY_API_KEY` | （无） | 访问认证所需的 API 密钥 |

## HTTPS 集成

### 自动生成证书

开发环境可自动生成自签名证书：

```bash
export MCP_HTTPS_ENABLED=true
python scripts/run_http_server.py
```

示例日志：
```
Generating self-signed certificate for HTTPS...
Generated self-signed certificate: /tmp/mcp-memory-certs/cert.pem
WARNING: This is a development certificate. Use proper certificates in production.
Starting MCP Memory Service HTTPS server on 0.0.0.0:8000
mDNS service advertisement started
```

### 自带证书

生产环境请使用受信任证书：

```bash
export MCP_HTTPS_ENABLED=true
export MCP_SSL_CERT_FILE="/path/to/your/cert.pem"
export MCP_SSL_KEY_FILE="/path/to/your/key.pem"
python scripts/run_http_server.py
```

## 服务发现流程

### 客户端流程

1. **发现阶段**：广播 `_mcp-memory._tcp.local.` 查询；
2. **收集响应**：接收所有服务端的反馈；
3. **优先级排序**：基于以下顺序筛选：
   - 是否支持 HTTPS（若 `MCP_MEMORY_PREFER_HTTPS=true`）
   - 健康检查结果
   - 响应耗时
   - 端口偏好
4. **健康校验**：调用 `/api/health` 验证服务状态；
5. **建立连接**：选择最优服务完成连接。

### 服务器广播信息

服务器以以下元数据对外发布：

- **服务类型**：`_mcp-memory._tcp.local.`
- **属性字段**：
  - `api_version`：服务器版本；
  - `https`：是否启用 HTTPS；
  - `auth_required`：是否需要 API 密钥；
  - `api_path`：API 基路径（`/api`）；
  - `sse_path`：SSE 事件流路径（`/api/events`）；
  - `docs_path`：文档路径（`/api/docs`）。

## 网络要求

### 防火墙配置

确保允许 mDNS 流量：

```bash
# Linux (UFW)
sudo ufw allow 5353/udp

# Linux (iptables)
sudo iptables -A INPUT -p udp --dport 5353 -j ACCEPT

# macOS/Windows：默认已放行 mDNS
```

### 网络拓扑

mDNS 在以下场景可用：

- ✅ 局域网（LAN）
- ✅ WiFi 网络
- ✅ 支持多播的 VPN
- ❌ 跨子网（除非配置 mDNS relay）
- ❌ 互联网（设计上仅限本地网络）

## 故障排查

### 常见问题

#### 未发现任何服务

**日志症状：**
```
Attempting to discover MCP Memory Service via mDNS...
No MCP Memory Services discovered
Using default endpoint: http://localhost:8000/api
```

**解决思路：**
1. 确认服务已启动且启用 mDNS：
   ```bash
   grep "mDNS service advertisement started" server.log
   ```
2. 检查网络连通性：
   ```bash
   ping 224.0.0.251
   ```
3. 检查防火墙规则：
   ```bash
   sudo ufw status | grep 5353
   ```

#### 发现超时

**日志症状：**
```
Discovery failed: Request timeout
```

**解决思路：**
1. 增加超时时间：
   ```bash
   export MCP_MDNS_DISCOVERY_TIMEOUT=10
   ```
2. 检查网络延迟；
3. 确认网络支持多播。

#### 连接到非预期服务

**现象：** 客户端优先连接 HTTP 而非 HTTPS。

**解决思路：**
1. 强制 HTTPS 优先（客户端桥）：
   ```bash
   export MCP_MEMORY_PREFER_HTTPS=true
   ```
2. 手动指定服务端点：
   ```bash
   export MCP_MEMORY_AUTO_DISCOVER=false
   export MCP_HTTP_ENDPOINT="https://preferred-server:8000/api"
   ```

### 调试模式

开启详细日志：

**服务器：**
```bash
export LOG_LEVEL=DEBUG
python scripts/run_http_server.py
```

**客户端：**
```bash
node examples/http-mcp-bridge.js 2>discovery.log
```

### 手动测试发现

**macOS：**
```bash
# 浏览可用服务
dns-sd -B _mcp-memory._tcp

# 解析特定服务
dns-sd -L "MCP Memory Service" _mcp-memory._tcp
```

**Linux：**
```bash
# 浏览服务
avahi-browse -t _mcp-memory._tcp

# 解析主机名
avahi-resolve-host-name hostname.local
```

## 高级用法

### 多服务环境

为不同环境部署独立服务：

```bash
# 开发环境
export MCP_MDNS_SERVICE_NAME="Dev Memory Service"
export MCP_HTTP_PORT=8000
python scripts/run_http_server.py &

# 预发布环境
export MCP_MDNS_SERVICE_NAME="Staging Memory Service"
export MCP_HTTP_PORT=8001
python scripts/run_http_server.py &
```

客户端将同时发现两者，可按需选择。

### 负载分担

面对多个相同服务实例，客户端会基于：
1. 健康检查响应时间；
2. 连接成功率；
3. 在健康实例间轮询，自动分摊请求量。

### 服务监控

可编程方式查看已发现服务：

```python
import asyncio
from mcp_memory_service.discovery import DiscoveryClient

async def monitor_services():
    client = DiscoveryClient()
    services = await client.find_services_with_health()
    
    for service, health in services:
        print(f"Service: {service.name} at {service.url}")
        print(f"Health: {'✅' if health.healthy else '❌'}")
        print(f"Response time: {health.response_time_ms:.1f}ms")
        print()

asyncio.run(monitor_services())
```

## 安全注意事项

### 网络安全

1. **仅限本地网络**：mDNS 默认不会跨互联网；
2. **网络隔离**：需要时可通过 VLAN 控制发现范围；
3. **防火墙规则**：仅在受信网段开放 mDNS。

### 认证

即便在本地网络，也建议启用 API Key：

```bash
# 服务器端
export MCP_API_KEY="$(openssl rand -base64 32)"

# 客户端（Node 桥）
export MCP_MEMORY_API_KEY="same-key-as-server"
```

### 加密

启用 HTTPS 以确保通信安全：

```bash
export MCP_HTTPS_ENABLED=true
export MCP_MEMORY_PREFER_HTTPS=true
```

## 最佳实践

### 开发环境

- 使用自动生成的自签名证书；
- 启用调试日志定位问题；
- 多人协作时为服务命名，便于区分。

### 生产环境

- 使用受信任 CA 签发的正式证书；
- 根据需求对网络进行分区；
- 监控服务发现相关日志；
- 根据网络情况调整发现超时。

### 团队协作

- 约定统一的服务命名；
- 将发现配置写入项目文档；
- 统一管理 API Key；
- 在不同网络环境下测试发现流程。

## 集成示例

### Docker Compose

```yaml
version: '3.8'
services:
  mcp-memory:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MCP_HTTPS_ENABLED=true
      - MCP_MDNS_ENABLED=true
      - MCP_MDNS_SERVICE_NAME=Docker Memory Service
      - MCP_API_KEY=your-secure-key
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-memory-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-memory
  template:
    metadata:
      labels:
        app: mcp-memory
    spec:
      hostNetwork: true  # Required for mDNS
      containers:
      - name: mcp-memory
        image: mcp-memory-service:latest
        env:
        - name: MCP_MDNS_ENABLED
          value: "true"
        - name: MCP_HTTPS_ENABLED
          value: "true"
        ports:
        - containerPort: 8000
```

## 结论

mDNS 服务发现大幅简化了 MCP Memory Service 的部署流程，摆脱手动配置端点的繁琐；配合自动化 HTTPS，可在本地网络中提供安全、零配置的接入体验。

更多信息：

- [多客户端服务器部署指南](../deployment/multi-client-server.md)
- [通用故障排查](../troubleshooting/general.md)
