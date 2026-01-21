"""
Unit Tests for Utils Module

Tests utility functions, constants, data structures, and conversions.

Author: Don Michael Feeney Jr
"""

import pytest
import numpy as np
from utils import (
    PhysicalConstants,
    ChemicalConstants,
    LunarLocation,
    RegolithSample,
    UnitConverter,
    sigmoid,
    arrhenius_factor,
    interpolate_linear,
    moving_average,
    calculate_r_squared,
    validate_temperature,
    validate_pressure,
    validate_percentage,
    format_scientific,
    format_percentage,
    format_duration,
    ConfigManager
)


class TestPhysicalConstants:
    """Test physical constants."""
    
    def test_gravity_constants(self):
        """Test gravity constants are correct."""
        assert PhysicalConstants.GRAVITY_MOON == 1.62
        assert PhysicalConstants.GRAVITY_EARTH == 9.81
        assert PhysicalConstants.GRAVITY_MARS == 3.71
        assert PhysicalConstants.GRAVITY_MOON < PhysicalConstants.GRAVITY_EARTH
    
    def test_lunar_day_length(self):
        """Test lunar day is ~29.5 Earth days."""
        lunar_day_hours = PhysicalConstants.LUNAR_DAY_HOURS
        earth_days = lunar_day_hours / 24
        assert 29 < earth_days < 30
    
    def test_temperature_extremes(self):
        """Test lunar temperature extremes are realistic."""
        assert PhysicalConstants.LUNAR_TEMP_MIN_C < 0
        assert PhysicalConstants.LUNAR_TEMP_MAX_C > 100
        assert PhysicalConstants.LUNAR_TEMP_MAX_C > PhysicalConstants.LUNAR_TEMP_MIN_C


class TestChemicalConstants:
    """Test chemical constants."""
    
    def test_molecular_weights_positive(self):
        """Test all molecular weights are positive."""
        for compound, mw in ChemicalConstants.MW.items():
            assert mw > 0, f"{compound} has non-positive molecular weight"
    
    def test_key_compounds_present(self):
        """Test key compounds are in the database."""
        assert 'K2SiO3' in ChemicalConstants.MW
        assert 'MgSO4' in ChemicalConstants.MW
        assert 'H2O' in ChemicalConstants.MW
    
    def test_water_molecular_weight(self):
        """Test water molecular weight is correct."""
        # H2O = 2*1.008 + 15.999 ≈ 18.015
        assert 18.0 < ChemicalConstants.MW['H2O'] < 18.1
    
    def test_nutrient_masses_present(self):
        """Test essential nutrient atomic masses are present."""
        assert 'N' in ChemicalConstants.NUTRIENT_MASS
        assert 'P' in ChemicalConstants.NUTRIENT_MASS
        assert 'K' in ChemicalConstants.NUTRIENT_MASS


class TestLunarLocation:
    """Test LunarLocation dataclass."""
    
    def test_default_initialization(self):
        """Test default location initialization."""
        loc = LunarLocation(name="Test Site", latitude=0.0, longitude=0.0)
        assert loc.name == "Test Site"
        assert loc.latitude == 0.0
        assert loc.elevation == 0.0
    
    def test_polar_detection(self):
        """Test polar region detection."""
        north_pole = LunarLocation(name="North", latitude=85.0, longitude=0.0)
        south_pole = LunarLocation(name="South", latitude=-85.0, longitude=0.0)
        equator = LunarLocation(name="Equator", latitude=0.0, longitude=0.0)
        
        assert north_pole.is_polar()
        assert south_pole.is_polar()
        assert not equator.is_polar()
    
    def test_permanently_shadowed_detection(self):
        """Test permanently shadowed region detection."""
        psr = LunarLocation(
            name="PSR",
            latitude=-89.5,
            longitude=0.0,
            solar_exposure=0.05
        )
        sunlit = LunarLocation(
            name="Sunlit",
            latitude=0.0,
            longitude=0.0,
            solar_exposure=0.5
        )
        
        assert psr.is_permanently_shadowed()
        assert not sunlit.is_permanently_shadowed()


