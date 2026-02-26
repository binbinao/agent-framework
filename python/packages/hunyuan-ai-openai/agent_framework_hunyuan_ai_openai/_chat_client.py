# Copyright (c) Microsoft. All rights reserved.

"""腾讯云混元大模型 OpenAI 兼容接口集成。

基于混元 OpenAI Compatible API（https://cloud.tencent.com/document/product/1729/111007），
通过继承 OpenAIChatClient 实现对腾讯云混元大模型的无缝集成。

使用方式：
    仅需替换 base_url 和 api_key 即可将应用从 OpenAI 切换到混元大模型，
    无需对应用做额外修改。

API 端点：
    base_url: https://api.hunyuan.cloud.tencent.com/v1
    完整请求路径: https://api.hunyuan.cloud.tencent.com/v1/chat/completions
"""

import sys
from collections.abc import Mapping, Sequence
from typing import ClassVar, Generic

from agent_framework import (
    ChatAndFunctionMiddlewareTypes,
    FunctionInvocationConfiguration,
    get_logger,
)
from agent_framework._pydantic import AFBaseSettings
from agent_framework.exceptions import ServiceInitializationError
from agent_framework.openai import OpenAIChatClient, OpenAIChatOptions
from openai import AsyncOpenAI
from pydantic import BaseModel, SecretStr, ValidationError

if sys.version_info >= (3, 13):
    from typing import TypeVar  # type: ignore # pragma: no cover
else:
    from typing_extensions import TypeVar  # type: ignore # pragma: no cover

if sys.version_info >= (3, 11):
    from typing import TypedDict  # type: ignore # pragma: no cover
else:
    from typing_extensions import TypedDict  # type: ignore # pragma: no cover

__all__ = [
    "HunyuanOpenAIChatClient",
    "HunyuanOpenAIChatOptions",
    "HunyuanOpenAISettings",
]

TResponseModel = TypeVar("TResponseModel", bound=BaseModel | None, default=None)

# 腾讯云混元大模型 OpenAI 兼容接口默认配置
HUNYUAN_OPENAI_DEFAULT_BASE_URL = "https://api.hunyuan.cloud.tencent.com/v1"
"""腾讯云混元 OpenAI 兼容接口的默认 base_url。"""

HUNYUAN_OPENAI_DEFAULT_MODEL = "hunyuan-turbos-latest"
"""腾讯云混元默认模型名称。"""

logger = get_logger("agent_framework.hunyuan_ai_openai")


# region Hunyuan OpenAI Chat Options


class HunyuanOpenAIChatOptions(OpenAIChatOptions[TResponseModel], Generic[TResponseModel], total=False):
    """腾讯云混元 OpenAI 兼容接口的聊天选项。

    继承自 OpenAIChatOptions，所有 OpenAI 标准参数均可使用。
    混元兼容接口完全遵循 OpenAI API 规范，因此无需额外选项。

    可用模型（部分列表）：
        - hunyuan-turbos-latest: 混元最新 Turbo-S 模型
        - hunyuan-2.0-instruct-20251111: 混元 2.0 指令模型
        - hunyuan-pro: 混元 Pro 模型
        - hunyuan-standard: 混元 Standard 模型
        - hunyuan-lite: 混元 Lite 模型（免费）

    参考文档：https://cloud.tencent.com/document/product/1729/111007

    Examples:
        .. code-block:: python

            from agent_framework_hunyuan_ai_openai import HunyuanOpenAIChatOptions

            options: HunyuanOpenAIChatOptions = {
                "temperature": 0.7,
                "max_tokens": 1024,
            }
    """


# endregion


class HunyuanOpenAISettings(AFBaseSettings):
    """腾讯云混元 OpenAI 兼容接口的环境配置。

    支持通过环境变量（前缀 HUNYUAN_OPENAI_）或 .env 文件配置：
        - HUNYUAN_OPENAI_API_KEY: API 密钥（必填）
        - HUNYUAN_OPENAI_BASE_URL: API 端点（可选，默认为腾讯云混元端点）
        - HUNYUAN_OPENAI_MODEL_ID: 模型名称（可选，默认为 hunyuan-turbos-latest）

    获取 API 密钥：https://console.cloud.tencent.com/hunyuan/start
    """

    env_prefix: ClassVar[str] = "HUNYUAN_OPENAI_"

    api_key: SecretStr | None = None
    base_url: str | None = None
    model_id: str | None = None


THunyuanOpenAIChatOptions = TypeVar(
    "THunyuanOpenAIChatOptions",
    bound=TypedDict,  # type: ignore[valid-type]
    default="HunyuanOpenAIChatOptions",
    covariant=True,
)


