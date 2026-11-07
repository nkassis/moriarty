"""The comms envelope: every crew, captain and Ship line on `comms.<channel>.<kind>`."""

from typing import Annotated, Self
from uuid import UUID

from pydantic import ConfigDict, Field, JsonValue, model_validator

from ship.contract.enums import CommsKind
from ship.contract.ids import IncidentId, Rationale
from ship.contract.models import ContractModel, ShipTime

Channel = Annotated[
    str,
    Field(
        pattern=r"^(bridge|all|captain|INC-\d{4,})$",
        description="bridge, all, captain or an incident id",
    ),
]
Sender = Annotated[
    str, Field(pattern=r"^[a-z][a-z0-9_-]{0,31}$", description="A station, `captain` or `ship`")
]
Recipient = Annotated[
    str,
    Field(
        pattern=r"^[a-z][a-z0-9_-]{0,31}$", description="A station, `bridge`, `captain` or `all`"
    ),
]

COMMS_ROUTING_KEY = "comms.{channel}.{kind}"


class CommsMessage(ContractModel):
    """One comms line. Crews leave `ship_time` empty; the Ship stamps it before the bridge
    stream and the archive see the line."""

    model_config = ConfigDict(
        extra="forbid", frozen=True, validate_by_name=True, serialize_by_alias=True
    )

    message_id: UUID
    run_id: UUID
    in_reply_to: UUID | None = None
    sender: Sender = Field(alias="from")
    to: Recipient
    channel: Channel
    incident_id: IncidentId | None = None
    kind: CommsKind
    text: Rationale
    payload: dict[str, JsonValue] = Field(default_factory=dict)
    ship_time: ShipTime | None = None
    traceparent: str | None = Field(
        default=None, pattern=r"^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$"
    )

    @model_validator(mode="after")
    def _check_references(self) -> Self:
        if self.channel != "all" and self.incident_id is None:
            raise ValueError("incident_id is required unless channel is `all`")
        if self.channel.startswith("INC-") and self.channel != self.incident_id:
            raise ValueError("an incident channel must match incident_id")
        if self.kind is CommsKind.ACK and self.in_reply_to is None:
            raise ValueError("an ack needs in_reply_to")
        return self

    def routing_key(self) -> str:
        return COMMS_ROUTING_KEY.format(channel=self.channel, kind=self.kind.value)
