# System Dynamics (SD) Integration

This guide covers the SD integration workflow for the Federated OSDK platform.

## What This Adds

- Stock/flow updates for ecological zones (biomass, grazing, fire risk)
- Water availability estimate for micro-hydro
- Suitability score update based on SD factors
- Outputs: updated GeoJSON + SD report JSON

## Script

- [scripts/sd_integration.py](scripts/sd_integration.py)

## Run

From repository root:

- python scripts/sd_integration.py

Optional parameters:

- --input mbse/exports/monchique_federated_model.geojson
- --output mbse/exports/monchique_federated_model_sd_<timestamp>.geojson
- --report sd/output/sd_report_<timestamp>.json
- --rainfall-index 0.6

## Output

1) Updated GeoJSON (adds sd_* properties):
- sd_biomassStock_tons
- sd_fireRiskIndex
- sd_grazingCapacity_tons
- sd_waterAvailability_m3s
- sd_suitabilityScore
- sd_timestamp

2) SD report JSON:
- sd/output/sd_report_<timestamp>.json

## How It Works (Model Overview)

- Biomass stock is updated via:
  - growth rate (governance-weighted)
  - grazing pressure (coop intensity, membership)
  - fire risk loss

- Fire risk is adjusted by:
  - grazing pressure and tourism pressure (increase)
  - governance and management capacity (decrease)

- Water availability is estimated by:
  - rainfall index
  - governance score
  - project required flow rate

- Suitability score is updated by:
  - water availability
  - community support index

## Next Steps

- Replace heuristics with calibrated SD model parameters
- Add time-series outputs per feature
- Integrate into n8n workflow after GeoJSON export
