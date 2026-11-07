"""Tool results, structured tool errors and the internal action stream."""

from typing import Annotated, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, JsonValue, model_validator

from ship.contract.enums import Source, ToolError
from ship.contract.ids import IdempotencyKey, IncidentId, StationName, ToolName
from ship.contract.models import ContractModel, ShipTime

ACTION_ROUTING_KEY = "action.{system}.{tool}"


class ToolErrorBody(ContractModel):
    """A structured tool error. `retry_after` (ticks) is present exactly when `retryable`;
    `age` (ticks) only on `stale`."""

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


class ToolResult(ContractModel):
    """What an action tool returned: `data` on success, `error` otherwise. `replayed` is
    true when an `idempotency_key` returned the recorded result."""

    data: dict[str, JsonValue] | None = None
    error: ToolErrorBody | None = None
    replayed: bool = False

    @model_validator(mode="after")
    def _one_of(self) -> Self:
        if (self.data is None) == (self.error is None):
            raise ValueError("exactly one of data and error")
        return self


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
    result: ToolResult
    ship_time: ShipTime
    wall_time: AwareDatetime

    def routing_key(self) -> str:
        return ACTION_ROUTING_KEY.format(system=self.system.value, tool=self.tool)
