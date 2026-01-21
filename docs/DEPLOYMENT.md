# Deployment Guide

Complete guide for installing, configuring, and using the Bio-Stabilizing Lunar Spray simulation system.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Git for cloning repository

### Method 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/dfeen87/bio-stabilizing-lunar-spray.git
cd bio-stabilizing-lunar-spray

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install in development mode
pip install -e .

# Install with optional dependencies
pip install -e ".[dev,viz]"
```

### Method 2: Install from PyPI (Future)

```bash
# Once published to PyPI
pip install bio-stabilizing-lunar-spray
```

### Method 3: Install Dependencies Only

```bash
# Install only required dependencies
pip install -r requirements.txt
```

### Verify Installation

```bash
# Test import
python -c "from src import SprayDynamics; print('✓ Installation successful!')"

# Run tests
pytest tests/ -v

# Check version
python -c "import src; print(src.__version__)"
```

---

## Quick Start

### 1. Basic Spray Simulation

```python
from src import SprayDynamics, SprayParameters

# Configure spray parameters
params = SprayParameters(
    pressure_psi=25.0,
    ambient_temp_c=0.0,
    surface_slope=5.0
)

# Create simulator
simulator = SprayDynamics(params)

# Run simulation
results = simulator.simulate_radial_expansion(volume_ml=500)

# View results
print(f"Coverage area: {results.coverage_area:.2f} m²")
print(f"Max radius: {results.max_radius:.2f} m")
```

### 2. Complete Mission Simulation

```python
from integrated_simulation import (
    IntegratedLunarSpraySimulation,
    MissionParameters
)

# Configure mission
params = MissionParameters(
    landing_site="Lunar South Pole",
    spray_volume_ml=500.0,
    target_crop="Lettuce",
    growth_duration_days=30
)

# Run simulation
simulation = IntegratedLunarSpraySimulation(params)
results = simulation.run_complete_simulation(verbose=True)

# Generate outputs
simulation.generate_report("mission_report.json")
simulation.plot_complete_timeline("timeline.png")

# Check success
if results.mission_success:
    print("✓ Mission successful!")
    print(f"Harvest date: {results.harvest_date}")
```

### 3. Run from Command Line

```bash
# After pip install
lunar-spray

# Or directly
python integrated_simulation.py
```

---

## Configuration

### Environment Variables

```bash
# Optional: Set output directory
export LUNAR_SPRAY_OUTPUT_DIR="/path/to/output"

# Optional: Set log level
export LUNAR_SPRAY_LOG_LEVEL="INFO"
```

### Configuration Files

Create `config.json` for custom defaults:

```json
{
  "spray": {
    "default_pressure_psi": 25.0,
    "default_volume_ml": 500.0
  },
  "curing": {
    "uv_assisted": true
  },
  "environment": {
    "dome_temperature_c": 22.0,
    "photoperiod_hours": 16.0
  }
}
```

Load configuration:

```python
import json

with open("config.json") as f:
    config = json.load(f)

params = SprayParameters(
    pressure_psi=config["spray"]["default_pressure_psi"]
)
```

---

## Usage Examples

### Example 1: Optimize Spray Volume

```python
from src import SprayDynamics, SprayParameters

simulator = SprayDynamics(SprayParameters())

# Target coverage
target_area = 15.0  # m²

# Calculate optimal volume
optimal_volume = simulator.calculate_optimal_volume(
    target_area_m2=target_area,
    target_thickness_mm=1.0
)

print(f"Optimal volume: {optimal_volume:.0f} mL")

# Verify
results = simulator.simulate_radial_expansion(volume_ml=optimal_volume)
print(f"Achieved area: {results.coverage_area:.2f} m²")
```

### Example 2: Compare Temperature Effects

```python
from src import CuringSimulator

simulator = CuringSimulator(uv_assisted=True)

# Test different temperatures
temperatures = [-20, 0, 20, 40]
profiles = simulator.compare_temperatures(temperatures)

