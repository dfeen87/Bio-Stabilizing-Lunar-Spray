"""
Utility Functions for Bio-Stabilizing Lunar Spray Simulation

Shared utilities, constants, data structures, and helper functions
used across all simulation modules.

Author: Don Michael Feeney Jr
Based on: Bio-Stabilizing Lunar Spray white paper (April 2025)
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import warnings

# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================


class PhysicalConstants:
    """Fundamental physical constants for lunar simulations."""

    # Gravity
    GRAVITY_MOON = 1.62  # m/s²
    GRAVITY_EARTH = 9.81  # m/s²
    GRAVITY_MARS = 3.71  # m/s²

    # Lunar environment
    LUNAR_DAY_HOURS = 708  # 29.5 Earth days
    LUNAR_NIGHT_HOURS = 708
    LUNAR_TEMP_MAX_C = 127  # Equatorial daytime
    LUNAR_TEMP_MIN_C = -173  # Polar night

    # Gas constants
    GAS_CONSTANT = 8.314  # J/(mol·K)
    AVOGADRO = 6.022e23  # molecules/mol

    # Conversions
    PSI_TO_PA = 6894.76
    ML_TO_M3 = 1e-6
    MM_TO_M = 1e-3

    # Atmospheric
    STANDARD_PRESSURE_PA = 101325
    LUNAR_VACUUM_PA = 1e-12


class ChemicalConstants:
    """Chemical properties and molecular weights."""

    # Molecular weights (g/mol)
    MW = {
        "K2SiO3": 154.28,
        "MgSO4": 120.37,
        "Ca3(PO4)2": 310.18,
        "CO(NH2)2": 60.06,  # Urea
        "H3PO4": 98.00,
        "H2O": 18.02,
        "CO2": 44.01,
        "O2": 32.00,
        "N2": 28.01,
    }

    # Nutrient atomic masses
    NUTRIENT_MASS = {
        "N": 14.01,
        "P": 30.97,
        "K": 39.10,
        "Mg": 24.31,
        "S": 32.07,
        "Ca": 40.08,
    }


class SprayConstants:
    """Constants for spray dynamics."""

    BASE_VISCOSITY = 3000.0  # cP at 20°C
    DEFAULT_PRESSURE = 25.0  # PSI
    DEFAULT_NOZZLE_DIAMETER = 2.0  # mm


class CuringConstants:
    """Constants for curing simulation."""

    BASE_CURE_TIME = 14.0  # minutes at 0°C
    MAX_BOND_STRENGTH = 3.5  # MPa
    UV_ACCELERATION = 0.30  # 30% faster with UV
    ACTIVATION_ENERGY = 45.0  # kJ/mol
    MAX_CURE_TIME = 90.0  # minutes


class NutrientConstants:
    """Constants for nutrient release."""

    K_MAX = 2000.0  # ppm
    N_MAX = 1500.0  # ppm
    P_MAX = 900.0  # ppm
    MG_MAX = 500.0  # ppm
    S_MAX = 800.0  # ppm
    CA_MAX = 600.0  # ppm

    # Release kinetics parameters
    K_RATE = 0.15
    K_DELAY = 30

    N_FAST_RATE = 30
    N_SLOW_RATE = 20
    N_TRANSITION_DAY = 20

    P_RATE = 0.1
    P_DELAY = 50

    MG_START_DAY = 10
    MG_RATE = 12


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class LunarLocation:
    """Lunar surface location with environmental context."""

    name: str
    latitude: float  # degrees
    longitude: float  # degrees
    elevation: float = 0.0  # meters above datum
    avg_temp_c: float = 0.0
    solar_exposure: float = 0.5  # 0-1, fraction of time in sunlight
    terrain_type: str = "mare"  # mare, highland, crater, polar

    def is_polar(self) -> bool:
        """Check if location is in polar region (>80° latitude)."""
        return abs(self.latitude) > 80.0

    def is_permanently_shadowed(self) -> bool:
        """Check if location is in permanently shadowed region."""
        return self.is_polar() and self.solar_exposure < 0.1


@dataclass
class RegolithSample:
    """Lunar regolith sample composition and properties."""

    name: str = "JSC-1A"
    sio2_percent: float = 47.0
    al2o3_percent: float = 14.0
    feo_percent: float = 10.5
    cao_percent: float = 10.0
    mgo_percent: float = 9.0
    tio2_percent: float = 3.5
    others_percent: float = 6.0

    particle_size_um: float = 70.0  # Mean particle size
    density_g_cm3: float = 1.5
    surface_area_m2_g: float = 0.5

    def validate(self) -> bool:
        """Check if composition sums to ~100%."""
        total = (
            self.sio2_percent
            + self.al2o3_percent
            + self.feo_percent
            + self.cao_percent
            + self.mgo_percent
            + self.tio2_percent
            + self.others_percent
        )
        return 99.0 <= total <= 101.0

    def get_composition_dict(self) -> Dict[str, float]:
        """Return composition as dictionary."""
        return {
            "SiO2": self.sio2_percent,
            "Al2O3": self.al2o3_percent,
            "FeO": self.feo_percent,
            "CaO": self.cao_percent,
            "MgO": self.mgo_percent,
            "TiO2": self.tio2_percent,
            "Others": self.others_percent,
        }


# ============================================================================
# MATHEMATICAL UTILITIES
# ============================================================================


def sigmoid(
    x: Union[float, np.ndarray], midpoint: float = 0.0, steepness: float = 1.0
) -> Union[float, np.ndarray]:
    """
    Sigmoid (logistic) function.

    Args:
        x: Input value(s)
        midpoint: Point where function equals 0.5
        steepness: Controls slope steepness

    Returns:
        Sigmoid output between 0 and 1
    """
    return 1.0 / (1.0 + np.exp(-steepness * (x - midpoint)))


def arrhenius_factor(
    temperature_c: float,
    activation_energy_kj_mol: float,
    reference_temp_c: float = 25.0,
) -> float:
    """
    Calculate Arrhenius temperature dependence factor.

    k(T) = k_ref * exp(-Ea/R * (1/T - 1/T_ref))

    Args:
        temperature_c: Temperature in Celsius
        activation_energy_kj_mol: Activation energy in kJ/mol
        reference_temp_c: Reference temperature

    Returns:
        Rate multiplier relative to reference temperature
    """
    T_kelvin = temperature_c + 273.15
    T_ref_kelvin = reference_temp_c + 273.15

    exponent = -(activation_energy_kj_mol * 1000) / PhysicalConstants.GAS_CONSTANT
    factor = exponent * (1 / T_kelvin - 1 / T_ref_kelvin)

    return np.exp(factor)


def interpolate_linear(x: float, x_points: List[float], y_points: List[float]) -> float:
    """
    Linear interpolation between data points.

    Args:
        x: Point to interpolate
        x_points: Known x values (must be sorted)
        y_points: Known y values

    Returns:
        Interpolated y value
    """
    return np.interp(x, x_points, y_points)


def moving_average(data: np.ndarray, window_size: int) -> np.ndarray:
    """
    Calculate moving average for smoothing data.

    Args:
        data: Input data array
        window_size: Size of averaging window

    Returns:
        Smoothed data array
    """
    if window_size < 2:
        return data

    cumsum = np.cumsum(np.insert(data, 0, 0))
    return (cumsum[window_size:] - cumsum[:-window_size]) / window_size


def calculate_r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate R² (coefficient of determination) for model fit.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        R² value (0-1, higher is better)
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)

    if ss_tot == 0:
        return 0.0

    return 1 - (ss_res / ss_tot)


# ============================================================================
# UNIT CONVERSIONS
# ============================================================================


class UnitConverter:
    """Common unit conversions for lunar engineering."""

    @staticmethod
    def celsius_to_kelvin(temp_c: float) -> float:
        """Convert Celsius to Kelvin."""
        return temp_c + 273.15

    @staticmethod
    def kelvin_to_celsius(temp_k: float) -> float:
        """Convert Kelvin to Celsius."""
        return temp_k - 273.15

    @staticmethod
    def psi_to_pascal(pressure_psi: float) -> float:
        """Convert PSI to Pascal."""
        return pressure_psi * PhysicalConstants.PSI_TO_PA

    @staticmethod
    def pascal_to_psi(pressure_pa: float) -> float:
        """Convert Pascal to PSI."""
        return pressure_pa / PhysicalConstants.PSI_TO_PA

    @staticmethod
    def ml_to_cubic_meters(volume_ml: float) -> float:
        """Convert milliliters to cubic meters."""
        return volume_ml * PhysicalConstants.ML_TO_M3

    @staticmethod
    def cubic_meters_to_ml(volume_m3: float) -> float:
        """Convert cubic meters to milliliters."""
        return volume_m3 / PhysicalConstants.ML_TO_M3

    @staticmethod
    def mm_to_meters(length_mm: float) -> float:
        """Convert millimeters to meters."""
        return length_mm * PhysicalConstants.MM_TO_M

    @staticmethod
    def meters_to_mm(length_m: float) -> float:
        """Convert meters to millimeters."""
        return length_m / PhysicalConstants.MM_TO_M

    @staticmethod
    def ppm_to_mg_per_liter(ppm: float, molecular_weight: float = 1.0) -> float:
        """
        Convert ppm to mg/L (considering molecular weight).

        For dilute solutions, 1 ppm ≈ 1 mg/L
        """
        return ppm * molecular_weight / 1.0

    @staticmethod
    def kwh_to_joules(energy_kwh: float) -> float:
        """Convert kilowatt-hours to joules."""
        return energy_kwh * 3.6e6

    @staticmethod
    def joules_to_kwh(energy_j: float) -> float:
        """Convert joules to kilowatt-hours."""
        return energy_j / 3.6e6


# ============================================================================
# DATA I/O UTILITIES
# ============================================================================


def load_json_data(filepath: Union[str, Path]) -> Dict:
    """
    Load JSON data file.

    Args:
        filepath: Path to JSON file

    Returns:
        Dictionary of loaded data
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")

    with open(filepath, "r") as f:
        return json.load(f)


