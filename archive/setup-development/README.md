<!-- 说明：以下保留英文原文，供核对；若需中文摘要请参考主文档。 -->
> 中文摘要：本文档保留英文原文，概述「Development Files Archive」的背景与要点，供历史记录与快速阅览。

# Development Files Archive

This directory contains files used during the development and setup process:

## 📁 Archived Files

- **`setup_consolidation_mdns.sh`** - Original manual startup script (superseded by systemd service)
- **`test_service.sh`** - Debug script for troubleshooting service startup issues
- **`STARTUP_SETUP_GUIDE.md`** - Original startup guide (superseded by COMPLETE_SETUP_GUIDE.md)

## 🔄 Superseded By

These files were used during development but are now superseded by:

- **Production Service**: `mcp-memory.service` + `service_control.sh`
- **Complete Documentation**: `COMPLETE_SETUP_GUIDE.md`
- **Quick Start**: `README_PRODUCTION.md`

## 🗂️ Purpose

These files are kept for:
- Historical reference
- Debugging if needed
- Understanding the development process
- Potential future troubleshooting

**Note**: Use the production files in the root directory for normal operation.