# Copyright (c) Microsoft. All rights reserved.

"""腾讯云混元 Anthropic 兼容客户端单元测试。"""

import os
from unittest.mock import patch

import pytest
from agent_framework.exceptions import ServiceInitializationError

from agent_framework_hunyuan_ai_anthropic import HunyuanAnthropicClient, HunyuanAnthropicSettings


class TestHunyuanAnthropicSettings:
    """测试 HunyuanAnthropicSettings 环境变量加载。"""

    def test_default_settings(self) -> None:
        """测试默认设置（无环境变量时应为 None）。"""
        with patch.dict(os.environ, {}, clear=True):
            settings = HunyuanAnthropicSettings()
            assert settings.api_key is None
            assert settings.base_url is None
            assert settings.model_id is None

    def test_settings_from_env(self) -> None:
        """测试从环境变量加载设置。"""
        with patch.dict(
            os.environ,
            {
                "HUNYUAN_ANTHROPIC_API_KEY": "test-api-key",
                "HUNYUAN_ANTHROPIC_BASE_URL": "https://custom.endpoint.com/anthropic",
                "HUNYUAN_ANTHROPIC_MODEL_ID": "hunyuan-pro",
            },
        ):
            settings = HunyuanAnthropicSettings()
            assert settings.api_key is not None
            assert settings.api_key.get_secret_value() == "test-api-key"
            assert settings.base_url == "https://custom.endpoint.com/anthropic"
            assert settings.model_id == "hunyuan-pro"


class TestHunyuanAnthropicClient:
    """测试 HunyuanAnthropicClient 初始化。"""

    def test_init_without_api_key_raises(self) -> None:
        """测试缺少 API 密钥时应抛出 ServiceInitializationError。"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ServiceInitializationError, match="Hunyuan API key is required"):
                HunyuanAnthropicClient()

    def test_init_with_api_key(self) -> None:
        """测试使用 API 密钥初始化。"""
        client = HunyuanAnthropicClient(api_key="test-api-key")
        assert client is not None

    def test_init_with_custom_model(self) -> None:
        """测试使用自定义模型名称初始化。"""
        client = HunyuanAnthropicClient(
            api_key="test-api-key",
            model_id="hunyuan-pro",
        )
        assert client is not None

    def test_init_with_env_vars(self) -> None:
        """测试从环境变量初始化。"""
        with patch.dict(
            os.environ,
            {
                "HUNYUAN_ANTHROPIC_API_KEY": "env-api-key",
                "HUNYUAN_ANTHROPIC_MODEL_ID": "hunyuan-standard",
            },
        ):
            client = HunyuanAnthropicClient()
            assert client is not None

    def test_as_agent(self) -> None:
        """测试 as_agent 方法创建 Agent。"""
        client = HunyuanAnthropicClient(api_key="test-api-key")
        agent = client.as_agent(
            name="TestAgent",
            instructions="你是一个测试助手。",
        )
        assert agent is not None
