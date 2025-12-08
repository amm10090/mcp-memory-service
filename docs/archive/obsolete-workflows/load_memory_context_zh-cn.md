# 记忆上下文加载提示

适用于局域网内的 Claude Code 会话启动阶段。

---

## 标准提示
```
在开始工作前，请从本地 MCP Memory Service 拉取此项目的全部知识：

- Endpoint: https://your-server-ip:8443/mcp
- Authorization: Bearer your-api-key

执行：
```bash
curl -k -s -X POST https://your-server-ip:8443/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "retrieve_memory", "arguments": {"query": "claude-code-reference distributable-reference", "limit": 20}}}' \
  | jq -r '.result.content[0].text'
```

记忆中包含：
- 项目结构/架构概览；
- 开发、测试、部署命令；
- 环境变量与配置模式；
- 最近版本（含 v5.0.2 ONNX 细节）；
- Issue 管理策略与当前状态；
- 测试实践及平台优化；
- 远程部署与健康监控方式。

加载完成后，请确认并简要总结关键信息。
```

---

## 简化提示
```
Load MCP context: curl -k -s -X POST https://your-server-ip:8443/mcp -H "Content-Type: application/json" -H "Authorization: Bearer your-api-key" -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "retrieve_memory", "arguments": {"query": "claude-code-reference", "limit": 20}}}' | jq -r '.result.content[0].text'
```

---

## 分发指引
1. 将本提示文件复制到其它开发机；
2. 若服务地址变动，更新 IP；
3. 通过 `curl -k -s https://your-server-ip:8443/api/health` 自测连通；
4. 会话伊始执行，即可免去重复熟悉代码库的流程。
