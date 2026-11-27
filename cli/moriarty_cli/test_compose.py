from pathlib import Path

from moriarty_cli import compose
from ship.contract.enums import DriveMode
from ship.contract.examples import run_config

BASE = compose.base_command(Path("infra/docker-compose.yml"), Path("infra/.env"))


def test_base_command_wraps_the_compose_file_and_env_file() -> None:
    assert BASE == [
        "docker", "compose", "-f", "infra/docker-compose.yml", "--env-file", "infra/.env"
    ]  # fmt: skip


def test_up_selects_the_crew_and_drive_profiles() -> None:
    cmd = compose.up_command(BASE, run_config(drive=DriveMode.REMOTE))
    assert cmd[len(BASE) :] == [
        "--profile", "crew-xo", "--profile", "drive-remote", "up", "-d", "--wait"
    ]  # fmt: skip


def test_down_covers_every_profile_and_drops_volumes_only_when_asked() -> None:
    assert compose.down_command(BASE, volumes=False)[len(BASE) :] == ["--profile", "*", "down"]
    assert compose.down_command(BASE, volumes=True)[-1] == "-v"


def test_logs_takes_an_optional_service_and_follow() -> None:
    assert compose.logs_command(BASE, None, follow=False)[len(BASE) :] == [
        "--profile", "*", "logs"
    ]  # fmt: skip
    assert compose.logs_command(BASE, "rabbitmq", follow=True)[-2:] == ["--follow", "rabbitmq"]


def test_ps_asks_for_json() -> None:
    assert compose.ps_command(BASE)[-4:] == ["ps", "--all", "--format", "json"]
