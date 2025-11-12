# Linux systemd 服务部署

## 概述
systemd 服务可实现：
- 登录自动启动、logout 后保持运行（启用 linger）；
- 失败自动重启；
- 日志汇总到 journald；
- `systemctl` 统一管理。

## 快速安装
```bash
cd /path/to/mcp-memory-service
bash scripts/service/install_http_service.sh
```
脚本会检查依赖、提示安装方式（用户/系统）、复制 service 文件、重载 systemd，并给出下一步。

### 手动安装
**用户级（推荐，无需 sudo）**
```bash
mkdir -p ~/.config/systemd/user
cp scripts/service/mcp-memory-http.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user start mcp-memory-http.service
systemctl --user enable mcp-memory-http.service
loginctl enable-linger $USER
```

**系统级（需 sudo）**
```bash
sudo cp scripts/service/mcp-memory-http.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start mcp-memory-http.service
sudo systemctl enable mcp-memory-http.service
```

## 管理命令
```bash
systemctl --user start|stop|restart|status mcp-memory-http.service
journalctl --user -u mcp-memory-http.service -f   # 实时日志
journalctl --user -u ... -n 50                   # 最近日志
```

## 配置
用户版：`~/.config/systemd/user/mcp-memory-http.service`；系统版：`/etc/systemd/system/`。

关键字段：
- `WorkingDirectory`、`Environment=PATH/ PYTHONPATH`、`EnvironmentFile=.env`；
- `ExecStart` 指向 `scripts/server/run_http_server.py`；
- `Restart=always`、`RestartSec=10`；
- 用户服务不能写 `User=/Group=`，`WantedBy=default.target`。

`.env` 修改后需 `systemctl --user restart ...`。

## 常见问题
1. **status=216/GROUP**：删除用户服务里的 `User=`/`Group=`；
2. **Permission denied**：确保 `.env`、venv、脚本对当前用户可读；系统服务需设置权限；
3. **服务未启动**：`systemctl --user status` 查看错误、`journalctl` 获取细节；
4. **退出后停止**：未开启 linger → `loginctl enable-linger $USER`。

完成后即可通过 systemd 方式运行 HTTP Server，提升可靠性与可维护性。
