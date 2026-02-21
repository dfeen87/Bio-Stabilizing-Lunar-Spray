"""
Environmental Control System

AI-regulated dome systems for maintaining optimal growing conditions
over bio-stabilized lunar regolith substrate.

Author: Don Michael Feeney Jr
Based on: Bio-Stabilizing Lunar Spray white paper (April 2025)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
from utils import PhysicalConstants


class ControlMode(Enum):
    """Dome environmental control modes."""

    STANDBY = "Standby"
    CONDITIONING = "Substrate conditioning"
    GROWING = "Active growing"
    EMERGENCY = "Emergency mode"
    MAINTENANCE = "Maintenance"


class AlertLevel(Enum):
    """System alert severity levels."""

    NORMAL = 0
    WARNING = 1
    CRITICAL = 2
    EMERGENCY = 3


@dataclass
class EnvironmentalSetpoints:
    """Target environmental parameters."""

    temperature_c: float = 22.0
    temperature_tolerance: float = 2.0
    humidity_percent: float = 65.0
    humidity_tolerance: float = 10.0
    co2_ppm: float = 800.0
    co2_tolerance: float = 200.0
    o2_percent: float = 20.9
    o2_tolerance: float = 1.0
    light_intensity_umol: float = 300.0  # μmol/m²/s
    photoperiod_hours: float = 16.0


@dataclass
class DomeSensors:
    """Current sensor readings."""

    temperature_c: float = 20.0
    humidity_percent: float = 60.0
    co2_ppm: float = 400.0
    o2_percent: float = 20.9
    light_intensity_umol: float = 0.0
    pressure_pa: float = PhysicalConstants.STANDARD_PRESSURE_PA
    soil_moisture_percent: float = 50.0
    timestamp: float = 0.0


@dataclass
class ControlActions:
    """Actuator control outputs."""

    heater_power_percent: float = 0.0
    cooler_active: bool = False
    misting_rate_ml_min: float = 0.0
    vent_position_percent: float = 0.0
    co2_injection_rate_ml_min: float = 0.0
    led_power_percent: float = 0.0
    circulation_fan_rpm: float = 0.0


@dataclass
class DomeState:
    """Complete dome system state."""

    mode: ControlMode = ControlMode.STANDBY
    sensors: DomeSensors = field(default_factory=DomeSensors)
    setpoints: EnvironmentalSetpoints = field(default_factory=EnvironmentalSetpoints)
    actions: ControlActions = field(default_factory=ControlActions)
    alerts: List[Tuple[AlertLevel, str]] = field(default_factory=list)
    energy_consumption_w: float = 0.0


class PIDController:
    """
    Proportional-Integral-Derivative controller for parameter regulation.
    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        output_min: float = 0.0,
        output_max: float = 100.0,
    ):
        """
        Initialize PID controller.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            output_min: Minimum output value
            output_max: Maximum output value
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max

        self.integral = 0.0
        self.last_error = 0.0

    def update(self, setpoint: float, measured: float, dt: float) -> float:
        """
        Calculate PID control output.

        Args:
            setpoint: Desired value
            measured: Current measured value
            dt: Time step in seconds

        Returns:
            Control output
        """
        error = setpoint - measured

        # Proportional term
        p_term = self.kp * error

        if dt <= 0:
            # Skip integral accumulation and derivative calculation
            i_term = self.ki * self.integral
            d_term = 0.0
        else:
            # Integral term with anti-windup
            self.integral += error * dt
            self.integral = np.clip(self.integral, -100, 100)
            i_term = self.ki * self.integral

            # Derivative term
            d_term = self.kd * (error - self.last_error) / dt
            self.last_error = error

        # Calculate output with limits
        output = p_term + i_term + d_term
        return np.clip(output, self.output_min, self.output_max)

    def reset(self):
        """Reset controller state."""
        self.integral = 0.0
        self.last_error = 0.0


class AIEnvironmentalController:
    """
    AI-regulated environmental control system for lunar growth domes.

    Manages:
    - Temperature regulation (heating/cooling)
    - Humidity control (misting/venting)
    - Gas composition (CO2/O2 levels)
    - Light cycle management
    - Substrate moisture
    - Emergency response
    """

    def __init__(self, dome_id: str = "DOME-001"):
        """
        Initialize environmental controller.

        Args:
            dome_id: Unique identifier for this dome
        """
        self.dome_id = dome_id
        self.state = DomeState()

        # Initialize PID controllers
        self.temp_controller = PIDController(
            kp=2.0, ki=0.1, kd=0.5, output_min=-100, output_max=100
        )
        # Humidity control must support both humidification (positive output)
        # and dehumidification (negative output for venting).
        self.humidity_controller = PIDController(
            kp=1.5,
            ki=0.05,
            kd=0.3,
            output_min=-100,
            output_max=100,
        )
        self.co2_controller = PIDController(kp=0.5, ki=0.02, kd=0.1)

        # System history for learning
        self.history: List[Dict] = []

    def sense_environment(self) -> DomeSensors:
        """
        Read all environmental sensors.

        In real system, this would interface with actual sensors.
        For simulation, returns current state.

        Returns:
            Current DomeSensors readings
        """
        return self.state.sensors

    def check_alerts(
        self, sensors: DomeSensors, setpoints: EnvironmentalSetpoints
    ) -> List[Tuple[AlertLevel, str]]:
        """
        Check for out-of-range conditions and generate alerts.

        Args:
            sensors: Current sensor readings
            setpoints: Target parameters

        Returns:
            List of (AlertLevel, message) tuples
        """
        alerts = []

        # Temperature checks
        temp_error = abs(sensors.temperature_c - setpoints.temperature_c)
        if temp_error > setpoints.temperature_tolerance * 3:
            alerts.append(
                (
                    AlertLevel.CRITICAL,
                    f"Temperature {sensors.temperature_c:.1f}°C critically out of range",
                )
            )
        elif temp_error > setpoints.temperature_tolerance * 2:
            alerts.append(
                (
                    AlertLevel.WARNING,
                    f"Temperature {sensors.temperature_c:.1f}°C outside tolerance",
                )
            )

        # Humidity checks
        humidity_error = abs(sensors.humidity_percent - setpoints.humidity_percent)
        if humidity_error > setpoints.humidity_tolerance * 2:
            alerts.append(
                (
                    AlertLevel.WARNING,
                    f"Humidity {sensors.humidity_percent:.1f}% outside tolerance",
                )
            )

        # CO2 checks
        if sensors.co2_ppm > 5000:
            alerts.append(
                (
                    AlertLevel.CRITICAL,
                    f"CO2 level {sensors.co2_ppm} ppm dangerously high",
                )
            )
        elif sensors.co2_ppm < 200:
            alerts.append(
                (
                    AlertLevel.WARNING,
                    f"CO2 level {sensors.co2_ppm} ppm too low for plant growth",
                )
            )

        # O2 checks
        if sensors.o2_percent < 18.0:
            alerts.append(
                (
                    AlertLevel.EMERGENCY,
                    f"Oxygen level {sensors.o2_percent:.1f}% critically low",
                )
            )
        elif sensors.o2_percent > 23.0:
            alerts.append(
                (
                    AlertLevel.CRITICAL,
                    f"Oxygen level {sensors.o2_percent:.1f}% fire hazard",
                )
            )

        return alerts

    def calculate_temperature_control(
        self, current: float, setpoint: float, dt: float
    ) -> Tuple[float, bool]:
        """
        Calculate heating/cooling requirements.

        Args:
            current: Current temperature
            setpoint: Target temperature
            dt: Time step

        Returns:
            Tuple of (heater_power_percent, cooler_active)
        """
        control_output = self.temp_controller.update(setpoint, current, dt)

        if control_output > 0:
            # Need heating
            return (control_output, False)
        else:
            # Need cooling
            return (0.0, control_output < 0)

    def calculate_humidity_control(
        self, current: float, setpoint: float, dt: float
    ) -> Tuple[float, float]:
        """
        Calculate misting and venting requirements.

        Args:
            current: Current humidity
            setpoint: Target humidity
            dt: Time step

        Returns:
            Tuple of (misting_rate, vent_position)
        """
        control_output = self.humidity_controller.update(setpoint, current, dt)

        if control_output > 0:
            # Need humidification
            misting_rate = control_output * 0.5  # mL/min
            vent_position = 0.0
        else:
            # Need dehumidification
            misting_rate = 0.0
            vent_position = min(abs(control_output), 50.0)

        return (misting_rate, vent_position)

    def calculate_co2_control(
        self, current: float, setpoint: float, dt: float
    ) -> float:
        """
        Calculate CO2 injection rate.

        Args:
            current: Current CO2 level
            setpoint: Target CO2 level
            dt: Time step

        Returns:
            CO2 injection rate in mL/min
        """
        control_output = self.co2_controller.update(setpoint, current, dt)
        return max(0.0, control_output * 0.1)

    def calculate_lighting_control(
        self, current_hour: float, photoperiod: float
    ) -> float:
        """
        Calculate LED power based on photoperiod.

        Args:
            current_hour: Hour of day (0-24)
            photoperiod: Hours of light per day

        Returns:
            LED power percent
        """
        hour_in_cycle = current_hour % 24

        if hour_in_cycle < photoperiod:
            # Lights on - gradual ramp at sunrise/sunset
            if hour_in_cycle < 1.0:
                return hour_in_cycle * 100  # Sunrise ramp
            elif hour_in_cycle > photoperiod - 1.0:
                return (photoperiod - hour_in_cycle) * 100  # Sunset ramp
            else:
                return 100.0  # Full power
        else:
            return 0.0  # Lights off

    def update_control(self, dt: float = 1.0) -> ControlActions:
        """
        Main control loop - calculate all actuator outputs.

        Args:
            dt: Time step in seconds

        Returns:
            ControlActions with updated actuator commands
        """
        sensors = self.state.sensors
        setpoints = self.state.setpoints

        # Check for alerts
        self.state.alerts = self.check_alerts(sensors, setpoints)

        # Emergency mode if critical alerts
        if any(alert[0] == AlertLevel.EMERGENCY for alert in self.state.alerts):
            self.state.mode = ControlMode.EMERGENCY
            return self._emergency_response()

        # Calculate control outputs
        heater, cooler = self.calculate_temperature_control(
            sensors.temperature_c, setpoints.temperature_c, dt
        )

        misting, venting = self.calculate_humidity_control(
            sensors.humidity_percent, setpoints.humidity_percent, dt
        )

        co2_injection = self.calculate_co2_control(
            sensors.co2_ppm, setpoints.co2_ppm, dt
        )

        led_power = self.calculate_lighting_control(
            sensors.timestamp / 3600, setpoints.photoperiod_hours
        )

        # Circulation fan - proportional to temperature error
        temp_error = abs(sensors.temperature_c - setpoints.temperature_c)
        fan_speed = 500 + min(temp_error * 100, 1500)  # 500-2000 RPM

        actions = ControlActions(
            heater_power_percent=heater,
            cooler_active=cooler,
            misting_rate_ml_min=misting,
            vent_position_percent=venting,
            co2_injection_rate_ml_min=co2_injection,
            led_power_percent=led_power,
            circulation_fan_rpm=fan_speed,
        )

        # Calculate energy consumption
        energy = (
            heater * 2.0  # Heater: up to 200W
            + (60 if cooler else 0)  # Cooler: 60W
            + led_power * 1.0  # LEDs: up to 100W
            + fan_speed * 0.02
        )  # Fan: ~40W at max

        self.state.actions = actions
        self.state.energy_consumption_w = energy

        return actions

    def _emergency_response(self) -> ControlActions:
        """
        Emergency shutdown and safe mode response.

        Returns:
            Safe-state ControlActions
        """
        return ControlActions(
            heater_power_percent=0.0,
            cooler_active=False,
            misting_rate_ml_min=0.0,
            vent_position_percent=100.0,  # Full ventilation
            co2_injection_rate_ml_min=0.0,
            led_power_percent=0.0,
            circulation_fan_rpm=2000.0,  # Max ventilation
        )

    def simulate_step(self, dt: float = 60.0):
        """
        Simulate one time step with physics model.

        Args:
            dt: Time step in seconds
        """
        # Update controls
        actions = self.update_control(dt)

        # Simple physics simulation
        sensors = self.state.sensors

        # Temperature dynamics
        temp_change = 0.0
        temp_change += actions.heater_power_percent * 0.001  # Heating effect
        temp_change -= 0.002 if actions.cooler_active else 0.0  # Cooling effect
        temp_change -= (
            sensors.temperature_c - (-20)
        ) * 0.0001  # Heat loss to lunar night
        sensors.temperature_c += temp_change * dt

        # Humidity dynamics
        humidity_change = 0.0
        humidity_change += actions.misting_rate_ml_min * 0.05  # Misting effect
        humidity_change -= actions.vent_position_percent * 0.001  # Venting effect
        humidity_change -= sensors.humidity_percent * 0.0005  # Natural evaporation
        sensors.humidity_percent = np.clip(
            sensors.humidity_percent + humidity_change * dt, 0, 100
        )

        # CO2 dynamics
        co2_change = 0.0
        co2_change += actions.co2_injection_rate_ml_min * 10  # Injection
        co2_change -= 5.0  # Plant consumption (simplified)
        co2_change -= actions.vent_position_percent * 0.5  # Venting loss
        sensors.co2_ppm = max(0, sensors.co2_ppm + co2_change * dt / 60)

        # O2 dynamics (inverse of CO2 from photosynthesis)
        if actions.led_power_percent > 50:
            sensors.o2_percent += 0.0001 * dt  # Photosynthesis

        sensors.timestamp += dt

        # Store history
        self.history.append(asdict(self.state))

    def run_simulation(self, duration_hours: float = 24.0, dt: float = 60.0):
        """
        Run multi-hour simulation.

        Args:
            duration_hours: Simulation duration
            dt: Time step in seconds
        """
        steps = int(duration_hours * 3600 / dt)

        for _ in range(steps):
            self.simulate_step(dt)

    def plot_performance(self, save_path: Optional[str] = None):
        """
        Visualize system performance over time.

        Args:
            save_path: Optional path to save figure
        """
        if not self.history:
            print("No simulation history to plot")
            return

        # Extract data from history
        times = [
            h["sensors"]["timestamp"] / 3600 for h in self.history
        ]  # Convert to hours
        temps = [h["sensors"]["temperature_c"] for h in self.history]
        humidity = [h["sensors"]["humidity_percent"] for h in self.history]
        co2 = [h["sensors"]["co2_ppm"] for h in self.history]
        energy = [h["energy_consumption_w"] for h in self.history]

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Temperature
        ax1 = axes[0, 0]
        ax1.plot(times, temps, "r-", linewidth=2)
        ax1.axhline(
            y=self.state.setpoints.temperature_c,
            color="g",
            linestyle="--",
            label="Setpoint",
        )
        ax1.fill_between(
            times,
            self.state.setpoints.temperature_c
            - self.state.setpoints.temperature_tolerance,
            self.state.setpoints.temperature_c
            + self.state.setpoints.temperature_tolerance,
            alpha=0.2,
            color="g",
            label="Tolerance",
        )
        ax1.set_xlabel("Time (hours)")
        ax1.set_ylabel("Temperature (°C)")
        ax1.set_title("Temperature Control")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Humidity
        ax2 = axes[0, 1]
        ax2.plot(times, humidity, "b-", linewidth=2)
        ax2.axhline(
            y=self.state.setpoints.humidity_percent,
            color="g",
            linestyle="--",
            label="Setpoint",
        )
        ax2.set_xlabel("Time (hours)")
        ax2.set_ylabel("Humidity (%)")
        ax2.set_title("Humidity Control")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # CO2
        ax3 = axes[1, 0]
        ax3.plot(times, co2, "purple", linewidth=2)
        ax3.axhline(
            y=self.state.setpoints.co2_ppm, color="g", linestyle="--", label="Setpoint"
        )
        ax3.set_xlabel("Time (hours)")
        ax3.set_ylabel("CO₂ (ppm)")
        ax3.set_title("CO₂ Concentration")
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Energy consumption
        ax4 = axes[1, 1]
        ax4.plot(times, energy, "orange", linewidth=2)
        ax4.set_xlabel("Time (hours)")
        ax4.set_ylabel("Power (W)")
        ax4.set_title("Energy Consumption")
        ax4.grid(True, alpha=0.3)

        total_energy_kwh = np.trapezoid(energy, times) / 1000
        ax4.text(
            0.5,
            0.95,
            f"Total: {total_energy_kwh:.2f} kWh",
            transform=ax4.transAxes,
            ha="center",
            va="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
        else:
            plt.show()


def run_example():
    """Run example environmental control simulation."""
    print("Bio-Stabilizing Lunar Spray - Environmental Control System")
    print("=" * 70)

    # Create controller
    controller = AIEnvironmentalController(dome_id="LUNAR-DOME-001")

    # Set growing mode
    controller.state.mode = ControlMode.GROWING

    # Set initial conditions (challenging scenario)
    controller.state.sensors.temperature_c = 15.0  # Below setpoint
    controller.state.sensors.humidity_percent = 40.0  # Below setpoint
    controller.state.sensors.co2_ppm = 400.0  # Below setpoint

    print(f"\nDome ID: {controller.dome_id}")
    print(f"Mode: {controller.state.mode.value}")
    print(f"\nInitial Conditions:")
    print(f"  Temperature: {controller.state.sensors.temperature_c}°C")
    print(f"  Humidity: {controller.state.sensors.humidity_percent}%")
    print(f"  CO₂: {controller.state.sensors.co2_ppm} ppm")

    print(f"\nSetpoints:")
    print(
        f"  Temperature: {controller.state.setpoints.temperature_c}°C ± {controller.state.setpoints.temperature_tolerance}°C"
    )
    print(
        f"  Humidity: {controller.state.setpoints.humidity_percent}% ± {controller.state.setpoints.humidity_tolerance}%"
    )
    print(
        f"  CO₂: {controller.state.setpoints.co2_ppm} ppm ± {controller.state.setpoints.co2_tolerance} ppm"
    )

    print(f"\nRunning 24-hour simulation...")
    controller.run_simulation(duration_hours=24.0, dt=60.0)

    # Final state
    final_sensors = controller.state.sensors
    print(f"\nFinal Conditions (after 24h):")
    print(f"  Temperature: {final_sensors.temperature_c:.1f}°C")
    print(f"  Humidity: {final_sensors.humidity_percent:.1f}%")
    print(f"  CO₂: {final_sensors.co2_ppm:.0f} ppm")
    print(f"  O₂: {final_sensors.o2_percent:.1f}%")
    print(f"  Total Energy: {controller.state.energy_consumption_w:.1f} W")

    # Plot results
    controller.plot_performance()

    return controller


if __name__ == "__main__":
    controller = run_example()
