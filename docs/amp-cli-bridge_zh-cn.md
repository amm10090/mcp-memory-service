# Amp CLI 桥接（半自动流程）

**目标**：通过文件队列，让 Claude Code 调用 Amp CLI（研究/代码分析/搜索）而不消耗 Claude Code 额度，仅需手动执行 `amp @prompt` 命令。

## 快速流程
1. **Claude Code 生成请求**：
```
你：@agent-amp-bridge 调研 TypeScript 5.0 特性
Claude：写入 prompt 文件并提示 amp 命令
```
2. **手动执行提示命令**：
```bash
amp @.claude/amp/prompts/pending/research-xyz.json
```
3. **Amp 自动写入响应文件**。
4. **Claude Code 读取结果并继续**。

## 架构
```
Claude Code → prompts/pending/{uuid}.json
你运行 amp → amp 输出 responses/ready/{uuid}.json
Claude Code 读取响应 → 继续对话
```

## 目录结构
```
.claude/amp/
├── prompts/pending        # 待处理请求
├── responses/ready        # Amp 生成的结果
├── responses/consumed     # 已使用归档
└── README.md
```

## 消息格式
**Prompt**：
```json
{
  "id": "uuid",
  "timestamp": "2025-11-04T20:00:00Z",
  "prompt": "Research async/await best practices in Python",
  "context": {"project": "mcp-memory-service", "cwd": "/path/to"},
  "options": {"timeout": 300000, "format": "markdown"}
}
```
**Response**：
```json
{
  "id": "uuid",
  "timestamp": "2025-11-04T20:05:00Z",
  "success": true,
  "output": "## Async/Await Best Practices...",
  "error": null,
  "duration": 300000
}
```

## 配置 `.claude/amp/config.json`
```json
{
  "pollInterval": 1000,
  "timeout": 300000,
  "debug": false,
  "ampCommand": "amp"
}
```

## 典型场景
- Web 研究：React 18 新特性。
- 架构分析：Storage backend 设计。
- 文档生成：MCP API 说明。
- 代码生成：TypeScript 类型。
- 最佳实践：OAuth 2.1 安全建议。

## 手动检查
```bash
ls -lt .claude/amp/prompts/pending/
cat .claude/amp/prompts/pending/{uuid}.json | jq -r '.prompt'
```

## 故障排查
- **Amp 额度/鉴权**：直接运行 `amp`，或检查官网额度。
- **无响应文件**：`ls -lt .claude/amp/responses/ready/`。
- **权限问题**：确认目录存在并可写。

## 优点
- 不占 Claude Code 额度，可用 Amp 免费配额。
- 文件队列具备容错、可审计、可重放。
- 完全由用户掌控执行时机。

## 限制
- 需手动运行 `amp @...`。
- Amp 仍消耗自身额度。
- 适合异步调研场景，不适合实时对话。