class TestRegolithSample:
    """Test RegolithSample dataclass."""
    
    def test_jsc1a_default(self):
        """Test JSC-1A default composition."""
        sample = RegolithSample()
        assert sample.name == "JSC-1A"
        assert sample.sio2_percent == 47.0
        assert sample.al2o3_percent == 14.0
    
    def test_composition_validation_valid(self):
        """Test valid composition passes validation."""
        sample = RegolithSample()
        assert sample.validate()
    
    def test_composition_validation_invalid(self):
        """Test invalid composition fails validation."""
        sample = RegolithSample(
            sio2_percent=10.0,
            al2o3_percent=10.0,
            feo_percent=10.0,
            cao_percent=10.0,
            mgo_percent=10.0,
            tio2_percent=10.0,
            others_percent=10.0  # Total = 70%, invalid
        )
        assert not sample.validate()
    
    def test_get_composition_dict(self):
        """Test composition dictionary generation."""
        sample = RegolithSample()
        comp_dict = sample.get_composition_dict()
        
        assert isinstance(comp_dict, dict)
        assert 'SiO2' in comp_dict
        assert 'Al2O3' in comp_dict
        assert comp_dict['SiO2'] == sample.sio2_percent


class TestSigmoid:
    """Test sigmoid function."""
    
    def test_sigmoid_at_midpoint(self):
        """Test sigmoid equals 0.5 at midpoint."""
        result = sigmoid(0.0, midpoint=0.0, steepness=1.0)
        assert abs(result - 0.5) < 0.01
    
    def test_sigmoid_range(self):
        """Test sigmoid output is between 0 and 1."""
        x_values = np.linspace(-10, 10, 100)
        y_values = sigmoid(x_values, midpoint=0.0, steepness=1.0)
        
        assert np.all(y_values >= 0)
        assert np.all(y_values <= 1)
    
    def test_sigmoid_monotonic(self):
        """Test sigmoid is monotonically increasing."""
        x_values = np.linspace(-10, 10, 100)
        y_values = sigmoid(x_values, midpoint=0.0, steepness=1.0)
        
        diffs = np.diff(y_values)
        assert np.all(diffs >= 0)
    
    def test_sigmoid_asymptotes(self):
        """Test sigmoid approaches 0 and 1 at extremes."""
        y_negative = sigmoid(-100, midpoint=0.0, steepness=1.0)
        y_positive = sigmoid(100, midpoint=0.0, steepness=1.0)
        
        assert y_negative < 0.01
        assert y_positive > 0.99


class TestArrheniusFactor:
    """Test Arrhenius factor calculation."""
    
    def test_at_reference_temperature(self):
        """Test factor equals 1 at reference temperature."""
        factor = arrhenius_factor(25.0, 45.0, reference_temp_c=25.0)
        assert abs(factor - 1.0) < 0.01
    
    def test_increases_with_temperature(self):
        """Test factor increases with temperature."""
        factor_low = arrhenius_factor(0.0, 45.0, reference_temp_c=25.0)
        factor_high = arrhenius_factor(50.0, 45.0, reference_temp_c=25.0)
        
        assert factor_high > factor_low
    
    def test_positive_for_all_temperatures(self):
        """Test factor is always positive."""
        temps = np.linspace(-50, 100, 50)
        for temp in temps:
            factor = arrhenius_factor(temp, 45.0, reference_temp_c=25.0)
            assert factor > 0


