# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework_venus_openai import VenusOpenAIChatClient


async def main():
    client = VenusOpenAIChatClient()
    agent = client.as_agent(
        name="VenusAgent",
        instructions="你是一个有帮助的AI助手。",
    )
    result = await agent.run("你好！")
    print(result.text)


asyncio.run(main())
