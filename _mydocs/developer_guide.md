# Microsoft Agent Framework 二次开发指南

> 📅 最后更新：2026年2月26日
>
> 本文档面向希望对 Microsoft Agent Framework 进行扩展、定制或贡献代码的开发者。涵盖架构设计、扩展机制、开发流程和贡献指南。

---

## 📑 目录

1. [开发环境搭建](#1-开发环境搭建)
2. [项目架构深度剖析](#2-项目架构深度剖析)
3. [核心模块源码解析](#3-核心模块源码解析)
4. [扩展机制详解](#4-扩展机制详解)
5. [自定义ChatClient实现](#5-自定义chatclient实现)
6. [自定义中间件开发](#6-自定义中间件开发)
7. [自定义编排模式](#7-自定义编排模式)
8. [自定义存储后端](#8-自定义存储后端)
9. [测试框架与规范](#9-测试框架与规范)
10. [代码质量与规范](#10-代码质量与规范)
11. [包管理与发布](#11-包管理与发布)
12. [贡献流程](#12-贡献流程)
13. [架构决策记录](#13-架构决策记录)
14. [常见开发问题](#14-常见开发问题)

---

## 1. 开发环境搭建

### 1.1 系统要求

- **Python**: 3.10, 3.11, 3.12, 3.13
- **操作系统**: Windows, macOS, Linux, WSL
- **工具**:
  - [uv](https://github.com/astral-sh/uv) - Python包管理器
  - Git
  - VSCode（推荐）

### 1.2 完整开发环境设置

```bash
# 1. 克隆仓库
git clone https://github.com/microsoft/agent-framework.git
cd agent-framework/python

# 2. 安装uv（macOS/Linux）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 安装Python多版本（用于测试兼容性）
uv python install 3.10 3.11 3.12 3.13

# 4. 创建开发虚拟环境
uv venv --python 3.11

# 5. 安装所有依赖（包括开发依赖）
uv sync --all-packages --all-extras --dev

# 6. 安装pre-commit钩子
uv run poe pre-commit-install

# 7. 验证环境
uv run poe check
```

### 1.3 WSL用户注意事项

```bash
# 确保项目在WSL文件系统中（不要在/mnt/c/下）
cd ~/workspace
git clone https://github.com/microsoft/agent-framework.git

# 安装WSL扩展
# 在VSCode中安装：Remote - WSL
```

### 1.4 IDE配置（VSCode）

**推荐扩展**:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Git Graph (mhutchie.git-graph)

**配置文件** `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
```

---

## 2. 项目架构深度剖析

### 2.1 Monorepo 结构

Agent Framework 采用 Python workspace（monorepo）模式：

```
python/
├── pyproject.toml           # Workspace 根配置
├── packages/                # 所有子包
│   ├── core/               # 核心包
│   │   ├── pyproject.toml  # 包配置
│   │   ├── agent_framework/
│   │   └── tests/
│   ├── azure-ai/           # Azure AI 集成
│   ├── anthropic/          # Anthropic 集成
│   └── ...
├── samples/                # 示例代码
└── tests/                  # 集成测试
```

**包依赖关系**:

```mermaid
graph TD
    CORE[core<br/>agent-framework-core]
    CORE --> AZURE[azure-ai<br/>agent-framework-azure-ai]
    CORE --> ANTHROPIC[anthropic<br/>agent-framework-anthropic]
    CORE --> ORC[orchestrations<br/>agent-framework-orchestrations]
    CORE --> DT[durabletask<br/>agent-framework-durabletask]
    CORE --> OTHER[...其他扩展包...]
    
    style CORE fill:#4CAF50,color:white
    style AZURE fill:#2196F3,color:white
    style ANTHROPIC fill:#FF9800,color:white
    style ORC fill:#9C27B0,color:white
    style DT fill:#F44336,color:white
```

### 2.2 核心包内部结构

```python
agent_framework/  # 包名
├── __init__.py              # 导出公共API
├── _agents/                 # Agent实现（私有）
│   ├── chat_agent.py
│   ├── agent_response.py
│   └── __init__.py
├── _clients/                # ChatClient抽象（私有）
│   ├── chat_client_base.py
│   └── __init__.py
├── _tools/                  # 工具系统（私有）
│   ├── function_tool.py
│   ├── tool_decorator.py
│   └── __init__.py
├── _types/                  # 类型定义（私有）
│   ├── chat_message.py
│   ├── role.py
│   └── __init__.py
├── _threads/                # 会话管理（私有）
├── _middleware/             # 中间件系统（私有）
├── _telemetry/              # 可观测性（私有）
├── openai/                  # OpenAI 集成（公开）
│   ├── openai_chat_client.py
│   └── __init__.py
└── azure/                   # Azure OpenAI 集成（公开）
    ├── azure_openai_chat_client.py
    └── __init__.py
```

**命名约定**:
- `_xxx/` - 私有模块，不应直接导入
- `xxx/` - 公开模块，可以导入
- `packages/core/agent_framework/` 通过 `__init__.py` 控制导出

### 2.3 懒加载机制

为了避免循环依赖和加快启动速度，Provider模块使用懒加载：

```python
# agent_framework/__init__.py

def __getattr__(name: str):
    """懒加载Provider模块"""
    if name == "OpenAIChatClient":
        from agent_framework.openai import OpenAIChatClient
        return OpenAIChatClient
    
    if name == "AzureOpenAIChatClient":
        from agent_framework.azure import AzureOpenAIChatClient
        return AzureOpenAIChatClient
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

### 2.4 抽象层次设计

```python
# 抽象基类层（定义契约）
class ChatClientBase(ABC):
    @abstractmethod
    async def get_response(self, messages: list[ChatMessage]) -> ChatClientResponse:
        """获取LLM响应"""
        pass

# 具体实现层（实现契约）
class OpenAIChatClient(ChatClientBase):
    async def get_response(self, messages: list[ChatMessage]) -> ChatClientResponse:
        # 调用OpenAI API
        response = await self._client.chat.completions.create(...)
        return self._parse_response(response)

# 便捷方法层（提供易用API）
class OpenAIChatClient:
    def as_agent(self, name: str = None, instructions: str = None, **kwargs) -> ChatAgent:
        """快捷创建Agent"""
        return ChatAgent(chat_client=self, name=name, instructions=instructions, **kwargs)
```

---

## 3. 核心模块源码解析

### 3.1 ChatAgent 实现

```python
# agent_framework/_agents/chat_agent.py

class ChatAgent:
    def __init__(
        self,
        chat_client: ChatClientBase,
        name: str | None = None,
        instructions: str | None = None,
        tools: list[Callable] | None = None,
        middleware: list[Middleware] | None = None,
        message_store: ChatMessageStore | None = None,
        context_providers: list[ContextProvider] | None = None,
    ):
        self.chat_client = chat_client
        self.name = name or "Agent"
        self.instructions = instructions
        self.tools = self._prepare_tools(tools)
        self.middleware = self._build_middleware_pipeline(middleware)
        self.message_store = message_store or InMemoryChatMessageStore()
        self.context_providers = context_providers or []
    
    async def run(
        self,
        message: str,
        thread: Thread | None = None,
        metadata: dict | None = None
    ) -> str:
        """执行Agent"""
        # 1. 获取或创建Thread
        thread = thread or await self.create_thread()
        
        # 2. 添加用户消息
        user_message = ChatMessage("user", [message])
        await self.message_store.add_messages(thread.id, [user_message])
        
        # 3. 构建请求上下文
        context = RunContext(
            agent=self,
            thread=thread,
            messages=await self._build_messages(thread),
            metadata=metadata or {}
        )
        
        # 4. 执行中间件管道
        response = await self.middleware(context)
        
        # 5. 保存响应消息
        await self.message_store.add_messages(thread.id, response.messages)
        
        # 6. 返回结果
        return response.messages[0].text
    
    async def _build_messages(self, thread: Thread) -> list[ChatMessage]:
        """构建消息列表"""
        messages = []
        
        # 系统指令
        if self.instructions:
            messages.append(ChatMessage("system", [self.instructions]))
        
        # 上下文提供者
        for provider in self.context_providers:
            context = await provider.get_context(thread.id)
            messages.append(ChatMessage("system", [context]))
        
        # 历史消息
        history = await self.message_store.get_messages(thread.id)
        messages.extend(history)
        
        return messages
    
    def _build_middleware_pipeline(self, middleware: list[Middleware]) -> Middleware:
        """构建中间件管道"""
        # 默认中间件
        pipeline = [
            ToolExecutionMiddleware(self.tools),
            ChatClientMiddleware(self.chat_client),
        ]
        
        # 用户自定义中间件
        if middleware:
            pipeline = middleware + pipeline
        
        # 组装管道
        return self._chain_middleware(pipeline)
    
    def _chain_middleware(self, middleware_list: list[Middleware]) -> Middleware:
        """链接中间件"""
        async def pipeline(context: RunContext):
            index = 0
            
            async def next_handler(ctx):
                nonlocal index
                if index >= len(middleware_list):
                    raise RuntimeError("中间件管道结束")
                
                current = middleware_list[index]
                index += 1
                return await current(ctx, next_handler)
            
            return await next_handler(context)
        
        return pipeline
```

### 3.2 Tool 装饰器实现

```python
# agent_framework/_tools/tool_decorator.py

def tool(
    approval_mode: Literal["always_require", "never_require"] = "always_require",
    max_invocations: int | None = None,
    max_invocation_exceptions: int | None = None
):
    """工具装饰器"""
    def decorator(func: Callable):
        # 1. 提取函数签名
        signature = inspect.signature(func)
        
        # 2. 生成JSON Schema
        schema = {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        for param_name, param in signature.parameters.items():
            # 提取参数类型和描述
            param_type = param.annotation
            description = _extract_description(param)
            
            schema["parameters"]["properties"][param_name] = {
                "type": _python_type_to_json_type(param_type),
                "description": description
            }
            
            if param.default == inspect.Parameter.empty:
                schema["parameters"]["required"].append(param_name)
        
        # 3. 创建FunctionTool对象
        tool_obj = FunctionTool(
            func=func,
            schema=schema,
            approval_mode=approval_mode,
            max_invocations=max_invocations,
            max_invocation_exceptions=max_invocation_exceptions
        )
        
        # 4. 附加元数据到函数对象
        func._tool_metadata = tool_obj
        
        return func
    
    return decorator
```

### 3.3 中间件执行流程

```python
# agent_framework/_middleware/middleware.py

class MiddlewareBase:
    """中间件基类"""
    async def __call__(
        self,
        context: RunContext,
        next_handler: Callable[[RunContext], Awaitable[AgentResponse]]
    ) -> AgentResponse:
        raise NotImplementedError

class ToolExecutionMiddleware(MiddlewareBase):
    """工具执行中间件"""
    def __init__(self, tools: list[FunctionTool]):
        self.tools = {t.name: t for t in tools}
    
    async def __call__(self, context, next_handler):
        # 递归执行，直到没有工具调用
        max_iterations = 10
        
        for _ in range(max_iterations):
            # 调用下一个中间件（ChatClient）
            response = await next_handler(context)
            
            # 检查是否有工具调用
            if not response.tool_calls:
                return response
            
            # 执行工具
            tool_results = []
            for tool_call in response.tool_calls:
                tool = self.tools[tool_call.name]
                
                # 检查是否需要审批
                if tool.approval_mode == "always_require":
                    approved = await self._request_approval(tool_call)
                    if not approved:
                        tool_results.append(ToolResult(
                            tool_call_id=tool_call.id,
                            content="用户拒绝执行"
                        ))
                        continue
                
                # 执行工具
                try:
                    result = await tool.func(**tool_call.arguments)
                    tool_results.append(ToolResult(
                        tool_call_id=tool_call.id,
                        content=str(result)
                    ))
                except Exception as e:
                    tool_results.append(ToolResult(
                        tool_call_id=tool_call.id,
                        content=f"错误: {str(e)}",
                        is_error=True
                    ))
            
            # 将工具结果添加到上下文
            context.messages.append(response.messages[0])  # Assistant消息
            context.messages.extend([
                ChatMessage("tool", [tr.content], tool_call_id=tr.tool_call_id)
                for tr in tool_results
            ])
        
        raise RuntimeError("工具调用次数超过限制")
```

---

## 4. 扩展机制详解

### 4.1 插件架构

Agent Framework 使用插件模式，每个Provider都是独立的包：

```python
# 创建新包的标准结构
packages/my-provider/
├── pyproject.toml
├── agent_framework_my_provider/
│   ├── __init__.py
│   ├── my_chat_client.py
│   └── py.typed
└── tests/
    └── test_my_chat_client.py
```

**pyproject.toml**:
```toml
[project]
name = "agent-framework-my-provider"
version = "0.1.0"
dependencies = [
    "agent-framework-core>=0.1.0",
    "my-provider-sdk>=1.0.0"
]

[tool.uv.workspace]
# 声明为workspace成员
```

### 4.2 公共API导出

所有子包必须通过 `__init__.py` 控制导出：

```python
# agent_framework_my_provider/__init__.py

# 导出公共类
from agent_framework_my_provider.my_chat_client import MyChatClient

# 定义__all__控制导入
__all__ = ["MyChatClient"]
```

### 4.3 懒加载集成到核心包

在 `core` 包中添加懒加载：

```python
# agent_framework/__init__.py

def __getattr__(name: str):
    if name == "MyChatClient":
        from agent_framework_my_provider import MyChatClient
        return MyChatClient
    
    # ... 其他Provider
```

---

## 5. 自定义ChatClient实现

### 5.1 最小实现

```python
from agent_framework import ChatClientBase, ChatMessage, ChatClientResponse

class MyCustomChatClient(ChatClientBase):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def get_response(
        self,
        messages: list[ChatMessage],
        **kwargs
    ) -> ChatClientResponse:
        """实现核心方法：获取LLM响应"""
        
        # 1. 转换消息格式
        api_messages = self._convert_messages(messages)
        
        # 2. 调用API
        response = await self._call_api(api_messages)
        
        # 3. 解析响应
        return self._parse_response(response)
    
    def _convert_messages(self, messages: list[ChatMessage]) -> list[dict]:
        """转换为API格式"""
        return [
            {
                "role": msg.role,
                "content": msg.text
            }
            for msg in messages
        ]
    
    async def _call_api(self, messages: list[dict]) -> dict:
        """调用API（异步）"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "messages": messages,
                    "model": "my-model"
                }
            ) as resp:
                return await resp.json()
    
    def _parse_response(self, response: dict) -> ChatClientResponse:
        """解析API响应"""
        content = response["choices"][0]["message"]["content"]
        
        return ChatClientResponse(
            messages=[ChatMessage("assistant", [content])]
        )
```

### 5.2 支持工具调用

```python
class MyCustomChatClient(ChatClientBase):
    async def get_response(self, messages: list[ChatMessage], tools: list[FunctionTool] | None = None, **kwargs):
        # 1. 构建工具定义
        api_tools = None
        if tools:
            api_tools = [self._convert_tool(t) for t in tools]
        
        # 2. 调用API
        response = await self._call_api(messages, tools=api_tools)
        
        # 3. 解析工具调用
        if "tool_calls" in response["choices"][0]["message"]:
            tool_calls = [
                ToolCall(
                    id=tc["id"],
                    name=tc["function"]["name"],
                    arguments=json.loads(tc["function"]["arguments"])
                )
                for tc in response["choices"][0]["message"]["tool_calls"]
            ]
            
            return ChatClientResponse(
                messages=[ChatMessage("assistant", [], tool_calls=tool_calls)],
                tool_calls=tool_calls
            )
        
        # 4. 普通响应
        content = response["choices"][0]["message"]["content"]
        return ChatClientResponse(
            messages=[ChatMessage("assistant", [content])]
        )
    
    def _convert_tool(self, tool: FunctionTool) -> dict:
        """转换工具定义为API格式"""
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.schema["parameters"]
            }
        }
```

### 5.3 支持流式响应

```python
class MyCustomChatClient(ChatClientBase):
    async def get_streaming_response(
        self,
        messages: list[ChatMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """流式响应"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "messages": self._convert_messages(messages),
                    "stream": True
                }
            ) as resp:
                async for line in resp.content:
                    if line.startswith(b"data: "):
                        data = json.loads(line[6:])
                        if "choices" in data:
                            delta = data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
```

---

## 6. 自定义中间件开发

### 6.1 函数式中间件

```python
async def my_middleware(context, next_handler):
    """最简单的中间件"""
    # 前置处理
    print(f"请求: {context.messages[-1].text}")
    
    # 调用下一个中间件
    response = await next_handler(context)
    
    # 后置处理
    print(f"响应: {response.messages[0].text}")
    
    return response
```

### 6.2 类式中间件

```python
from agent_framework import MiddlewareBase

class LoggingMiddleware(MiddlewareBase):
    def __init__(self, logger):
        self.logger = logger
    
    async def __call__(self, context, next_handler):
        request_id = str(uuid.uuid4())
        
        self.logger.info(f"[{request_id}] 请求开始", extra={
            "agent_name": context.agent.name,
            "user_id": context.metadata.get("user_id"),
            "message": context.messages[-1].text[:100]
        })
        
        try:
            response = await next_handler(context)
            self.logger.info(f"[{request_id}] 请求成功")
            return response
        except Exception as e:
            self.logger.error(f"[{request_id}] 请求失败: {str(e)}")
            raise
```

### 6.3 装饰器中间件

```python
from functools import wraps

def timing_middleware():
    """计时中间件装饰器"""
    def decorator(middleware):
        @wraps(middleware)
        async def wrapper(context, next_handler):
            start = time.time()
            response = await middleware(context, next_handler)
            duration = time.time() - start
            
            print(f"耗时: {duration:.2f}s")
            return response
        return wrapper
    return decorator

# 使用
@timing_middleware()
async def my_middleware(context, next_handler):
    return await next_handler(context)
```

---

## 7. 自定义编排模式

### 7.1 创建自定义编排

```python
from agent_framework_orchestrations import Orchestration

class RoundRobinOrchestration(Orchestration):
    """轮询编排：每个Agent轮流处理"""
    
    def __init__(self, agents: list[ChatAgent]):
        self.agents = agents
        self.current_index = 0
    
    async def run(self, initial_message: str) -> str:
        responses = []
        
        # 每个Agent处理一次
        for agent in self.agents:
            result = await agent.run(initial_message)
            responses.append(f"{agent.name}: {result}")
        
        return "\n\n".join(responses)

# 使用
orchestration = RoundRobinOrchestration([agent1, agent2, agent3])
result = await orchestration.run("分析这个问题")
```

### 7.2 实现Builder模式

```python
class RoundRobinBuilder:
    def __init__(self):
        self._agents = []
    
    def participants(self, agents: list[ChatAgent]) -> "RoundRobinBuilder":
        self._agents = agents
        return self
    
    def build(self) -> RoundRobinOrchestration:
        if not self._agents:
            raise ValueError("至少需要一个Agent")
        return RoundRobinOrchestration(self._agents)

# 使用
orchestration = RoundRobinBuilder() \
    .participants([agent1, agent2, agent3]) \
    .build()
```

---

## 8. 自定义存储后端

### 8.1 实现ChatMessageStore

```python
from agent_framework import ChatMessageStore, ChatMessage

class PostgreSQLMessageStore(ChatMessageStore):
    """PostgreSQL消息存储"""
    
    def __init__(self, connection_string: str):
        self.conn_string = connection_string
        self._pool = None
    
    async def initialize(self):
        """初始化连接池"""
        import asyncpg
        self._pool = await asyncpg.create_pool(self.conn_string)
        
        # 创建表
        async with self._pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    thread_id VARCHAR(255),
                    role VARCHAR(50),
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    async def add_messages(self, thread_id: str, messages: list[ChatMessage]):
        """添加消息"""
        async with self._pool.acquire() as conn:
            for msg in messages:
                await conn.execute(
                    'INSERT INTO chat_messages (thread_id, role, content) VALUES ($1, $2, $3)',
                    thread_id, msg.role, msg.text
                )
    
    async def get_messages(
        self,
        thread_id: str,
        limit: int | None = None
    ) -> list[ChatMessage]:
        """获取消息"""
        query = 'SELECT role, content FROM chat_messages WHERE thread_id = $1 ORDER BY created_at'
        if limit:
            query += f' LIMIT {limit}'
        
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, thread_id)
            return [ChatMessage(row['role'], [row['content']]) for row in rows]
    
    async def delete_thread(self, thread_id: str):
        """删除线程"""
        async with self._pool.acquire() as conn:
            await conn.execute('DELETE FROM chat_messages WHERE thread_id = $1', thread_id)

# 使用
store = PostgreSQLMessageStore("postgresql://user:pass@localhost/db")
await store.initialize()

agent = ChatAgent(
    chat_client=client,
    message_store=store
)
```

### 8.2 实现CheckpointStore

```python
from agent_framework_durabletask import CheckpointStore

class S3CheckpointStore(CheckpointStore):
    """S3检查点存储"""
    
    def __init__(self, bucket_name: str, aws_access_key: str, aws_secret_key: str):
        import boto3
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        self.bucket = bucket_name
    
    async def save_checkpoint(self, checkpoint_id: str, data: dict):
        """保存检查点"""
        import json
        self.s3.put_object(
            Bucket=self.bucket,
            Key=f"checkpoints/{checkpoint_id}.json",
            Body=json.dumps(data)
        )
    
    async def load_checkpoint(self, checkpoint_id: str) -> dict:
        """加载检查点"""
        import json
        response = self.s3.get_object(
            Bucket=self.bucket,
            Key=f"checkpoints/{checkpoint_id}.json"
        )
        return json.loads(response['Body'].read())
```

---

## 9. 测试框架与规范

### 9.1 单元测试

```python
# tests/test_my_feature.py

import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_basic():
    """测试基础Agent功能"""
    # 创建Mock ChatClient
    mock_client = AsyncMock()
    mock_client.get_response.return_value = ChatClientResponse(
        messages=[ChatMessage("assistant", ["Hello"])]
    )
    
    # 创建Agent
    agent = ChatAgent(chat_client=mock_client)
    
    # 执行测试
    result = await agent.run("Hi")
    
    # 断言
    assert result == "Hello"
    mock_client.get_response.assert_called_once()

@pytest.mark.asyncio
async def test_tool_execution():
    """测试工具执行"""
    @tool(approval_mode="never_require")
    def add(a: int, b: int) -> int:
        return a + b
    
    mock_client = AsyncMock()
    # 第一次返回工具调用
    mock_client.get_response.side_effect = [
        ChatClientResponse(
            messages=[ChatMessage("assistant", [], tool_calls=[
                ToolCall(id="1", name="add", arguments={"a": 1, "b": 2})
            ])],
            tool_calls=[ToolCall(id="1", name="add", arguments={"a": 1, "b": 2})]
        ),
        # 第二次返回最终结果
        ChatClientResponse(
            messages=[ChatMessage("assistant", ["结果是3"])]
        )
    ]
    
    agent = ChatAgent(chat_client=mock_client, tools=[add])
    result = await agent.run("计算1+2")
    
    assert "3" in result
```

### 9.2 集成测试

```python
@pytest.mark.asyncio
@pytest.mark.integration  # 标记为集成测试
async def test_openai_integration():
    """测试与OpenAI的集成"""
    import os
    
    # 检查环境变量
    if not os.getenv("RUN_INTEGRATION_TESTS"):
        pytest.skip("集成测试未启用")
    
    # 使用真实的OpenAI Client
    client = OpenAIChatClient()
    agent = client.as_agent()
    
    result = await agent.run("1+1等于几？")
    assert "2" in result
```

### 9.3 测试覆盖率

```bash
# 运行测试并生成覆盖率报告
uv run poe test

# 查看覆盖率报告
# 报告会显示在终端，也会生成HTML报告在htmlcov/目录

# 单个包的测试
uv run --directory packages/core poe test
```

---

## 10. 代码质量与规范

### 10.1 编码规范

**必须遵守的规则**:

1. **Copyright**: 所有 `.py` 文件顶部必须包含：
```python
# Copyright (c) Microsoft. All rights reserved.
```

2. **类型注解**: 所有公共函数必须有类型注解
```python
# ✅ 正确
async def my_function(name: str, age: int) -> str:
    return f"{name} is {age} years old"

# ❌ 错误
async def my_function(name, age):
    return f"{name} is {age} years old"
```

3. **使用 Type | None 而不是 Optional**:
```python
# ✅ 正确
def foo(x: str | None = None) -> int | None:
    pass

# ❌ 错误
from typing import Optional
def foo(x: Optional[str] = None) -> Optional[int]:
    pass
```

4. **日志**: 使用框架的logger
```python
# ✅ 正确
from agent_framework import get_logger
logger = get_logger(__name__)

# ❌ 错误
import logging
logger = logging.getLogger(__name__)
```

5. **Docstring**: 使用Google风格
```python
def my_function(param1: str, param2: int) -> bool:
    """函数简短描述。
    
    详细描述（可选）。
    
    Args:
        param1: 参数1的描述
        param2: 参数2的描述
    
    Returns:
        返回值的描述
    
    Raises:
        ValueError: 何时抛出此异常
    """
    pass
```

### 10.2 代码质量检查

```bash
# 格式化代码
uv run poe fmt

# Lint检查
uv run poe lint

# 类型检查
uv run poe typing

# 运行所有检查
uv run poe check
```

### 10.3 Pre-commit Hooks

安装后，每次commit会自动运行检查：

```bash
uv run poe pre-commit-install

# 手动运行所有hooks
uv run pre-commit run -a
```

配置文件 `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

---

## 11. 包管理与发布

### 11.1 构建包

```bash
# 构建所有包
uv run poe build

# 构建特定包
uv run --directory packages/core poe build
```

### 11.2 版本管理

版本号遵循语义化版本（Semantic Versioning）：

```
MAJOR.MINOR.PATCH[-PRERELEASE]

例如：
0.1.0 - 初始版本
0.1.1 - Bug修复
0.2.0 - 新功能
1.0.0 - 稳定版本
1.0.0-beta.1 - 预发布版本
```

**更新版本**:
```toml
# pyproject.toml
[project]
version = "0.2.0"  # 更新版本号
```

### 11.3 发布到PyPI

```bash
# 1. 清理旧的构建
uv run poe clean-dist

# 2. 构建包
uv run poe build

# 3. 发布到PyPI（需要凭证）
uv run poe publish
```

---

## 12. 贡献流程

### 12.1 Fork和克隆

```bash
# 1. Fork仓库（在GitHub上点击Fork）

# 2. 克隆你的Fork
git clone https://github.com/YOUR_USERNAME/agent-framework.git
cd agent-framework

# 3. 添加上游仓库
git remote add upstream https://github.com/microsoft/agent-framework.git

# 4. 获取上游更新
git fetch upstream
```

### 12.2 创建Feature分支

```bash
# 从main创建新分支
git checkout -b feature/my-new-feature

# 或者修复bug
git checkout -b fix/issue-123
```

### 12.3 开发和提交

```bash
# 1. 进行修改...

# 2. 添加变更
git add .

# 3. 提交（pre-commit hooks会自动运行）
git commit -m "feat: add new feature"

# 提交消息规范：
# feat: 新功能
# fix: Bug修复
# docs: 文档更新
# test: 测试相关
# refactor: 重构
# chore: 构建/工具相关
```

### 12.4 推送和创建PR

```bash
# 推送到你的Fork
git push origin feature/my-new-feature

# 在GitHub上创建Pull Request
# 目标分支：microsoft/agent-framework:main
# 源分支：YOUR_USERNAME/agent-framework:feature/my-new-feature
```

### 12.5 PR检查清单

提交PR前确保：

- [ ] 代码通过所有质量检查（`uv run poe check`）
- [ ] 添加了单元测试
- [ ] 更新了相关文档
- [ ] 遵循编码规范
- [ ] 提交消息清晰明确
- [ ] 签署了CLA（首次贡献）

---

## 13. 架构决策记录

项目在 `docs/decisions/` 目录维护架构决策记录（ADR）：

| ADR | 主题 | 关键决策 |
|-----|------|----------|
| 0001 | Agent Run Response | 统一响应格式为 `AgentResponse` |
| 0002 | Agent Tools | 采用装饰器 + JSON Schema 方式定义工具 |
| 0003 | OpenTelemetry | 内置OTel支持，零配置可观测性 |
| 0005 | Python Naming | 私有模块用 `_xxx`，公共模块不加前缀 |
| 0006 | User Approval | 工具审批通过 `approval_mode` 控制 |
| 0007 | Agent Filtering | 中间件系统设计为管道模式 |
| 0008 | Python Subpackages | 采用Monorepo + workspace模式 |
| 0009 | Long Running Ops | 通过Durable Task支持长时间运行 |

**如何提出新的ADR**:

1. 复制 `docs/decisions/0000-template.md`
2. 编号为下一个序号（如 0014）
3. 填写决策内容：
   - Context（背景）
   - Decision（决策）
   - Consequences（影响）
4. 提交PR讨论

---

## 14. 常见开发问题

### Q1: 如何调试Agent执行过程？

```python
# 方法1: 使用日志
from agent_framework import get_logger
logger = get_logger(__name__)
logger.setLevel("DEBUG")

# 方法2: 使用中间件打印上下文
async def debug_middleware(context, next_handler):
    print(f"Messages: {context.messages}")
    response = await next_handler(context)
    print(f"Response: {response}")
    return response

agent = ChatAgent(middleware=[debug_middleware])

# 方法3: 使用VSCode调试器
# 在代码中设置断点，F5启动调试
```

### Q2: 如何测试需要API密钥的代码？

```python
# 使用Mock
from unittest.mock import AsyncMock, patch

@patch('agent_framework.openai.OpenAIChatClient')
def test_with_mock(mock_client):
    mock_instance = AsyncMock()
    mock_client.return_value = mock_instance
    
    # 测试代码...
```

### Q3: 如何处理循环依赖？

```python
# 方法1: 使用TYPE_CHECKING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_framework import ChatAgent

def my_function(agent: "ChatAgent"):
    pass

# 方法2: 使用字符串类型注解
def my_function(agent: "ChatAgent") -> str:
    pass
```

### Q4: 包导入失败怎么办？

```bash
# 1. 确认虚拟环境激活
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 2. 重新同步依赖
uv sync --all-packages --dev

# 3. 检查Python解释器
which python  # 应该指向.venv/bin/python
```

### Q5: 如何贡献文档？

```bash
# 1. 文档位于多个位置：
# - python/README.md: Python包总览
# - python/packages/*/README.md: 各包文档
# - python/samples/*/README.md: 示例文档
# - docs/: 架构文档

# 2. 修改文档后提交PR
# 3. 确保示例代码可运行
```

---

## 附录

### A. 开发工具推荐

| 工具 | 用途 | 安装 |
|------|------|------|
| uv | 包管理 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| VSCode | IDE | https://code.visualstudio.com/ |
| httpie | API测试 | `pip install httpie` |
| jq | JSON处理 | `brew install jq` |
| commitizen | 提交规范 | `pip install commitizen` |

### B. 有用的命令

```bash
# 查看可用的poe任务
uv run poe

# 运行特定Python版本的测试
uv run --python 3.12 poe test

# 清理构建产物
uv run poe clean-dist

# 检查依赖更新
uv sync --upgrade

# 查看依赖树
uv tree
```

### C. 相关资源

- [项目GitHub](https://github.com/microsoft/agent-framework)
- [官方文档](https://learn.microsoft.com/agent-framework/)
- [Discord社区](https://discord.gg/b5zjErwbQM)
- [PyPI发布](https://pypi.org/project/agent-framework/)
- [问题追踪](https://github.com/microsoft/agent-framework/issues)

---

*欢迎加入 Agent Framework 开发社区！如有问题，请在Discord或GitHub Issues中提问。*
