# Memory Hooks 配置指南

本文档列出 Claude Code 记忆感知 Hooks 的全部配置项，并解释各字段的行为与影响。

## 配置层级
`config.json` 采用层级式结构：
1. **memoryService**：连接方式与协议偏好。
2. **projectDetection**：如何识别项目上下文。
3. **memoryScoring**：记忆排序与打分策略。
4. **gitAnalysis**：Git 仓库上下文的使用方式。
5. **timeWindows**：查询的时间窗口/范围。
6. **output**：日志、展示与调试相关选项。

---

## 1. Memory Service 连接

```json
"memoryService": {
  "protocol": "auto",
  "preferredProtocol": "http",
  "fallbackEnabled": true,
  "http": {
    "endpoint": "http://127.0.0.1:8889",
    "apiKey": "YOUR_API_KEY_HERE",
    "healthCheckTimeout": 3000,
    "useDetailedHealthCheck": true
  },
  "mcp": {
    "serverCommand": ["uv", "run", "memory", "server", "-s", "hybrid"],
    "serverWorkingDir": "../",
    "connectionTimeout": 2000,
    "toolCallTimeout": 3000
  }
}
```

### HTTP 设置
- **endpoint**：HTTP 服务地址。
  - `http://` 仅适合本地开发（明文）；
  - `https://` 用于远端或需 TLS 场景（自签证书需提前信任 CA）。
- **apiKey**：访问凭据，建议通过环境变量注入。
- **healthCheckTimeout** / **useDetailedHealthCheck**：健康检查超时与是否返回详细指标。

### MCP 设置
- **serverCommand**：启动本地 MCP 服务器的命令，可根据后端改 `-s hybrid|cloudflare|sqlite_vec|chromadb`；
- **serverWorkingDir**：命令执行目录，`../` 适用于 `project/claude-hooks/` 结构；
- **connectionTimeout** / **toolCallTimeout**：连接与 MCP 调用的超时时间（毫秒）。

> 若目录结构不同，可改为绝对路径或利用环境变量如 `process.env.MCP_MEMORY_PROJECT_ROOT`。

---

## 2. Memory Scoring

### `memoryScoring.weights`
```json
"weights": {
  "timeDecay": 0.40,
  "tagRelevance": 0.25,
  "contentRelevance": 0.15,
  "contentQuality": 0.20,
  "conversationRelevance": 0.25
}
```
- **timeDecay**：时间衰减权重（0.35~0.45 推荐），较高时近期记忆优先；
- **tagRelevance**：标签匹配权重（0.20~0.30），提升规范打标的记忆排名；
- **contentRelevance**：关键词匹配权重；
- **contentQuality**：根据记忆质量（长度、关键字）加权；
- **conversationRelevance**：会话上下文匹配，需开启对话信号时使用。

### 其他参数
- **minRelevanceScore**：过滤低分记忆（默认 0.4，0.3 = 宽松，0.5 = 严格）。
- **timeDecayRate**：指数衰减速率，`score = e^(-rate * days)`，0.05 时 30 天后得分≈0.22。

### 类型/状态加成
- **typeBonus**：对 `implementation`/`decision` 等类型追加分值；
- **recencyBonus**：在关键操作、recent tags 命中时额外加分；
- **projectMatchBonus**：项目名一致时提高得分。

---

## 3. 项目检测 `projectDetection`
- **mode**：`auto`（默认，根据 git/目录推断）或 `manual`；
- **defaultProjectName**：自动失败时的兜底项目名；
- **detectFromGitRemote**：是否使用远端 URL/分支名；
- **maxDirectoryDepth**：向上搜索项目根目录的层数；
- **fallbackTags**：当无法识别项目时自动追加的标签。

---

## 4. Git 分析 `gitAnalysis`
```json
"gitAnalysis": {
  "enabled": true,
  "historyDepth": 20,
  "diffContext": 80,
  "detectIssueRefs": true,
  "ignoredPaths": ["tests/generated/"]
}
```
- **enabled**：是否读取 Git 状态；
- **historyDepth**：读取最近 commit 数（影响 “最近活动” 报告）；
- **diffContext**：一次展示的 diff 行数；
- **detectIssueRefs**：是否解析 `#123` 引用；
- **ignoredPaths**：忽略的路径模式，减少噪声。

Git 分析会影响项目判定、记忆评分的 tag matching，以及输出文案（如 “最近修改文件”）。

---

## 5. 时间窗口 `timeWindows`
- **recentActivityDays**：近期活动（默认 7 天）；
- **recentMemoryDays**：调用搜索时限定的记忆时间范围；
- **maxWindowDays**：当用户查询指定时间段时允许的最大窗口；
- **defaultSessionLookbackMinutes**：Session Start Hook 回溯历史会话的分钟数。

---

## 6. 输出 `output`
- **logLevel**：`info`/`debug`/`warn` 等；
- **showScoringBreakdown**：是否在日志/调试中打印打分细节；
- **maxMemoriesShown**：插入上下文的最大记忆数量；
- **highlightTags**：在输出中高亮的标签集合。

---

## 常见问题与建议
1. **HTTP 401**：确认 `apiKey` 与服务端配置一致；
2. **MCP 启动失败**：检查 `serverCommand` 与 `serverWorkingDir`；
3. **记忆重复或质量差**：调高 `minRelevanceScore`，合理调整各权重；
4. **老记忆覆盖新记忆**：降低 `tagRelevance` 或提高 `timeDecayRate`；
5. **找不到项目**：切换 `mode=manual` 并手动配置 `projectName`。

通过以上配置，可按照团队需求定制 Hook 的检索策略、上下文感知与输出方式，确保 Claude Code 在不同项目中都能准确加载记忆。EOF
