# Natural Memory Triggers v7.1.3 CLI 参考

CLI 控制器（`memory-mode-controller.js`）提供实时配置、监控与诊断，无需编辑文件或重启 Claude Code。

## 基本用法
```bash
node ~/.claude/hooks/memory-mode-controller.js <command> [参数]
```

## 常用命令
- `status [--verbose|--json]`：查看档位/敏感度/性能指标；
- `profiles`：列出 speed_focused / balanced / memory_aware / adaptive 配置；
- `profile <name>`：切换性能档位；
- `sensitivity <value>`：0.0~1.0 之间，数值越低触发越频繁；
- `enable` / `disable`：启用或暂停触发；
- `reset [--force]`：恢复默认（balanced、0.6、cooldown=30000ms、maxMemories=5）。

## 测试与诊断
- `test "查询"`：模拟触发流程，展示各层耗时/置信度；
- `metrics`：输出平均延迟、命中率、触发成功率等；
- `health`：检测核心模块、配置、依赖、Memory Service/Git 状态；
- `config show/get/set`：查看或修改配置；
- `cache stats/clear/show`：管理语义缓存；
- `export` / `import`：备份/恢复配置或指标。

## 典型场景
- 架构/调研：`profile memory_aware` + `sensitivity 0.4`；
- 日常开发：`profile balanced`；
- 快速调试：`profile speed_focused` + `sensitivity 0.8`；
- 自适应：`profile adaptive`，系统自动学习偏好。

## 自动化示例
```bash
alias nmt-status='node ~/.claude/hooks/memory-mode-controller.js status'
node ~/.claude/hooks/memory-mode-controller.js profile balanced
watch -n5 "node ~/.claude/hooks/memory-mode-controller.js metrics"
```
Cron 任务监控：`0 * * * * node ... metrics --json >> ~/nmt-metrics.log`。

CLI 可输出 JSON，便于脚本集成；支持调试模式 `export CLAUDE_HOOKS_DEBUG=true`。

通过以上命令即可快速调优 Natural Memory Triggers，兼顾性能与记忆准确度。EOF
