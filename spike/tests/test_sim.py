"""The step function: no broker, no model."""

from spike.ship import (
    CLEAR_ABOVE,
    FAULT_AT,
    NOMINAL_PRESSURE,
    NOMINAL_TEMP,
    RAISE_BELOW,
    AlertEvent,
    SimState,
    step,
)


def run(state: SimState, ticks: int) -> tuple[SimState, list[AlertEvent]]:
    """Step the simulation and collect the alert changes."""
    alerts = []
    for _ in range(ticks):
        state, alert = step(state)
        if alert:
            alerts.append(alert)
    return state, alerts


def test_healthy_stays_nominal() -> None:
    state, alerts = run(SimState(), FAULT_AT - 1)

    assert state.pump_a_health == "ok"
    assert state.pressure_kpa == NOMINAL_PRESSURE
    assert state.temp_c == NOMINAL_TEMP
    assert alerts == []


def test_fault_drops_pressure_and_raises_alert_once() -> None:
    state, alerts = run(SimState(), FAULT_AT + 30)

    assert state.pump_a_health == "degraded"
    assert state.pressure_kpa < RAISE_BELOW
    assert state.temp_c > NOMINAL_TEMP
    assert [alert.state for alert in alerts] == ["raised"]
    assert alerts[0].value < RAISE_BELOW
    assert alerts[0].threshold == RAISE_BELOW


def test_switching_to_pump_b_recovers_and_clears_once() -> None:
    faulted, _ = run(SimState(), FAULT_AT + 30)

    state, alerts = run(faulted.model_copy(update={"active_pump": "b"}), 30)

    assert state.pressure_kpa == NOMINAL_PRESSURE
    assert state.temp_c < faulted.temp_c
    assert [alert.state for alert in alerts] == ["cleared"]
    assert alerts[0].value > CLEAR_ABOVE
