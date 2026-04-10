#include "LunarEquatorialDay.hpp"
#include <cmath>
#include <algorithm>

namespace LunarSimulation {

LunarEquatorialDay::LunarEquatorialDay() {}

double LunarEquatorialDay::temperature_profile(double time_of_day_hours) const {
    // Peak temperature at midday (12.0), reaching ~390K
    return 390.0 * std::sin((time_of_day_hours / 24.0) * M_PI);
}

double LunarEquatorialDay::dust_density() const {
    return 0.3; // Moderate dust, typical for exposed flatlands
}

double LunarEquatorialDay::vacuum_pressure() const {
    return 3e-10; // Nominal daytime exosphere pressure
}

double LunarEquatorialDay::solar_radiation_factor(double time_of_day_hours) const {
    // Max radiation at noon
    return std::max(0.0, std::sin((time_of_day_hours / 24.0) * M_PI));
}

double LunarEquatorialDay::microgravity_modifier() const {
    return 1.0; // Standard lunar gravity
}

PluginMetadata LunarEquatorialDay::get_metadata() const {
    return {
        "LunarEquatorialDay",
        "1.0.0",
        "Standard environment model for lunar equatorial regions during sunlight.",
        "LunarSimulationTeam",
        {{"type", "hot_vacuum"}, {"sunlight", "high"}}
    };
}

bool LunarEquatorialDay::register_plugin() {
    return true;
}

static bool is_registered = LunarEquatorialDay::register_plugin();

} // namespace LunarSimulation
