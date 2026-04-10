# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2025-04-12

### Added
- **Plugin Architecture**: Added a new modular, C++-based plugin system for expanding the simulation capabilities without altering core logic.
  - **Spray Formulation Plugins**: Interface for defining new binding agents (e.g., `RegolithBinderX`, `CryoReactiveMist`).
  - **Environment Model Plugins**: Interface for defining new lunar topographic/environmental conditions (e.g., `LunarEquatorialDay`, `ShadedCraterFloor`).
  - **Interaction Layer**: A `SimulationInteraction` class that combines a formulation and an environment to compute emergent behaviors (reaction intensity, adhesion, stability, and environmental penalties).
- **Documentation**: Added `docs/plugin_architecture.md` detailing how to create, register, and safely extend the new plugin systems.
