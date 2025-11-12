# LM Studio 兼容性指南

## 问题描述

在 LM Studio 或 Claude Desktop 中使用 MCP Memory Service 时，取消/超时操作可能触发以下错误：

1. **LM Studio 验证错误**：
```
pydantic_core._pydantic_core.ValidationError: 5 validation errors for ClientNotification
ProgressNotification.method
  Input should be 'notifications/progress' [type=literal_error, input_value='notifications/cancelled', input_type=str]
```

2. **Claude Desktop 超时错误**：
```
Message from client: {"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":0,"reason":"McpError: MCP error -32001: Request timed out"}}
Server transport closed unexpectedly, this is likely due to the process exiting early.
```

原因：
- LM Studio / Claude Desktop 会发送非标准的 `notifications/cancelled`。
- 该消息不在 MCP（Model Context Protocol）规范内。
- Windows 上若超时，服务可能提早退出。

## 解决方案

服务现已自带兼容补丁：
- 自动检测 `notifications/cancelled`。
- 记录取消原因并转为安全通知，避免崩溃。
- Windows 下默认超时延长至 30 秒，增强信号处理。

无需额外操作，启动服务即自动生效。

## 日志验证
```
Applied enhanced LM Studio/Claude Desktop compatibility patch for notifications/cancelled
Intercepted cancelled notification (ID: 0): McpError: MCP error -32001: Request timed out
```
出现上述日志即代表补丁在工作，服务将继续运行。

## 技术细节
- 位于 `src/mcp_memory_service/lm_studio_compat.py`。
- Monkey patch `ClientNotification.model_validate`。
- 识别并记录超时。
- 将非标准通知转为合法的 `InitializedNotification`。
- Windows：延长超时、改进信号处理。
- 如有必要，可退而修改 session 接收循环。

## Windows 专属优化
- 初始化超时：30s。
- 兼容 Defender / 杀毒软件的延迟。
- 更优 SIGTERM/SIGINT 处理。
- 超时后可平滑恢复。

## 限制
- 补丁仅绕过客户端的非标准行为。
- 服务器端不会真正取消操作，只是抑制异常通知。
- 操作超时后可能仍在后台完成。

## 未来方向
1. LM Studio 遵循 MCP 规范。
2. MCP 库原生支持厂商扩展。

## 排障
1. 确保使用最新版本。
2. 检查日志是否出现补丁提示。
3. 附完整日志开 issue 反馈。
