"""`moriarty`: bring the local stack up and down, check it, and regenerate the contract schemas."""

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from moriarty_cli import REPO_ROOT, compose
from moriarty_cli.checks import Check, capture
from moriarty_cli.doctor import run_doctor
from moriarty_cli.paths import COMPOSE_FILE, DEFAULT_PROFILE, ENV_EXAMPLE, ENV_FILE
from moriarty_cli.profile import ProfileError, load_profile
from moriarty_cli.status import parse_ps, reachability_checks, service_check
from ship.contract import generate
from ship.contract.enums import DriveMode

app = typer.Typer(no_args_is_help=True, add_completion=False, help=__doc__)

ProfileArg = Annotated[Path, typer.Argument(help="Run profile (RunConfig JSON).", dir_okay=False)]


def execute(cmd: list[str]) -> int:
    """Run `cmd` with the terminal attached and return its exit code."""
    return subprocess.run(cmd, check=False).returncode


def base_command() -> list[str]:
    return compose.base_command(COMPOSE_FILE, ENV_FILE)


def require_env_file() -> None:
    if not ENV_FILE.is_file():
        typer.echo("infra/.env is missing: cp infra/.env.example infra/.env", err=True)
        raise typer.Exit(1)


def echo_checks(checks: list[Check]) -> bool:
    for check in checks:
        typer.echo(check.line())
    return all(check.ok for check in checks)


@app.command()
def up(profile: ProfileArg = DEFAULT_PROFILE) -> None:
    """Start the stack with the compose profiles for the run profile's crew and drive."""
    require_env_file()
    try:
        config = load_profile(profile)
    except ProfileError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    raise typer.Exit(execute(compose.up_command(base_command(), config)))


@app.command()
def down(
    volumes: Annotated[bool, typer.Option("--volumes", "-v", help="Drop volumes too.")] = False,
) -> None:
    """Stop the stack, every compose profile included."""
    require_env_file()
    raise typer.Exit(execute(compose.down_command(base_command(), volumes=volumes)))


@app.command()
def status() -> None:
    """Service health from compose, then RabbitMQ and Postgres reachability."""
    require_env_file()
    code, out = capture(compose.ps_command(base_command()))
    if code != 0:
        typer.echo("docker compose ps failed; run `moriarty doctor`", err=True)
        raise typer.Exit(1)
    services = [service_check(row) for row in parse_ps(out)]
    if not services:
        typer.echo("stack is down: moriarty up")
        raise typer.Exit(1)
    ok = echo_checks(services + reachability_checks(ENV_FILE))
    raise typer.Exit(0 if ok else 1)


@app.command()
def logs(
    service: Annotated[str | None, typer.Argument(help="One service; all when omitted.")] = None,
    follow: Annotated[bool, typer.Option("--follow", "-f", help="Keep streaming.")] = False,
) -> None:
    """Compose logs for the stack or one service."""
    require_env_file()
    raise typer.Exit(execute(compose.logs_command(base_command(), service, follow=follow)))


@app.command()
def doctor(
    profile: Annotated[
        Path, typer.Option(help="Run profile to validate and check against.", dir_okay=False)
    ] = DEFAULT_PROFILE,
    drive: Annotated[
        DriveMode | None, typer.Option(help="Drive mode to check for; the profile's by default.")
    ] = None,
) -> None:
    """Check tools, services, config and the local git harness; one line per check."""
    checks = run_doctor(REPO_ROOT, profile, ENV_FILE, ENV_EXAMPLE, drive)
    raise typer.Exit(0 if echo_checks(checks) else 1)


@app.command()
def schema() -> None:
    """Regenerate the contract JSON Schemas (python -m ship.contract.generate)."""
    generate.main()
    shown = generate.SCHEMA_DIR.relative_to(REPO_ROOT)
    typer.echo(f"wrote {len(generate.MODELS)} schemas to {shown}/")
