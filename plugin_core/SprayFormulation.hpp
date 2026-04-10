#ifndef SPRAY_FORMULATION_HPP
#define SPRAY_FORMULATION_HPP

#include <string>
#include <map>
#include <vector>

namespace LunarSimulation {

struct PluginMetadata {
    std::string name;
    std::string version;
    std::string description;
    std::string author;
    std::map<std::string, std::string> properties;
};

class SprayFormulation {
public:
    virtual ~SprayFormulation() = default;

    // Interface methods required by specification
    virtual double compute_reaction_curve(double time_seconds, double temperature_k) const = 0;
    virtual double adhesion_strength(double dust_density) const = 0;
    virtual double dust_binding_efficiency() const = 0;
    virtual double thermal_stability(double temperature_k) const = 0;
    virtual double volatility_under_vacuum(double pressure_pa) const = 0;

    // Plugin identification
    virtual PluginMetadata get_metadata() const = 0;
};

} // namespace LunarSimulation

#endif // SPRAY_FORMULATION_HPP
