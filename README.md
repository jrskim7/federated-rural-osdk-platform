# Federated Rural OSDK Platform

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

**Maintainer:** John Roy Ballossini Dommett (JRBD) / Conscious Circle  
**Started:** February 2026  
**Reference case:** Monchique, Portugal (Montalma)

---

## What is this?

A federated territorial intelligence environment for rural planning, land governance, and agroforestry systems design. It connects formal systems engineering, authoritative geospatial data, qualitative causal reasoning, social network analysis, system dynamics, and agroforestry design into one interoperable platform.

Designed as a consulting tool for [Conscious Circle](https://consciouscircle.io) rural development engagements, and as a portfolio project for systems engineering certification (INCOSE ASEP) and academic application (MDEF, Fab Lab Barcelona 2027).

---

## Module overview

| Module | Status | Description |
|--------|--------|-------------|
| `gis/` | Live | Global cadastral registry (45 countries), fetch scripts, QGIS/ArcGIS integration |
| `mbse/` | Live | Capella MBSE exports, GeoJSON bridge, federated model outputs |
| `agroforestry/` | v1.1 | Syntropic design module — species database, guild compositions, BOM/MEL, stratification geometry, Quadriga integration |
| `sna/` | Live | Social network analysis, Kumu exports, actor-network topology |
| `sd/` | Live | System dynamics integration, scenario scripts |
| `qsem/` | Live | Qualitative systems/causal loop integration |
| `orchestrator/` | Live | n8n workflows, webhook bridges, Docker Compose |
| `docs/` | Live | Architecture brief, integration guides, ArcGIS/QGIS setup |
| `analysis/` | v1.0 | Monchique fragmentation analysis notebook |

---

## Agroforestry module highlights

The `agroforestry/` module provides:
- **species_database.json** — 40+ Mediterranean species with DEXi scores (Nature Plants 2024 / Zenodo:3460431), production traits, guild partners, slope zone placement, drought/frost tolerance
- **Syntropic triangle geometry** — formalised spatial design grammar: above-ground stacking triangle, below-ground root diamond, plan view crown projection, and Monchique terrace cross-section with Quadriga mechanisation constraints
- **BOM_template.csv** — phased Bill of Materials for 36 species across a 5-phase installation sequence
- **Permaculture design as MBSE activity sequence** — Bill Mollison's methodology converted to formal SE phases
- **Propagation taxonomy** — vegetative and seed methods mapped to Montalma species inventory
- Reference case: south-facing 30-40 degree terraces, Monte da Foia, Monchique (USDA Zone 10a-10b)

---

## Shared master schema

All modules share a common data schema:
- **Places/spatial units** — municipality, parcel, corridor, zone, intervention area
- **Actors/institutions** — landowner, cooperative, municipality, NGO, regulator
- **Assets/infrastructure** — buildings, water points, berms, access routes
- **System variables** — fire risk, biomass, governance capacity, fragmentation pressure
- **Interventions/processes** — parcel aggregation, berm corridors, clearing regimes
- **Relationships** — contains, adjacent_to, owned_by, influences, collaborates_with

---

## GIS module quick start (Portugal)

```bash
cd ~/Documents/GitHub/federated-rural-osdk-platform
source .venv/bin/activate

# Query the global cadastral registry
python gis/query_cadastre_registry.py --country PT

# Fetch Monchique cadastral parcels (open, CC-BY 4.0)
python gis/fetch_cadastro.py \
  --country PT \
  --bbox "-8.65,37.20,-8.45,37.38" \
  --output mbse/exports/monchique_cadastro_predial.geojson
```

---

## License

This work is licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.

You are free to use, adapt, and build on this work — including commercially — provided you:
1. Give credit: *"Federated Rural OSDK Platform — JRBD / Conscious Circle. github.com/jrskim7/federated-rural-osdk-platform"*
2. Share any adaptations under the same CC-BY-SA 4.0 license

See [LICENSE](./LICENSE) for full terms and third-party data acknowledgements.

---

## Key references

- LIFE AgroForAdapt (LIFE20 CCA/ES/001682) — agroforadapt.eu
- Nature Plants 2024 DEXi study — Zenodo:3460431
- Ernst Gotsch syntropic agroforestry — agendagotsch.com
- DGT OGC API (Portugal cadastre) — ogcapi.dgterritorio.gov.pt
- Danyadara syntropic project (Andalusia) — danyadara.com
- Iberian Agroforestry Pioneer Network — resilience-blog.com (EFI/LIFE)
