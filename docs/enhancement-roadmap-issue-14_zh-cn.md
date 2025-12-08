# 记忆感知增强路线图（Issue #14）

## 摘要

本路线图描述如何将 GitHub Issue #14 从一个基础外部工具演进为具备记忆感知能力的 Claude Code 体验，充分利用 hooks、项目感知与 MCP 深度集成。

## 阶段 1：自动记忆感知（第 1-2 周）

### 1.1 会话启动 Hook
**目标**：启动 Claude Code 会话时自动注入相关记忆。

```javascript
// claude-hooks/session-start.js
export async function onSessionStart(context) {
  const projectContext = await detectProjectContext(context.workingDirectory);
  const relevantMemories = await queryMemoryService({
    tags: [projectContext.name, 'key-decisions', 'recent-insights'],
    timeRange: 'last-2-weeks',
    limit: 8
  });
  
  if (relevantMemories.length > 0) {
    await injectSystemMessage(`
      Recent project context from memory:
      ${formatMemoriesForContext(relevantMemories)}
    `);
  }
}
```

**特性**：
- 基于 Git 仓库与目录结构的项目检测。
- 依据项目与时间窗口的智能记忆筛选。
- 无需人工操作即可自动注入上下文。

### 1.2 项目感知记忆选择
**目标**：根据当前项目上下文智能挑选记忆。

```python
class ProjectAwareMemoryRetrieval:
    def select_relevant_memories(self, project_context):
        memories = self.memory_service.search_by_tags([
            project_context.name,
            f"tech:{project_context.language}",
            "decisions", "architecture", "bugs-fixed"
        ])
        scored_memories = self.score_by_relevance(memories, project_context)
        return scored_memories[:10]
```

### 1.3 对话上下文注入
**目标**：将记忆上下文无缝嵌入对话流。

交付物：
- 会话初始化 hook。
- 项目上下文检测算法。
- 记忆相关性打分系统。
- 上下文格式化与注入工具集。

## 阶段 2：智能上下文更新（第 3-4 周）

### 2.1 动态记忆加载
**目标**：随对话主题变化更新记忆上下文。

```javascript
// claude-hooks/topic-change.js
export async function onTopicChange(context, newTopics) {
  const additionalMemories = await queryMemoryService({
    semanticSearch: newTopics,
    excludeAlreadyLoaded: context.loadedMemoryHashes,
    limit: 5
  });
  
  if (additionalMemories.length > 0) {
    await updateContext(`
      Additional relevant context:
      ${formatMemoriesForContext(additionalMemories)}
    `);
  }
}
```

### 2.2 会话连续性
- 目标：跨多次会话保持连续体验。
- 特性：跨会话关联、会话结果整合、持久线程管理。

### 2.3 智能记忆过滤
- 目标：基于对话分析自动筛选记忆。
- 技术：话题抽取、语义匹配、相关性衰减模型、用户偏好学习。

## 阶段 3：高级集成功能（第 5-6 周）

### 3.1 会话自动打标
**目标**：自动归档会话结论并打标签。

```javascript
// claude-hooks/session-end.js
export async function onSessionEnd(context) {
  const sessionSummary = await analyzeSession(context.conversation);
  const autoTags = await generateTags(sessionSummary);
  
  await storeMemory({
    content: sessionSummary,
    tags: [...autoTags, 'session-outcome', context.project.name],
    type: 'session-summary'
  });
}
```

### 3.2 记忆整合系统
- 目标：智能整理会话洞察。
- 特性：重复检测与合并、洞察提取、知识图谱构建、记忆全生命周期管理。

### 3.3 跨会话智能
- 目标：在不同编码会话中维持知识连贯。
- 方法：会话关系映射、渐进式记忆构建、上下文演进跟踪、模式学习。

## 技术架构

### 核心组件

1. **Memory Hook System**：生命周期 hook、项目上下文检测、动态记忆注入。
2. **Intelligent Memory Selection**：相关性打分、话题分析、上下文过滤。
3. **Context Management**：动态更新、格式化工具、连续性追踪。
4. **Integration Layer**：Claude Code hook 接口、MCP Memory 连接器、项目结构分析器。

### API 增强

```python
@app.post("/claude-code/session-context")
async def get_session_context(project: ProjectContext):
    """Claude Code 启动时请求记忆上下文"""

@app.post("/claude-code/dynamic-context")
async def get_dynamic_context(topics: List[str], exclude: List[str]):
    """根据新话题拉取额外上下文"""

@app.post("/claude-code/consolidate-session")
async def consolidate_session(session_data: SessionData):
    """存储并组织会话结果"""
```

## 成功指标

### 阶段 1
- ✅ 100% 自动注入会话上下文。
- ✅ 记忆加载后启动耗时 < 2 秒。
- ✅ 记忆相关性准确率 ≥ 90%。

### 阶段 2
- ✅ 话题变化触发实时上下文更新。
- ✅ 会话连续性 ≥ 95%。
- ✅ 具备智能话题检测与匹配。

### 阶段 3
- ✅ 记忆管理全流程自动化。
- ✅ 构建跨会话知识库。
