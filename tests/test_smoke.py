import importlib

import pytest


@pytest.mark.parametrize(
    "module", ["holodeck", "ship", "ship.bus", "ship.world", "ship.contract.generate"]
)
def test_package_imports(module: str) -> None:
    importlib.import_module(module)
