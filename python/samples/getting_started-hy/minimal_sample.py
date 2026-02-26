# Copyright (c) Microsoft. All rights reserved.
"""
腾讯云混元大模型适配示例

这个示例展示了如何将agent-framework从OpenAI适配到腾讯云混元大模型。

使用步骤：
1. 获取腾讯云API密钥：访问 https://console.cloud.tencent.com/hunyuan
2. 设置环境变量：export TENCENT_HUNYUAN_API_KEY="your-api-key"
3. 运行示例：python minimal_sample.py

注意：腾讯云混元大模型需要OpenAI兼容的API接口支持。
"""

import asyncio
import os
from random import randint
from typing import Annotated

# 导入dotenv用于.env文件支持
from dotenv import load_dotenv

from agent_framework import tool
from agent_framework.openai import OpenAIChatClient

# 加载.env文件中的环境变量（指定正确路径，override=True 确保覆盖已有的同名环境变量）
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)


# NOTE: approval_mode="never_require" is for sample brevity. Use "always_require" in production; see samples/getting_started/tools/function_tool_with_approval.py and samples/getting_started/tools/function_tool_with_approval_and_threads.py.
@tool(approval_mode="never_require")
def get_weather(
    location: Annotated[str, "The location to get the weather for."],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."


# 腾讯云混元大模型配置
# 腾讯云混元大模型API端点（官方提供的OpenAI兼容接口）
TENCENT_HUNYUAN_BASE_URL = "https://api.hunyuan.cloud.tencent.com/v1"
# 腾讯云混元大模型名称
TENCENT_HUNYUAN_MODEL = "hunyuan-2.0-instruct-20251111"

# 从环境变量获取API密钥，优先使用.env文件中的配置
tencent_api_key = os.getenv("TENCENT_HUNYUAN_API_KEY")

# 检查API密钥是否已设置
if not tencent_api_key:
    print("⚠️  请先设置腾讯云API密钥：")
    print("方式一：创建.env文件并添加：")
    print("TENCENT_HUNYUAN_API_KEY=\"your-actual-api-key\"")
    print("方式二：设置环境变量：")
    print("export TENCENT_HUNYUAN_API_KEY=\"your-actual-api-key\"")
    print("然后重新运行此脚本。")
    exit(1)
else:
    print(f"✅ API密钥已设置")

# 创建腾讯云混元大模型客户端
agent = OpenAIChatClient(
    model_id=TENCENT_HUNYUAN_MODEL,
    api_key=tencent_api_key,
    base_url=TENCENT_HUNYUAN_BASE_URL
).as_agent(
    name="WeatherAgent", instructions="You are a helpful weather agent.", tools=get_weather
)

if __name__ == "__main__":
    print("🚀 正在使用腾讯云混元大模型...")
    result = asyncio.run(agent.run("What's the weather like in Seattle?"))
    print(f"📝 结果：{result}")
