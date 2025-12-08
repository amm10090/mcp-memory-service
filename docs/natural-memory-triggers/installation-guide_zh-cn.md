# Natural Memory Triggers v7.1.3 安装指南

智能记忆触发系统为 Claude Code 自动注入项目上下文。本文介绍快速安装与手动配置流程。

## 前置条件
- Claude Code CLI 已安装：`claude --version`
- Node.js ≥14：`node --version`
- MCP Memory Service 运行中：`curl -k https://localhost:8443/api/health`
- Hook 配置文件存在：`~/.claude/hooks/config.json`

## 安装方式
### 方法一：自动安装（推荐）
```bash
cd mcp-memory-service/claude-hooks
python install_hooks.py --natural-triggers
```
安装器会：校验环境、备份 `~/.claude/hooks/`、复制核心组件、合并配置、执行 18 项测试并输出报告。

### 方法二：手动安装
1. 创建目录：`mkdir -p ~/.claude/hooks/{core,utilities,tests}`；
2. 拷贝核心脚本与 CLI 控制器；
3. 添加配置段：`naturalTriggers` 与 `performance.profiles`；
4. 设置权限：`chmod +x ~/.claude/hooks/core/*.js` 等；
5. 测试：`node test-natural-triggers.js`、`node memory-mode-controller.js status`。

配置示例（节选）：
```json
{
  "naturalTriggers": {
    "enabled": true,
    "triggerThreshold": 0.6,
    "cooldownPeriod": 30000,
    "maxMemoriesPerTrigger": 5
  },
  "performance": {
    "defaultProfile": "balanced",
    "profiles": {
      "speed_focused": {...},
      "balanced": {...},
      "memory_aware": {...},
      "adaptive": {...}
    }
  }
}
```

## 验证步骤
1. 核查文件存在；
2. JSON 校验：`cat config.json | node -e 'JSON.parse...'`；
3. CLI：`node memory-mode-controller.js status/profiles`；
4. 测试 Memory Service 连接：`node memory-mode-controller.js test "What did we decide about authentication?"`。

## 安装后配置
- 调整性能档位：`node memory-mode-controller.js profile memory_aware`；
- 设置敏感度：`node ... sensitivity 0.6`；
- Git 集成：保持 14 天内 commit 信息、更新 CHANGELOG。

## 常见问题
- 找不到 Node：安装 Node.js 并验证；
- 权限错误：`chmod +x`、`chmod 755 ~/.claude/hooks`；
- 无法连接 Memory Service：确认服务启动、API Key、端口、证书；
- 配置损坏：用 `python -m json.tool` 校验，或恢复备份；
- Claude Code 未加载：路径是否 `~/.claude/hooks/`，必要时重启。%

## 检查清单
- [ ] 文件与权限正确；
- [ ] 配置含 Trigger & Performance 配置；
- [ ] CLI status 输出正常；
- [ ] 测试套件通过；
- [ ] Memory Service 连通；
- [ ] 已选定 profile/sensitivity。

## 下一步
- 阅读用户指南；
- 在 Claude 中提问“我们如何实现认证？”等以体验；
- 使用 `node memory-mode-controller.js metrics` 观察性能；
- 根据工作流调整 profile/sensitivity。
