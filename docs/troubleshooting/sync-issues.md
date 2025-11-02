# 分布式同步故障排查指南

本指南针对 MCP Memory Service v6.3.0+ 的分布式记忆同步系统，介绍常见问题与解决方案。

## 目录
- [诊断命令](#诊断命令)
- [网络连接问题](#网络连接问题)
- [数据库问题](#数据库问题)
- [同步冲突](#同步冲突)
- [服务相关问题](#服务相关问题)
- [性能问题](#性能问题)
- [恢复流程](#恢复流程)
- [日志与监控](#日志与监控)
- [获取支持](#获取支持)

## 诊断命令

在排查具体问题前，可先收集基础信息：

### 系统状态

```bash
# 同步系统概览
./sync/memory_sync.sh status

# 系统详细信息
./sync/memory_sync.sh system-info

# 生成完整诊断报告
./sync/memory_sync.sh diagnose
```

### 组件测试

```bash
./sync/memory_sync.sh test-connectivity    # 网络连通性
./sync/memory_sync.sh test-database       # 数据库完整性
./sync/memory_sync.sh test-sync           # 同步功能
./sync/memory_sync.sh test-all            # 全套测试
```

### 开启调试模式

```bash
export SYNC_DEBUG=1
export SYNC_VERBOSE=1
./sync/memory_sync.sh sync
```

## 网络连接问题

### 无法连接远程服务器

**症状**：连接超时、提示 “Remote server unreachable”、同步立即失败。

**排查**：

```bash
ping your-remote-server
telnet your-remote-server 8443
curl -v -k https://your-remote-server:8443/api/health
```

**解决方案**：

- **DNS 问题**：尝试使用 IP；如需，可在 `/etc/hosts` 中添加映射；
- **防火墙/端口**：确认端口开放，或改用 HTTP（8001）测试；
- **SSL/TLS**：使用 `-k` 忽略（仅测试），或检查证书信息。

### API 鉴权失败

**症状**：返回 401、提示 API key 无效。

```bash
curl -k https://your-remote-server:8443/api/health
export REMOTE_MEMORY_API_KEY="your-api-key"
curl -k -H "Authorization: Bearer your-api-key" https://...
```

### 网络性能缓慢

**症状**：同步耗时长，频繁超时。

**解决方案**：

```bash
export SYNC_BATCH_SIZE=25
export SYNC_TIMEOUT=60
export SYNC_RETRY_ATTEMPTS=5
./sync/memory_sync.sh benchmark-network
```

## 数据库问题

### 暂存库损坏

**症状**：提示 `database is locked`、完整性检查失败、出现损坏警告。

```bash
sqlite3 ~/.mcp_memory_staging/staging.db "PRAGMA integrity_check;"
lsof ~/.mcp_memory_staging/staging.db
```

**恢复**：

```bash
cp ~/.mcp_memory_staging/staging.db ~/.mcp_memory_staging/staging.db.backup
sqlite3 ~/.mcp_memory_staging/staging.db ".recover" > recovered.sql
rm ~/.mcp_memory_staging/staging.db
sqlite3 ~/.mcp_memory_staging/staging.db < recovered.sql
# 或全量重建
rm ~/.mcp_memory_staging/staging.db
./sync/memory_sync.sh init
```

### 数据库版本不兼容

```bash
sqlite3 ~/.mcp_memory_staging/staging.db "PRAGMA user_version;"
./sync/memory_sync.sh upgrade-db
./sync/memory_sync.sh init --force-schema
```

### 磁盘空间不足

```bash
df -h ~/.mcp_memory_staging/
find ~/.mcp_memory_staging/ -name "*.log.*" -mtime +30 -delete
./sync/memory_sync.sh optimize
```

## 同步冲突

### 内容哈希冲突

**症状**：提示重复内容、同步跳过记忆、哈希不一致。

```bash
./sync/memory_sync.sh show-conflicts
export SYNC_CONFLICT_RESOLUTION="merge"
./sync/memory_sync.sh sync
./sync/memory_sync.sh resolve-conflicts --interactive
```

### 标签冲突

```bash
export TAG_MERGE_STRATEGY="union"  # union/intersection/local/remote
./sync/memory_sync.sh resolve-tags --memory-hash "abc123"
./sync/memory_sync.sh cleanup-tags
```

### 时间戳冲突

```bash
timedatectl status  # 或 macOS: sntp -sS time.apple.com
./sync/memory_sync.sh sync --update-timestamps
export SYNC_TIMESTAMP_STRATEGY="newest"
```

## 服务相关问题

### 服务无法启动

```bash
./sync/memory_sync.sh status-service
./sync/memory_sync.sh logs
./sync/memory_sync.sh test-service-config
```

- systemd 下：`systemctl --user daemon-reload`、查看 `journalctl --user -u mcp-memory-sync`；
- macOS LaunchAgent：重新 load plist 并查看日志。

### 服务内存泄漏

```bash
./sync/memory_sync.sh monitor-resources
./sync/memory_sync.sh install-service --restart-interval daily
export SYNC_MEMORY_LIMIT="100MB"
./sync/memory_sync.sh restart-service
```

## 性能问题

### 同步速度慢

```bash
export SYNC_BATCH_SIZE=25
export SYNC_PARALLEL_JOBS=4
./sync/memory_sync.sh optimize
./sync/memory_sync.sh profile-sync
```

### 资源占用高

```bash
export SYNC_CPU_LIMIT=50
export SYNC_MEMORY_LIMIT=200
export SYNC_IO_PRIORITY=3
nice -n 10 ionice -c 3 ./sync/memory_sync.sh sync
# 调整 cron 计划，避开高峰
```

## 恢复流程

### 完全重置

```bash
./sync/memory_sync.sh stop-service
cp -r ~/.mcp_memory_staging ~/.mcp_memory_staging.backup
./sync/memory_sync.sh uninstall --remove-data
./sync/memory_sync.sh install
./sync/memory_sync.sh init
```

### 灾备

```bash
litestream restore -o recovered_sqlite_vec.db /backup/path
cp ~/.mcp_memory_staging.backup/staging.db ~/.mcp_memory_staging/
./sync/memory_sync.sh pull --force
./sync/memory_sync.sh verify-integrity
```

### 数据迁移

```bash
./sync/memory_sync.sh export --format json --output backup.json
export REMOTE_MEMORY_HOST="new-server.local"
./sync/memory_sync.sh import --input backup.json
./sync/memory_sync.sh status
```

## 日志与监控

- 同步日志：`~/.mcp_memory_staging/sync.log`
- 错误日志：`~/.mcp_memory_staging/error.log`
- 服务日志：取决于系统（journalctl/Console.app 等）

常用命令：

```bash
tail -f ~/.mcp_memory_staging/sync.log
grep -i error ~/.mcp_memory_staging/sync.log | tail -10
grep "sync completed" ~/.mcp_memory_staging/sync.log | awk '{print $(NF-1)}' | sort -n
grep -c "sync started" ~/.mcp_memory_staging/sync.log
```

可编写简易监控脚本，如每日健康检查、性能告警等。

## 获取支持

```bash
./sync/memory_sync.sh support-report > support_info.txt
./sync/memory_sync.sh support-report --include-samples >> support_info.txt
```

- GitHub Issues、文档与 Wiki 提供最新信息；
- 如遇生产级故障，请附上日志、配置等详细资料提交 Issue，并标记紧急程度。

同步系统具备较强的容错能力，大多数问题可按对应步骤恢复。EOF
