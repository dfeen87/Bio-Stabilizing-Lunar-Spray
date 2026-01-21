# Chemistry Documentation

Detailed chemistry and formulation guide for the Bio-Stabilizing Lunar Spray system.

---

## Table of Contents

- [Overview](#overview)
- [Chemical Formulation](#chemical-formulation)
- [Phase 1: Geopolymerization](#phase-1-geopolymerization)
- [Phase 2: Nutrient Release](#phase-2-nutrient-release)
- [Reaction Mechanisms](#reaction-mechanisms)
- [Material Properties](#material-properties)
- [Safety Information](#safety-information)
- [Quality Control](#quality-control)

---

## Overview

The Bio-Stabilizing Lunar Spray is a **dual-phase chemical system** designed to:

1. **Phase I (0-30 minutes)**: Rapidly harden lunar regolith through geopolymerization
2. **Phase II (15-60 days)**: Gradually transition into a nutrient-rich substrate for plant growth

This document details the chemical composition, reaction mechanisms, and material properties underlying both phases.

---

## Chemical Formulation

### Standard Formulation

The spray consists of a multi-component salt-based geopolymer system:

| Component | Formula | Percentage | Mass (g) | Role |
|-----------|---------|------------|----------|------|
| **Potassium Silicate** | K₂SiO₃ | 60% | 600 | Primary binder + K source |
| **Magnesium Sulfate** | MgSO₄·7H₂O | 20% | 200 | Mg/S nutrients + moisture retention |
| **Calcium Phosphate** | Ca₃(PO₄)₂ | 15% | 150 | P/Ca source + pH buffer |
| **Urea Phosphate** | CO(NH₂)₂·H₃PO₄ | 5% | 50 | Nitrogen delivery |
| **Total Solids** | - | 100% | 1000 | - |

### Additives (Optional)

| Additive | Amount | Purpose |
|----------|--------|---------|
| Citric Acid | 10 g | pH buffering (10 → 9.5) |
| Xanthan Gum | 2 g | Viscosity modifier |
| TiO₂ (nano) | 1 g | UV protection |

### Activation Medium

- **Water**: 5-15% by mass (50-150 mL per 1000g solids)
- **Purpose**: Activates geopolymerization, evaporates in vacuum
- **Quality**: Deionized or distilled preferred

---

## Phase 1: Geopolymerization

### Primary Reaction

Alkali-activated aluminosilicate geopolymerization:

```
K₂SiO₃ + Al₂O₃·2SiO₂ (regolith) → K-Al-Si-O (geopolymer)
```

### Detailed Mechanism

#### Step 1: Dissolution & Depolymerization

```
K₂SiO₃ → 2K⁺ + SiO₃²⁻

SiO₃²⁻ + Si-O-Al (regolith) → dissolved aluminosilicate species
```

**Rate-determining step**: Breaking Si-O-Al bonds in regolith
**Time scale**: 1-5 minutes
**Temperature dependence**: Arrhenius (Ea ≈ 45 kJ/mol)

#### Step 2: Polymerization

```
Dissolved species → [Si-O-Al-O]ₙ (gel formation)
```

**Process**: Condensation of silicate and aluminate species
**Time scale**: 5-10 minutes
**pH**: 10-13 (highly alkaline)

#### Step 3: Hardening

```
Gel → 3D geopolymer network + water evaporation (vacuum)
```

**Bond formation**: Si-O-Si and Si-O-Al-O linkages
**Bond strength**: 3.5-5.0 MPa
**Cure time**: 8-14 minutes (temperature-dependent)

### Supporting Reactions

#### Magnesium Cross-linking

```
MgSO₄ → Mg²⁺ + SO₄²⁻

Mg²⁺ + 2(Si-OH) → (Si-O)₂Mg
```

**Effect**: Creates ionic cross-links between polymer chains
**Contribution**: +0.5 MPa additional strength

#### Calcium-Silicate Formation

```
Ca₃(PO₄)₂ + H₂O → Ca²⁺ + HPO₄²⁻ + OH⁻

Ca²⁺ + Si-O⁻ → Ca-O-Si (C-S-H phases)
```

**Effect**: Hydraulic setting (slower)
**Contribution**: +0.3-0.8 MPa over 24 hours

### Kinetic Parameters

| Parameter | Value | Units | Notes |
|-----------|-------|-------|-------|
| Activation Energy | 45 | kJ/mol | Arrhenius |
| Pre-exponential Factor | 2.1×10⁶ | min⁻¹ | Rate constant |
| Reaction Order | ~1.5 | - | Pseudo-order |
| pH Range | 10-13 | - | Alkaline |
| Max Bond Strength | 3.5 | MPa | At full cure |

### Temperature Effects

**Cure Time Equation:**
```
t_cure = t_base × exp(Ea/R × (1/T - 1/T_ref))
```

Where:
- t_base = 14 minutes (at 0°C)
- Ea = 45,000 J/mol
- R = 8.314 J/(mol·K)
- T_ref = 273.15 K (0°C)

**Examples:**
- -20°C: ~18 minutes
- 0°C: ~14 minutes
- 20°C: ~11 minutes
- 40°C: ~8 minutes

### UV Acceleration

UV-assisted formulation includes photocatalyst (optional TiO₂):
- **Mechanism**: UV energy accelerates condensation reactions
- **Effect**: 30% reduction in cure time
- **Wavelength**: 200-400 nm (UV-A, UV-B, UV-C)

---

## Phase 2: Nutrient Release

### Transition Timeline

The geopolymer matrix gradually breaks down through hydrolysis and plant-mediated processes, releasing bioavailable nutrients:

| Days | Process | Nutrients Released |
|------|---------|-------------------|
| 0-15 | Initial hardening, pH drop begins | Minimal |
| 15-30 | Geopolymer hydrolysis starts | K⁺, Mg²⁺ |
| 30-45 | Active breakdown, root exudates | K⁺, Mg²⁺, PO₄³⁻, N |
| 45-60 | Sustained release, pH neutral | All nutrients |

### Nutrient Release Mechanisms

#### Potassium Release

```
K-Al-Si-O + H₂O + CO₂ → K⁺(aq) + Al-Si gel
```

**Kinetics**: Sigmoid (delayed release)
```
[K⁺] = K_max / (1 + exp(-k(t - t₀)))
```
- K_max = 2000 ppm
- k = 0.15 day⁻¹
- t₀ = 20 days

**Mechanism**: 
1. Water infiltration into geopolymer pores
2. CO₂ from plant respiration forms carbonic acid
3. Acid catalyzes K-O bond hydrolysis
4. K⁺ ions become mobile and bioavailable

#### Nitrogen Release

```
CO(NH₂)₂ + H₂O → 2NH₃ + CO₂

NH₃ + H₂O → NH₄⁺ + OH⁻

2NH₄⁺ + 3O₂ → 2NO₃⁻ + 4H⁺ + 2H₂O (nitrification)
```

**Kinetics**: Biphasic (fast then slow)
- **Fast phase** (0-20 days): 40 ppm/day
- **Slow phase** (20+ days): 17.5 ppm/day
- **Total yield**: ~1500 ppm

**Mechanism**:
1. Urea phosphate hydrolyzes readily in water
2. Forms ammonium ions
3. Nitrifying bacteria convert NH₄⁺ → NO₃⁻
4. Both forms are plant-available

#### Phosphorus Release

```
Ca₃(PO₄)₂ + organic acids → Ca²⁺ + H₂PO₄⁻
```

**Kinetics**: Delayed sigmoid (requires root exudates)
```
[P] = P_max / (1 + exp(-k(t - t₀)))
```
- P_max = 300 ppm
- k = 0.1 day⁻¹
- t₀ = 30 days

**Mechanism**:
1. Plant roots secrete organic acids (citric, malic)
2. Acids chelate Ca²⁺, dissolving Ca₃(PO₄)₂
3. Releases H₂PO₄⁻ into solution
4. Additional P from urea phosphate (fast-release)

#### Magnesium & Sulfur Release

```
MgSO₄·7H₂O → Mg²⁺(aq) + SO₄²⁻(aq) + 7H₂O
```

**Kinetics**: Linear (highly soluble)
```
[Mg²⁺] = min(rate × (t - t_start), Mg_max)
```
- rate = 12 ppm/day
- t_start = 10 days
- Mg_max = 500 ppm

**Mechanism**:
1. Direct dissolution in hydroponic mist
2. Mg²⁺ for chlorophyll synthesis
3. SO₄²⁻ for amino acids and proteins

### pH Evolution

**Initial**: pH 10-11 (alkaline from K-silicate)
**Final**: pH 6.5-7.0 (neutral)

```
pH(t) = pH_final + (pH_initial - pH_final) × exp(-k × t)
```
- pH_initial = 10.0
- pH_final = 6.5
- k = 0.08 day⁻¹

**Buffering agents**:
- Citric acid: immediate pH reduction
- CO₂ absorption: gradual neutralization
- Phosphate buffers: pH stabilization

---

## Reaction Mechanisms

### Geopolymer Formation (Detailed)

#### Molecular Structure

Geopolymers form a three-dimensional aluminosilicate framework:

```
[-Si-O-Al-O-Si-O-]ₙ with K⁺ charge-balancing cations
         |
         O⁻···K⁺
```

**Key features**:
- Amorphous to semi-crystalline structure
- Pore sizes: 1-100 nm
- Surface area: 10-50 m²/g
- Charge-balancing by K⁺ ions

#### Bond Energies

| Bond Type | Energy (kJ/mol) | Abundance |
|-----------|----------------|-----------|
| Si-O-Si | 452 | High |
| Si-O-Al | 427 | Medium |
| Al-O-Al | 395 | Low |
| K-O (ionic) | 238 | High |

**Implications**:
- Strong covalent Si-O bonds provide structural integrity
- Weaker K-O bonds allow later potassium release
- Controlled breakdown through hydrolysis

### Nutrient Bioavailability

#### Forms and Plant Uptake

| Nutrient | Released Form | Plant-Available Form | Uptake Mechanism |
|----------|---------------|---------------------|------------------|
| Nitrogen | NH₄⁺, NO₃⁻ | NH₄⁺, NO₃⁻ | Active transport |
| Phosphorus | H₂PO₄⁻, HPO₄²⁻ | H₂PO₄⁻ | Co-transport with H⁺ |
| Potassium | K⁺ | K⁺ | Ion channels |
| Magnesium | Mg²⁺ | Mg²⁺ | Active transport |
| Sulfur | SO₄²⁻ | SO₄²⁻ | Active transport |
| Calcium | Ca²⁺ | Ca²⁺ | Ion channels |

---

## Material Properties

### Physical Properties

| Property | Value | Units | Method |
|----------|-------|-------|--------|
| **Uncured Spray** |
| Density | 1.18 | g/cm³ | Pycnometry |
| Viscosity | 2000-5000 | cP | Rheometry |
| pH | 9.5-10.5 | - | pH meter |
| Solid content | 85-90 | % | Gravimetric |
| **Cured Surface** |
| Density | 1.5-1.8 | g/cm³ | Archimedes |
| Compressive strength | 3.5-5.0 | MPa | Compression test |
| Porosity (initial) | 15-20 | % | Mercury porosimetry |
| Porosity (final) | 40-45 | % | After 60 days |
| Thermal conductivity | 0.3-0.5 | W/(m·K) | Hot wire method |
| Thermal expansion | 8-12 | 10⁻⁶/K | Dilatometry |

### Chemical Composition (by element)

| Element | Initial (%) | After 60 days (%) | Fate |
|---------|-------------|------------------|------|
| Silicon (Si) | 22 | 20 | Retained in matrix |
| Aluminum (Al) | 8 | 8 | Retained in matrix |
| Potassium (K) | 19 | 5 | Released to plants |
| Magnesium (Mg) | 3 | 0.5 | Released to plants |
| Calcium (Ca) | 7 | 5 | Partially released |
| Phosphorus (P) | 2 | 0.5 | Released to plants |
| Nitrogen (N) | 1 | 0.1 | Released to plants |
| Sulfur (S) | 3 | 0.8 | Released to plants |
| Oxygen (O) | 35 | 35 | Structural |

---

## Safety Information

### Hazard Classification

#### Potassium Silicate (K₂SiO₃)

- **GHS**: Corrosive (Category 1A)
- **Hazards**: 
  - Causes severe skin burns and eye damage
  - May cause respiratory irritation
- **pH**: 11-13 (highly alkaline)
- **PPE Required**: Chemical-resistant gloves, goggles, lab coat

#### Magnesium Sulfate (MgSO₄·7H₂O)

- **GHS**: Not classified as hazardous
- **Hazards**: Minimal (eye/skin irritant at high concentrations)
- **pH**: 6-8 (neutral)
- **PPE Required**: Safety glasses, gloves (optional)

#### Calcium Phosphate (Ca₃(PO₄)₂)

- **GHS**: Not classified as hazardous
- **Hazards**: Dust may cause mechanical irritation
- **PPE Required**: Dust mask, safety glasses

#### Urea Phosphate

- **GHS**: Not classified as hazardous
- **Hazards**: Mild eye/skin irritant
- **pH**: 6-7 (neutral)
- **PPE Required**: Safety glasses, gloves

### Handling Procedures

#### Mixing Protocol Safety

1. **Work in ventilated area** (fume hood recommended)
2. **Wear appropriate PPE** at all times
3. **Add K-silicate to water** (never reverse - exothermic)
4. **Keep citric acid available** for neutralization
5. **Avoid skin/eye contact** with alkaline solution
6. **Wash thoroughly** after handling

#### First Aid

**Skin Contact:**
- Immediately flush with water for 15 minutes
- Remove contaminated clothing
- Seek medical attention if irritation persists

**Eye Contact:**
- Immediately flush with water for 15 minutes
- Hold eyelids open during flushing
- Seek immediate medical attention

**Ingestion:**
- Do NOT induce vomiting
- Rinse mouth with water
- Seek immediate medical attention

**Inhalation:**
- Move to fresh air
- If breathing is difficult, give oxygen
- Seek medical attention

### Storage

- **Temperature**: 15-30°C
- **Container**: Chemical-resistant (HDPE, glass)
- **Shelf life**: 6 months (unmixed), 48 hours (mixed)
- **Keep away from**: Strong acids, oxidizers
- **Label clearly**: Contents, date, hazards

### Disposal

- **Small amounts**: Neutralize with dilute acid (pH 6-8), flush with water
- **Large amounts**: Contact waste disposal service
- **Containers**: Triple rinse before disposal
- **Comply with**: Local regulations

---

## Quality Control

### Critical Parameters

| Parameter | Specification | Test Method | Frequency |
|-----------|---------------|-------------|-----------|
| pH (mixed) | 9.5-10.5 | pH meter | Every batch |
| Viscosity | 2000-5000 cP | Rheometer | Every batch |
| Cure time (0°C) | 12-16 min | Gelation test | Weekly |
| Bond strength | >3.0 MPa | Compression | Weekly |
| Solid content | 85-90% | Gravimetric | Every batch |
| K₂SiO₃ purity | >98% | Titration | Per shipment |

### Quality Assurance Tests

#### Cure Time Test

```
1. Mix 100g spray according to protocol
2. Apply 10mL to JSC-1A simulant at 0°C
3. Monitor gelation with needle penetration
4. Record time to 90% cure (target: 14±2 min)
```

#### Bond Strength Test

```
1. Prepare 50mm diameter × 100mm cylinder
2. Cure for 24 hours at 20°C
3. Test compression strength (ASTM C39)
4. Target: >3.5 MPa
```

#### Nutrient Release Test

```
1. Mix spray and cure on regolith
2. Place in hydroponic mist chamber
3. Sample solution weekly for 8 weeks
4. Analyze by ICP-OES or ion chromatography
5. Verify release profiles match specification
```

### Batch Documentation

Each batch should be documented with:
- Batch number and date
- Raw material lot numbers
- Mixing protocol followed
- QC test results
- Operator initials
- Storage location

---

## References

### Scientific Basis

1. **Davidovits, J.** (2008). *Geopolymer Chemistry and Applications*. Institut Géopolymère.

2. **Provis, J.L. & van Deventer, J.S.J.** (2014). *Alkali Activated Materials*. Springer.

3. **NASA Technical Memorandum 2017-219454**: Geopolymer Concrete for Lunar Construction

4. **NASA Technical Paper 2020-220346**: JSC-1A Lunar Regolith Simulant

5. **Feeney, D.M. Jr.** (2025). *Bio-Stabilizing Lunar Spray: A Dual-Purpose Surface and Agricultural Solution*. White Paper.

### Standards

- ASTM C39: Compressive Strength of Cylindrical Concrete Specimens
- ASTM C348: Flexural Strength of Hydraulic-Cement Mortars
- ISO 14688: Geotechnical Investigation and Testing
- NASA-STD-6001: Flammability, Offgassing, and Compatibility Requirements

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: Don Michael Feeney Jr  
**Review Date**: Annual