# Display results
for temp, profile in zip(temperatures, profiles):
    cure_time = simulator.calculate_cure_time(temp)
    final_strength = profile.bond_strength_mpa[-1]
    print(f"{temp:3d}°C: {cure_time:5.1f} min, {final_strength:.2f} MPa")
```

### Example 3: Nutrient Timeline

```python
from src import NutrientReleaseSimulator, Nutrient

simulator = NutrientReleaseSimulator()
profile = simulator.simulate_release_cycle(duration_days=60)

# Key milestones
for day in [0, 15, 30, 45, 60]:
    idx = int(day / 60 * len(profile.time_days))
    n = profile.concentrations[Nutrient.NITROGEN][idx]
    p = profile.concentrations[Nutrient.PHOSPHORUS][idx]
    k = profile.concentrations[Nutrient.POTASSIUM][idx]
    ph = profile.ph_values[idx]
    
    print(f"Day {day:2d}: N={n:5.0f} P={p:4.0f} K={k:5.0f} pH={ph:.2f}")
```

### Example 4: Multi-Site Comparison

```python
from integrated_simulation import IntegratedLunarSpraySimulation, MissionParameters

sites = [
    ("Shackleton Crater", -40.0, 8.0),
    ("Mare Imbrium", 20.0, 2.0),
    ("Highland Region", -10.0, 5.0),
]

results = []
for site_name, temp, slope in sites:
    params = MissionParameters(
        landing_site=site_name,
        ambient_temp_c=temp,
        surface_slope_deg=slope
    )
    
    sim = IntegratedLunarSpraySimulation(params)
    result = sim.run_complete_simulation(verbose=False)
    results.append((site_name, result))

# Compare
for site, result in results:
    print(f"{site:20s}: Day {result.substrate_ready_day}, {result.total_energy_kwh:.1f} kWh")
```

---

## Advanced Usage

### Custom Formulations

```python
from src import CuringSimulator, RegolithProperties

# Custom regolith composition
custom_regolith = RegolithProperties(
    name="Custom-1",
    silica_content=50.0,
    alumina_content=18.0,
    iron_content=8.0
)

# Simulate with custom regolith
simulator = CuringSimulator(
    uv_assisted=True,
    regolith=custom_regolith
)

profile = simulator.simulate_curing(temperature_c=0.0)
print(f"Cure time: {simulator.calculate_cure_time(0):.1f} min")
```

### Batch Simulations

```python
import numpy as np
from src import SprayDynamics, SprayParameters

# Parameter sweep
pressures = np.linspace(20, 30, 11)
volumes = [250, 500, 1000]

results_matrix = []
for pressure in pressures:
    row = []
    for volume in volumes:
        params = SprayParameters(pressure_psi=pressure)
        sim = SprayDynamics(params)
        result = sim.simulate_radial_expansion(volume_ml=volume)
        row.append(result.coverage_area)
    results_matrix.append(row)

# Analyze results
print("Coverage Area (m²) Matrix:")
print("Pressure \\ Volume: ", volumes)
for i, pressure in enumerate(pressures):
    print(f"{pressure:4.1f} PSI: ", [f"{x:5.2f}" for x in results_matrix[i]])
```

### Custom Visualization

```python
import matplotlib.pyplot as plt
from src import NutrientReleaseSimulator, Nutrient

simulator = NutrientReleaseSimulator()
profile = simulator.simulate_release_cycle(duration_days=60)

# Create custom plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Nutrients
ax1.plot(profile.time_days, profile.concentrations[Nutrient.NITROGEN], label='N')
ax1.plot(profile.time_days, profile.concentrations[Nutrient.PHOSPHORUS], label='P')
ax1.plot(profile.time_days, profile.concentrations[Nutrient.POTASSIUM], label='K')
ax1.set_ylabel('Concentration (ppm)')
ax1.legend()
ax1.grid(True)

# pH
ax2.plot(profile.time_days, profile.ph_values, 'r-')
ax2.set_xlabel('Days')
ax2.set_ylabel('pH')
ax2.grid(True)

