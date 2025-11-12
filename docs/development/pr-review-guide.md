# Pull Request 审查指南

面向评审者的结构化 checklist，确保 PR 质量一致且在合并前捕获风险。

## 审查流程
1. **初步分诊（~2 分钟）**：核对 PR 模板是否完整；
2. **代码审查（10-30 分钟）**：关注正确性与质量；
3. **测试验证（5-15 分钟）**：确认测试与覆盖率；
4. **文档检查（~5 分钟）**：确认文档同步更新；
5. **Gemini Review（可选）**：`/gemini review` 做额外分析；
6. **批准或请求修改**：输出明确、可执行的反馈。

---

## 1. PR 模板与元数据

### ✅ 描述质量
- [ ] **Summary**：说明改了什么、为什么；引用 Issue（Fixes/Closes #123）；Breaking change 明示；
- [ ] **Changes**：用条目列出具体改动、技术细节、影响范围；
- [ ] **Testing**：说明测试策略、手工步骤（若有）、覆盖率变化；
- [ ] **UI/API 变更**：附前后对比截图、API 请求/响应示例或 CLI 输出。

### ✅ 元数据
- [ ] **标签**：`bug`/`feature`/`docs` 等；涉及行为变更加 `breaking-change`；可见性变更加 `needs-release-notes`；
- [ ] **Milestone**：若有发布计划，设置目标版本；
- [ ] **评审人**：至少一位维护者 + 相关领域 SME。

---

## 2. 代码评审标准

### ✅ 类型与文档
- [ ] **类型标注齐全**，避免 `def foo(a, b):`；
- [ ] **Docstring** 使用 Google/NumPy 风格，说明 Args/Returns/Raises；
- [ ] **异步规范**：I/O 用 `async def` + `await`，避免阻塞调用。

### ✅ 错误处理
- [ ] 捕获具体异常并加上下文：
```python
try:
    result = await storage.store(memory)
except StorageError as e:
    logger.error("store failed", extra={"memory": memory.id, "err": str(e)})
    raise MemoryServiceError("Storage operation failed") from e
```
- [ ] 错误信息含操作背景，不泄露敏感数据；
- [ ] 日志级别合适（错误/警告/调试）。

### ✅ 性能
- [ ] DB 操作批量化，避免 N+1；必要时新增索引；
- [ ] 模型/嵌入缓存复用，注意过期策略；
- [ ] 充分利用 `asyncio.gather`、超时控制。

### ✅ 安全
- [ ] 输入校验（类型、范围、长度）；SQL 参数化；防止 Path Traversal；
- [ ] 不硬编码凭据，敏感信息来自环境变量且日志已脱敏；
- [ ] HTTP/API 需验证 API Key / OAuth；MCP 协议安全约束未破坏。

---

## 3. 测试验证

### ✅ 覆盖范围
- [ ] 新功能有对应单测/集成测试/回归测试；
- [ ] 测试可读、可维护，必要时 mock 外部依赖；
- [ ] 边界条件、异常路径均覆盖。

### ✅ 执行情况
- [ ] 本地 `pytest` 全绿；CI Workflow 全部通过；
- [ ] 复杂改动需要手工验证（附步骤或截图）；
- [ ] 若改动影响性能，大规模数据场景需验证。

### ✅ 防回归
- [ ] 未无故删除/禁用旧测试；
- [ ] Fixture 与数据模型同步更新；
- [ ] 如修复缺陷，添加针对性回归用例。

---

## 4. 文档同步

- [ ] **CLAUDE.md**：新增命令/脚本/流程需更新；
- [ ] **CHANGELOG.md**：按 Keep a Changelog 结构记录（Added/Changed/Fixed），Breaking 变更突出；
- [ ] **README / Wiki**：安装、配置、故障排查若受影响需同步；
- [ ] **API 文档**：新增/修改端点需附请求/响应示例、错误码；
- [ ] **迁移指南**：Breaking 变更给出迁移路径、前后对比、脚本等；
- [ ] **Deprecation**：标明生效版本与替代方案。

---

## 5. Gemini Review（`/gemini review`）
- **推荐场景**：500+ 行改动、复杂算法、安全/性能关键、首次贡献者；
- **流程**：提交 `/gemini review` → 等 1 分钟 → 将结果与人工点评一并反馈；
- **擅长**：常见反模式、安全隐患、性能建议、测试覆盖提醒；
- **局限**：对项目上下文了解有限，最终决策仍由维护者把控。

---

## 6. 合并条件

### ✅ Merge 前必备
- [ ] 评审意见均处理完毕，讨论 resolved；
- [ ] 本地/CI 测试均通过；
- [ ] 新代码有充足测试；
- [ ] 文档/Changelog 更新；
- [ ] Breaking 变更附迁移方案；
- [ ] 分支已 rebase/merge 最新 `main`，无冲突；
- [ ] 提交信息遵循语义化（`feat: ...`）。

### ✅ 审批流程
- 常规：≥1 维护者；
- Breaking：≥2 人；
- 安全相关需安全负责人确认。

### ✅ Merge 方式
- **Squash and Merge**：多次 WIP 提交或历史混乱时使用；
- **Merge Commit**：多个独立特性或需保留细粒度历史；
- **禁止 Rebase and Merge**（影响 CI 历史）。

---

## 7. 常见问题清单
- 性能：N+1、同步阻塞、缓存泄漏；
- 安全：SQL 拼接、路径注入、日志泄密；
- 错误处理：`except:` 全吞、无日志、信息含糊；
- 测试：形式化测试、不可重复、遗漏边界；
- 文档：示例过期、API 未更新、未披露 Breaking。

---

## 8. 高效反馈技巧
- **具体**：指出风险及原因，避免“可能有问题”；
- **示例**：提供建议代码片段；
- **区分优先级**：标记必改 vs. Nit；
- **建设性**：说明更佳实践或参考实现；
- **尊重且专业**：目标是提升代码，而非挑错。

示例：
```markdown
**Required:** DB 查询在循环里会导致 N+1，可改成一次性 fetch。
**Optional:** 变量名 `tmp` 不够语义化，可考虑 `temporary_result`。
```

---

借助上述 checklist，可显著提升 PR 审查效率，并保持交付质量一致。EOF
