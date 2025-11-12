# 标签存储作业流程

## 目录结构
```
mcp_memory_service/
├── tests/
│   └── test_tag_storage.py    # 集成测试
├── scripts/
│   ├── validate_memories.py   # 校验脚本
│   └── migrate_tags.py        # 迁移脚本
```

## 执行步骤

1. **初始校验**
   ```bash
   python scripts/validate_memories.py
   ```
   - 生成当前数据状态报告。

2. **运行集成测试**
   ```bash
   python tests/test_tag_storage.py
   ```
   - 验证读写流程是否正常。

3. **执行迁移**
   ```bash
   python scripts/migrate_tags.py
   ```
   - 自动创建备份 → 复检 → 交互式确认 → 执行迁移 → 再次验证。

4. **迁移后复核**
   ```bash
   python scripts/validate_memories.py
   ```
   - 确认迁移成功且无数据漂移。

## 监控要求
- 备份保留至少 7 天；
- 关注日志中的标签相关错误；
- 迁移后一周内每日运行校验脚本；
- 使用不同标签组合测试搜索接口。

## 回滚
如发现问题，可执行：
```bash
python scripts/migrate_tags.py --rollback
```