plt.tight_layout()
plt.savefig('custom_nutrients.png', dpi=300)
```

---

## Troubleshooting

### Common Issues

#### Issue: Import Error

```
ImportError: No module named 'src'
```

**Solution:**
```bash
# Install package
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Issue: NumPy/SciPy Errors

```
ImportError: numpy.core.multiarray failed to import
```

**Solution:**
```bash
# Upgrade NumPy
pip install --upgrade numpy scipy

# Or reinstall
pip uninstall numpy scipy
pip install numpy scipy
```

#### Issue: Test Failures

```
FAILED tests/test_spray_dynamics.py::test_something
```

**Solution:**
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Clear cache
pytest --cache-clear

# Run specific test with verbose output
pytest tests/test_spray_dynamics.py::test_something -vv
```

#### Issue: Visualization Not Working

```
RuntimeError: main thread is not in main loop
```

**Solution:**
```python
# Use non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Or save instead of show
plt.savefig('output.png')
```

### Performance Issues

#### Slow Simulations

```python
# Reduce time steps
results = simulator.simulate_radial_expansion(
    volume_ml=500,
    time_steps=50  # Instead of 100
)

# Use coarser resolution for nutrients
profile = nutrient_sim.simulate_release_cycle(
    duration_days=60,
    time_points=60  # Instead of 120
)
```

#### Memory Issues

```python
# Process in chunks for large parameter sweeps
import gc

for condition in large_condition_list:
    result = run_simulation(condition)
    # Process result immediately
    save_result(result)
    # Clear memory
    gc.collect()
```

---

## Best Practices

### 1. Always Use Virtual Environments

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -e .
```

### 2. Version Control Your Configurations

```bash
# Track mission configurations
git add config/missions/*.json
git commit -m "Add new mission configuration"
```

### 3. Save Simulation Results

```python
import json

# Save results
results_dict = {
    'coverage_area': results.coverage_area,
    'cure_time': profile.time[-1],
    'substrate_ready_day': ready_day
}

with open('results.json', 'w') as f:
    json.dump(results_dict, f, indent=2)
```

### 4. Document Your Experiments

```python
# Add metadata to results
metadata = {
    'date': datetime.now().isoformat(),
    'parameters': {
        'pressure': params.pressure_psi,
        'temperature': params.ambient_temp_c
    },
    'results': results_dict
}
```

### 5. Use Logging for Production

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting simulation...")
results = simulator.simulate_radial_expansion(volume_ml=500)
logger.info(f"Coverage: {results.coverage_area:.2f} m²")
```

### 6. Run Tests Before Deployment

```bash
# Full test suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Quick sanity check
pytest tests/ -m "not slow" -x
```

---

## Deployment Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -e .`)
- [ ] Tests passing (`pytest tests/ -v`)
- [ ] Configuration files created
- [ ] Output directory set up
- [ ] Documentation reviewed
- [ ] Example scripts tested
- [ ] Version control initialized
- [ ] Backup strategy in place

---

## Production Deployment

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "integrated_simulation.py"]
```

Build and run:
```bash
docker build -t lunar-spray .
docker run lunar-spray
```

### Cloud Deployment

```bash
# Example: AWS Lambda deployment
# Package dependencies
pip install -r requirements.txt -t package/
cp -r src package/
cd package && zip -r ../deployment.zip .
```

---

## Getting Help

- **Documentation**: See [API.md](API.md) for detailed API reference
- **Examples**: Check `examples/` directory
- **Issues**: Open issue on GitHub
- **Email**: dfeen87@gmail.com

---

## Next Steps

1. **Try Examples**: Run example scripts in `examples/` directory
2. **Read Chemistry**: Review [CHEMISTRY.md](CHEMISTRY.md) for formulation details
3. **Run Benchmarks**: Test performance with `pytest tests/test_benchmarks.py`
4. **Customize**: Create your own mission configurations
5. **Contribute**: See CONTRIBUTING.md for guidelines

---

**Version**: 0.1.0  
**Last Updated**: 2025  
**Maintainer**: Don Michael Feeney Jr
