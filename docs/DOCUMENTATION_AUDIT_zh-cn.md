# 文档审计报告
**日期**：2025-07-26  
**分支**：feature/http-sse-sqlite-vec  
**目的**：为统一安装器合并进行整体系文档分析

## 当前文档清单

### 安装相关
- `README.md`（根目录）—— 主要安装说明，需补充后端选择指引。
- `docs/guides/installation.md` —— 详细安装指南（12KB）。
- `docs/guides/windows-setup.md` —— Windows 专用步骤（4KB）。
- `docs/guides/UBUNTU_SETUP.md` —— Ubuntu 专用步骤。
- `docs/sqlite-vec-backend.md` —— SQLite-vec 后端指南。
- `MIGRATION_GUIDE.md`（根目录）—— ChromaDB → SQLite-vec 迁移。
- `scripts/install_windows.py` —— Windows 安装脚本。
- `scripts/installation/install.py` —— 另一套安装脚本。

### 平台专用
- `docs/integration/homebrew/`（7 个文件）—— Homebrew PyTorch 集成：
  - `HOMEBREW_PYTORCH_README.md` —— 主文档。
  - `HOMEBREW_PYTORCH_SETUP.md` —— 步骤。
  - `TROUBLESHOOTING_GUIDE.md` —— 故障排查。
- `docs/guides/windows-setup.md` —— Windows 指南。
- `docs/guides/UBUNTU_SETUP.md` —— Linux 指南。

### API / 技术
- `docs/IMPLEMENTATION_PLAN_HTTP_SSE.md` —— HTTP/SSE 实施计划。
- `docs/guides/claude_integration.md` —— Claude Desktop 集成。
- `docs/guides/invocation_guide.md` —— 使用方式。
- `docs/technical/` —— 各类技术细节。

### 迁移与排障
- `MIGRATION_GUIDE.md`。
- `docs/guides/migration.md`。
- `docs/guides/troubleshooting.md`。
- `docs/integration/homebrew/TROUBLESHOOTING_GUIDE.md`。

## 发现的缺口

1. **缺少主安装指南**：无单一真源，后端选择分散，硬件优化缺乏统一说明。
2. **旧硬件支持不足**：2015 MacBook Pro 没有明确流程，Intel Mac 路线模糊，Homebrew 指南隐蔽。
3. **存储后端对比缺失**：没有 ChromaDB vs SQLite-vec 的全面比较，也缺少显著的迁移说明。
4. **HTTP/SSE API 文档不完整**：仅有实施计划，缺乏面向用户的 API 说明与示例。

## 整合策略

### 阶段 1：创建主文档
1. `docs/guides/INSTALLATION_MASTER.md` —— 综合安装指南。
2. `docs/guides/STORAGE_BACKENDS.md` —— 后端对比与选择建议。
3. `docs/guides/HARDWARE_OPTIMIZATION.md` —— 各平台优化建议。
4. `docs/api/HTTP_SSE_API.md` —— 完整 API 文档。

### 阶段 2：平台整合
1. `docs/platforms/macos-intel-legacy.md` —— 2015 MacBook Pro 场景。
2. `docs/platforms/macos-modern.md` —— 新款 Mac。
3. `docs/platforms/windows.md` —— Windows 合并指南。
4. `docs/platforms/linux.md` —— Linux 合并指南。

### 阶段 3：合并与重构
1. 去除重复内容并相互引用。
2. 更新 `README.md` 指向新结构。
3. 归档或删除过时文档。

## 高优任务
1. ✅ 完成本审计。
2. ⏳ 撰写主安装指南。
3. ⏳ 整合平台指南。
4. ⏳ 记录硬件智能矩阵。
5. ⏳ 汇总迁移文档。
6. ⏳ 更新 README 结构。

## 内容质量评估

**优秀（保留/增强）**：`MIGRATION_GUIDE.md`、`docs/sqlite-vec-backend.md`、Homebrew 主文档。  
**需改进**：`README.md`（后端选择不突出）、`docs/guides/installation.md`（缺乏硬件维度）、多个排障文档重复。  
**重复待并**：安装说明、Windows 步骤、Homebrew 文档。

## 下一步
1. 撰写主安装指南。
2. 整合硬件相关内容。
3. 明确用户旅程。
4. 实机验证文档准确性。
