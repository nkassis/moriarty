"""`docker compose` command lines for the local stack."""

from pathlib import Path

from ship.contract.runs import RunConfig

ALL_PROFILES = "*"


def base_command(compose_file: Path, env_file: Path) -> list[str]:
    return ["docker", "compose", "-f", str(compose_file), "--env-file", str(env_file)]


def compose_profiles(profile: RunConfig) -> list[str]:
    """Compose profiles selected by a run profile: the crew, then the drive mode."""
    return [profile.crew, f"drive-{profile.drive.value}"]


def profile_flags(profiles: list[str]) -> list[str]:
    flags: list[str] = []
    for name in profiles:
        flags += ["--profile", name]
    return flags


def up_command(base: list[str], profile: RunConfig) -> list[str]:
    return [*base, *profile_flags(compose_profiles(profile)), "up", "-d", "--wait"]


def down_command(base: list[str], *, volumes: bool) -> list[str]:
    # Every profile, so crew and drive services started by any profile stop too.
    return [*base, *profile_flags([ALL_PROFILES]), "down", *(["-v"] if volumes else [])]


def logs_command(base: list[str], service: str | None, *, follow: bool) -> list[str]:
    return [
        *base,
        *profile_flags([ALL_PROFILES]),
        "logs",
        *(["--follow"] if follow else []),
        *([service] if service else []),
    ]


def ps_command(base: list[str]) -> list[str]:
    return [*base, *profile_flags([ALL_PROFILES]), "ps", "--all", "--format", "json"]
