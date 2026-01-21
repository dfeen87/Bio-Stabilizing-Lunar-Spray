"""
Unit Tests for Nutrient Release Module

Tests nutrient release kinetics, pH evolution, and substrate
readiness for plant growth.

Author: Don Michael Feeney Jr
"""

import pytest
import numpy as np
from nutrient_release import (
    NutrientReleaseSimulator,
    NutrientProfile,
    PlantRequirements,
    Nutrient
)


class TestPlantRequirements:
    """Test PlantRequirements dataclass."""
    
    def test_default_requirements(self):
        """Test default plant nutrient requirements."""
        req = PlantRequirements()
        
        assert req.nitrogen_min == 100.0
        assert req.nitrogen_max == 200.0
        assert req.phosphorus_min == 30.0
        assert req.potassium_min == 150.0
        assert req.ph_min == 5.5
        assert req.ph_max == 7.0
    
    def test_custom_requirements(self):
        """Test custom plant requirements."""
        req = PlantRequirements(
            nitrogen_min=150.0,
            phosphorus_min=50.0,
            ph_min=6.0
        )
        
        assert req.nitrogen_min == 150.0
        assert req.phosphorus_min == 50.0
        assert req.ph_min == 6.0


class TestNutrientReleaseSimulator:
    """Test NutrientReleaseSimulator class."""
    
    @pytest.fixture
    def simulator(self):
        """Create standard simulator instance."""
        return NutrientReleaseSimulator(
            initial_ph=10.0,
            water_availability=1.0
        )
    
    def test_initialization(self, simulator):
        """Test simulator initialization."""
        assert simulator.initial_ph == 10.0
        assert simulator.water_factor == 1.0
        assert simulator.K_MAX == 2000.0
        assert simulator.N_MAX == 1500.0
    
    def test_potassium_release_starts_low(self, simulator):
        """Test potassium release starts near zero."""
        k_day0 = simulator.calculate_potassium_release(0)
        assert k_day0 < 100  # Should be very low initially
    
    def test_potassium_release_increases(self, simulator):
        """Test potassium release increases over time."""
        k_day10 = simulator.calculate_potassium_release(10)
        k_day20 = simulator.calculate_potassium_release(20)
        k_day30 = simulator.calculate_potassium_release(30)
        
        assert k_day10 < k_day20 < k_day30
    
    def test_potassium_release_plateaus(self, simulator):
        """Test potassium release plateaus at maximum."""
        k_day50 = simulator.calculate_potassium_release(50)
        k_day60 = simulator.calculate_potassium_release(60)
        
        # Both should be near K_MAX
        assert k_day50 > 1800
        assert k_day60 > 1800
        # Change should be small
        assert abs(k_day60 - k_day50) < 100
    
    def test_potassium_never_exceeds_max(self, simulator):
        """Test potassium never exceeds maximum."""
        for day in range(0, 61):
            k = simulator.calculate_potassium_release(day)
            assert k <= simulator.K_MAX * 1.01  # Allow 1% tolerance
    
    def test_nitrogen_release_biphasic(self, simulator):
        """Test nitrogen has fast then slow release phases."""
        n_day5 = simulator.calculate_nitrogen_release(5)
        n_day10 = simulator.calculate_nitrogen_release(10)
        n_day15 = simulator.calculate_nitrogen_release(15)
        n_day25 = simulator.calculate_nitrogen_release(25)
        
        # Fast phase (0-20 days)
        fast_rate = (n_day15 - n_day5) / 10
        # Slow phase (20+ days)
        slow_rate = (n_day25 - simulator.calculate_nitrogen_release(20)) / 5
        
        # Fast phase should be faster
        assert fast_rate > slow_rate
    
    def test_nitrogen_never_exceeds_max(self, simulator):
        """Test nitrogen never exceeds maximum."""
        for day in range(0, 61):
            n = simulator.calculate_nitrogen_release(day)
            assert n <= simulator.N_MAX * 1.01
    
    def test_phosphorus_release_delayed(self, simulator):
        """Test phosphorus release is delayed (needs root exudates)."""
        p_day10 = simulator.calculate_phosphorus_release(10)
        p_day20 = simulator.calculate_phosphorus_release(20)
        p_day30 = simulator.calculate_phosphorus_release(30)
        p_day40 = simulator.calculate_phosphorus_release(40)
        
        # Should be low early, increase later
        assert p_day10 < 100
        assert p_day20 < p_day30 < p_day40
    
    def test_phosphorus_never_exceeds_max(self, simulator):
        """Test phosphorus never exceeds maximum + urea contribution."""
        for day in range(0, 61):
            p = simulator.calculate_phosphorus_release(day)
            # Max from Ca3(PO4)2 + 50 from urea phosphate
            assert p <= (simulator.P_MAX + 60)
    
    def test_magnesium_starts_after_delay(self, simulator):
        """Test magnesium release starts after initial delay."""
        mg_day5 = simulator.calculate_magnesium_release(5)
        mg_day15 = simulator.calculate_magnesium_release(15)
        
        # Should be zero before day 10, increasing after
        assert mg_day5 == 0
        assert mg_day15 > 0
    
    def test_magnesium_linear_increase(self, simulator):
        """Test magnesium increases linearly."""
        mg_day15 = simulator.calculate_magnesium_release(15)
        mg_day20 = simulator.calculate_magnesium_release(20)
        mg_day25 = simulator.calculate_magnesium_release(25)
        
        # Linear increase means equal increments
        diff1 = mg_day20 - mg_day15
        diff2 = mg_day25 - mg_day20
        
        assert abs(diff1 - diff2) < 10  # Should be approximately equal
    
    def test_magnesium_never_exceeds_max(self, simulator):
        """Test magnesium never exceeds maximum."""
        for day in range(0, 61):
            mg = simulator.calculate_magnesium_release(day)
            assert mg <= simulator.MG_MAX * 1.01
    
    def test_sulfur_follows_magnesium(self, simulator):
        """Test sulfur release follows magnesium (MgSO4)."""
        for day in [15, 25, 35, 45]:
            mg = simulator.calculate_magnesium_release(day)
            s = simulator.calculate_sulfur_release(day)
            
            # S should be proportional to Mg
            ratio = s / mg if mg > 0 else 0
            assert 1.5 < ratio < 1.7  # Should be ~1.6
    
    def test_calcium_follows_phosphorus(self, simulator):
        """Test calcium release follows phosphorus (Ca3(PO4)2)."""
        for day in [20, 30, 40, 50]:
            p = simulator.calculate_phosphorus_release(day)
            ca = simulator.calculate_calcium_release(day)
            
            # Ca should be proportional to P
            if p > 10:  # Only test when P is significant
                ratio = ca / p
                assert 1.0 < ratio < 1.5  # Should be ~1.2
    
    def test_ph_decreases_over_time(self, simulator):
        """Test pH decreases from alkaline to neutral."""
        ph_day0 = simulator.calculate_ph(0)
        ph_day15 = simulator.calculate_ph(15)
        ph_day30 = simulator.calculate_ph(30)
        ph_day60 = simulator.calculate_ph(60)
        
        assert ph_day0 > ph_day15 > ph_day30 > ph_day60
    
    def test_ph_starts_alkaline(self, simulator):
        """Test pH starts at alkaline level."""
        ph_day0 = simulator.calculate_ph(0)
        assert 9.5 < ph_day0 < 10.5
    
    def test_ph_ends_neutral(self, simulator):
        """Test pH ends at neutral level."""
        ph_day60 = simulator.calculate_ph(60)
        assert 6.0 < ph_day60 < 7.0
    
    def test_porosity_increases(self, simulator):
        """Test substrate porosity increases over time."""
        por_day0 = simulator.calculate_porosity(0)
        por_day30 = simulator.calculate_porosity(30)
        por_day60 = simulator.calculate_porosity(60)
        
        assert por_day0 < por_day30 < por_day60
    
    def test_porosity_starts_low(self, simulator):
        """Test porosity starts low (hardened geopolymer)."""
        por_day0 = simulator.calculate_porosity(0)
        assert 0.10 < por_day0 < 0.20
    
    def test_porosity_ends_permeable(self, simulator):
        """Test porosity ends high (root-permeable)."""
        por_day60 = simulator.calculate_porosity(60)
        assert 0.40 < por_day60 < 0.50
    
    def test_simulate_release_cycle_returns_profile(self, simulator):
        """Test simulation returns NutrientProfile."""
        profile = simulator.simulate_release_cycle(duration_days=60)
        
        assert isinstance(profile, NutrientProfile)
        assert hasattr(profile, 'time_days')
        assert hasattr(profile, 'concentrations')
        assert hasattr(profile, 'ph_values')
        assert hasattr(profile, 'substrate_porosity')
    
    def test_profile_contains_all_nutrients(self, simulator):
        """Test profile contains all six nutrients."""
        profile = simulator.simulate_release_cycle(duration_days=60)
        
        assert Nutrient.NITROGEN in profile.concentrations
        assert Nutrient.PHOSPHORUS in profile.concentrations
        assert Nutrient.POTASSIUM in profile.concentrations
        assert Nutrient.MAGNESIUM in profile.concentrations
        assert Nutrient.SULFUR in profile.concentrations
        assert Nutrient.CALCIUM in profile.concentrations
    
    def test_profile_array_lengths_consistent(self, simulator):
        """Test all profile arrays have same length."""
        time_points = 150
        profile = simulator.simulate_release_cycle(
            duration_days=60,
            time_points=time_points
        )
        
        assert len(profile.time_days) == time_points
        assert len(profile.ph_values) == time_points
        assert len(profile.substrate_porosity) == time_points
        
        for nutrient in profile.concentrations.values():
            assert len(nutrient) == time_points
    
    def test_all_nutrients_non_negative(self, simulator):
        """Test all nutrients are non-negative."""
        profile = simulator.simulate_release_cycle(duration_days=60)
        
        for nutrient, values in profile.concentrations.items():
            assert np.all(values >= 0), f"{nutrient} has negative values"
    
    def test_all_nutrients_increase_overall(self, simulator):
        """Test all nutrients generally increase over time."""
        profile = simulator.simulate_release_cycle(duration_days=60)
        
        for nutrient, values in profile.concentrations.items():
            # Final value should be much higher than initial
            assert values[-1] > values[0] * 2, f"{nutrient} didn't increase sufficiently"


