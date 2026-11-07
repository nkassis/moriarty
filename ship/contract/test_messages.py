"""The M1 contract messages: envelope, heartbeat, actions, desk, runs, control and stream."""

import json
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from ship.contract import examples as ex
from ship.contract.actions import ToolErrorBody, ToolResult
from ship.contract.comms import CommsMessage
from ship.contract.crew import Heartbeat
from ship.contract.desk import Order
from ship.contract.enums import ClockMode, CommsKind, ToolError, Verdict
from ship.contract.runs import CaptainPolicy, ClockSettings, RunPause, RunResume, RunStart
from ship.contract.stream import StreamComms, StreamMessage, StreamOrder, StreamSnapshot

EXAMPLES: list[BaseModel] = [
    ex.comms(),
    ex.heartbeat(),
    ex.action(),
    ex.action(ToolResult(error=ex.tool_error())),
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


@pytest.mark.parametrize("model", EXAMPLES, ids=lambda model: type(model).__name__)
def test_round_trips_through_json(model: BaseModel) -> None:
    assert type(model).model_validate_json(model.model_dump_json()) == model


# Comms envelope


def test_envelope_serializes_sender_as_from() -> None:
    wire = json.loads(ex.comms().model_dump_json())
    assert wire["from"] == "ops"
    assert "sender" not in wire


def test_envelope_routing_key() -> None:
    assert ex.comms().routing_key() == "comms.INC-0042.request"


def test_envelope_text_is_capped_at_160() -> None:
    with pytest.raises(ValidationError):
        ex.comms(text="x" * 161)


def test_envelope_needs_incident_id_off_the_all_channel() -> None:
    with pytest.raises(ValidationError, match="incident_id is required"):
        ex.comms(channel="bridge", incident_id=None)
    assert ex.comms(channel="all", to="all", incident_id=None).incident_id is None


def test_incident_channel_must_match_incident_id() -> None:
    with pytest.raises(ValidationError, match="must match"):
        ex.comms(channel="INC-0043")


def test_ack_needs_in_reply_to() -> None:
    with pytest.raises(ValidationError, match="in_reply_to"):
        ex.comms(kind=CommsKind.ACK)
    assert ex.comms(kind=CommsKind.ACK, in_reply_to=uuid4()).kind is CommsKind.ACK


def test_envelope_rejects_hidden_fields() -> None:
    with pytest.raises(ValidationError):
        CommsMessage.model_validate(ex.comms().model_dump() | {"cause": "stowaway"})


# Heartbeat


def test_heartbeat_rejects_duplicate_stations() -> None:
    beat = ex.heartbeat().model_dump()
    beat["stations"].append(beat["stations"][0])
    with pytest.raises(ValidationError, match="unique"):
        Heartbeat.model_validate(beat)


# Tool errors and results


def test_retryable_error_needs_retry_after() -> None:
    with pytest.raises(ValidationError, match="retry_after"):
        ToolErrorBody(error=ToolError.TIMEOUT, message="t", retryable=True)


def test_non_retryable_error_forbids_retry_after() -> None:
    with pytest.raises(ValidationError, match="retry_after"):
        ToolErrorBody(
            error=ToolError.REQUIRES_AUTHORIZATION, message="m", retryable=False, retry_after=1
        )


def test_age_only_on_stale() -> None:
    stale = ToolErrorBody(error=ToolError.STALE, message="s", retryable=True, retry_after=1, age=3)
    assert stale.age == 3
    with pytest.raises(ValidationError, match="age"):
        ToolErrorBody(error=ToolError.TIMEOUT, message="t", retryable=True, retry_after=1, age=3)


@pytest.mark.parametrize("fields", [{}, {"data": {}, "error": ex.tool_error()}])
def test_tool_result_is_data_or_error(fields: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="exactly one"):
        ToolResult.model_validate(fields)


def test_action_routing_key() -> None:
    assert ex.action().routing_key() == "action.bulkheads.seal_section"


# Desk


def test_order_decision_fields_are_set_together() -> None:
    with pytest.raises(ValidationError, match="together"):
        ex.order(verdict=Verdict.APPROVE)


def test_order_decider_is_captain_or_scripted() -> None:
    with pytest.raises(ValidationError):
        Order.model_validate(ex.order().model_dump() | ex.APPROVED | {"decided_by": "xo"})


@pytest.mark.parametrize("incident_id", ["INC-42", "inc-0042", "0042"])
def test_incident_id_format(incident_id: str) -> None:
    with pytest.raises(ValidationError):
        ex.order(incident_id=incident_id)


# Run profile and captain policy


def test_run_config_needs_triage_and_summary() -> None:
    models = ex.run_config().models
    with pytest.raises(ValidationError, match="summary"):
        ex.run_config(models={"triage": models["triage"]})


def test_run_config_seed_is_32_bit() -> None:
    with pytest.raises(ValidationError):
        ex.run_config(seed=2**32)


def test_provider_route_names_a_key_env_never_a_key() -> None:
    route = ex.run_config().models["summary"].model_dump()
    with pytest.raises(ValidationError):
        type(ex.run_config().models["summary"]).model_validate(route | {"key_env": "sk-ant-x"})


def test_approve_after_needs_ticks() -> None:
    with pytest.raises(ValidationError, match="ticks"):
        CaptainPolicy(default="approve_after")
    with pytest.raises(ValidationError, match="ticks"):
        CaptainPolicy(default="approve", ticks=5)
    assert CaptainPolicy(default="approve_after", ticks=20).ticks == 20


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


def stream_examples() -> list[BaseModel]:
    return [
        StreamSnapshot(
            type="snapshot",
            run_id=ex.RUN_ID,
            seq=0,
            status=ex.run_status(),
            condition="yellow",
            heartbeat=ex.heartbeat(),
            incidents=[ex.incident()],
            orders=[ex.order()],
            comms=[ex.comms()],
            tools=[ex.action()],
        ),
        StreamComms(type="comms", run_id=ex.RUN_ID, seq=1, message=ex.comms()),
        StreamOrder(type="order", run_id=ex.RUN_ID, seq=2, order=ex.order(**ex.APPROVED)),
    ]


@pytest.mark.parametrize("message", stream_examples(), ids=lambda m: type(m).__name__)
def test_stream_message_parses_by_type(message: BaseModel) -> None:
    parsed = StreamMessage.model_validate_json(message.model_dump_json())
    assert parsed.root == message


def test_stream_message_rejects_unknown_type() -> None:
    body = json.loads(stream_examples()[1].model_dump_json()) | {"type": "act"}
    with pytest.raises(ValidationError):
        StreamMessage.model_validate(body)


def test_stream_schema_requires_the_discriminator() -> None:
    schema = StreamMessage.model_json_schema()
    assert schema["discriminator"]["propertyName"] == "type"
    assert all(
        "type" in schema["$defs"][name]["required"]
        for name in schema["$defs"]
        if name.startswith("Stream")
    )
