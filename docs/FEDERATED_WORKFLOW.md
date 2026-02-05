# Federated OSDK Platform: End-to-End Workflow Guide

## Overview

This document describes the **complete federated workflow** for the Rural OSDK platform, demonstrating how participatory GIS editing integrates with MBSE, System Dynamics, QSEM, and SNA analysis.

## The Complete Federated Loop

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. MBSE EXPORT (Capella)                                            │
│    └─ Eclipse Capella SysML model → JSON export                     │
└─────────────────────┬───────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. SCHEMA MAPPING (Ontology)                                        │
│    └─ Convert MBSE blocks → GeoJSON features with:                  │
│       • mbseBlockId (links to Capella)                              │
│       • snaNodeId (links to Social Network)                         │
│       • Properties: type, level, sector, status, metrics            │
└─────────────────────┬───────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. ARCGIS UPLOAD (Geospatial Validation)                            │
│    └─ GeoJSON → CSV → ArcGIS Online Feature Layer                   │
│       • Spatial reference system (WGS84)                            │
│       • Rich properties for filtering/symbology                     │
│       • Shared with community stakeholders                          │
└─────────────────────┬───────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. PARTICIPATORY EDITING (Community Validation)                     │
│    └─ ArcGIS Online: Community members edit & validate:             │
│       • Forest stand locations (community knowledge)                │
│       • Fire risk assessments (local observations)                  │
│       • Project suitability (stakeholder approval)                  │
│       • Changes tracked: who, when, what, why                       │
└─────────────────────┬───────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. EXPORT FROM ARCGIS (Bidirectional Sync)                          │
│    └─ Feature Layer → GeoJSON + Change Metadata                     │
│       • Timestamps for each edit                                    │
│       • Editor information (user, role)                             │
│       • Change descriptions (validation notes)                      │
│       • Audit trail for compliance                                  │
└─────────────────────┬───────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. GITHUB COMMIT (Version Control & Audit Trail)                    │
│    └─ Commit edited GeoJSON + change summary                        │
│       • Branch: feature/community-edits-{date}                      │
│       • Commit message: Details of changes & participants           │
│       • Files: Edited GeoJSON + change_summary.json                 │
│       • Webhook: Automatically triggers n8n orchestration           │
└─────────────────────┬───────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 7. N8N ORCHESTRATION (Multi-Tool Analysis)                          │
│    └─ Workflow 003 (Full Pipeline) executes:                        │
│       • Webhook receives GitHub commit event                        │
│       • Converter: GeoJSON → updated model format                   │
│       • Branch & Commit: Creates PR with analysis-ready data        │
│       • Triggers downstream:                                        │
│         - QSEM: Causal loop analysis (fire risk drivers)            │
│         - System Dynamics: Hydrology + grazing stock/flows          │
│         - SNA: Relationship network updates (trust, influence)      │
│         - ArcGIS ModelBuilder: Recalculate suitability models       │
└─────────────────────┬───────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 8. RESULTS → ARCGIS DASHBOARDS (Feedback Loop)                      │
│    └─ Analysis results update visualization:                        │
│       • Fire Risk Heat Map (QSEM-validated)                         │
│       • Suitability Scores (SD-optimized)                           │
│       • Partnership Network (SNA-updated)                           │
│       • Implementation Timeline (with community milestones)         │
│       • Edit History (audit trail)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Schema: From MBSE to GeoJSON

All features follow the **unified ontological schema**:

```json
{
  "type": "Feature",
  "id": "UniqueFeatID",
  "geometry": { "type": "Point|Polygon", "coordinates": [...] },
  "properties": {
    "name": "Feature Name",
    "type": "EntityType (Municipality, Project, Cooperative, Zone, etc.)",
    "level": "Municipal|District|National",
    "sector": "Public|Private|Civil Society|Environment",
    
    // MBSE Traceability
    "mbseBlockId": "BLK_MUN_001",
    "mbseBlockType": "Entity|Subsystem|Property",
    
    // SNA Traceability
    "snaNodeId": "Node_Municipality_Monchique",
    "snaNodeType": "Actor|Organization|Institution",
    
    // Status & Lifecycle
    "status": "planning|active|completed|inactive",
    
    // Domain-Specific Properties
    "population": 8500,
    "area_ha": 45000,
    "gdp_euros": 125000000,
    "fireRiskIndex": 0.75,
    "suitabilityScore": 0.85,
    
    // Participatory Validation
    "validatedBy": "Community Meeting - Feb 5 2026",
    "validationNotes": "Community consensus on forest management",
    "communityApproval": "Yes",
    
    // Audit Trail
    "_arcgis_export_timestamp": "2026-02-05T16:44:17",
    "_last_edited": "2026-02-05T15:30:00",
    "_editor": "Maria Silva (Municipal Council)"
  }
}
```

