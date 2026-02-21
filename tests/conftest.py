"""
Pytest Configuration and Shared Fixtures

Provides reusable fixtures, test configuration, and utilities
for all test modules.

Author: Don Michael Feeney Jr
"""

import sys
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import all modules for fixtures
from src.spray_dynamics import SprayDynamics, SprayParameters
from src.curing_simulation import CuringSimulator, RegolithProperties
from src.nutrient_release import NutrientReleaseSimulator, PlantRequirements
from src.environmental_control import AIEnvironmentalController, EnvironmentalSetpoints
from integrated_simulation import IntegratedLunarSpraySimulation, MissionParameters

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line(
        "markers", "benchmark: marks tests as performance benchmarks"
    )


# ============================================================================
# DIRECTORY AND FILE FIXTURES
# ============================================================================


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    data_dir = Path(__file__).parent / "test_data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test outputs."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    # Cleanup after test
    shutil.rmtree(temp_path)


@pytest.fixture
def output_dir(temp_dir):
    """Provide directory for test output files."""
    output_path = temp_dir / "outputs"
    output_path.mkdir(exist_ok=True)
    return output_path


# ============================================================================
# SPRAY DYNAMICS FIXTURES
# ============================================================================


@pytest.fixture
def spray_params_nominal():
    """Standard spray parameters for nominal conditions."""
    return SprayParameters(
        pressure_psi=25.0, ambient_temp_c=0.0, surface_slope=0.0, viscosity_cp=3000.0
    )


@pytest.fixture
def spray_params_cold():
    """Spray parameters for cold lunar conditions."""
    return SprayParameters(
        pressure_psi=25.0, ambient_temp_c=-50.0, surface_slope=0.0, viscosity_cp=3000.0
    )


@pytest.fixture
def spray_params_sloped():
    """Spray parameters for sloped terrain."""
    return SprayParameters(
        pressure_psi=25.0, ambient_temp_c=0.0, surface_slope=10.0, viscosity_cp=3000.0
    )


@pytest.fixture
def spray_simulator(spray_params_nominal):
    """Standard spray dynamics simulator."""
    return SprayDynamics(spray_params_nominal)


@pytest.fixture
def spray_results_500ml(spray_simulator):
    """Pre-computed spray results for 500mL application."""
    return spray_simulator.simulate_radial_expansion(volume_ml=500)


# ============================================================================
# CURING SIMULATION FIXTURES
# ============================================================================


@pytest.fixture
def regolith_jsc1a():
    """JSC-1A lunar regolith simulant properties."""
    return RegolithProperties()


@pytest.fixture
def regolith_high_alumina():
    """High-alumina regolith for faster curing."""
    return RegolithProperties(alumina_content=20.0)


@pytest.fixture
def curing_simulator_standard():
    """Standard curing simulator (no UV)."""
    return CuringSimulator(uv_assisted=False)


@pytest.fixture
def curing_simulator_uv():
    """UV-assisted curing simulator."""
    return CuringSimulator(uv_assisted=True)


@pytest.fixture
def curing_profile_nominal(curing_simulator_standard):
    """Pre-computed curing profile at 0°C."""
    return curing_simulator_standard.simulate_curing(
        temperature_c=0.0, duration_min=30.0
    )


# ============================================================================
# NUTRIENT RELEASE FIXTURES
# ============================================================================


@pytest.fixture
def nutrient_simulator():
    """Standard nutrient release simulator."""
    return NutrientReleaseSimulator(initial_ph=10.0, water_availability=1.0)


@pytest.fixture
def nutrient_simulator_limited_water():
    """Nutrient simulator with limited water."""
    return NutrientReleaseSimulator(initial_ph=10.0, water_availability=0.6)


@pytest.fixture
def plant_requirements_standard():
    """Standard plant nutrient requirements."""
    return PlantRequirements()


@pytest.fixture
def plant_requirements_strict():
    """Strict plant nutrient requirements."""
    return PlantRequirements(
        nitrogen_min=150.0, phosphorus_min=50.0, potassium_min=200.0
    )


