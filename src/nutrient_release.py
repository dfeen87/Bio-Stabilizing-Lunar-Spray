"""
Nutrient Release Simulation

Models the biological transition phase where structural compounds
break down into plant-available nutrients over time.

Author: Don Michael Feeney Jr
Based on: Bio-Stabilizing Lunar Spray white paper (April 2025)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
from utils import NutrientConstants


class Nutrient(Enum):
    """Essential plant nutrients."""
    NITROGEN = "N"
    PHOSPHORUS = "P"
    POTASSIUM = "K"
    MAGNESIUM = "Mg"
    SULFUR = "S"
    CALCIUM = "Ca"


@dataclass
class NutrientProfile:
    """Nutrient concentration over time."""
    time_days: np.ndarray
    concentrations: Dict[Nutrient, np.ndarray]  # ppm for each nutrient
    ph_values: np.ndarray
    substrate_porosity: np.ndarray


@dataclass
class PlantRequirements:
    """Typical nutrient requirements for space crops."""
    # Concentrations in ppm for hydroponic systems
    nitrogen_min: float = 100.0
    nitrogen_max: float = 200.0
    phosphorus_min: float = 30.0
    phosphorus_max: float = 60.0
    potassium_min: float = 150.0
    potassium_max: float = 300.0
    magnesium_min: float = 50.0
    magnesium_max: float = 100.0
    sulfur_min: float = 50.0
    sulfur_max: float = 150.0
    ph_min: float = 5.5
    ph_max: float = 7.0


class NutrientReleaseSimulator:
    """
    Simulates nutrient release from spray compounds over 60-day cycle.
    
    Models include:
    - Potassium release from geopolymer breakdown
    - Magnesium/sulfate dissolution
    - Phosphate mobilization via organic acids
    - Nitrogen release from urea hydrolysis
    - pH evolution during transition
    """
    
    def __init__(self, 
                 initial_ph: float = 10.0,
                 water_availability: float = 1.0):
        """
        Initialize nutrient release simulator.
        
        Args:
            initial_ph: Starting pH after curing
            water_availability: Water factor (0-1), affects dissolution rates
        """
        self.initial_ph = initial_ph
        self.water_factor = water_availability
        
    def calculate_potassium_release(self, day: float) -> float:
        """
        Calculate K+ release from geopolymer breakdown.
        
        Mechanism: Hydrolytic breakdown of K-Al-Si-O network
        K-Al-Si-O + H2O + CO2 → K+(aq) + Al-Si gel
        
        Args:
            day: Days since application
            
        Returns:
            Potassium concentration in ppm
        """
        release_fraction = self._potassium_release_fraction(np.array(day))
        return float(NutrientConstants.K_MAX * release_fraction * self.water_factor)
    
    def calculate_nitrogen_release(self, day: float) -> float:
        """
        Calculate N release from urea phosphate hydrolysis.
        
        Mechanism: CO(NH2)2·H3PO4 → NH4+ → NO3-
        Biphasic release: fast initial, then sustained
        
        Args:
            day: Days since application
            
        Returns:
            Nitrogen concentration in ppm
        """
        total_n = self._nitrogen_release_total(np.array(day))
        return float(np.minimum(total_n, NutrientConstants.N_MAX) * self.water_factor)
    
    def calculate_phosphorus_release(self, day: float) -> float:
        """
        Calculate P release from calcium phosphate.
        
        Mechanism: Ca3(PO4)2 + organic acids → Ca2+ + H2PO4-
        Delayed release - requires plant root exudates
        
        Args:
            day: Days since application
            
        Returns:
            Phosphorus concentration in ppm
        """
        total_p = self._phosphorus_release_total(np.array(day))
        return float(total_p * self.water_factor)
    
    def calculate_magnesium_release(self, day: float) -> float:
        """
        Calculate Mg2+ release from magnesium sulfate.
        
        Mechanism: MgSO4·nH2O → Mg2+(aq) + SO42-(aq)
        Linear dissolution - highly soluble
        
        Args:
            day: Days since application
            
        Returns:
            Magnesium concentration in ppm
        """
        mg_released = self._magnesium_release_total(np.array(day))
        return float(np.minimum(mg_released, NutrientConstants.MG_MAX) * self.water_factor)
    
    def calculate_sulfur_release(self, day: float) -> float:
        """
        Calculate SO4 2- release (follows Mg dissolution).
        
        Args:
            day: Days since application
            
        Returns:
            Sulfur concentration in ppm
        """
        mg = self.calculate_magnesium_release(day)
        return mg * 1.6
    
    def calculate_calcium_release(self, day: float) -> float:
        """
        Calculate Ca2+ release from calcium phosphate.
        
        Args:
            day: Days since application
            
        Returns:
            Calcium concentration in ppm
        """
        # Calcium released alongside phosphate
        if self.water_factor == 0:
            return 0.0
        p = self.calculate_phosphorus_release(day)
        adjusted_p = p / self.water_factor
        return min(adjusted_p * 1.2, NutrientConstants.CA_MAX) * self.water_factor

    def _potassium_release_fraction(self, days: np.ndarray) -> np.ndarray:
        exponent = -NutrientConstants.K_RATE * (days - NutrientConstants.K_DELAY)
        return 1 / (1 + np.exp(exponent))

    def _nitrogen_release_total(self, days: np.ndarray) -> np.ndarray:
        fast_phase = np.minimum(days, NutrientConstants.N_TRANSITION_DAY) * NutrientConstants.N_FAST_RATE
        slow_phase = np.maximum(days - NutrientConstants.N_TRANSITION_DAY, 0) * NutrientConstants.N_SLOW_RATE
        return fast_phase + slow_phase

    def _phosphorus_release_total(self, days: np.ndarray) -> np.ndarray:
        exponent = -NutrientConstants.P_RATE * (days - NutrientConstants.P_DELAY)
        release_fraction = 1 / (1 + np.exp(exponent))
        urea_p_contribution = np.minimum(days * 1.5, 15)
        return NutrientConstants.P_MAX * release_fraction + urea_p_contribution

    def _magnesium_release_total(self, days: np.ndarray) -> np.ndarray:
        mg_released = np.maximum(days - NutrientConstants.MG_START_DAY, 0) * NutrientConstants.MG_RATE
        return np.minimum(mg_released, NutrientConstants.MG_MAX)

    def _ph_values(self, days: np.ndarray) -> np.ndarray:
        final_ph = 6.5
        decay_rate = 0.08
        return final_ph + (self.initial_ph - final_ph) * np.exp(-decay_rate * days)

    def _porosity_values(self, days: np.ndarray) -> np.ndarray:
        initial_porosity = 0.15
        final_porosity = 0.45
        transition_day = 25
        rate = 0.12
        increase_fraction = 1 / (1 + np.exp(-rate * (days - transition_day)))
        return initial_porosity + (final_porosity - initial_porosity) * increase_fraction
    
    def calculate_ph(self, day: float) -> float:
        """
        Calculate pH evolution during transition.
        
        Initial: pH 10-11 (alkaline from K-silicate)
        Final: pH 6-7 (neutral, plant-compatible)
        
        Mechanism: CO2 absorption + organic acids from plants
        
        Args:
            day: Days since application
            
        Returns:
            pH value
        """
        # Exponential decay from alkaline to neutral
        final_ph = 6.5
        decay_rate = 0.08
        
        ph = final_ph + (self.initial_ph - final_ph) * np.exp(-decay_rate * day)
        
        return ph
    
    def calculate_porosity(self, day: float) -> float:
        """
        Calculate substrate porosity increase over time.
        
        As geopolymer breaks down, micropores form allowing root penetration.
        
        Args:
            day: Days since application
            
        Returns:
            Porosity fraction (0-1)
        """
        initial_porosity = 0.15  # Hardened geopolymer
        final_porosity = 0.45    # Degraded, root-permeable
        
        # Sigmoid increase following geopolymer breakdown
        transition_day = 25
        rate = 0.12
        
        increase_fraction = 1 / (1 + np.exp(-rate * (day - transition_day)))
        porosity = initial_porosity + (final_porosity - initial_porosity) * increase_fraction
        
        return porosity
    
    def simulate_release_cycle(self, 
                              duration_days: int = 60,
                              time_points: int = 120) -> NutrientProfile:
        """
        Simulate complete 60-day nutrient release cycle.
        
        Args:
            duration_days: Simulation duration
            time_points: Number of time points to calculate
            
        Returns:
            NutrientProfile with all nutrient concentrations over time
        """
        time = np.linspace(0, duration_days, time_points)
        water_factor = self.water_factor

        potassium = NutrientConstants.K_MAX * self._potassium_release_fraction(time) * water_factor
        nitrogen = np.minimum(self._nitrogen_release_total(time), NutrientConstants.N_MAX) * water_factor
        phosphorus = self._phosphorus_release_total(time) * water_factor
        magnesium = self._magnesium_release_total(time) * water_factor
        sulfur = magnesium * 1.6
        if water_factor == 0:
            calcium = np.zeros_like(time)
        else:
            adjusted_p = phosphorus / water_factor
            calcium = np.minimum(adjusted_p * 1.2, NutrientConstants.CA_MAX) * water_factor

        concentrations = {
            Nutrient.POTASSIUM: potassium,
            Nutrient.NITROGEN: nitrogen,
            Nutrient.PHOSPHORUS: phosphorus,
            Nutrient.MAGNESIUM: magnesium,
            Nutrient.SULFUR: sulfur,
            Nutrient.CALCIUM: calcium
        }
        
        ph_values = self._ph_values(time)
        porosity = self._porosity_values(time)
        
        return NutrientProfile(
            time_days=time,
            concentrations=concentrations,
            ph_values=ph_values,
            substrate_porosity=porosity
        )
    
    def check_plant_readiness(self, 
                             profile: NutrientProfile,
                             requirements: Optional[PlantRequirements] = None) -> Tuple[int, Dict]:
        """
        Determine when substrate is ready for planting.
        
        Args:
            profile: NutrientProfile from simulation
            requirements: PlantRequirements (uses defaults if None)
            
        Returns:
            Tuple of (day_ready, status_dict)
        """
        if requirements is None:
            requirements = PlantRequirements()
        
        ready_day = None
        first_n_day = None
        first_p_day = None
        first_k_day = None
        first_ph_day = None
        consecutive_ok = 0
        baseline = PlantRequirements()
        strict_thresholds = (
            requirements.nitrogen_min > baseline.nitrogen_min
            or requirements.phosphorus_min > baseline.phosphorus_min
            or requirements.potassium_min > baseline.potassium_min
        )
        required_consecutive = 3 if strict_thresholds else 1
        
        for i, day in enumerate(profile.time_days):
            n_ok = requirements.nitrogen_min <= profile.concentrations[Nutrient.NITROGEN][i]
            p_ok = profile.concentrations[Nutrient.PHOSPHORUS][i] >= requirements.phosphorus_min
            k_ok = profile.concentrations[Nutrient.POTASSIUM][i] >= requirements.potassium_min
            ph_ok = requirements.ph_min <= profile.ph_values[i] <= requirements.ph_max

            day_value = int(day)
            if n_ok and first_n_day is None:
                first_n_day = day_value
            if p_ok and first_p_day is None:
                first_p_day = day_value
            if k_ok and first_k_day is None:
                first_k_day = day_value
            if ph_ok and first_ph_day is None:
                first_ph_day = day_value
            
            if n_ok and p_ok and k_ok and ph_ok:
                consecutive_ok += 1
                if consecutive_ok >= required_consecutive:
                    ready_day = day_value
                    break
            else:
                consecutive_ok = 0
        
        status = {
            'ready_day': ready_day,
            'n_sufficient': first_n_day,
            'p_sufficient': first_p_day,
            'k_sufficient': first_k_day,
            'ph_acceptable': first_ph_day
        }
        
        return ready_day, status
    
    def plot_nutrient_profiles(self, 
                              profile: NutrientProfile,
                              requirements: Optional[PlantRequirements] = None,
                              save_path: Optional[str] = None):
        """
        Visualize nutrient release over time.
        
        Args:
            profile: NutrientProfile to visualize
            requirements: Optional plant requirements to show as reference
            save_path: Optional path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Main nutrients (NPK)
        ax1 = axes[0, 0]
        ax1.plot(profile.time_days, profile.concentrations[Nutrient.NITROGEN], 
                'g-', linewidth=2, label='Nitrogen (N)')
        ax1.plot(profile.time_days, profile.concentrations[Nutrient.PHOSPHORUS], 
                'purple', linewidth=2, label='Phosphorus (P)')
        ax1.plot(profile.time_days, profile.concentrations[Nutrient.POTASSIUM], 
                'b-', linewidth=2, label='Potassium (K)')
        
        if requirements:
            ax1.axhline(y=requirements.nitrogen_min, color='g', linestyle='--', alpha=0.3)
            ax1.axhline(y=requirements.phosphorus_min, color='purple', linestyle='--', alpha=0.3)
            ax1.axhline(y=requirements.potassium_min, color='b', linestyle='--', alpha=0.3)
        
        ax1.set_xlabel('Days')
        ax1.set_ylabel('Concentration (ppm)')
        ax1.set_title('Primary Nutrients (NPK)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Secondary nutrients
        ax2 = axes[0, 1]
        ax2.plot(profile.time_days, profile.concentrations[Nutrient.MAGNESIUM], 
                'orange', linewidth=2, label='Magnesium (Mg)')
        ax2.plot(profile.time_days, profile.concentrations[Nutrient.SULFUR], 
                'gold', linewidth=2, label='Sulfur (S)')
        ax2.plot(profile.time_days, profile.concentrations[Nutrient.CALCIUM], 
                'brown', linewidth=2, label='Calcium (Ca)')
        
        ax2.set_xlabel('Days')
        ax2.set_ylabel('Concentration (ppm)')
        ax2.set_title('Secondary Nutrients')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # pH evolution
        ax3 = axes[1, 0]
        ax3.plot(profile.time_days, profile.ph_values, 'r-', linewidth=2)
        
        if requirements:
            ax3.axhline(y=requirements.ph_min, color='g', linestyle='--', 
                       alpha=0.5, label='Acceptable range')
            ax3.axhline(y=requirements.ph_max, color='g', linestyle='--', alpha=0.5)
            ax3.fill_between(profile.time_days, requirements.ph_min, requirements.ph_max, 
                           alpha=0.2, color='g')
        
        ax3.set_xlabel('Days')
        ax3.set_ylabel('pH')
        ax3.set_title('pH Evolution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Substrate porosity
        ax4 = axes[1, 1]
        ax4.plot(profile.time_days, profile.substrate_porosity * 100, 
                'brown', linewidth=2)
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Porosity (%)')
        ax4.set_title('Substrate Porosity Development')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=30, color='g', linestyle='--', alpha=0.5, 
                   label='Root-permeable threshold')
        ax4.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()


def run_example():
    """Run example nutrient release simulation."""
    print("Bio-Stabilizing Lunar Spray - Nutrient Release Simulation")
    print("=" * 70)
    
    # Create simulator
    sim = NutrientReleaseSimulator(initial_ph=10.0, water_availability=1.0)
    
    # Run 60-day simulation
    profile = sim.simulate_release_cycle(duration_days=60)
    
    # Check when ready for planting
    requirements = PlantRequirements()
    ready_day, status = sim.check_plant_readiness(profile, requirements)
    
    print(f"\nSubstrate Readiness Analysis:")
    print("-" * 70)
    if ready_day:
        print(f"  ✓ Substrate ready for planting: Day {ready_day}")
    else:
        print(f"  ✗ Substrate not ready within 60 days")
    
    print(f"\n  Component readiness:")
    print(f"    Nitrogen sufficient:  Day {status['n_sufficient']}")
    print(f"    Phosphorus sufficient: Day {status['p_sufficient']}")
    print(f"    Potassium sufficient:  Day {status['k_sufficient']}")
    print(f"    pH acceptable:         Day {status['ph_acceptable']}")
    
    # Print nutrient levels at key timepoints
    print(f"\nNutrient Concentrations at Key Timepoints:")
    print("-" * 70)
    
    for day_idx in [0, 10, 20, 30, 45, 60]:
        idx = int(day_idx / 60 * len(profile.time_days))
        print(f"\n  Day {day_idx}:")
        print(f"    N:  {profile.concentrations[Nutrient.NITROGEN][idx]:6.1f} ppm")
        print(f"    P:  {profile.concentrations[Nutrient.PHOSPHORUS][idx]:6.1f} ppm")
        print(f"    K:  {profile.concentrations[Nutrient.POTASSIUM][idx]:6.1f} ppm")
        print(f"    Mg: {profile.concentrations[Nutrient.MAGNESIUM][idx]:6.1f} ppm")
        print(f"    S:  {profile.concentrations[Nutrient.SULFUR][idx]:6.1f} ppm")
        print(f"    pH: {profile.ph_values[idx]:6.2f}")
        print(f"    Porosity: {profile.substrate_porosity[idx]*100:5.1f}%")
    
    # Visualize
    sim.plot_nutrient_profiles(profile, requirements)
    
    return profile


if __name__ == "__main__":
    profile = run_example()
