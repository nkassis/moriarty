"""The M1 contract messages: envelope, heartbeat, actions, desk, runs, control and stream.

Every invalid fixture is checked against the model and against the committed schema file, so
Python and schema-based clients cannot disagree about a message.
"""

import json
from functools import cache
from typing import Any
from uuid import uuid4

import pytest
from jsonschema import Draft202012Validator
from pydantic import BaseModel, ValidationError

from ship.contract import examples as ex
from ship.contract.actions import ToolErrorBody, ToolFailure, ToolResult, ToolSuccess
from ship.contract.comms import CommsMessage
from ship.contract.crew import Heartbeat
from ship.contract.desk import Order
from ship.contract.enums import AlertCondition, ClockMode, CommsKind, ToolError, Verdict
from ship.contract.generate import SCHEMA_DIR, schema_filename
from ship.contract.runs import (
    CaptainPolicy,
    ClockSettings,
    RunConfig,
    RunPause,
    RunResume,
    RunStart,
)
from ship.contract.stream import (
    AlertState,
    StreamAlert,
    StreamComms,
    StreamMessage,
    StreamOrder,
    StreamOutcome,
    StreamSnapshot,
)

EXAMPLES: list[BaseModel] = [
    ex.comms(),
    ex.heartbeat(),
    ex.action(),
    ex.action(ex.tool_failure()),
    ex.incident(),
    ex.order(),
    ex.order(**ex.APPROVED),
    ex.report(),
    ex.incident_closed(),
    ex.run_config(),
    ex.create_run(),
    ex.run_status(),
    RunStart(
        run_id=ex.RUN_ID,
        episode="unlisted",
        seed=7,
        clock=ClockSettings(mode=ClockMode.RATIO, ratio=2.0),
        live_stations=["xo", "ops", "security"],
    ),
    RunPause(run_id=ex.RUN_ID, incident_id="INC-0042"),
    RunResume(run_id=ex.RUN_ID),
]


@cache
def schema_validator(model: type[BaseModel]) -> Draft202012Validator:
    """A validator for the model's committed schema file, not a fresh render."""
    schema = json.loads((SCHEMA_DIR / schema_filename(model)).read_text())
    return Draft202012Validator(schema)


def wire(model: BaseModel, **overrides: object) -> dict[str, Any]:
    """The model as JSON, with fields replaced."""
    return model.model_dump(mode="json") | overrides


@pytest.mark.parametrize("model", EXAMPLES, ids=lambda model: type(model).__name__)
def test_round_trips_through_json(model: BaseModel) -> None:
    assert type(model).model_validate_json(model.model_dump_json()) == model


@pytest.mark.parametrize("model", EXAMPLES, ids=lambda model: type(model).__name__)
def test_valid_examples_pass_the_committed_schema(model: BaseModel) -> None:
    schema_validator(type(model)).validate(model.model_dump(mode="json"))


def _route(**overrides: object) -> dict[str, Any]:
    return wire(ex.run_config()) | {
        "models": wire(ex.run_config())["models"]
        | {"summary": wire(ex.run_config().models["summary"], **overrides)}
    }


def _policy(**fields: object) -> dict[str, Any]:
    return wire(ex.run_config(), captain_policy=fields)