## Implementation Roadmap

### ✅ Phase 1: Data Schema & Integration (COMPLETE)
- [x] Design MBSE-GIS-SNA ontology (100+ mappings)
- [x] Create Monchique GeoJSON (6 sample features)
- [x] Upload to ArcGIS Online (CSV → Feature Layer)
- [x] Implement bidirectional sync (export_from_arcgis.py)
- [x] Change tracking & audit trail

### 🔄 Phase 2: Participatory Workflow (IN PROGRESS)
- [ ] **Immediate**: Publish CSV as Feature Layer in ArcGIS Online
  - Go to https://ccgisonline.maps.arcgis.com/home
  - Find "Monchique Federated OSDK Model" (CSV item)
  - Click "Visualize" → "Publish as Feature Layer"
  
- [ ] Enable collaborative editing permissions
  - Share Feature Layer with team
  - Set "Editor" role for community members
  - Enable comments/attachment tracking
  
- [ ] Test bidirectional sync
  ```bash
  python scripts/export_from_arcgis.py
  ```
  
- [ ] Create ArcGIS webhook integration
  - Listen to FeatureLayer.updated events
  - Auto-trigger export_from_arcgis.py on edits
  - Push changes to GitHub via GitHub API

### ⏳ Phase 3: Downstream Analysis Integration
- [ ] QSEM Integration (Causal Loop Validation)
  - Pull fire risk changes from GeoJSON
  - Validate against causal loop models
  - Identify new risk drivers
  
- [ ] System Dynamics Integration
  - Update stock/flow model with community inputs
  - Run hydrology simulation (water availability)
  - Run grazing model (land carrying capacity)
  - Export results as GeoJSON properties
  
- [ ] SNA Integration
  - Extract partnership edits from GeoJSON
  - Update network graph (nodes, edges, weights)
  - Calculate centrality & influence metrics
  - Export as SNA visualization nodes
  
- [ ] ArcGIS Experience Builder
  - Create dashboard with 4 panels:
    1. Spatial map (fire risk heat map, suitability scores)
    2. Network diagram (partnership graph)
    3. Time series (SD model results)
    4. Change log (audit trail)

### 🚀 Phase 4: Production Hardening
- [ ] Webhook signature verification (GitHub + ArcGIS)
- [ ] OIDC integration (community user authentication)
- [ ] Role-based access control (who can edit what)
- [ ] Real-time collaboration notifications
- [ ] Conflict resolution (simultaneous edits)
- [ ] Data validation & constraint checking
- [ ] Performance optimization (large datasets)
- [ ] Monitoring & alerting (failed workflows)

## Quick Start: Testing the Workflow

### 1. Verify Schema
```bash
python scripts/demo_federated_workflow.py
```
Output: Full workflow summary with generated test files

### 2. Upload to ArcGIS
```bash
python scripts/import_to_arcgis.py
```
Output: CSV uploaded to ArcGIS Online

### 3. Publish Feature Layer (Manual, in ArcGIS UI)
- Visit https://ccgisonline.maps.arcgis.com/home
- Find "Monchique Federated OSDK Model" CSV
- Click "Visualize" → "Publish as Feature Layer"
- Configure symbology:
  - Color by sector (Public=Blue, Private=Red, Civil=Green)
  - Size by area_ha
  - Labels by name

### 4. Simulate Community Edits
In ArcGIS Online feature layer:
- Edit EucalyptusZone_12: fireRiskIndex (0.75 → 0.65)
- Edit Project_MicroHydro_Alpha: suitabilityScore (0.85 → 0.92)
- Add validation notes to each

### 5. Export Edits Back
```bash
python scripts/export_from_arcgis.py
```
Output: 
- `monchique_federated_model_edited_TIMESTAMP.geojson` (edits)
- `change_summary_TIMESTAMP.json` (change metadata)

