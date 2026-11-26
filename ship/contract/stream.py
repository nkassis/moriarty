"""The bridge stream: one WebSocket per run at `/runs/{run_id}/stream`.

The first message after connecting is a `snapshot` of the run's current state; every later
message is a change. `seq` increases by one per message on a connection, so a client that
sees a gap reconnects and resyncs from the next snapshot.
"""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, RootModel

from ship.contract.actions import ActionEvent
from ship.contract.comms import CommsMessage
from ship.contract.crew import Heartbeat
from ship.contract.desk import Incident, IncidentClosed, Order
from ship.contract.enums import AlertCondition
from ship.contract.models import ContractModel, ShipTime
from ship.contract.runs import RunStatus

Seq = Annotated[int, Field(ge=0)]


class AlertState(ContractModel):
    """The ship's alert condition and its reason, as the AlertBanner shows it."""

    condition: AlertCondition
    detail: Annotated[str, Field(max_length=80)]


class StreamSnapshot(ContractModel):
    """The run's current state. `alert` and `closed` are the same records the `alert` and
    `outcome` deltas carried, so a client that connects late draws the same banners."""

    type: Literal["snapshot"]
    run_id: UUID
    seq: Seq
    status: RunStatus
    alert: AlertState
    heartbeat: Heartbeat | None = None
    incidents: list[Incident]
    orders: list[Order]
    closed: list[IncidentClosed]
    comms: list[CommsMessage]
    tools: list[ActionEvent]


class StreamComms(ContractModel):
    type: Literal["comms"]
    run_id: UUID
    seq: Seq
    message: CommsMessage


class StreamTool(ContractModel):
    """An action-stream entry, rendered as a muted `tool` line."""

    type: Literal["tool"]
    run_id: UUID
    seq: Seq
    action: ActionEvent


class StreamStations(ContractModel):
    type: Literal["stations"]
    run_id: UUID
    seq: Seq
    heartbeat: Heartbeat


class StreamIncident(ContractModel):
    type: Literal["incident"]
    run_id: UUID
    seq: Seq
    incident: Incident


class StreamOrder(ContractModel):
    """An order request or its answer; a pending order lights the Captain's Chair."""

    type: Literal["order"]
    run_id: UUID
    seq: Seq
    order: Order


class StreamClock(ContractModel):
    type: Literal["clock"]
    run_id: UUID
    seq: Seq
    ship_time: ShipTime
    paused: bool


class StreamAlert(ContractModel):
    type: Literal["alert"]
    run_id: UUID
    seq: Seq
    alert: AlertState


class StreamOutcome(ContractModel):
    type: Literal["outcome"]
    run_id: UUID
    seq: Seq
    closed: IncidentClosed


class StreamMessage(
    RootModel[
        Annotated[
            StreamSnapshot
            | StreamComms
            | StreamTool
            | StreamStations
            | StreamIncident
            | StreamOrder
            | StreamClock
            | StreamAlert
            | StreamOutcome,
            Field(discriminator="type"),
        ]
    ]
):
    """Any message on the bridge stream, discriminated on `type`."""
