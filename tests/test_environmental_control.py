"""Tests for environmental control dynamics."""

from src.environmental_control import AIEnvironmentalController


def test_humidity_control_dehumidifies_when_above_setpoint():
    """Controller should open vents when humidity is too high."""
    controller = AIEnvironmentalController()

    # Force high humidity to require dehumidification.
    controller.state.sensors.humidity_percent = 95.0
    controller.state.setpoints.humidity_percent = 65.0

    misting, venting = controller.calculate_humidity_control(
        current=controller.state.sensors.humidity_percent,
        setpoint=controller.state.setpoints.humidity_percent,
        dt=60.0,
    )

    assert misting == 0.0
    assert venting > 0.0
