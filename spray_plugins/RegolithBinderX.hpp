#ifndef REGOLITH_BINDER_X_HPP
#define REGOLITH_BINDER_X_HPP

#include "../plugin_core/SprayFormulation.hpp"

namespace LunarSimulation {

class RegolithBinderX : public SprayFormulation {
public:
    RegolithBinderX();
    virtual ~RegolithBinderX() = default;

    double compute_reaction_curve(double time_seconds, double temperature_k) const override;
    double adhesion_strength(double dust_density) const override;
    double dust_binding_efficiency() const override;
    double thermal_stability(double temperature_k) const override;
    double volatility_under_vacuum(double pressure_pa) const override;

    PluginMetadata get_metadata() const override;

    // Self-registration
    static bool register_plugin();
};

} // namespace LunarSimulation

#endif // REGOLITH_BINDER_X_HPP