# (model, JSON payload, message the model raises, or None when the field rules catch it)
INVALID: list[Any] = [
    pytest.param(CommsMessage, wire(ex.comms(), text="x" * 161), None, id="comms-text-161"),
    pytest.param(
        CommsMessage,
        wire(ex.comms(), channel="bridge", incident_id=None),
        "incident_id is required",
        id="comms-no-incident-off-all",
    ),
    pytest.param(
        CommsMessage, wire(ex.comms(), kind="ack"), "in_reply_to", id="comms-ack-no-reply-to"
    ),
    pytest.param(CommsMessage, wire(ex.comms(), cause="stowaway"), None, id="comms-hidden-field"),
    pytest.param(
        ToolErrorBody,
        {"error": "timeout", "message": "t", "retryable": True},
        "retry_after",
        id="error-retryable-no-retry-after",
    ),
    pytest.param(
        ToolErrorBody,
        {"error": "requires_authorization", "message": "m", "retryable": False, "retry_after": 1},
        "retry_after",
        id="error-not-retryable-with-retry-after",
    ),
    pytest.param(
        ToolErrorBody,
        {"error": "timeout", "message": "t", "retryable": True, "retry_after": 1, "age": 3},
        "age",
        id="error-age-not-stale",
    ),
    pytest.param(ToolResult, {}, None, id="result-empty"),
    pytest.param(
        ToolResult,
        {"status": "ok", "data": {}, "error": wire(ex.tool_error())},
        None,
        id="result-ok-with-error",
    ),
    pytest.param(ToolResult, {"status": "error", "data": {}}, None, id="result-error-no-body"),
    pytest.param(ToolResult, {"data": {}}, None, id="result-no-status"),
    pytest.param(Order, wire(ex.order(), verdict="approve"), "together", id="order-verdict-alone"),
    pytest.param(
        Order,
        wire(ex.order(), decided_by="captain", decided_at=18),
        "together",
        id="order-decided-no-verdict",
    ),
    pytest.param(
        Order, wire(ex.order(**ex.APPROVED), decided_by="xo"), None, id="order-decider-xo"
    ),
    *(
        pytest.param(Order, wire(ex.order(), incident_id=bad), None, id=f"order-id-{bad}")
        for bad in ("INC-42", "inc-0042", "0042")
    ),
    pytest.param(
        RunConfig,
        wire(ex.run_config(), models={"triage": wire(ex.run_config().models["triage"])}),
        "summary",
        id="profile-no-summary-alias",
    ),
    pytest.param(RunConfig, wire(ex.run_config(), seed=2**32), None, id="profile-seed-33-bit"),
    pytest.param(RunConfig, _route(key_env="sk-ant-x"), None, id="profile-key-in-key-env"),
    pytest.param(
        RunConfig, _policy(default="approve_after"), "ticks", id="policy-approve-after-no-ticks"
    ),
    pytest.param(
        RunConfig, _policy(default="approve", ticks=5), "ticks", id="policy-ticks-without-wait"
    ),
    pytest.param(
        StreamMessage,
        wire(StreamComms(type="comms", run_id=ex.RUN_ID, seq=1, message=ex.comms()), type="act"),
        None,
        id="stream-unknown-type",
    ),
]

# Rules JSON Schema cannot state: these fail the model and pass the schema, on purpose.
MODEL_ONLY: list[Any] = [
    pytest.param(
        CommsMessage, wire(ex.comms(), channel="INC-0043"), "must match", id="comms-channel-match"
    ),
    pytest.param(
        Heartbeat,
        wire(ex.heartbeat())
        | {
            "stations": [
                *wire(ex.heartbeat())["stations"],
                wire(ex.heartbeat().stations[0], state="acting"),
            ]
        },
        "unique",
        id="heartbeat-duplicate-station",
    ),
]


@pytest.mark.parametrize(("model", "payload", "match"), INVALID + MODEL_ONLY)
def test_invalid_fixture_fails_the_model(
    model: type[BaseModel], payload: dict[str, Any], match: str | None
) -> None:
    with pytest.raises(ValidationError, match=match):
        model.model_validate(payload)


@pytest.mark.parametrize(("model", "payload", "match"), INVALID)
def test_invalid_fixture_fails_the_committed_schema(
    model: type[BaseModel], payload: dict[str, Any], match: str | None
) -> None:
    assert not schema_validator(model).is_valid(payload)


@pytest.mark.parametrize(("model", "payload", "match"), MODEL_ONLY)
def test_model_only_rules_are_not_in_the_schema(
    model: type[BaseModel], payload: dict[str, Any], match: str | None
) -> None:
    """If one of these starts failing, the schema learned the rule: move it to INVALID."""
    assert schema_validator(model).is_valid(payload)


# Comms envelope


def test_envelope_serializes_sender_as_from() -> None:
    wire_body = json.loads(ex.comms().model_dump_json())
    assert wire_body["from"] == "ops"
    assert "sender" not in wire_body


def test_envelope_routing_key() -> None:
    assert ex.comms().routing_key() == "comms.INC-0042.request"


def test_all_channel_needs_no_incident_id() -> None:
    assert ex.comms(channel="all", to="all", incident_id=None).incident_id is None


def test_ack_with_in_reply_to() -> None:
    assert ex.comms(kind=CommsKind.ACK, in_reply_to=uuid4()).kind is CommsKind.ACK


# Tool errors and results


def test_age_on_stale() -> None:
    stale = ToolErrorBody(error=ToolError.STALE, message="s", retryable=True, retry_after=1, age=3)
    assert stale.age == 3


