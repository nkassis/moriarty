"""Run profiles: `profiles/*.json`, validated by `RunConfig` from the contract."""

from pathlib import Path

from pydantic import ValidationError

from ship.contract.runs import RunConfig


class ProfileError(ValueError):
    """A profile file that is missing, not JSON, or not a valid `RunConfig`."""


def load_profile(path: Path) -> RunConfig:
    try:
        text = path.read_text()
    except OSError as exc:
        raise ProfileError(f"{path}: {exc.strerror}") from exc
    try:
        return RunConfig.model_validate_json(text)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "(root)"
        count = exc.error_count()
        more = f" (+{count - 1} more)" if count > 1 else ""
        raise ProfileError(f"{path.name}: {where}: {first['msg']}{more}") from exc
