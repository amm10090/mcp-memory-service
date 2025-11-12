# 仪表盘截图占位说明

此目录用于存放 MCP Memory Service 仪表盘截图。

## v3.3.0 仪表盘特性
- 渐变背景 + 卡片式现代设计；
- 实时统计：服务器指标、记忆数量；
- 交互式 API 面板（悬浮说明）；
- 技术栈徽章：FastAPI / SQLite-vec / PyTorch 等；
- 自适应布局，桌面与移动端兼容；
- 30 秒自动刷新。

## 访问地址
- Dashboard: http://localhost:8001
- mDNS: http://mcp-memory-service.local:8001
- API Docs: http://localhost:8001/api/docs
- ReDoc: http://localhost:8001/api/redoc

## 截图步骤
1. 启动 HTTP 服务；
2. 打开浏览器访问 http://localhost:8001；
3. 待实时数据加载完毕；
4. 进行整页截图；
5. 保存为 `dashboard-v3.3.0.png` 至本目录。
