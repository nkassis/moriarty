"""Repo paths the CLI works from, whatever the current directory."""

from pathlib import Path

from moriarty_cli import REPO_ROOT

COMPOSE_FILE: Path = REPO_ROOT / "infra" / "docker-compose.yml"
ENV_FILE: Path = REPO_ROOT / "infra" / ".env"
ENV_EXAMPLE: Path = REPO_ROOT / "infra" / ".env.example"
PROFILES_DIR: Path = REPO_ROOT / "profiles"
DEFAULT_PROFILE: Path = PROFILES_DIR / "demo.json"
