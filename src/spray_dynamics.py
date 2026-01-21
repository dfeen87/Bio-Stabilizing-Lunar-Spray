"""
Spray Dynamics Simulation Module

Models the radial expansion and coverage behavior of the bio-stabilizing
spray when applied to lunar regolith surfaces.

Author: Don Michael Feeney Jr
Based on: Bio-Stabilizing Lunar Spray white paper (April 2025)
"""

import numpy as np
from typing import Tuple, Dict, Optional
import matplotlib.pyplot as plt
from dataclasses import dataclass


@dataclass
class SprayParameters:
    """Configuration parameters for spray application."""
    pressure_psi: float = 25.0  # Application pressure (20-30 recommended)
    ambient_temp_c: float = 0.0  # Ambient temperature
    surface_slope: float = 0.0  # Surface incline in degrees (0-15)
    viscosity_cp: float = 3000.0  # Fluid viscosity in centipoise
    nozzle_diameter_mm: float = 2.0  # Spray nozzle diameter
    

@dataclass
class SprayResults:
    """Results from spray simulation."""
    time: np.ndarray
    radius: np.ndarray
    thickness: np.ndarray
    coverage_area: float
    max_radius: float
    volume_ml: float


class SprayDynamics:
    """
    Simulates spray dispersion and coverage patterns on lunar regolith.
    
    Models radial expansion based on:
    - Application pressure and nozzle characteristics
    - Temperature effects on viscosity
    - Surface slope constraints
    - Vacuum environment behavior
    """
    
    # Physical constants
    GRAVITY_MOON = 1.62  # m/s²
    GRAVITY_EARTH = 9.81  # m/s²
    BASE_VISCOSITY = 3000  # cP at 20°C
    
    def __init__(self, params: Optional[SprayParameters] = None):
        """
        Initialize spray dynamics simulator.
        
        Args:
            params: SprayParameters object with configuration
        """
        self.params = params or SprayParameters()
        
    def calculate_viscosity_factor(self) -> float:
        """
        Calculate temperature-dependent viscosity adjustment.
        
        Temperature affects spray spreading through viscosity changes.
        Cooler temperatures increase viscosity, reducing spread.
        
        Returns:
            Viscosity multiplier relative to base temperature
        """
        # Arrhenius-type temperature dependence
        # Viscosity roughly doubles every 10°C drop
        temp_delta = self.params.ambient_temp_c - 20.0
        return np.exp(-0.069 * temp_delta)
    
    def calculate_coverage_radius(self, volume_ml: float) -> float:
        """
        Calculate expected coverage radius for given volume.
        
        Args:
            volume_ml: Spray volume in milliliters
            
        Returns:
            Maximum radius in meters
        """
        # Base coverage model - assumes radial spreading
        # Volume = π * r² * h, solving for r given target thickness ~1mm
        base_thickness_mm = 1.0
        base_radius = np.sqrt(volume_ml / (np.pi * base_thickness_mm))
        
        # Pressure adjustment (higher pressure = better spread)
        pressure_factor = (self.params.pressure_psi / 25.0) ** 0.3
        
        # Temperature adjustment (affects viscosity)
        visc_factor = self.calculate_viscosity_factor()
        temp_factor = 1.0 / (visc_factor ** 0.2)  # Higher viscosity reduces spread
        
        # Slope penalty (gravity works against uphill flow)
        slope_radians = np.radians(self.params.surface_slope)
        slope_factor = 1.0 - 0.4 * np.sin(slope_radians)
        
        # Lunar gravity enhancement (lower gravity = better spread)
        gravity_factor = np.sqrt(self.GRAVITY_EARTH / self.GRAVITY_MOON)
        
        return (base_radius * pressure_factor * temp_factor * 
                slope_factor * gravity_factor / 100.0)
    
    def simulate_radial_expansion(self, 
                                  volume_ml: float,
                                  duration_s: float = 30.0,
                                  time_steps: int = 100) -> SprayResults:
        """
        Simulate time-dependent radial expansion.
        
        Models the spray as it spreads radially from application point.
        Uses logistic growth model to represent:
        - Initial rapid expansion
        - Gradual deceleration as viscosity dominates
        - Final equilibrium when surface tension balances
        
        Args:
            volume_ml: Total spray volume
            duration_s: Simulation duration in seconds
            time_steps: Number of time points to calculate
            
        Returns:
            SprayResults with time-series data
        """
        max_radius = self.calculate_coverage_radius(volume_ml)
        
        # Time array
        time = np.linspace(0, duration_s, time_steps)
        
        # Logistic growth model for radius expansion
        # r(t) = r_max / (1 + exp(-k*(t - t0)))
        growth_rate = 0.3  # Controls expansion speed
        inflection_time = 10.0  # When expansion is at 50%
        
        radius = max_radius / (1 + np.exp(-growth_rate * (time - inflection_time)))
        
        # Thickness decreases as radius increases (conservation of volume)
        # Avoid division by zero at t=0
        thickness = np.where(radius > 0.01, 
                            volume_ml / (np.pi * radius**2),
                            volume_ml)  # mm
        
        coverage_area = np.pi * max_radius ** 2
        
        return SprayResults(
            time=time,
            radius=radius,
            thickness=thickness,
            coverage_area=coverage_area,
            max_radius=max_radius,
            volume_ml=volume_ml
        )
    
    def estimate_coverage_area(self, volume_ml: float) -> float:
        """
        Calculate total coverage area in square meters.
        
        Args:
            volume_ml: Spray volume
            
        Returns:
            Coverage area in m²
        """
        radius = self.calculate_coverage_radius(volume_ml)
        return np.pi * radius ** 2
    
    def calculate_optimal_volume(self, 
                                target_area_m2: float,
                                target_thickness_mm: float = 1.0) -> float:
        """
        Calculate required spray volume for desired coverage.
        
        Args:
            target_area_m2: Desired coverage area
            target_thickness_mm: Desired coating thickness
            
        Returns:
            Required volume in milliliters
        """
        # Convert area to mm²
        target_area_mm2 = target_area_m2 * 1e6
        
        # Volume = Area × Thickness
        volume_mm3 = target_area_mm2 * target_thickness_mm
        
        # Convert to mL (1 mL = 1000 mm³)
        return volume_mm3 / 1000.0
    
    def plot_expansion(self, results: SprayResults, save_path: Optional[str] = None):
        """
        Visualize spray expansion dynamics.
        
        Args:
            results: SprayResults from simulation
            save_path: Optional path to save figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Radius vs time
        ax1.plot(results.time, results.radius, 'b-', linewidth=2)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Radius (meters)')
        ax1.set_title('Radial Expansion Over Time')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=results.max_radius, color='r', linestyle='--', 
                   label=f'Max radius: {results.max_radius:.2f} m')
        ax1.legend()
        
        # Thickness vs time
        ax2.plot(results.time, results.thickness, 'g-', linewidth=2)
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Thickness (mm)')
        ax2.set_title('Coating Thickness Over Time')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=1.0, color='r', linestyle='--', 
                   label='Target: 1.0 mm')
        ax2.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()


def compare_conditions():
    """
    Compare spray behavior under different lunar conditions.
    """
    conditions = [
        SprayParameters(ambient_temp_c=-20, surface_slope=0, pressure_psi=25),
        SprayParameters(ambient_temp_c=0, surface_slope=0, pressure_psi=25),
        SprayParameters(ambient_temp_c=20, surface_slope=0, pressure_psi=25),
        SprayParameters(ambient_temp_c=0, surface_slope=10, pressure_psi=25),
        SprayParameters(ambient_temp_c=0, surface_slope=0, pressure_psi=30),
    ]
    
    labels = [
        'Cold (-20°C, flat)',
        'Nominal (0°C, flat)',
        'Warm (20°C, flat)',
        'Sloped (0°C, 10° slope)',
        'High pressure (30 PSI)'
    ]
    
    volume = 500  # mL
    
    print("Spray Coverage Comparison")
    print("=" * 60)
    print(f"Volume: {volume} mL\n")
    
    for params, label in zip(conditions, labels):
        sim = SprayDynamics(params)
        results = sim.simulate_radial_expansion(volume)
        
        print(f"{label:30s} | Radius: {results.max_radius:.2f} m | "
              f"Area: {results.coverage_area:.2f} m²")


def run_example():
    """Run example simulation and visualization."""
    print("Bio-Stabilizing Lunar Spray - Dynamics Simulation")
    print("=" * 60)
    
    # Create simulator with nominal conditions
    params = SprayParameters(
        pressure_psi=25,
        ambient_temp_c=0,
        surface_slope=5
    )
    sim = SprayDynamics(params)
    
    # Simulate 500mL spray
    volume = 500
    results = sim.simulate_radial_expansion(volume)
    
    print(f"\nSimulation Parameters:")
    print(f"  Pressure: {params.pressure_psi} PSI")
    print(f"  Temperature: {params.ambient_temp_c}°C")
    print(f"  Surface Slope: {params.surface_slope}°")
    print(f"  Volume: {volume} mL")
    
    print(f"\nResults:")
    print(f"  Maximum Radius: {results.max_radius:.2f} m")
    print(f"  Coverage Area: {results.coverage_area:.2f} m²")
    print(f"  Final Thickness: {results.thickness[-1]:.2f} mm")
    print(f"  Time to 90% Expansion: {results.time[np.argmax(results.radius > 0.9*results.max_radius)]:.1f} s")
    
    # Calculate optimal volume for target coverage
    target_area = 10.0  # m²
    optimal_vol = sim.calculate_optimal_volume(target_area)
    print(f"\n  Volume needed for {target_area} m²: {optimal_vol:.0f} mL")
    
    # Plot results
    sim.plot_expansion(results)
    
    return results


if __name__ == "__main__":
    # Run single example
    results = run_example()
    
    print("\n")
    
    # Compare different conditions
    compare_conditions()
