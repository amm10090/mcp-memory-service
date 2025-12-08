# 记忆元数据增强 API

## 概述

Memory Metadata Enhancement API 用于在不重建记忆的前提下高效更新元数据，解决 Issue #10 中“更新元数据必须删除并重建整条记忆”的瓶颈。

## API 方法

### `update_memory_metadata`

在保留原始内容、嵌入乃至时间戳（可选）的情况下更新记忆元数据。

**函数签名：**
```python
async def update_memory_metadata(
    content_hash: str,
    updates: Dict[str, Any],
    preserve_timestamps: bool = True
) -> Tuple[bool, str]
```

**参数说明：**
- `content_hash`（必填）：目标记忆的内容哈希；
- `updates`（必填）：包含要修改字段的字典；
- `preserve_timestamps`（默认 True）：是否保留原 `created_at`。

**返回值：**
- `success`：布尔值，指示是否成功；
- `message`：更新摘要或错误信息。

## 支持更新的字段

### 核心字段

1. **tags**（字符串数组）
   - 完全替换原标签；
   - 示例：`"tags": ["important", "reference", "new-tag"]`。

2. **memory_type**
   - 更新记忆类型，示例：`"memory_type": "reminder"`。

3. **metadata**（对象）
   - 与原自定义元数据合并；
   - 示例：`"metadata": {"priority": "high", "due_date": "2024-01-15"}`。

### 自定义字段

除受保护字段外，其余键均可直接更新，例如：
- `"priority": "urgent"`
- `"status": "active"`
- `"category": "work"`
- 业务自定义键值。

### 受保护字段

禁止修改以下字段：
- `content`
- `content_hash`
- `embedding`
- `created_at` / `created_at_iso`（除非 `preserve_timestamps=false`）
- 内部时间戳（`timestamp`、`timestamp_float`、`timestamp_str`）

## 使用示例

### 示例 1：添加标签
```json
{
  "content_hash": "abc123def456...",
  "updates": {
    "tags": ["important", "reference", "project-alpha"]
  }
}
```

### 示例 2：更新记忆类型与自定义元数据
```json
{
  "content_hash": "abc123def456...",
  "updates": {
    "memory_type": "reminder",
    "metadata": {
      "priority": "high",
      "due_date": "2024-01-15",
      "assignee": "john.doe@example.com"
    }
  }
}
```

### 示例 3：直接更新自定义字段
```json
{
  "content_hash": "abc123def456...",
  "updates": {
    "priority": "urgent",
    "status": "active",
    "category": "work",
    "last_reviewed": "2024-01-10"
  }
}
```

### 示例 4：重置时间戳
```json
{
  "content_hash": "abc123def456...",
  "updates": {
    "tags": ["archived", "completed"]
  },
  "preserve_timestamps": false
}
```

## 时间戳策略

### 默认（`preserve_timestamps=true`）
- `created_at` / `created_at_iso` 保留旧值；
- `updated_at` / `updated_at_iso` 更新为当前时间；
- 兼容旧字段同步更新。

### 重置（`preserve_timestamps=false`）
- 所有时间戳均设为当前值；
- 适合标记“刷新/重新激活”记忆。

## 实现细节

### 存储层
1. **抽象接口**（`storage/base.py`）：定义统一方法；
2. **ChromaDB**（`storage/chroma.py`）：通过高效 upsert 保留嵌入，并校验/合并元数据；
3. **其他后端**：未来 sqlite-vec 等将复用同一接口。

### MCP 协议
1. **工具注册**：暴露为 `update_memory_metadata`；
2. **输入校验**：严格验证参数；
3. **错误处理**：返回可读错误；
4. **日志**：详细记录，便于审计。

## 性能优势

### 效率
1. **无需重处理内容**：不重新生成嵌入，保持向量引用；
2. **最小网络传输**：仅发送变更字段；
3. **数据库友好**：一次更新替代删除+重建，降低事务成本。

### 资源节省
- 内存：无需加载完整内容；
- CPU：无嵌入重算；
- IO：最少数据库操作；
- 网络：仅传元数据差异。

## 错误处理

### 常见错误
1. **记忆不存在**：`Memory with hash ... not found`；
2. **updates 不是字典**；
3. **标签格式错误**：必须是字符串数组；
4. **存储未初始化**：需先初始化集合。

### 恢复策略
- 错误信息清晰可追溯；
- 失败时回滚事务；
- 原始记忆保持不变；
- 详细日志可供排查。

## 迁移与兼容

### 向后兼容
- 旧记忆无需调整即可使用；
- 历史时间戳字段仍保留；
- 不会破坏现有 API。

### 采用策略
1. **即时可用**：部署后直接调用；
2. **渐进迁移**：可按模块分批使用；
3. **回退方案**：仍可通过“删+增”方式；
4. **上线前验证**：建议充分测试。

## 典型场景

### 记忆组织
1. **标签治理**：补充/替换标签，实现批量分类；
2. **优先级管理**：动态标注高/低优先级；
3. **状态跟踪**：标记已处理、待复查等状态。

### 高阶能力
1. **记忆关联**：添加引用/层级关系；
2. **生命周期**：记录过期/清理策略；
3. **访问控制**：记录所有者、共享策略、权限等。

## 测试与验证

### 单元测试
- 覆盖所有更新场景；
- 校验错误分支；
- 验证时间戳更新逻辑；
- 合并元数据的准确性。

### 集成测试
- MCP 端到端调用；
- 各存储后端兼容性；
- 性能基准；
- 跨平台验证。

### 性能测试
- 大数据批量更新；
- 并发写入；
- 监控内存使用；
- 响应时延统计。

## 未来计划

### 功能增强
1. **批量更新**：一次更新多条记忆；
2. **条件更新**：满足条件才写入；
3. **元数据 Schema 校验**；
4. **更新时间线**：记录变更历史；
5. **选择性更新**：仅更新指定字段。

### 后端支持
- sqlite-vec（Issue #40）
- 其他向量数据库
- 跨后端统一接口
- 针对不同后端定制优化

## 总结

该 API 提供了高效的记忆元数据管理能力，同时保持性能与兼容性，是后续再标签系统（Issue #45）与记忆归并（Issue #11）的基础模块。