class HunyuanOpenAIChatClient(OpenAIChatClient[THunyuanOpenAIChatOptions]):
    """腾讯云混元大模型 OpenAI 兼容接口客户端。

    基于 OpenAIChatClient 构建，预设了腾讯云混元的 API 端点和默认模型。
    完全兼容 OpenAI API 规范，支持所有 OpenAI SDK 功能。

    特性：
        - 自动配置腾讯云混元 API 端点
        - 支持 HUNYUAN_OPENAI_ 前缀的环境变量
        - 完全兼容 OpenAI 的工具调用、流式输出等功能
        - 支持混元全系列模型

    API 文档：https://cloud.tencent.com/document/product/1729/111007

    Examples:
        .. code-block:: python

            from agent_framework_hunyuan_ai_openai import HunyuanOpenAIChatClient

            # 使用环境变量配置（推荐）
            # 设置 HUNYUAN_OPENAI_API_KEY=your-api-key
            client = HunyuanOpenAIChatClient()

            # 直接传参
            client = HunyuanOpenAIChatClient(
                api_key="your-api-key",
                model_id="hunyuan-2.0-instruct-20251111",
            )

            # 创建 Agent
            agent = client.as_agent(
                name="MyAgent",
                instructions="你是一个有帮助的AI助手。",
            )
            result = await agent.run("你好！")
    """

    OTEL_PROVIDER_NAME: ClassVar[str] = "hunyuan_openai"

    def __init__(
        self,
        *,
        api_key: str | SecretStr | None = None,
        model_id: str | None = None,
        base_url: str | None = None,
        async_client: AsyncOpenAI | None = None,
        default_headers: Mapping[str, str] | None = None,
        instruction_role: str | None = None,
        middleware: Sequence[ChatAndFunctionMiddlewareTypes] | None = None,
        function_invocation_configuration: FunctionInvocationConfiguration | None = None,
        env_file_path: str | None = None,
        env_file_encoding: str | None = None,
    ) -> None:
        """初始化腾讯云混元 OpenAI 兼容客户端。

        Keyword Args:
            api_key: 腾讯云混元 API 密钥。
                可通过 HUNYUAN_OPENAI_API_KEY 环境变量设置。
                获取密钥：https://console.cloud.tencent.com/hunyuan/start
            model_id: 混元模型名称，如 hunyuan-turbos-latest、hunyuan-pro 等。
                可通过 HUNYUAN_OPENAI_MODEL_ID 环境变量设置。
                默认为 hunyuan-turbos-latest。
            base_url: API 端点地址。
                可通过 HUNYUAN_OPENAI_BASE_URL 环境变量设置。
                默认为 https://api.hunyuan.cloud.tencent.com/v1。
            async_client: 可选的 AsyncOpenAI 客户端实例。
            default_headers: 默认 HTTP 请求头。
            instruction_role: 指令消息的角色，如 "system" 或 "developer"。
            middleware: 可选的中间件序列。
            function_invocation_configuration: 可选的函数调用配置。
            env_file_path: .env 文件路径。
            env_file_encoding: .env 文件编码。

        Raises:
            ServiceInitializationError: 当 API 密钥未提供时抛出。
        """
        # 加载混元特有的环境变量设置
        try:
            hunyuan_settings = HunyuanOpenAISettings(
                api_key=api_key,  # type: ignore[arg-type]
                base_url=base_url,
                model_id=model_id,
                env_file_path=env_file_path,
                env_file_encoding=env_file_encoding,
            )
        except ValidationError as ex:
            raise ServiceInitializationError("Failed to create Hunyuan OpenAI settings.", ex) from ex

        # 确定最终的 API 密钥、base_url 和 model_id
        resolved_api_key = api_key or hunyuan_settings.api_key
        resolved_base_url = base_url or hunyuan_settings.base_url or HUNYUAN_OPENAI_DEFAULT_BASE_URL
        resolved_model_id = model_id or hunyuan_settings.model_id or HUNYUAN_OPENAI_DEFAULT_MODEL

        if not resolved_api_key and not async_client:
            raise ServiceInitializationError(
                "Hunyuan API key is required. "
                "Set via 'api_key' parameter or 'HUNYUAN_OPENAI_API_KEY' environment variable. "
                "Get your API key at: https://console.cloud.tencent.com/hunyuan/start"
            )

        logger.info(
            "Initializing Hunyuan OpenAI client with model '%s' at '%s'",
            resolved_model_id,
            resolved_base_url,
        )

        # 将 SecretStr 转换为 str
        api_key_value = (
            resolved_api_key.get_secret_value() if isinstance(resolved_api_key, SecretStr) else resolved_api_key
        )

        super().__init__(
            api_key=api_key_value,
            model_id=resolved_model_id,
            base_url=resolved_base_url,
            async_client=async_client,
            default_headers=default_headers,
            instruction_role=instruction_role,
            middleware=middleware,
            function_invocation_configuration=function_invocation_configuration,
        )
