# Venus OpenAI-Compatible Integration for Microsoft Agent Framework

Venus OpenAI 兼容接口集成包，支持多种主流大语言模型。

## 安装

```bash
pip install agent-framework-venus-openai --pre
```

## 快速开始

### 环境变量配置

```bash
export VENUS_OPENAI_API_KEY="your-api-key"
# 可选：自定义模型（默认 deepseek-v3.2）
export VENUS_OPENAI_MODEL_ID="deepseek-v3.2"
```

### 基础用法

```python
import asyncio
from agent_framework_venus_openai import VenusOpenAIChatClient

async def main():
    client = VenusOpenAIChatClient(api_key="your-api-key")
    agent = client.as_agent(
        name="VenusAgent",
        instructions="你是一个有帮助的AI助手。",
    )
    result = await agent.run("你好！")
    print(result)

asyncio.run(main())
```

### 带工具调用

```python
from agent_framework import tool
from agent_framework_venus_openai import VenusOpenAIChatClient

@tool(approval_mode="never_require")
def get_weather(location: str) -> str:
    """获取天气信息。"""
    return f"{location}: 晴天, 25°C"

async def main():
    agent = VenusOpenAIChatClient(api_key="your-key").as_agent(
        name="WeatherAgent",
        instructions="你是天气查询助手。",
        tools=get_weather,
    )
    result = await agent.run("北京的天气怎么样？")
    print(result)
```

## 支持的模型

### DeepSeek 系列
- `deepseek-v3.2` - DeepSeek V3.2（默认）
- `deepseek-v3.1-terminus` - DeepSeek V3.1 Terminus
- `deepseek-ocr` - DeepSeek OCR

### GLM 系列
- `glm-4.6-fp8` - GLM 4.6 FP8
- `glm-4.7` - GLM 4.7
- `glm-5` - GLM 5

### 混元系列
- `hunyuan-turbo` - 混元 Turbo
- `hunyuan-turbos-latest` - 混元 Turbos 最新版
- `hunyuan-turbos-vision-latest` - 混元 Turbos Vision 最新版（支持多模态）

### 其他模型
- `kimi-k2.5` - Kimi K2.5
- `minimax-m2.5` - Minimax M2.5
- `qwen3-235b-a22b-2507-fp8` - Qwen3 235B
- `qwen3-235b-a22b-thinking-2507-fp8` - Qwen3 235B Thinking

## API 参考

- **API 端点**: http://v2.open.venus.oa.com/llmproxy
- **完整路径**: http://v2.open.venus.oa.com/llmproxy/v1/chat/completions
- **协议**: OpenAI Compatible API

## 特性

- ✅ 完全兼容 OpenAI API
- ✅ 支持函数调用（Function Calling）
- ✅ 支持流式输出（Streaming）
- ✅ 支持多模态输入（部分模型）
- ✅ 环境变量配置
- ✅ 类型安全（完整类型注解）

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
