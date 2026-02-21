"""
Bio-Stabilizing Lunar Spray
============================

A dual-purpose surface and agricultural solution for lunar habitats.

This package provides simulation tools for:
- Spray dynamics and regolith coverage
- Temperature-dependent curing kinetics
- Nutrient release and biological transition
- AI-regulated environmental control systems

Author: Don Michael Feeney Jr
Date: January 2026
License: MIT

Usage Examples
--------------

Basic spray simulation:
    >>> from src import SprayDynamics, SprayParameters
    >>> params = SprayParameters(pressure_psi=25.0)
    >>> sim = SprayDynamics(params)
    >>> results = sim.simulate_radial_expansion(volume_ml=500)
    >>> print(f"Coverage: {results.coverage_area:.2f} m²")

Complete mission:
    >>> from integrated_simulation import IntegratedLunarSpraySimulation
    >>> from integrated_simulation import MissionParameters
    >>> params = MissionParameters()
    >>> sim = IntegratedLunarSpraySimulation(params)
    >>> results = sim.run_complete_simulation()
"""

__version__ = "0.1.0"
__author__ = "Don Michael Feeney Jr"
__license__ = "MIT"
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # Spray Dynamics
    "SprayDynamics",
    "SprayParameters",
    "SprayResults",
    # Curing Simulation
    "CuringSimulator",
    "CuringProfile",
    "CuringPhase",
    "RegolithProperties",
    # Nutrient Release
    "NutrientReleaseSimulator",
    "NutrientProfile",
    "PlantRequirements",
    "Nutrient",
    # Environmental Control
    "AIEnvironmentalController",
    "DomeState",
    "ControlMode",
    "EnvironmentalSetpoints",
    # Utils
    "PhysicalConstants",
    "ChemicalConstants",
    "UnitConverter",
]

# Import core classes
try:
    from .spray_dynamics import SprayDynamics, SprayParameters, SprayResults
except ImportError as e:
    import warnings

    warnings.warn(f"Could not import spray_dynamics: {e}")

try:
    from .curing_simulation import (
        CuringSimulator,
        CuringProfile,
        CuringPhase,
        RegolithProperties,
    )
except ImportError as e:
    import warnings

    warnings.warn(f"Could not import curing_simulation: {e}")

try:
    from .nutrient_release import (
        NutrientReleaseSimulator,
        NutrientProfile,
        PlantRequirements,
        Nutrient,
    )
except ImportError as e:
    import warnings

    warnings.warn(f"Could not import nutrient_release: {e}")

try:
    from .environmental_control import (
        AIEnvironmentalController,
        DomeState,
        ControlMode,
        EnvironmentalSetpoints,
    )
except ImportError as e:
    import warnings

    warnings.warn(f"Could not import environmental_control: {e}")

try:
    from .utils import PhysicalConstants, ChemicalConstants, UnitConverter
except ImportError as e:
    import warnings

    warnings.warn(f"Could not import utils: {e}")


def get_version():
    """Return the current version."""
    return __version__


def get_info():
    """Return package information."""
    return {
        "name": "Bio-Stabilizing Lunar Spray",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": "Dual-purpose regolith stabilization and agricultural substrate",
    }
