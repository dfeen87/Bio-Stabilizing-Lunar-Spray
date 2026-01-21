"""
Test Suite for Bio-Stabilizing Lunar Spray
===========================================

Comprehensive test coverage for all simulation modules.

Test Organization
-----------------
- test_spray_dynamics.py    : Spray expansion and coverage tests
- test_curing.py            : Geopolymer curing kinetics tests
- test_nutrients.py         : Nutrient release and plant readiness tests
- test_utils.py             : Utility functions and helpers tests
- test_integration.py       : End-to-end integration tests
- test_benchmarks.py        : Performance benchmarks

Running Tests
-------------
All tests:
    pytest tests/ -v

Specific module:
    pytest tests/test_spray_dynamics.py -v

With coverage:
    pytest tests/ --cov=src --cov-report=html

Skip slow tests:
    pytest tests/ -m "not slow" -v

Integration tests only:
    pytest tests/ -m integration -v

Benchmarks only:
    pytest tests/ -m benchmark --benchmark-only

Test Markers
------------
- @pytest.mark.unit         : Unit tests
- @pytest.mark.integration  : Integration tests
- @pytest.mark.slow         : Slow-running tests
- @pytest.mark.benchmark    : Performance benchmarks

Author: Don Michael Feeney Jr
"""

__version__ = "0.1.0"

# Test configuration
TEST_DATA_DIR = "test_data"
TEST_OUTPUT_DIR = "test_outputs"

# Test tolerances
TOLERANCES = {
    "temperature": 0.1,      # °C
    "pressure": 1.0,         # PSI
    "percentage": 0.5,       # %
    "concentration": 10.0,   # ppm
    "time": 0.1,             # minutes
    "distance": 0.01,        # meters
    "strength": 0.1          # MPa
}

# Physical limits for validation
PHYSICAL_LIMITS = {
    "temperature_min": -273.15,  # Absolute zero
    "temperature_max": 200.0,
    "pressure_min": 0.0,
    "pressure_max": 100.0,
    "ph_min": 0.0,
    "ph_max": 14.0,
    "porosity_min": 0.0,
    "porosity_max": 1.0,
    "concentration_max": 10000.0  # ppm
}
