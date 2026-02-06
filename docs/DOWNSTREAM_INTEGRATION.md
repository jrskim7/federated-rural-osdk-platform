# Downstream Analysis Integration: Complete Guide

This document summarizes the complete integration of System Dynamics (SD), QSEM Causal Loop Diagrams (CLD), and ArcGIS Experience Builder dashboards into the federated workflow.

## Overview

The federated OSDK platform now includes three major downstream analysis tools:

1. **System Dynamics** - Stock/flow updates for ecological and project features
2. **QSEM** - Causal loop diagrams for policy testing and impact analysis
3. **Experience Builder** - Unified dashboards for visualization and stakeholder engagement

## Architecture

```
GeoJSON Input
    ↓
SNA Integration → Network Graph → Kumu (JSON)
    ↓
SD Integration → Stock/Flow Updates → GeoJSON Properties + Report
    ↓
QSEM Integration → Causal Loops → CLD JSON + Summary
    ↓
ArcGIS Experience Builder Dashboard
    ├─ Spatial Map (with SD overlays)
    ├─ Network Diagram (SNA Kumu)
    ├─ System Dynamics Table
    ├─ Causal Loop Diagram (QSEM)
    └─ Audit Trail (Changes)
```

## Workflow Steps

### Step 1: Community Editing (ArcGIS Online)
- Community members edit features in ArcGIS Feature Layer
- Changes tracked with timestamps, editor info, notes
- Edits captured in GeoJSON

### Step 2: Export from ArcGIS
```bash
python scripts/export_from_arcgis.py
# Output: GeoJSON with edits + change_summary.json
```

### Step 3: Run SNA Analysis
```bash
python scripts/sna_integration.py
# Output: 
#   - sna/output/sna_nodes.csv
#   - sna/output/sna_edges.csv
#   - sna/output/kumu_network_TIMESTAMP.json
# Update canonical: sna/exports/kumu_network.json
```

Then push to GitHub (Kumu auto-refreshes from remote URL)

### Step 4: Run System Dynamics
```bash
python scripts/sd_integration.py --rainfall-index 0.65
# Output:
#   - mbse/exports/monchique_federated_model_sd_TIMESTAMP.geojson
#   - sd/output/sd_report_TIMESTAMP.json
```

The updated GeoJSON has new properties:
- sd_biomassStock_tons
- sd_fireRiskIndex
- sd_grazingCapacity_tons
- sd_waterAvailability_m3s
- sd_suitabilityScore

### Step 5: Run QSEM Analysis
```bash
python scripts/qsem_cld_integration.py
# Output:
#   - qsem/output/cld_network_TIMESTAMP.json
#   - qsem/exports/cld_network.json (canonical)
#   - qsem/output/cld_summary_TIMESTAMP.md
```

The CLD shows causal relationships:
- Grazing → Biomass (-)
- Biomass → Fire Risk (+)
- Governance → Fire Risk (-)
- Fire Risk → Suitability (-)
- And more...

### Step 6: Update ArcGIS with Results
```bash
# Option A: Manual via ArcGIS Online UI
# - Open Feature Layer
# - Update fields with sd_* values
# - Save

# Option B: Re-import via script
python scripts/import_to_arcgis.py --input mbse/exports/monchique_federated_model_sd_TIMESTAMP.geojson
```

### Step 7: View in Experience Builder Dashboard
1. Go to https://ccgisonline.maps.arcgis.com
2. Open "Monchique OSDK Dashboard" Experience
3. View tabs:
   - **Spatial Map**: Fire risk heatmap, suitability zones
   - **Network**: Partnership graph from Kumu
   - **System Dynamics**: Biomass, grazing, water, suitability tables
   - **Causal Loops**: QSEM CLD with factors and links
   - **Audit Trail**: Edit history with who/what/when
4. Interact: Click features → see SD & CLD details

## Integration with n8n

Create n8n Workflow 006 to automate the entire pipeline:

**Workflow: "GeoJSON → SD → QSEM → ArcGIS"**

