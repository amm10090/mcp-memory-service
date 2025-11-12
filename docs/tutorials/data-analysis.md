# 数据分析范例

本指南演示如何从 MCP Memory Service 中提炼洞察、模式与可视化，将存量知识转化为可执行情报。

## 🎯 概述

MCP Memory Service 不只是存储/检索系统，它还能作为分析平台，帮助理解知识增长节奏、使用趋势以及信息之间的关系。以下示例展示多种实用分析技术，可直接复刻到你的知识库中。

## 📊 分析类型

1. **时间序列分析**：识别知识随时间的增长规律。
2. **内容分析**：观察存储信息的类型与组织方式。
3. **使用模式分析**：了解信息被访问与引用的路径。
4. **质量分析**：衡量知识库的健康度与结构化程度。
5. **关系分析**：发现信息之间的联系与共现模式。

## 📈 时间分布分析

### 基础时间查询

**按月统计：**
```javascript
const januaryMemories = await recall_memory({
  "query": "memories from january 2025",
  "n_results": 50
});

const juneMemories = await recall_memory({
  "query": "memories from june 2025",
  "n_results": 50
});

console.log(`January: ${januaryMemories.length} memories`);
console.log(`June: ${juneMemories.length} memories`);
```

**周度活跃度：**
```javascript
const lastWeek = await recall_memory({
  "query": "memories from last week",
  "n_results": 25
});

const thisWeek = await recall_memory({
  "query": "memories from this week",
  "n_results": 25
});

const weeklyGrowth = ((thisWeek.length - lastWeek.length) / lastWeek.length) * 100;
console.log(`Weekly growth rate: ${weeklyGrowth.toFixed(1)}%`);
```

### 进阶时间分析

**记忆创建频率：**
```javascript
function analyzeMemoryDistribution(memories) {
  const monthlyDistribution = {};
  memories.forEach(memory => {
    const date = new Date(memory.timestamp);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    if (!monthlyDistribution[monthKey]) {
      monthlyDistribution[monthKey] = { count: 0, memories: [] };
    }
    monthlyDistribution[monthKey].count++;
    monthlyDistribution[monthKey].memories.push(memory);
  });
  return monthlyDistribution;
}

function prepareChartData(distribution) {
  return Object.entries(distribution)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, data]) => {
      const [year, monthNum] = month.split('-');
      const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
      return {
        month: `${monthNames[parseInt(monthNum) - 1]} ${year}`,
        count: data.count,
        monthKey: month,
        memories: data.memories
      };
    });
}
```

**项目生命周期：**
```javascript
async function analyzeProjectLifecycle(projectTag) {
  const projectMemories = await search_by_tag({ "tags": [projectTag] });
  const phases = { planning: [], development: [], testing: [], deployment: [], maintenance: [] };
  projectMemories.forEach(memory => {
    const tags = memory.tags || [];
    if (tags.includes('planning') || tags.includes('design')) phases.planning.push(memory);
    else if (tags.includes('development') || tags.includes('implementation')) phases.development.push(memory);
    else if (tags.includes('testing') || tags.includes('debugging')) phases.testing.push(memory);
    else if (tags.includes('deployment') || tags.includes('production')) phases.deployment.push(memory);
    else if (tags.includes('maintenance') || tags.includes('optimization')) phases.maintenance.push(memory);
  });
  return phases;
}

const mcpLifecycle = await analyzeProjectLifecycle('mcp-memory-service');
console.log('Project phases:', {
  planning: mcpLifecycle.planning.length,
  development: mcpLifecycle.development.length,
  testing: mcpLifecycle.testing.length,
  deployment: mcpLifecycle.deployment.length,
  maintenance: mcpLifecycle.maintenance.length
});
```

## 🏷️ 标签分析

### 频次统计

```javascript
async function analyzeTagFrequency() {
  const allMemories = await retrieve_memory({ "query": "all memories", "n_results": 500 });
  const tagFrequency = {};
  allMemories.forEach(({ tags = [] }) => tags.forEach(tag => {
    tagFrequency[tag] = (tagFrequency[tag] || 0) + 1;
  }));
  return Object.entries(tagFrequency)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 20);
}

const topTags = await analyzeTagFrequency();
topTags.forEach(([tag, count]) => console.log(`${tag}: ${count}`));
```

### 标签共现

```javascript
function analyzeTagRelationships(memories) {
  const cooccurrence = {};
  memories.forEach(({ tags = [] }) => {
    for (let i = 0; i < tags.length; i++) {
      for (let j = i + 1; j < tags.length; j++) {
        const pair = [tags[i], tags[j]].sort().join(' + ');
        cooccurrence[pair] = (cooccurrence[pair] || 0) + 1;
      }
    }
  });
  return Object.entries(cooccurrence)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10);
}
```

### 分类分布

```javascript
function categorizeTagsByType(tags) {
  const categories = { projects: [], technologies: [], activities: [], status: [], content: [], temporal: [], other: [] };
  const patterns = {
    projects: /^(mcp-memory-service|memory-dashboard|github-integration)/,
    technologies: /^(python|react|typescript|chromadb|git|docker)/,
    activities: /^(testing|debugging|development|documentation|deployment)/,
    status: /^(resolved|in-progress|blocked|verified|completed)/,
    content: /^(concept|architecture|tutorial|reference|example)/,
    temporal: /^(january|february|march|april|may|june|q1|q2|2025)/
  };
  tags.forEach(([tag, count]) => {
    let matched = false;
    for (const [category, pattern] of Object.entries(patterns)) {
      if (pattern.test(tag)) {
        categories[category].push([tag, count]);
        matched = true;
        break;
      }
    }
    if (!matched) categories.other.push([tag, count]);
  });
  return categories;
}

const tagCategories = categorizeTagsByType(topTags);
Object.entries(tagCategories).forEach(([category, items]) => console.log(`${category}: ${items.length}`));
```

