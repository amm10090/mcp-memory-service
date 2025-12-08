# 测试说明（中文）

- 测试类型：unit、integration、contracts、performance。
- 常用命令：`pytest tests/`；单测 `pytest tests/unit -q`；集成 `pytest tests/integration -q`。
- 运行前确保依赖已安装，必要时设置后端配置（hybrid/cloudflare/sqlite-vec）。
- 详情见下方英文原文。

---

# README.md（中文说明）

测试运行与结构说明。

---

<!-- 说明：以下保留英文原文，供核对；若需中文摘要请参考主文档。 -->
# MCP-MEMORY-SERVICE Tests

This directory contains tests for the MCP-MEMORY-SERVICE project.

## Directory Structure

- `integration/` - Integration tests between components
- `unit/` - Unit tests for individual components
- `performance/` - Performance benchmarks

## Running Tests

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
```
