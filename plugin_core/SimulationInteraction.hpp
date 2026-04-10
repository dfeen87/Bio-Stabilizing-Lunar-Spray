#ifndef SIMULATION_INTERACTION_HPP
#define SIMULATION_INTERACTION_HPP

#include <string>
#include <algorithm>
#include <memory>
#include "SprayFormulation.hpp"
#include "EnvironmentModel.hpp"

namespace LunarSimulation {

struct SimulationResult {
    double reaction_intensity;
    double adhesion_score;
    double stability_rating;
    double environmental_penalty;
    std::string narrative_summary;
};

class SimulationInteraction {
public:
    SimulationInteraction(std::shared_ptr<SprayFormulation> spray,
                          std::shared_ptr<EnvironmentModel> environment)
        : m_spray(spray), m_environment(environment) {}

    SimulationResult run_interaction(double time_seconds, double time_of_day_hours) const {
        SimulationResult result;

        // Fetch environmental parameters
        double temp = m_environment->temperature_profile(time_of_day_hours);
        double dust = m_environment->dust_density();
        double pressure = m_environment->vacuum_pressure();

        // Calculate spray behavior in this environment
        result.reaction_intensity = m_spray->compute_reaction_curve(time_seconds, temp);
        result.adhesion_score = m_spray->adhesion_strength(dust) * m_spray->dust_binding_efficiency();

        double thermal_score = m_spray->thermal_stability(temp);
        double vacuum_score = 1.0 - m_spray->volatility_under_vacuum(pressure);

        result.stability_rating = (thermal_score + vacuum_score) / 2.0;

        // Compute an environmental penalty if conditions are hostile
        result.environmental_penalty = 0.0;
        if (temp > 350.0) result.environmental_penalty += 0.2;
        if (temp < 100.0) result.environmental_penalty += 0.2;
        if (dust > 0.7) result.environmental_penalty += 0.1;

        // Apply penalty to final stability
        result.stability_rating = std::max(0.0, result.stability_rating - result.environmental_penalty);

        // Generate narrative
        result.narrative_summary = "Simulated interaction between " +
                                   m_spray->get_metadata().name + " and " +
                                   m_environment->get_metadata().name + ". " +
                                   "Reaction Intensity: " + std::to_string(result.reaction_intensity) +
                                   ", Adhesion: " + std::to_string(result.adhesion_score) +
                                   ", Stability: " + std::to_string(result.stability_rating);

        return result;
    }

private:
    std::shared_ptr<SprayFormulation> m_spray;
    std::shared_ptr<EnvironmentModel> m_environment;
};

} // namespace LunarSimulation

#endif // SIMULATION_INTERACTION_HPP
