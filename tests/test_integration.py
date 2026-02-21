"""
Integration Tests for Complete System

Tests end-to-end workflows, multi-module interactions, and
complete mission simulations.

Author: Don Michael Feeney Jr
"""

import pytest
import numpy as np
from datetime import datetime

from spray_dynamics import SprayDynamics, SprayParameters
from curing_simulation import CuringSimulator
from nutrient_release import NutrientReleaseSimulator, PlantRequirements, Nutrient
from environmental_control import AIEnvironmentalController, ControlMode
from integrated_simulation import IntegratedLunarSpraySimulation, MissionParameters


@pytest.mark.integration
class TestSprayToCuringPipeline:
    """Test integration between spray application and curing."""

    def test_spray_coverage_supports_curing(self):
        """Test spray coverage is adequate for curing."""
        # Apply spray
        spray_params = SprayParameters(pressure_psi=25.0, ambient_temp_c=0.0)
        spray_sim = SprayDynamics(spray_params)
        spray_results = spray_sim.simulate_radial_expansion(volume_ml=500)

        # Cure the sprayed area
        curing_sim = CuringSimulator(uv_assisted=True)
        curing_profile = curing_sim.simulate_curing(
            temperature_c=spray_params.ambient_temp_c, duration_min=30
        )

        # Verify integration
        assert spray_results.coverage_area > 10.0  # At least 10 m²
        assert curing_profile.bond_strength_mpa[-1] > 3.0  # Strong bond
        assert spray_results.thickness[-1] > 0.5  # Adequate thickness

    def test_temperature_consistency(self):
        """Test temperature is consistently used across modules."""
        temp = -20.0

        # Spray at cold temp
        spray_params = SprayParameters(ambient_temp_c=temp)
        spray_sim = SprayDynamics(spray_params)

        # Cure at same temp
        curing_sim = CuringSimulator(uv_assisted=False)
        cure_time = curing_sim.calculate_cure_time(temp)

        # Both should reflect cold temperature effects
        assert cure_time > 15.0  # Slower curing in cold


@pytest.mark.integration
class TestCuringToNutrientsPipeline:
    """Test integration between curing and nutrient release."""

    def test_cured_surface_supports_nutrients(self):
        """Test cured surface transitions to nutrient release."""
        # Complete curing
        curing_sim = CuringSimulator(uv_assisted=True)
        curing_profile = curing_sim.simulate_curing(temperature_c=0.0)

        # Start nutrient release
        nutrient_sim = NutrientReleaseSimulator(initial_ph=10.0)
        nutrient_profile = nutrient_sim.simulate_release_cycle(duration_days=60)

        # Verify transition
        assert curing_profile.cure_fraction[-1] > 0.95  # Fully cured
        assert nutrient_profile.ph_values[0] > 9.0  # Starts alkaline
        assert nutrient_profile.ph_values[-1] < 7.5  # Ends neutral

    def test_ph_evolution_timeline(self):
        """Test pH evolution from curing to biological phase."""
        # Curing creates alkaline surface
        nutrient_sim = NutrientReleaseSimulator(initial_ph=10.5)

        # Track pH over 60 days
        profile = nutrient_sim.simulate_release_cycle(duration_days=60)

        # pH should steadily decrease
        ph_values = profile.ph_values
        diffs = np.diff(ph_values)

        # All differences should be negative or near-zero (monotonic decrease)
        assert np.all(diffs <= 0.01)


@pytest.mark.integration
class TestNutrientsToEnvironmentPipeline:
    """Test integration between nutrients and environmental control."""

    def test_substrate_ready_before_dome_activation(self):
        """Test substrate is ready before starting dome control."""
        # Prepare substrate
        nutrient_sim = NutrientReleaseSimulator()
        profile = nutrient_sim.simulate_release_cycle(duration_days=60)
        requirements = PlantRequirements()

        ready_day, status = nutrient_sim.check_plant_readiness(profile, requirements)

        # Activate dome after substrate is ready
        dome = AIEnvironmentalController(dome_id="INTEGRATION-TEST")
        dome.state.mode = ControlMode.GROWING

        # Verify timing
        assert ready_day < 30  # Ready within a month
        assert dome.state.mode == ControlMode.GROWING

    def test_nutrient_levels_during_growth(self):
        """Test nutrient levels are maintained during growth period."""
        # Get nutrient profile
        nutrient_sim = NutrientReleaseSimulator()
        profile = nutrient_sim.simulate_release_cycle(duration_days=60)

        # Simulate 30-day growth
        dome = AIEnvironmentalController()
        dome.run_simulation(duration_hours=30 * 24, dt=3600)

        # Check nutrients at planting (day 25) and harvest (day 55)
        idx_plant = int(25 / 60 * len(profile.time_days))
        idx_harvest = int(55 / 60 * len(profile.time_days))

        n_plant = profile.concentrations[Nutrient.NITROGEN][idx_plant]
        n_harvest = profile.concentrations[Nutrient.NITROGEN][idx_harvest]

        # Both should be above minimum
        assert n_plant > 100
        assert n_harvest > 100


