# MCP Memory Service — Cloudflare 鉴权排查

本文帮助你解决使用 MCP Memory Service 访问 Cloudflare 后端时遇到的常见鉴权问题。

## 概览

Cloudflare 提供多种类型的 API Token，其作用域与校验方式不同。理解差异是成功鉴权的关键。

## Token 类型与校验方式

### 账户级（推荐）

**说明**：仅在指定账户内生效，可按需设置精确权限。

**需要的权限**：
- `Cloudflare D1:Edit` —— 操作 D1 数据库；
- `Vectorize:Edit` —— 操作向量索引。

**校验端点**：
```bash
curl "https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/tokens/verify" \
     -H "Authorization: Bearer {YOUR_TOKEN}"
```

**成功响应示例**：
```json
{
  "result": {
    "id": "token_id_here",
    "status": "active",
    "expires_on": "2026-04-30T23:59:59Z"
  },
  "success": true,
  "errors": [],
  "messages": [
    {
      "code": 10000,
      "message": "This API Token is valid and active"
    }
  ]
}
```

### 全局 Token（Legacy）

**说明**：对所有账户生效，权限范围较大。

**校验端点**：
```bash
curl "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer {YOUR_TOKEN}"
```

## 常见错误信息

### “Invalid API Token”（Error 1000）

**原因**：使用了与 Token 类型不匹配的校验端点。

**解决步骤**：
1. 账户级 Token 使用 `/accounts/{id}/tokens/verify`；
2. 全局 Token 使用 `/user/tokens/verify`；
3. 检查 Token 是否过期；
4. 确认权限配置正确。

**示例**：
```bash
# 错误示例：对账户级 Token 使用 user 校验端点
time curl "https://api.cloudflare.com/client/v4/user/tokens/verify" \
     -H "Authorization: Bearer account_scoped_token"
# 返回 {"success":false,"errors":[{"code":1000,"message":"Invalid API Token"}]}

# 正确示例：
curl "https://api.cloudflare.com/client/v4/accounts/your_account_id/tokens/verify" \
     -H "Authorization: Bearer account_scoped_token"
# 返回 {"success":true,...}
```

### 操作时出现 “401 Unauthorized”

**原因**：Token 缺少所需权限或已失效。

**解决步骤**：
1. 确认已授予 `D1 Database:Edit`；
2. 确认已授予 `Vectorize:Edit`；
3. 检查 Token 是否过期；
4. 确认 `ACCOUNT_ID` 与 Token 所属账户一致。

### MCP 服务日志出现 “Client error '401 Unauthorized'”

**原因**：环境变量未正确加载或 Token 无效。

**排查步骤**：
1. 检查环境变量：
   ```bash
   python scripts/validation/diagnose_backend_config.py
   ```
2. 手动校验 Token：
   ```bash
   curl "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/tokens/verify" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
   ```
3. 测试 D1 权限：
   ```bash
   curl -X POST "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/d1/database/$CLOUDFLARE_D1_DATABASE_ID/query" \
        -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"sql": "SELECT name FROM sqlite_master WHERE type=""table"";"}'
   ```

## 创建账户级 Token

1. 访问 [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)；
2. 点击 “Create Token” → 选择 “Custom token”；
3. 设置权限：
   - `Account` → `Cloudflare D1:Edit`；
   - `Account` → `Vectorize:Edit`；
4. 选择对应的 `Account` 资源；
5. （可选）设置客户端 IP 限制；
6. 设置过期时间；
7. 创建并立即复制 Token。

## 安全建议

- ✅ 使用账户级 Token，并遵循最小权限原则；
- ✅ 设置合理的过期时间（如 1 年以内）；
- ✅ 根据需要设置 IP 限制；
- ✅ 将 Token 保存在环境变量中，勿写入代码库；
- ✅ 定期轮换 Token；
- ❌ 避免无限期 Token；
- ❌ 不要在版本控制中提交 Token。

## 环境变量示例

```bash
CLOUDFLARE_API_TOKEN=your_account_scoped_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
CLOUDFLARE_D1_DATABASE_ID=your_d1_database_id_here
CLOUDFLARE_VECTORIZE_INDEX=mcp-memory-index
```

## 验证命令

```bash
python scripts/validation/diagnose_backend_config.py

curl "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/tokens/verify" \
     -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

## 排查清单

- [ ] Token 为账户级且权限正确；
- [ ] 使用正确的校验端点；
- [ ] 环境变量加载无误；
- [ ] 账户 ID 与 Token 作用域一致；
- [ ] Token 未过期；
- [ ] D1 数据库 ID 正确；
- [ ] Vectorize 索引存在；
- [ ] 修改配置后已重启 MCP 服务。

## 获取支持

如仍无法解决：
1. 运行诊断脚本：`python scripts/validation/diagnose_backend_config.py`；
2. 查阅 [GitHub Issues](https://github.com/doobidoo/mcp-memory-service/issues)；
3. 参考主仓库 [README.md](../../README.md) 获取安装指引；
4. 查看 [CLAUDE.md](../../CLAUDE.md) 获取 Claude Code 使用指南。
