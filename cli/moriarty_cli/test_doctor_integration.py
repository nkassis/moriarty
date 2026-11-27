"""`moriarty doctor` as installed: the console script, a real Docker daemon, a stand-in Ollama."""

import os
import shutil
import subprocess

import pytest

from moriarty_cli.paths import PROFILES_DIR

pytestmark = pytest.mark.integration

CHECKS = [
    "python", "uv", "docker", "ollama", "infra/.env", "profile",
    "git hooks", "trufflehog", "git user.email",
]  # fmt: skip


def test_doctor_prints_one_line_per_check(ollama_url: str, tmp_path: object) -> None:
    moriarty = shutil.which("moriarty")
    assert moriarty, "moriarty is not installed; uv sync --all-packages"
    env = os.environ | {"OLLAMA_URL": ollama_url}
    done = subprocess.run(
        [moriarty, "doctor", "--profile", str(PROFILES_DIR / "eval.json")],
        capture_output=True,
        text=True,
        env=env,
        cwd=tmp_path,  # the CLI finds the repo from its own install, not the working directory
        check=False,
    )
    lines = done.stdout.splitlines()
    names = [line[5:21].rstrip() for line in lines]
    assert names == CHECKS, done.stdout + done.stderr
    assert all(line[:4] in ("ok  ", "FAIL") for line in lines)
    by_name = dict(zip(names, lines, strict=True))
    for name in ("python", "uv", "docker", "ollama", "profile"):
        assert by_name[name].startswith("ok"), by_name[name]
    assert done.returncode == (0 if all(line.startswith("ok") for line in lines) else 1)
