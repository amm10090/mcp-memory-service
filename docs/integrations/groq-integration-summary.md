# Groq Bridge 集成摘要

## 概览
- Groq 桥接提供 10 倍速的 LLM 推理（可选增强项，默认仍用 Gemini CLI）；
- 文件位置：`scripts/utils/groq_agent_bridge.py`，文档见 `docs/integrations/groq-bridge.md`；
- `CLAUDE.md`、code-quality-guard agent、pre-commit hook 已支持 Groq/Gemini 双模式。

## 用户需执行
```bash
pip install groq      # 或 uv pip install groq
export GROQ_API_KEY="your-api-key"
```
> API Key 获取：https://console.groq.com/keys

## 使用
- **Gemini CLI（默认）**：`gemini "Analyze complexity..."`
- **Groq 桥接**：`python scripts/utils/groq_agent_bridge.py "Analyze complexity..." --model moonshotai/kimi-k2-instruct`
- CLI 支持 `--json`、`--temperature`、`--max-tokens` 等参数。

## Pre-commit Hook
- 位于 `.git/hooks/pre-commit`（默认调用 Gemini CLI）；
- 检查复杂度、安全、SQL/XSS/命令注入、硬编码密钥等；
- 若需改用 Groq：将脚本中的 `gemini` 命令替换为 `python scripts/utils/groq_agent_bridge.py`。

## 测试
```bash
bash scripts/utils/test_groq_bridge.sh             # Groq 桥测试
python scripts/utils/groq_agent_bridge.py "test"   # 手动测试
```
Git 提交时自动运行 pre-commit：`git commit -m "test"`。

## 性能对比
| 任务 | Gemini | Groq | 提升 |
| --- | --- | --- | --- |
| 单文件复杂度分析 | 3-5s | 0.3-0.5s | ~10x |
| 安全扫描 | 3-5s | 0.3-0.5s | ~10x |
| 多文件 TODO 分析 | 30s | 3s | ~10x |

## 建议场景
- 日常临时分析：继续使用 Gemini，零配置；
- CI/CD / 批量分析 / 大型文件：启用 Groq，显著缩短等待时间。

## 故障排查
- `ModuleNotFoundError: groq` → 安装 `groq`；
- `GROQ_API_KEY required` → 设置环境变量；
- Gemini CLI 认证异常 → 手动运行 `gemini --version` 完成登录。

相关文档：`docs/integrations/groq-bridge.md`、`.claude/agents/code-quality-guard.md`、`CLAUDE.md` agent 章节。EOF
