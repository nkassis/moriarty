"""Start a run: seed the world, drive the clock, emit the hard-coded M0 reading at tick 10."""

import argparse
import asyncio
import logging
import os
from dataclasses import dataclass
from uuid import UUID, uuid4

import aio_pika
from opentelemetry import trace
from psycopg import AsyncConnection

from holodeck.clock import Clock, ClockConfig, StationRegistry
from holodeck.world import Person, apply_world_sql, expected_in_section, seed_manifest
from ship.bus.messaging import publish
from ship.bus.topology import Topology, declare_topology
from ship.contract.enums import ClockMode, Source
from ship.contract.models import (
    CLOCK_TICK_ROUTING_KEY,
    LIFEFORM_MISMATCH_ROUTING_KEY,
    ClockTick,
    LifeformMismatch,
    RawObservation,
)
from ship.telemetry import setup_tracing

log = logging.getLogger(__name__)
tracer = trace.get_tracer("holodeck")

READING_TICK = 10


@dataclass(frozen=True)
class RunResult:
    run_id: UUID
    ship_time: int
    missed: dict[int, frozenset[str]]


def lifeform_mismatch(people: list[Person], ship_time: int) -> RawObservation:
    """The one M0 reading: an unlisted lifeform in the first manifest section."""
    deck, section = people[0].deck, people[0].section
    expected = expected_in_section(people, deck, section)
    observed = LifeformMismatch(
        deck=deck, section=section, expected_count=expected, detected_count=expected + 1
    )
    return RawObservation(
        routing_key=LIFEFORM_MISMATCH_ROUTING_KEY,
        source=Source.SENSORS,
        severity=3,
        observed=observed.model_dump(),
        ship_time=ship_time,
    )


class Run:
    def __init__(self, run_id: UUID, config: ClockConfig, topology: Topology) -> None:
        self.run_id = run_id
        self.config = config
        self.topology = topology
        self.people: list[Person] = []

    async def emit(self, ship_time: int) -> None:
        """One tick: publish it, then any reading due at it, under the tick's span."""
        with tracer.start_as_current_span("tick", attributes={"ship_time": ship_time}):
            tick = ClockTick(run_id=self.run_id, ship_time=ship_time, mode=self.config.mode)
            await publish(
                self.topology.holodeck, CLOCK_TICK_ROUTING_KEY, tick.model_dump_json().encode()
            )
            if ship_time == READING_TICK:
                await self.emit_reading(lifeform_mismatch(self.people, ship_time))

    async def emit_reading(self, reading: RawObservation) -> None:
        with tracer.start_as_current_span(
            "emit reading", attributes={"routing_key": reading.routing_key}
        ):
            await publish(
                self.topology.holodeck, reading.routing_key, reading.model_dump_json().encode()
            )


async def start_run(
    *,
    seed: int,
    config: ClockConfig,
    ticks: int,
    amqp_url: str,
    database_url: str,
    stations: StationRegistry | None = None,
) -> RunResult:
    """Run `ticks` ticks of a seeded world. One trace per run, rooted here."""
    run_id = uuid4()
    with tracer.start_as_current_span(
        "run", attributes={"run_id": str(run_id), "seed": seed, "clock_mode": config.mode.value}
    ):
        connection = await aio_pika.connect_robust(amqp_url)
        async with connection, await AsyncConnection.connect(database_url) as db:
            await apply_world_sql(db)
            channel = await connection.channel()
            run = Run(run_id, config, await declare_topology(channel))
            run.people = await seed_manifest(db, run_id, seed)
            await db.commit()
            clock = Clock(config, run.emit, stations=stations)
            await clock.run(ticks)
    log.info("run %s ended at ship_time %d", run_id, clock.ship_time)
    return RunResult(run_id=run_id, ship_time=clock.ship_time, missed=clock.missed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a Holodeck run.")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--mode", type=ClockMode, choices=list(ClockMode), default=ClockMode.RATIO)
    parser.add_argument("--ratio", type=float, default=1.0, help="ratio mode: ticks per second")
    parser.add_argument("--ticks", type=int, default=15)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    provider = setup_tracing("holodeck")
    config = ClockConfig(mode=args.mode, ratio=args.ratio)
    asyncio.run(
        start_run(
            seed=args.seed,
            config=config,
            ticks=args.ticks,
            amqp_url=os.environ["AMQP_URL"],
            database_url=os.environ["DATABASE_URL"],
        )
    )
    provider.shutdown()


if __name__ == "__main__":
    main()