1. **Trigger**: GitHub Push (mbse/exports/*)
2. **Node 1**: Checkout repository
3. **Node 2**: Execute SNA integration
   - Command: `python scripts/sna_integration.py`
4. **Node 3**: Commit & push SNA outputs to GitHub
5. **Node 4**: Execute SD integration
   - Command: `python scripts/sd_integration.py --rainfall-index 0.6`
6. **Node 5**: Execute QSEM CLD integration
   - Command: `python scripts/qsem_cld_integration.py`
7. **Node 6**: Commit results to GitHub
8. **Node 7**: Upload updated GeoJSON to ArcGIS Online
   - Method: REST API or Python script
9. **Node 8**: Send notification to stakeholders
   - Email: "Analysis complete. View results in dashboard"

## Files Reference

### System Dynamics
- Script: [scripts/sd_integration.py](../scripts/sd_integration.py)
- Docs: [docs/SYSTEM_DYNAMICS_INTEGRATION.md](SYSTEM_DYNAMICS_INTEGRATION.md)
- Outputs:
  - `mbse/exports/monchique_federated_model_sd_<timestamp>.geojson`
  - `sd/output/sd_report_<timestamp>.json`

### QSEM
- Script: [scripts/qsem_cld_integration.py](../scripts/qsem_cld_integration.py)
- Docs: [docs/QSEM_CLD_INTEGRATION.md](QSEM_CLD_INTEGRATION.md)
- Outputs:
  - `qsem/output/cld_network_<timestamp>.json`
  - `qsem/exports/cld_network.json` (canonical)
  - `qsem/output/cld_summary_<timestamp>.md`

### ArcGIS Experience Builder
- Docs: [docs/ARCGIS_EXPERIENCE_BUILDER.md](ARCGIS_EXPERIENCE_BUILDER.md)
- Dashboard: "Monchique OSDK Dashboard"
- Data layers:
  - Feature Layer (Monchique Federated OSDK Model)
  - SD results (overlaid on Feature Layer or separate)
  - Audit trail table

### Social Network Analysis
- Script: [scripts/sna_integration.py](../scripts/sna_integration.py)
- Remote URL: [sna/exports/kumu_network.json](../sna/exports/kumu_network.json)
- Docs: [docs/KUMU_REMOTE_LINK.md](KUMU_REMOTE_LINK.md)

## Data Flow Summary

```
Community Edit in ArcGIS
    ↓
export_from_arcgis.py
    ↓
GeoJSON + change_summary.json
    ↓
sna_integration.py + sna_export_kumu.py
    ↓
Kumu JSON (pushed to GitHub remote)
    ↓
sd_integration.py
    ↓
GeoJSON with sd_* properties + SD report
    ↓
qsem_cld_integration.py
    ↓
CLD JSON + Summary
    ↓
import_to_arcgis.py (optional, to update Feature Layer)
    ↓
ArcGIS Experience Builder Dashboard
    ↓
Stakeholder Decision-Making & Feedback
```

## Parameterization

### System Dynamics
Key parameters in `sd_integration.py`:

- `--rainfall-index` (0-1): Affects water availability estimate
  - Default: 0.6 (moderate rainfall)
  - Range: 0.0 (drought) to 1.0 (heavy rainfall)

These can be adjusted based on:
- Seasonal variations
- Climate change scenarios
- Community input on expected conditions

### QSEM
The CLD factors and links are currently **heuristic-based**. To calibrate:

1. Conduct expert interviews (domain scientists)
2. Gather community feedback on causal relationships
3. Update factor extraction logic in `qsem_cld_integration.py`
4. Add loop detection and classification (reinforcing vs balancing)

### ArcGIS
Configure display based on:
- Fire risk thresholds (red if > 0.7, yellow if > 0.4)
- Suitability grades (green if > 0.8, orange if > 0.5)
- Ecosystem health colors

## Customization

To adapt for different regions/projects:

1. **Update GeoJSON schema** (`mbse/exports/`)
   - Add region-specific properties
   - Adjust coordinate system if needed

2. **Modify SD model** (`scripts/sd_integration.py`)
   - Replace heuristics with calibrated model
   - Add time-stepping for temporal analysis
   - Include stochastic components

3. **Extend CLD** (`scripts/qsem_cld_integration.py`)
   - Add more factors from your model
   - Refine causal relationships
   - Test for feedback loops

4. **Create region-specific Experience Builder**
   - Adapt symbology to local context
   - Add regional maps/overlays
   - Customize popups & legends

## Known Limitations

1. **SD Model**
   - Currently uses heuristic updates
   - Needs calibration with real hydrological/ecological data
   - Time-stepping is implicit (single update per run)

2. **QSEM CLD**
   - Factors extracted from GeoJSON properties only
   - Links are static (don't adjust based on data)
   - No loop detection or classification

3. **Experience Builder**
   - Manual dashboard creation (no auto-generation)
   - Kumu embed requires public project
   - CLD display requires URL or embed (not auto-generated in ArcGIS)

## Next Steps

### Immediate
- [ ] Create Kumu projects for SNA network
- [ ] Create Kumu project for QSEM CLD
- [ ] Set up ArcGIS Experience Builder dashboard
- [ ] Link SNA and CLD to Experience Builder
- [ ] Test full workflow end-to-end

### Short-term
- [ ] Integrate n8n Workflow 006 (full pipeline)
- [ ] Add temporal analysis (time-series)
- [ ] Create "what-if" scenario explorer
- [ ] Add stakeholder notification step

### Medium-term
- [ ] Calibrate SD model with real data
- [ ] Validate CLD with expert elicitation
- [ ] Implement loop detection (reinforcing/balancing)
- [ ] Create optimization runner (find best policy)

### Long-term
- [ ] Machine learning for CLD inference
- [ ] Real-time updates (streaming GeoJSON)
- [ ] Multi-objective optimization (economy vs environment)
- [ ] Mobile app for field validation

## Support & References

- [System Dynamics Integration](SYSTEM_DYNAMICS_INTEGRATION.md)
- [QSEM CLD Integration](QSEM_CLD_INTEGRATION.md)
- [ArcGIS Experience Builder](ARCGIS_EXPERIENCE_BUILDER.md)
- [Kumu Remote Link Setup](KUMU_REMOTE_LINK.md)
- [SNA Integration](SNA_INTEGRATION.md)

For questions or issues, refer to the [Federated Workflow Guide](FEDERATED_WORKFLOW.md).
