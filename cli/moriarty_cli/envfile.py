"""Read `infra/.env`-style files. Values already in the environment win over the file."""

import os
from collections.abc import Mapping
from pathlib import Path


def parse_env_file(path: Path) -> dict[str, str]:
    """`KEY=value` lines; blank lines and `#` comments skipped, one layer of quotes stripped."""
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.removeprefix("export ").partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def resolve(key: str, env_file: Path, environ: Mapping[str, str] | None = None) -> str | None:
    """The value of `key`: the environment first, then the file, else None."""
    env: Mapping[str, str] = os.environ if environ is None else environ
    if key in env:
        return env[key]
    return parse_env_file(env_file).get(key)
