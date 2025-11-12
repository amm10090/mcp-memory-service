# OAuth 2.1 动态客户端注册配置

本文档说明如何在 MCP Memory Service 中配置并使用 OAuth 2.1 动态客户端注册（Dynamic Client Registration，DCR），以启用 Claude Code 的 HTTP 传输集成。

## 概览

MCP Memory Service 已根据 RFC 7591 实现 OAuth 2.1 DCR，带来以下能力：

- **Claude Code HTTP 传输**：直接融入 Claude Code 团队协作功能。
- **自动客户端注册**：客户端可自助注册，无需人工干预。
- **安全认证**：基于 JWT 的访问令牌，并附带精细化的 scope 校验。
- **向后兼容**：现有 API Key 认证依旧可用。

## 快速开始

### 1. 启用 OAuth

```bash
export MCP_OAUTH_ENABLED=true
```

### 2. 启动服务

```bash
# 启动启用了 OAuth 的 HTTP 服务
uv run memory server --http

# 生产环境建议启用 HTTPS
export MCP_HTTPS_ENABLED=true
export MCP_SSL_CERT_FILE=/path/to/cert.pem
export MCP_SSL_KEY_FILE=/path/to/key.pem
uv run memory server --http
```

### 3. 测试 OAuth 端点

```bash
# 调用集成测试验证 OAuth 流程
python tests/integration/test_oauth_flow.py http://localhost:8001
```

## 配置项

### 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `MCP_OAUTH_ENABLED` | `true` | 是否启用 OAuth 2.1 端点 |
| `MCP_OAUTH_SECRET_KEY` | 自动生成 | JWT 签名密钥（生产环境需显式设置） |
| `MCP_OAUTH_ISSUER` | 自动探测 | OAuth Issuer URL |
| `MCP_OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | 访问令牌有效期（分钟） |
| `MCP_OAUTH_AUTHORIZATION_CODE_EXPIRE_MINUTES` | `10` | 授权码有效期（分钟） |

### 配置示例

```bash
# 生产环境
export MCP_OAUTH_ENABLED=true
export MCP_OAUTH_SECRET_KEY="your-secure-secret-key-here"
export MCP_OAUTH_ISSUER="https://your-domain.com"
export MCP_HTTPS_ENABLED=true

# 开发环境
export MCP_OAUTH_ENABLED=true
export MCP_OAUTH_ISSUER="http://localhost:8001"  # 与本地端口一致
```

## OAuth 端点

### Discovery 端点

- `GET /.well-known/oauth-authorization-server/mcp` —— OAuth 元数据。
- `GET /.well-known/openid-configuration/mcp` —— OpenID Connect Discovery。

### OAuth 流程端点

- `POST /oauth/register` —— 动态客户端注册。
- `GET /oauth/authorize` —— 授权端点。
- `POST /oauth/token` —— 令牌端点。

### 管理端点

- `GET /oauth/clients/{client_id}` —— 查询指定客户端信息（调试用）。

## Claude Code 集成

### 自动化流程

Claude Code 会自动发现并注册 OAuth 服务器：

1. **Discovery**：请求 `/.well-known/oauth-authorization-server/mcp`。
2. **Registration**：作为 OAuth 客户端自动注册。
3. **Authorization**：重定向用户完成授权（MVP 阶段自动批准）。
4. **Token Exchange**：用授权码换取访问令牌。
5. **API Access**：在所有 HTTP 传输请求中携带 Bearer Token。

### 手动配置（如需）

```json
{
  "memoryService": {
    "protocol": "http",
    "http": {
      "endpoint": "http://localhost:8001",
      "oauth": {
        "enabled": true,
        "discoveryUrl": "http://localhost:8001/.well-known/oauth-authorization-server/mcp"
      }
    }
  }
}
```

## API 认证方式

### Bearer Token

```bash
# 通过 OAuth 获取访问令牌
export ACCESS_TOKEN="your-jwt-access-token"

# 使用 Bearer Token 访问 API
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
     http://localhost:8001/api/memories
```

### Scope 授权

系统支持三个 scope：

- `read`：只读接口。
- `write`：创建 / 更新接口。
- `admin`：管理类接口。

### 向后兼容

```bash
# 传统 API Key 依旧可用
export MCP_API_KEY="your-api-key"
curl -H "Authorization: Bearer $MCP_API_KEY" \
     http://localhost:8001/api/memories
```

## 安全注意事项

### 生产部署建议

1. **强制 HTTPS**：生产环境务必启用 HTTPS。
2. **设置密钥**：`MCP_OAUTH_SECRET_KEY` 必须使用高强度随机值。
3. **安全存储**：生产环境建议持久化客户端信息。
4. **限流**：对 OAuth 端点增加限流防护。

### OAuth 2.1 合规要点

- 非 localhost URL 必须使用 HTTPS。
- 客户端凭据需安全生成。
- JWT 访问令牌做严格校验。
- 授权码及时过期并失效。
- 严格验证重定向 URI。

## 故障排查

### 常见问题

**OAuth 端点返回 404**：

- 确认 `MCP_OAUTH_ENABLED=true`。
- 修改配置后需重启服务。

**Claude Code 连接失败**：

- 检查生产环境 HTTPS 配置。
- 验证 Discovery 端点是否响应。

**令牌无效**：

- 确保 `MCP_OAUTH_SECRET_KEY` 未变更。
- 检查令牌是否过期。
- 确认 JWT 格式正确。

### 调试命令

```bash
# 测试 Discovery 端点
curl http://localhost:8001/.well-known/oauth-authorization-server/mcp

# 发起客户端注册
curl -X POST http://localhost:8001/oauth/register \
     -H "Content-Type: application/json" \
     -d '{"client_name": "Test Client"}'

# 查看服务器日志
tail -f logs/mcp-memory-service.log | grep -i oauth
```

## API 参考

### 客户端注册请求

```json
{
	"client_name": "My Application",
	"redirect_uris": ["https://myapp.com/callback"],
	"grant_types": ["authorization_code"],
	"response_types": ["code"],
	"scope": "read write"
}
```

### 客户端注册响应

```json
{
	"client_id": "mcp_client_abc123",
	"client_secret": "secret_xyz789",
	"redirect_uris": ["https://myapp.com/callback"],
	"grant_types": ["authorization_code"],
	"response_types": ["code"],
	"token_endpoint_auth_method": "client_secret_basic"
}
```

### 令牌响应

```json
{
	"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"token_type": "Bearer",
	"expires_in": 3600,
	"scope": "read write"
}
```

## 开发说明

### 运行测试

```bash
# 基础 OAuth 测试
python tests/integration/test_oauth_flow.py

# 过滤运行 OAuth 相关用例
pytest tests/ -k oauth

# 使用脚本手动测试
./scripts/test_oauth_flow.sh
```

### 新增 scope 的流程

1. 在 `oauth/models.py` 中添加 scope 定义。
2. 在 `oauth/middleware.py` 中补充校验逻辑。
3. 通过 `require_scope()` 为目标端点增加权限约束。

更多细节可参考 [OAuth 2.1 草案](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1) 与 [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591)。
