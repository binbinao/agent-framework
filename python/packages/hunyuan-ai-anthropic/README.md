# Tencent Hunyuan Anthropic-Compatible Integration for Microsoft Agent Framework

腾讯云混元大模型 Anthropic 兼容接口集成包。

## 安装

```bash
pip install agent-framework-hunyuan-ai-anthropic --pre
```

## 快速开始

基于混元 Anthropic Compatible API（[官方文档](https://cloud.tencent.com/document/product/1729/127293)），
通过继承 `AnthropicClient` 实现无缝集成。

### 环境变量配置

```bash
export HUNYUAN_ANTHROPIC_API_KEY="your-api-key"
# 可选：自定义模型（默认 hunyuan-turbos-latest）
export HUNYUAN_ANTHROPIC_MODEL_ID="hunyuan-pro"
```

### 基础用法

```python
import asyncio
from agent_framework_hunyuan_ai_anthropic import HunyuanAnthropicClient

async def main():
    client = HunyuanAnthropicClient(api_key="your-api-key")
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
from agent_framework_hunyuan_ai_anthropic import HunyuanAnthropicClient

@tool(approval_mode="never_require")
def get_weather(location: str) -> str:
    """获取天气信息。"""
    return f"{location}: 晴天, 25°C"

agent = HunyuanAnthropicClient(api_key="your-key").as_agent(
    name="WeatherAgent",
    instructions="你是天气查询助手。",
    tools=get_weather,
)
```

## 支持的模型

| 模型名称 | 说明 |
|---------|------|
| `hunyuan-turbos-latest` | 混元最新 Turbo-S 模型（默认） |
| `hunyuan-pro` | 混元 Pro 模型 |
| `hunyuan-standard` | 混元 Standard 模型 |
| `hunyuan-lite` | 混元 Lite 模型（免费） |

## API 参考

- API 端点: `https://api.lkeap.cloud.tencent.com/anthropic`
- [API Key 管理](https://console.cloud.tencent.com/lkeap)
- [官方文档](https://cloud.tencent.com/document/product/1729/127293)
