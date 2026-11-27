from pathlib import Path

from moriarty_cli.envfile import parse_env_file, resolve


def test_parse_skips_comments_and_strips_quotes(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("# comment\n\nA=1\nB=\"two words\"\nexport C='3'\nnot a pair\nD=x=y\n")
    assert parse_env_file(env) == {"A": "1", "B": "two words", "C": "3", "D": "x=y"}


def test_missing_file_is_empty(tmp_path: Path) -> None:
    assert parse_env_file(tmp_path / "absent") == {}


def test_environment_wins_over_file(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("KEY=from-file\nOTHER=file-only\n")
    assert resolve("KEY", env, {"KEY": "from-env"}) == "from-env"
    assert resolve("OTHER", env, {}) == "file-only"
    assert resolve("NONE", env, {}) is None
