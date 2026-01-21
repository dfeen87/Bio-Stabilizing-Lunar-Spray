"""
Integrated Lunar Spray System Simulation

Complete end-to-end simulation combining:
- Spray dynamics and application
- Curing behavior
- Nutrient release
- Environmental control

Author: Don Michael Feeney Jr
Based on: Bio-Stabilizing Lunar Spray white paper (April 2025)
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

# Import all simulation modules
from spray_dynamics import SprayDynamics, SprayParameters, SprayResults
from curing_simulation import CuringSimulator, CuringProfile, RegolithProperties
from nutrient_release import NutrientReleaseSimulator, NutrientProfile, PlantRequirements, Nutrient
from environmental_control import AIEnvironmentalController, DomeState, ControlMode


@dataclass
class MissionParameters:
    """Complete mission configuration."""
    # Location
    landing_site: str = "Lunar South Pole - Shackleton Crater Rim"
    latitude: float = -89.5
    longitude: float = 0.0
    
    # Spray application
    spray_volume_ml: float = 500.0
    application_pressure_psi: float = 25.0
    surface_slope_deg: float = 5.0
    ambient_temp_c: float = 0.0
    uv_assisted: bool = True
    
    # Agriculture
    target_crop: str = "Lettuce (Lactuca sativa)"
    planting_delay_days: int = 25
    growth_duration_days: int = 30
    
    # Environmental
    dome_temperature_c: float = 22.0
    dome_humidity_percent: float = 65.0
    photoperiod_hours: float = 16.0


@dataclass
class SimulationResults:
    """Complete simulation outputs."""
    mission_params: MissionParameters
    spray_results: SprayResults
    curing_profile: CuringProfile
    nutrient_profile: NutrientProfile
    dome_controller: AIEnvironmentalController
    
    # Summary metrics
    coverage_area_m2: float
    substrate_ready_day: int
    total_energy_kwh: float
    mission_success: bool
    
    # Timeline
    start_date: datetime
    spray_date: datetime
    cure_date: datetime
    planting_date: datetime
    harvest_date: datetime


class IntegratedLunarSpraySimulation:
    """
    Complete mission simulation from spray application to harvest.
    """
    
    def __init__(self, params: Optional[MissionParameters] = None):
        """
        Initialize integrated simulation.
        
        Args:
            params: Mission parameters (uses defaults if None)
        """
        self.params = params or MissionParameters()
        self.results: Optional[SimulationResults] = None
        
    def run_complete_simulation(self, 
                               start_date: Optional[datetime] = None,
                               verbose: bool = True) -> SimulationResults:
        """
        Execute complete mission simulation.
        
        Args:
            start_date: Mission start date
            verbose: Print progress updates
            
        Returns:
            Complete SimulationResults
        """
        if start_date is None:
            start_date = datetime.now()
        
        if verbose:
            self._print_header()
            print(f"Mission Start: {start_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"Landing Site: {self.params.landing_site}")
            print(f"Target Crop: {self.params.target_crop}\n")
        
        # Phase 1: Spray Application
        if verbose:
            print("=" * 70)
            print("PHASE 1: SPRAY APPLICATION")
            print("=" * 70)
        
        spray_results = self._simulate_spray_application(verbose)
        spray_date = start_date
        
        # Phase 2: Curing
        if verbose:
            print("\n" + "=" * 70)
            print("PHASE 2: SURFACE CURING")
            print("=" * 70)
        
        curing_profile = self._simulate_curing(verbose)
        cure_time_hours = curing_profile.time[-1] / 60  # Convert minutes to hours
        cure_date = spray_date + timedelta(hours=cure_time_hours)
        
        # Phase 3: Nutrient Release & Substrate Development
        if verbose:
            print("\n" + "=" * 70)
            print("PHASE 3: NUTRIENT RELEASE & BIOLOGICAL TRANSITION")
            print("=" * 70)
        
        nutrient_profile, substrate_ready_day = self._simulate_nutrient_release(verbose)
        planting_date = spray_date + timedelta(days=substrate_ready_day)
        
        # Phase 4: Environmental Control & Growing
        if verbose:
            print("\n" + "=" * 70)
            print("PHASE 4: ENVIRONMENTAL CONTROL & CROP GROWTH")
            print("=" * 70)
        
        dome_controller, total_energy = self._simulate_environmental_control(
            substrate_ready_day, verbose)
        harvest_date = planting_date + timedelta(days=self.params.growth_duration_days)
        
        # Compile results
        mission_success = self._evaluate_mission_success(
            spray_results, curing_profile, nutrient_profile, dome_controller)
        
        self.results = SimulationResults(
            mission_params=self.params,
            spray_results=spray_results,
            curing_profile=curing_profile,
            nutrient_profile=nutrient_profile,
            dome_controller=dome_controller,
            coverage_area_m2=spray_results.coverage_area,
            substrate_ready_day=substrate_ready_day,
            total_energy_kwh=total_energy,
            mission_success=mission_success,
            start_date=start_date,
            spray_date=spray_date,
            cure_date=cure_date,
            planting_date=planting_date,
            harvest_date=harvest_date
        )
        
        if verbose:
            self._print_summary()
        
        return self.results
    
    def _simulate_spray_application(self, verbose: bool) -> SprayResults:
        """Simulate spray dynamics."""
        spray_params = SprayParameters(
            pressure_psi=self.params.application_pressure_psi,
            ambient_temp_c=self.params.ambient_temp_c,
            surface_slope=self.params.surface_slope_deg
        )
        
        simulator = SprayDynamics(spray_params)
        results = simulator.simulate_radial_expansion(self.params.spray_volume_ml)
        
        if verbose:
            print(f"Spray Volume: {self.params.spray_volume_ml} mL")
            print(f"Application Pressure: {self.params.application_pressure_psi} PSI")
            print(f"Surface Temperature: {self.params.ambient_temp_c}°C")
            print(f"Surface Slope: {self.params.surface_slope_deg}°")
            print(f"\nResults:")
            print(f"  Coverage Radius: {results.max_radius:.2f} m")
            print(f"  Coverage Area: {results.coverage_area:.2f} m²")
            print(f"  Average Thickness: {results.thickness[-1]:.2f} mm")
            print(f"  Expansion Time (90%): {results.time[np.argmax(results.radius > 0.9*results.max_radius)]:.1f} s")
        
        return results
    
    def _simulate_curing(self, verbose: bool) -> CuringProfile:
        """Simulate curing behavior."""
        regolith = RegolithProperties()  # JSC-1A simulant properties
        
        simulator = CuringSimulator(
            uv_assisted=self.params.uv_assisted,
            regolith=regolith
        )
        
        profile = simulator.simulate_curing(
            temperature_c=self.params.ambient_temp_c,
            duration_min=30.0
        )
        
        cure_time = simulator.calculate_cure_time(self.params.ambient_temp_c)
        
        if verbose:
            print(f"Formulation: {'UV-assisted' if self.params.uv_assisted else 'Standard'}")
            print(f"Curing Temperature: {self.params.ambient_temp_c}°C")
            print(f"Regolith: JSC-1A simulant")
            print(f"  SiO₂: {regolith.silica_content}%")
            print(f"  Al₂O₃: {regolith.alumina_content}%")
            print(f"\nResults:")
            print(f"  Full Cure Time: {cure_time:.1f} minutes")
            print(f"  Bond Strength (30 min): {profile.bond_strength_mpa[-1]:.2f} MPa")
            print(f"  Cure Fraction (30 min): {profile.cure_fraction[-1]*100:.1f}%")
        
        return profile
    
    def _simulate_nutrient_release(self, verbose: bool) -> Tuple[NutrientProfile, int]:
        """Simulate nutrient release and determine planting readiness."""
        simulator = NutrientReleaseSimulator(
            initial_ph=10.0,
            water_availability=1.0
        )
        
        profile = simulator.simulate_release_cycle(duration_days=60)
        
        # Check when ready for planting
        requirements = PlantRequirements()
        ready_day, status = simulator.check_plant_readiness(profile, requirements)
        
        if verbose:
            print(f"Simulation Duration: 60 days")
            print(f"Target Crop: {self.params.target_crop}")
            print(f"\nSubstrate Readiness:")
            if ready_day:
                print(f"  ✓ Ready for planting: Day {ready_day}")
            else:
                print(f"  ✗ Not ready within 60 days")
            
            print(f"\nNutrient Levels at Day {ready_day or 30}:")
            idx = int((ready_day or 30) / 60 * len(profile.time_days))
            print(f"  Nitrogen (N):   {profile.concentrations[Nutrient.NITROGEN][idx]:6.1f} ppm")
            print(f"  Phosphorus (P): {profile.concentrations[Nutrient.PHOSPHORUS][idx]:6.1f} ppm")
            print(f"  Potassium (K):  {profile.concentrations[Nutrient.POTASSIUM][idx]:6.1f} ppm")
            print(f"  Magnesium (Mg): {profile.concentrations[Nutrient.MAGNESIUM][idx]:6.1f} ppm")
            print(f"  Sulfur (S):     {profile.concentrations[Nutrient.SULFUR][idx]:6.1f} ppm")
            print(f"  pH:             {profile.ph_values[idx]:6.2f}")
            print(f"  Porosity:       {profile.substrate_porosity[idx]*100:6.1f}%")
        
        return profile, ready_day or self.params.planting_delay_days
    
    def _simulate_environmental_control(self, 
                                       planting_day: int,
                                       verbose: bool) -> Tuple[AIEnvironmentalController, float]:
        """Simulate dome environmental control."""
        controller = AIEnvironmentalController(dome_id="LUNAR-DOME-001")
        
        # Configure for growing mode
        controller.state.mode = ControlMode.GROWING
        controller.state.setpoints.temperature_c = self.params.dome_temperature_c
        controller.state.setpoints.humidity_percent = self.params.dome_humidity_percent
        controller.state.setpoints.photoperiod_hours = self.params.photoperiod_hours
        
        # Set realistic initial conditions (cold lunar environment)
        controller.state.sensors.temperature_c = 15.0
        controller.state.sensors.humidity_percent = 40.0
        controller.state.sensors.co2_ppm = 400.0
        
        # Simulate from planting through harvest
        simulation_hours = self.params.growth_duration_days * 24
        
        if verbose:
            print(f"Dome ID: {controller.dome_id}")
            print(f"Growth Duration: {self.params.growth_duration_days} days")
            print(f"Photoperiod: {self.params.photoperiod_hours} hours/day")
            print(f"\nSetpoints:")
            print(f"  Temperature: {controller.state.setpoints.temperature_c}°C")
            print(f"  Humidity: {controller.state.setpoints.humidity_percent}%")
            print(f"  CO₂: {controller.state.setpoints.co2_ppm} ppm")
            print(f"\nRunning {simulation_hours:.0f}-hour simulation...")
        
        controller.run_simulation(duration_hours=simulation_hours, dt=60.0)
        
        # Calculate total energy
        times = [h['sensors']['timestamp'] / 3600 for h in controller.history]
        energy = [h['energy_consumption_w'] for h in controller.history]
        total_energy_kwh = np.trapz(energy, times)
        
        if verbose:
            final = controller.state.sensors
            print(f"\nFinal Environmental Conditions:")
            print(f"  Temperature: {final.temperature_c:.1f}°C")
            print(f"  Humidity: {final.humidity_percent:.1f}%")
            print(f"  CO₂: {final.co2_ppm:.0f} ppm")
            print(f"  O₂: {final.o2_percent:.1f}%")
            print(f"\nEnergy Consumption:")
            print(f"  Total: {total_energy_kwh:.2f} kWh")
            print(f"  Average Power: {total_energy_kwh*1000/simulation_hours:.1f} W")
            print(f"  Per Day: {total_energy_kwh/self.params.growth_duration_days:.2f} kWh/day")
        
        return controller, total_energy_kwh
    
    def _evaluate_mission_success(self, 
                                  spray: SprayResults,
                                  curing: CuringProfile,
                                  nutrients: NutrientProfile,
                                  dome: AIEnvironmentalController) -> bool:
        """Evaluate overall mission success criteria."""
        # Check spray coverage
        spray_ok = spray.coverage_area >= 10.0  # At least 10 m²
        
        # Check curing strength
        curing_ok = curing.bond_strength_mpa[-1] >= 3.0  # At least 3 MPa
        
        # Check nutrient availability
        final_idx = -1
        n_ok = nutrients.concentrations[Nutrient.NITROGEN][final_idx] >= 100
        p_ok = nutrients.concentrations[Nutrient.PHOSPHORUS][final_idx] >= 30
        k_ok = nutrients.concentrations[Nutrient.POTASSIUM][final_idx] >= 150
        nutrients_ok = n_ok and p_ok and k_ok
        
        # Check environmental stability
        temp_deviation = abs(dome.state.sensors.temperature_c - 
                           dome.state.setpoints.temperature_c)
        env_ok = temp_deviation < 5.0  # Within 5°C of setpoint
        
        return spray_ok and curing_ok and nutrients_ok and env_ok
    
    def _print_header(self):
        """Print simulation header."""
        print("\n" + "=" * 70)
        print("BIO-STABILIZING LUNAR SPRAY - INTEGRATED MISSION SIMULATION")
        print("=" * 70)
        print("Author: Don Michael Feeney Jr")
        print("Based on: Bio-Stabilizing Lunar Spray White Paper (April 2025)")
        print("=" * 70 + "\n")
    
    def _print_summary(self):
        """Print mission summary."""
        if not self.results:
            return
        
        r = self.results
        
        print("\n" + "=" * 70)
        print("MISSION SUMMARY")
        print("=" * 70)
        print(f"\nTimeline:")
        print(f"  Spray Application: {r.spray_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Surface Cured:     {r.cure_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Substrate Ready:   {r.planting_date.strftime('%Y-%m-%d')}")
        print(f"  Harvest Date:      {r.harvest_date.strftime('%Y-%m-%d')}")
        print(f"  Total Duration:    {(r.harvest_date - r.start_date).days} days")
        
        print(f"\nKey Metrics:")
        print(f"  Coverage Area:     {r.coverage_area_m2:.2f} m²")
        print(f"  Bond Strength:     {r.curing_profile.bond_strength_mpa[-1]:.2f} MPa")
        print(f"  Substrate Ready:   Day {r.substrate_ready_day}")
        print(f"  Total Energy:      {r.total_energy_kwh:.2f} kWh")
        
        print(f"\nMission Status: {'✓ SUCCESS' if r.mission_success else '✗ FAILED'}")
        print("=" * 70 + "\n")
    
    def generate_report(self, output_path: str = "mission_report.json"):
        """
        Generate detailed JSON report.
        
        Args:
            output_path: Path to save report
        """
        if not self.results:
            print("No simulation results to report. Run simulation first.")
            return
        
        report = {
            "mission": {
                "landing_site": self.params.landing_site,
                "target_crop": self.params.target_crop,
                "start_date": self.results.start_date.isoformat(),
                "harvest_date": self.results.harvest_date.isoformat(),
                "total_days": (self.results.harvest_date - self.results.start_date).days,
                "success": self.results.mission_success
            },
            "spray_application": {
                "volume_ml": self.params.spray_volume_ml,
                "coverage_area_m2": self.results.coverage_area_m2,
                "max_radius_m": self.results.spray_results.max_radius,
                "thickness_mm": float(self.results.spray_results.thickness[-1])
            },
            "curing": {
                "cure_time_minutes": float(self.results.curing_profile.time[-1]),
                "bond_strength_mpa": float(self.results.curing_profile.bond_strength_mpa[-1]),
                "uv_assisted": self.params.uv_assisted
            },
            "nutrients": {
                "substrate_ready_day": self.results.substrate_ready_day,
                "final_ph": float(self.results.nutrient_profile.ph_values[-1])
            },
            "energy": {
                "total_kwh": self.results.total_energy_kwh,
                "avg_power_w": self.results.total_energy_kwh * 1000 / 
                              (self.params.growth_duration_days * 24)
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report saved to: {output_path}")
    
    def plot_complete_timeline(self, save_path: Optional[str] = None):
        """
        Create comprehensive visualization of entire mission.
        
        Args:
            save_path: Optional path to save figure
        """
        if not self.results:
            print("No simulation results to plot. Run simulation first.")
            return
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Spray expansion
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(self.results.spray_results.time, 
                self.results.spray_results.radius, 'b-', linewidth=2)
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Radius (m)')
        ax1.set_title('Spray Expansion')
        ax1.grid(True, alpha=0.3)
        
        # Curing
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(self.results.curing_profile.time,
                self.results.curing_profile.bond_strength_mpa, 'r-', linewidth=2)
        ax2.set_xlabel('Time (min)')
        ax2.set_ylabel('Bond Strength (MPa)')
        ax2.set_title('Curing Progress')
        ax2.grid(True, alpha=0.3)
        
        # Cure fraction
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.plot(self.results.curing_profile.time,
                self.results.curing_profile.cure_fraction * 100, 'g-', linewidth=2)
        ax3.set_xlabel('Time (min)')
        ax3.set_ylabel('Cure Fraction (%)')
        ax3.set_title('Cure Completion')
        ax3.grid(True, alpha=0.3)
        
        # Nutrients (NPK)
        ax4 = fig.add_subplot(gs[1, :])
        ax4.plot(self.results.nutrient_profile.time_days,
                self.results.nutrient_profile.concentrations[Nutrient.NITROGEN],
                'g-', linewidth=2, label='Nitrogen')
        ax4.plot(self.results.nutrient_profile.time_days,
                self.results.nutrient_profile.concentrations[Nutrient.PHOSPHORUS],
                'purple', linewidth=2, label='Phosphorus')
        ax4.plot(self.results.nutrient_profile.time_days,
                self.results.nutrient_profile.concentrations[Nutrient.POTASSIUM],
                'b-', linewidth=2, label='Potassium')
        ax4.axvline(x=self.results.substrate_ready_day, color='r', 
                   linestyle='--', label='Planting Day')
        ax4.set_xlabel('Days')
        ax4.set_ylabel('Concentration (ppm)')
        ax4.set_title('Nutrient Release Timeline')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Temperature control
        ax5 = fig.add_subplot(gs[2, 0])
        times = [h['sensors']['timestamp'] / 3600 for h in self.results.dome_controller.history]
        temps = [h['sensors']['temperature_c'] for h in self.results.dome_controller.history]
        ax5.plot(times, temps, 'r-', linewidth=1)
        ax5.axhline(y=self.params.dome_temperature_c, color='g', linestyle='--')
        ax5.set_xlabel('Hours')
        ax5.set_ylabel('Temperature (°C)')
        ax5.set_title('Dome Temperature')
        ax5.grid(True, alpha=0.3)
        
        # Humidity control
        ax6 = fig.add_subplot(gs[2, 1])
        humidity = [h['sensors']['humidity_percent'] for h in self.results.dome_controller.history]
        ax6.plot(times, humidity, 'b-', linewidth=1)
        ax6.axhline(y=self.params.dome_humidity_percent, color='g', linestyle='--')
        ax6.set_xlabel('Hours')
        ax6.set_ylabel('Humidity (%)')
        ax6.set_title('Dome Humidity')
        ax6.grid(True, alpha=0.3)
        
        # Energy consumption
        ax7 = fig.add_subplot(gs[2, 2])
        energy = [h['energy_consumption_w'] for h in self.results.dome_controller.history]
        ax7.plot(times, energy, 'orange', linewidth=1)
        ax7.set_xlabel('Hours')
        ax7.set_ylabel('Power (W)')
        ax7.set_title('Energy Consumption')
        ax7.grid(True, alpha=0.3)
        
        plt.suptitle(f'Complete Mission Timeline - {self.params.landing_site}', 
                    fontsize=14, fontweight='bold')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()


def run_example_mission():
    """Run complete example mission simulation."""
    # Configure mission
    params = MissionParameters(
        landing_site="Lunar South Pole - Shackleton Crater Rim",
        spray_volume_ml=500.0,
        application_pressure_psi=25.0,
        surface_slope_deg=5.0,
        ambient_temp_c=0.0,
        uv_assisted=True,
        target_crop="Lettuce (Lactuca sativa)",
        planting_delay_days=25,
        growth_duration_days=30,
        dome_temperature_c=22.0,
        dome_humidity_percent=65.0,
        photoperiod_hours=16.0
    )
    
    # Run simulation
    simulation = IntegratedLunarSpraySimulation(params)
    results = simulation.run_complete_simulation(verbose=True)
    
    # Generate outputs
    simulation.generate_report("mission_report.json")
    simulation.plot_complete_timeline("mission_timeline.png")
    
    return simulation


if __name__ == "__main__":
    simulation = run_example_mission()
    print("\nSimulation complete! Check mission_report.json and mission_timeline.png")
