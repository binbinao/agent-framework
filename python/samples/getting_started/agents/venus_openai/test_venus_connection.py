# Copyright (c) Microsoft. All rights reserved.

"""Venus API 连通性诊断工具。

测试 Venus API 的网络连接和认证。
"""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv


async def test_venus_connection():
    """测试 Venus API 连通性。"""
    print("=" * 60)
    print("Venus API 连通性诊断")
    print("=" * 60)
    print()

    # 加载环境变量（从项目根目录的 .env 文件）
    env_path = os.path.join(os.path.dirname(__file__), "../../../../.env")
    load_dotenv(env_path)
    api_key = os.getenv("VENUS_OPENAI_API_KEY")
    base_url = os.getenv("VENUS_OPENAI_BASE_URL", "http://v2.open.venus.oa.com/llmproxy")

    if not api_key:
        print("❌ 错误: 未找到 VENUS_OPENAI_API_KEY 环境变量")
        print("   请在 .env 文件中设置 VENUS_OPENAI_API_KEY")
        return False

    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"✅ API 端点: {base_url}")
    print()

    # 测试 1: 基础网络连接
    print("【测试 1】基础网络连接")
    print("-" * 60)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/v1/models", headers={"Authorization": f"Bearer {api_key}"})
            print("✅ 网络连接成功")
            print(f"   状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"   响应: {response.text[:200]}...")
            else:
                print(f"   响应: {response.text}")
    except httpx.ConnectError as e:
        print(f"❌ 网络连接失败: {e}")
        print("   可能原因:")
        print("   - 网络不可达")
        print("   - 防火墙拦截")
        print("   - VPN 未连接")
        return False
    except httpx.TimeoutException:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

    print()

    # 测试 2: API 调用
    print("【测试 2】API 调用测试")
    print("-" * 60)
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-v3.2",
                    "messages": [{"role": "user", "content": "你好"}],
                    "max_tokens": 10,
                },
            )

            print(f"   状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print("✅ API 调用成功!")
                print(f"   模型: {result.get('model')}")
                print(f"   回复: {content}")
                return True
            if response.status_code == 403:
                error_data = response.json()
                print("❌ 访问被拒绝 (403)")
                print(f"   错误代码: {error_data.get('code')}")
                print(f"   错误信息: {error_data.get('desc')}")
                if "iOA" in str(error_data) or "风险软件" in str(error_data):
                    print()
                    print("⚠️  这是 iOA 安全策略拦截!")
                    print("   解决方案:")
                    print("   1. 打开 iOA 主界面")
                    print("   2. 进入 安全 → 软件访问详情")
                    print("   3. 设置访问规则，允许访问 v2.open.venus.oa.com")
                    print("   4. 或联系 8000 热线获取帮助")
                return False
            if response.status_code == 401:
                print("❌ 认证失败 (401) - API Key 无效或已过期")
                return False
            print("❌ API 调用失败")
            print(f"   响应: {response.text}")
            return False

    except httpx.ConnectError as e:
        print(f"❌ 网络连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {type(e).__name__}: {e}")
        return False


async def main():
    """主函数。"""
    success = await test_venus_connection()
    print()
    print("=" * 60)
    if success:
        print("✅ 所有测试通过! Venus API 连接正常")
    else:
        print("❌ 测试失败，请检查上述错误信息")
    print("=" * 60)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
