# 过时工作流存档

此目录记录已被自动化方案取代的历史文档，仅供参考。

## 内容概览

### `load_memory_context.md`（2025-08）
- **原用途**：在 Claude Code 会话启动阶段手动使用 curl 加载记忆上下文；
- **淘汰原因**：2025-09 起由 Natural Memory Triggers v7.1.3+ 全面取代。

#### 演进时间线

1. **Phase 1：手动加载（2025-08）** ❌ 已废弃
```bash
curl -k -s -X POST https://server:8443/mcp \
  -H "Authorization: Bearer token" \
  -d '{"method": "tools/call", "params": {...}}'
```
问题：全凭手工、易出错、需复制粘贴且网络配置复杂。

2. **Phase 2：SessionStart Hook（2025-08~09）** ✅ 改进版
- 会话启动自动检索记忆；
- 支持项目识别、智能排序、Git 上下文。

3. **Phase 3：Natural Memory Triggers（2025-09+）** ✅ 生产方案
- 触发准确率 85%+；
- 50ms / 500ms 多级性能；
- CLI 实时配置；
- 根据使用习惯自适应学习。

4. **Phase 4：团队协作（v7.0.0+）** ✅ 网络分发
- OAuth 2.1 动态注册；
- Claude Code HTTP 传输；
- 团队零配置共享。

#### 当前做法
```bash
cd claude-hooks && python install_hooks.py --natural-triggers
# 从此自动注入上下文，无需手动命令
```
优势：零人工、85%+ 准确率、智能模式识别、性能分层、支持 OAuth 团队共享。

#### 历史价值
- 展示 UX 从手动 → 半自动 → 全自动的演进；
- 将痛点（手动 curl）转化为产品改进；
- 佐证“不断降低摩擦”的设计理念。

#### 若仍在使用旧流程
```bash
# 旧：手动
curl -k -s -X POST https://server:8443/mcp ... | jq -r '.result.content[0].text'

# 新：一次安装，永久自动
python claude-hooks/install_hooks.py --natural-triggers
```
详见 [Natural Memory Triggers 指南](https://github.com/doobidoo/mcp-memory-service/wiki/Natural-Memory-Triggers-v7.1.0)。

---

**最近更新**：2025-10-25  
**状态**：仅作历史归档
