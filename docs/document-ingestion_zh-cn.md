# 文档摄取（v7.6.0+）

针对多种文档格式提供增强解析，并可选接入 semtools 以获得更高质量的抽取效果。

## 支持格式

| 格式 | 原生解析器 | 搭配 Semtools | 质量 |
| --- | --- | --- | --- |
| PDF | PyPDF2 / pdfplumber | LlamaParse | 卓越（含 OCR、表格） |
| DOCX | 不支持 | LlamaParse | 卓越 |
| PPTX | 不支持 | LlamaParse | 卓越 |
| TXT/MD | 内置 | 不适用 | 完美 |

## Semtools 集成（可选）

安装 [semtools](https://github.com/run-llama/semtools) 以获得更强的解析：

```bash
# 推荐：npm 安装
npm i -g @llamaindex/semtools

# 或使用 cargo
cargo install semtools

# 可选：配置 LlamaParse API Key 获得最佳质量
export LLAMAPARSE_API_KEY="your-api-key"
```

## 配置项

```bash
# 文档分块
export MCP_DOCUMENT_CHUNK_SIZE=1000       # 每块字符数
export MCP_DOCUMENT_CHUNK_OVERLAP=200     # 分块重叠

# LlamaParse API Key（可选）
export LLAMAPARSE_API_KEY="llx-..."
```

## 使用示例

```bash
# 摄取单个文件
claude /memory-ingest document.pdf --tags documentation

# 摄取目录
claude /memory-ingest-dir ./docs --tags knowledge-base

# Python 方式
from mcp_memory_service.ingestion import get_loader_for_file

loader = get_loader_for_file(Path("document.pdf"))
async for chunk in loader.extract_chunks(Path("document.pdf")):
    await store_memory(chunk.content, tags=["doc"])
```

## 功能特性

- **自动识别格式**：为每个文件选择最佳 Loader。
- **智能分块**：遵循段落/句子边界。
- **元数据增强**：保留文件信息、解析方式、页码。
- **优雅回退**：在 semtools 不可用时退回原生解析。
- **进度跟踪**：实时报告块处理进度。

## 性能注意事项

- LlamaParse 输出质量最高，但需 API Key 与外网。
- 原生解析器可离线运行，但复杂文档效果略差。
- 分块尺寸影响检索粒度与上下文完整性。
- 较大的重叠可提升连续性，但会增加存储占用。