class TestWaterAvailability:
    """Test water availability effects."""
    
    def test_low_water_reduces_release(self):
        """Test low water availability reduces nutrient release."""
        sim_full = NutrientReleaseSimulator(water_availability=1.0)
        sim_limited = NutrientReleaseSimulator(water_availability=0.5)
        
        k_full = sim_full.calculate_potassium_release(30)
        k_limited = sim_limited.calculate_potassium_release(30)
        
        # Limited water should reduce release
        assert k_limited < k_full
        assert k_limited / k_full < 0.6  # Should be roughly half
    
    def test_water_affects_all_nutrients(self):
        """Test water availability affects all nutrients."""
        sim_full = NutrientReleaseSimulator(water_availability=1.0)
        sim_limited = NutrientReleaseSimulator(water_availability=0.7)
        
        day = 30
        
        # Check each nutrient
        assert (sim_limited.calculate_potassium_release(day) < 
                sim_full.calculate_potassium_release(day))
        assert (sim_limited.calculate_nitrogen_release(day) < 
                sim_full.calculate_nitrogen_release(day))
        assert (sim_limited.calculate_phosphorus_release(day) < 
                sim_full.calculate_phosphorus_release(day))


class TestPlantReadiness:
    """Test substrate readiness determination."""
    
    def test_check_plant_readiness(self):
        """Test plant readiness checking."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        requirements = PlantRequirements()
        
        ready_day, status = sim.check_plant_readiness(profile, requirements)
        
        assert ready_day is not None
        assert isinstance(ready_day, int)
        assert 15 < ready_day < 35  # Should be ready in 2-4 weeks
    
    def test_status_dict_structure(self):
        """Test status dictionary contains expected keys."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        requirements = PlantRequirements()
        
        ready_day, status = sim.check_plant_readiness(profile, requirements)
        
        assert 'ready_day' in status
        assert 'n_sufficient' in status
        assert 'p_sufficient' in status
        assert 'k_sufficient' in status
        assert 'ph_acceptable' in status
    
    def test_ready_before_end_of_cycle(self):
        """Test substrate becomes ready before end of 60-day cycle."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        requirements = PlantRequirements()
        
        ready_day, status = sim.check_plant_readiness(profile, requirements)
        
        # Should be ready well before day 60
        assert ready_day < 40
    
    def test_stricter_requirements_delay_readiness(self):
        """Test stricter requirements delay readiness."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        
        req_normal = PlantRequirements()
        req_strict = PlantRequirements(
            nitrogen_min=150.0,
            phosphorus_min=50.0,
            potassium_min=200.0
        )
        
        ready_normal, _ = sim.check_plant_readiness(profile, req_normal)
        ready_strict, _ = sim.check_plant_readiness(profile, req_strict)
        
        # Stricter requirements should delay readiness
        assert ready_strict > ready_normal


