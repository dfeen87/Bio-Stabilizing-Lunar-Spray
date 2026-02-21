"""
Performance Benchmarks

Measures performance and execution time of key system components.

Author: Don Michael Feeney Jr

Run with: pytest test_benchmarks.py -v --benchmark-only
"""

import pytest
import time
import numpy as np

from src.spray_dynamics import SprayDynamics, SprayParameters
from src.curing_simulation import CuringSimulator
from src.nutrient_release import NutrientReleaseSimulator
from src.environmental_control import AIEnvironmentalController
from integrated_simulation import IntegratedLunarSpraySimulation, MissionParameters


@pytest.mark.benchmark
class TestSprayDynamicsBenchmarks:
    """Benchmark spray dynamics simulations."""

    def test_benchmark_single_expansion(self, benchmark):
        """Benchmark single spray expansion simulation."""
        spray_sim = SprayDynamics(SprayParameters())

        result = benchmark(
            spray_sim.simulate_radial_expansion,
            volume_ml=500,
            duration_s=30,
            time_steps=100,
        )

        assert result is not None

    def test_benchmark_coverage_calculation(self, benchmark):
        """Benchmark coverage radius calculation."""
        spray_sim = SprayDynamics(SprayParameters())

        result = benchmark(spray_sim.calculate_coverage_radius, volume_ml=500)

        assert result > 0

    def test_benchmark_multiple_volumes(self):
        """Benchmark multiple volume simulations."""
        spray_sim = SprayDynamics(SprayParameters())
        volumes = [100, 250, 500, 1000, 2000]

        start_time = time.time()
        results = []
        for vol in volumes:
            res = spray_sim.simulate_radial_expansion(vol)
            results.append(res)
        end_time = time.time()

        elapsed = end_time - start_time
        print(f"\nMultiple volumes: {elapsed:.3f}s for {len(volumes)} simulations")

        assert elapsed < 5.0  # Should complete in under 5 seconds
        assert len(results) == len(volumes)


@pytest.mark.benchmark
class TestCuringBenchmarks:
    """Benchmark curing simulations."""

    def test_benchmark_single_curing(self, benchmark):
        """Benchmark single curing simulation."""
        curing_sim = CuringSimulator(uv_assisted=False)

        result = benchmark(
            curing_sim.simulate_curing,
            temperature_c=0.0,
            duration_min=30.0,
            time_steps=100,
        )

        assert result is not None

    def test_benchmark_cure_time_calculation(self, benchmark):
        """Benchmark cure time calculation."""
        curing_sim = CuringSimulator()

        result = benchmark(curing_sim.calculate_cure_time, temperature_c=0.0)

        assert result > 0

    def test_benchmark_temperature_comparison(self):
        """Benchmark multi-temperature comparison."""
        curing_sim = CuringSimulator()
        temps = list(range(-50, 81, 10))

        start_time = time.time()
        profiles = curing_sim.compare_temperatures(temps, duration_min=30)
        end_time = time.time()

        elapsed = end_time - start_time
        print(f"\nTemperature comparison: {elapsed:.3f}s for {len(temps)} temperatures")

        assert elapsed < 10.0
        assert len(profiles) == len(temps)


@pytest.mark.benchmark
class TestNutrientReleaseBenchmarks:
    """Benchmark nutrient release simulations."""

    def test_benchmark_full_cycle(self, benchmark):
        """Benchmark full 60-day nutrient cycle."""
        nutrient_sim = NutrientReleaseSimulator()

        result = benchmark(
            nutrient_sim.simulate_release_cycle, duration_days=60, time_points=120
        )

        assert result is not None

    def test_benchmark_individual_nutrients(self):
        """Benchmark individual nutrient calculations."""
        nutrient_sim = NutrientReleaseSimulator()
        days = np.linspace(0, 60, 100)

        start_time = time.time()
        for day in days:
            nutrient_sim.calculate_potassium_release(day)
            nutrient_sim.calculate_nitrogen_release(day)
            nutrient_sim.calculate_phosphorus_release(day)
            nutrient_sim.calculate_magnesium_release(day)
        end_time = time.time()

        elapsed = end_time - start_time
        print(f"\nNutrient calculations: {elapsed:.3f}s for {len(days)} time points")

        assert elapsed < 1.0  # Should be very fast

    def test_benchmark_high_resolution(self, benchmark):
        """Benchmark high-resolution simulation."""
        nutrient_sim = NutrientReleaseSimulator()

        result = benchmark(
            nutrient_sim.simulate_release_cycle,
            duration_days=60,
            time_points=500,  # High resolution
        )

        assert result is not None


