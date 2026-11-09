"""Viewer: tails alerts and comms to the terminal, one line per message."""

import asyncio
import contextlib
import json
from datetime import datetime
from typing import Any

from spike.bus import ALERTS, COMMS, connect


def alert_text(alert: dict[str, Any]) -> str:
    """Describe an alert."""
    return (
        f"{alert['key']} {alert['state']}: "
        f"{alert['sensor']}={alert['value']} (threshold {alert['threshold']})"
    )


def comms_text(message: dict[str, Any]) -> str:
    """Describe a crew message."""
    match message["kind"]:
        case "tool_call":
            return f"call {message['name']} {json.dumps(message['arguments'])}"
        case "tool_result":
            return f"result {message['name']} {message['result']}"
        case "error":
            return f"ERROR {message['text']}"
        case _:
            return message["text"]


def format_line(routing_key: str, message: dict[str, Any]) -> str:
    """Render one message as `HH:MM:SS  source  text`."""
    clock = datetime.fromisoformat(message["ts"]).strftime("%H:%M:%S")
    if routing_key == ALERTS:
        source, text = "alert", alert_text(message)
    else:
        source, text = message["from"], comms_text(message)
    return f"{clock}  {source:<5}  {' '.join(text.split())}"


async def show(routing_key: str, message: dict[str, Any]) -> None:
    """Print one message."""
    print(format_line(routing_key, message), flush=True)


async def main() -> None:
    """Tail until interrupted."""
    bus = await connect()
    await bus.subscribe([ALERTS, COMMS], show)
    await asyncio.Future()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
