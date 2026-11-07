"""Run configuration, the Ship API's run shapes and the Ship-only control messages."""

from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import AwareDatetime, Field, model_validator

from ship.contract.enums import Captain, ClockMode, DriveMode, Outcome, Verdict
from ship.contract.ids import IncidentId, StationName, ToolName
from ship.contract.models import ContractModel, ShipTime

CONTROL_EXCHANGE = "control"
RUN_START_ROUTING_KEY = "run.start"
RUN_PAUSE_ROUTING_KEY = "run.pause"
RUN_RESUME_ROUTING_KEY = "run.resume"

Seed = Annotated[int, Field(ge=0, lt=2**32)]
EpisodeName = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{0,63}$", description="e.g. unlisted")]
Alias = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,31}$", description="e.g. triage")]


class CaptainPolicy(ContractModel):
    """The scripted captain's script (decisions-m1 8). `approve_after` counts world ticks;
    `only` limits approval to the listed tools and denies the rest."""

    default: Literal["approve", "deny", "approve_after"]
    ticks: Annotated[int, Field(ge=1)] | None = None
    only: list[ToolName] | None = None

    @model_validator(mode="after")
    def _ticks_with_approve_after(self) -> Self:
        if (self.default == "approve_after") != (self.ticks is not None):
            raise ValueError("ticks is required with approve_after and forbidden otherwise")
        return self

    def verdict_for(self, tool: str) -> Verdict:
        """The answer for `tool`, ignoring when it is given."""
        if self.default == "deny" or (self.only is not None and tool not in self.only):
            return Verdict.DENY
        return Verdict.APPROVE


class ClockSettings(ContractModel):
    mode: ClockMode
    ratio: Annotated[float, Field(gt=0, description="ratio mode: ticks per wall second")] = 1.0
    lockstep_budget: Annotated[float, Field(gt=0, description="wall seconds")] = 2.0
    max_catchup_ticks: Annotated[int, Field(ge=0)] = 10


class ProviderRoute(ContractModel):
    """Where the gateway sends an alias (decisions-m1 9). `key_env` names the gateway's
    environment variable holding the key; the key itself never appears in a profile."""

    base_url: Annotated[str, Field(pattern=r"^https?://\S+$", description="OpenAI-compatible /v1")]
    model: Annotated[str, Field(min_length=1, max_length=128)]
    key_env: Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_]{0,63}$")] | None = None


class Budget(ContractModel):
    """Token budget the gateway enforces; past either, it answers 402."""

    incident_tokens: Annotated[int, Field(gt=0)]
    run_tokens: Annotated[int, Field(gt=0)]


class RunConfig(ContractModel):
    """A run profile (`profiles/*.json`): how an episode is played."""

    clock: ClockSettings
    crew: Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]{0,31}$", description="e.g. crew-xo")]
    live_stations: Annotated[list[StationName], Field(min_length=1)]
    drive: DriveMode
    captain: Captain
    captain_policy: CaptainPolicy | None = None
    seed: Seed | None = None
    models: dict[Alias, ProviderRoute]
    budget: Budget

    @model_validator(mode="after")
    def _required_aliases(self) -> Self:
        missing = {"triage", "summary"} - self.models.keys()
        if missing:
            raise ValueError(f"models must map {sorted(missing)}")
        return self


class CreateRun(ContractModel):
    """`POST /runs`. With no seed in the profile the Ship draws one and returns it."""

    episode: EpisodeName
    profile: RunConfig


class RunStatus(ContractModel):
    """`GET /runs/{run_id}`; `outcome` is set once the run has resolved."""

    run_id: UUID
    episode: EpisodeName
    seed: Seed
    captain: Captain
    ship_time: ShipTime
    paused: bool
    bridge_connected: bool
    outcome: Outcome | None = None
    started_at: AwareDatetime


class OrderDecision(ContractModel):
    """`POST /runs/{run_id}/orders/{order_id}/decision`: the captain's answer."""

    verdict: Verdict


class RunStart(ContractModel):
    """`run.start` on `control`: the Holodeck service seeds the world and runs the clock."""

    run_id: UUID
    episode: EpisodeName
    seed: Seed
    clock: ClockSettings
    live_stations: list[StationName]


class RunPause(ContractModel):
    """`run.pause` on `control`: an incident entered `awaiting_captain`."""

    run_id: UUID
    incident_id: IncidentId


class RunResume(ContractModel):
    """`run.resume` on `control`: no incident is awaiting the captain."""

    run_id: UUID
