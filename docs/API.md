# API Documentation

Complete API reference for Bio-Stabilizing Lunar Spray simulation modules.

---

## Table of Contents

- [Spray Dynamics](#spray-dynamics)
- [Curing Simulation](#curing-simulation)
- [Nutrient Release](#nutrient-release)
- [Environmental Control](#environmental-control)
- [Utilities](#utilities)
- [Integrated Simulation](#integrated-simulation)

---

## Spray Dynamics

### `SprayDynamics`

Models radial expansion and coverage behavior of spray on lunar regolith.

#### Constructor

```python
SprayDynamics(params: SprayParameters)
```

**Parameters:**
- `params` (SprayParameters): Configuration for spray application

**Example:**
```python
from src import SprayDynamics, SprayParameters

params = SprayParameters(
    pressure_psi=25.0,
    ambient_temp_c=0.0,
    surface_slope=5.0
)
simulator = SprayDynamics(params)
```

#### Methods

##### `calculate_coverage_radius(volume_ml: float) -> float`

Calculate expected coverage radius for given spray volume.

**Parameters:**
- `volume_ml` (float): Spray volume in milliliters

**Returns:**
- `float`: Maximum radius in meters

**Example:**
```python
radius = simulator.calculate_coverage_radius(volume_ml=500)
print(f"Coverage radius: {radius:.2f} m")
```

##### `simulate_radial_expansion(volume_ml: float, duration_s: float = 30.0, time_steps: int = 100) -> SprayResults`

Simulate time-dependent radial expansion.

**Parameters:**
- `volume_ml` (float): Total spray volume
- `duration_s` (float, optional): Simulation duration in seconds. Default: 30.0
- `time_steps` (int, optional): Number of time points. Default: 100

**Returns:**
- `SprayResults`: Object containing time-series data
  - `time` (np.ndarray): Time array in seconds
  - `radius` (np.ndarray): Radius array in meters
  - `thickness` (np.ndarray): Thickness array in millimeters
  - `coverage_area` (float): Total coverage in m²
  - `max_radius` (float): Maximum radius in meters
  - `volume_ml` (float): Input volume

**Example:**
```python
results = simulator.simulate_radial_expansion(
    volume_ml=500,
    duration_s=30.0,
    time_steps=100
)
print(f"Final radius: {results.max_radius:.2f} m")
print(f"Coverage area: {results.coverage_area:.2f} m²")
```

##### `estimate_coverage_area(volume_ml: float) -> float`

Quick calculation of total coverage area.

**Parameters:**
- `volume_ml` (float): Spray volume

**Returns:**
- `float`: Coverage area in m²

##### `calculate_optimal_volume(target_area_m2: float, target_thickness_mm: float = 1.0) -> float`

Calculate required volume for desired coverage.

**Parameters:**
- `target_area_m2` (float): Desired coverage area
- `target_thickness_mm` (float, optional): Desired thickness. Default: 1.0

**Returns:**
- `float`: Required volume in milliliters

### `SprayParameters`

Configuration dataclass for spray application.

**Attributes:**
- `pressure_psi` (float): Application pressure (20-30 PSI recommended)
- `ambient_temp_c` (float): Ambient temperature in Celsius
- `surface_slope` (float): Surface incline in degrees (0-15)
- `viscosity_cp` (float): Fluid viscosity in centipoise. Default: 3000.0
- `nozzle_diameter_mm` (float): Spray nozzle diameter. Default: 2.0

---

## Curing Simulation

### `CuringSimulator`

Simulates geopolymer curing behavior under lunar conditions.

#### Constructor

```python
CuringSimulator(uv_assisted: bool = False, regolith: RegolithProperties = None)
```

**Parameters:**
- `uv_assisted` (bool, optional): Whether UV-assisted formulation is used. Default: False
- `regolith` (RegolithProperties, optional): Regolith composition. Default: JSC-1A

**Example:**
```python
from src import CuringSimulator, RegolithProperties

regolith = RegolithProperties()  # JSC-1A default
simulator = CuringSimulator(uv_assisted=True, regolith=regolith)
```

#### Methods

##### `calculate_cure_time(temperature_c: float) -> float`

Calculate full cure time at given temperature.

**Parameters:**
- `temperature_c` (float): Ambient temperature (-170 to 120°C)

**Returns:**
- `float`: Cure time in minutes

**Example:**
```python
cure_time = simulator.calculate_cure_time(temperature_c=0.0)
print(f"Cure time at 0°C: {cure_time:.1f} minutes")
```

##### `calculate_bond_strength(time_min: float, temperature_c: float) -> float`

Calculate bond strength at given time and temperature.

**Parameters:**
- `time_min` (float): Elapsed time in minutes
- `temperature_c` (float): Curing temperature

**Returns:**
- `float`: Bond strength in MPa

##### `simulate_curing(temperature_c: float, duration_min: float = 30.0, time_steps: int = 200) -> CuringProfile`

Simulate complete curing process.

**Parameters:**
- `temperature_c` (float): Ambient temperature
- `duration_min` (float, optional): Simulation duration. Default: 30.0
- `time_steps` (int, optional): Number of time points. Default: 200

**Returns:**
- `CuringProfile`: Object containing:
  - `time` (np.ndarray): Time in minutes
  - `cure_fraction` (np.ndarray): Cure fraction (0-1)
  - `bond_strength_mpa` (np.ndarray): Bond strength in MPa
  - `temperature_c` (float): Temperature
  - `uv_assisted` (bool): UV assistance flag
  - `phase` (np.ndarray): Curing phase at each time point

**Example:**
```python
profile = simulator.simulate_curing(
    temperature_c=0.0,
    duration_min=30.0
)
print(f"Final strength: {profile.bond_strength_mpa[-1]:.2f} MPa")
print(f"Cure fraction: {profile.cure_fraction[-1]*100:.1f}%")
```

##### `compare_temperatures(temps: List[float], duration_min: float = 30.0) -> List[CuringProfile]`

Compare curing at multiple temperatures.

**Parameters:**
- `temps` (List[float]): List of temperatures to compare
- `duration_min` (float, optional): Simulation duration. Default: 30.0

**Returns:**
- `List[CuringProfile]`: List of profiles for each temperature

### `RegolithProperties`

Lunar regolith composition and properties.

**Attributes:**
- `name` (str): Sample name (e.g., "JSC-1A")
- `silica_content` (float): SiO₂ percentage
- `alumina_content` (float): Al₂O₃ percentage
- `iron_content` (float): FeO percentage
- `particle_size_um` (float): Mean particle size in micrometers
- `density_g_cm3` (float): Bulk density
- `surface_area_m2_g` (float): Specific surface area

---

## Nutrient Release

### `NutrientReleaseSimulator`

Simulates nutrient release and biological transition over 60-day cycle.

#### Constructor

```python
NutrientReleaseSimulator(initial_ph: float = 10.0, water_availability: float = 1.0)
```

**Parameters:**
- `initial_ph` (float, optional): Starting pH after curing. Default: 10.0
- `water_availability` (float, optional): Water factor (0-1). Default: 1.0

**Example:**
```python
from src import NutrientReleaseSimulator

simulator = NutrientReleaseSimulator(
    initial_ph=10.0,
    water_availability=1.0
)
```

#### Methods

##### `calculate_potassium_release(day: float) -> float`

Calculate K⁺ concentration at given day.

**Parameters:**
- `day` (float): Days since application (0-60)

**Returns:**
- `float`: Potassium concentration in ppm

##### `calculate_nitrogen_release(day: float) -> float`

Calculate nitrogen concentration at given day.

**Parameters:**
- `day` (float): Days since application

**Returns:**
- `float`: Nitrogen concentration in ppm

##### `calculate_phosphorus_release(day: float) -> float`

Calculate phosphorus concentration at given day.

**Parameters:**
- `day` (float): Days since application

**Returns:**
- `float`: Phosphorus concentration in ppm

##### `calculate_ph(day: float) -> float`

Calculate pH at given day.

**Parameters:**
- `day` (float): Days since application

**Returns:**
- `float`: pH value (typically 10 → 6.5)

##### `simulate_release_cycle(duration_days: int = 60, time_points: int = 120) -> NutrientProfile`

Simulate complete 60-day nutrient release cycle.

**Parameters:**
- `duration_days` (int, optional): Simulation duration. Default: 60
- `time_points` (int, optional): Number of time points. Default: 120

**Returns:**
- `NutrientProfile`: Object containing:
  - `time_days` (np.ndarray): Time in days
  - `concentrations` (Dict[Nutrient, np.ndarray]): All nutrient concentrations
  - `ph_values` (np.ndarray): pH evolution
  - `substrate_porosity` (np.ndarray): Porosity development

**Example:**
```python
profile = simulator.simulate_release_cycle(duration_days=60)

# Access nutrients
nitrogen = profile.concentrations[Nutrient.NITROGEN]
phosphorus = profile.concentrations[Nutrient.PHOSPHORUS]
potassium = profile.concentrations[Nutrient.POTASSIUM]

print(f"Final N: {nitrogen[-1]:.0f} ppm")
print(f"Final pH: {profile.ph_values[-1]:.2f}")
```

##### `check_plant_readiness(profile: NutrientProfile, requirements: PlantRequirements = None) -> Tuple[int, Dict]`

Determine when substrate is ready for planting.

**Parameters:**
- `profile` (NutrientProfile): Nutrient profile from simulation
- `requirements` (PlantRequirements, optional): Plant requirements. Default: standard

**Returns:**
- `Tuple[int, Dict]`: (ready_day, status_dict)
  - `ready_day`: Day when substrate is ready
  - `status_dict`: Detailed readiness status

**Example:**
```python
from src import PlantRequirements

requirements = PlantRequirements()
ready_day, status = simulator.check_plant_readiness(profile, requirements)

print(f"Substrate ready: Day {ready_day}")
print(f"Nitrogen sufficient: Day {status['n_sufficient']}")
```

### `Nutrient` Enum

Available nutrients tracked in the system:
- `Nutrient.NITROGEN` - N
- `Nutrient.PHOSPHORUS` - P
- `Nutrient.POTASSIUM` - K
- `Nutrient.MAGNESIUM` - Mg
- `Nutrient.SULFUR` - S
- `Nutrient.CALCIUM` - Ca

---

## Environmental Control

### `AIEnvironmentalController`

AI-regulated environmental control system for lunar growth domes.

#### Constructor

```python
AIEnvironmentalController(dome_id: str = "DOME-001")
```

**Parameters:**
- `dome_id` (str, optional): Unique identifier for dome. Default: "DOME-001"

**Example:**
```python
from src import AIEnvironmentalController, ControlMode

controller = AIEnvironmentalController(dome_id="LUNAR-DOME-001")
controller.state.mode = ControlMode.GROWING
```

#### Methods

##### `update_control(dt: float = 1.0) -> ControlActions`

Execute one control loop update.

**Parameters:**
- `dt` (float, optional): Time step in seconds. Default: 1.0

**Returns:**
- `ControlActions`: Actuator commands

##### `run_simulation(duration_hours: float = 24.0, dt: float = 60.0)`

Run multi-hour simulation.

**Parameters:**
- `duration_hours` (float, optional): Simulation duration. Default: 24.0
- `dt` (float, optional): Time step in seconds. Default: 60.0

**Example:**
```python
controller.run_simulation(duration_hours=168.0, dt=60.0)  # 1 week
print(f"Final temp: {controller.state.sensors.temperature_c:.1f}°C")
print(f"Final humidity: {controller.state.sensors.humidity_percent:.1f}%")
```

##### `plot_performance(save_path: str = None)`

Visualize system performance over time.

**Parameters:**
- `save_path` (str, optional): Path to save figure. Default: None (display)

### `EnvironmentalSetpoints`

Target environmental parameters.

**Attributes:**
- `temperature_c` (float): Target temperature. Default: 22.0
- `humidity_percent` (float): Target humidity. Default: 65.0
- `co2_ppm` (float): Target CO₂. Default: 800.0
- `o2_percent` (float): Target O₂. Default: 20.9
- `photoperiod_hours` (float): Hours of light per day. Default: 16.0

---

## Utilities

### `PhysicalConstants`

Fundamental physical constants for lunar simulations.

**Constants:**
- `GRAVITY_MOON` (float): 1.62 m/s²
- `GRAVITY_EARTH` (float): 9.81 m/s²
- `LUNAR_DAY_HOURS` (float): 708 hours
- `LUNAR_TEMP_MAX_C` (float): 127°C
- `LUNAR_TEMP_MIN_C` (float): -173°C
- `GAS_CONSTANT` (float): 8.314 J/(mol·K)

### `ChemicalConstants`

Chemical properties and molecular weights.

**Dictionaries:**
- `MW` (Dict[str, float]): Molecular weights in g/mol
- `NUTRIENT_MASS` (Dict[str, float]): Nutrient atomic masses

### `UnitConverter`

Unit conversion utilities.

**Methods:**
- `celsius_to_kelvin(temp_c: float) -> float`
- `kelvin_to_celsius(temp_k: float) -> float`
- `psi_to_pascal(pressure_psi: float) -> float`
- `pascal_to_psi(pressure_pa: float) -> float`
- `ml_to_cubic_meters(volume_ml: float) -> float`
- `kwh_to_joules(energy_kwh: float) -> float`

**Example:**
```python
from src import UnitConverter

kelvin = UnitConverter.celsius_to_kelvin(0)  # 273.15
pascals = UnitConverter.psi_to_pascal(25)    # 172369
```

---

## Integrated Simulation

### `IntegratedLunarSpraySimulation`

Complete end-to-end mission simulator.

#### Constructor

```python
IntegratedLunarSpraySimulation(params: MissionParameters = None)
```

**Parameters:**
- `params` (MissionParameters, optional): Mission configuration. Default: standard

**Example:**
```python
from integrated_simulation import (
    IntegratedLunarSpraySimulation,
    MissionParameters
)

params = MissionParameters(
    landing_site="Shackleton Crater",
    spray_volume_ml=500.0,
    target_crop="Lettuce",
    growth_duration_days=30
)

simulation = IntegratedLunarSpraySimulation(params)
```

#### Methods

##### `run_complete_simulation(start_date: datetime = None, verbose: bool = True) -> SimulationResults`

Execute complete mission simulation from spray to harvest.

**Parameters:**
- `start_date` (datetime, optional): Mission start. Default: now
- `verbose` (bool, optional): Print progress. Default: True

**Returns:**
- `SimulationResults`: Complete mission results including:
  - `mission_params`: Configuration
  - `spray_results`: Spray application data
  - `curing_profile`: Curing behavior
  - `nutrient_profile`: Nutrient release
  - `dome_controller`: Environmental control
  - `coverage_area_m2`: Coverage area
  - `substrate_ready_day`: Planting day
  - `total_energy_kwh`: Energy consumption
  - `mission_success`: Success flag

**Example:**
```python
results = simulation.run_complete_simulation(verbose=True)

print(f"Mission success: {results.mission_success}")
print(f"Coverage: {results.coverage_area_m2:.2f} m²")
print(f"Substrate ready: Day {results.substrate_ready_day}")
print(f"Total energy: {results.total_energy_kwh:.2f} kWh")
```

##### `generate_report(output_path: str = "mission_report.json")`

Generate detailed JSON report.

**Parameters:**
- `output_path` (str, optional): Output file path

##### `plot_complete_timeline(save_path: str = None)`

Create comprehensive visualization of entire mission.

**Parameters:**
- `save_path` (str, optional): Path to save figure

### `MissionParameters`

Complete mission configuration.

**Attributes:**
- `landing_site` (str): Location name
- `spray_volume_ml` (float): Spray volume
- `application_pressure_psi` (float): Application pressure
- `surface_slope_deg` (float): Surface slope
- `ambient_temp_c` (float): Temperature
- `uv_assisted` (bool): UV assistance flag
- `target_crop` (str): Crop type
- `planting_delay_days` (int): Days before planting
- `growth_duration_days` (int): Days to harvest
- `dome_temperature_c` (float): Dome temperature
- `dome_humidity_percent` (float): Dome humidity
- `photoperiod_hours` (float): Light hours per day

---

## Error Handling

All modules raise standard Python exceptions:

- `ValueError`: Invalid parameter values
- `TypeError`: Incorrect types
- `FileNotFoundError`: Missing data files
- `RuntimeError`: Simulation failures

**Example:**
```python
try:
    simulator = SprayDynamics(params)
    results = simulator.simulate_radial_expansion(volume_ml=-100)
except ValueError as e:
    print(f"Invalid parameter: {e}")
```

---

## Performance Considerations

- **Spray simulations**: ~0.01s for 100 time steps
- **Curing simulations**: ~0.02s for 200 time steps
- **Nutrient simulations**: ~0.05s for 120 time points
- **Environmental control**: ~5s for 24-hour simulation
- **Integrated mission**: ~15s for complete 30-day mission

For best performance:
- Use fewer time steps during development
- Enable caching for repeated calculations
- Run benchmarks with `pytest -m benchmark`

---

## Version Compatibility

- Python: 3.8+
- NumPy: 1.21+
- SciPy: 1.7+
- Matplotlib: 3.4+

---

## Support

For issues, questions, or contributions:
- GitHub Issues: [Project Issues](https://github.com/dfeen87/bio-stabilizing-lunar-spray/issues)
- Email: dfeen87@gmail.com
- Documentation: [Full Docs](https://github.com/dfeen87/bio-stabilizing-lunar-spray/tree/main/docs)