### 6. Commit to GitHub
```bash
git add mbse/exports/monchique_federated_model_edited_*.geojson
git add mbse/exports/change_summary_*.json
git commit -m "Participatory edits: Community validates forest & project sites"
git push origin main
```

### 7. Watch n8n Workflow
- Go to http://localhost:5678 (n8n)
- Watch Workflow 003 execute on webhook
- See branch/commit in GitHub

## Files Reference

| File | Purpose |
|------|---------|
| `mbse/exports/monchique_federated_model.geojson` | Original schema (6 features) |
| `mbse/exports/monchique_federated_model_edited_*.geojson` | Edited version with community feedback |
| `mbse/exports/change_summary_*.json` | Change metadata (who, what, when) |
| `scripts/import_to_arcgis.py` | Upload GeoJSON to ArcGIS Online |
| `scripts/export_from_arcgis.py` | Download edits from ArcGIS |
| `scripts/demo_federated_workflow.py` | Full workflow demonstration |
| `orchestrator/.env` | ArcGIS credentials + config |
| `orchestrator/docker-compose.yml` | n8n + postgres services |
| `orchestrator/n8n/workflows/003-*.json` | n8n full pipeline workflow |

## Key Design Features

### 1. **Ontological Traceability**
- Every GeoJSON feature links back to MBSE block (mbseBlockId)
- Every actor/entity links to SNA node (snaNodeId)
- Properties match unified data schema across all tools

### 2. **Participatory Validation**
- Community members can edit spatial data in ArcGIS (familiar UX)
- Edits automatically tracked with metadata
- No special technical skills required

### 3. **Bidirectional Sync**
- MBSE → GeoJSON → ArcGIS (forward)
- ArcGIS edits → GeoJSON → GitHub (backward)
- Closed-loop feedback system

### 4. **Multi-Tool Orchestration**
- Single edit triggers analysis across 4+ tools (QSEM, SD, SNA, ModelBuilder)
- Results consolidated back into shared GeoJSON/ArcGIS
- Coordinated through n8n workflows

### 5. **Audit Trail & Compliance**
- Every change tracked: user, timestamp, description
- GitHub provides immutable version control
- Change summary JSON documents rationale
- Suitable for government/compliance requirements

## Troubleshooting

### "Feature Layer not found in ArcGIS Online"
- Ensure CSV was published as Feature Layer (not just table)
- Check that feature layer name matches: "Monchique Federated OSDK Model"

### "export_from_arcgis.py returns no features"
- Verify feature layer has edit permissions enabled
- Check feature layer is public or shared with script user account
- Verify ArcGIS credentials in .env are correct

### "n8n workflow not triggered on GitHub push"
- Check GitHub webhook is configured (Settings → Webhooks)
- Verify webhook URL points to n8n: `http://<ngrok-url>/webhook/mbse-change`
- Check GitHub Action is enabled (`.github/workflows/trigger-n8n-on-mbse-change.yml`)

### "Changes not appearing in ArcGIS after commit"
- Re-run `import_to_arcgis.py` to sync GeoJSON back to Feature Layer
- Or set up automated sync (webhook from GitHub → import_to_arcgis.py)

## Future Enhancements

1. **Real-Time Collaboration**
   - WebSocket-based sync (Firebase, Supabase)
   - Simultaneous multi-user editing
   - Conflict resolution for overlapping edits

2. **Advanced QSEM Integration**
   - Causal loop diagrams auto-generated from edits
   - Hypothesis testing on policy changes
   - Sensitivity analysis

3. **System Dynamics Optimization**
   - Optimization runs triggered by suitability score changes
   - Exploration of "what-if" scenarios
   - Results as interactive dashboards

4. **Mobile-Friendly Editing**
   - ArcGIS Field Apps for offline data collection
   - Offline edits sync on reconnect
   - GPS-enabled location validation

5. **Stakeholder Notification**
   - Email/SMS alerts on major edits
   - Community consensus tracking
   - Decision documentation

## References

- [ArcGIS Online Feature Services](https://developers.arcgis.com/rest/services-reference/enterprise/feature-service-overview/)
- [GeoJSON Specification (RFC 7946)](https://tools.ietf.org/html/rfc7946)
- [n8n Workflow Automation](https://n8n.io/)
- [Federated OSDK Schema](../docs/MBSE_GIS_SNA_ONTOLOGY.md)
