"""Crew registration: the heartbeat on `crew.heartbeat`."""

from typing import Annotated, Self
from uuid import UUID

from pydantic import Field, model_validator

from ship.contract.enums import AgentState, Division
from ship.contract.ids import IncidentId, StationName
from ship.contract.models import ContractModel, ShipTime

HEARTBEAT_ROUTING_KEY = "crew.heartbeat"


class StationStatus(ContractModel):
    """One station as the Stations panel shows it."""

    name: StationName
    index: Annotated[int, Field(ge=1, le=99)]
    division: Division
    state: AgentState
    activity: Annotated[str, Field(max_length=80)] | None = None
    incident_id: IncidentId | None = None


class Heartbeat(ContractModel):
    """Every station a crew defines, live or `standby`. `seen_tick` is the latest
    `ship_time` the crew has observed, for the lockstep predicate."""

    crew: Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{0,31}$", description="e.g. crew-xo")]
    run_id: UUID
    seen_tick: ShipTime | None = None
    stations: Annotated[list[StationStatus], Field(min_length=1)]

    @model_validator(mode="after")
    def _unique_stations(self) -> Self:
        names = [station.name for station in self.stations]
        if len(names) != len(set(names)):
            raise ValueError("station names must be unique")
        return self
