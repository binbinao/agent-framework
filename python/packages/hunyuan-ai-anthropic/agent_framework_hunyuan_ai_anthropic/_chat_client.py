# Copyright (c) Microsoft. All rights reserved.

"""腾讯云混元大模型 Anthropic 兼容接口集成。

基于混元 Anthropic Compatible API（https://cloud.tencent.com/document/product/1729/127293），
通过继承 AnthropicClient 实现对腾讯云混元大模型的无缝集成。

使用方式：
    仅需替换 base_url 和 api_key 即可将应用从 Anthropic 切换到混元大模型，
    无需对应用做额外修改。

API 端点：
    base_url: https://api.lkeap.cloud.tencent.com/anthropic
    完整请求路径: https://api.lkeap.cloud.tencent.com/anthropic/v1/messages
"""

import sys
from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, Generic, TypedDict

from agent_framework import (
    ChatAndFunctionMiddlewareTypes,
    FunctionInvocationConfiguration,
    get_logger,
)
from agent_framework._pydantic import AFBaseSettings
from agent_framework.exceptions import ServiceInitializationError
from agent_framework_anthropic import AnthropicChatOptions, AnthropicClient
from anthropic import AsyncAnthropic
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
    "HunyuanAnthropicClient",
    "HunyuanAnthropicChatOptions",
    "HunyuanAnthropicSettings",
]

TResponseModel = TypeVar("TResponseModel", bound=BaseModel | None, default=None)

# 腾讯云混元大模型 Anthropic 兼容接口默认配置
HUNYUAN_ANTHROPIC_DEFAULT_BASE_URL = "https://api.lkeap.cloud.tencent.com/anthropic"
"""腾讯云混元 Anthropic 兼容接口的默认 base_url。"""

HUNYUAN_ANTHROPIC_DEFAULT_MODEL = "hunyuan-turbos-latest"
"""腾讯云混元 Anthropic 兼容接口默认模型名称。"""

logger = get_logger("agent_framework.hunyuan_ai_anthropic")


# region Hunyuan Anthropic Chat Options


class HunyuanAnthropicChatOptions(AnthropicChatOptions[TResponseModel], Generic[TResponseModel], total=False):
    """腾讯云混元 Anthropic 兼容接口的聊天选项。

    继承自 AnthropicChatOptions，所有 Anthropic 标准参数均可使用。

    可用模型（部分列表）：
        - hunyuan-turbos-latest: 混元最新 Turbo-S 模型
        - hunyuan-pro: 混元 Pro 模型
        - hunyuan-standard: 混元 Standard 模型
        - hunyuan-lite: 混元 Lite 模型（免费）

    参考文档：https://cloud.tencent.com/document/product/1729/127293

    Examples:
        .. code-block:: python

            from agent_framework_hunyuan_ai_anthropic import HunyuanAnthropicChatOptions

            options: HunyuanAnthropicChatOptions = {
                "temperature": 0.7,
                "max_tokens": 1024,
            }
    """


# endregion


class HunyuanAnthropicSettings(AFBaseSettings):
    """腾讯云混元 Anthropic 兼容接口的环境配置。

    支持通过环境变量（前缀 HUNYUAN_ANTHROPIC_）或 .env 文件配置：
        - HUNYUAN_ANTHROPIC_API_KEY: API 密钥（必填）
        - HUNYUAN_ANTHROPIC_BASE_URL: API 端点（可选，默认为腾讯云混元 Anthropic 端点）
        - HUNYUAN_ANTHROPIC_MODEL_ID: 模型名称（可选，默认为 hunyuan-turbos-latest）

    获取 API 密钥：https://console.cloud.tencent.com/lkeap
    """

    env_prefix: ClassVar[str] = "HUNYUAN_ANTHROPIC_"

    api_key: SecretStr | None = None
    base_url: str | None = None
    model_id: str | None = None


THunyuanAnthropicChatOptions = TypeVar(
    "THunyuanAnthropicChatOptions",
    bound=TypedDict,  # type: ignore[valid-type]
    default="HunyuanAnthropicChatOptions",
    covariant=True,
)


