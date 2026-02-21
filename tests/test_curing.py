"""
Unit Tests for Curing Simulation Module

Tests geopolymer curing kinetics, temperature effects, and
bond strength development.

Author: Don Michael Feeney Jr
"""

import pytest
import numpy as np
from curing_simulation import (
    CuringSimulator,
    CuringProfile,
    CuringPhase,
    RegolithProperties,
)
from utils import CuringConstants


class TestRegolithProperties:
    """Test RegolithProperties dataclass."""

    def test_default_jsc1a_properties(self):
        """Test default JSC-1A simulant properties."""
        regolith = RegolithProperties()
        assert regolith.silica_content == 47.0
        assert regolith.alumina_content == 14.0
        assert regolith.iron_content == 10.5
        assert regolith.particle_size_um == 70.0

    def test_custom_properties(self):
        """Test custom regolith properties."""
        regolith = RegolithProperties(
            silica_content=50.0, alumina_content=15.0, particle_size_um=100.0
        )
        assert regolith.silica_content == 50.0
        assert regolith.alumina_content == 15.0
        assert regolith.particle_size_um == 100.0


class TestCuringSimulator:
    """Test CuringSimulator class."""

    @pytest.fixture
    def simulator(self):
        """Create standard simulator instance."""
        return CuringSimulator(uv_assisted=False)

    @pytest.fixture
    def uv_simulator(self):
        """Create UV-assisted simulator instance."""
        return CuringSimulator(uv_assisted=True)

    def test_initialization(self, simulator):
        """Test simulator initialization."""
        assert simulator.uv_assisted is False
        assert isinstance(simulator.regolith, RegolithProperties)
        assert CuringConstants.MAX_BOND_STRENGTH == 3.5
        assert CuringConstants.BASE_CURE_TIME == 14.0

    def test_uv_initialization(self, uv_simulator):
        """Test UV-assisted initialization."""
        assert uv_simulator.uv_assisted is True
        assert CuringConstants.UV_ACCELERATION == 0.30

    def test_activation_factor_at_reference(self, simulator):
        """Test Arrhenius factor at reference temperature."""
        factor = simulator.calculate_activation_factor(0.0)
        # At reference temp (0°C), factor should be 1.0
        assert abs(factor - 1.0) < 0.01

    def test_activation_factor_increases_with_temp(self, simulator):
        """Test reaction rate increases with temperature."""
        factor_cold = simulator.calculate_activation_factor(-20.0)
        factor_warm = simulator.calculate_activation_factor(20.0)

        # Higher temperature = higher reaction rate
        assert factor_warm > factor_cold

    def test_cure_time_at_zero_celsius(self, simulator):
        """Test cure time at 0°C matches base time."""
        cure_time = simulator.calculate_cure_time(0.0)
        # Should be close to BASE_CURE_TIME (14 min)
        assert 13.0 < cure_time < 15.0

    def test_cure_time_decreases_with_temp(self, simulator):
        """Test cure time decreases at higher temperatures."""
        time_cold = simulator.calculate_cure_time(-20.0)
        time_warm = simulator.calculate_cure_time(20.0)
        time_hot = simulator.calculate_cure_time(40.0)

        assert time_cold > time_warm > time_hot

    def test_uv_acceleration_reduces_cure_time(self, simulator, uv_simulator):
        """Test UV assistance reduces cure time by ~30%."""
        time_standard = simulator.calculate_cure_time(0.0)
        time_uv = uv_simulator.calculate_cure_time(0.0)

        reduction = (time_standard - time_uv) / time_standard
        # Should be approximately 30% reduction
        assert 0.25 < reduction < 0.35

    def test_minimum_cure_time_enforced(self, simulator):
        """Test minimum cure time is enforced."""
        # Even at very high temp, cure time should be >= 2 min
        time = simulator.calculate_cure_time(200.0)
        assert time >= 2.0

    def test_bond_strength_increases_over_time(self, simulator):
        """Test bond strength increases with time."""
        strength_5min = simulator.calculate_bond_strength(5.0, 0.0)
        strength_10min = simulator.calculate_bond_strength(10.0, 0.0)
        strength_20min = simulator.calculate_bond_strength(20.0, 0.0)

        assert strength_5min < strength_10min < strength_20min

    def test_bond_strength_plateau(self, simulator):
        """Test bond strength plateaus at maximum."""
        strength_30min = simulator.calculate_bond_strength(30.0, 0.0)
        strength_60min = simulator.calculate_bond_strength(60.0, 0.0)

        # Should both be near MAX_BOND_STRENGTH
        assert strength_30min > 3.0
        assert strength_60min > 3.0
        # Change between 30 and 60 min should be small
        assert abs(strength_60min - strength_30min) < 0.5

    def test_bond_strength_never_exceeds_max(self, simulator):
        """Test bond strength never exceeds maximum."""
        for time in [10, 20, 30, 60, 120]:
            strength = simulator.calculate_bond_strength(time, 0.0)
            assert (
                strength <= CuringConstants.MAX_BOND_STRENGTH * 1.01
            )  # Allow 1% tolerance

    def test_curing_phase_determination(self, simulator):
        """Test curing phase identification."""
        assert simulator.get_curing_phase(0.05) == CuringPhase.INITIAL
        assert simulator.get_curing_phase(0.30) == CuringPhase.SETTING
        assert simulator.get_curing_phase(0.70) == CuringPhase.HARDENING
        assert simulator.get_curing_phase(0.98) == CuringPhase.MATURE

    def test_simulate_curing_returns_profile(self, simulator):
        """Test simulation returns CuringProfile."""
        profile = simulator.simulate_curing(temperature_c=0.0)

        assert isinstance(profile, CuringProfile)
        assert hasattr(profile, "time")
        assert hasattr(profile, "cure_fraction")
        assert hasattr(profile, "bond_strength_mpa")
        assert profile.temperature_c == 0.0
        assert profile.uv_assisted is False

    def test_cure_fraction_array_length(self, simulator):
        """Test cure fraction array has correct length."""
        time_steps = 150
        profile = simulator.simulate_curing(temperature_c=0.0, time_steps=time_steps)

        assert len(profile.time) == time_steps
        assert len(profile.cure_fraction) == time_steps
        assert len(profile.bond_strength_mpa) == time_steps

    def test_cure_fraction_bounds(self, simulator):
        """Test cure fraction stays between 0 and 1."""
        profile = simulator.simulate_curing(temperature_c=0.0)

        assert np.all(profile.cure_fraction >= 0)
        assert np.all(profile.cure_fraction <= 1.0)

    def test_cure_fraction_monotonic(self, simulator):
        """Test cure fraction increases monotonically."""
        profile = simulator.simulate_curing(temperature_c=0.0)

        # Check cure fraction is non-decreasing
        diffs = np.diff(profile.cure_fraction)
        assert np.all(diffs >= -1e-10)  # Allow small numerical errors

    def test_bond_strength_follows_cure_fraction(self, simulator):
        """Test bond strength correlates with cure fraction."""
        profile = simulator.simulate_curing(temperature_c=0.0)

        # At 50% cure, strength should be roughly 50% of max
        idx_50 = np.argmin(np.abs(profile.cure_fraction - 0.5))
        strength_at_50 = profile.bond_strength_mpa[idx_50]

        assert 1.5 < strength_at_50 < 2.0  # ~50% of 3.5 MPa

    def test_compare_temperatures(self, simulator):
        """Test temperature comparison functionality."""
        temps = [-20, 0, 20, 40]
        profiles = simulator.compare_temperatures(temps)

        assert len(profiles) == len(temps)
        for profile, temp in zip(profiles, temps):
            assert isinstance(profile, CuringProfile)
            assert profile.temperature_c == temp


