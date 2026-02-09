# Tencent Hunyuan OpenAI-Compatible Integration for Microsoft Agent Framework

腾讯云混元大模型 OpenAI 兼容接口集成包。

## 安装

```bash
pip install agent-framework-hunyuan-ai-openai --pre
```

## 快速开始

基于混元 OpenAI Compatible API（[官方文档](https://cloud.tencent.com/document/product/1729/111007)），
通过继承 `OpenAIChatClient` 实现无缝集成。

### 环境变量配置

```bash
export HUNYUAN_OPENAI_API_KEY="your-api-key"
# 可选：自定义模型（默认 hunyuan-turbos-latest）
export HUNYUAN_OPENAI_MODEL_ID="hunyuan-2.0-instruct-20251111"
```

### 基础用法

```python
import asyncio
from agent_framework_hunyuan_ai_openai import HunyuanOpenAIChatClient

async def main():
    client = HunyuanOpenAIChatClient(api_key="your-api-key")
    agent = client.as_agent(
        name="MyAgent",
        instructions="你是一个有帮助的AI助手。",
    )
    result = await agent.run("你好！")
    print(result)

asyncio.run(main())
```

### 带工具调用

```python
from agent_framework import tool
from agent_framework_hunyuan_ai_openai import HunyuanOpenAIChatClient

@tool(approval_mode="never_require")
def get_weather(location: str) -> str:
    """获取天气信息。"""
    return f"{location}: 晴天, 25°C"

agent = HunyuanOpenAIChatClient(api_key="your-key").as_agent(
    name="WeatherAgent",
    instructions="你是天气查询助手。",
    tools=get_weather,
)
```

## 支持的模型

| 模型名称 | 说明 |
|---------|------|
| `hunyuan-turbos-latest` | 混元最新 Turbo-S 模型（默认） |
| `hunyuan-2.0-instruct-20251111` | 混元 2.0 指令模型 |
| `hunyuan-pro` | 混元 Pro 模型 |
| `hunyuan-standard` | 混元 Standard 模型 |
| `hunyuan-lite` | 混元 Lite 模型（免费） |

## API 参考

- API 端点: `https://api.hunyuan.cloud.tencent.com/v1`
- [API Key 管理](https://console.cloud.tencent.com/hunyuan/start)
- [官方文档](https://cloud.tencent.com/document/product/1729/111007)
