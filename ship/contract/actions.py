"""Tool results, structured tool errors and the internal action stream."""

from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, ConfigDict, Field, JsonValue, RootModel, model_validator

from ship.contract.enums import Source, ToolError
from ship.contract.ids import IdempotencyKey, IncidentId, StationName, ToolName
from ship.contract.models import ContractModel, ShipTime

ACTION_ROUTING_KEY = "action.{system}.{tool}"


class ToolErrorBody(ContractModel):
    """A structured tool error. `retry_after` (ticks) is present exactly when `retryable`;
    `age` (ticks) only on `stale`. The validator and the schema's `allOf` state the same rules,
    so schema validators agree with Python."""

    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {"properties": {"retryable": {"const": True}}},
                    "then": {
                        "required": ["retry_after"],
                        "properties": {"retry_after": {"type": "integer"}},
                    },
                    "else": {"properties": {"retry_after": {"type": "null"}}},
                },
                {
                    "if": {"not": {"properties": {"error": {"const": ToolError.STALE.value}}}},
                    "then": {"properties": {"age": {"type": "null"}}},
                },
            ]
        }
    )

    error: ToolError
    message: Annotated[str, Field(max_length=120)]
    retryable: bool
    retry_after: Annotated[int, Field(ge=1)] | None = None
    age: ShipTime | None = None

    @model_validator(mode="after")
    def _check_retry(self) -> Self:
        if self.retryable != (self.retry_after is not None):
            raise ValueError("retry_after is required when retryable and forbidden otherwise")
        if self.age is not None and self.error is not ToolError.STALE:
            raise ValueError("age is only set on a stale error")
        return self


class ToolSuccess(ContractModel):
    """An action tool's data. `replayed` is true when an `idempotency_key` returned the
    recorded result."""

    status: Literal["ok"]
    data: dict[str, JsonValue]
    replayed: bool = False


class ToolFailure(ContractModel):
    """An action tool's structured error; `replayed` as on `ToolSuccess`."""

    status: Literal["error"]
    error: ToolErrorBody
    replayed: bool = False


ToolOutcome = Annotated[ToolSuccess | ToolFailure, Field(discriminator="status")]


class ToolResult(RootModel[ToolOutcome]):
    """What an action tool returned, discriminated on `status`."""


class ActionEvent(ContractModel):
    """One action tool call, on the Ship-only `action.<system>.<tool>`. The Holodeck reacts to
    it, the judge scores it and the bridge renders it as a muted `tool` line."""

    action_id: UUID
    run_id: UUID
    system: Source
    tool: ToolName
    station: StationName
    incident_id: IncidentId | None = None
    args: dict[str, JsonValue]
    idempotency_key: IdempotencyKey
    order_id: UUID | None = None
    result: ToolOutcome
    ship_time: ShipTime
    wall_time: AwareDatetime

    def routing_key(self) -> str:
        return ACTION_ROUTING_KEY.format(system=self.system.value, tool=self.tool)
