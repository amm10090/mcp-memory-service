# Docker 镜像保留策略

## 概览

本文描述 MCP Memory Service 在 Docker Hub 与 GHCR 的镜像清理策略（`.github/workflows/cleanup-images.yml` 自动执行）。目标：
- 降低存储成本（≈70%）。
- 仅保留有效版本，移除潜在漏洞镜像。
- 加速 CI/CD。

## 保留规则

**永久保留**：`latest`、`slim`、`main`、`stable`。  
**语义版本**（`v6.6.0`）：保留最近 5 个。  
**Major.Minor / Major 标签**：永久保留。  
**临时标签**：`buildcache-*`（7 天）、`test-*`/`dev-*`（30 天）、SHA/无标签（30 天/立即删除）。

## 触发方式
1. 发布完成后。
2. 每周日 02:00 UTC。
3. 手动触发（可设 `dry_run`、`keep_versions`、`delete_untagged`）。

## Registry 细节
- **Docker Hub**：API v2 + Python 脚本，需 `DOCKER_USERNAME/PASSWORD`，限速 100 req/6h。
- **GHCR**：使用 `actions/delete-package-versions` + `container-retention-policy`，仓库拥有者无限速。

## 成本与安全
- 镜像数量约 15-20 个，体积 3-5GB。
- 自动移除旧 CVE 镜像，缩小攻击面。
- 所有删除记录保存在 Actions 日志中。

## 监控
- 每次运行输出：删除/保留数量、各 registry 状态、策略摘要。
- 关注指标：执行耗时、删除数量、存储趋势、失败次数。

## 手动操作
```bash
gh workflow run cleanup-images.yml \
  -f dry_run=true \
  -f keep_versions=5 \
  -f delete_untagged=true
```
或在 Actions UI 直接配置。若需保护特定标签，将其加入 `protected_tags` 或遵循匹配规则。

## 回滚
- 30 天内可联系 registry 支持恢复缓存。
- 否则用对应 git tag 重新构建，或从备份恢复。
- 如需停用，将 workflow 重命名或改 cron 为无效值。

## 最佳实践
1. 先 `dry_run` 验证。
2. 上线首周密切监控。
3. 根据使用情况调整 `keep_versions`。
4. 记录特殊标签。
5. 每季度复审策略。

## 常见问题
- **鉴权失败**：检查 Docker Hub 凭证/权限。
- **保护标签被删**：确认命名匹配规则，并查看 dry run 输出。
- **执行时间长**：降低频率或提高 `days_to_keep`。

## 配置参考
```bash
DOCKER_USERNAME
DOCKER_PASSWORD
DOCKER_REPOSITORY=doobidoo/mcp-memory-service
DRY_RUN=false
KEEP_VERSIONS=5
DAYS_TO_KEEP=30
```
工作流 inputs：`dry_run`（默认 true）、`keep_versions`（默认 5）、`delete_untagged`（默认 true）。

## 支持
- 先查阅本文档与 Actions 日志。
- 若仍有问题，提 `docker-cleanup` 标签的 Issue 或联系维护者。

## 策略更新
- 每季度依据成本、使用、安全、性能指标调整。
- 最后更新：2024-08-24；下次评审：2024-11-24。
