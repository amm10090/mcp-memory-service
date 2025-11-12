# 发布检查清单

确保类似 HTTP-MCP Bridge 的严重问题在发布前被捕获。

## 预发布测试

### ✅ 核心功能
- [ ] **健康检查**：`/api/health` 返回 200，`/health` 按预期 404；MCP Bridge 与 Claude Desktop 均可调用；
- [ ] **记忆操作**：写入成功、重复写入返回 `success:false`、异常返回正确状态码，Bridge 端流程一致；
- [ ] **API 路由**：全部带 `/api/` 前缀，URL 拼接不破坏 base path，Bridge 透传路径正确。

### ✅ HTTP-MCP Bridge 专项
- [ ] 状态码：接受 200/201，依据 `success` 字段判断结果；
- [ ] URL：保留 `/api`，`new URL()` 不覆盖路径；
- [ ] MCP 协议：`initialize` / `tools/list` / `tools/call` 正常，错误响应格式符合规范。

### ✅ 端到端
- [ ] **Claude Desktop**：写入/检索/健康检查通过，无误报“unhealthy”；
- [ ] **远程服务器**：Bridge 可连远端，API Key 认证 & SSL 皆正常；
- [ ] **API Consumer**：直接调用 HTTP API，验证响应格式与错误场景。

### ✅ 合同验证
- 响应结构、错误格式、兼容旧配置，Bridge 同时支持 200/201。

## 自动化要求
- 单测：Bridge 相关单测全绿，mock 场景真实，覆盖边界与错误；
- 集成：Bridge↔Server、Contract、MCP 端到端、真实服务器连通测试通过；
- CI：每次提交跑 Bridge 测试，失败阻止合并；多 Node.js 版本矩阵。

## 手动验证
1. **Claude Desktop**：安装→写入→检索→健康状态→无警告；
2. **远程用户**：配置 Bridge→跨网络操作→认证/端点均可用；
3. **API 消费者**：直连 REST，验证成功/失败路径。

跨平台：Windows/macOS/Linux 全覆盖。

## 代码质量
- 评审：状态码假设、URL 构造、错误处理均经审查；无硬编码端点；
- 文档：API 合同、Bridge 使用、排障、Breaking 变更等全部更新。

## 版本与依赖（3 文件流程）
- 更新 `src/mcp_memory_service/__init__.py` 的 `__version__`；
- 更新 `pyproject.toml` 中 `[project].version`；
- 运行 `uv lock`，同一提交包含上述三文件；
- 遵循 SemVer：MAJOR=破坏性，MINOR=新特性，PATCH=修复。

## CHANGELOG 质量门槛
- 符合 Keep a Changelog，格式 `## [8.17.0] - 2025-11-04`；
- 分类：Added/Changed/Fixed/...；Breaking 加粗；性能项提供指标；Bug 修复引用 Issue；
- 若 Breaking：需迁移指南、示例、环境变量变更、DB 脚本、弃用时间线。

## CI/CD 验证
- Actions 全绿（Docker Publish、Publish & Test、Bridge Tests、Platform Tests）；
- Docker：`latest` + `v8.x.x` 多架构镜像（linux/amd64, arm64）；
- PyPI：可在 https://pypi.org/project/mcp-memory-service/ 下载，`pip install mcp-memory-service==8.x.x` 通过。

## Tag & Release
- 打注释标签：`git tag -a v8.x.x -m "Release v8.x.x"` → `git push origin v8.x.x`；
- 创建 GitHub Release：标题 `vx.x.x - 描述`，正文复制 CHANGELOG，必要时附构建产物。

## 发布后收尾
- Issue：搜索 `fixed-in-main`，验证、引用 PR/CHANGELOG，贴模板关闭并加 `released`；
- 文档：Wiki、排障、FAQ 同步；
- 沟通：Release notes 突出关键修复，明确 Breaking 与迁移。

## 发布后监控
- 健康：监控错误率、unhealthy 报告、Claude 连接、API 使用；
- 反馈：关注 Issue / Discussions，及时响应并记录常见问题。

---

## HTTP-MCP Bridge 事故教训
- 不假设状态码；
- 关键组件必须端到端测试；
- `new URL()` 行为需验证；
- 实际 API 行为必须写入文档；
- 单测之外还需完整集成测试。

**每次发布都要确认**：Bridge 在真实服务器下测试、假设已验证、关键路径手测、API 契约匹配实现。

若发现生产级严重 Bug：
1. 立即建 hotfix 分支 + 失败测试；
2. 修复并 24h 内发布；
3. 摘要复盘并更新本清单。

---

## 回滚流程
- **触发条件**：存取/协议崩溃、数据损坏、安全漏洞、大量用户故障；
- **步骤**：
  1. 记录 Issue，打 `critical/rollback-needed` 并公告；
  2. 切回上个版本，重建/推送 Docker `latest`，文档标注；
  3. PyPI `twine yank mcp-memory-service==8.x.x`；
  4. Git Tag 保留，新增 hotfix tag，Release 标记“存在问题”；
  5. 公告：Issue/README/Discussions 说明回滚及临时方案；
  6. 复盘：新增回归测试，更新本清单。
- **时间线**：1h 内建 Issue，4h 内完成回滚，24h 内发布修复，1 周内完成复盘。

此检查清单需在每次发布前完整执行，以避免严重缺陷流入用户环境。