@pytest.fixture
def nutrient_profile_60day(nutrient_simulator):
    """Pre-computed 60-day nutrient release profile."""
    return nutrient_simulator.simulate_release_cycle(duration_days=60)


# ============================================================================
# ENVIRONMENTAL CONTROL FIXTURES
# ============================================================================


@pytest.fixture
def environmental_setpoints():
    """Standard environmental setpoints."""
    return EnvironmentalSetpoints(
        temperature_c=22.0, humidity_percent=65.0, co2_ppm=800.0, photoperiod_hours=16.0
    )


@pytest.fixture
def dome_controller():
    """Standard dome environmental controller."""
    return AIEnvironmentalController(dome_id="TEST-DOME-001")


@pytest.fixture
def dome_controller_with_history(dome_controller):
    """Dome controller with simulated history."""
    dome_controller.run_simulation(duration_hours=24.0, dt=60.0)
    return dome_controller


# ============================================================================
# INTEGRATED SIMULATION FIXTURES
# ============================================================================


@pytest.fixture
def mission_params_standard():
    """Standard mission parameters."""
    return MissionParameters(
        landing_site="Test Site - Lunar South Pole",
        spray_volume_ml=500.0,
        application_pressure_psi=25.0,
        surface_slope_deg=5.0,
        ambient_temp_c=0.0,
        uv_assisted=True,
        target_crop="Lettuce (Test)",
        planting_delay_days=25,
        growth_duration_days=30,
    )


@pytest.fixture
def mission_params_cold():
    """Mission parameters for cold environment."""
    return MissionParameters(
        landing_site="Permanently Shadowed Region",
        spray_volume_ml=500.0,
        application_pressure_psi=25.0,
        surface_slope_deg=0.0,
        ambient_temp_c=-50.0,
        uv_assisted=True,
        target_crop="Lettuce (Test)",
        planting_delay_days=30,
        growth_duration_days=30,
    )


@pytest.fixture
def integrated_simulation(mission_params_standard):
    """Standard integrated simulation."""
    return IntegratedLunarSpraySimulation(mission_params_standard)


# ============================================================================
# DATA GENERATION FIXTURES
# ============================================================================


@pytest.fixture
def sample_time_array():
    """Standard time array for testing."""
    return np.linspace(0, 60, 100)


@pytest.fixture
def sample_temperature_profile():
    """Sample temperature profile data."""
    time = np.linspace(0, 24, 100)
    temp = 22.0 + 2.0 * np.sin(2 * np.pi * time / 24)
    return time, temp


@pytest.fixture
def sample_nutrient_data():
    """Sample nutrient concentration data."""
    days = np.linspace(0, 60, 60)
    nitrogen = np.minimum(days * 25, 1500)
    phosphorus = np.maximum(0, (days - 15) * 8)
    potassium = 2000 / (1 + np.exp(-0.15 * (days - 20)))

    return {
        "days": days,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium,
    }


# ============================================================================
# VALIDATION FIXTURES
# ============================================================================


@pytest.fixture
def validation_tolerances():
    """Standard validation tolerances for numerical comparisons."""
    return {
        "temperature": 0.1,  # °C
        "pressure": 1.0,  # PSI
        "percentage": 0.5,  # %
        "concentration": 10.0,  # ppm
        "time": 0.1,  # minutes
        "distance": 0.01,  # meters
        "strength": 0.1,  # MPa
    }


@pytest.fixture
def physical_limits():
    """Physical limits for validation."""
    return {
        "temperature_min": -273.15,  # Absolute zero
        "temperature_max": 200.0,  # Reasonable max
        "pressure_min": 0.0,
        "pressure_max": 100.0,
        "ph_min": 0.0,
        "ph_max": 14.0,
        "porosity_min": 0.0,
        "porosity_max": 1.0,
        "concentration_max": 10000.0,  # ppm
    }


# ============================================================================
# COMPARISON UTILITIES
# ============================================================================


