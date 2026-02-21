"""
Curing Behavior Simulation

Models the temperature-dependent curing process and bond strength
development of the spray on lunar regolith.

Author: Don Michael Feeney Jr
Based on: Bio-Stabilizing Lunar Spray white paper (April 2025)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Optional
from enum import Enum
from utils import CuringConstants, PhysicalConstants


class CuringPhase(Enum):
    """Phases of the curing process."""
    INITIAL = "Initial gelation"
    SETTING = "Primary setting"
    HARDENING = "Strength development"
    MATURE = "Mature geopolymer"


@dataclass
class CuringProfile:
    """Results from curing simulation."""
    time: np.ndarray
    cure_fraction: np.ndarray
    bond_strength_mpa: np.ndarray
    temperature_c: float
    uv_assisted: bool
    phase: np.ndarray  # CuringPhase at each time point
    

@dataclass
class RegolithProperties:
    """Properties of lunar regolith affecting curing."""
    silica_content: float = 47.0  # SiO2 percentage
    alumina_content: float = 14.0  # Al2O3 percentage
    iron_content: float = 10.5  # FeO percentage
    particle_size_um: float = 70.0  # Mean particle size
    surface_area_m2_g: float = 0.5  # Specific surface area


class CuringSimulator:
    """
    Simulates spray curing behavior under lunar conditions.
    
    Models geopolymerization kinetics including:
    - Temperature-dependent reaction rates
    - Bond strength development over time
    - UV-assisted acceleration
    - Regolith composition effects
    """
    
    def __init__(self, 
                 uv_assisted: bool = False,
                 regolith: Optional[RegolithProperties] = None):
        """
        Initialize curing simulator.
        
        Args:
            uv_assisted: Whether UV-assisted formulation is used
            regolith: RegolithProperties for composition-dependent behavior
        """
        self.uv_assisted = uv_assisted
        self.regolith = regolith or RegolithProperties()
        
    def calculate_activation_factor(self, temperature_c: float) -> float:
        """
        Calculate Arrhenius temperature factor.
        
        Geopolymerization follows Arrhenius kinetics:
        k(T) = A * exp(-Ea / RT)
        
        Args:
            temperature_c: Temperature in Celsius
            
        Returns:
            Reaction rate multiplier
        """
        T_kelvin = temperature_c + 273.15
        T_ref = 273.15  # 0°C reference
        
        exponent = -(CuringConstants.ACTIVATION_ENERGY * 1000) / PhysicalConstants.GAS_CONSTANT
        factor = np.exp(exponent * (1/T_kelvin - 1/T_ref))
        
        return factor
        
    def calculate_cure_time(self, temperature_c: float) -> float:
        """
        Calculate full cure time at given temperature.
        
        Args:
            temperature_c: Ambient temperature (-170 to 120)
            
        Returns:
            Cure time in minutes
        """
        # Arrhenius-style temperature dependence
        activation_factor = self.calculate_activation_factor(temperature_c)
        cure_time = CuringConstants.BASE_CURE_TIME / activation_factor
        
        # UV acceleration
        if self.uv_assisted:
            cure_time *= (1 - CuringConstants.UV_ACCELERATION)
        
        # Regolith composition effects
        # Higher Al2O3 content accelerates geopolymerization
        # Use a small epsilon to avoid division by zero if alumina is 0
        alumina = max(self.regolith.alumina_content, 0.01)
        al_factor = alumina / 14.0
        cure_time /= al_factor
        
        # Clamp cure time to keep extreme cold reactions progressing
        return min(max(cure_time, 2.0), CuringConstants.MAX_CURE_TIME)
    
    def calculate_bond_strength(self, 
                               time_min: float, 
                               temperature_c: float) -> float:
        """
        Calculate bond strength at given time and temperature.
        
        Args:
            time_min: Elapsed time in minutes
            temperature_c: Curing temperature
            
        Returns:
            Bond strength in MPa
        """
        cure_time = self.calculate_cure_time(temperature_c)
        
        # Sigmoidal strength development
        # Strength develops as geopolymer network forms
        curve_steepness = 5
        # Avoid division by zero if cure_time is 0 (unlikely but safe)
        safe_cure_time = max(cure_time, 1e-6)
        normalized_time = (time_min - safe_cure_time) / safe_cure_time
        cure_fraction = 1 / (1 + np.exp(-curve_steepness * normalized_time))
        
        # Base strength from geopolymer network
        base_strength = CuringConstants.MAX_BOND_STRENGTH * cure_fraction
        
        # Temperature-dependent maximum strength
        # Very low temperatures reduce ultimate strength slightly
        temp_strength_factor = 1.0 - 0.001 * max(0, -temperature_c - 50)
        
        return base_strength * temp_strength_factor
    
    def get_curing_phase(self, cure_fraction: float) -> CuringPhase:
        """
        Determine curing phase based on cure fraction.
        
        Args:
            cure_fraction: Fraction of curing complete (0-1)
            
        Returns:
            Current CuringPhase
        """
        if cure_fraction < 0.15:
            return CuringPhase.INITIAL
        elif cure_fraction < 0.5:
            return CuringPhase.SETTING
        elif cure_fraction < 0.95:
            return CuringPhase.HARDENING
        else:
            return CuringPhase.MATURE
    
    def simulate_curing(self, 
                       temperature_c: float,
                       duration_min: float = 30.0,
                       time_steps: int = 200) -> CuringProfile:
        """
        Simulate curing process over time.
        
        Args:
            temperature_c: Ambient temperature
            duration_min: Simulation duration in minutes
            time_steps: Number of time points
            
        Returns:
            CuringProfile with simulation results
        """
        time = np.linspace(0, duration_min, time_steps)
        
        # Calculate characteristic cure time
        cure_time = self.calculate_cure_time(temperature_c)
        
        # Sigmoidal cure fraction development
        curve_steepness = 5
        # Avoid division by zero
        safe_cure_time = max(cure_time, 1e-6)
        normalized_time = (time - safe_cure_time) / safe_cure_time
        cure_fraction = 1 / (1 + np.exp(-curve_steepness * normalized_time))
        
        # Bond strength follows cure fraction with temperature correction
        temp_strength_factor = 1.0 - 0.001 * max(0, -temperature_c - 50)
        bond_strength = CuringConstants.MAX_BOND_STRENGTH * cure_fraction * temp_strength_factor
        
        # Determine phase at each time point
        phase = np.array([self.get_curing_phase(cf) for cf in cure_fraction])
        
        return CuringProfile(
            time=time,
            cure_fraction=cure_fraction,
            bond_strength_mpa=bond_strength,
            temperature_c=temperature_c,
            uv_assisted=self.uv_assisted,
            phase=phase
        )
    
    def compare_temperatures(self, 
                           temps: List[float],
                           duration_min: float = 30.0) -> List[CuringProfile]:
        """
        Compare curing at different temperatures.
        
        Args:
            temps: List of temperatures to compare
            duration_min: Simulation duration
            
        Returns:
            List of CuringProfile results
        """
        return [self.simulate_curing(t, duration_min) for t in temps]
    
    def plot_curing_curves(self, 
                          profiles: List[CuringProfile],
                          labels: Optional[List[str]] = None,
                          save_path: Optional[str] = None):
        """
        Visualize curing behavior for multiple conditions.
        
        Args:
            profiles: List of CuringProfile results
            labels: Optional labels for each profile
            save_path: Optional path to save figure
        """
        if labels is None:
            labels = [f"{p.temperature_c}°C" + 
                     (" (UV)" if p.uv_assisted else "") 
                     for p in profiles]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(profiles)))
        
        # Cure fraction vs time
        for profile, label, color in zip(profiles, labels, colors):
            ax1.plot(profile.time, profile.cure_fraction * 100, 
                    label=label, linewidth=2, color=color)
        
        ax1.set_xlabel('Time (minutes)')
        ax1.set_ylabel('Cure Fraction (%)')
        ax1.set_title('Curing Progress Over Time')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.axhline(y=50, color='r', linestyle='--', alpha=0.3)
        ax1.axhline(y=95, color='g', linestyle='--', alpha=0.3)
        
        # Bond strength vs time
        for profile, label, color in zip(profiles, labels, colors):
            ax2.plot(profile.time, profile.bond_strength_mpa, 
                    label=label, linewidth=2, color=color)
        
        ax2.set_xlabel('Time (minutes)')
        ax2.set_ylabel('Bond Strength (MPa)')
        ax2.set_title('Strength Development Over Time')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.axhline(y=CuringConstants.MAX_BOND_STRENGTH, color='g',
                   linestyle='--', alpha=0.3, label='Max strength')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()


def generate_cure_time_chart():
    """Generate comprehensive cure time vs temperature data."""
    temperatures = np.linspace(-50, 80, 50)
    
    standard = CuringSimulator(uv_assisted=False)
    uv_assisted = CuringSimulator(uv_assisted=True)
    
    standard_times = np.array([standard.calculate_cure_time(t) 
                               for t in temperatures])
    uv_times = np.array([uv_assisted.calculate_cure_time(t) 
                        for t in temperatures])
    
    plt.figure(figsize=(10, 6))
    plt.plot(temperatures, standard_times, 'b-', linewidth=2, 
            label='Standard formulation')
    plt.plot(temperatures, uv_times, 'r-', linewidth=2, 
            label='UV-assisted formulation')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Cure Time (minutes)')
    plt.title('Cure Time vs Temperature')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.axvline(x=0, color='k', linestyle='--', alpha=0.3, label='Nominal (0°C)')
    plt.show()
    
    return {
        'temperature': temperatures,
        'standard': standard_times,
        'uv_assisted': uv_times
    }


def analyze_phase_transitions():
    """Analyze timing of different curing phases."""
    sim = CuringSimulator(uv_assisted=False)
    temps = [-20, 0, 20, 40]
    
    print("Phase Transition Analysis")
    print("=" * 70)
    
    for temp in temps:
        profile = sim.simulate_curing(temp, duration_min=40)
        
        # Find transition points
        initial_end = np.where(profile.cure_fraction >= 0.15)[0][0]
        setting_end = np.where(profile.cure_fraction >= 0.5)[0][0]
        hardening_end = np.where(profile.cure_fraction >= 0.95)[0][0]
        
        print(f"\nTemperature: {temp}°C")
        print(f"  Initial gelation:      0.0 - {profile.time[initial_end]:.1f} min")
        print(f"  Primary setting:       {profile.time[initial_end]:.1f} - {profile.time[setting_end]:.1f} min")
        print(f"  Strength development:  {profile.time[setting_end]:.1f} - {profile.time[hardening_end]:.1f} min")
        print(f"  Mature (95%+):         {profile.time[hardening_end]:.1f} min+")
        print(f"  Final strength:        {profile.bond_strength_mpa[-1]:.2f} MPa")


def run_example():
    """Run example simulation with visualization."""
    print("Bio-Stabilizing Lunar Spray - Curing Simulation")
    print("=" * 60)
    
    # Create simulators
    standard = CuringSimulator(uv_assisted=False)
    uv_sim = CuringSimulator(uv_assisted=True)
    
    # Simulate at multiple temperatures
    temps = [-20, 0, 20, 40]
    
    print("\nCure Time Comparison:")
    print("-" * 60)
    for temp in temps:
        std_time = standard.calculate_cure_time(temp)
        uv_time = uv_sim.calculate_cure_time(temp)
        
        print(f"  {temp:3d}°C | Standard: {std_time:5.1f} min | "
              f"UV-assisted: {uv_time:5.1f} min | "
              f"Improvement: {(1-uv_time/std_time)*100:.1f}%")
    
    # Detailed simulation at 0°C
    profile_std = standard.simulate_curing(0, duration_min=30)
    profile_uv = uv_sim.simulate_curing(0, duration_min=30)
    
    print(f"\nDetailed Results at 0°C (Standard):")
    print(f"  Cure time: {standard.calculate_cure_time(0):.1f} min")
    print(f"  Strength at 15 min: {profile_std.bond_strength_mpa[np.argmax(profile_std.time >= 15)]:.2f} MPa")
    print(f"  Strength at 30 min: {profile_std.bond_strength_mpa[-1]:.2f} MPa")
    
    # Compare multiple temperatures
    profiles = standard.compare_temperatures(temps)
    standard.plot_curing_curves(profiles)
    
    return profiles


if __name__ == "__main__":
    # Run main example
    profiles = run_example()
    
    print("\n")
    
    # Generate cure time chart
    generate_cure_time_chart()
    
    print("\n")
    
    # Analyze phase transitions
    analyze_phase_transitions()
