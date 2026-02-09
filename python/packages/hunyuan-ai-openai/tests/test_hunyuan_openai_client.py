# Copyright (c) Microsoft. All rights reserved.

"""腾讯云混元 OpenAI 兼容客户端单元测试。"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agent_framework.exceptions import ServiceInitializationError

from agent_framework_hunyuan_ai_openai import HunyuanOpenAIChatClient, HunyuanOpenAISettings


class TestHunyuanOpenAISettings:
    """测试 HunyuanOpenAISettings 环境变量加载。"""

    def test_default_settings(self) -> None:
        """测试默认设置（无环境变量时应为 None）。"""
        with patch.dict(os.environ, {}, clear=True):
            settings = HunyuanOpenAISettings()
            assert settings.api_key is None
            assert settings.base_url is None
            assert settings.model_id is None

    def test_settings_from_env(self) -> None:
        """测试从环境变量加载设置。"""
        with patch.dict(
            os.environ,
            {
                "HUNYUAN_OPENAI_API_KEY": "test-api-key",
                "HUNYUAN_OPENAI_BASE_URL": "https://custom.endpoint.com/v1",
                "HUNYUAN_OPENAI_MODEL_ID": "hunyuan-pro",
            },
        ):
            settings = HunyuanOpenAISettings()
            assert settings.api_key is not None
            assert settings.api_key.get_secret_value() == "test-api-key"
            assert settings.base_url == "https://custom.endpoint.com/v1"
            assert settings.model_id == "hunyuan-pro"


class TestHunyuanOpenAIChatClient:
    """测试 HunyuanOpenAIChatClient 初始化。"""

    def test_init_without_api_key_raises(self) -> None:
        """测试缺少 API 密钥时应抛出 ServiceInitializationError。"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ServiceInitializationError, match="Hunyuan API key is required"):
                HunyuanOpenAIChatClient()

    def test_init_with_api_key(self) -> None:
        """测试使用 API 密钥初始化。"""
        client = HunyuanOpenAIChatClient(api_key="test-api-key")
        assert client.model_id == "hunyuan-turbos-latest"
        assert "api.hunyuan.cloud.tencent.com" in str(client.base_url)

    def test_init_with_custom_model(self) -> None:
        """测试使用自定义模型名称初始化。"""
        client = HunyuanOpenAIChatClient(
            api_key="test-api-key",
            model_id="hunyuan-pro",
        )
        assert client.model_id == "hunyuan-pro"

    def test_init_with_custom_base_url(self) -> None:
        """测试使用自定义 base_url 初始化。"""
        client = HunyuanOpenAIChatClient(
            api_key="test-api-key",
            base_url="https://custom.endpoint.com/v1",
        )
        assert "custom.endpoint.com" in str(client.base_url)

    def test_init_with_env_vars(self) -> None:
        """测试从环境变量初始化。"""
        with patch.dict(
            os.environ,
            {
                "HUNYUAN_OPENAI_API_KEY": "env-api-key",
                "HUNYUAN_OPENAI_MODEL_ID": "hunyuan-standard",
            },
        ):
            client = HunyuanOpenAIChatClient()
            assert client.model_id == "hunyuan-standard"

    def test_default_base_url(self) -> None:
        """测试默认 base_url 为腾讯云混元端点。"""
        client = HunyuanOpenAIChatClient(api_key="test-api-key")
        assert "api.hunyuan.cloud.tencent.com/v1" in str(client.base_url)

    def test_as_agent(self) -> None:
        """测试 as_agent 方法创建 Agent。"""
        client = HunyuanOpenAIChatClient(api_key="test-api-key")
        agent = client.as_agent(
            name="TestAgent",
            instructions="你是一个测试助手。",
        )
        assert agent is not None
