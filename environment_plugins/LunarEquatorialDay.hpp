#ifndef LUNAR_EQUATORIAL_DAY_HPP
#define LUNAR_EQUATORIAL_DAY_HPP

#include "../plugin_core/EnvironmentModel.hpp"

namespace LunarSimulation {

class LunarEquatorialDay : public EnvironmentModel {
public:
    LunarEquatorialDay();
    virtual ~LunarEquatorialDay() = default;

    double temperature_profile(double time_of_day_hours) const override;
    double dust_density() const override;
    double vacuum_pressure() const override;
    double solar_radiation_factor(double time_of_day_hours) const override;
    double microgravity_modifier() const override;

    PluginMetadata get_metadata() const override;

    // Self-registration
    static bool register_plugin();
};

} // namespace LunarSimulation

#endif // LUNAR_EQUATORIAL_DAY_HPP
