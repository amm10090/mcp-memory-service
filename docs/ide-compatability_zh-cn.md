## IDE 兼容性

[![Works with Claude](https://img.shields.io/badge/Works%20with-Claude-blue)](https://claude.ai)
[![Works with Cursor](https://img.shields.io/badge/Works%20with-Cursor-orange)](https://cursor.sh)
[![Works with WindSurf](https://img.shields.io/badge/Works%20with-WindSurf-green)](https://codeium.com/windsurf)
[![Works with Cline](https://img.shields.io/badge/Works%20with-Cline-purple)](https://github.com/saoudrizwan/claude-dev)
[![Works with RooCode](https://img.shields.io/badge/Works%20with-RooCode-red)](https://roo.ai)

截至 2025 年 6 月，MCP 已成为 AI IDE 集成的标准协议，MCP Memory Service 对主流 IDE 均提供完整支持：

| IDE | MCP 支持 | 配置位置 | 备注 |
| --- | --- | --- | --- |
| Claude Desktop | ✅ | `claude_desktop_config.json` | 官方原生 |
| Claude Code | ✅ | CLI | 官方原生 |
| Cursor | ✅ | `.cursor/mcp.json` 或全局配置 | 支持 stdio/SSE/HTTP |
| WindSurf | ✅ | MCP 配置文件 | 内置服务管理 |
| Cline | ✅ | VS Code MCP 配置 | 可共享服务器 |
| RooCode | ✅ | IDE 配置 | 完整 MCP 客户端 |
| VS Code | ✅ | `.vscode/mcp.json` | 通过 MCP 扩展 |
| Zed | ✅ | IDE 内置 | 原生 MCP |

### 快速配置示例

**Cursor**（`/path/to` 换成仓库路径）：
```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-service", "run", "memory"],
      "env": {
        "MCP_MEMORY_CHROMA_PATH": "/path/to/chroma_db",
        "MCP_MEMORY_BACKUPS_PATH": "/path/to/backups"
      }
    }
  }
}
```

**WindSurf**：配置格式与 Cursor 相同，可通过 GUI 添加。

**Cline（VS Code）**：在扩展面板选择 MCP Servers → Configure → 贴入上述配置。

**RooCode**：参考其 MCP 文档，配置结构一致。

### 多 MCP 服务器示例
```json
{
  "mcpServers": {
    "memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-service", "run", "memory"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "your-token" }
    },
    "task-master": {
      "command": "npx",
      "args": ["-y", "task-master-mcp"]
    }
  }
}
```

### 替代安装方式
- `npx -y @doobidoo/mcp-memory-service`
- 或 `python /path/to/memory_wrapper.py`

### 为什么选 MCP Memory Service？
- 跨 IDE 共享记忆。
- 持久化，重启 IDE 不丢失。
- 语义检索、时间自然语言查询、标签组织。
- 跨平台：macOS / Windows / Linux。

### 连接问题排查
1. `python scripts/test_installation.py`。
2. 查看 IDE MCP 日志面板。
3. `uv run memory` 独立测试。
4. 配置使用绝对路径。
5. 确保 IDE 能访问对应 Python 环境。

### IDE 小贴士
- **Cursor**：注意 MCP 数量上限，按需排序。
- **WindSurf**：善用图形化服务管理。
- **Cline**：检查绿色状态标识。
- **VS Code**：安装官方 MCP 扩展体验更佳。
