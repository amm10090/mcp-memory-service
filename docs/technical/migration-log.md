# FastAPI MCP 服务器迁移日志

- **日期**：2025-08-03  
- **分支**：`feature/fastapi-mcp-native-v4`  
- **版本**：4.0.0-alpha.1

## 架构决策：从 Node.js 网桥切换到原生 FastAPI MCP 服务器

| 问题 | 方案 |
|------|------|
| Node.js HTTP→MCP 网桥在自签名证书场景下握手失败，远端访问不稳定 | 使用 FastAPI + 官方 MCP Python SDK，构建原生 MCP 服务器 |

### 技术发现
1. **Node.js SSL 问题**：即使自定义 HTTPS Agent 或关闭验证，依旧无法稳定通过自签名证书；Slash 命令可用，但 MCP 工具失败。
2. **FastAPI MCP 优势**：
   - 原生 MCP 协议实现（FastMCP 框架）；
   - Python SSL 更适配自签证书；
   - 移除桥接层，降低复杂度；
   - 与现有存储后端无缝集成。

### 实施状态
- 5709be1：完成基础 FastAPI MCP 结构、5 个核心操作（store/retrieve/search_by_tag/delete/health）、新增入口 `mcp-memory-server`；
- c0a0a45：双服务部署（FastMCP 8001 + HTTP Dashboard 8080）上线，SSL 问题解决，标准 MCP 客户端验证完成。

### 限制
- Claude Code SSE 客户端有特定要求，暂与 FastMCP 不兼容；建议 Claude Code 用户暂用 HTTP Dashboard 或其他 MCP 客户端。

### 后续工作
1. 调研自定义 SSE 客户端以兼容 Claude Code；
2. 扩展剩余 17 个记忆操作；
3. 监控双服务性能并优化；
4. 提供多语言 MCP 客户端 SDK；
5. 完善客户端兼容性矩阵文档。

### Dashboard 工具排除说明
- MCP 服务器聚焦 Claude Code 场景，Dashboard 功能由 `mcp-memory-dashboard` 负责，避免重复；
- 排除工具：`dashboard_check_health`、`dashboard_recall_memory` … 等 8 个 Dashboard 专用操作。

### 架构对比
| 维度 | Node.js 网桥 | FastAPI MCP |
|------|--------------|-------------|
| 协议栈 | Claude → 网桥 → HTTP → Memory | Claude → MCP Server |
| SSL | Node.js HTTPS（问题多） | Python SSL（稳定） |
| 复杂度 | 三层 | 两层 |
| 维护 | 多个代码库 | Python 单栈 |
| 远端访问 | 依赖网桥 | 原生支持 |

### 成功指标
- ✅ SSL/HTTPS 连通无须额外配置；
- ✅ 性能与旧方案持平或更优；
- ✅ 远端多客户端接入成功；
- ⚠️ Claude Code 需后续解决 SSE 兼容。

**结论**：迁移成功，双服务架构已投入生产。下一步聚焦 Claude Code SSE 兼容与工具扩展。