class TestNPKRatios:
    """Test NPK nutrient ratios."""
    
    def test_npk_ratios_reasonable(self):
        """Test NPK ratios are in reasonable range for plant growth."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        
        # Check at day 30 (mid-cycle)
        idx = len(profile.time_days) // 2
        
        n = profile.concentrations[Nutrient.NITROGEN][idx]
        p = profile.concentrations[Nutrient.PHOSPHORUS][idx]
        k = profile.concentrations[Nutrient.POTASSIUM][idx]
        
        # NPK ratios for general crops typically 3:1:2 to 5:1:3
        n_to_p = n / p if p > 0 else 0
        k_to_p = k / p if p > 0 else 0
        
        assert 3 < n_to_p < 7  # N:P ratio
        assert 3 < k_to_p < 10  # K:P ratio


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_day_zero_all_nutrients(self):
        """Test all nutrients at day zero."""
        sim = NutrientReleaseSimulator()
        
        k = sim.calculate_potassium_release(0)
        n = sim.calculate_nitrogen_release(0)
        p = sim.calculate_phosphorus_release(0)
        mg = sim.calculate_magnesium_release(0)
        
        # All should be very low or zero
        assert k < 50
        assert n < 10  # Some N from fast release
        assert p < 20  # Small amount from urea phosphate
        assert mg == 0
    
    def test_day_sixty_all_nutrients_present(self):
        """Test all nutrients present at day 60."""
        sim = NutrientReleaseSimulator()
        
        k = sim.calculate_potassium_release(60)
        n = sim.calculate_nitrogen_release(60)
        p = sim.calculate_phosphorus_release(60)
        mg = sim.calculate_magnesium_release(60)
        s = sim.calculate_sulfur_release(60)
        ca = sim.calculate_calcium_release(60)
        
        # All should be well above minimum requirements
        assert k > 1500
        assert n > 1000
        assert p > 200
        assert mg > 400
        assert s > 600
        assert ca > 150
    
    def test_zero_water_availability(self):
        """Test handling of zero water availability."""
        sim = NutrientReleaseSimulator(water_availability=0.0)
        
        k = sim.calculate_potassium_release(30)
        n = sim.calculate_nitrogen_release(30)
        
        # Should be zero or near-zero
        assert k < 10
        assert n < 10
    
    def test_excessive_water_availability(self):
        """Test handling of excessive water (>1.0)."""
        sim = NutrientReleaseSimulator(water_availability=1.5)
        
        # Should still work but cap at reasonable values
        k = sim.calculate_potassium_release(30)
        assert k <= sim.K_MAX * 1.5


class TestPhysicalConstraints:
    """Test physical and chemical constraints."""
    
    def test_ph_in_valid_range(self):
        """Test pH stays in chemically valid range."""
        sim = NutrientReleaseSimulator()
        
        for day in range(0, 61):
            ph = sim.calculate_ph(day)
            assert 5.0 < ph < 12.0  # Valid pH range
    
    def test_porosity_in_valid_range(self):
        """Test porosity stays in valid range (0-1)."""
        sim = NutrientReleaseSimulator()
        
        for day in range(0, 61):
            por = sim.calculate_porosity(day)
            assert 0 < por < 1.0
    
    def test_nutrient_concentrations_realistic(self):
        """Test nutrient concentrations stay realistic for hydroponics."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        
        # Hydroponic solutions typically < 3000 ppm total nutrients
        for nutrient, values in profile.concentrations.items():
            max_value = np.max(values)
            assert max_value < 5000, f"{nutrient} exceeds realistic maximum"


