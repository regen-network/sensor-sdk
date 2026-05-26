"""Smoke test — proves the package imports and the CI pipeline is wired up."""

import regen_sensor_sdk


def test_version_is_defined():
    assert regen_sensor_sdk.__version__ == "0.0.0"