class TestTemperatureEffects:
    """Test temperature-dependent behavior."""

    def test_cold_environment_slows_curing(self):
        """Test curing is slower in cold environment."""
        sim = CuringSimulator(uv_assisted=False)

        profile_cold = sim.simulate_curing(-20.0, duration_min=30)
        profile_normal = sim.simulate_curing(0.0, duration_min=30)

        # At same time point, cold should have lower cure fraction
        assert profile_cold.cure_fraction[-1] < profile_normal.cure_fraction[-1]

    def test_hot_environment_speeds_curing(self):
        """Test curing is faster in hot environment."""
        sim = CuringSimulator(uv_assisted=False)

        profile_normal = sim.simulate_curing(0.0, duration_min=30)
        profile_hot = sim.simulate_curing(40.0, duration_min=30)

        # At same time point, hot should have higher cure fraction
        assert profile_hot.cure_fraction[-1] > profile_normal.cure_fraction[-1]

    def test_extreme_cold_still_cures(self):
        """Test curing still occurs at extreme cold."""
        sim = CuringSimulator(uv_assisted=False)
        profile = sim.simulate_curing(-100.0, duration_min=60)

        # Should still show some curing progress
        assert profile.cure_fraction[-1] > 0.1
        assert profile.bond_strength_mpa[-1] > 0.5


