#include "RegolithBinderX.hpp"
#include <cmath>
#include <algorithm>
#include <iostream>

namespace LunarSimulation {

RegolithBinderX::RegolithBinderX() {
}

double RegolithBinderX::compute_reaction_curve(double time_seconds, double temperature_k) const {
    // Fictional model: Reaction speed increases with temperature, plateaus over time
    double base_rate = 0.05 * (temperature_k / 273.15);
    return 1.0 - std::exp(-base_rate * time_seconds / 60.0);
}

double RegolithBinderX::adhesion_strength(double dust_density) const {
    // Binds well with moderate dust density, drops off if too dusty
    if (dust_density < 0.5) return 0.9;
    return 0.9 * std::exp(-(dust_density - 0.5));
}

double RegolithBinderX::dust_binding_efficiency() const {
    return 0.95; // 95% efficient under ideal conditions
}

double RegolithBinderX::thermal_stability(double temperature_k) const {
    // Highly stable up to 400K, then degrades
    if (temperature_k < 400.0) return 1.0;
    return std::max(0.0, 1.0 - (temperature_k - 400.0) / 100.0);
}

double RegolithBinderX::volatility_under_vacuum(double pressure_pa) const {
    // Low volatility, safely usable in near-vacuum
    return 0.01 + (pressure_pa * 1e-6);
}

PluginMetadata RegolithBinderX::get_metadata() const {
    return {
        "RegolithBinderX",
        "1.0.0",
        "Standard geopolymer matrix optimized for equatorial regolith binding.",
        "LunarSimulationTeam",
        {{"type", "alkali_activated_silicate"}, {"cure_time", "moderate"}}
    };
}

// Dummy registration mechanism (in a real system this would register with a central factory)
bool RegolithBinderX::register_plugin() {
    // Registration logic would go here
    return true;
}

// Global static variable to trigger self-registration at load time
static bool is_registered = RegolithBinderX::register_plugin();

} // namespace LunarSimulation
