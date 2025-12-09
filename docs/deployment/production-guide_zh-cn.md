# MCP Memory Service - 生产环境部署指南

[简体中文](production-guide_zh-cn.md) | [English](production-guide.md)

## 🚀 快速开始

默认配置包含 **整合系统**、**mDNS 自动发现**、**HTTPS**、**自启动**。

### **Installation**
```bash
# 1. Install the service
bash install_service.sh

# 2. Update configuration (if needed)
./update_service.sh

# 3. Start the service
sudo systemctl start mcp-memory
```

### **Verification**
```bash
# Check service status
sudo systemctl status mcp-memory

# Test API health
curl -k https://localhost:8000/api/health

# Verify mDNS discovery
avahi-browse -t _mcp-memory._tcp
```

## 📋 **Service Details**

- **Service Name**: `memory._mcp-memory._tcp.local.`
- **HTTPS Address**: https://localhost:8000 
- **API Key**: `mcp-0b1ccbde2197a08dcb12d41af4044be6`
- **Auto-Startup**: ✅ Enabled
- **Consolidation**: ✅ Active
- **mDNS Discovery**: ✅ Working

## 🛠️ **Management**

```bash
./service_control.sh start     # Start service
./service_control.sh stop      # Stop service  
./service_control.sh status    # Show status
./service_control.sh logs      # View logs
./service_control.sh health    # Test API
```

## 📖 **Documentation**

- **Complete Guide**: `COMPLETE_SETUP_GUIDE.md`
- **Service Files**: `mcp-memory.service`, management scripts
- **Archive**: `archive/setup-development/` (development files)

**✅ Ready for production use!**
