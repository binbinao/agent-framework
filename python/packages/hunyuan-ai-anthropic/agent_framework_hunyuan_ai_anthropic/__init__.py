# Copyright (c) Microsoft. All rights reserved.

"""腾讯云混元大模型 Anthropic 兼容接口集成。"""

import importlib.metadata

from ._chat_client import HunyuanAnthropicClient, HunyuanAnthropicChatOptions, HunyuanAnthropicSettings

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback for development mode

__all__ = [
    "HunyuanAnthropicChatOptions",
    "HunyuanAnthropicClient",
    "HunyuanAnthropicSettings",
    "__version__",
]