class TestUnitConverter:
    """Test unit conversion functions."""
    
    def test_celsius_to_kelvin(self):
        """Test Celsius to Kelvin conversion."""
        assert abs(UnitConverter.celsius_to_kelvin(0) - 273.15) < 0.01
        assert abs(UnitConverter.celsius_to_kelvin(100) - 373.15) < 0.01
    
    def test_kelvin_to_celsius(self):
        """Test Kelvin to Celsius conversion."""
        assert abs(UnitConverter.kelvin_to_celsius(273.15) - 0) < 0.01
        assert abs(UnitConverter.kelvin_to_celsius(373.15) - 100) < 0.01
    
    def test_temperature_round_trip(self):
        """Test temperature conversions are reversible."""
        temp_c = 25.0
        temp_k = UnitConverter.celsius_to_kelvin(temp_c)
        temp_c_back = UnitConverter.kelvin_to_celsius(temp_k)
        
        assert abs(temp_c - temp_c_back) < 0.01
    
    def test_psi_to_pascal(self):
        """Test PSI to Pascal conversion."""
        pascals = UnitConverter.psi_to_pascal(1.0)
        assert 6800 < pascals < 6900  # ~6895 Pa
    
    def test_ml_to_cubic_meters(self):
        """Test mL to m³ conversion."""
        m3 = UnitConverter.ml_to_cubic_meters(1000)
        assert abs(m3 - 0.001) < 1e-6
    
    def test_kwh_to_joules(self):
        """Test kWh to Joules conversion."""
        joules = UnitConverter.kwh_to_joules(1.0)
        assert abs(joules - 3.6e6) < 1e3


class TestMathematicalUtilities:
    """Test mathematical utility functions."""
    
    def test_interpolate_linear(self):
        """Test linear interpolation."""
        x_points = [0, 10, 20]
        y_points = [0, 100, 200]
        
        result = interpolate_linear(5, x_points, y_points)
        assert abs(result - 50) < 0.01
    
    def test_moving_average_smooths(self):
        """Test moving average smooths data."""
        noisy_data = np.random.randn(100) + np.linspace(0, 10, 100)
        smoothed = moving_average(noisy_data, window_size=5)
        
        # Smoothed should have less variance
        assert np.std(smoothed) < np.std(noisy_data[2:-2])
    
    def test_moving_average_length(self):
        """Test moving average output length."""
        data = np.arange(100)
        window = 5
        smoothed = moving_average(data, window)
        
        assert len(smoothed) == len(data) - window + 1
    
    def test_r_squared_perfect_fit(self):
        """Test R² equals 1 for perfect fit."""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = y_true.copy()
        
        r2 = calculate_r_squared(y_true, y_pred)
        assert abs(r2 - 1.0) < 0.01
    
    def test_r_squared_poor_fit(self):
        """Test R² is low for poor fit."""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([5, 4, 3, 2, 1])  # Reversed
        
        r2 = calculate_r_squared(y_true, y_pred)
        assert r2 < 0.0  # Negative for worse than mean


class TestValidationFunctions:
    """Test validation utility functions."""
    
    def test_validate_temperature_valid(self):
        """Test valid temperatures pass validation."""
        assert validate_temperature(0.0)
        assert validate_temperature(25.0)
        assert validate_temperature(-100.0)
    
    def test_validate_temperature_invalid(self):
        """Test invalid temperatures raise ValueError."""
        with pytest.raises(ValueError):
            validate_temperature(-300.0)  # Below absolute zero
        
        with pytest.raises(ValueError):
            validate_temperature(300.0, max_temp=200.0)
    
    def test_validate_pressure_valid(self):
        """Test valid pressures pass validation."""
        assert validate_pressure(25.0)
        assert validate_pressure(0.0)
    
    def test_validate_pressure_invalid(self):
        """Test invalid pressures raise ValueError."""
        with pytest.raises(ValueError):
            validate_pressure(-5.0)
        
        with pytest.raises(ValueError):
            validate_pressure(150.0, max_pressure=100.0)
    
    def test_validate_percentage_valid(self):
        """Test valid percentages pass validation."""
        assert validate_percentage(50.0)
        assert validate_percentage(0.0)
        assert validate_percentage(100.0)
    
    def test_validate_percentage_invalid(self):
        """Test invalid percentages raise ValueError."""
        with pytest.raises(ValueError):
            validate_percentage(-5.0)
        
        with pytest.raises(ValueError):
            validate_percentage(150.0)


