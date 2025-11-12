# SQLite-vec 嵌入修复汇总

针对 Issue #64（SQLite-vec 语义搜索返回 0 结果）所做的修复与脚本说明。

## 根因
1. `sentence-transformers`、`torch` 仅为可选依赖，缺失时静默失败；
2. 向量表在模型初始化前以固定维度创建，导致维度不匹配；
3. 依赖缺失/生成失败未抛错，返回零向量；
4. memories 与 embeddings 表间可能出现 rowid 不一致。

## 修复项
1. **依赖**：`sentence-transformers>=2.2.2`、`torch>=1.6.0` 调整为核心依赖；
2. **初始化顺序**：先加载嵌入模型，再创建向量表，保证维度一致；
3. **错误处理**：嵌入生成失败直接抛异常并记录日志；
4. **存取流程**：
   - `store()` 添加 try/except，必要时回退 rowid 写入；
   - `retrieve()` 检查 embeddings 表为空的情况，并输出调试日志；
   - `_generate_embedding()` 校验维度与数值有效性；
5. **诊断脚本**：`scripts/test_sqlite_vec_embeddings.py` 覆盖依赖、初始化、存储/搜索全链路。

## 测试脚本
```bash
python3 scripts/test_sqlite_vec_embeddings.py
```
验证内容：
- 依赖安装；
- Storage 初始化；
- 嵌入生成、存储与检索；
- 数据库完整性。

## 迁移/修复流程
1. `uv pip install -e .` 更新依赖；
2. 尝试快速修复：
   ```bash
   python3 scripts/repair_sqlite_vec_embeddings.py /path/to/sqlite_vec.db
   ```
   重新生成缺失嵌入。
3. 若失败，执行全量迁移：
   ```bash
   python3 scripts/migrate_sqlite_vec_embeddings.py /path/to/sqlite_vec.db
   ```
   - 自动备份原库；
   - 导出所有记忆；
   - 建立新库、重建嵌入并恢复数据。

## 后续规划
- [x] 嵌入迁移脚本；
- [x] 现有记忆的嵌入再生能力；
- [ ] 批量嵌入生成以提升性能；
- [ ] 更完善的 rowid 同步策略；
- [ ] 启动时自动检测并修复；
- [ ] 嵌入模型版本化，便于模型升级。