class TestUVEffects:
    """Test UV-assisted curing effects."""

    def test_uv_accelerates_curing(self):
        """Test UV assistance accelerates curing."""
        sim_standard = CuringSimulator(uv_assisted=False)
        sim_uv = CuringSimulator(uv_assisted=True)

        profile_standard = sim_standard.simulate_curing(0.0, duration_min=20)
        profile_uv = sim_uv.simulate_curing(0.0, duration_min=20)

        # UV should achieve higher cure fraction in same time
        assert profile_uv.cure_fraction[-1] > profile_standard.cure_fraction[-1]

    def test_uv_increases_bond_strength_rate(self):
        """Test UV increases bond strength development rate."""
        sim_standard = CuringSimulator(uv_assisted=False)
        sim_uv = CuringSimulator(uv_assisted=True)

        profile_standard = sim_standard.simulate_curing(0.0, duration_min=15)
        profile_uv = sim_uv.simulate_curing(0.0, duration_min=15)

        # UV should achieve higher strength in same time
        assert profile_uv.bond_strength_mpa[-1] > profile_standard.bond_strength_mpa[-1]

    def test_uv_benefit_consistent_across_temps(self):
        """Test UV benefit is consistent across temperatures."""
        sim_standard = CuringSimulator(uv_assisted=False)
        sim_uv = CuringSimulator(uv_assisted=True)

        for temp in [-20, 0, 20]:
            time_standard = sim_standard.calculate_cure_time(temp)
            time_uv = sim_uv.calculate_cure_time(temp)

            speedup = time_standard / time_uv
            # Should be roughly 30% faster (1 / 0.7 ≈ 1.43)
            assert 1.35 < speedup < 1.50


class TestRegolithComposition:
    """Test regolith composition effects."""

    def test_high_alumina_accelerates_curing(self):
        """Test higher Al2O3 content accelerates geopolymerization."""
        regolith_normal = RegolithProperties(alumina_content=14.0)
        regolith_high_al = RegolithProperties(alumina_content=20.0)

        sim_normal = CuringSimulator(uv_assisted=False, regolith=regolith_normal)
        sim_high_al = CuringSimulator(uv_assisted=False, regolith=regolith_high_al)

        time_normal = sim_normal.calculate_cure_time(0.0)
        time_high_al = sim_high_al.calculate_cure_time(0.0)

        # Higher alumina should cure faster
        assert time_high_al < time_normal

    def test_low_alumina_slows_curing(self):
        """Test lower Al2O3 content slows geopolymerization."""
        regolith_normal = RegolithProperties(alumina_content=14.0)
        regolith_low_al = RegolithProperties(alumina_content=10.0)

        sim_normal = CuringSimulator(uv_assisted=False, regolith=regolith_normal)
        sim_low_al = CuringSimulator(uv_assisted=False, regolith=regolith_low_al)

        time_normal = sim_normal.calculate_cure_time(0.0)
        time_low_al = sim_low_al.calculate_cure_time(0.0)

        # Lower alumina should cure slower
        assert time_low_al > time_normal


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_time(self):
        """Test behavior at time zero."""
        sim = CuringSimulator()
        strength = sim.calculate_bond_strength(0.0, 0.0)

        # At time zero, strength should be very low but not negative
        assert 0 <= strength < 0.1

    def test_very_long_cure_time(self):
        """Test very long curing times."""
        sim = CuringSimulator()
        profile = sim.simulate_curing(0.0, duration_min=240)

        # Should be fully cured
        assert profile.cure_fraction[-1] > 0.99
        assert profile.bond_strength_mpa[-1] > 3.4

    def test_negative_temperature_handling(self):
        """Test handling of negative temperatures."""
        sim = CuringSimulator()

        # Should not raise exception
        cure_time = sim.calculate_cure_time(-50.0)
        assert cure_time > 0

        profile = sim.simulate_curing(-50.0, duration_min=30)
        assert len(profile.time) > 0


