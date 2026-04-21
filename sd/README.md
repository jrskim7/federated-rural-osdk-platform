# SD Module — System Dynamics

Quantitative simulation layer of the Federated Rural OSDK Platform.

## Relationship to QSEM/CLD

```
Field Data → CLD (qsem/) → SD Model (sd/) → Simulation Output → GIS Alignment → Report
```

The QSEM module produces qualitative causal structure (polarities, feedback loops).
This module operationalises that structure as stocks, flows, and rates.

## Directory Structure

```
sd/
├── models/
│   └── monchique_rural.py      # Native Python stock-flow model (9 CLD links)
├── analysis/
│   └── sensitivity.py          # OAT sweep + scenario comparison
├── data/
│   ├── sd_skeleton.json         # Auto-generated from CLD via cld_to_sd.py
│   ├── initial_conditions.json  # Stock initial values
│   └── parameters.json          # Exogenous parameters
├── calibration/                 # (future: fit.py for pysd calibration)
├── tests/                       # (future: validate against SDXorg/test-models)
└── output/
    └── sd_report_*.json         # Per-run reports
```

## Running

### Single-step (legacy, backward-compatible)
```bash
python scripts/sd_integration.py
```

### Multi-step with scenario
```bash
python scripts/sd_integration.py --scenario intervention --run-length 30
```

### Generate CLD→SD skeleton
```bash
python scripts/cld_to_sd.py
```

### Sensitivity analysis
```bash
python sd/analysis/sensitivity.py --run-length 50 --sweep-steps 11
```

### Run model directly
```bash
python sd/models/monchique_rural.py baseline
python sd/models/monchique_rural.py intervention
python sd/models/monchique_rural.py pessimistic
```

## Scenarios

| Scenario | Description |
|----------|-------------|
| `baseline` | CLD initial values from qsem/exports/cld_network.json |
| `intervention` | Improved governance (0.90), halved grazing intensity, higher budget |
| `pessimistic` | Low governance (0.40), high grazing + tourism, reduced revenue |

## pysd Integration (Phase 1 — roadmap)

Once a `.mdl` or `.xmile` file exists:
```python
import pysd
model = pysd.read_vensim("sd/models/monchique_rural.mdl")
results = model.run(params={"Grazing_Intensity": 0.3})
```

The `MonchiqueModel` in `sd/models/monchique_rural.py` has a compatible
`model.run()` → DataFrame interface to allow drop-in replacement.

Install pysd:
```bash
pip install pysd
```

## Integration Points

| Module | How SD connects |
|--------|----------------|
| `qsem/` | CLD JSON seeds model parameters via `cld_to_sd.py` |
| `gis/` | `sd_aligned.geojson` spatially joins SD outputs to parcels |
| `mbse/` | `monchique_federated_model_sd_*.geojson` embeds SD in federated model |
| `sna/` | Future: network centrality feeds governance/connectivity parameters |
| `scripts/sd_integration.py` | Orchestration entry point — runs model + updates GeoJSON |
