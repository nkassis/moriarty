"""Contract models. JSON Schemas in `ship/contract/schema/` are generated from these."""

from typing import Annotated
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, JsonValue

from ship.contract.enums import ClockMode, Source

ShipTime = Annotated[int, Field(ge=0, description="Ticks since run start")]
Severity = Annotated[int, Field(ge=1, le=5, description="1 to 5, 5 most severe")]
RoutingKey = Annotated[str, Field(pattern=r"^alert\.[a-z_]+\.[a-z_]+$")]

CLOCK_TICK_ROUTING_KEY = "clock.tick"
LIFEFORM_MISMATCH_ROUTING_KEY = "alert.security.lifeform_mismatch"


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ClockTick(ContractModel):
    """One clock tick. `traceparent` rides in AMQP headers only."""

    run_id: UUID
    ship_time: ShipTime
    mode: ClockMode


class LifeformMismatch(ContractModel):
    """`observed` for `alert.security.lifeform_mismatch`."""

    deck: Annotated[int, Field(ge=1)]
    section: Annotated[str, Field(min_length=1)]
    expected_count: Annotated[int, Field(ge=0)]
    detected_count: Annotated[int, Field(ge=0)]


class RawObservation(ContractModel):
    """A reading as the Holodeck emits it, before the relay validates and stamps it."""

    routing_key: RoutingKey
    source: Source
    severity: Severity
    observed: dict[str, JsonValue]
    ship_time: ShipTime


class Event(ContractModel):
    """A reading as crews receive it on `subspace`. `traceparent` rides in AMQP headers only."""

    event_id: UUID
    run_id: UUID
    routing_key: RoutingKey
    source: Source
    severity: Severity
    observed: dict[str, JsonValue]
    ship_time: ShipTime
    wall_time: AwareDatetime


OBSERVED_MODELS: dict[str, type[ContractModel]] = {
    LIFEFORM_MISMATCH_ROUTING_KEY: LifeformMismatch,
}


class UnknownRoutingKeyError(ValueError):
    """A reading whose routing key has no `observed` schema."""


def parse_reading(routing_key: str, body: bytes) -> RawObservation:
    """Validate a raw reading and its `observed` payload against the routing key's schema."""
    observed_model = OBSERVED_MODELS.get(routing_key)
    if observed_model is None:
        raise UnknownRoutingKeyError(routing_key)
    reading = RawObservation.model_validate_json(body)
    if reading.routing_key != routing_key:
        raise UnknownRoutingKeyError(
            f"body routing_key {reading.routing_key!r} != message routing key {routing_key!r}"
        )
    observed_model.model_validate(reading.observed)
    return reading
