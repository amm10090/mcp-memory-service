# PR #162 修复排查：逗号分隔标签问题

## 问题
合并 PR #162（支持逗号分隔标签）后，仍出现以下错误：
```
Input validation error: 'tag1,tag2,tag3' is not of type 'array'
```

## 根因分析

### PR #162 的修复内容
- **位置**：`src/mcp_memory_service/server.py` 第 1320-1337 行；
- **修改**：`tags` 的 JSONSchema 支持 `array` 或逗号分隔字符串：
  ```json
  "tags": {
    "oneOf": [
      {"type": "array", "items": {"type": "string"}},
      {"type": "string", "description": "Tags as comma-separated string"}
    ]
  }
  ```
- **服务器逻辑**：第 2076-2081 行将字符串转换为数组。

### 错误为何仍然出现

1. **MCP 客户端 Schema 缓存**：Claude Code 的 MCP 客户端在首次连接时会缓存工具 Schema；
2. **旧进程仍在运行**：MCP Server 进程在 git pull 前启动，未重启仍在使用旧代码：
   - 例如 PID 68270/70013 启动于 10:43，早于 PR 合并；
   - HTTP 服务器 11:51 重启为新代码，但 MCP stdio 进程仍旧；
3. **HTTP 与 MCP 进程独立**：重启 HTTP 服务不会影响 MCP stdio 进程；
4. **验证发生在客户端**：JSONSchema 校验在客户端进行，请求未传至服务器即失败。

### 证据

- 进程列表：
  ```
  PID 68270: Started 10:43 (旧)
  PID 70013: Started 10:44 (旧)
  PID 117228: HTTP server restarted 11:51 (新)
  ```
- 错误信息格式：`'value' is not of type 'array'`，来自客户端 `jsonschema` 验证；
- 时间线：
  - 2025-10-20 17:22 UTC：PR #162 合并；
  - 2025-10-21 10:48：HTTP 服务器启动（版本未知）；
  - 2025-10-21 11:51：HTTP 服务器重启，加载新代码；
  - 2025-10-21 11:5x：Claude Code 执行 MCP 重连。

## 解决方案

### 即时处理
```bash
# 在 Claude Code 中运行：
/mcp
```

- 作用：
  1. 终止旧的 MCP Server 进程；
  2. 启动加载最新代码的新进程；
  3. 重新获取工具 Schema；
  4. 清理客户端缓存。

### 验证步骤
1. 确认 MCP 进程启动时间晚于 git pull/合并时间；
2. 测试字符串标签：`{"tags": "tag1,tag2,tag3"}`；
3. 测试数组标签：`{"tags": ["tag1", "tag2", "tag3"]}`；
4. 均应正常通过验证。

## 给后续 PR 的建议

- **合并 Schema 变更后**：
  1. 重启 HTTP 服务（若使用 HTTP 协议）：`systemctl --user restart mcp-memory-http.service`；
  2. 在 Claude Code 中执行 `/mcp` 或重启应用；
  3. 检查 MCP 进程启动时间：`ps aux | grep "memory.*server" | grep -v grep`。

- **PR 描述中提醒**：告知需要在部署后重新连接 MCP；
- **更新 CHANGELOG**：明确重连步骤；
- **部署脚本**：可考虑自动重启相关进程。

## 经验总结

1. MCP 客户端在客户端侧进行 Schema 校验；
2. HTTP 与 MCP 进程独立，需要分别重启；
3. Schema 更新必须让客户端重新获取；
4. git pull 不会自动刷新运行进程；
5. 排查顺序：PR 合并时间 → 进程启动时间 → 服务器日志 → 重连/重启。

## 相关文件
- Schema 定义：`src/mcp_memory_service/server.py:1320-1337`；
- 处理逻辑：`src/mcp_memory_service/server.py:2076-2081`；
- PR 链接：https://github.com/doobidoo/mcp-memory-service/pull/162。

## 快速排查卡片

### 症状
✗ 合并 PR 后仍提示 “Input validation error: 'X' is not of type 'Y'”。

### 诊断
```bash
# 1. 查看 PR 合并时间
gh pr view <PR_NUMBER> --json mergedAt

# 2. 查看服务进程启动时间
ps aux | grep "memory.*server" | grep -v grep

# 若进程早于合并时间，即为旧代码。
```

### 修复
```bash
# Claude Code 中执行：
/mcp

# 或重启 systemd 服务：
systemctl --user restart mcp-memory-http.service
```

### 验证
```bash
ps aux | grep "memory.*server" | grep -v grep  # 确认新进程时间
# 然后测试逗号分隔与数组标签
```

## 时间信息
- 分析日期：2025 年 10 月 21 日；
- PR 合并时间：2025 年 10 月 20 日 17:22 UTC；
- 问题性质：MCP 客户端缓存 Schema 未更新。
