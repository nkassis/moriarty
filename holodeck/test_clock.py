import asyncio
from collections.abc import Callable

import pytest

from holodeck.clock import Clock, ClockConfig, StationRegistry
from ship.contract.enums import AgentState, ClockMode


class FakeWallClock:
    """Wall time that only moves when the clock sleeps or a test advances it."""

    def __init__(self) -> None:
        self.now = 0.0

    def monotonic(self) -> float:
        return self.now

    async def sleep(self, seconds: float) -> None:
        self.now += seconds
        await asyncio.sleep(0)


class Recorder:
    """Records each emitted tick with the wall time it went out."""

    def __init__(self, wall: FakeWallClock) -> None:
        self.wall = wall
        self.ticks: list[tuple[int, float]] = []
        self.on_tick: Callable[[int], None] = lambda tick: None

    async def __call__(self, tick: int) -> None:
        self.ticks.append((tick, self.wall.now))
        self.on_tick(tick)

    @property
    def numbers(self) -> list[int]:
        return [tick for tick, _ in self.ticks]

    def time_of(self, tick: int) -> float:
        return dict(self.ticks)[tick]


def make_clock(config: ClockConfig, **kwargs: object) -> tuple[Clock, Recorder, FakeWallClock]:
    wall = FakeWallClock()
    recorder = Recorder(wall)
    clock = Clock(config, recorder, wall=wall, **kwargs)  # type: ignore[arg-type]
    return clock, recorder, wall


LOCKSTEP = ClockConfig(mode=ClockMode.LOCKSTEP)
RATIO = ClockConfig(mode=ClockMode.RATIO)


async def test_first_tick_is_one_and_ticks_are_contiguous() -> None:
    clock, recorder, _ = make_clock(LOCKSTEP)
    await clock.run(5)
    assert recorder.numbers == [1, 2, 3, 4, 5]
    assert clock.ship_time == 5


async def test_lockstep_with_no_stations_honours_min_interval() -> None:
    clock, recorder, wall = make_clock(LOCKSTEP)
    await clock.run(3)
    gaps = [b - a for (_, a), (_, b) in zip(recorder.ticks, recorder.ticks[1:], strict=False)]
    assert all(gap == pytest.approx(LOCKSTEP.min_interval) for gap in gaps)
    assert wall.now == pytest.approx(3 * LOCKSTEP.min_interval)
    assert clock.missed == {}


async def test_lockstep_advances_when_every_station_is_idle_after_the_tick() -> None:
    stations = StationRegistry()
    clock, recorder, wall = make_clock(LOCKSTEP, stations=stations)
    recorder.on_tick = lambda tick: [
        stations.report(name, AgentState.IDLE, tick) for name in ("ops", "security")
    ]
    await clock.run(3)
    assert recorder.numbers == [1, 2, 3]
    assert wall.now == pytest.approx(3 * LOCKSTEP.min_interval)
    assert clock.missed == {}


async def test_lockstep_idle_before_the_tick_does_not_count() -> None:
    stations = StationRegistry()
    clock, recorder, _ = make_clock(LOCKSTEP, stations=stations)
    recorder.on_tick = lambda tick: stations.report("ops", AgentState.IDLE, tick - 1)
    await clock.run(2)
    assert clock.missed == {1: frozenset({"ops"}), 2: frozenset({"ops"})}


async def test_lockstep_advances_on_budget_and_records_missed_stations() -> None:
    stations = StationRegistry()
    clock, recorder, _ = make_clock(LOCKSTEP, stations=stations)

    def report(tick: int) -> None:
        stations.report("ops", AgentState.IDLE, tick)
        stations.report("science", AgentState.THINKING, tick)

    recorder.on_tick = report
    await clock.run(2)
    assert recorder.time_of(2) - recorder.time_of(1) == pytest.approx(LOCKSTEP.budget)
    assert clock.missed == {1: frozenset({"science"}), 2: frozenset({"science"})}


async def test_ratio_emits_k_ticks_per_wall_second() -> None:
    clock, recorder, _ = make_clock(ClockConfig(mode=ClockMode.RATIO, ratio=4.0))
    await clock.run(8)
    assert recorder.numbers == list(range(1, 9))
    assert recorder.time_of(8) == pytest.approx(2.0, abs=0.01)


async def test_ratio_catches_up_without_skipping_and_caps_the_catch_up() -> None:
    clock, recorder, wall = make_clock(RATIO)

    def stall(tick: int) -> None:
        if tick == 1:
            wall.now += 30.0

    recorder.on_tick = stall
    await clock.run(12)
    assert recorder.numbers == list(range(1, 13))
    burst = [tick for tick, at in recorder.ticks if at == pytest.approx(31.0, abs=0.01)]
    assert burst == list(range(2, 2 + RATIO.max_catchup_ticks))
    assert clock.dropped_ticks == 30 - RATIO.max_catchup_ticks  # owed: ticks 2 to 31


async def test_ratio_does_not_count_wall_time_spent_paused() -> None:
    wall_holder: list[FakeWallClock] = []

    def awaiting() -> bool:
        return 1.0 <= wall_holder[0].now < 4.0

    clock, recorder, wall = make_clock(RATIO, awaiting_captain=awaiting)
    wall_holder.append(wall)
    await clock.run(2)
    assert clock.paused_wall == pytest.approx(3.0, abs=0.01)
    assert recorder.time_of(2) == pytest.approx(5.0, abs=0.01)


async def test_lockstep_records_paused_wall_time() -> None:
    wall_holder: list[FakeWallClock] = []

    def awaiting() -> bool:
        return 0.5 <= wall_holder[0].now < 2.5

    clock, recorder, wall = make_clock(LOCKSTEP, awaiting_captain=awaiting)
    wall_holder.append(wall)
    recorder.on_tick = lambda tick: setattr(wall, "now", wall.now + 0.5) if tick == 1 else None
    await clock.run(2)
    assert recorder.numbers == [1, 2]
    assert clock.paused_wall == pytest.approx(2.0 - LOCKSTEP.min_interval, abs=0.01)