class HunyuanAnthropicClient(AnthropicClient[THunyuanAnthropicChatOptions]):
    """腾讯云混元大模型 Anthropic 兼容接口客户端。

    基于 AnthropicClient 构建，预设了腾讯云混元的 Anthropic 兼容 API 端点和默认模型。
    完全兼容 Anthropic Messages API 规范。

    特性：
        - 自动配置腾讯云混元 Anthropic 兼容 API 端点
        - 支持 HUNYUAN_ANTHROPIC_ 前缀的环境变量
        - 兼容 Anthropic 的消息格式、工具调用等功能
        - 支持混元全系列模型

    API 文档：https://cloud.tencent.com/document/product/1729/127293

    Examples:
        .. code-block:: python

            from agent_framework_hunyuan_ai_anthropic import HunyuanAnthropicClient

            # 使用环境变量配置（推荐）
            # 设置 HUNYUAN_ANTHROPIC_API_KEY=your-api-key
            client = HunyuanAnthropicClient()

            # 直接传参
            client = HunyuanAnthropicClient(
                api_key="your-api-key",
                model_id="hunyuan-pro",
            )

            # 创建 Agent
            agent = client.as_agent(
                name="MyAgent",
                instructions="你是一个有帮助的AI助手。",
            )
            result = await agent.run("你好！")
    """

    OTEL_PROVIDER_NAME: ClassVar[str] = "hunyuan_anthropic"

    def __init__(
        self,
        *,
        api_key: str | SecretStr | None = None,
        model_id: str | None = None,
        base_url: str | None = None,
        async_client: AsyncAnthropic | None = None,
        default_headers: Mapping[str, str] | None = None,
        middleware: Sequence[ChatAndFunctionMiddlewareTypes] | None = None,
        function_invocation_configuration: FunctionInvocationConfiguration | None = None,
        env_file_path: str | None = None,
        env_file_encoding: str | None = None,
    ) -> None:
        """初始化腾讯云混元 Anthropic 兼容客户端。

        Keyword Args:
            api_key: 腾讯云混元 API 密钥。
                可通过 HUNYUAN_ANTHROPIC_API_KEY 环境变量设置。
                获取密钥：https://console.cloud.tencent.com/lkeap
            model_id: 混元模型名称，如 hunyuan-turbos-latest、hunyuan-pro 等。
                可通过 HUNYUAN_ANTHROPIC_MODEL_ID 环境变量设置。
                默认为 hunyuan-turbos-latest。
            base_url: API 端点地址。
                可通过 HUNYUAN_ANTHROPIC_BASE_URL 环境变量设置。
                默认为 https://api.lkeap.cloud.tencent.com/anthropic。
            async_client: 可选的 AsyncAnthropic 客户端实例。
            default_headers: 默认 HTTP 请求头。
            middleware: 可选的中间件序列。
            function_invocation_configuration: 可选的函数调用配置。
            env_file_path: .env 文件路径。
            env_file_encoding: .env 文件编码。

        Raises:
            ServiceInitializationError: 当 API 密钥未提供时抛出。
        """
        # 加载混元特有的环境变量设置
        try:
            hunyuan_settings = HunyuanAnthropicSettings(
                api_key=api_key,  # type: ignore[arg-type]
                base_url=base_url,
                model_id=model_id,
                env_file_path=env_file_path,
                env_file_encoding=env_file_encoding,
            )
        except ValidationError as ex:
            raise ServiceInitializationError("Failed to create Hunyuan Anthropic settings.", ex) from ex

        # 确定最终的 API 密钥、base_url 和 model_id
        resolved_api_key = api_key or hunyuan_settings.api_key
        resolved_base_url = base_url or hunyuan_settings.base_url or HUNYUAN_ANTHROPIC_DEFAULT_BASE_URL
        resolved_model_id = model_id or hunyuan_settings.model_id or HUNYUAN_ANTHROPIC_DEFAULT_MODEL

        if not resolved_api_key and not async_client:
            raise ServiceInitializationError(
                "Hunyuan API key is required. "
                "Set via 'api_key' parameter or 'HUNYUAN_ANTHROPIC_API_KEY' environment variable. "
                "Get your API key at: https://console.cloud.tencent.com/lkeap"
            )

        logger.info(
            "Initializing Hunyuan Anthropic client with model '%s' at '%s'",
            resolved_model_id,
            resolved_base_url,
        )

        # 构建 AsyncAnthropic 客户端（如果未提供）
        if not async_client:
            api_key_value = (
                resolved_api_key.get_secret_value()
                if isinstance(resolved_api_key, SecretStr)
                else resolved_api_key
            )
            async_client = AsyncAnthropic(
                api_key=api_key_value,
                base_url=resolved_base_url,
                default_headers=dict(default_headers) if default_headers else None,
            )

        super().__init__(
            model_id=resolved_model_id,
            anthropic_client=async_client,
            middleware=middleware,
            function_invocation_configuration=function_invocation_configuration,
        )
