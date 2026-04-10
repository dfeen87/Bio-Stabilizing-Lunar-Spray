#include "ShadedCraterFloor.hpp"

namespace LunarSimulation {

ShadedCraterFloor::ShadedCraterFloor() {}

double ShadedCraterFloor::temperature_profile(double time_of_day_hours) const {
    // Constant extreme cold
    return 40.0; // 40 Kelvin
}

double ShadedCraterFloor::dust_density() const {
    // Electrostatic levitation causes high dust density in craters
    return 0.85;
}

double ShadedCraterFloor::vacuum_pressure() const {
    return 1e-10; // Extremely hard vacuum
}

double ShadedCraterFloor::solar_radiation_factor(double time_of_day_hours) const {
    // Permanently shadowed
    return 0.0;
}

double ShadedCraterFloor::microgravity_modifier() const {
    // Deep craters might have tiny local gravity anomalies
    return 1.001;
}

PluginMetadata ShadedCraterFloor::get_metadata() const {
    return {
        "ShadedCraterFloor",
        "1.0.0",
        "Environment model for permanently shadowed polar craters.",
        "LunarSimulationTeam",
        {{"type", "cryo_vacuum"}, {"sunlight", "none"}}
    };
}

bool ShadedCraterFloor::register_plugin() {
    return true;
}

static bool is_registered = ShadedCraterFloor::register_plugin();

} // namespace LunarSimulation
