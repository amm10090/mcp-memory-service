# 记忆迁移技术说明

本文记录 MCP Memory Service 中 ChromaDB 记忆迁移流程的技术细节，涵盖本地/远端场景、核心实现与配置要点。

## 概览

迁移通过 `scripts/mcp-migration.py` 脚本执行，可在不同 ChromaDB 实例之间转移记忆，既支持本地环境，也支持远端服务器，同时保证数据一致性。

## 迁移类型

1. **本地 → 远端**：开发环境向生产环境同步记忆。
2. **远端 → 本地**：从线上拉取数据以构建备份或本地调试环境。

## 技术实现

### 环境校验

迁移开始前脚本会：
- 检查 Python 版本与依赖；
- 校验 ChromaDB 路径/配置；
- 远端模式下测试网络连通性。

### 迁移流程

1. **连接建立**：
   - 同时连接源、目标 ChromaDB；
   - 检查集合是否存在，必要时创建；
   - 初始化嵌入函数以保证向量维度一致。

2. **数据传输**：
   - 默认批次 10 条，批间延时 1s，防止目标过载；
   - 进行重复检测，避免冗余；
   - 保留 metadata 与文档引用关系。

3. **结果校验**：
   - 比较记录数量；
   - 校验数据完整性；
   - 记录详细日志。

### 错误处理

脚本会捕获并提示：
- 连接失败 / 配置错误；
- 集合访问或权限问题；
- 数据传输中断；
- 运行环境不兼容等。

### 性能参数
- 批大小：默认 10；
- 批间延时：1s；
- 内存占用：按批处理控制；
- 网络：内置超时与重试逻辑。

## 配置示例

```json
{
  "type": "local | remote",
  "config": {
    "path": "/path/to/chroma",  // 本地
    "host": "remote-host",       // 远端
    "port": 8001                  // 远端端口
  }
}
```

## 最佳实践

- **迁移前**：确认磁盘空间、网络连通性并备份数据；
- **迁移中**：监控日志，避免中途终止；
- **迁移后**：核对统计、验证记忆可访问并记录结果。

## 故障排查

- **连接失败**：检查网络、端口、防火墙；
- **传输问题**：确认磁盘空间、集合权限、系统资源；
- **环境异常**：重新执行环境校验，确认依赖版本。

## 使用示例

```bash
# 本地 → 远端
python scripts/mcp-migration.py \
  --source-type local --source-config /path/to/local/chroma \
  --target-type remote --target-config '{"host": "remote-host", "port": 8001}'

# 远端 → 本地
python scripts/mcp-migration.py \
  --source-type remote --source-config '{"host": "remote-host", "port": 8001}' \
  --target-type local --target-config /path/to/local/chroma
```

```python
from scripts.mcp_migration import migrate_memories

migrate_memories(
    source_type='local',
    source_config='/path/to/local/chroma',
    target_type='remote',
    target_config={'host': 'remote-host', 'port': 8001}
)
```
