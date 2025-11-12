# Groq Agent Bridge 要求

```bash
pip install groq   # 或 uv pip install groq
export GROQ_API_KEY="your-api-key"
```

## 支持模型
| 模型 | 上下文 | 适用场景 | 速度 |
| --- | --- | --- | --- |
| llama-3.3-70b-versatile | 128K | 通用默认 | ~300ms |
| moonshotai/kimi-k2-instruct | 256K | Agentic 编码/工具调用 | ~200ms |
| llama-3.1-8b-instant | 128K | 极速简单任务 | ~100ms |

**Kimi K2 特性**：256K 窗口、1T 参数、前端/复杂编码表现优，185 tok/s。

## 使用示例
Python：
```python
from groq_agent_bridge import GroqAgentBridge
bridge = GroqAgentBridge()
print(bridge.call_model_raw("Explain quantum computing"))
print(bridge.call_model(prompt="生成 BST Python 代码",
                        model="llama-3.3-70b-versatile",
                        max_tokens=500,
                        temperature=0.3,
                        system_message="你是 Python 专家"))
```
CLI：
```bash
./scripts/utils/groq "What is machine learning?"
./scripts/utils/groq "Generate a React component" --model moonshotai/kimi-k2-instruct
./scripts/utils/groq "Rate complexity" --model llama-3.1-8b-instant
./scripts/utils/groq "Generate SQL" --max-tokens 200 --temperature 0.5 --system "DB expert" --json
```
脚本集成：
```bash
python groq_agent_bridge.py "Write a haiku" > resp.txt
json=$(python groq_agent_bridge.py "Explain REST" --json)
```
