#include "CryoReactiveMist.hpp"
#include <cmath>

namespace LunarSimulation {

CryoReactiveMist::CryoReactiveMist() {}

double CryoReactiveMist::compute_reaction_curve(double time_seconds, double temperature_k) const {
    // Specifically formulated to react instantly in ultra-cold conditions
    double thermal_factor = (temperature_k < 150.0) ? 2.0 : 0.1;
    return 1.0 - std::exp(-thermal_factor * time_seconds / 10.0);
}

double CryoReactiveMist::adhesion_strength(double dust_density) const {
    // High adhesion even in deep dust
    return 0.85;
}

double CryoReactiveMist::dust_binding_efficiency() const {
    return 0.99; // Ultra-fine mist captures 99% of dust particles
}

double CryoReactiveMist::thermal_stability(double temperature_k) const {
    // Highly unstable if heated
    if (temperature_k > 200.0) return 0.1;
    return 0.95;
}

double CryoReactiveMist::volatility_under_vacuum(double pressure_pa) const {
    // Highly volatile if pressure increases even slightly
    if (pressure_pa > 1e-4) return 0.8;
    return 0.05;
}

PluginMetadata CryoReactiveMist::get_metadata() const {
    return {
        "CryoReactiveMist",
        "1.0.0",
        "An advanced cold-welding mist formulated for permanently shadowed regions.",
        "LunarSimulationTeam",
        {{"type", "exothermic_cryo_binder"}, {"cure_time", "instant"}}
    };
}

bool CryoReactiveMist::register_plugin() {
    return true;
}

static bool is_registered = CryoReactiveMist::register_plugin();

} // namespace LunarSimulation
