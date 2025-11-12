# Natural Memory Triggers v7.1.3 性能优化指南

## 性能概览
- 多层架构：Instant (<50ms)、Fast (<150ms)、Intensive (<500ms)；
- 实战数据：触发准确率 85%+，Instant 缓存命中 <5ms，Fast 语义检测 <150ms。

## 预设档位
| 档位 | 场景 | 配置 | 适用 |
| --- | --- | --- | --- |
| speed_focused | 追求极低延迟 | 仅启用 Instant；无后台处理；maxLatency=100ms | 快速调试/Pair | 
| balanced（推荐） | 日常开发 | Instant+Fast；后台处理；maxLatency=200ms | 常规编码 |
| memory_aware | 注重上下文 | 三层全开；maxLatency=500ms；全量语义分析 | 架构/调研 |
| adaptive | 自适应 | 自动调节阈值/层次 | 长期学习使用习惯 |

切换示例：`node memory-mode-controller.js profile balanced`。

## 监控
```bash
node memory-mode-controller.js status      # 基本状态
node memory-mode-controller.js metrics     # 详细指标
watch -n5 "node ... metrics"            # 持续监控
```
关注：平均延迟、层级延迟、缓存命中率、触发准确度、资源占用等。

## 缓存优化
```bash
node ... cache stats
node ... config set performance.cacheSize 75
node ... config set performance.cacheCleanupThreshold 0.8
node ... cache analyze
```
缓存策略：
- 高命中：增大 cacheSize、延长保留；
- 低内存：减小 cacheSize，提升清理阈值。

## Memory Service 调优
```bash
node ... config set memoryService.timeout 5000
node ... config set memoryService.keepAlive true
```
- SQLite：开启 `localOptimizations`、较短 timeout；
- Cloudflare：timeout≈8000ms、retry=2；
- ChromaDB：开启批量请求。

## Git 集成
```bash
node ... config set gitAnalysis.commitLookback 7
node ... config set gitAnalysis.maxCommits 10
```
大型仓库：缩小 lookback、禁用 changelog 解析、开启 lightweight 模式。

## 资源优化
- 内存：`export NODE_OPTIONS="--max-old-space-size=512 --gc-interval=100"`；
- CPU：低配禁用后台、maxConcurrent=1；高配可启用 parallel processing。

## 问题诊断
- 高延迟：切换档位、优化缓存/后端、降低分析深度；
- 缓存命中低：增大 cache、延长保留、分析模式；
- Memory Service 超时：测试 `curl`、增加 timeout、检查网络/后端；
- Claude 未加载：验证 `~/.claude/hooks` 路径、重启。

## 进阶
- 自定义档位：`node ... config set performance.profiles.code_review '{...}'`
- 自动化脚本：根据时间段自动切换档位；
- 日/周维护：定期 `metrics`、导出数据、清理缓存。

Natural Memory Triggers 支持高度可调的性能策略，合理组合档位、缓存、后端设置即可在速度与记忆准确度间取得最佳平衡。🚀