def save_json_data(data: Dict, filepath: Union[str, Path], indent: int = 2):
    """
    Save data to JSON file.

    Args:
        data: Dictionary to save
        filepath: Output file path
        indent: JSON indentation level
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=indent, default=str)


def dataclass_to_dict(obj: Any) -> Union[Dict, List, Any]:
    """
    Convert dataclass to dictionary, handling nested structures.

    Args:
        obj: Dataclass instance

    Returns:
        Dictionary representation
    """
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    elif isinstance(obj, (list, tuple)):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: dataclass_to_dict(value) for key, value in obj.items()}
    else:
        return obj


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================


def validate_temperature(
    temp_c: float, min_temp: float = -273.15, max_temp: float = 200.0
) -> bool:
    """
    Validate temperature is within physical bounds.

    Args:
        temp_c: Temperature in Celsius
        min_temp: Minimum allowed temperature
        max_temp: Maximum allowed temperature

    Returns:
        True if valid

    Raises:
        ValueError if temperature is invalid
    """
    if not min_temp <= temp_c <= max_temp:
        raise ValueError(
            f"Temperature {temp_c}°C outside valid range " f"[{min_temp}, {max_temp}]°C"
        )
    return True


def validate_pressure(
    pressure_psi: float, min_pressure: float = 0.0, max_pressure: float = 100.0
) -> bool:
    """
    Validate pressure is within operational bounds.

    Args:
        pressure_psi: Pressure in PSI
        min_pressure: Minimum allowed pressure
        max_pressure: Maximum allowed pressure

    Returns:
        True if valid

    Raises:
        ValueError if pressure is invalid
    """
    if not min_pressure <= pressure_psi <= max_pressure:
        raise ValueError(
            f"Pressure {pressure_psi} PSI outside valid range "
            f"[{min_pressure}, {max_pressure}] PSI"
        )
    return True


def validate_percentage(
    value: float, name: str = "Value", min_val: float = 0.0, max_val: float = 100.0
) -> bool:
    """
    Validate percentage is within bounds.

    Args:
        value: Percentage value
        name: Name for error messages
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        True if valid

    Raises:
        ValueError if percentage is invalid
    """
    if not min_val <= value <= max_val:
        raise ValueError(f"{name} {value}% outside valid range [{min_val}, {max_val}]%")
    return True


def validate_concentration(
    conc_ppm: float, nutrient: str = "Nutrient", max_safe: float = 10000.0
) -> bool:
    """
    Validate nutrient concentration is safe for plants.

    Args:
        conc_ppm: Concentration in ppm
        nutrient: Nutrient name
        max_safe: Maximum safe concentration

    Returns:
        True if valid

    Raises:
        Warning if concentration is high
    """
    if conc_ppm > max_safe:
        warnings.warn(
            f"{nutrient} concentration {conc_ppm:.0f} ppm exceeds "
            f"recommended maximum {max_safe:.0f} ppm"
        )
    return True


# ============================================================================
# LOGGING AND FORMATTING
# ============================================================================


def format_scientific(value: float, precision: int = 2) -> str:
    """
    Format number in scientific notation.

    Args:
        value: Number to format
        precision: Decimal places

    Returns:
        Formatted string
    """
    return f"{value:.{precision}e}"


def format_percentage(value: float, precision: int = 1) -> str:
    """
    Format number as percentage.

    Args:
        value: Number (0-100 or 0-1)
        precision: Decimal places

    Returns:
        Formatted percentage string
    """
    if value <= 1.0:
        value *= 100
    return f"{value:.{precision}f}%"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable form.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def create_progress_bar(
    current: int, total: int, width: int = 50, prefix: str = "Progress"
) -> str:
    """
    Create text-based progress bar.

    Args:
        current: Current progress
        total: Total items
        width: Bar width in characters
        prefix: Label prefix

    Returns:
        Progress bar string
    """
    fraction = current / total if total > 0 else 0
    filled = int(width * fraction)
    bar = "█" * filled + "░" * (width - filled)
    percent = fraction * 100

    return f"{prefix}: |{bar}| {percent:.1f}% ({current}/{total})"


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================


class ConfigManager:
    """Manage simulation configuration files."""

    def __init__(self, config_dir: Union[str, Path] = "config"):
        """
        Initialize configuration manager.

        Args:
            config_dir: Directory for configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_config(self, config: Dict, name: str):
        """Save configuration to file."""
        filepath = self.config_dir / f"{name}.json"
        save_json_data(config, filepath)

    def load_config(self, name: str) -> Dict:
        """Load configuration from file."""
        filepath = self.config_dir / f"{name}.json"
        return load_json_data(filepath)

    def list_configs(self) -> List[str]:
        """List available configuration files."""
        return [f.stem for f in self.config_dir.glob("*.json")]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