class TestNumericalStability:
    """Test numerical stability and convergence."""
    
    def test_no_nan_values(self):
        """Test simulation produces no NaN values."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        
        assert not np.any(np.isnan(profile.ph_values))
        assert not np.any(np.isnan(profile.substrate_porosity))
        
        for values in profile.concentrations.values():
            assert not np.any(np.isnan(values))
    
    def test_no_infinite_values(self):
        """Test simulation produces no infinite values."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        
        assert not np.any(np.isinf(profile.ph_values))
        assert not np.any(np.isinf(profile.substrate_porosity))
        
        for values in profile.concentrations.values():
            assert not np.any(np.isinf(values))
    
    def test_time_point_independence(self):
        """Test results are stable with different time point counts."""
        sim = NutrientReleaseSimulator()
        
        profile_100 = sim.simulate_release_cycle(
            duration_days=60, time_points=100
        )
        profile_200 = sim.simulate_release_cycle(
            duration_days=60, time_points=200
        )
        
        # Final pH should be similar
        assert abs(profile_100.ph_values[-1] - 
                  profile_200.ph_values[-1]) < 0.1


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_nutrient_cycle(self):
        """Test complete 60-day nutrient release cycle."""
        sim = NutrientReleaseSimulator(initial_ph=10.0)
        profile = sim.simulate_release_cycle(duration_days=60)
        requirements = PlantRequirements()
        
        # Check substrate becomes ready
        ready_day, status = sim.check_plant_readiness(profile, requirements)
        assert ready_day is not None
        assert ready_day < 60
        
        # Check final state
        assert profile.ph_values[-1] < 7.5
        assert profile.substrate_porosity[-1] > 0.3
        assert profile.concentrations[Nutrient.POTASSIUM][-1] > 1500


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
