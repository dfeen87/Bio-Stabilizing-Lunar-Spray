# Plugin Architecture

**Version**: 1.7.0
**Context**: Bio-Stabilizing Lunar Spray Fictional Simulation

## Overview
The Bio-Stabilizing Lunar Spray repository has been extended to support a highly modular, plug-and-play architecture for scientific simulation. To increase realism, expressive behavior, and extensibility without modifying core code, we introduce two complementary plugin systems:
1. **Spray Formulation Plugins**
2. **Environmental Model Plugins**

These systems interact through a central **Interaction Layer**, allowing complex emergent behavior based on the combined traits of the spray chemistry and the hostile lunar environment.

*(Note: This project is a fictional lunar-chemistry simulation environment. All additions must increase realism and modularity, but nothing should be interpreted as real scientific or engineering guidance.)*

---

## 1. Spray Formulation Plugins

Spray Formulation plugins define the chemical and physical characteristics of the binding agent when applied to lunar regolith.

### Interface
All spray formulations must implement the `SprayFormulation` interface defined in `plugin_core/SprayFormulation.hpp`.

Key methods to implement:
- `compute_reaction_curve(time_seconds, temperature_k)`: Determines how quickly and intensely the spray reacts under specific thermal conditions.
- `adhesion_strength(dust_density)`: Calculates the bonding strength based on local dust conditions.
- `dust_binding_efficiency()`: A scalar representing how effectively the formulation traps loose particulates.
- `thermal_stability(temperature_k)`: Evaluates the formulation's resilience against degradation at specific temperatures.
- `volatility_under_vacuum(pressure_pa)`: Models the outgassing or evaporation rate in a hard vacuum.
- `get_metadata()`: Returns a `PluginMetadata` struct for identification.

### Example: Creating a New Formulation
To create a new formulation, create a class inheriting from `SprayFormulation`:

```cpp
#include "plugin_core/SprayFormulation.hpp"

class MyLunarBinder : public LunarSimulation::SprayFormulation {
    // Implement virtual methods...
};
```
Place your implementation in the `spray_plugins/` directory.

---

## 2. Environmental Model Plugins

Environmental Model plugins define the localized conditions of specific lunar topographies or mission scenarios.

### Interface
All environment models must implement the `EnvironmentModel` interface defined in `plugin_core/EnvironmentModel.hpp`.

Key methods to implement:
- `temperature_profile(time_of_day_hours)`: Returns the local temperature (in Kelvin) based on the time of day.
- `dust_density()`: Returns the localized ambient dust concentration.
- `vacuum_pressure()`: Returns the local exospheric pressure (in Pascals).
- `solar_radiation_factor(time_of_day_hours)`: Returns the intensity of solar radiation.
- `microgravity_modifier()`: Accounts for local gravitational anomalies (base is 1.0 for standard lunar gravity).
- `get_metadata()`: Returns a `PluginMetadata` struct for identification.

### Example: Creating a New Environment
To create a new environment, create a class inheriting from `EnvironmentModel`:

```cpp
#include "plugin_core/EnvironmentModel.hpp"

class MyCraterEnvironment : public LunarSimulation::EnvironmentModel {
    // Implement virtual methods...
};
```
Place your implementation in the `environment_plugins/` directory.

---

## 3. The Interaction Layer

The true power of this architecture lies in the **Interaction Layer** (`plugin_core/SimulationInteraction.hpp`), which combines a `SprayFormulation` and an `EnvironmentModel`.

### Mechanism
The `SimulationInteraction` class takes a shared pointer to a spray and an environment. When `run_interaction(time_seconds, time_of_day_hours)` is called:
1. It polls the environment for current conditions (temperature, dust, pressure).
2. It feeds these conditions into the spray formulation to calculate dynamic responses.
3. It computes aggregated scores and applies environmental penalties.

### Outputs
The result is a `SimulationResult` struct containing:
- `reaction_intensity`: The calculated speed/strength of the chemical reaction.
- `adhesion_score`: The final binding capability.
- `stability_rating`: The long-term viability of the cured matrix.
- `environmental_penalty`: Deductions applied due to extreme heat, cold, or dust.
- `narrative_summary`: A human-readable description of the emergent simulation behavior.

---

## 4. Plugin Registration

Plugins utilize a static self-registration pattern. By defining a static boolean that calls a registration function within your `.cpp` file, the plugin automatically makes itself known to the central registry when the shared library or executable is loaded.

```cpp
// Inside MyLunarBinder.cpp
bool MyLunarBinder::register_plugin() {
    // Factory registration logic...
    return true;
}
static bool is_registered = MyLunarBinder::register_plugin();
```

---

## 5. Extending the System Safely

- **Do not modify `plugin_core` interfaces** unless absolutely necessary, as it will break backward compatibility with existing plugins.
- **Maintain Additive Changes**: Ensure new plugins reside in `spray_plugins/` or `environment_plugins/` and do not alter existing simulation logic.
- **Adhere to the Narrative**: When creating metadata and defining behavior, maintain the creative, scientific-simulation flavor of the project.
