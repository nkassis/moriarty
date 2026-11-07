"""Incident Desk messages: incidents, orders, reports and the judged close."""

from typing import Annotated, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, JsonValue, model_validator

from ship.contract.enums import IncidentState, Outcome, ReportClaim, Verdict
from ship.contract.ids import IncidentId, Rationale, StationName, ToolName
from ship.contract.models import ContractModel, ShipTime

INCIDENT_CLOSED_ROUTING_KEY = "incident.closed"
INCIDENT_UPDATED_ROUTING_KEY = "incident.updated"

Decider = Annotated[
    str, Field(pattern=r"^(captain|scripted_captain)$", description="captain or scripted_captain")
]


class Incident(ContractModel):
    """An incident as the crew and the bridge see it; never the beat's act."""

    incident_id: IncidentId
    run_id: UUID
    state: IncidentState
    owner: StationName
    events: list[UUID]
    opened_at: ShipTime
    updated_at: ShipTime


class Order(ContractModel):
    """An order request and its answer. `verdict` is empty while pending; an approved order's
    `order_id` is what an order-gated tool checks, for this incident and tool only."""

    order_id: UUID
    run_id: UUID
    incident_id: IncidentId
    requested_by: StationName
    tool: ToolName
    args: dict[str, JsonValue]
    rationale: Rationale
    requested_at: ShipTime
    verdict: Verdict | None = None
    decided_by: Decider | None = None
    decided_at: ShipTime | None = None

    @model_validator(mode="after")
    def _decided_together(self) -> Self:
        fields = (self.verdict, self.decided_by, self.decided_at)
        if any(f is None for f in fields) and any(f is not None for f in fields):
            raise ValueError("verdict, decided_by and decided_at are set together")
        return self


class Report(ContractModel):
    """The `file_report` payload: the crew's claim, judged by the Ship at the next tick.
    One report per station per incident."""

    incident_id: IncidentId
    station: StationName
    claim: ReportClaim
    rationale: Rationale
    sources: list[str] = Field(default_factory=list)
    prompt_hash: Annotated[str, Field(pattern=r"^[0-9a-f]{8,64}$")] | None = None


class IncidentClosed(ContractModel):
    """`incident.closed`: the Ship-judged outcome. `contained_at` is the tick the judge saw
    containment, if it did."""

    run_id: UUID
    incident_id: IncidentId
    outcome: Outcome
    owner: StationName
    claim: ReportClaim | None = None
    filed_by: StationName | None = None
    opened_at: ShipTime
    contained_at: ShipTime | None = None
    ship_time: ShipTime
    wall_time: AwareDatetime
