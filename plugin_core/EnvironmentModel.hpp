#ifndef ENVIRONMENT_MODEL_HPP
#define ENVIRONMENT_MODEL_HPP

#include <string>
#include <map>
#include "SprayFormulation.hpp" // For PluginMetadata

namespace LunarSimulation {

class EnvironmentModel {
public:
    virtual ~EnvironmentModel() = default;

    // Interface methods required by specification
    virtual double temperature_profile(double time_of_day_hours) const = 0;
    virtual double dust_density() const = 0;
    virtual double vacuum_pressure() const = 0;
    virtual double solar_radiation_factor(double time_of_day_hours) const = 0;
    virtual double microgravity_modifier() const = 0;

    // Plugin identification
    virtual PluginMetadata get_metadata() const = 0;
};

} // namespace LunarSimulation

#endif // ENVIRONMENT_MODEL_HPP
