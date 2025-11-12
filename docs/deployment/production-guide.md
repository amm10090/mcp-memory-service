# MCP Memory Service 生产部署指南

## 🚀 快速开始
默认启用记忆归并、mDNS 自动发现、HTTPS 与自启动。

```bash
bash install_service.sh         # 安装
./update_service.sh             # 按需更新配置
sudo systemctl start mcp-memory # 启动
```

验证：
```bash
sudo systemctl status mcp-memory
curl -k https://localhost:8001/api/health
avahi-browse -t _mcp-memory._tcp
```

## 📋 服务信息
- 服务名：`memory._mcp-memory._tcp.local.`
- HTTPS 地址：`https://localhost:8001`
- API Key：`mcp-0b1ccbde2197a08dcb12d41af4044be6`
- 自启动：✅
- 归并：✅
- mDNS：✅

## 🛠 管理脚本
```bash
./service_control.sh start|stop|status|logs|health
```

## 📖 参考
- 全量指南：`COMPLETE_SETUP_GUIDE.md`
- systemd 与脚本：`mcp-memory.service`、`archive/setup-development/`

✅ 可直接投入生产。
