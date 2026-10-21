"""Contract enums. `docs/vocabulary.md` is canonical; `test_enums.py` fails if the two differ."""

from enum import StrEnum


class AgentState(StrEnum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    STANDBY = "standby"


class IncidentState(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    ACTING = "acting"
    AWAITING_CAPTAIN = "awaiting_captain"
    CLOSED = "closed"


class Outcome(StrEnum):
    WIN = "win"
    PARTIAL = "partial"
    FAIL = "fail"
    ESCALATED = "escalated"


class CommsKind(StrEnum):
    REQUEST = "request"
    REPORT = "report"
    ACK = "ack"
    ORDER = "order"
    ESCALATION = "escalation"
    SYSTEM = "system"


class Division(StrEnum):
    COMMAND = "command"
    OPS = "ops"
    SCIENCE = "science"


class ReportClaim(StrEnum):
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CANNOT_RESOLVE = "cannot_resolve"


class DriveMode(StrEnum):
    LOCAL = "local"
    REMOTE = "remote"


class ClockMode(StrEnum):
    LOCKSTEP = "lockstep"
    RATIO = "ratio"


class ToolError(StrEnum):
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    STALE = "stale"
    PARTIAL = "partial"
    REQUIRES_AUTHORIZATION = "requires_authorization"
    NOT_ALLOWED = "not_allowed"


class FaultKind(StrEnum):
    UNAVAILABLE = "unavailable"
    STALE = "stale"
    TRANSIENT = "transient"
    SILENT = "silent"


class FaultSource(StrEnum):
    BEAT = "beat"
    CHAOS = "chaos"
    DIRECTOR = "director"


class Source(StrEnum):
    """The ship system that produced a reading; the same names as the MCP servers."""

    SENSORS = "sensors"
    MANIFEST = "manifest"
    BULKHEADS = "bulkheads"
    SECURITY = "security"
    SICKBAY = "sickbay"
    ENGINEERING = "engineering"
    LIBRARIAN = "librarian"
    COMMS = "comms"


class PersonKind(StrEnum):
    CREW = "crew"
    PASSENGER = "passenger"
    UNLISTED = "unlisted"


CONTRACT_ENUMS: tuple[type[StrEnum], ...] = (
    AgentState,
    IncidentState,
    Outcome,
    CommsKind,
    Division,
    ReportClaim,
    DriveMode,
    ClockMode,
    ToolError,
    FaultKind,
    FaultSource,
    Source,
    PersonKind,
)
