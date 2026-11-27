"""Identifier and text field types shared by the contract models."""

from typing import Annotated

from pydantic import Field

IncidentId = Annotated[str, Field(pattern=r"^INC-\d{4,}$", description="e.g. INC-0042")]
StationName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,31}$", description="e.g. ops")]
ToolName = Annotated[str, Field(pattern=r"^[a-z][a-z_]{0,63}$", description="e.g. seal_section")]
IdempotencyKey = Annotated[
    str, Field(min_length=1, max_length=128, description="A crew passes `event_id:step`")
]
Rationale = Annotated[str, Field(max_length=160, description="One line, 160 characters max")]
