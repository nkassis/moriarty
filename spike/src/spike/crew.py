"""The crew: one agent that wakes on an alert and works it through MCP."""

import asyncio
import json
import logging
import os
from typing import Any

import httpx
from mcp import Client
from mcp.types import CallToolResult, TextContent, Tool
from pydantic import BaseModel, Field, SecretStr

from spike.bus import ALERTS, COMMS, Bus, connect, now

logger = logging.getLogger("spike.crew")

MAX_TURNS = 8
MAX_TOKENS = 4096
RESULT_LIMIT = 300
MODEL_TIMEOUT_SECONDS = 30.0
SYSTEM_PROMPT = (
    "You are the operations officer of a starship. Investigate before acting. "
    "Change one thing at a time. Verify with a sensor read before declaring the "
    "incident resolved. Keep messages to one or two sentences."
)


class ToolFailedError(Exception):
    """An MCP tool call came back flagged as an error."""


class LlmSettings(BaseModel):
    """Model endpoint configuration."""

    base_url: str = Field(min_length=1)
    api_key: SecretStr = Field(min_length=1)
    model: str = Field(min_length=1)


def load_settings() -> LlmSettings:
    """Read the model configuration from the environment."""
    return LlmSettings(
        base_url=os.environ["LLM_BASE_URL"],
        api_key=SecretStr(os.environ["LLM_API_KEY"]),
        model=os.environ["LLM_MODEL"],
    )


def to_openai_tool(tool: Tool) -> dict[str, Any]:
    """Convert an MCP tool to an OpenAI tool definition."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.input_schema,
        },
    }


def result_text(result: CallToolResult) -> str:
    """Join the text blocks of a tool result."""
    return "\n".join(block.text for block in result.content if isinstance(block, TextContent))


async def say(bus: Bus, kind: str, **fields: Any) -> None:  # noqa: ANN401 -- JSON message fields
    """Publish one crew message to comms."""
    await bus.publish(COMMS, {"ts": now(), "from": "ops", "kind": kind, **fields})


async def chat(
    http: httpx.AsyncClient,
    settings: LlmSettings,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> dict[str, Any]:
    """Make one chat completion call and return the assistant message."""
    response = await http.post(
        f"{settings.base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.api_key.get_secret_value()}"},
        json={
            "model": settings.model,
            "max_tokens": MAX_TOKENS,
            "messages": messages,
            "tools": tools,
        },
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]


async def execute_call(bus: Bus, client: Client, call: dict[str, Any]) -> dict[str, Any]:
    """Run one tool call through MCP and return the tool message for the model."""
    name = call["function"]["name"]
    arguments = json.loads(call["function"]["arguments"] or "{}")
    await say(bus, "tool_call", name=name, arguments=arguments)
    result = await client.call_tool(name, arguments)
    text = result_text(result)
    if result.is_error:
        raise ToolFailedError(f"{name}: {text}")
    await say(bus, "tool_result", name=name, result=text[:RESULT_LIMIT])
    return {"role": "tool", "tool_call_id": call["id"], "content": text}


async def run_agent(bus: Bus, settings: LlmSettings, mcp_url: str, alert: dict[str, Any]) -> None:
    """Work one alert until the model stops calling tools or the turns run out."""
    async with Client(mcp_url) as client, httpx.AsyncClient(timeout=MODEL_TIMEOUT_SECONDS) as http:
        tools = [to_openai_tool(tool) for tool in (await client.list_tools()).tools]
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Alert received: {json.dumps(alert)}"},
        ]
        for _ in range(MAX_TURNS):
            message = await chat(http, settings, messages, tools)
            content = message.get("content")
            calls = message.get("tool_calls") or []
            if content:
                await say(bus, "say", text=content)
            if not calls:
                return
            messages.append({"role": "assistant", "content": content, "tool_calls": calls})
            for call in calls:
                messages.append(await execute_call(bus, client, call))
        await say(bus, "error", text=f"gave up after {MAX_TURNS} turns")


class Crew:
    """Starts one agent run per alert key at a time."""

    def __init__(self, bus: Bus, settings: LlmSettings, mcp_url: str) -> None:
        self.bus = bus
        self.settings = settings
        self.mcp_url = mcp_url
        self.active: dict[str, asyncio.Task[None]] = {}

    async def on_alert(self, _routing_key: str, alert: dict[str, Any]) -> None:
        """Start a run on a raised alert unless one is active for the same key."""
        key = alert["key"]
        if alert["state"] != "raised" or key in self.active:
            return
        self.active[key] = asyncio.create_task(self.run(key, alert))

    async def run(self, key: str, alert: dict[str, Any]) -> None:
        """Run the agent; any failure ends the run with an error line on comms."""
        logger.info("run started for %s", key)
        try:
            await run_agent(self.bus, self.settings, self.mcp_url, alert)
        except Exception as exc:  # Run boundary: every failure must reach comms.
            logger.exception("run failed for %s", key)
            await say(self.bus, "error", text=f"run failed: {exc!r}"[:RESULT_LIMIT])
        finally:
            del self.active[key]
            logger.info("run finished for %s", key)


async def main() -> None:
    """Listen for alerts forever."""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    settings = load_settings()
    bus = await connect()
    crew = Crew(bus, settings, os.environ.get("MCP_URL", "http://ship:8000/mcp"))
    await bus.subscribe([ALERTS], crew.on_alert)
    logger.info("crew on station")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