@pytest.fixture
def assert_close():
    """Fixture providing a flexible comparison function."""

    def _assert_close(actual, expected, tolerance=1e-6, message=""):
        """Assert two values are close within tolerance."""
        if isinstance(actual, np.ndarray):
            diff = np.abs(actual - expected)
            assert np.all(diff <= tolerance), (
                f"{message}\nMax difference: {np.max(diff):.6e}, "
                f"Tolerance: {tolerance:.6e}"
            )
        else:
            diff = abs(actual - expected)
            assert diff <= tolerance, (
                f"{message}\nDifference: {diff:.6e}, " f"Tolerance: {tolerance:.6e}"
            )

    return _assert_close


# ============================================================================
# BENCHMARK FIXTURES
# ============================================================================


@pytest.fixture
def benchmark_config():
    """Configuration for performance benchmarks."""
    return {
        "spray_volume_ml": 500.0,
        "curing_duration_min": 30.0,
        "nutrient_duration_days": 60,
        "dome_duration_hours": 24.0,
        "time_steps": 100,
        "iterations": 5,
    }


# ============================================================================
# HELPER FUNCTIONS AS FIXTURES
# ============================================================================


@pytest.fixture
def create_test_report():
    """Factory fixture for creating test reports."""

    def _create_report(test_name, results, output_dir):
        """Create a JSON test report."""
        report = {
            "test_name": test_name,
            "timestamp": datetime.now().isoformat(),
            "results": results,
        }

        output_file = output_dir / f"{test_name}_report.json"
        import json

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        return output_file

    return _create_report


@pytest.fixture
def compare_arrays():
    """Fixture for comparing numpy arrays with detailed output."""

    def _compare(array1, array2, name1="Array1", name2="Array2"):
        """Compare two arrays and return detailed statistics."""
        diff = array1 - array2
        return {
            "mean_diff": np.mean(diff),
            "max_diff": np.max(np.abs(diff)),
            "std_diff": np.std(diff),
            "rmse": np.sqrt(np.mean(diff**2)),
            "all_close": np.allclose(array1, array2),
        }

    return _compare


# ============================================================================
# MOCK DATA FIXTURES
# ============================================================================


@pytest.fixture
def mock_sensor_readings():
    """Mock sensor readings for testing."""
    return {
        "temperature_c": 22.5,
        "humidity_percent": 64.0,
        "co2_ppm": 820.0,
        "o2_percent": 20.9,
        "pressure_pa": 101325.0,
    }


@pytest.fixture
def mock_weather_conditions():
    """Mock lunar surface conditions."""
    return {
        "solar_flux": 1361.0,  # W/m²
        "surface_temp_c": -20.0,
        "in_shadow": False,
        "time_of_day_hours": 12.0,
    }


# ============================================================================
# PARAMETRIZE HELPERS
# ============================================================================

# Temperature range for parametrized tests
TEMPERATURE_RANGE = [-50, -20, 0, 20, 40, 60]

# Volume range for parametrized tests
VOLUME_RANGE = [100, 250, 500, 1000, 2000]

# Pressure range for parametrized tests
PRESSURE_RANGE = [15, 20, 25, 30, 35]

# Time points for parametrized tests
TIME_POINTS = [50, 100, 150, 200]


@pytest.fixture
def temperature_range():
    """Provide standard temperature range for parametrized tests."""
    return TEMPERATURE_RANGE


@pytest.fixture
def volume_range():
    """Provide standard volume range for parametrized tests."""
    return VOLUME_RANGE


# ============================================================================
# CLEANUP AND REPORTING
# ============================================================================


@pytest.fixture(autouse=True, scope="session")
def cleanup_test_artifacts():
    """Cleanup test artifacts after session."""
    yield
    # Cleanup logic runs after all tests
    test_output_dir = Path(__file__).parent / "test_outputs"
    if test_output_dir.exists():
        # Keep for inspection, but could delete if desired
        pass


# ============================================================================
# CUSTOM MARKERS
# ============================================================================

# Example usage in tests:
# @pytest.mark.slow
# @pytest.mark.integration
# @pytest.mark.benchmark

# Run specific tests:
# pytest -m "not slow"  # Skip slow tests
# pytest -m integration # Only integration tests
# pytest -m unit        # Only unit tests
