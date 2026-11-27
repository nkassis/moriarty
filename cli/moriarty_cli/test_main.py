import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from moriarty_cli import main
from moriarty_cli.checks import Check
from moriarty_cli.paths import PROFILES_DIR

runner = CliRunner()


@pytest.fixture
def ran(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Point the CLI at a temp infra/.env and record compose commands instead of running them."""
    env = tmp_path / ".env"
    env.write_text("")
    monkeypatch.setattr(main, "ENV_FILE", env)
    calls: list[list[str]] = []

    def execute(cmd: list[str]) -> int:
        calls.append(cmd)
        return 0

    monkeypatch.setattr(main, "execute", execute)
    return calls


def tail(cmd: list[str]) -> list[str]:
    return cmd[len(main.base_command()) :]


def test_up_defaults_to_the_demo_profile(ran: list[list[str]]) -> None:
    result = runner.invoke(main.app, ["up"])
    assert result.exit_code == 0
    assert tail(ran[0]) == [
        "--profile", "crew-xo", "--profile", "drive-remote", "up", "-d", "--wait"
    ]  # fmt: skip


def test_up_takes_a_profile_file(ran: list[list[str]]) -> None:
    assert runner.invoke(main.app, ["up", str(PROFILES_DIR / "eval.json")]).exit_code == 0
    assert "drive-local" in ran[0]


def test_up_refuses_an_invalid_profile(ran: list[list[str]], tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    result = runner.invoke(main.app, ["up", str(bad)])
    assert result.exit_code == 1
    assert "bad.json" in result.output
    assert ran == []


def test_commands_need_infra_env(ran: list[list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "ENV_FILE", Path("/nonexistent/.env"))
    for args in (["up"], ["down"], ["logs"], ["status"]):
        result = runner.invoke(main.app, args)
        assert result.exit_code == 1, args
        assert "cp infra/.env.example infra/.env" in result.output
    assert ran == []


def test_down_and_down_with_volumes(ran: list[list[str]]) -> None:
    assert runner.invoke(main.app, ["down"]).exit_code == 0
    assert runner.invoke(main.app, ["down", "-v"]).exit_code == 0
    assert tail(ran[0]) == ["--profile", "*", "down"]
    assert tail(ran[1]) == ["--profile", "*", "down", "-v"]


def test_logs_for_one_service_following(ran: list[list[str]]) -> None:
    assert runner.invoke(main.app, ["logs", "rabbitmq", "-f"]).exit_code == 0
    assert tail(ran[0])[-3:] == ["logs", "--follow", "rabbitmq"]


def test_up_passes_compose_failures_through(
    ran: list[list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(main, "execute", lambda cmd: 17)
    assert runner.invoke(main.app, ["up"]).exit_code == 17


def ps_output(*rows: dict[str, str]) -> str:
    return "\n".join(json.dumps(row) for row in rows)


def test_status_lists_services_then_reachability(
    ran: list[list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    rows = ps_output({"Service": "rabbitmq", "State": "running", "Health": "healthy"})
    monkeypatch.setattr(main, "capture", lambda cmd: (0, rows))
    reach = [Check("rabbitmq (amqp)", True, "connected"), Check("postgres (sql)", True, "ok")]
    monkeypatch.setattr(main, "reachability_checks", lambda env: reach)
    result = runner.invoke(main.app, ["status"])
    assert result.exit_code == 0
    assert [line.split()[1] for line in result.output.splitlines()] == [
        "rabbitmq", "rabbitmq", "postgres"
    ]  # fmt: skip


def test_status_fails_when_anything_is_unhealthy(
    ran: list[list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    rows = ps_output({"Service": "postgres", "State": "running", "Health": "unhealthy"})
    monkeypatch.setattr(main, "capture", lambda cmd: (0, rows))
    monkeypatch.setattr(main, "reachability_checks", lambda env: [])
    result = runner.invoke(main.app, ["status"])
    assert result.exit_code == 1
    assert result.output.startswith("FAIL postgres")


def test_status_says_when_the_stack_is_down(
    ran: list[list[str]], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(main, "capture", lambda cmd: (0, ""))
    result = runner.invoke(main.app, ["status"])
    assert result.exit_code == 1
    assert "moriarty up" in result.output


def test_doctor_exits_nonzero_on_any_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    checks = [Check("python", True, "3.14.3"), Check("uv", False, "not found", "install uv")]
    monkeypatch.setattr(main, "run_doctor", lambda *args: checks)
    result = runner.invoke(main.app, ["doctor"])
    assert result.exit_code == 1
    assert len(result.output.splitlines()) == 2


def test_doctor_passes_profile_and_drive(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[tuple[object, ...]] = []
    monkeypatch.setattr(main, "run_doctor", lambda *args: seen.append(args) or [])
    profile = PROFILES_DIR / "eval.json"
    result = runner.invoke(main.app, ["doctor", "--profile", str(profile), "--drive", "remote"])
    assert result.exit_code == 0
    assert seen[0][1] == profile
    assert seen[0][4] == main.DriveMode.REMOTE


def test_schema_regenerates_the_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[bool] = []
    monkeypatch.setattr(main.generate, "main", lambda: called.append(True))
    result = runner.invoke(main.app, ["schema"])
    assert result.exit_code == 0 and called == [True]
    assert "ship/contract/schema/" in result.output
