# Microsoft Agent Framework 项目介绍

## 🚀 项目概述

**Microsoft Agent Framework** 是一个现代化的AI代理开发框架，支持Python和.NET双语言栈，专为构建企业级AI应用而设计。该框架提供了完整的工具链、工作流引擎和开发工具，帮助开发者快速构建、部署和管理智能代理系统。

### 核心特性
- **多语言支持**：完整的Python和.NET实现
- **多AI提供商**：支持Azure AI、OpenAI、Anthropic、Google Gemini、Ollama等
- **工作流引擎**：基于Durable Task Framework的强大编排能力
- **模块化架构**：22个独立Python包，功能高度解耦
- **现代化工具链**：集成Ruff、Pyright、Mypy等代码质量工具

## 🏗️ 技术架构

### Python技术栈

#### 核心模块
- **agent-framework-core**：基础框架核心
- **agent-framework-durabletask**：工作流引擎
- **agent-framework-orchestrations**：编排管理
- **agent-framework-declarative**：声明式工作流

#### AI模型支持
- **agent-framework-azure-ai**：Azure AI服务集成
- **agent-framework-anthropic**：Anthropic Claude支持
- **agent-framework-bedrock**：AWS Bedrock支持
- **agent-framework-ollama**：本地Ollama模型支持
- **agent-framework-claude**：Claude模型专用支持

#### 开发工具
- **agent-framework-devui**：开发用户界面
- **agent-framework-ag-ui**：AG UI框架
- **agent-framework-lab**：实验性功能模块

#### 存储和集成
- **agent-framework-redis**：Redis存储支持
- **agent-framework-mem0**：Mem0内存管理
- **agent-framework-a2a**：代理间通信
- **agent-framework-copilotstudio**：Copilot Studio集成
- **agent-framework-github-copilot**：GitHub Copilot集成

### .NET技术栈

#### 核心项目
- **Microsoft.Agents.AI.Abstractions**：核心抽象层
- **Microsoft.Agents.AI**：核心实现层
- **Microsoft.Agents.AI.Orchestrations**：编排引擎

#### 多AI提供商支持
- Azure AI Services
- OpenAI API
- Anthropic Claude
- Google Gemini
- 本地Ollama部署

## 🛠️ 开发工具链

### Python开发环境

#### 包管理器
- **uv**：现代化的Python包管理器
- **flit**：包构建和发布工具

#### 代码质量工具
- **Ruff**：极速的Python代码检查器
- **Pyright**：微软官方的Python类型检查器
- **Mypy**：静态类型检查
- **pytest**：测试框架

#### 开发工具
- **poethepoet**：任务运行器
- **pre-commit**：Git钩子管理
- **debugpy**：调试工具

### .NET开发环境
- **PackageReference**：现代包管理
- **Azure SDK集成**：完整的Azure服务支持
- **多目标框架**：支持.NET 6.0+版本

## 📚 示例和学习路径

### 入门示例
- **minimal_sample.py**：最基础的代理示例
- **getting_started/agents**：各种代理类型示例
- **getting_started/tools**：工具使用示例

### 高级功能
- **orchestrations**：工作流编排示例
- **durabletask**：持久化任务示例
- **declarative**：声明式编程示例
- **middleware**：中间件开发示例

### 集成示例
- **autogen-migration**：AutoGen迁移示例
- **semantic-kernel-migration**：Semantic Kernel迁移示例
- **m365-agent**：Microsoft 365集成示例

## 🔧 核心概念

### 代理（Agent）
代理是框架的核心构建块，封装了AI模型、工具和业务逻辑：

```python
from agent_framework.openai import OpenAIChatClient

agent = OpenAIChatClient().as_agent(
    name="WeatherAgent",
    instructions="You are a helpful weather agent.",
    tools=get_weather
)
```

### 工具（Tools）
工具是代理可以调用的功能模块：

```python
from agent_framework import tool

@tool(approval_mode="never_require")
def get_weather(location: str) -> str:
    """Get the weather for a given location."""
    return f"Weather in {location}: sunny"
```

### 工作流（Workflows）
工作流支持复杂的多代理协作：

- **顺序执行**：代理按顺序执行任务
- **并发执行**：多个代理并行工作
- **条件分支**：基于条件选择执行路径
- **人工介入**：支持人工审核和决策

## 🚀 快速开始

### Python环境设置

```bash
# 安装uv包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone https://github.com/microsoft/agent-framework.git
cd agent-framework/python

# 安装依赖
uv sync --all-packages --all-extras --dev

# 运行示例
python samples/getting_started/minimal_sample.py
```

### .NET环境设置

```bash
# 克隆项目
git clone https://github.com/microsoft/agent-framework.git
cd agent-framework/dotnet

# 恢复NuGet包
dotnet restore

# 构建项目
dotnet build

# 运行示例
dotnet run --project samples/GettingStarted/MinimalSample
```

## 📊 项目结构

```
agent-framework/
├── python/                 # Python实现
│   ├── packages/          # 22个功能模块包
│   ├── samples/           # 丰富的示例代码
│   └── pyproject.toml     # 项目配置
├── dotnet/                # .NET实现
│   ├── src/               # 核心源代码
│   ├── samples/           # .NET示例
│   └── Directory.Packages.props # 包管理
└── README.md              # 项目主文档
```

## 🔍 核心优势

### 企业级特性
- **可观测性**：完整的监控和追踪支持
- **安全性**：内置安全最佳实践
- **可扩展性**：模块化架构支持自定义扩展
- **可靠性**：基于Durable Task的持久化工作流

### 开发体验
- **类型安全**：全面的类型注解和检查
- **开发工具**：丰富的调试和测试工具
- **文档完善**：详细的示例和API文档
- **社区支持**：活跃的开发社区

### 生产就绪
- **部署友好**：支持Azure Functions、容器化部署
- **性能优化**：异步处理和并行执行
- **错误处理**：完善的异常处理机制
- **配置管理**：灵活的环境配置支持

## 🤝 贡献指南

项目欢迎社区贡献，主要贡献方式包括：
- 提交bug报告和功能请求
- 改进文档和示例代码
- 开发新的功能模块
- 性能优化和代码重构

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🔗 相关资源

- [官方文档](https://aka.ms/agent-framework)
- [GitHub仓库](https://github.com/microsoft/agent-framework)
- [问题追踪](https://github.com/microsoft/agent-framework/issues)
- [发布说明](https://github.com/microsoft/agent-framework/releases)

---

*最后更新：2026年2月9日*