@pytest.mark.integration
@pytest.mark.slow
class TestCompleteMissionSimulation:
    """Test complete end-to-end mission simulation."""

    def test_standard_mission_success(self):
        """Test standard mission completes successfully."""
        params = MissionParameters(
            spray_volume_ml=500.0, uv_assisted=True, growth_duration_days=30
        )

        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        # Verify mission success
        assert results.mission_success
        assert results.coverage_area_m2 > 10.0
        assert results.substrate_ready_day < 35
        assert results.total_energy_kwh > 0

    def test_timeline_consistency(self):
        """Test mission timeline is consistent."""
        params = MissionParameters(growth_duration_days=30)
        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        # Verify chronological order
        assert results.spray_date <= results.cure_date
        assert results.cure_date <= results.planting_date
        assert results.planting_date <= results.harvest_date

        # Verify durations
        cure_hours = (results.cure_date - results.spray_date).total_seconds() / 3600
        assert cure_hours < 1  # Cures in under 1 hour

        growth_days = (results.harvest_date - results.planting_date).days
        assert growth_days == 30

    def test_mission_with_cold_environment(self):
        """Test mission in permanently shadowed region."""
        params = MissionParameters(
            ambient_temp_c=-50.0, uv_assisted=True, growth_duration_days=30
        )

        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        # Should still succeed but take longer
        assert results.mission_success
        # Curing takes longer in cold
        assert results.curing_profile.time[-1] > 15  # >15 min cure time

    def test_mission_energy_budget(self):
        """Test mission stays within energy budget."""
        params = MissionParameters(growth_duration_days=30)
        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        # Verify energy consumption is reasonable
        # ~45 kWh for 30 days = 1.5 kWh/day
        energy_per_day = results.total_energy_kwh / params.growth_duration_days

        assert 1.0 < energy_per_day < 2.5  # Reasonable range


@pytest.mark.integration
class TestMultiModuleDataFlow:
    """Test data flows correctly between modules."""

    def test_volume_to_coverage_to_nutrient_capacity(self):
        """Test volume determines coverage and nutrient capacity."""
        volume = 500.0

        # Spray coverage
        spray_sim = SprayDynamics(SprayParameters())
        area = spray_sim.estimate_coverage_area(volume_ml=volume)

        # Nutrient capacity scales with volume
        nutrient_sim = NutrientReleaseSimulator()
        profile = nutrient_sim.simulate_release_cycle(duration_days=60)

        # Final K concentration should support the area
        final_k = profile.concentrations[Nutrient.POTASSIUM][-1]

        assert area > 10  # Good coverage
        assert final_k > 1500  # Adequate nutrients

    def test_temperature_affects_all_phases(self):
        """Test temperature consistently affects all phases."""
        temp_cold = -20.0
        temp_warm = 20.0

        # Spray spreading
        spray_cold = SprayDynamics(SprayParameters(ambient_temp_c=temp_cold))
        spray_warm = SprayDynamics(SprayParameters(ambient_temp_c=temp_warm))

        radius_cold = spray_cold.calculate_coverage_radius(500)
        radius_warm = spray_warm.calculate_coverage_radius(500)

        # Curing speed
        cure_sim = CuringSimulator()
        cure_time_cold = cure_sim.calculate_cure_time(temp_cold)
        cure_time_warm = cure_sim.calculate_cure_time(temp_warm)

        # Verify temperature effects
        assert radius_cold < radius_warm  # Cold reduces spread
        assert cure_time_cold > cure_time_warm  # Cold slows curing