class TestPhysicalConstraints:
    """Test physical and chemical constraints."""

    def test_cure_fraction_never_exceeds_one(self):
        """Test cure fraction never exceeds 100%."""
        sim = CuringSimulator()

        # Try various conditions
        for temp in [-50, 0, 50]:
            for duration in [30, 60, 120]:
                profile = sim.simulate_curing(temp, duration_min=duration)
                assert np.all(profile.cure_fraction <= 1.0)

    def test_bond_strength_physically_realistic(self):
        """Test bond strength stays in physically realistic range."""
        sim = CuringSimulator()

        # Geopolymers typically achieve 3-10 MPa
        for temp in [-20, 0, 20, 40]:
            profile = sim.simulate_curing(temp, duration_min=60)
            max_strength = np.max(profile.bond_strength_mpa)

            assert 0 <= max_strength <= 6.0  # Upper bound for safety

    def test_curing_is_irreversible(self):
        """Test cure fraction never decreases (irreversible process)."""
        sim = CuringSimulator()
        profile = sim.simulate_curing(0.0, duration_min=60)

        diffs = np.diff(profile.cure_fraction)
        # Should never decrease (allowing tiny numerical errors)
        assert np.all(diffs >= -1e-10)


class TestNumericalStability:
    """Test numerical stability and convergence."""

    def test_no_nan_values(self):
        """Test simulation produces no NaN values."""
        sim = CuringSimulator()
        profile = sim.simulate_curing(0.0, duration_min=30)

        assert not np.any(np.isnan(profile.cure_fraction))
        assert not np.any(np.isnan(profile.bond_strength_mpa))

    def test_no_infinite_values(self):
        """Test simulation produces no infinite values."""
        sim = CuringSimulator()
        profile = sim.simulate_curing(0.0, duration_min=30)

        assert not np.any(np.isinf(profile.cure_fraction))
        assert not np.any(np.isinf(profile.bond_strength_mpa))

    def test_time_step_convergence(self):
        """Test results converge with finer time steps."""
        sim = CuringSimulator()

        profile_100 = sim.simulate_curing(0.0, duration_min=30, time_steps=100)
        profile_200 = sim.simulate_curing(0.0, duration_min=30, time_steps=200)

        # Final values should be very similar
        assert abs(profile_100.cure_fraction[-1] - profile_200.cure_fraction[-1]) < 0.01


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_curing_cycle(self):
        """Test complete curing cycle from start to finish."""
        sim = CuringSimulator(uv_assisted=True)
        regolith = RegolithProperties()

        # Run simulation
        profile = sim.simulate_curing(
            temperature_c=0.0, duration_min=30.0, time_steps=150
        )

        # Verify complete cycle
        assert profile.cure_fraction[0] < 0.1  # Starts low
        assert profile.cure_fraction[-1] > 0.9  # Ends high
        assert profile.bond_strength_mpa[0] < 0.5  # Starts low
        assert profile.bond_strength_mpa[-1] > 3.0  # Ends strong

    def test_multi_temperature_comparison(self):
        """Test comparing multiple temperature conditions."""
        sim = CuringSimulator(uv_assisted=False)
        temps = [-20, 0, 20, 40]

        profiles = sim.compare_temperatures(temps, duration_min=30)

        # Verify ordering: higher temp = faster curing
        final_cures = [p.cure_fraction[-1] for p in profiles]
        assert all(
            final_cures[i] <= final_cures[i + 1] for i in range(len(final_cures) - 1)
        )


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
