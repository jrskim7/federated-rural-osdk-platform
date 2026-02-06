# Import Federated OSDK Model to ArcGIS Online

This guide walks you through importing your data schema as a Feature Layer into ArcGIS Online.

## What We're Doing

Converting your ontology-mapped GeoJSON (with MBSE block IDs, SNA node IDs, and properties) into an ArcGIS Online Feature Layer.

## Files Created

### 1. **GeoJSON Schema** (`mbse/exports/monchique_federated_model.geojson`)
- 6 feature objects representing Monchique case study
- Structured with your MBSE-GIS-SNA data schema:
  - **mbseBlockId**: Link back to Capella MBSE blocks (e.g., `BLK_MUN_001`, `BLK_PROJ_ENER_042`)
  - **snaNodeId**: Social Network Analysis node identifiers (e.g., `Node_Municipality_Monchique`)
  - **Properties**: Sector, level, status, numeric indicators (population, area, budget, etc.)
- Includes entities: Municipality, Projects, Cooperatives, Civil Society, Public Entities, Ecological Zones

### 2. **Import Script** (`scripts/import_to_arcgis.py`)
- Python 3 script using ArcGIS API for Python
- Loads GeoJSON and publishes to your ArcGIS Online organization
- Configurable feature layer name and metadata

## Prerequisites

### Install ArcGIS API for Python
```bash
pip install arcgis pandas python-dotenv
```

### Ensure .env is Configured
Your `.env` file (in `orchestrator/`) must have:
```
ARCGIS_USERNAME=your_arcgis_online_username
ARCGIS_PASSWORD=your_arcgis_online_password
ARCGIS_ORG_URL=https://www.arcgis.com  # Or your Enterprise URL
```

## Step 1: Prepare Your Data

### Option A: Use the Sample Monchique Model (Recommended for Testing)
The `monchique_federated_model.geojson` file is pre-populated with:
- Municipality (Monchique)
- Micro-hydro project site
- Goat cooperative (Algarve)
- Ecological zones (Eucalyptus)
- Public & civil society entities

This demonstrates the full schema structure.

### Option B: Create Your Own GeoJSON

Use this template structure:
```json
{
  "type": "Feature",
  "id": "UniqueFeatID",
  "geometry": {
    "type": "Point|Polygon|LineString",
    "coordinates": [lon, lat]  // WGS84
  },
  "properties": {
    "name": "Feature Name",
    "type": "EntityType",
    "level": "Municipal|District|National",
    "sector": "Public|Private|Civil Society|Environment",
    "mbseBlockId": "BLK_XXX_NNN",        // Link to Capella
    "snaNodeId": "Node_Name_ID",        // Link to SNA
    "status": "active|inactive|planning",
    // Add any domain-specific properties
  }
}
```

**Key Properties:**
- `mbseBlockId`: Ensures traceability to your Capella MBSE model
- `snaNodeId`: Enables relationship mapping to SNA (actors, partnerships, influence)
- `type`: Categorizes entity for filtering (Municipality, Project, Cooperative, etc.)
- `sector`: Filters by governance/ownership (Public, Private, Civil Society, Environment)
- `status`: Track lifecycle (planning, active, completed, inactive)

## Step 2: Import to ArcGIS Online

### Run the Import Script

From the repository root:
```bash
cd /Users/jrbd/Documents/GitHub/federated-rural-osdk-platform
python scripts/import_to_arcgis.py
```

**Output:**
```
🔐 Authenticating with ArcGIS Online...
✅ Authenticated as [your_username]
📂 Loading GeoJSON: mbse/exports/monchique_federated_model.geojson
📊 Loaded 6 features
🔄 Publishing Feature Layer from GeoJSON...
✅ Feature Layer published: Monchique Federated OSDK Model
📍 Item ID: a1b2c3d4e5f6g7h8i9j0k1l2
🔗 URL: https://www.arcgis.com/home/item.html?id=a1b2c3d4e5f6g7h8i9j0k1l2

✨ Feature Layer successfully published to ArcGIS Online!
```

## Step 3: Configure Feature Layer in ArcGIS Online

