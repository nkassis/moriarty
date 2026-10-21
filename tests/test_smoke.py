import importlib

import pytest


@pytest.mark.parametrize(
    "module",
    [
        "holodeck",
        "holodeck.clock",
        "holodeck.run",
        "holodeck.world",
        "ship",
        "ship.bus",
        "ship.bus.messaging",
        "ship.bus.topology",
        "ship.contract.generate",
        "ship.relay",
        "ship.telemetry",
        "ship.world",
    ],
)
def test_package_imports(module: str) -> None:
    importlib.import_module(module)
