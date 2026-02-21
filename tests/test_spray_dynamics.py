"""
Unit Tests for Spray Dynamics Module

Tests spray expansion modeling, coverage calculations, and 
environmental factor effects.

Author: Don Michael Feeney Jr
"""

import pytest
import numpy as np
from spray_dynamics import SprayDynamics, SprayParameters, SprayResults


class TestSprayParameters:
    """Test SprayParameters dataclass."""
    
    def test_default_parameters(self):
        """Test default parameter values."""
        params = SprayParameters()
        assert params.pressure_psi == 25.0
        assert params.ambient_temp_c == 0.0
        assert params.surface_slope == 0.0
        assert params.viscosity_cp == 3000.0
        
    def test_custom_parameters(self):
        """Test custom parameter initialization."""
        params = SprayParameters(
            pressure_psi=30.0,
            ambient_temp_c=20.0,
            surface_slope=10.0
        )
        assert params.pressure_psi == 30.0
        assert params.ambient_temp_c == 20.0
        assert params.surface_slope == 10.0


class TestSprayDynamics:
    """Test SprayDynamics simulation class."""
    
    @pytest.fixture
    def simulator(self):
        """Create standard simulator instance."""
        params = SprayParameters(
            pressure_psi=25.0,
            ambient_temp_c=0.0,
            surface_slope=0.0
        )
        return SprayDynamics(params)
    
    def test_initialization(self, simulator):
        """Test simulator initialization."""
        assert simulator.params.pressure_psi == 25.0
    
    def test_viscosity_factor_at_reference_temp(self, simulator):
        """Test viscosity factor at reference temperature (20°C)."""
        simulator.params.ambient_temp_c = 20.0
        factor = simulator.calculate_viscosity_factor()
        # At reference temp, factor should be ~1.0
        assert 0.95 <= factor <= 1.05
    
    def test_viscosity_factor_cold_temp(self, simulator):
        """Test viscosity increases at cold temperatures."""
        simulator.params.ambient_temp_c = -20.0
        factor = simulator.calculate_viscosity_factor()
        # Cold temperature increases viscosity (factor > 1)
        assert factor > 1.0
    
    def test_viscosity_factor_hot_temp(self, simulator):
        """Test viscosity decreases at hot temperatures."""
        simulator.params.ambient_temp_c = 40.0
        factor = simulator.calculate_viscosity_factor()
        # Hot temperature decreases viscosity (factor < 1)
        assert factor < 1.0
    
    def test_coverage_radius_positive(self, simulator):
        """Test coverage radius is always positive."""
        radius = simulator.calculate_coverage_radius(volume_ml=500)
        assert radius > 0
    
    def test_coverage_radius_scales_with_volume(self, simulator):
        """Test radius increases with volume."""
        radius_250 = simulator.calculate_coverage_radius(volume_ml=250)
        radius_500 = simulator.calculate_coverage_radius(volume_ml=500)
        radius_1000 = simulator.calculate_coverage_radius(volume_ml=1000)
        
        assert radius_250 < radius_500 < radius_1000
    
    def test_pressure_effect_on_radius(self):
        """Test higher pressure increases spread."""
        params_low = SprayParameters(pressure_psi=20.0)
        params_high = SprayParameters(pressure_psi=30.0)
        
        sim_low = SprayDynamics(params_low)
        sim_high = SprayDynamics(params_high)
        
        radius_low = sim_low.calculate_coverage_radius(volume_ml=500)
        radius_high = sim_high.calculate_coverage_radius(volume_ml=500)
        
        assert radius_high > radius_low
    
    def test_slope_effect_on_radius(self):
        """Test slope reduces spread."""
        params_flat = SprayParameters(surface_slope=0.0)
        params_sloped = SprayParameters(surface_slope=10.0)
        
        sim_flat = SprayDynamics(params_flat)
        sim_sloped = SprayDynamics(params_sloped)
        
        radius_flat = sim_flat.calculate_coverage_radius(volume_ml=500)
        radius_sloped = sim_sloped.calculate_coverage_radius(volume_ml=500)
        
        assert radius_flat > radius_sloped
    
    def test_simulate_radial_expansion_returns_results(self, simulator):
        """Test simulation returns SprayResults."""
        results = simulator.simulate_radial_expansion(volume_ml=500)
        
        assert isinstance(results, SprayResults)
        assert hasattr(results, 'time')
        assert hasattr(results, 'radius')
        assert hasattr(results, 'thickness')
        assert hasattr(results, 'coverage_area')
    
    def test_expansion_time_array_length(self, simulator):
        """Test time array has correct length."""
        time_steps = 150
        results = simulator.simulate_radial_expansion(
            volume_ml=500,
            time_steps=time_steps
        )
        
        assert len(results.time) == time_steps
        assert len(results.radius) == time_steps
        assert len(results.thickness) == time_steps
    
    def test_expansion_monotonic_increase(self, simulator):
        """Test radius increases monotonically over time."""
        results = simulator.simulate_radial_expansion(volume_ml=500)
        
        # Check radius is non-decreasing
        radius_diffs = np.diff(results.radius)
        assert np.all(radius_diffs >= 0)
    
    def test_expansion_reaches_max_radius(self, simulator):
        """Test expansion converges to max radius."""
        results = simulator.simulate_radial_expansion(
            volume_ml=500,
            duration_s=60.0
        )
        
        # Final radius should be close to max_radius
        assert results.radius[-1] >= 0.95 * results.max_radius
    
    def test_thickness_decreases_with_expansion(self, simulator):
        """Test thickness decreases as radius increases."""
        results = simulator.simulate_radial_expansion(volume_ml=500)
        
        # Thickness should generally decrease (volume conservation)
        # Check first 90% of expansion
        idx_90 = int(0.9 * len(results.thickness))
        assert results.thickness[idx_90] < results.thickness[0]
    
    def test_volume_conservation(self, simulator):
        """Test volume is approximately conserved."""
        volume_ml = 500.0
        results = simulator.simulate_radial_expansion(volume_ml=volume_ml)
        
        # Calculate volume from final radius and thickness
        # Volume = π * r² * h
        final_volume = (np.pi * results.radius[-1]**2 * 
                       results.thickness[-1] / 1000)  # Convert to m³ then mL
        
        # Should be within 20% (due to spreading model simplifications)
        assert abs(final_volume - volume_ml) / volume_ml < 0.2
    
    def test_coverage_area_calculation(self, simulator):
        """Test coverage area matches radius calculation."""
        results = simulator.simulate_radial_expansion(volume_ml=500)
        expected_area = np.pi * results.max_radius ** 2
        
        # Should match within small tolerance
        assert abs(results.coverage_area - expected_area) < 0.01
    
    def test_estimate_coverage_area(self, simulator):
        """Test direct coverage area estimation."""
        area = simulator.estimate_coverage_area(volume_ml=500)
        assert area > 0
        assert 10 < area < 20  # Reasonable range for 500mL
    
    def test_calculate_optimal_volume(self, simulator):
        """Test optimal volume calculation."""
        target_area = 10.0  # m²
        target_thickness = 1.0  # mm
        
        volume = simulator.calculate_optimal_volume(
            target_area_m2=target_area,
            target_thickness_mm=target_thickness
        )
        
        assert volume > 0
        # Should be roughly target_area * thickness
        # 10 m² * 1 mm = 10,000 mm³ = 10,000 mL
        assert 8000 < volume < 12000  # Allow some variance


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_volume(self):
        """Test handling of zero volume."""
        simulator = SprayDynamics(SprayParameters())
        with pytest.raises(ValueError):
            simulator.calculate_coverage_radius(volume_ml=0)
    
    def test_very_small_volume(self):
        """Test handling of very small volume."""
        simulator = SprayDynamics(SprayParameters())
        radius = simulator.calculate_coverage_radius(volume_ml=1)
        assert radius > 0
        assert radius < 0.1  # Should be very small
    
    def test_very_large_volume(self):
        """Test handling of very large volume."""
        simulator = SprayDynamics(SprayParameters())
        radius = simulator.calculate_coverage_radius(volume_ml=10000)
        assert radius > 0
        assert radius < 50  # Should still be reasonable
    
    def test_extreme_cold_temperature(self):
        """Test extreme cold temperature."""
        params = SprayParameters(ambient_temp_c=-150)
        simulator = SprayDynamics(params)
        radius = simulator.calculate_coverage_radius(volume_ml=500)
        assert radius > 0  # Should still produce valid result
    
    def test_extreme_hot_temperature(self):
        """Test extreme hot temperature."""
        params = SprayParameters(ambient_temp_c=100)
        simulator = SprayDynamics(params)
        radius = simulator.calculate_coverage_radius(volume_ml=500)
        assert radius > 0
    
    def test_steep_slope(self):
        """Test steep slope (near vertical)."""
        params = SprayParameters(surface_slope=15.0)
        simulator = SprayDynamics(params)
        radius = simulator.calculate_coverage_radius(volume_ml=500)
        assert radius > 0
        # Should be significantly reduced
        
        params_flat = SprayParameters(surface_slope=0.0)
        sim_flat = SprayDynamics(params_flat)
        radius_flat = sim_flat.calculate_coverage_radius(volume_ml=500)
        
        assert radius < radius_flat * 0.9


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_simulation_workflow(self):
        """Test complete simulation workflow."""
        # Setup
        params = SprayParameters(
            pressure_psi=25.0,
            ambient_temp_c=0.0,
            surface_slope=5.0
        )
        simulator = SprayDynamics(params)
        
        # Run simulation
        results = simulator.simulate_radial_expansion(
            volume_ml=500,
            duration_s=30.0,
            time_steps=100
        )
        
        # Verify results structure
        assert results.volume_ml == 500
        assert results.max_radius > 0
        assert results.coverage_area > 0
        assert len(results.time) == 100
        
        # Verify physical constraints
        assert results.radius[0] < results.radius[-1]  # Expansion occurred
        assert results.thickness[-1] > 0  # Non-zero thickness
        assert results.coverage_area < 100  # Reasonable coverage
    
    def test_comparison_workflow(self):
        """Test comparing different conditions."""
        volumes = [250, 500, 1000]
        params = SprayParameters()
        simulator = SprayDynamics(params)
        
        results = []
        for vol in volumes:
            res = simulator.simulate_radial_expansion(volume_ml=vol)
            results.append(res)
        
        # Verify increasing volumes give increasing coverage
        for i in range(len(results) - 1):
            assert results[i].coverage_area < results[i+1].coverage_area


class TestNumericalStability:
    """Test numerical stability and convergence."""
    
    def test_time_step_independence(self):
        """Test results are stable with different time steps."""
        simulator = SprayDynamics(SprayParameters())
        
        results_100 = simulator.simulate_radial_expansion(
            volume_ml=500, time_steps=100
        )
        results_200 = simulator.simulate_radial_expansion(
            volume_ml=500, time_steps=200
        )
        
        # Final results should be similar
        assert abs(results_100.max_radius - results_200.max_radius) < 0.1
    
    def test_no_nan_values(self):
        """Test simulation produces no NaN values."""
        simulator = SprayDynamics(SprayParameters())
        results = simulator.simulate_radial_expansion(volume_ml=500)
        
        assert not np.any(np.isnan(results.radius))
        assert not np.any(np.isnan(results.thickness))
        assert not np.isnan(results.coverage_area)
    
    def test_no_infinite_values(self):
        """Test simulation produces no infinite values."""
        simulator = SprayDynamics(SprayParameters())
        results = simulator.simulate_radial_expansion(volume_ml=500)
        
        assert not np.any(np.isinf(results.radius))
        assert not np.any(np.isinf(results.thickness))
        assert not np.isinf(results.coverage_area)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
