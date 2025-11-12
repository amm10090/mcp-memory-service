# MCP Memory Service 文档索引

欢迎查阅 MCP Memory Service 的完整文档。该服务基于 Model Context Protocol，为 Claude Desktop 等 MCP 客户端提供语义记忆与持久化存储能力。

## 快速入口

- **新用户**：阅读 [安装总览](installation/master-guide.md)
- **多客户端场景**：参见 [多客户端集成](integration/multi-client.md)
- **Docker 用户**：查看 [Docker 部署](deployment/docker.md)
- **疑难排查**：访问 [常规故障排除](troubleshooting/general.md)

## 文档结构

### 📦 安装与设置

- **[安装总览](installation/master-guide.md)**：覆盖所有平台的安装步骤。
- **[平台指南](platforms/)**：针对特定系统的详细说明。
  - [macOS Intel](platforms/macos-intel.md)：含 2013-2017 旧机型注意事项。
  - [Windows](platforms/windows.md)：支持 CUDA / DirectML。
  - [Ubuntu](platforms/ubuntu.md)：桌面与服务器设置。

### 🔗 集成与连接

- **[多客户端共享](integration/multi-client.md)**：多应用共享记忆。
- **[Homebrew 集成](integration/homebrew.md)**：使用系统级 PyTorch。
- **[Claude Desktop 指南](guides/claude_integration.md)**。
- **[IDE 兼容性](ide-compatability.md)**：VS Code、Continue 等。

### 🚀 部署

- **[Docker 部署](deployment/docker.md)**：多种容器方案。
- **[服务器部署](deployment/multi-client-server.md)**：生产级架构。
- **[云平台部署](glama-deployment.md)**。

### 📚 用户指南

- **[MCP 协议增强](guides/mcp-enhancements.md)**：资源、提示、进度跟踪。
- **[存储后端](guides/STORAGE_BACKENDS.md)**：ChromaDB vs SQLite-vec。
- **[迁移指南](guides/migration.md)**。
- **[脚本参考](guides/scripts.md)**：辅助工具。
- **[调用方式](guides/invocation_guide.md)**。

### 🎯 教程与示例

- **[数据分析示例](tutorials/data-analysis.md)**。
- **[高级技巧](tutorials/advanced-techniques.md)**。
- **[演示会话](tutorials/demo-session-walkthrough.md)**。

### 🔧 维护与运维

- **[记忆维护](maintenance/memory-maintenance.md)**：清理、优化、备份。
- **[健康检查](implementation/health_checks.md)**。
- **[性能调优](implementation/performance.md)**。

### 📖 API 参考

- **[Memory Metadata API](api/memory-metadata-api.md)**。
- **[标签标准化](api/tag-standardization.md)**。
- **[HTTP / SSE API](IMPLEMENTATION_PLAN_HTTP_SSE.md)**。

### 🛠️ 开发与技术

- **[开发指南](technical/development.md)**：贡献流程。
- **[架构概览](development/multi-client-architecture.md)**。
- **[技术实现](technical/)**：
  - [记忆迁移](technical/memory-migration.md)
  - [标签存储](technical/tag-storage.md)

### 🔍 故障排除

- **[通用问题](troubleshooting/general.md)**。
- **[Docker 排障](deployment/docker.md#troubleshooting)**。
- **[平台特定问题](platforms/)**。

## 项目信息

### 关于 MCP Memory Service

通过 MCP 提供持久语义记忆：

- **语义检索**：基于句向量的相似度搜索。
- **多存储后端**：ChromaDB、SQLite-vec、Hybrid。
- **多客户端**：跨应用共享记忆。
- **跨平台**：macOS / Windows / Linux。
- **灵活部署**：本地、Docker、云端。

### 主要特性

- ✅ 语义记忆读写。
- ✅ 多客户端访问（Claude、VS Code 等）。
- ✅ 存储可切换（ChromaDB / SQLite-vec / Hybrid）。
- ✅ 自动硬件优化（CUDA、MPS、DirectML）。
- ✅ 完整部署方案（HTTP/SSE、认证、监控）。

### 最近更新

- **v0.2.2+**：多客户端自动识别。
- **SQLite-vec Backend**：轻量方案。
- **Homebrew 支持**。
- **Docker 改进**：解决循环启动等问题。
- **HTTP/SSE API**：实时多客户端通信。

## 获取帮助

- 安装问题：参见 [安装指南](installation/master-guide.md)。
- 配置疑问：查看 [故障排除](troubleshooting/general.md)。
- 多客户端：阅读 [多客户端指南](integration/multi-client.md)。
- 性能瓶颈：参考 [性能调优](implementation/performance.md)。

### 支持渠道

- **GitHub Issues**：提交 bug / feature。
- **文档**：覆盖所有场景。
- **社区**：交流经验。

### 参与贡献

详见 [开发指南](technical/development.md)：开发环境、测试、PR 流程、编码规范。

## 版本历史

- **最新**：文档重组、导航增强。
- **v0.2.2**：多客户端 + SQLite-vec + Homebrew。
- **v0.2.1**：Docker 修复、HTTP/SSE 增强。
- **v0.2.0**：多客户端支持与跨平台改进。

---

## 导航提示

- **📁** 浏览目录获取子章节。
- **🔗** 所有内部链接可离线使用。
- **📱** 支持移动端阅读。
- **🔍** 使用浏览器搜索定位内容。

**Happy memory-ing! 🧠✨**