@pytest.mark.benchmark
class TestEnvironmentalControlBenchmarks:
    """Benchmark environmental control simulations."""

    def test_benchmark_24hour_simulation(self, benchmark):
        """Benchmark 24-hour dome simulation."""
        controller = AIEnvironmentalController()

        def run_simulation():
            ctrl = AIEnvironmentalController()
            ctrl.run_simulation(duration_hours=24.0, dt=60.0)
            return ctrl

        result = benchmark(run_simulation)
        assert result is not None

    def test_benchmark_single_control_update(self, benchmark):
        """Benchmark single control loop update."""
        controller = AIEnvironmentalController()

        result = benchmark(controller.update_control, dt=60.0)

        assert result is not None

    def test_benchmark_extended_simulation(self):
        """Benchmark extended dome simulation."""
        controller = AIEnvironmentalController()

        start_time = time.time()
        controller.run_simulation(duration_hours=168.0, dt=300.0)  # 1 week
        end_time = time.time()

        elapsed = end_time - start_time
        print(f"\nWeek-long simulation: {elapsed:.3f}s")

        assert elapsed < 30.0  # Should complete in under 30 seconds


@pytest.mark.benchmark
@pytest.mark.slow
class TestIntegratedBenchmarks:
    """Benchmark complete integrated simulations."""

    def test_benchmark_complete_mission(self, benchmark):
        """Benchmark complete mission simulation."""
        params = MissionParameters(growth_duration_days=30)

        def run_mission():
            sim = IntegratedLunarSpraySimulation(params)
            return sim.run_complete_simulation(verbose=False)

        result = benchmark(run_mission)
        assert result.mission_success

    def test_benchmark_fast_mission(self):
        """Benchmark shortened mission for speed testing."""
        params = MissionParameters(growth_duration_days=7)  # Short growth
        sim = IntegratedLunarSpraySimulation(params)

        start_time = time.time()
        results = sim.run_complete_simulation(verbose=False)
        end_time = time.time()

        elapsed = end_time - start_time
        print(f"\nFast mission: {elapsed:.3f}s")

        assert elapsed < 20.0
        assert results.mission_success


@pytest.mark.benchmark
class TestScalabilityBenchmarks:
    """Test performance scaling with problem size."""

    def test_time_step_scaling(self):
        """Test how execution time scales with time steps."""
        spray_sim = SprayDynamics(SprayParameters())
        time_steps = [50, 100, 200, 400]
        times = []

        for steps in time_steps:
            start = time.time()
            spray_sim.simulate_radial_expansion(volume_ml=500, time_steps=steps)
            times.append(time.time() - start)

        print(f"\nTime step scaling:")
        for steps, t in zip(time_steps, times):
            print(f"  {steps} steps: {t:.4f}s")

        # Check scaling is reasonable (should be roughly linear)
        ratio = times[-1] / times[0]
        assert ratio < 10  # 8x more steps shouldn't take 10x longer

    def test_duration_scaling(self):
        """Test how nutrient simulation scales with duration."""
        nutrient_sim = NutrientReleaseSimulator()
        durations = [15, 30, 60, 120]
        times = []

        for duration in durations:
            start = time.time()
            nutrient_sim.simulate_release_cycle(duration_days=duration, time_points=100)
            times.append(time.time() - start)

        print(f"\nDuration scaling:")
        for duration, t in zip(durations, times):
            print(f"  {duration} days: {t:.4f}s")

        # Should scale linearly or better
        assert times[-1] < times[0] * 5