@pytest.mark.integration
class TestSystemResilience:
    """Test system handles various conditions gracefully."""

    def test_partial_water_availability(self):
        """Test system functions with limited water."""
        nutrient_sim = NutrientReleaseSimulator(water_availability=0.6)
        profile = nutrient_sim.simulate_release_cycle(duration_days=60)
        requirements = PlantRequirements()

        ready_day, status = nutrient_sim.check_plant_readiness(profile, requirements)

        # Should still become ready, just delayed
        assert ready_day is not None
        assert ready_day < 50  # Within reasonable time

    def test_high_slope_terrain(self):
        """Test system handles steep slopes."""
        spray_params = SprayParameters(surface_slope=12.0)
        spray_sim = SprayDynamics(spray_params)
        results = spray_sim.simulate_radial_expansion(volume_ml=500)

        # Should still achieve some coverage
        assert results.coverage_area > 5.0  # Reduced but functional

    def test_extended_growth_period(self):
        """Test system handles extended mission durations."""
        params = MissionParameters(growth_duration_days=60)
        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        # Should succeed with longer timeline
        assert results.mission_success
        assert results.total_energy_kwh > 0


@pytest.mark.integration
class TestDataPersistence:
    """Test data can be saved and loaded correctly."""

    def test_save_and_load_mission_results(self, temp_dir):
        """Test mission results can be saved and loaded."""
        params = MissionParameters()
        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        # Save results
        output_file = temp_dir / "mission_results.json"
        sim.generate_report(str(output_file))

        assert output_file.exists()

        # Verify file contains key data
        import json

        with open(output_file) as f:
            data = json.load(f)

        assert "mission" in data
        assert "spray_application" in data
        assert "success" in data["mission"]

    def test_visualization_generation(self, temp_dir):
        """Test visualizations can be generated."""
        params = MissionParameters(growth_duration_days=15)
        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        # Generate plot
        plot_file = temp_dir / "timeline.png"
        sim.plot_complete_timeline(str(plot_file))

        assert plot_file.exists()
        assert plot_file.stat().st_size > 1000  # Non-trivial file size


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test system performance under various loads."""

    def test_high_resolution_simulation(self):
        """Test system with high time resolution."""
        # High-resolution nutrient simulation
        nutrient_sim = NutrientReleaseSimulator()
        profile = nutrient_sim.simulate_release_cycle(
            duration_days=60, time_points=500  # High resolution
        )

        # Should complete without issues
        assert len(profile.time_days) == 500
        assert not np.any(np.isnan(profile.ph_values))

    def test_multiple_mission_scenarios(self):
        """Test running multiple mission scenarios."""
        scenarios = [
            MissionParameters(ambient_temp_c=-20.0),
            MissionParameters(ambient_temp_c=0.0),
            MissionParameters(ambient_temp_c=20.0),
        ]

        results = []
        for params in scenarios:
            sim = IntegratedLunarSpraySimulation(params)
            result = sim.run_complete_simulation(verbose=False)
            results.append(result)

        # All should succeed
        assert all(r.mission_success for r in results)

        # Verify temperature effects on timing
        cure_times = [r.curing_profile.time[-1] for r in results]
        assert cure_times[0] > cure_times[1] > cure_times[2]


@pytest.mark.integration
class TestRealWorldScenarios:
    """Test realistic lunar mission scenarios."""

    def test_shackleton_crater_mission(self):
        """Test mission at Shackleton Crater."""
        params = MissionParameters(
            landing_site="Shackleton Crater",
            ambient_temp_c=-40.0,
            surface_slope=8.0,
            uv_assisted=True,
        )

        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        assert results.mission_success
        assert "Shackleton" in results.mission_params.landing_site

    def test_equatorial_highland_mission(self):
        """Test mission in equatorial highlands."""
        params = MissionParameters(
            landing_site="Equatorial Highland",
            ambient_temp_c=20.0,
            surface_slope=3.0,
            uv_assisted=False,  # No UV assistance needed
        )

        sim = IntegratedLunarSpraySimulation(params)
        results = sim.run_complete_simulation(verbose=False)

        assert results.mission_success
        # Should cure faster in warm conditions
        assert results.curing_profile.time[-1] < 12  # <12 min


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "-m", "integration", "--tb=short"])
