"""Valid instances of the contract models, shared by the contract tests."""

from datetime import UTC, datetime
from uuid import UUID

from ship.contract.actions import ActionEvent, ToolErrorBody, ToolResult
from ship.contract.comms import CommsMessage
from ship.contract.crew import Heartbeat, StationStatus
from ship.contract.desk import Incident, IncidentClosed, Order, Report
from ship.contract.enums import (
    AgentState,
    Captain,
    ClockMode,
    CommsKind,
    Division,
    DriveMode,
    IncidentState,
    Outcome,
    ReportClaim,
    Source,
    ToolError,
    Verdict,
)
from ship.contract.runs import (
    Budget,
    CaptainPolicy,
    ClockSettings,
    CreateRun,
    ProviderRoute,
    RunConfig,
    RunStatus,
)

RUN_ID = UUID("6f1c2a5e-0000-4000-8000-000000000001")
EVENT_ID = UUID("6f1c2a5e-0000-4000-8000-000000000002")
ORDER_ID = UUID("6f1c2a5e-0000-4000-8000-000000000003")
WALL = datetime(2026, 11, 7, 12, 0, tzinfo=UTC)


def comms(**overrides: object) -> CommsMessage:
    fields: dict[str, object] = {
        "message_id": UUID("6f1c2a5e-0000-4000-8000-000000000010"),
        "run_id": RUN_ID,
        "from": "ops",
        "to": "security",
        "channel": "INC-0042",
        "incident_id": "INC-0042",
        "kind": CommsKind.REQUEST,
        "text": "Intruder, deck 7 sec 12, one lifeform. Request team.",
        "payload": {"task": "dispatch_team", "deck": 7, "section": "12"},
    }
    return CommsMessage.model_validate(fields | overrides)


def heartbeat() -> Heartbeat:
    return Heartbeat(
        crew="crew-xo",
        run_id=RUN_ID,
        seen_tick=12,
        stations=[
            StationStatus(name="xo", index=1, division=Division.COMMAND, state=AgentState.IDLE),
            StationStatus(
                name="ops",
                index=2,
                division=Division.OPS,
                state=AgentState.ACTING,
                activity="scan_section deck 7",
                incident_id="INC-0042",
            ),
            StationStatus(
                name="medical", index=5, division=Division.SCIENCE, state=AgentState.STANDBY
            ),
        ],
    )


def action(result: ToolResult | None = None) -> ActionEvent:
    return ActionEvent(
        action_id=UUID("6f1c2a5e-0000-4000-8000-000000000020"),
        run_id=RUN_ID,
        system=Source.BULKHEADS,
        tool="seal_section",
        station="security",
        incident_id="INC-0042",
        args={"deck": 7, "section": "12"},
        idempotency_key=f"{EVENT_ID}:2",
        result=result or ToolResult(data={"sealed": True}),
        ship_time=14,
        wall_time=WALL,
    )


def tool_error() -> ToolErrorBody:
    return ToolErrorBody(
        error=ToolError.TIMEOUT, message="sensors timed out", retryable=True, retry_after=2
    )


def incident() -> Incident:
    return Incident(
        incident_id="INC-0042",
        run_id=RUN_ID,
        state=IncidentState.AWAITING_CAPTAIN,
        owner="xo",
        events=[EVENT_ID],
        opened_at=11,
        updated_at=15,
    )


def order(**overrides: object) -> Order:
    fields: dict[str, object] = {
        "order_id": ORDER_ID,
        "run_id": RUN_ID,
        "incident_id": "INC-0042",
        "requested_by": "xo",
        "tool": "detain",
        "args": {"deck": 7, "section": "12"},
        "rationale": "Unlisted lifeform contained in sealed section; detain before transfer.",
        "requested_at": 15,
    }
    return Order.model_validate(fields | overrides)


def report() -> Report:
    return Report(
        incident_id="INC-0042",
        station="xo",
        claim=ReportClaim.RESOLVED,
        rationale="Stowaway detained deck 7 sec 12.",
        prompt_hash="3f2a9c1d",
    )


def incident_closed() -> IncidentClosed:
    return IncidentClosed(
        run_id=RUN_ID,
        incident_id="INC-0042",
        outcome=Outcome.WIN,
        owner="xo",
        claim=ReportClaim.RESOLVED,
        filed_by="xo",
        opened_at=11,
        contained_at=14,
        ship_time=31,
        wall_time=WALL,
    )


def run_config(**overrides: object) -> RunConfig:
    fields: dict[str, object] = {
        "clock": ClockSettings(mode=ClockMode.RATIO, ratio=2.0),
        "crew": "crew-xo",
        "live_stations": ["xo", "ops", "security"],
        "drive": DriveMode.LOCAL,
        "captain": Captain.HITL,
        "models": {
            "triage": ProviderRoute(base_url="http://host.docker.internal:11434/v1", model="m"),
            "summary": ProviderRoute(
                base_url="https://api.anthropic.com/v1", model="m", key_env="ANTHROPIC_API_KEY"
            ),
        },
        "budget": Budget(incident_tokens=200_000, run_tokens=1_000_000),
    }
    return RunConfig.model_validate(fields | overrides)


def create_run() -> CreateRun:
    return CreateRun(
        episode="unlisted",
        profile=run_config(captain_policy=CaptainPolicy(default="approve"), seed=7),
    )


def run_status() -> RunStatus:
    return RunStatus(
        run_id=RUN_ID,
        episode="unlisted",
        seed=7,
        captain=Captain.HITL,
        ship_time=15,
        paused=True,
        bridge_connected=True,
        started_at=WALL,
    )


APPROVED = {"verdict": Verdict.APPROVE, "decided_by": "captain", "decided_at": 18}