@pytest.mark.benchmark
class TestMemoryEfficiency:
    """Test memory usage of simulations."""

    def test_spray_memory_usage(self):
        """Test spray simulation doesn't use excessive memory."""
        import sys

        spray_sim = SprayDynamics(SprayParameters())

        # Get size before
        size_before = sys.getsizeof(spray_sim)

        # Run simulation
        results = spray_sim.simulate_radial_expansion(
            volume_ml=500, time_steps=1000  # Large number of steps
        )

        # Check result size is reasonable
        result_size = (
            sys.getsizeof(results.time)
            + sys.getsizeof(results.radius)
            + sys.getsizeof(results.thickness)
        )

        print(f"\nSpray result size: {result_size / 1024:.2f} KB")

        # Should be under 1 MB for 1000 time steps
        assert result_size < 1024 * 1024

    def test_nutrient_profile_memory(self):
        """Test nutrient profile doesn't use excessive memory."""
        import sys

        nutrient_sim = NutrientReleaseSimulator()
        profile = nutrient_sim.simulate_release_cycle(duration_days=60, time_points=500)

        # Calculate approximate memory usage
        arrays_size = (
            sys.getsizeof(profile.time_days)
            + sys.getsizeof(profile.ph_values)
            + sys.getsizeof(profile.substrate_porosity)
            + sum(sys.getsizeof(arr) for arr in profile.concentrations.values())
        )

        print(f"\nNutrient profile size: {arrays_size / 1024:.2f} KB")

        # Should be under 500 KB
        assert arrays_size < 512 * 1024


@pytest.mark.benchmark
class TestComparativeBenchmarks:
    """Compare performance across modules."""

    def test_relative_execution_times(self):
        """Compare execution times of different modules."""
        results = {}

        # Spray dynamics
        start = time.time()
        spray_sim = SprayDynamics(SprayParameters())
        spray_sim.simulate_radial_expansion(volume_ml=500)
        results["spray"] = time.time() - start

        # Curing
        start = time.time()
        curing_sim = CuringSimulator()
        curing_sim.simulate_curing(temperature_c=0.0, duration_min=30)
        results["curing"] = time.time() - start

        # Nutrients
        start = time.time()
        nutrient_sim = NutrientReleaseSimulator()
        nutrient_sim.simulate_release_cycle(duration_days=60, time_points=100)
        results["nutrients"] = time.time() - start

        # Environmental control (short)
        start = time.time()
        dome = AIEnvironmentalController()
        dome.run_simulation(duration_hours=24.0, dt=300.0)
        results["environment"] = time.time() - start

        print("\nModule execution times:")
        for module, t in results.items():
            print(f"  {module:12s}: {t:.4f}s")

        # All should complete in reasonable time
        assert all(t < 5.0 for t in results.values())


@pytest.mark.benchmark
class TestOptimizationOpportunities:
    """Identify optimization opportunities."""

    def test_bottleneck_identification(self):
        """Identify computational bottlenecks."""
        import cProfile
        import pstats
        from io import StringIO

        profiler = cProfile.Profile()

        # Profile integrated simulation
        profiler.enable()

        params = MissionParameters(growth_duration_days=7)
        sim = IntegratedLunarSpraySimulation(params)
        sim.run_complete_simulation(verbose=False)

        profiler.disable()

        # Get stats
        s = StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats("cumulative")
        ps.print_stats(10)  # Top 10 functions

        print("\nTop computational hotspots:")
        print(s.getvalue())


if __name__ == "__main__":
    # Run benchmarks
    pytest.main(
        [__file__, "-v", "-m", "benchmark", "--benchmark-only", "--benchmark-autosave"]
    )