class TestFormattingFunctions:
    """Test formatting utility functions."""
    
    def test_format_scientific(self):
        """Test scientific notation formatting."""
        result = format_scientific(0.00123, precision=2)
        assert "1.23e" in result or "1.23E" in result
    
    def test_format_percentage(self):
        """Test percentage formatting."""
        result = format_percentage(0.856, precision=1)
        assert "85.6%" == result
        
        result = format_percentage(85.6, precision=1)
        assert "85.6%" == result
    
    def test_format_duration_hours(self):
        """Test duration formatting with hours."""
        result = format_duration(7385)  # 2h 3m 5s
        assert "2h" in result
        assert "3m" in result
        assert "5s" in result
    
    def test_format_duration_minutes(self):
        """Test duration formatting with minutes only."""
        result = format_duration(185)  # 3m 5s
        assert "3m" in result
        assert "5s" in result
        assert "h" not in result
    
    def test_format_duration_seconds(self):
        """Test duration formatting with seconds only."""
        result = format_duration(45)  # 45s
        assert "45s" in result
        assert "m" not in result


class TestConfigManager:
    """Test configuration management."""
    
    def test_initialization(self, temp_dir):
        """Test config manager initialization."""
        config_dir = temp_dir / "config"
        mgr = ConfigManager(config_dir)
        
        assert mgr.config_dir == config_dir
        assert config_dir.exists()
    
    def test_save_and_load_config(self, temp_dir):
        """Test saving and loading configuration."""
        mgr = ConfigManager(temp_dir / "config")
        
        test_config = {
            'parameter1': 25.0,
            'parameter2': 'test_value',
            'parameter3': [1, 2, 3]
        }
        
        mgr.save_config(test_config, "test_config")
        loaded_config = mgr.load_config("test_config")
        
        assert loaded_config == test_config
    
    def test_list_configs(self, temp_dir):
        """Test listing available configurations."""
        mgr = ConfigManager(temp_dir / "config")
        
        mgr.save_config({'a': 1}, "config1")
        mgr.save_config({'b': 2}, "config2")
        
        configs = mgr.list_configs()
        
        assert "config1" in configs
        assert "config2" in configs


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_sigmoid_with_array(self):
        """Test sigmoid works with numpy arrays."""
        x_array = np.array([0, 1, 2, 3])
        result = sigmoid(x_array, midpoint=1.5, steepness=1.0)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == len(x_array)
    
    def test_moving_average_small_window(self):
        """Test moving average with window size 1."""
        data = np.array([1, 2, 3, 4, 5])
        result = moving_average(data, window_size=1)
        
        # Window size 1 should return original data
        np.testing.assert_array_equal(result, data)
    
    def test_r_squared_constant_predictions(self):
        """Test R² with constant predictions."""
        y_true = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([3, 3, 3, 3, 3])  # Constant
        
        r2 = calculate_r_squared(y_true, y_pred)
        assert r2 == 0.0  # Predicting mean gives R² = 0


class TestIntegration:
    """Integration tests for utility combinations."""
    
    def test_temperature_conversion_chain(self):
        """Test chained temperature conversions."""
        temp_c = 25.0
        temp_k = UnitConverter.celsius_to_kelvin(temp_c)
        
        # Validate
        validate_temperature(temp_c)
        
        # Convert back
        temp_c_back = UnitConverter.kelvin_to_celsius(temp_k)
        
        assert abs(temp_c - temp_c_back) < 0.01
    
    def test_location_with_validation(self):
        """Test lunar location with parameter validation."""
        location = LunarLocation(
            name="Test Site",
            latitude=45.0,
            longitude=90.0,
            avg_temp_c=-20.0
        )
        
        # Validate temperature
        validate_temperature(location.avg_temp_c)
        
        # Validate solar exposure as percentage
        validate_percentage(location.solar_exposure * 100)
        
        assert True  # Should not raise exceptions


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