### 1. Open the Feature Layer
Click the URL output by the script or search for "Monchique Federated OSDK Model" in your ArcGIS Online content.

### 2. Configure Fields
- **Display Field**: Set to `name` for feature labels
- **Visible Fields**: Hide internal IDs if desired (keep mbseBlockId, snaNodeId visible for traceability)
- **Aliases**: Rename to user-friendly labels

### 3. Set Up Relationships
- Use `mbseBlockId` to link queries back to Capella MBSE model
- Use `snaNodeId` to enable SNA cross-platform analysis
- Create relates in ArcGIS for data lineage tracking

### 4. Symbology
- Color by `sector` (Public=Blue, Private=Red, Civil Society=Green, Environment=Brown)
- Size by numeric indicators (population, budget, area, etc.)
- Icon by `type` (Municipality=Pentagon, Project=Star, Cooperative=Circle)

### 5. Sharing & Collaboration
- Share with your project team or organization
- Set permissions (View, Edit, Admin)
- Document source data: "Source: Federated OSDK Model (Capella + SNA + SD + QSEM)"

## Step 4: Enable Bidirectional Sync

### Option A: Periodic Updates (CSV/GeoJSON)
Whenever your Capella model changes:
1. Export MBSE → GeoJSON (via `mbse_bridge.py`)
2. Re-run import script
3. ArcGIS Online layer updated

### Option B: Real-Time Sync (n8n Workflow)
Add a step to your n8n workflow (Workflow 003/004):
- After converter creates GeoJSON
- Call `import_to_arcgis.py` or use ArcGIS Python API node
- Feature Layer automatically stays in sync with MBSE

## Mapping Reference

Your GeoJSON `properties` directly map to the MBSE-GIS-SNA ontology:

| GeoJSON Property | MBSE Block | SNA Node | Purpose |
|---|---|---|---|
| `mbseBlockId` | Block ID (e.g., BLK_MUN_001) | — | Traceability to Capella MBSE model |
| `snaNodeId` | — | Node ID (e.g., Node_Mun_Camara) | SNA actor/entity reference |
| `type` | Entity type (Municipality, Project, etc.) | Node type | Classification |
| `level` | Hierarchical level (Municipal, District) | — | Governance level |
| `sector` | Sector (Public, Private, Civil Society) | — | Ownership/governance |
| `status` | Status (active, planning) | — | Lifecycle state |
| `name` | Entity name | — | Display label |
| Domain-specific (e.g., `population`, `budget`, `estimatedOutput_kW`) | Parameter values | — | Quantitative indicators |

## Troubleshooting

### "AuthenticationError: Invalid username/password"
- Verify ARCGIS_USERNAME and ARCGIS_PASSWORD in `.env`
- Check ArcGIS Online login at https://www.arcgis.com

### "File not found: monchique_federated_model.geojson"
- Ensure script runs from repository root
- Verify file at: `mbse/exports/monchique_federated_model.geojson`

### "Feature Layer published but fields are blank"
- GeoJSON may have geometry type mismatch (mixed Point/Polygon)
- Solution: Create separate layers per geometry type or use MultiGeometry

### "Properties not showing in ArcGIS Online"
- Check field names match exactly (case-sensitive)
- Some field names may be reserved (ID, globalID, Shape)
- Rename if needed and re-upload

## Next Steps

1. ✅ Import schema GeoJSON to ArcGIS Online
2. ✅ Verify 6 features and properties visible
3. 🔄 **NEXT:** Configure ModelBuilder geoprocessing (watershed analysis, fire risk, suitability)
4. 🔄 Integrate n8n workflow to auto-sync on MBSE changes
5. 🔄 Set up SNA layer (actors, partnerships, influence flows)
6. 🔄 Link System Dynamics stocks/flows to spatial features

## References

- [ArcGIS Python API Docs](https://developers.arcgis.com/python/)
- [GeoJSON Specification](https://tools.ietf.org/html/rfc7946)
- [Your MBSE-GIS-SNA Ontology](../docs/MBSE_GIS_SNA_ONTOLOGY.md)
