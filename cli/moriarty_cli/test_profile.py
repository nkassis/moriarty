from pathlib import Path

import pytest

from moriarty_cli.paths import PROFILES_DIR
from moriarty_cli.profile import ProfileError, load_profile
from ship.contract.enums import Captain, ClockMode, DriveMode


def test_demo_profile_plays_ratio_on_a_remote_model_with_a_human_captain() -> None:
    demo = load_profile(PROFILES_DIR / "demo.json")
    assert (demo.clock.mode, demo.clock.ratio) == (ClockMode.RATIO, 2.0)
    assert demo.drive is DriveMode.REMOTE
    assert demo.captain is Captain.HITL
    assert demo.models["triage"].model == "claude-sonnet-5-5"  # decisions-m1 1
    assert demo.live_stations == ["xo", "ops", "security"]  # decisions-m1 2
    assert demo.seed is None


def test_eval_profile_is_lockstep_on_local_ollama_with_the_scripted_captain() -> None:
    profile = load_profile(PROFILES_DIR / "eval.json")
    assert profile.clock.mode is ClockMode.LOCKSTEP
    assert profile.drive is DriveMode.LOCAL
    assert profile.captain is Captain.AUTO
    assert {route.key_env for route in profile.models.values()} == {None}
    assert profile.models["triage"].model == "gpt-oss:20b"  # decisions-m1 4


def test_invalid_profile_names_the_field(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text((PROFILES_DIR / "eval.json").read_text().replace('"local"', '"warp"'))
    with pytest.raises(ProfileError, match=r"bad\.json: drive: "):
        load_profile(bad)


def test_missing_profile_is_a_profile_error(tmp_path: Path) -> None:
    with pytest.raises(ProfileError, match=r"absent\.json"):
        load_profile(tmp_path / "absent.json")
