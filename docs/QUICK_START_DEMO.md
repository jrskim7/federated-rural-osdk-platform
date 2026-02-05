# Quick Start: Run the Complete Federated Workflow Demo

## One-Command Demo (Shows Full Workflow)

```bash
cd /Users/jrbd/Documents/GitHub/federated-rural-osdk-platform
python .venv/bin/python scripts/demo_federated_workflow.py
```

**Output**: Full 8-step workflow walkthrough with generated test files

---

## Manual Full Workflow (With Real ArcGIS Data)

### Step 1️⃣ : Create & Verify Schema
```bash
# The schema is already created
cat mbse/exports/monchique_federated_model.geojson
```
✅ 6 features with MBSE-GIS-SNA mappings

---

### Step 2️⃣ : Upload to ArcGIS Online
```bash
python .venv/bin/python scripts/import_to_arcgis.py
```
✅ Output: CSV uploaded to your ArcGIS Online account

**Next**: Visit https://ccgisonline.maps.arcgis.com/home
- Find "Monchique Federated OSDK Model" (CSV item)
- Click **"Visualize"** → **"Publish as Feature Layer"**

---

### Step 3️⃣ : Enable Participatory Editing
In ArcGIS Online Feature Layer:
1. Click **Share** → select collaborators
2. Set role to **"Editor"** (allows edits)
3. Enable **"Track changes"** if available

---

### Step 4️⃣ : Community Edits Feature Layer
In ArcGIS Online, community members edit features:

**Example edits:**
- **EucalyptusZone_12** (Forest): 
  - fireRiskIndex: 0.75 → 0.65 (recent rains)
  - Add note: "Community validated on 2026-02-05"

- **Project_MicroHydro_Alpha**:
  - suitabilityScore: 0.85 → 0.92 (community approved)
  - communityApproval: "Yes"

---

### Step 5️⃣ : Export Edits Back to GeoJSON
```bash
python .venv/bin/python scripts/export_from_arcgis.py
```

**Output:**
- `monchique_federated_model_edited_TIMESTAMP.geojson`
- `change_summary_TIMESTAMP.json`

✅ Community edits now in GeoJSON format with full audit trail

---

### Step 6️⃣ : Commit to GitHub (Triggers Workflow)
```bash
git add mbse/exports/monchique_federated_model_edited_*.geojson
git add mbse/exports/change_summary_*.json

git commit -m "Participatory edits: Community validates forest & project sites

- Eucalyptus Zone 12: Fire risk (0.75→0.65) - Recent rains analysis
- Micro-Hydro Project: Suitability (0.85→0.92) - Community approved
- Meeting: 2026-02-05, Participants: Municipal Council, Cooperative, Tourism"

git push origin main
```

✅ Webhook automatically triggers n8n Workflow 003

---

### Step 7️⃣ : Watch n8n Pipeline Execute
```bash
# Open n8n in browser
open http://localhost:5678
```

**Workflow 003 should execute:**
1. GitHub webhook received
2. Convert edits to model format
3. Create feature branch: `feature/community-edits-{date}`
4. Commit GeoJSON with metadata
5. ✅ Ready for code review & merge

---

### Step 8️⃣ : Results Feed Back to ArcGIS
Once analysis completes, run:
```bash
python .venv/bin/python scripts/import_to_arcgis.py
```
(or create n8n node to auto-sync results back)

✅ ArcGIS dashboards update with:
- Fire risk scores (QSEM-validated)
- Suitability assessments (SD-optimized)
- Partnership network (SNA-updated)
- Audit trail (complete change history)

---

## Key Scripts Reference

| Script | Purpose | Run |
|--------|---------|-----|
| **demo_federated_workflow.py** | Show full 8-step workflow | `python .venv/bin/python scripts/demo_federated_workflow.py` |
| **import_to_arcgis.py** | Upload GeoJSON to ArcGIS | `python .venv/bin/python scripts/import_to_arcgis.py` |
| **export_from_arcgis.py** | Download edits from ArcGIS | `python .venv/bin/python scripts/export_from_arcgis.py` |

---

## Expected File Structure After Demo

```
mbse/exports/
├── monchique_federated_model.geojson              # Original schema
├── monchique_federated_model_edited_*.geojson     # Community edits
├── change_summary_*.json                          # Change audit trail
├── output_geojson.json                            # Converter output
└── sample_capella_export.json                     # MBSE export
```

---

## What Gets Demonstrated

✅ **Data Schema**: MBSE blocks → GeoJSON with SNA node IDs
✅ **Geospatial Validation**: Community uses familiar ArcGIS interface
✅ **Participatory Edits**: Changes tracked with user/date/note
✅ **Bidirectional Sync**: ArcGIS ↔ GeoJSON ↔ GitHub
✅ **Audit Trail**: Complete change history (who/what/when/why)
✅ **n8n Orchestration**: Automated workflow on GitHub push
✅ **Multi-Tool Integration**: Results feed to QSEM/SD/SNA analysis

---

## Docker Containers (Required)

Ensure n8n and postgres are running:
```bash
cd orchestrator
docker-compose up -d
docker-compose ps
```

Expected output:
```
NAME                STATUS              PORTS
federated-n8n       running (healthy)   0.0.0.0:5678->5678/tcp
federated-postgres  running (healthy)   5432/tcp
federated-mbse-bridge running            0.0.0.0:5000->5000/tcp
```

---

## Environment Setup

Ensure `.env` has ArcGIS credentials:
```
ARCGIS_USERNAME=your_username
ARCGIS_PASSWORD=your_password
ARCGIS_ORG_URL=https://ccgisonline.maps.arcgis.com  # Your org URL
```

---

## Troubleshooting

**"Feature Layer not found"**
- Verify CSV was published as Feature Layer (not just table)
- Check layer name: "Monchique Federated OSDK Model"

**"export_from_arcgis.py returns empty"**
- Ensure feature layer has Edit permissions enabled
- Verify credentials in `.env`

**"n8n webhook not triggered"**
- Check GitHub Action is enabled
- Verify webhook URL: `http://<ngrok-url>/webhook/mbse-change`

**"Missing dependencies"**
- `python .venv/bin/python -m pip install arcgis requests`

---

## Next: Production Hardening

Once demo works, implement:

1. **Real-time sync** (webhook from ArcGIS → auto-export)
2. **QSEM integration** (causal loop validation)
3. **System Dynamics** (hydrology + grazing models)
4. **SNA analysis** (partnership network updates)
5. **ArcGIS Experience Builder** (unified dashboards)
6. **Role-based access** (who can edit what)
7. **Conflict resolution** (simultaneous edits)

See [FEDERATED_WORKFLOW.md](../docs/FEDERATED_WORKFLOW.md) for complete roadmap.