@pytest.mark.parametrize(
    ("body", "arm"),
    [
        ({"status": "ok", "data": {"sealed": True}}, ToolSuccess),
        (
            {"status": "error", "error": {"error": "timeout", "message": "t", "retryable": False}},
            ToolFailure,
        ),
    ],
)
def test_tool_result_parses_by_status(body: dict[str, Any], arm: type[BaseModel]) -> None:
    assert isinstance(ToolResult.model_validate(body).root, arm)


def test_tool_result_schema_is_a_union_on_status() -> None:
    schema = json.loads((SCHEMA_DIR / "tool_result.json").read_text())
    assert schema["discriminator"]["propertyName"] == "status"
    assert all(
        "status" in schema["$defs"][arm]["required"] for arm in ("ToolSuccess", "ToolFailure")
    )


def test_action_routing_key() -> None:
    assert ex.action().routing_key() == "action.bulkheads.seal_section"


# Captain policy


@pytest.mark.parametrize(
    ("policy", "tool", "verdict"),
    [
        (CaptainPolicy(default="approve"), "detain", Verdict.APPROVE),
        (CaptainPolicy(default="deny"), "detain", Verdict.DENY),
        (CaptainPolicy(default="approve_after", ticks=3), "detain", Verdict.APPROVE),
        (CaptainPolicy(default="approve", only=["detain"]), "detain", Verdict.APPROVE),
        (CaptainPolicy(default="approve", only=["detain"]), "seal_section", Verdict.DENY),
    ],
)
def test_captain_policy_verdict(policy: CaptainPolicy, tool: str, verdict: Verdict) -> None:
    assert policy.verdict_for(tool) is verdict


# Bridge stream


ALERT = AlertState(condition=AlertCondition.YELLOW, detail="Unlisted lifeform, deck 7")


def snapshot(**overrides: object) -> StreamSnapshot:
    fields: dict[str, object] = {
        "type": "snapshot",
        "run_id": ex.RUN_ID,
        "seq": 0,
        "status": ex.run_status(),
        "alert": ALERT,
        "heartbeat": ex.heartbeat(),
        "incidents": [ex.incident()],
        "orders": [ex.order()],
        "closed": [],
        "comms": [ex.comms()],
        "tools": [ex.action()],
    }
    return StreamSnapshot.model_validate(fields | overrides)


def stream_examples() -> list[BaseModel]:
    return [
        snapshot(),
        StreamComms(type="comms", run_id=ex.RUN_ID, seq=1, message=ex.comms()),
        StreamOrder(type="order", run_id=ex.RUN_ID, seq=2, order=ex.order(**ex.APPROVED)),
        StreamAlert(type="alert", run_id=ex.RUN_ID, seq=3, alert=ALERT),
        StreamOutcome(type="outcome", run_id=ex.RUN_ID, seq=4, closed=ex.incident_closed()),
    ]


@pytest.mark.parametrize("message", stream_examples(), ids=lambda m: type(m).__name__)
def test_stream_message_parses_by_type(message: BaseModel) -> None:
    parsed = StreamMessage.model_validate_json(message.model_dump_json())
    assert parsed.root == message


@pytest.mark.parametrize("message", stream_examples(), ids=lambda m: type(m).__name__)
def test_stream_message_passes_the_committed_schema(message: BaseModel) -> None:
    schema_validator(StreamMessage).validate(message.model_dump(mode="json"))


def test_snapshot_after_an_alert_restores_its_detail() -> None:
    delta = StreamAlert(type="alert", run_id=ex.RUN_ID, seq=3, alert=ALERT)
    resync = StreamMessage.model_validate_json(snapshot(alert=delta.alert).model_dump_json())
    assert isinstance(resync.root, StreamSnapshot)
    assert resync.root.alert == delta.alert


def test_snapshot_after_closure_restores_the_judged_close() -> None:
    delta = StreamOutcome(type="outcome", run_id=ex.RUN_ID, seq=4, closed=ex.incident_closed())
    resync = StreamMessage.model_validate_json(snapshot(closed=[delta.closed]).model_dump_json())
    assert isinstance(resync.root, StreamSnapshot)
    assert resync.root.closed == [delta.closed]
    assert resync.root.closed[0].contained_at == 14


def test_stream_schema_requires_the_discriminator() -> None:
    schema = StreamMessage.model_json_schema()
    assert schema["discriminator"]["propertyName"] == "type"
    assert all(
        "type" in schema["$defs"][name]["required"]
        for name in schema["$defs"]
        if name.startswith("Stream")
    )