## 📋 内容质量分析

### 未打标检测

```javascript
async function findUntaggedMemories() {
  const candidates = await retrieve_memory({
    "query": "test simple basic example memory",
    "n_results": 50
  });
  const untagged = candidates.filter(memory => {
    const tags = memory.tags || [];
    return tags.length === 0 || (tags.length === 1 && ['test','memory','note'].includes(tags[0]));
  });
  return {
    total: candidates.length,
    untagged: untagged.length,
    percentage: (untagged.length / candidates.length) * 100,
    examples: untagged.slice(0, 5)
  };
}
```

### 标签一致性

```javascript
function analyzeTagConsistency(memories) {
  const inconsistencies = [];
  memories.forEach(memory => {
    const content = memory.content.toLowerCase();
    const tags = memory.tags || [];
    if ((content.includes('issue') || content.includes('bug')) && !tags.some(tag => tag.includes('issue') || tag.includes('bug'))) {
      inconsistencies.push({ type: 'missing-issue-tag', memory: content.slice(0, 100), tags });
    }
    if (content.includes('test') && !(tags.includes('test') || tags.includes('testing'))) {
      inconsistencies.push({ type: 'missing-test-tag', memory: content.slice(0, 100), tags });
    }
  });
  return {
    totalMemories: memories.length,
    inconsistencies: inconsistencies.length,
    consistencyScore: ((memories.length - inconsistencies.length) / memories.length) * 100,
    examples: inconsistencies.slice(0, 5)
  };
}
```

## 📊 可视化数据

### 分布数据

```javascript
function prepareDistributionData(memories) {
  const distribution = analyzeMemoryDistribution(memories);
  const chartData = prepareChartData(distribution);
  const total = chartData.reduce((sum, item) => sum + item.count, 0);
  const average = total / chartData.length;
  const peak = chartData.reduce((max, item) => item.count > max.count ? item : max, chartData[0]);
  const valley = chartData.reduce((min, item) => item.count < min.count ? item : min, chartData[0]);
  return {
    chartData,
    metrics: {
      total,
      average: Math.round(average * 10) / 10,
      peak: { month: peak.month, count: peak.count },
      valley: { month: valley.month, count: valley.count },
      growth: calculateGrowthRate(chartData)
    }
  };
}

function calculateGrowthRate(chartData) {
  if (chartData.length < 2) return 0;
  const first = chartData[0].count;
  const last = chartData[chartData.length - 1].count;
  return ((last - first) / first) * 100;
}
```

### 活动热力图

```javascript
function generateActivityHeatmap(memories) {
  const heatmapData = {};
  memories.forEach(memory => {
    const date = new Date(memory.timestamp);
    const key = `${date.getDay()}-${date.getHours()}`;
    heatmapData[key] = (heatmapData[key] || 0) + 1;
  });
  const matrix = [];
  const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  for (let day = 0; day < 7; day++) {
    const dayData = [];
    for (let hour = 0; hour < 24; hour++) {
      const key = `${day}-${hour}`;
      dayData.push({ day: days[day], hour, value: heatmapData[key] || 0 });
    }
    matrix.push(dayData);
  }
  return matrix;
}
```

## 🔍 高阶分析

### 语义相似度 / 知识图

```javascript
async function findRelatedMemories(targetMemory, threshold = 0.7) {
  const related = await retrieve_memory({
    "query": targetMemory.content.substring(0, 200),
    "n_results": 20
  });
  return related.filter(memory =>
    memory.relevanceScore > threshold &&
    memory.content_hash !== targetMemory.content_hash
  );
}

async function buildKnowledgeGraph(memories) {
  const nodes = [];
  const edges = [];
  for (const memory of memories.slice(0, 50)) {
    nodes.push({
      id: memory.content_hash,
      label: memory.content.substring(0, 50) + '...',
      tags: memory.tags || [],
      group: memory.tags?.[0] || 'untagged'
    });
    const related = await findRelatedMemories(memory, 0.8);
    related.forEach(rel => {
      edges.push({ from: memory.content_hash, to: rel.content_hash, weight: rel.relevanceScore || 0.5 });
    });
  }
  return { nodes, edges };
}
```

### 趋势识别

```javascript
function analyzeTrends(memories, timeWindow = 30) {
  const now = new Date();
  const cutoff = new Date(now - timeWindow * 24 * 60 * 60 * 1000);
  const recent = memories.filter(memory => new Date(memory.timestamp) > cutoff);
  const historical = memories.filter(memory => new Date(memory.timestamp) <= cutoff);
  const recentTags = getTagFrequency(recent);
  const historicalTags = getTagFrequency(historical);
  const trends = [];
  Object.entries(recentTags).forEach(([tag, recentCount]) => {
    const historicalCount = historicalTags[tag] || 0;
    const change = recentCount - historicalCount;
    const changePercent = historicalCount > 0 ? (change / historicalCount) * 100 : 100;
    if (Math.abs(changePercent) > 50) {
      trends.push({ tag, trend: changePercent > 0 ? 'increasing' : 'decreasing', change: changePercent, recentCount, historicalCount });
    }
  });
  return trends.sort((a, b) => Math.abs(b.change) - Math.abs(a.change));
}
```

（文末还包含质量评估、自动化报告、导出等脚本，请根据需要复制使用。）

---

*以上示例说明：只要把 MCP Memory Service 当作“知识分析平台”，就能系统洞察知识库的增长、质量与价值链。*
