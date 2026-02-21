"""
Unit Tests for Nutrient Release Module

Tests nutrient release kinetics, pH evolution, and
plant readiness determination.

Author: Don Michael Feeney Jr
"""

import pytest
import numpy as np
from nutrient_release import (
    NutrientReleaseSimulator,
    NutrientProfile,
    PlantRequirements,
    Nutrient,
)
from utils import NutrientConstants


class TestPlantRequirements:
    """Test PlantRequirements dataclass."""

    def test_default_requirements(self):
        """Test default requirements match lettuce/leafy greens."""
        reqs = PlantRequirements()
        assert reqs.nitrogen_min == 100.0
        assert reqs.phosphorus_min == 30.0
        assert reqs.potassium_min == 150.0
        assert reqs.ph_min == 5.5
        assert reqs.ph_max == 7.0

    def test_custom_requirements(self):
        """Test custom requirement initialization."""
        reqs = PlantRequirements(nitrogen_min=200.0, ph_min=6.0)
        assert reqs.nitrogen_min == 200.0
        assert reqs.ph_min == 6.0
        assert reqs.potassium_min == 150.0  # Default preserved


class TestNutrientReleaseSimulator:
    """Test NutrientReleaseSimulator class."""

    @pytest.fixture
    def simulator(self):
        """Create standard simulator instance."""
        return NutrientReleaseSimulator(initial_ph=10.0)

    def test_initialization(self, simulator):
        """Test simulator initialization."""
        assert simulator.initial_ph == 10.0
        assert simulator.water_factor == 1.0
        assert NutrientConstants.K_MAX == 2000.0

    def test_potassium_release_kinetics(self, simulator):
        """Test potassium release follows sigmoid curve."""
        # Check specific time points
        k_0 = simulator.calculate_potassium_release(0)
        k_30 = simulator.calculate_potassium_release(30)
        k_60 = simulator.calculate_potassium_release(60)

        # At day 0, release should be low
        assert k_0 < NutrientConstants.K_MAX * 0.1

        # At day 30 (delay param), release should be ~50%
        assert 0.4 * NutrientConstants.K_MAX < k_30 < 0.6 * NutrientConstants.K_MAX

        # At day 60, release should be high
        assert k_60 > NutrientConstants.K_MAX * 0.9

        # Check monotonicity
        assert k_0 < k_30 < k_60

    def test_potassium_never_exceeds_max(self, simulator):
        """Test potassium never exceeds maximum."""
        for day in range(0, 61):
            k = simulator.calculate_potassium_release(day)
            assert k <= NutrientConstants.K_MAX * 1.01  # Allow 1% tolerance

    def test_nitrogen_release_kinetics(self, simulator):
        """Test nitrogen biphasic release."""
        n_10 = simulator.calculate_nitrogen_release(10)
        n_30 = simulator.calculate_nitrogen_release(30)

        # Day 10: 10 * 30 = 300
        assert abs(n_10 - 300) < 1.0

        # Day 30: (20 * 30) + (10 * 20) = 600 + 200 = 800
        assert abs(n_30 - 800) < 1.0

    def test_nitrogen_never_exceeds_max(self, simulator):
        """Test nitrogen never exceeds maximum."""
        for day in range(0, 61):
            n = simulator.calculate_nitrogen_release(day)
            assert n <= NutrientConstants.N_MAX * 1.01

    def test_phosphorus_release_kinetics(self, simulator):
        """Test phosphorus delayed release."""
        p_10 = simulator.calculate_phosphorus_release(10)
        p_50 = simulator.calculate_phosphorus_release(50)

        # Early release dominated by urea phosphate
        assert p_10 > 0

        # Major release around day 50
        assert p_50 > p_10

    def test_phosphorus_never_exceeds_max(self, simulator):
        """Test phosphorus never exceeds maximum + urea contribution."""
        for day in range(0, 61):
            p = simulator.calculate_phosphorus_release(day)
            # Max from Ca3(PO4)2 + 50 from urea phosphate
            assert p <= (NutrientConstants.P_MAX + 60)

    def test_magnesium_release_kinetics(self, simulator):
        """Test magnesium linear release after delay."""
        mg_5 = simulator.calculate_magnesium_release(5)
        mg_20 = simulator.calculate_magnesium_release(20)

        # Before start day (10), release is 0
        assert mg_5 == 0

        # Day 20: (20-10) * 12 = 120
        assert abs(mg_20 - 120) < 1.0

    def test_magnesium_never_exceeds_max(self, simulator):
        """Test magnesium never exceeds maximum."""
        for day in range(0, 61):
            mg = simulator.calculate_magnesium_release(day)
            assert mg <= NutrientConstants.MG_MAX * 1.01

    def test_sulfur_linked_to_magnesium(self, simulator):
        """Test sulfur release is proportional to magnesium."""
        days = [10, 20, 40]
        for day in days:
            mg = simulator.calculate_magnesium_release(day)
            s = simulator.calculate_sulfur_release(day)

            # Ratio should be 1.6
            if mg > 0:
                assert abs(s / mg - 1.6) < 0.01

    def test_calcium_linked_to_phosphorus(self, simulator):
        """Test calcium release is linked to phosphorus."""
        p = simulator.calculate_phosphorus_release(40)
        ca = simulator.calculate_calcium_release(40)

        assert ca > 0
        # Should be roughly 1.2x phosphorus
        assert abs(ca / p - 1.2) < 0.2  # Allow wider tolerance due to capping

    def test_ph_evolution(self, simulator):
        """Test pH drops from alkaline to neutral."""
        ph_0 = simulator.calculate_ph(0)
        ph_30 = simulator.calculate_ph(30)
        ph_60 = simulator.calculate_ph(60)

        # Initial pH should match setting
        assert abs(ph_0 - 10.0) < 0.1

        # pH should decrease
        assert ph_0 > ph_30 > ph_60

        # Final pH should be near 6.5
        assert abs(ph_60 - 6.5) < 0.5

    def test_porosity_development(self, simulator):
        """Test porosity increases over time."""
        por_0 = simulator.calculate_porosity(0)
        por_60 = simulator.calculate_porosity(60)

        # Initial porosity (hardened)
        assert abs(por_0 - 0.15) < 0.02

        # Final porosity (degraded)
        assert abs(por_60 - 0.45) < 0.05

        # Should increase
        assert por_60 > por_0

    def test_simulate_release_cycle_returns_profile(self, simulator):
        """Test simulation returns NutrientProfile."""
        profile = simulator.simulate_release_cycle()

        assert isinstance(profile, NutrientProfile)
        assert hasattr(profile, "time_days")
        assert hasattr(profile, "concentrations")
        assert hasattr(profile, "ph_values")

        # Check all nutrients present
        for nutrient in Nutrient:
            assert nutrient in profile.concentrations

    def test_check_plant_readiness_basic(self, simulator):
        """Test plant readiness determination."""
        profile = simulator.simulate_release_cycle(duration_days=60)
        ready_day, status = simulator.check_plant_readiness(profile)

        # Should be ready eventually
        assert ready_day is not None
        assert 15 < ready_day < 50

        # Status should contain details
        assert "n_sufficient" in status
        assert "p_sufficient" in status
        assert "ph_acceptable" in status


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_water_availability(self):
        """Test zero water stops nutrient release."""
        sim = NutrientReleaseSimulator(water_availability=0.0)

        # All soluble nutrients should be 0
        assert sim.calculate_potassium_release(30) == 0
        assert sim.calculate_nitrogen_release(30) == 0
        assert sim.calculate_magnesium_release(30) == 0

        # Phosphorus might be non-zero if modeled as acid-mobilized
        # but in this simplified model, check implementation behavior
        p = sim.calculate_phosphorus_release(30)
        assert p == 0

    def test_very_short_duration(self):
        """Test very short simulation duration."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=5)

        assert len(profile.time_days) > 0
        # Should not be ready
        ready_day, _ = sim.check_plant_readiness(profile)
        assert ready_day is None

    def test_very_long_duration(self):
        """Test very long simulation duration."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=200)

        # Should reach steady state
        final_k = profile.concentrations[Nutrient.POTASSIUM][-1]
        assert abs(final_k - NutrientConstants.K_MAX) < 10.0

    def test_extreme_initial_ph(self):
        """Test extreme initial pH recovery."""
        sim = NutrientReleaseSimulator(initial_ph=14.0)
        ph_60 = sim.calculate_ph(60)

        # Should still drop significantly
        assert ph_60 < 8.0

    def test_strict_plant_requirements(self):
        """Test strict requirements delay readiness."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)

        strict_reqs = PlantRequirements(
            nitrogen_min=1000.0, phosphorus_min=500.0  # Very high
        )

        ready_day, _ = sim.check_plant_readiness(profile, strict_reqs)

        # Should verify readiness is delayed or never achieved
        if ready_day:
            assert ready_day > 30
        else:
            assert ready_day is None

    def test_excessive_water_availability(self):
        """Test handling of excessive water (>1.0)."""
        sim = NutrientReleaseSimulator(water_availability=1.5)

        # Should still work but cap at reasonable values
        k = sim.calculate_potassium_release(30)
        assert k <= NutrientConstants.K_MAX * 1.5


class TestIntegration:
    """Integration tests for nutrient workflows."""

    def test_complete_cycle_consistency(self):
        """Test internal consistency of complete cycle."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)

        # Check pH and nutrients correlate directionally
        # As pH drops, P availability should eventually rise (modeled simplified here)

        # Check data lengths match
        assert len(profile.time_days) == len(profile.ph_values)
        assert len(profile.time_days) == len(profile.concentrations[Nutrient.NITROGEN])

    def test_readiness_requires_all_factors(self):
        """Test readiness requires all nutrients and pH."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)
        reqs = PlantRequirements()

        ready_day, status = sim.check_plant_readiness(profile, reqs)

        # Readiness day should be >= max of individual readiness days
        components = [
            status["n_sufficient"],
            status["p_sufficient"],
            status["k_sufficient"],
            status["ph_acceptable"],
        ]

        # Filter None values
        valid_days = [d for d in components if d is not None]

        if ready_day and valid_days:
            assert ready_day >= max(valid_days)


class TestPhysicalConstraints:
    """Test physical and chemical constraints."""

    def test_ph_bounds(self):
        """Test pH stays within physical bounds (0-14)."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)

        assert np.all(profile.ph_values >= 0.0)
        assert np.all(profile.ph_values <= 14.0)

    def test_porosity_bounds(self):
        """Test porosity stays within 0-1 range."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)

        assert np.all(profile.substrate_porosity >= 0.0)
        assert np.all(profile.substrate_porosity <= 1.0)

    def test_concentrations_non_negative(self):
        """Test nutrient concentrations are never negative."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)

        for nutrient, concs in profile.concentrations.items():
            assert np.all(concs >= 0.0)


class TestNumericalStability:
    """Test numerical stability and convergence."""

    def test_no_nan_values(self):
        """Test simulation produces no NaN values."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)

        assert not np.any(np.isnan(profile.time_days))
        assert not np.any(np.isnan(profile.ph_values))
        assert not np.any(np.isnan(profile.substrate_porosity))
        for concs in profile.concentrations.values():
            assert not np.any(np.isnan(concs))

    def test_no_infinite_values(self):
        """Test simulation produces no infinite values."""
        sim = NutrientReleaseSimulator()
        profile = sim.simulate_release_cycle(duration_days=60)

        assert not np.any(np.isinf(profile.time_days))
        assert not np.any(np.isinf(profile.ph_values))
        assert not np.any(np.isinf(profile.substrate_porosity))
        for concs in profile.concentrations.values():
            assert not np.any(np.isinf(concs))


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
