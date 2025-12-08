# MCP Memory Service — Cloudflare API Token 配置

本指南帮助你为 Cloudflare 后端创建并配置具有正确权限的 API Token。

## 所需权限

使用 Cloudflare 后端时，API Token 需具备以下权限：

### 核心权限

#### D1 数据库
- **权限**：`Cloudflare D1:Edit`
- **用途**：存储记忆元数据、标签与关联关系
- **必要**：是

#### Vectorize 索引
- **权限**：`AI Gateway:Edit` 或 `Vectorize:Edit`
- **用途**：写入与查询记忆向量
- **必要**：是

#### Workers AI
- **权限**：`AI Gateway:Read` 或 `Workers AI:Read`
- **用途**：调用 Cloudflare AI 模型生成嵌入（默认使用 `@cf/baai/bge-base-en-v1.5`）
- **必要**：是

#### 账户访问
- **权限**：`Account:Read`
- **用途**：基础账户级操作
- **必要**：是

#### R2 存储（可选）
- **权限**：`R2:Edit`
- **用途**：存储大于 1MB 的大文件内容
- **必要**：仅在启用 R2 时需要

## 创建 Token 步骤

1. **进入 Cloudflare 控制台**  
   https://dash.cloudflare.com/profile/api-tokens

2. **创建自定义 Token**  
   点击 “Create Token” → 选择 “Custom token”。

3. **配置权限**  
   - **Token 名称**：例如 `MCP Memory Service Token`；
   - **Permissions**：按上文添加所有必需权限；
   - **Account Resources**：选择目标 Cloudflare 账户；
   - **Zone Resources**：可选择所有 Zone 或仅需的 Zone；
   - **IP 限制**：一般留空以提升兼容性；
   - **TTL**：根据安全策略设置过期时间。

4. **保存并复制 Token**  
   点击 “Continue to summary” → “Create Token”，并立即复制 Token（后续无法再次查看）。

## 配置环境变量

### 方式一：项目 `.env`
```bash
# 项目根目录 .env
MCP_MEMORY_STORAGE_BACKEND=cloudflare
CLOUDFLARE_API_TOKEN=your_new_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_D1_DATABASE_ID=your_d1_database_id
CLOUDFLARE_VECTORIZE_INDEX=your_vectorize_index_name
```

### 方式二：Claude Desktop 配置
```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": [
        "--directory", "path/to/mcp-memory-service",
        "run", "python", "-m", "mcp_memory_service.server"
      ],
      "env": {
        "MCP_MEMORY_STORAGE_BACKEND": "cloudflare",
        "CLOUDFLARE_API_TOKEN": "your_new_token_here",
        "CLOUDFLARE_ACCOUNT_ID": "your_account_id",
        "CLOUDFLARE_D1_DATABASE_ID": "your_d1_database_id",
        "CLOUDFLARE_VECTORIZE_INDEX": "your_vectorize_index_name"
      }
    }
  }
}
```

## 验证 Token

```bash
cd path/to/mcp-memory-service

uv run python -c "
import asyncio, os
from src.mcp_memory_service.storage.cloudflare import CloudflareStorage

async def test():
    storage = CloudflareStorage(
        api_token=os.getenv('CLOUDFLARE_API_TOKEN'),
        account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
        vectorize_index=os.getenv('CLOUDFLARE_VECTORIZE_INDEX'),
        d1_database_id=os.getenv('CLOUDFLARE_D1_DATABASE_ID')
    )
    await storage.initialize()
    print('Token configuration successful!')

asyncio.run(test())
"
```

## 常见鉴权问题

### 错误代码及处理

#### Error 9109：位置限制
- **现象**：提示 “Cannot use the access token from location: [IP]”
- **原因**：Token 设置了 IP 白名单或黑名单
- **解决**：移除 IP 限制或将当前 IP 加入允许列表

#### Error 7403：权限不足
- **现象**：提示 “The given account is not valid or is not authorized”
- **原因**：缺少 D1、Vectorize、Workers AI 等权限
- **解决**：为 Token 增补缺失权限

#### Error 10000：鉴权错误
- **现象**：针对某个服务返回 “Authentication error”
- **原因**：该服务对应权限未授权
- **解决**：检查并补齐所需权限

#### Error 1000：Token 无效
- **现象**：提示 “Invalid API Token”
- **原因**：Token 格式错误或已过期
- **解决**：重新生成 Token 或确认格式正确

### Google SSO 账户

若使用 Google SSO 登录 Cloudflare：

1. 设置账户密码：进入 **My Profile → Authentication**，点击 **Set Password**；
2. 可选方案：使用 Global API Key，路径为 **My Profile → API Tokens → Global API Key**。

## 安全建议

1. **最小权限原则**：仅授予必要权限；
2. **定期轮换**：建议每 90 天滚动更新 Token；
3. **环境变量管理**：严禁将 Token 提交至版本控制；
4. **IP 限制**：生产环境可结合 IP 白名单使用；
5. **监控**：在 Cloudflare 控制台监控 Token 使用情况；
6. **设置过期时间**：避免无限期 Token。

## 排障流程

若仍然鉴权失败：

1. **检查配置**：确认环境变量是否正确，资源 ID（账户、数据库、索引）是否准确；
2. **逐一测试服务**：先验证账户访问，再逐项验证 D1、Vectorize、Workers AI；
3. **查看 Cloudflare 日志**：在控制台查看 API 使用日志，定位具体错误；
4. **核对权限**：确保权限同时包含读写；
5. **网络检查**：确认网络可访问 Cloudflare API，并排除防火墙阻断。

更多说明请参阅 [Cloudflare Setup Guide](../cloudflare-setup.md) 或主故障排查文档（见目录）。
