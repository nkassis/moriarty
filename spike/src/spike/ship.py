"""The ship: one simulated coolant loop, its alerts, and its MCP tools."""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Literal

from mcp.server import MCPServer
from pydantic import BaseModel, ConfigDict

from spike.bus import ALERTS, SENSORS, Bus, connect, now

logger = logging.getLogger("spike.ship")

FAULT_AT = 30
NOMINAL_PRESSURE = 400.0
PRESSURE_FLOOR = 200.0
PRESSURE_FALL = 5.0
PRESSURE_RECOVERY = 10.0
NOMINAL_TEMP = 70.0
TEMP_RISE = 0.2
TEMP_RECOVERY = 1.0
RAISE_BELOW = 340.0
CLEAR_ABOVE = 380.0

ALERT_KEY = "coolant.pressure_low"
PRESSURE = "coolant.pressure_kpa"
TEMP = "coolant.temp_c"
ACTIVE_PUMP = "coolant.active_pump"
PUMPS = ("a", "b")
MCP_PORT = 8000


class SimState(BaseModel):
    """The whole simulated coolant loop."""

    model_config = ConfigDict(frozen=True)

    active_pump: Literal["a", "b"] = "a"
    pump_a_health: Literal["ok", "degraded"] = "ok"
    pressure_kpa: float = NOMINAL_PRESSURE
    temp_c: float = NOMINAL_TEMP
    t: int = 0
    alert_raised: bool = False


class AlertEvent(BaseModel):
    """A pressure alert changing state."""

    model_config = ConfigDict(frozen=True)

    state: Literal["raised", "cleared"]
    value: float
    threshold: float


def step(state: SimState) -> tuple[SimState, AlertEvent | None]:
    """Advance one tick. Returns the new state and the alert change, if there was one."""
    t = state.t + 1
    pump_a_health = "degraded" if t >= FAULT_AT else state.pump_a_health
    if state.active_pump == "a" and pump_a_health == "degraded":
        pressure = max(PRESSURE_FLOOR, state.pressure_kpa - PRESSURE_FALL)
        temp = round(state.temp_c + TEMP_RISE, 1)
    else:
        pressure = min(NOMINAL_PRESSURE, state.pressure_kpa + PRESSURE_RECOVERY)
        temp = round(max(NOMINAL_TEMP, state.temp_c - TEMP_RECOVERY), 1)

    alert = None
    if not state.alert_raised and pressure < RAISE_BELOW:
        alert = AlertEvent(state="raised", value=pressure, threshold=RAISE_BELOW)
    elif state.alert_raised and pressure > CLEAR_ABOVE:
        alert = AlertEvent(state="cleared", value=pressure, threshold=CLEAR_ABOVE)

    alert_raised = alert.state == "raised" if alert else state.alert_raised
    new_state = state.model_copy(
        update={
            "pump_a_health": pump_a_health,
            "pressure_kpa": pressure,
            "temp_c": temp,
            "t": t,
            "alert_raised": alert_raised,
        }
    )
    return new_state, alert


def readings(state: SimState) -> dict[str, tuple[float, str]]:
    """Return every sensor's current value and unit."""
    return {PRESSURE: (state.pressure_kpa, "kPa"), TEMP: (state.temp_c, "C")}


@dataclass
class Ship:
    """Holds the current state, shared by the tick loop and the MCP tools."""

    state: SimState


def read_sensor(state: SimState, name: str) -> dict[str, Any]:
    """Return one sensor's value and unit, or an error."""
    if name not in readings(state):
        return {"error": f"unknown sensor {name!r}; known: {sorted(readings(state))}"}
    value, unit = readings(state)[name]
    return {"name": name, "value": value, "unit": unit}


def system_status(state: SimState, system: str) -> dict[str, Any]:
    """Return the status of a system, or an error."""
    if system != "coolant":
        return {"error": f"unknown system {system!r}; known: ['coolant']"}
    health = {"a": state.pump_a_health, "b": "ok"}
    return {
        "active_pump": state.active_pump,
        "pumps": {
            pump: {
                "health": health[pump],
                "mode": "active" if pump == state.active_pump else "standby",
            }
            for pump in PUMPS
        },
        "readings": {name: value for name, (value, _) in readings(state).items()},
    }


def set_control(state: SimState, name: str, value: str) -> tuple[SimState, dict[str, Any]]:
    """Apply a control change. Returns the new state and the tool result."""
    if name != ACTIVE_PUMP:
        return state, {"error": f"unknown control {name!r}; known: ['{ACTIVE_PUMP}']"}
    if value not in PUMPS:
        return state, {"error": f"invalid value {value!r} for {name}; allowed: {list(PUMPS)}"}
    return state.model_copy(update={"active_pump": value}), {"name": name, "value": value}


def build_server(ship: Ship) -> MCPServer:
    """Build the MCP server over the shared ship state."""
    server = MCPServer("ship", log_level="WARNING")

    @server.tool(name="read_sensor", description="Read the current value of one sensor.")
    def read_sensor_tool(name: str) -> dict[str, Any]:
        return read_sensor(ship.state, name)

    @server.tool(name="system_status", description="Get the status of a ship system.")
    def system_status_tool(system: str) -> dict[str, Any]:
        return system_status(ship.state, system)

    @server.tool(name="set_control", description="Change a ship control setting.")
    def set_control_tool(name: str, value: str) -> dict[str, Any]:
        ship.state, result = set_control(ship.state, name, value)
        return result

    return server


async def publish_tick(bus: Bus, state: SimState, alert: AlertEvent | None) -> None:
    """Publish this tick's readings and alert change."""
    ts = now()
    for sensor, (value, unit) in readings(state).items():
        await bus.publish(SENSORS, {"ts": ts, "sensor": sensor, "value": value, "unit": unit})
    if alert:
        logger.info("alert %s value=%s", alert.state, alert.value)
        await bus.publish(
            ALERTS, {"ts": ts, "key": ALERT_KEY, "sensor": PRESSURE, **alert.model_dump()}
        )


async def tick_loop(ship: Ship, bus: Bus) -> None:
    """Step the simulation once per second."""
    while True:
        await asyncio.sleep(1)
        ship.state, alert = step(ship.state)
        await publish_tick(bus, ship.state, alert)


async def main() -> None:
    """Run the tick loop and the MCP server together."""
    logging.basicConfig(level=logging.INFO)
    bus = await connect()
    ship = Ship(SimState())
    server = build_server(ship)
    logger.info("ship started; fault at t=%s", FAULT_AT)
    async with asyncio.TaskGroup() as group:
        group.create_task(tick_loop(ship, bus))
        group.create_task(server.run_streamable_http_async(host="0.0.0.0", port=MCP_PORT))


if __name__ == "__main__":
    asyncio.run(main())
