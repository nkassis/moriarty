"""Write the contract's JSON Schemas to ship/contract/schema/."""

import json
import re
from pathlib import Path

from pydantic import BaseModel

from ship.contract.actions import ActionEvent, ToolErrorBody, ToolResult
from ship.contract.comms import CommsMessage
from ship.contract.crew import Heartbeat
from ship.contract.desk import Incident, IncidentClosed, Order, Report
from ship.contract.models import ClockTick, Event, LifeformMismatch, RawObservation
from ship.contract.runs import (
    CreateRun,
    OrderDecision,
    RunConfig,
    RunPause,
    RunResume,
    RunStart,
    RunStatus,
)
from ship.contract.stream import StreamMessage

SCHEMA_DIR = Path(__file__).parent / "schema"
MODELS: tuple[type[BaseModel], ...] = (
    ClockTick,
    Event,
    LifeformMismatch,
    RawObservation,
    CommsMessage,
    Heartbeat,
    ActionEvent,
    ToolErrorBody,
    ToolResult,
    Incident,
    Order,
    Report,
    IncidentClosed,
    RunConfig,
    CreateRun,
    RunStatus,
    OrderDecision,
    RunStart,
    RunPause,
    RunResume,
    StreamMessage,
)


def schema_filename(model: type[BaseModel]) -> str:
    """`RawObservation` -> `raw_observation.json`."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", model.__name__).lower() + ".json"


def render(model: type[BaseModel]) -> str:
    """The model's JSON Schema, stable across runs."""
    return json.dumps(model.model_json_schema(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    """Generate every contract schema."""
    SCHEMA_DIR.mkdir(exist_ok=True)
    for model in MODELS:
        (SCHEMA_DIR / schema_filename(model)).write_text(render(model))


if __name__ == "__main__":
    main()
