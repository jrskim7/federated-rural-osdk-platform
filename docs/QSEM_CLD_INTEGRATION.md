# QSEM Causal Loop Diagram (CLD) Integration

This guide documents the QSEM CLD integration for the Federated OSDK platform.

## What This Adds

- CLD generation from GeoJSON factors
- Kumu-compatible CLD JSON output
- Summary markdown with factors and causal links

## Script

- [scripts/qsem_cld_integration.py](scripts/qsem_cld_integration.py)

## Run

From repository root:

- python scripts/qsem_cld_integration.py

Optional parameters:

- --input mbse/exports/monchique_federated_model.geojson
- --output qsem/output/cld_network_<timestamp>.json
- --export qsem/exports/cld_network.json
- --summary qsem/output/cld_summary_<timestamp>.md

## Output

1) CLD JSON (Kumu-compatible):
- qsem/output/cld_network_<timestamp>.json
- qsem/exports/cld_network.json (canonical)

2) Summary markdown:
- qsem/output/cld_summary_<timestamp>.md

## CLD Factors (Current Heuristics)

- Biomass Stock
- Fire Risk
- Grazing Intensity
- Management Capacity
- Governance Capacity
- Tourism Pressure
- Water Requirement
- Suitability
- Economic Resilience
- Community Governance

## Example Links

- Grazing Intensity → Biomass Stock (negative)
- Biomass Stock → Fire Risk (positive)
- Governance Capacity → Fire Risk (negative)
- Fire Risk → Suitability (negative)
- Water Requirement → Suitability (negative)
- Economic Resilience → Management Capacity (positive)

## Next Steps

- Calibrate CLD using domain expert feedback
- Add loop detection and balancing/reinforcing tags
- Feed CLD diagnostics into ArcGIS dashboards
