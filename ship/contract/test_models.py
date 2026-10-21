from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import BaseModel, ValidationError

from ship.contract.enums import ClockMode, Source
from ship.contract.generate import MODELS, render, schema_filename
from ship.contract.models import (
    LIFEFORM_MISMATCH_ROUTING_KEY,
    ClockTick,
    Event,
    LifeformMismatch,
    RawObservation,
    UnknownRoutingKeyError,
    parse_reading,
)

OBSERVED = {"deck": 4, "section": "C", "expected_count": 6, "detected_count": 7}


def reading(**overrides: object) -> RawObservation:
    fields: dict[str, object] = {
        "routing_key": LIFEFORM_MISMATCH_ROUTING_KEY,
        "source": Source.SENSORS,
        "severity": 3,
        "observed": OBSERVED,
        "ship_time": 10,
    }
    return RawObservation.model_validate(fields | overrides)


EXAMPLES: list[BaseModel] = [
    ClockTick(run_id=uuid4(), ship_time=1, mode=ClockMode.LOCKSTEP),
    LifeformMismatch.model_validate(OBSERVED),
    reading(),
    Event(
        event_id=uuid4(),
        run_id=uuid4(),
        routing_key=LIFEFORM_MISMATCH_ROUTING_KEY,
        source=Source.SENSORS,
        severity=3,
        observed=OBSERVED,
        ship_time=10,
        wall_time=datetime.now(UTC),
    ),
]


@pytest.mark.parametrize("model", EXAMPLES, ids=lambda model: type(model).__name__)
def test_round_trips_through_json(model: BaseModel) -> None:
    assert type(model).model_validate_json(model.model_dump_json()) == model


@pytest.mark.parametrize("severity", [0, 6])
def test_severity_is_bounded(severity: int) -> None:
    with pytest.raises(ValidationError):
        reading(severity=severity)


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        reading(hidden_cause="intruder")


def test_event_needs_timezone_aware_wall_time() -> None:
    fields = EXAMPLES[3].model_dump() | {"wall_time": datetime(2026, 1, 1)}
    with pytest.raises(ValidationError):
        Event.model_validate(fields)


def test_parse_reading_accepts_valid_reading() -> None:
    body = reading().model_dump_json().encode()
    assert parse_reading(LIFEFORM_MISMATCH_ROUTING_KEY, body) == reading()


def test_parse_reading_rejects_unknown_routing_key() -> None:
    body = reading(routing_key="alert.medical.symptoms").model_dump_json().encode()
    with pytest.raises(UnknownRoutingKeyError):
        parse_reading("alert.medical.symptoms", body)


def test_parse_reading_rejects_routing_key_mismatch() -> None:
    body = reading(routing_key="alert.medical.symptoms").model_dump_json().encode()
    with pytest.raises(UnknownRoutingKeyError):
        parse_reading(LIFEFORM_MISMATCH_ROUTING_KEY, body)


def test_parse_reading_validates_observed() -> None:
    body = reading(observed={"deck": 4}).model_dump_json().encode()
    with pytest.raises(ValidationError):
        parse_reading(LIFEFORM_MISMATCH_ROUTING_KEY, body)


def test_schema_filenames() -> None:
    assert [schema_filename(model) for model in MODELS] == [
        "clock_tick.json",
        "event.json",
        "lifeform_mismatch.json",
        "raw_observation.json",
    ]


def test_rendered_schema_is_stable() -> None:
    assert render(Event) == render(Event)
    assert render(Event).endswith("}\n")
