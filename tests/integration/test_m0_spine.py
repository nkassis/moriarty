"""M0 definition of done: a trace with Holodeck, bus and Ship spans; ship_time advances in both
clock modes; a reading stamped under the wrong tick is rejected to lost-hail."""

import asyncio
import re
from uuid import uuid4

import pytest
from aio_pika.abc import AbstractIncomingMessage
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from holodeck.clock import ClockConfig
from holodeck.run import READING_TICK, RunResult, lifeform_mismatch, start_run
from holodeck.world import generate_manifest
from ship.bus.messaging import publish
from ship.contract.enums import ClockMode
from ship.contract.models import CLOCK_TICK_ROUTING_KEY, ClockTick, Event, RawObservation
from tests.integration.conftest import (
    Listener,
    connected,
    running_relay,
    subspace_listener,
    wait_until,
)

pytestmark = pytest.mark.integration

TICKS = 12
TRACEPARENT = re.compile(r"^00-(?P<trace_id>[0-9a-f]{32})-[0-9a-f]{16}-[0-9a-f]{2}$")


async def run_with_relay(
    amqp_url: str, database_url: str, config: ClockConfig
) -> tuple[RunResult, Listener]:
    async with running_relay(amqp_url), subspace_listener(amqp_url) as listener:
        result = await start_run(
            seed=7, config=config, ticks=TICKS, amqp_url=amqp_url, database_url=database_url
        )
        await listener.until(
            lambda: len(listener.alerts) >= 1 and len(ticks_of(listener, result)) >= TICKS
        )
        await asyncio.sleep(0.2)  # anything else in flight would arrive now
    return result, listener


def ticks_of(listener: Listener, result: RunResult) -> list[int]:
    ticks = [ClockTick.model_validate_json(message.body) for message in listener.ticks]
    return [tick.ship_time for tick in ticks if tick.run_id == result.run_id]


def assert_one_event_at_reading_tick(listener: Listener, result: RunResult) -> Event:
    assert len(listener.alerts) == 1
    message = listener.alerts[0]
    event = Event.model_validate_json(message.body)
    assert event.run_id == result.run_id
    assert event.ship_time == READING_TICK
    assert event.wall_time is not None
    assert TRACEPARENT.match(str((message.headers or {}).get("traceparent", "")))
    return event


@pytest.mark.parametrize(
    "config",
    [
        ClockConfig(mode=ClockMode.LOCKSTEP),
        ClockConfig(mode=ClockMode.RATIO, ratio=200.0),
    ],
    ids=["lockstep", "ratio"],
)
async def test_ship_time_advances_and_the_reading_arrives(
    amqp_url: str, database_url: str, spans: InMemorySpanExporter, config: ClockConfig
) -> None:
    result, listener = await run_with_relay(amqp_url, database_url, config)
    assert result.ship_time == TICKS
    assert ticks_of(listener, result) == list(range(1, TICKS + 1))
    assert_one_event_at_reading_tick(listener, result)


def only(spans: list[ReadableSpan], name: str, parent: ReadableSpan | None) -> ReadableSpan:
    """The one span called `name` whose parent is `parent`."""
    parent_id = parent.context.span_id if parent is not None else None
    matches = [
        span
        for span in spans
        if span.name == name and (span.parent.span_id if span.parent else None) == parent_id
    ]
    assert len(matches) == 1, f"{name!r} under {parent.name if parent else None!r}: {matches}"
    return matches[0]


async def test_one_trace_runs_from_the_holodeck_through_the_bus_and_ship_to_a_crew(
    amqp_url: str, database_url: str, spans: InMemorySpanExporter
) -> None:
    result, listener = await run_with_relay(
        amqp_url, database_url, ClockConfig(mode=ClockMode.LOCKSTEP)
    )
    finished = list(spans.get_finished_spans())
    run = only(
        [s for s in finished if (s.attributes or {}).get("run_id") == str(result.run_id)],
        "run",
        None,
    )
    trace = [s for s in finished if s.context.trace_id == run.context.trace_id]

    ticks = [
        s
        for s in trace
        if s.name == "tick" and s.parent and s.parent.span_id == run.context.span_id
    ]
    assert len(ticks) == TICKS
    tick = next(s for s in ticks if (s.attributes or {}).get("ship_time") == READING_TICK)
    emit = only(trace, "emit reading", tick)
    holodeck_publish = only(trace, "publish holodeck", emit)
    relay_consume = only(trace, "consume holodeck.relay", holodeck_publish)
    relay = only(trace, "relay reading", relay_consume)
    subspace_publish = only(trace, "publish subspace", relay)
    crew_consume = only(trace, f"consume {listener.alert_queue}", subspace_publish)

    scopes = {
        span.name: span.instrumentation_scope.name
        for span in (tick, emit, holodeck_publish, relay_consume, relay, subspace_publish)
        if span.instrumentation_scope is not None
    }
    assert scopes == {
        "tick": "holodeck",
        "emit reading": "holodeck",
        "publish holodeck": "ship.bus",
        "consume holodeck.relay": "ship.bus",
        "relay reading": "ship.relay",
        "publish subspace": "ship.bus",
    }
    header = str((listener.alerts[0].headers or {}).get("traceparent", ""))
    match = TRACEPARENT.match(header)
    assert match and int(match["trace_id"], 16) == run.context.trace_id
    assert crew_consume.context.trace_id == run.context.trace_id


async def test_reading_stamped_under_the_wrong_tick_goes_to_lost_hail(amqp_url: str) -> None:
    run_id = uuid4()
    stale = lifeform_mismatch(generate_manifest(seed=7), ship_time=READING_TICK - 1)
    async with connected(amqp_url) as (_, topology), subspace_listener(amqp_url) as listener:
        await topology.lost_hail.purge()
        dead: list[RawObservation] = []
        dead_arrived = asyncio.Event()

        async def on_dead_letter(message: AbstractIncomingMessage) -> None:
            dead.append(RawObservation.model_validate_json(message.body))
            await message.ack()
            dead_arrived.set()

        await topology.lost_hail.consume(on_dead_letter)
        async with running_relay(amqp_url):
            tick = ClockTick(run_id=run_id, ship_time=READING_TICK, mode=ClockMode.LOCKSTEP)
            await publish(
                topology.holodeck, CLOCK_TICK_ROUTING_KEY, tick.model_dump_json().encode()
            )
            await publish(topology.holodeck, stale.routing_key, stale.model_dump_json().encode())
            await wait_until(dead_arrived, lambda: bool(dead))
            await asyncio.sleep(0.2)  # an event wrongly relayed would arrive now

    assert dead == [stale]
    assert listener.alerts == []
    assert len(listener.ticks) == 1
