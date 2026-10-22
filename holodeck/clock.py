"""The logical clock: lockstep and ratio modes (docs/decisions-m0.md, decisions 3 and 5 to 9)."""

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Protocol

from ship.contract.enums import AgentState, ClockMode

log = logging.getLogger(__name__)

Emit = Callable[[int], Awaitable[None]]


class WallClock(Protocol):
    def monotonic(self) -> float: ...

    async def sleep(self, seconds: float) -> None: ...


class SystemWallClock:
    def monotonic(self) -> float:
        return time.monotonic()

    async def sleep(self, seconds: float) -> None:
        await asyncio.sleep(seconds)


@dataclass(frozen=True)
class ClockConfig:
    mode: ClockMode
    ratio: float = 1.0  # ratio mode: ticks per wall second
    budget: float = 2.0  # lockstep: wall seconds before a tick advances without every station
    min_interval: float = 0.010  # lockstep: never a hot loop, even with no stations
    max_catchup_ticks: int = 10  # ratio: ticks emitted back to back after a stall
    poll_interval: float = 0.005


@dataclass
class StationRegistry:
    """Stations that report state. A station is idle for tick N only if it reported idle
    after tick N went out."""

    _last: dict[str, tuple[AgentState, int]] = field(default_factory=dict)

    def report(self, station: str, state: AgentState, seen_tick: int) -> None:
        self._last[station] = (state, seen_tick)

    def pending(self, tick: int) -> frozenset[str]:
        """Stations not yet idle for `tick`."""
        return frozenset(
            station
            for station, (state, seen_tick) in self._last.items()
            if state is not AgentState.IDLE or seen_tick < tick
        )


def never_awaiting() -> bool:
    """The `awaiting_captain` predicate; a stub until the Incident Desk exists (M4)."""
    return False


class Clock:
    def __init__(
        self,
        config: ClockConfig,
        emit: Emit,
        *,
        wall: WallClock | None = None,
        stations: StationRegistry | None = None,
        awaiting_captain: Callable[[], bool] = never_awaiting,
    ) -> None:
        self.config = config
        self.stations = stations if stations is not None else StationRegistry()
        self.ship_time = 0
        self.missed: dict[int, frozenset[str]] = {}
        self.paused_wall = 0.0
        self.dropped_ticks = 0
        self._emit = emit
        self._wall = wall if wall is not None else SystemWallClock()
        self._awaiting_captain = awaiting_captain

    async def run(self, ticks: int) -> None:
        """Emit ticks until `ship_time` reaches `ticks`."""
        if self.config.mode is ClockMode.LOCKSTEP:
            await self._run_lockstep(ticks)
        else:
            await self._run_ratio(ticks)

    async def _tick(self) -> None:
        self.ship_time += 1
        await self._emit(self.ship_time)

    async def _wait_while_paused(self) -> float:
        """Sleep while the captain is awaited; return the wall time spent paused."""
        started = self._wall.monotonic()
        while self._awaiting_captain():
            await self._wall.sleep(self.config.poll_interval)
        paused = self._wall.monotonic() - started
        self.paused_wall += paused
        return paused

    async def _run_lockstep(self, ticks: int) -> None:
        while self.ship_time < ticks:
            await self._wait_while_paused()
            await self._tick()
            await self._await_stations(self.ship_time)

    async def _await_stations(self, tick: int) -> None:
        started = self._wall.monotonic()
        while True:
            elapsed = self._wall.monotonic() - started
            pending = self.stations.pending(tick)
            if not pending and elapsed >= self.config.min_interval:
                return
            if elapsed >= self.config.budget:
                self.missed[tick] = pending
                log.info("tick %d advanced on budget; missed: %s", tick, sorted(pending))
                return
            await self._wall.sleep(min(self.config.poll_interval, self.config.budget - elapsed))

    async def _run_ratio(self, ticks: int) -> None:
        period = 1.0 / self.config.ratio
        next_due = self._wall.monotonic() + period
        while self.ship_time < ticks:
            next_due += await self._wait_while_paused()
            now = self._wall.monotonic()
            if now < next_due:
                await self._wall.sleep(min(next_due - now, self.config.poll_interval))
                continue
            owed = int((now - next_due) / period) + 1
            if owed > self.config.max_catchup_ticks:
                dropped = owed - self.config.max_catchup_ticks
                self.dropped_ticks += dropped
                next_due += dropped * period
                log.warning("ratio clock behind by %d ticks; dropped %d", owed, dropped)
            await self._tick()
            next_due += period
