# Copyright (c) Microsoft. All rights reserved.

"""Venus OpenAI 兼容客户端单元测试。"""

import os
from unittest.mock import patch

import pytest
from agent_framework.exceptions import ServiceInitializationError

from agent_framework_venus_openai import VenusOpenAIChatClient, VenusOpenAISettings


class TestVenusOpenAISettings:
    """测试 VenusOpenAISettings 环境变量加载。"""

    def test_default_settings(self) -> None:
        """测试默认设置（无环境变量时应为 None）。"""
        with patch.dict(os.environ, {}, clear=True):
            settings = VenusOpenAISettings()
            assert settings.api_key is None
            assert settings.base_url is None
            assert settings.model_id is None

    def test_settings_from_env(self) -> None:
        """测试从环境变量加载设置。"""
        with patch.dict(
            os.environ,
            {
                "VENUS_OPENAI_API_KEY": "test-api-key",
                "VENUS_OPENAI_BASE_URL": "https://custom.endpoint.com/v1",
                "VENUS_OPENAI_MODEL_ID": "glm-5",
            },
        ):
            settings = VenusOpenAISettings()
            assert settings.api_key is not None
            assert settings.api_key.get_secret_value() == "test-api-key"
            assert settings.base_url == "https://custom.endpoint.com/v1"
            assert settings.model_id == "glm-5"


class TestVenusOpenAIChatClient:
    """测试 VenusOpenAIChatClient 初始化。"""

    def test_init_without_api_key_raises(self) -> None:
        """测试缺少 API 密钥时应抛出 ServiceInitializationError。"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ServiceInitializationError, match="Venus API key is required"):
                VenusOpenAIChatClient()

    def test_init_with_api_key(self) -> None:
        """测试使用 API 密钥初始化。"""
        client = VenusOpenAIChatClient(api_key="test-api-key")
        assert client.model_id == "deepseek-v3.2"
        assert "v2.open.venus.oa.com" in str(client.base_url)

    def test_init_with_custom_model(self) -> None:
        """测试使用自定义模型名称初始化。"""
        client = VenusOpenAIChatClient(
            api_key="test-api-key",
            model_id="glm-5",
        )
        assert client.model_id == "glm-5"

    def test_init_with_custom_base_url(self) -> None:
        """测试使用自定义 base_url 初始化。"""
        client = VenusOpenAIChatClient(
            api_key="test-api-key",
            base_url="https://custom.endpoint.com/v1",
        )
        assert "custom.endpoint.com" in str(client.base_url)

    def test_init_with_env_vars(self) -> None:
        """测试从环境变量初始化。"""
        with patch.dict(
            os.environ,
            {
                "VENUS_OPENAI_API_KEY": "env-api-key",
                "VENUS_OPENAI_MODEL_ID": "hunyuan-turbo",
            },
        ):
            client = VenusOpenAIChatClient()
            assert client.model_id == "hunyuan-turbo"

    def test_default_base_url(self) -> None:
        """测试默认 base_url 为 Venus 端点。"""
        client = VenusOpenAIChatClient(api_key="test-api-key")
        assert "v2.open.venus.oa.com/llmproxy" in str(client.base_url)

    def test_default_model(self) -> None:
        """测试默认模型为 deepseek-v3.2。"""
        client = VenusOpenAIChatClient(api_key="test-api-key")
        assert client.model_id == "deepseek-v3.2"

    def test_as_agent(self) -> None:
        """测试 as_agent 方法创建 Agent。"""
        client = VenusOpenAIChatClient(api_key="test-api-key")
        agent = client.as_agent(
            name="TestAgent",
            instructions="你是一个测试助手。",
        )
        assert agent is not None
