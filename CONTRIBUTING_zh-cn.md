# MCP Memory Service 贡献指南

[简体中文](CONTRIBUTING_zh-cn.md) | [English](CONTRIBUTING.md)

感谢你关注 MCP Memory Service！🎉

本项目通过模型上下文协议（Model Context Protocol, MCP）为 AI 助手提供语义记忆与持久化存储。我们欢迎各种形式的贡献——无论是缺陷修复、功能增强、文档完善还是测试补充。

## 目录

- [行为准则](#行为准则)
- [贡献方式](#贡献方式)
- [快速上手](#快速上手)
- [开发流程](#开发流程)
- [编码规范](#编码规范)
- [测试要求](#测试要求)
- [文档规范](#文档规范)
- [提交变更](#提交变更)
- [问题反馈](#问题反馈)
- [社区与支持](#社区与支持)
- [贡献者致谢](#贡献者致谢)

## 行为准则

我们致力于营造友好、包容的协作环境，请：

- 在所有交流中保持尊重和体谅；
- 欢迎新伙伴并主动提供帮助；
- 关注建设性的反馈与共同解决问题；
- 尊重不同观点与经历；
- 避免任何形式的骚扰、歧视或不当行为。

## 贡献方式

### 🐛 缺陷报告
提供详尽信息，帮助我们重现并修复问题。

### ✨ 功能需求
提出新功能或对现有功能的改进建议。

### 📝 文档完善
改进 README、Wiki、代码注释或 API 文档。

### 🧪 测试补充
编写或改进测试用例，协助手动验证。

### 💻 代码贡献
修复缺陷、实现新特性或提升性能。

### 🌍 翻译工作
协助多语言文档（当前 zh-CN 分支正进行中）。

### 💬 社区支持
在 Issues、Discussions 中回答问题或帮助其他用户。

## 快速上手

### 前置要求

- Python 3.10 或以上版本
- Git
- 各平台额外依赖：
  - **macOS**：建议使用 Homebrew Python 以启用 SQLite 扩展
  - **Windows**：部分依赖需要 Visual Studio Build Tools
  - **Linux**：需要安装 build-essential 等基础构建工具

### 开发环境配置

1. **Fork 仓库**（GitHub）
2. **克隆 Fork**：
   ```bash
   git clone https://github.com/YOUR_USERNAME/mcp-memory-service.git
   cd mcp-memory-service
   ```
3. **安装依赖**：
   ```bash
   python install.py
   ```
   脚本会自动识别平台并安装适配依赖。
4. **验证安装**：
   ```bash
   python scripts/verify_environment.py
   ```
5. **启动服务**：
   ```bash
   uv run memory server
   ```
6. **使用 MCP Inspector（可选）**：
   ```bash
   npx @modelcontextprotocol/inspector uv run memory server
   ```

### Docker 方案

如需容器化环境：
```bash
docker-compose up -d  # MCP 模式

docker-compose -f docker-compose.http.yml up -d  # HTTP API 模式
```

## 开发流程

### 1. 创建特性分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-description
```

分支命名建议：
- `feature/`：新功能
- `fix/`：缺陷修复
- `docs/`：文档改动
- `test/`：测试强化
- `refactor/`：重构

### 2. 实施改动

- 编写简洁、易读的代码；
- 遵循下方编码规范；
- 根据需要添加/更新测试；
- 涉及功能变化时更新文档；
- 保持提交粒度清晰、聚焦。

### 3. 运行测试

```bash
# 运行全部测试
pytest tests/

# 运行指定测试文件
pytest tests/test_server.py

# 带覆盖率执行
pytest --cov=mcp_memory_service tests/
```

### 4. 提交代码

推荐使用语义化提交信息：
```bash
git commit -m "feat: add memory export functionality"
git commit -m "fix: resolve timezone handling in memory search"
git commit -m "docs: update installation guide for Windows"
git commit -m "test: add coverage for storage backends"
```
格式：`<type>: <description>`。常见类型：
- `feat`：新功能
- `fix`：缺陷修复
- `docs`：文档更新
- `test`：测试调整
- `refactor`：代码重构
- `perf`：性能提升
- `chore`：日常维护

### 5. 推送到个人仓库

```bash
git push origin your-branch-name
```

### 6. 创建 Pull Request

在主仓库发起 PR 并包含：
- 清晰的标题，概述改动内容；
- 描述改动动机、细节与影响；
- 引用相关 Issue；
- 如有必要附截图或示例。

## 编码规范

### Python 风格

- 基于 PEP 8，并采用以下约定：
  - 行宽 88 字符（Black 默认）；
  - 字符串使用双引号。
- 所有函数签名需加类型注解；
- 使用具象、易懂的变量/函数名；
- 公共函数/类需编写 Google 风格 docstring。

### 代码组织示例

```python
# Import order
import standard_library
import third_party_libraries
from mcp_memory_service import local_modules

# Type hints
from typing import Optional, List, Dict, Any

# Async functions
async def process_memory(content: str) -> Dict[str, Any]:
    """Process and store memory content.

    Args:
        content: The memory content to process

    Returns:
        Dictionary containing memory metadata
    """
    # Implementation
```

### 错误处理

- 捕获具体异常类型；
- 提供明确的错误信息；
- 合理记录日志；
- 避免静默失败。

```python
try:
    result = await storage.store(memory)
except StorageError as e:
    logger.error(f"Failed to store memory: {e}")
    raise MemoryServiceError(f"Storage operation failed: {e}") from e
```

## 测试要求

### 编写测试

- 测试文件置于 `tests/` 目录；
- 文件名以 `test_` 前缀命名；
- 使用具描述性的测试函数名；
- 同时覆盖正向与异常场景；
- 外部依赖请适当 mock。

示例：
```python
import pytest
from mcp_memory_service.storage import SqliteVecStorage

@pytest.mark.asyncio
async def test_store_memory_success():
    """Test successful memory storage."""
    storage = SqliteVecStorage(":memory:")
    result = await storage.store("test content", tags=["test"])
    assert result is not None
    assert "hash" in result
```

### 覆盖率

- 目标覆盖率 ≥80%；
- 重点覆盖关键路径与边界场景；
- 包括错误处理与集成测试。

## 文档规范

### 代码文档

- 公共 API 必须有 docstring；
- 使用类型注解；
- 在 docstring 中提供必要示例；
- 保持注释简洁、直指要点。

### 项目文档

当功能或流程发生变化时：

1. 视情况更新 README.md；
2. 在 Wiki 补充详细指南；
3. 按 Keep a Changelog 规范更新 CHANGELOG.md；
4. 若开发流程改变，更新 AGENTS.md 或 CLAUDE.md。

**高级工作流自动化**：
- 参考 [Context Provider Workflow Automation](https://github.com/doobidoo/mcp-memory-service/wiki/Context-Provider-Workflow-Automation)，利用智能模式自动化开发流程。

### API 文档

- 在 `docs/api/tools.md` 记录新增 MCP 工具；
- 列出参数说明与使用示例；
- 若存在破坏性变更需特别标注。

## 提交变更

### Pull Request 指南

1. **标题格式**：使用语义化描述，例如 `feat: add batch memory operations`。
2. **描述模板**：
   ```markdown
   ## Description
   简述改动内容

   ## Motivation
   为什么需要此改动

   ## Changes
   - 具体改动列表
   - 是否包含破坏性改动

   ## Testing
   - 测试方式
   - 新增覆盖率说明

   ## Screenshots
   (如适用)

   ## Related Issues
   Fixes #123
   ```
3. **检查清单**：
   - [ ] 本地测试通过
   - [ ] 符合编码规范
   - [ ] 文档已更新
   - [ ] CHANGELOG.md 已更新
   - [ ] 未引入敏感信息

### 评审流程

- 每个 PR 至少需要一名维护者审核；
- 请及时响应评审意见并保持讨论聚焦；
- 审核可能需要数日，敬请耐心等待。

## 问题反馈

### 缺陷报告

请提供以下信息：

1. **环境信息**：
   - 操作系统与版本；
   - Python 版本；
   - MCP Memory Service 版本；
   - 安装方式（pip、Docker、源码等）。
2. **复现步骤**：
   - 最小复现代码；
   - 执行命令；
   - 使用的配置。
3. **预期与实际行为**：
   - 预期结果；
   - 实际结果；
   - 错误信息/堆栈。
4. **补充信息**：
   - 截图（如有）；
   - 相关日志；
   - 关联 Issue。

### 功能请求

请描述：

- 想解决的问题；
- 期望的方案；
- 考虑过的替代方案；
- 对现有功能的潜在影响。

## 社区与支持

### 获取帮助

- **文档**：优先查阅 [Wiki](https://github.com/doobidoo/mcp-memory-service/wiki)。
- **问题**：新建 Issue 前先搜索现有 [issues](https://github.com/doobidoo/mcp-memory-service/issues)。
- **讨论**：使用 [GitHub Discussions](https://github.com/doobidoo/mcp-memory-service/discussions) 提问。
- **响应时间**：维护者通常会在 2-3 天内回复。

### 沟通渠道

- **GitHub Issues**：缺陷报告、功能需求；
- **GitHub Discussions**：一般问题与社区交流；
- **Pull Requests**：代码贡献与评审。

### 给 AI 助手的提示

- 查阅 [AGENTS.md](AGENTS.md) 获取通用指引；
- 阅读 [CLAUDE.md](CLAUDE.md) 了解 Claude 专属约定；
- 参考 [Context Provider Workflow Automation](https://github.com/doobidoo/mcp-memory-service/wiki/Context-Provider-Workflow-Automation) 自动化开发流程。

## 贡献者致谢

我们感谢所有贡献者：

- 在发布说明中点名感谢；
- 在 CHANGELOG.md 中记录贡献；
- 合并提交时保留原作者信息；
- 欢迎未来建立 CONTRIBUTORS 文件以展示贡献者名单。

### 表彰类型

- 🐛 提供高质量缺陷报告；
- 💻 提交代码改进；
- 📝 完善文档；
- 🧪 编写或审阅测试。

期待你的加入，让 MCP Memory Service 更加出色！