def run_utils_demo():
    """Demonstrate utility functions."""
    print("Bio-Stabilizing Lunar Spray - Utilities Demo")
    print("=" * 60)

    # Constants
    print(f"\nPhysical Constants:")
    print(f"  Moon gravity: {PhysicalConstants.GRAVITY_MOON} m/s²")
    print(f"  Lunar day: {PhysicalConstants.LUNAR_DAY_HOURS} hours")
    print(f"  Max temp: {PhysicalConstants.LUNAR_TEMP_MAX_C}°C")

    # Unit conversions
    print(f"\nUnit Conversions:")
    print(f"  25 PSI = {UnitConverter.psi_to_pascal(25):.0f} Pa")
    print(f"  500 mL = {UnitConverter.ml_to_cubic_meters(500):.6f} m³")
    print(f"  0°C = {UnitConverter.celsius_to_kelvin(0):.2f} K")

    # Math functions
    print(f"\nMathematical Functions:")
    print(f"  sigmoid(0) = {sigmoid(0):.3f}")
    print(f"  sigmoid(5) = {sigmoid(5):.3f}")

    temp_factor = arrhenius_factor(0, 45.0, 25.0)
    print(f"  Arrhenius factor (0°C, 45 kJ/mol) = {temp_factor:.3f}")

    # Regolith sample
    print(f"\nRegolith Sample (JSC-1A):")
    sample = RegolithSample()
    print(f"  Valid composition: {sample.validate()}")
    print(f"  SiO₂: {sample.sio2_percent}%")
    print(f"  Al₂O₃: {sample.al2o3_percent}%")

    # Location
    print(f"\nLunar Location:")
    location = LunarLocation(
        name="Shackleton Crater", latitude=-89.9, longitude=0.0, solar_exposure=0.05
    )
    print(f"  Name: {location.name}")
    print(f"  Polar: {location.is_polar()}")
    print(f"  Permanently shadowed: {location.is_permanently_shadowed()}")

    # Formatting
    print(f"\nFormatting:")
    print(f"  Scientific: {format_scientific(0.00123, 2)}")
    print(f"  Percentage: {format_percentage(0.856, 1)}")
    print(f"  Duration: {format_duration(7385)}")
    print(f"  Progress: {create_progress_bar(75, 100, width=30)}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_utils_demo()
