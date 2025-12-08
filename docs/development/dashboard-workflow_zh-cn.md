# 仪表盘开发工作流

记录互动式仪表盘的关键流程，避免反复踩坑。

## 1. 静态文件修改后务必重启服务 ⚠️
- FastAPI/uvicorn 会缓存 CSS/JS/HTML；
- 不重启会导致浏览器一直加载旧版脚本/样式。

```bash
# 重启 HTTP 服务
systemctl --user restart mcp-memory-http.service
# 浏览器强制刷新
Ctrl+Shift+R（Win/Linux）或 Cmd+Shift+R（macOS）
```

## 2. Claude Code 自动化 Hook ✅
在 `.claude/settings.local.json` 加入：
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matchers": ["Write(file_path:**/web/static/*.css)", ...],
        "hooks": [
          {
            "type": "command",
            "command": "bash",
            "args": [
              "-c",
              "systemctl --user restart mcp-memory-http.service && echo '\n⚠️  REMINDER: Hard refresh browser (Ctrl+Shift+R)!'"
            ]
          }
        ]
      },
      {
        "matchers": ["Write(file_path:**/web/static/*.css)", "Edit(file_path:**/web/static/*.css)"],
        "hooks": [
          {
            "type": "command",
            "command": "bash",
            "args": [
              "-c",
              "if grep -E 'background.*:.*white|#fff|color.*:.*white' src/mcp_memory_service/web/static/style.css | grep -v 'dark-mode'; then echo '\n⚠️  WARNING: Hardcoded light colors, remember dark-mode overrides!'; fi"
            ]
          }
        ]
      }
    ]
  }
}
```
**作用**：
- 修改 CSS/JS/HTML 自动重启 HTTP；
- 控制台提示“记得硬刷新”；
- 扫描硬编码浅色，提醒补 dark-mode。

## 3. 深色模式检查表
- 禁止硬编码 `background: white`、`color: #fff`；
- 新增组件需提供 `body.dark-mode` 覆盖；
- 代码示例：
```css
.chunk-content { background: white; }
body.dark-mode .chunk-content { background: #111827 !important; color: #d1d5db !important; }
```

## 4. 浏览器缓存
- 强制刷新：Ctrl+Shift+R / Cmd+Shift+R；
- URL 加 `?nocache=timestamp`；
- DevTools 开启 “Disable cache”。

## 开发清单
- [ ] 修改过 CSS/JS/HTML；
- [ ] 已重启 HTTP 服务；
- [ ] 浏览器硬刷新；
- [ ] 检查 console；
- [ ] 验证 dark/light 模式。

## 性能目标（v7.2.2 验证）
| 项目 | 目标 | 常见值 |
| --- | --- | --- |
| 页面加载 | <2s | 25ms |
| Memory 操作 | <1s | ~26ms |
| Tag 搜索 | <500ms | <100ms |

若性能下降：
1. DevTools Network 查慢请求；
2. 查看服务器日志；
3. DevTools Profiler 分析 JS。

## 使用 browser-mcp 调试
```bash
mcp__browsermcp__browser_navigate http://127.0.0.1:8888/
mcp__browsermcp__browser_screenshot
mcp__browsermcp__browser_get_console_logs
```

## 常见坑
1. 忘记重启服务 → 用 Hook；
2. 忘记清缓存；
3. 未测深色模式；
4. 忽视 console 报错；
5. 未测 768px/1024px 响应式。

## 参考
- `CLAUDE.md`：Interactive Dashboard 章节；
- `docs/implementation/performance.md`；
- Wiki Troubleshooting。
