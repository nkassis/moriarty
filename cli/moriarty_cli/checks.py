"""One pass-or-fail line per check, shared by `doctor` and `status`."""

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str
    fix: str | None = None

    def line(self) -> str:
        mark = "ok  " if self.ok else "FAIL"
        text = f"{mark} {self.name:<16} {self.detail}"
        if not self.ok and self.fix:
            text += f"  -> {self.fix}"
        return text


def capture(cmd: list[str], timeout: float = 15.0) -> tuple[int, str]:
    """Run `cmd`, returning its exit code and stripped stdout; a missing binary is 127."""
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError:
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""
    return done.returncode, done.stdout.strip()
