<div align="center">

# 🐉 ScalesBot

**A highly-modular AI agent framework for everyday automation**

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-4c73a2.svg?style=flat-square)](LICENSE)
[![pydantic-ai](https://img.shields.io/badge/pydantic-ai-orange?style=flat-square)](https://github.com/pydantic/pydantic-ai)

[![uv](https://img.shields.io/badge/uv-managed-4834d4?style=flat-square)](https://github.com/astral-sh/uv)
[![asyncio](https://img.shields.io/badge/async-native-2d79c7?style=flat-square)](https://docs.python.org/3/library/asyncio.html)
[![logfire](https://img.shields.io/badge/logging-logfire-ff5219?style=flat-square)](https://logfire.pydantic.dev/)

</div>

---

A powerful and extensible AI agent built on [`pydantic-ai`](https://github.com/pydantic/pydantic-ai). ScalesBot equips LLMs with tools for web browsing, HTTP requests, filesystem operations, and a dynamic skill-loading system - all configurable through your workspace.

---


## 📋 Philosophy

| Principle | Description |
|-----------|-------------|
| **📅 Daily Tasks First** | Designed for everyday automation: emails, research, data gathering, not code generation |
| **🚫 No Computer-Use** | No direct OS control or screen manipulation. Agent works through well-defined tools and APIs |
| **🧩 Modular by Design** | Everything is pluggable: providers, tools, skills. Mix and match as needed |
| **🔌 Docker Compose Ready** | Tools and services are orchestrated via docker-compose for isolated, reproducible deployments |
| **🚀 Easy Extensibility** | Add custom tools, providers, or skills without modifying core code |
| **🐛 Easy Bug Tracking** | Clear error messages, structured logging, and simple debugging workflow |
| **🧹 Clean Code** | Readable, well-documented, and maintainable codebase |
| **📝 Logging First** | Comprehensive logging with logfire for observability and troubleshooting |

---

## 🐍 Why Pydantic?

The entire framework is built around **Pydantic** for validation and configuration. This brings several advantages:

| Benefit | Description |
|---------|-------------|
| **Type Safety** | Runtime type checking catches errors before they happen |
| **Auto-Validation** | Config files, API responses, and tool inputs are validated automatically |
| **Self-Documenting** | Type hints serve as living documentation for developers |
| **Zero Boilerplate** | Pydantic models handle parsing, serialization, and validation out of the box |
| **Error Clarity** | Validation errors are human-readable and point directly to the issue |

This approach means fewer bugs, easier debugging, and a more maintainable codebase.


---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| **🛠️ Tool System** | Pre-built tools: browser automation, HTTP client, workspace management, skill loading |
| **🧩 Pluggable Providers** | Switch between OpenRouter, llama.cpp, or add custom providers |
| **📚 Skills Framework** | Load specialized capabilities dynamically via `skill.md` files |
| **🗂️ Workspace Isolation** | Each agent instance gets its own configurable workspace |
| **⚡ Async First** | Built with `asyncio` for high-performance operations |
| **🔒 Type-Safe** | Full type safety with Pydantic validation |

> 💡 **Note**: Current version tested with **Qwen3.5 27B** - works well with mid-sized models.

---

---

## 🚀 Quick Start

### Prerequisites

- [Python 3.13+](https://python.org)
- [uv](https://github.com/astral-sh/uv) - fast Python package manager

### Installation

```bash
git clone https://github.com/alexgar0/ScalesBot
cd ScalesBot
uv sync
```

### Setup

Initialize your workspace (creates `~/.ScalesBot`):

```bash
uv run setup
```

### Run

Start an interactive chat session:

```bash
uv run start
```

---

## 💬 Example Workflow

**Interactive Session:**

```bash
$ uv run start
```

```
Agent: How can I help you today?

You: Check the weather in London and send me a summary

Agent: I'll need to load the weather skill first...
[skill loaded: weather]

Agent: Here's the weather forecast for London:
- Current: -2°C, cloudy
- Today's high: +1°C
- Tomorrow: Sunny, +3°C
```

---

## ⚙️ Configuration

Your workspace is located at `~/.ScalesBot/workspace/`:

### Directory Structure

```
workspace/
├── AGENT.MD              # System prompt: agent persona, goals, execution protocol
├── USER.MD               # User profile: preferences, context, background info
├── skills/               # Skill definitions and references
│   ├── agent-browser/
│   │   ├── SKILL.md      # Core skill instructions
│   │   └── references/   # Additional docs (commands, auth, session mgmt)
│   ├── weather/
│   │   └── SKILL.md
│   └── reddit/
│       └── SKILL.md
├── states/               # Browser session states (cookies, localStorage)
└── tmp/                  # Temporary files (screenshots, downloads)
```

### Key Files

| File | Purpose |
|------|---------|
| `AGENT.MD` | System prompt: agent persona, goals, execution protocol |
| `USER.MD` | User profile: preferences, context, background information |
| `skills/` | Custom skill definitions with `SKILL.md` and optional references |
| `states/` | Browser session persistence (cookies, localStorage as JSON) |
| `tmp/` | Temporary files: screenshots, downloads, intermediate results |

### settings.toml

Located at `~/.ScalesBot/settings.toml`, this file controls provider, model, and runtime settings.

---

```toml
# LLM Provider Configuration
provider = "llamacpp"           # or "openrouter"
model = "Qwen3.5-27B-Q4_1.gguf"  # Model name/ID
api_key = "sk-dummy"            # API key (or dummy for local)

# Model Behavior
context_window = 64000          # Maximum context window size
temperature = 1.5                # Creativity vs. determinism (0-2)

# Workspace Limits
file_read_max_mb = 20           # Maximum file size for reading (MB)
```

---

## 🏗️ Architecture

```
ScalesBot/
├── src/
│   ├── core/              # Agent orchestration, config, main entry point
│   │   ├── agent.py       # pydantic-ai agent setup
│   │   ├── config.py      # Settings management
│   │   ├── main.py        # CLI entry point
│   │   ├── system_prompt.py
│   │   └── ...
│   ├── providers/         # LLM provider implementations
│   │   ├── openrouter.py
│   │   ├── llamacpp.py
│   │   └── _internal/     # Provider registry & base classes
│   └── tools/             # Agent capabilities
│       ├── browser/       # Web automation via agent-browser
│       ├── common/        # Utility tools (time, etc.)
│       ├── requests/      # HTTP client
│       ├── skills/        # Dynamic skill loading
│       ├── workspace/     # Workspace filesystem operations
│       └── _internal/     # Tool registry & base classes
├── root_template/         # Default workspace template
├── tests/                 # Test suite
└── pyproject.toml
```

---

## 🐳 Docker Services

ScalesBot supports running external services via Docker Compose for enhanced capabilities. Services are managed through a **tool abstraction layer** - the agent never touches `docker-compose` files directly.

### Example: Self-Hosted Search Server

Imagine you need web search capabilities without relying on external APIs. You can deploy a local search service:

```yaml
# docker-compose.services.yml
version: "3.8"
services:
  search:
    image: docker.io/searxng/searxng:latest
    ports:
      - "8080:8080"
    environment:
      - INSTANCE_NAME=local
    volumes:
      - ./searxng:/etc/searxng:rw
    restart: unless-stopped
```

**How the agent interacts:**

```python
# Tool call (abstracted from docker-compose)
start_service("search")  # Starts the container

# Agent can now use the service
do_http_request(
    url="http://localhost:8080/search?q=pydantic",
    method="GET"
)

stop_service("search")  # Stops when done
```

### Design Principles

| Principle | Description |
|-----------|-------------|
| **No Direct Compose Access** | Agent interacts via high-level tools (`start_service`, `stop_service`, `get_service_status`) |
| **Pre-Defined Services** | Services are declared in compose files, validated at startup |
| **Health Checks** | Tools verify service readiness before agent can use them |
| **Resource Limits** | CPU/memory constraints enforced to prevent runaway services |
| **Auto-Cleanup** | Unused services can be auto-stopped after idle timeout |

### Use Cases

- 🔍 **Local Search** - SearXNG, Metasearch
- 🗄️ **Vector Databases** - Chroma, Weaviate, Qdrant for RAG
- 🌐 **Web Scrapers** - Playwright, Puppeteer containers
- 📊 **Data Processing** - Jupyter, RStudio for analysis tasks

---

## 🔌 Available Tools

### Browser & Web

| Tool | Description |
|------|-------------|
| `use_browser()` | Execute browser commands via `agent-browser` (requires skill) |
| `take_screenshot()` | Capture current browser state as PNG image |

### HTTP & APIs

| Tool | Description |
|------|-------------|
| `do_http_request()` | Async HTTP client: GET, POST, PUT, DELETE with JSON support |

### Skills System

| Tool | Description |
|------|-------------|
| `load_skill()` | Load a skill by name (e.g., `agent-browser`, `weather`) |
| `list_skills()` | List all available skills in workspace |

### Workspace & Files

| Tool | Description |
|------|-------------|
| `list_workspace_path()` | List files and directories in workspace |
| `read_workspace_file_text()` | Read text file content (with size limits) |
| `read_workspace_image()` | Read image files for vision models |
| `create_workspace_file()` | Create new file with content |
| `edit_workspace_file()` | Overwrite existing file |
| `extend_workspace_file()` | Append content to existing file |

### Utilities

| Tool | Description |
|------|-------------|
| `get_local_time()` | Get current system time in local timezone |

---

## 🔐 Security

- **API Keys**: Store sensitive credentials in environment variables, never commit them
- **Workspace Isolation**: Each agent instance runs in its own workspace directory
- **File Access**: Tools operate only within the configured workspace path
- **Network Requests**: HTTP client has timeouts and connection limits built-in

---

## 🛠️ Development

### Adding a New Toolset

A toolset consists of tools and their shared dependencies.

**1. Create dependencies in `src/tools/<category>/deps.py`:**

```python
import httpx
from pydantic import ConfigDict
from tools._internal.base import ToolsetDeps


class RequestsDeps(ToolsetDeps):
    """Dependencies for HTTP request tools"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    http_client: httpx.AsyncClient  # Shared async client
```

**2. Create tools in `src/tools/<category>/tools.py`:**

```python
from pydantic_ai import RunContext
from tools._internal.registry import tool
from tools.requests.deps import RequestsDeps

# Plain tool (no context needed)
@tool(plain=True)
def get_local_time() -> str:
    """Returns the current system time."""
    return datetime.now().isoformat()


# Tool with dependencies
@tool()
async def do_http_request(ctx: RunContext[RequestsDeps], url: str) -> str:
    """Make HTTP requests using the shared client.
    
    Args:
        ctx: Agent context with RequestsDeps
        url: Target URL
    """
    response = await ctx.deps.http_client.get(url)
    return response.text
```

**3. The `@tool()` decorator auto-registers tools with the agent.**

### Adding a New Provider

1. Create `src/providers/<name>.py`:

```python
from pydantic_ai import ModelSettings
from pydantic_ai.models import Model
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel

from core.config import settings
from providers._internal.base import BaseProvider
from providers._internal.registry import provider


@provider("my-provider")
class MyProvider(BaseProvider):
    def _init_model(self) -> Model:
        return OpenAIChatModel(
            model_name=self.config.model,
            provider=OpenAIProvider(
                base_url="https://api.example.com/v1",
                api_key=self.config.api_key,
            ),
            settings=ModelSettings(
                temperature=self.config.temperature,
                max_tokens=self.config.context_window,
            ),
        )
```

2. The `@provider("name")` decorator auto-registers it.
3. Select it in `settings.toml`: `provider = "my-provider"`

### Adding a New Skill

Create a directory in `~/.ScalesBot/workspace/skills/<skill-name>/`:

```
skills/weather/
├── skill.md          # Required: skill description and instructions
└── references/       # Optional: additional reference files
```

---

## 🚧 TODO

Planned features and improvements:

- [x] **Vector Store Integration** - RAG capabilities with local/embedded vector databases
- [x] **Docker Compose Integration** - Automatic tool/service orchestration via docker-compose (see [Docker Services](#docker-services) below)
- [ ] **Plugin System** - External plugins for tools, providers, and skills (installable via uv)
- [ ] **Messaging Channels** - Telegram, Signal, Matrix, Nostr bridges for chat-based interaction
- [ ] **Cron & Scheduling** - Scheduled task execution with cron-like syntax (e.g., "run daily at 9 AM")
- [ ] **More Pre-built Skills** - Email handling, calendar management, research assistants
- [ ] **Multi-Agent Support** - Coordinate multiple specialized agents for complex tasks
- [ ] **CLI Improvements** - Better interactive mode, history, and session management
- [ ] **Testing Framework** - Comprehensive tests for tools and skills

---

## 🤝 Contributing

This is an actively developed hobby project. Contributions are welcome!

- 🐛 Report bugs via issues
- 💡 Suggest features
- 📝 Submit pull requests

---

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).

