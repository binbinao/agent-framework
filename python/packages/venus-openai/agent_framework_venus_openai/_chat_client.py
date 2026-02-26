# Copyright (c) Microsoft. All rights reserved.

"""Venus OpenAI 兼容接口集成。

基于 OpenAI Compatible API，通过继承 OpenAIChatClient 实现对 Venus 服务的无缝集成。

使用方式：
    仅需替换 base_url 和 api_key 即可将应用从 OpenAI 切换到 Venus，
    无需对应用做额外修改。

API 端点：
    base_url: http://v2.open.venus.oa.com/llmproxy
    完整请求路径: http://v2.open.venus.oa.com/llmproxy/v1/chat/completions
"""

import sys
from collections.abc import Mapping, Sequence
from typing import ClassVar, Generic, TypedDict

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
    "VenusOpenAIChatClient",
    "VenusOpenAIChatOptions",
    "VenusOpenAISettings",
]

TResponseModel = TypeVar("TResponseModel", bound=BaseModel | None, default=None)

VENUS_OPENAI_DEFAULT_BASE_URL = "http://v2.open.venus.oa.com/llmproxy"
"""Venus OpenAI 兼容接口的默认 base_url。"""

VENUS_OPENAI_DEFAULT_MODEL = "deepseek-v3.2"
"""Venus 默认模型名称。"""

logger = get_logger("agent_framework.venus_openai")


class VenusOpenAIChatOptions(OpenAIChatOptions[TResponseModel], Generic[TResponseModel], total=False):
    """Venus OpenAI 兼容接口的聊天选项。

    继承自 OpenAIChatOptions，所有 OpenAI 标准参数均可使用。
    Venus 兼容接口完全遵循 OpenAI API 规范，因此无需额外选项。

    可用模型（部分列表）：
        - deepseek-v3.2: DeepSeek V3.2 模型（默认）
        - deepseek-v3.1-terminus: DeepSeek V3.1 Terminus
        - deepseek-ocr: DeepSeek OCR 模型
        - glm-4.6-fp8: GLM 4.6 FP8
        - glm-4.7: GLM 4.7
        - glm-5: GLM 5
        - hunyuan-turbo: 混元 Turbo
        - hunyuan-turbos-latest: 混元 Turbos 最新版
        - hunyuan-turbos-vision-latest: 混元 Turbos Vision 最新版
        - kimi-k2.5: Kimi K2.5
        - minimax-m2.5: Minimax M2.5
        - qwen3-235b-a22b-2507-fp8: Qwen3 235B
        - qwen3-235b-a22b-thinking-2507-fp8: Qwen3 235B Thinking
    """


class VenusOpenAISettings(AFBaseSettings):
    """Venus OpenAI 兼容接口的环境配置。

    支持通过环境变量（前缀 VENUS_OPENAI_）或 .env 文件配置：
        - VENUS_OPENAI_API_KEY: API 密钥（必填）
        - VENUS_OPENAI_BASE_URL: API 端点（可选，默认为 Venus 端点）
        - VENUS_OPENAI_MODEL_ID: 模型名称（可选，默认为 deepseek-v3.2）
    """

    env_prefix: ClassVar[str] = "VENUS_OPENAI_"

    api_key: SecretStr | None = None
    base_url: str | None = None
    model_id: str | None = None


TVenusOpenAIChatOptions = TypeVar(
    "TVenusOpenAIChatOptions",
    bound=TypedDict,  # type: ignore[valid-type]
    default="VenusOpenAIChatOptions",
    covariant=True,
)


class VenusOpenAIChatClient(OpenAIChatClient[TVenusOpenAIChatOptions]):
    """Venus OpenAI 兼容接口客户端。

    基于 OpenAIChatClient 构建，预设了 Venus 的 API 端点和默认模型。
    完全兼容 OpenAI API 规范，支持所有 OpenAI SDK 功能。

    特性：
        - 自动配置 Venus API 端点
        - 支持 VENUS_OPENAI_ 前缀的环境变量
        - 完全兼容 OpenAI 的工具调用、流式输出等功能
        - 支持 Venus 全系列模型
    """

    OTEL_PROVIDER_NAME: ClassVar[str] = "venus_openai"

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
        """初始化 Venus OpenAI 兼容客户端。"""
        try:
            venus_settings = VenusOpenAISettings(
                api_key=api_key,  # type: ignore[arg-type]
                base_url=base_url,
                model_id=model_id,
                env_file_path=env_file_path,
                env_file_encoding=env_file_encoding,
            )
        except ValidationError as ex:
            raise ServiceInitializationError("Failed to create Venus OpenAI settings.", ex) from ex

        resolved_api_key = api_key or venus_settings.api_key
        resolved_base_url = base_url or venus_settings.base_url or VENUS_OPENAI_DEFAULT_BASE_URL
        resolved_model_id = model_id or venus_settings.model_id or VENUS_OPENAI_DEFAULT_MODEL

        if not resolved_api_key and not async_client:
            raise ServiceInitializationError(
                "Venus API key is required. Set via 'api_key' parameter or 'VENUS_OPENAI_API_KEY' environment variable."
            )

        logger.info(
            "Initializing Venus OpenAI client with model '%s' at '%s'",
            resolved_model_id,
            resolved_base_url,
        )

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
