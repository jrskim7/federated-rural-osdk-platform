# Capella Project Setup for Monchique OSDK

This guide walks through creating the Capella MBSE model that matches your federated GeoJSON schema.

## Prerequisites

- ✅ Eclipse Capella installed (download: https://www.eclipse.org/capella/)
- 📂 This repository cloned locally
- 🔧 Python environment configured (.venv)

## Step 1: Create New Capella Project

### In Capella IDE:

1. **Launch Capella**
   - Open Eclipse Capella application

2. **Create Project**
   - File → New → Capella Project
   - Project name: `MonchiqueRuralOSDK`
   - Click "Finish"

3. **Set Workspace Location**
   - Recommended: Create in `mbse/capella/` directory
   - Full path: `/Users/jrbd/Documents/GitHub/federated-rural-osdk-platform/mbse/capella/MonchiqueRuralOSDK`

## Step 2: Create System Architecture

### Operational Analysis Layer

1. **Right-click** on "Operational Analysis" → New → Operational Entity
2. Create entities matching your GeoJSON features:

#### Entity 1: Municipality
- Name: `Municipality Monchique`
- ID: `BLK_MUN_001` (custom property)
- Properties:
  - `population: Integer = 8500`
  - `area_ha: Real = 45000`
  - `gdp_euros: Real = 125000000`
  - `governanceScore: Real = 0.72`
  - `jurisdiction: String = "Algarve"`

#### Entity 2: Energy Project Site
- Name: `MicroHydro Dam Site Alpha`
- ID: `BLK_PROJ_ENER_042`
- Properties:
  - `estimatedOutput_kW: Real = 50`
  - `minHeadHeight_m: Real = 15`
  - `requiredFlowRate_m3s: Real = 0.5`
  - `suitabilityScore: Real = 0.85`
  - `estimatedCost_euros: Real = 75000`

#### Entity 3: Private Entity (Cooperative)
- Name: `Algarve Goat Cooperative`
- ID: `BLK_ENT_PVT_001`
- Properties:
  - `memberCount: Integer = 45`
  - `managementCapacity: Real = 0.8`
  - `revenue_euros: Real = 180000`
  - `grazingIntensity: Real = 0.5`

#### Entity 4: Ecological Zone
- Name: `Eucalyptus Monoculture Zone 12`
- ID: `BLK_ECO_ZONE_12`
- Properties:
  - `biomassStock_tons: Real = 1000`
  - `area_ha: Real = 50`
  - `fireRiskIndex: Real = 0.75`
  - `grazableArea_ha: Real = 35`

#### Entity 5: Public Entity
- Name: `Monchique Municipal Council`
- ID: `BLK_ENT_PUB_001`
- Properties:
  - `budget_euros: Real = 2500000`
  - `governmentLevel: String = "Local"`

#### Entity 6: Civil Society Entity
- Name: `Monchique Tourism Collective`
- ID: `BLK_ENT_CSO_001`
- Properties:
  - `memberCount: Integer = 23`
  - `budget_euros: Real = 45000`

### Add Custom Properties (MBSE-GIS Traceability)

For **each entity**, add these custom properties:

1. Right-click entity → Properties
2. Go to "Applied Property Values" tab
3. Add:
   - `mbseBlockId: String` (unique identifier)
   - `snaNodeId: String` (for Social Network Analysis)
   - `type: String` (Municipality, Energy.ProjectSite, etc.)
   - `level: String` (Municipal, District, National)
   - `sector: String` (Public, Private, Civil Society, Environment)
   - `status: String` (active, planning, completed)

## Step 3: Create Relationships

### Partnerships (between entities)

Create **Operational Entity Exchanges** to represent partnerships:

1. **Cooperative ↔ Municipal Council**
   - Type: Collaboration
   - Weight: 1.1

2. **Cooperative ↔ Tourism Collective**
   - Type: Partnership
   - Weight: 1.1

3. **Municipal Council ↔ Tourism Collective**
   - Type: Coordination
   - Weight: 1.1

## Step 4: Add Functional Blocks (System Analysis)

Create functional blocks for system dynamics modeling:

### Block 1: Biomass Management System
- Inputs:
  - Grazing Intensity
  - Fire Risk
- Outputs:
  - Biomass Stock
  - Carbon Sequestration
- Parameters:
  - Growth Rate: 0.04
  - Grazing Impact: 0.03

### Block 2: Water Availability System
- Inputs:
  - Rainfall Index
  - Required Flow Rate
- Outputs:
  - Water Availability
  - Suitability Score
- Parameters:
  - Governance Score
  - Community Support

### Block 3: Fire Risk System
- Inputs:
  - Biomass Stock
  - Tourism Pressure
  - Governance Capacity
- Outputs:
  - Fire Risk Index
- Parameters:
  - Management Capacity
  - Grazing Pressure

## Step 5: Export to JSON

### Using Capella JSON Exporter:

1. **Install JSON Export Add-on** (if not already installed)
   - Help → Install New Software
   - Search for "JSON Exporter" or use M2Doc/Python API

2. **Export Model**
   - Right-click on project → Export → JSON
   - Or use Python API (see script below)

3. **Export Location**
   - Target: `mbse/exports/capella_export.json`

### Alternative: Use Python API

Save this script as `mbse/scripts/export_capella_to_json.py`:

```python
#!/usr/bin/env python3
"""
Export Capella model to JSON using Python API
Requires: Python4Capella installed in Capella
"""

# This runs inside Capella's Python console
# Tools → Python → Python Console

import json
from simplified_api.capella import *

def export_to_json(output_path):
    model = get_model()
    
    entities = []
    for entity in model.get_operational_entities():
        entity_data = {
            "id": entity.get_id(),
            "name": entity.get_name(),
            "type": "OperationalEntity",
            "properties": {}
        }
        
        # Extract properties
        for prop in entity.get_owned_properties():
            entity_data["properties"][prop.get_name()] = {
                "type": prop.get_type().get_name() if prop.get_type() else "String",
                "value": prop.get_value()
            }
        
        entities.append(entity_data)
    
    output = {
        "model": model.get_name(),
        "exported": datetime.utcnow().isoformat(),
        "entities": entities
    }
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"Exported {len(entities)} entities to {output_path}")

# Run export
export_to_json("/Users/jrbd/Documents/GitHub/federated-rural-osdk-platform/mbse/exports/capella_export.json")
```

## Step 6: Integrate with Workflow

Once exported, run the converter:

```bash
cd /Users/jrbd/Documents/GitHub/federated-rural-osdk-platform

# Convert Capella JSON to GeoJSON
python scripts/capella_to_geojson.py \
  --input mbse/exports/capella_export.json \
  --output mbse/exports/monchique_federated_model.geojson
```

## Step 7: Validate Export

Check that the GeoJSON contains all required properties:

```bash
# Verify schema
python scripts/validate_geojson.py mbse/exports/monchique_federated_model.geojson
```

Expected output:
- ✅ 6 features (Municipality, Project, 3 Entities, 1 Zone)
- ✅ All features have `mbseBlockId`
- ✅ All features have `snaNodeId`
- ✅ All features have geometry (Point or Polygon)

## Capella Project Structure (Expected)

```
mbse/capella/MonchiqueRuralOSDK/
├── MonchiqueRuralOSDK.aird          # Main project file
├── MonchiqueRuralOSDK.capella       # Model data
├── MonchiqueRuralOSDK.afm           # Architecture framework
└── fragments/                        # Model fragments (if used)
```

## Tips for Capella Modeling

### 1. Use Layers Correctly
- **Operational Analysis**: Entities, activities, processes
- **System Analysis**: Functional blocks, exchanges, scenarios
- **Logical Architecture**: Components, interfaces
- **Physical Architecture**: Nodes, deployment

### 2. Maintain Traceability
- Always set `mbseBlockId` custom property
- Use consistent naming (matches GeoJSON `id`)
- Document relationships

### 3. Properties Best Practices
- Use typed properties (Integer, Real, Boolean, String)
- Set default values where applicable
- Add descriptions for complex properties

### 4. Versioning
- Commit `.aird` and `.capella` files to Git
- Use Git LFS for large model files
- Tag releases matching GeoJSON schema versions

## Add-ons & Plugins (Optional)

### Recommended Capella Add-ons:

1. **Python4Capella**
   - For scripting and automation
   - Download: Capella Marketplace

2. **M2Doc**
   - Generate Word/PDF documentation from model
   - Download: Capella Marketplace

3. **Requirements Viewpoint**
   - Link requirements to blocks
   - Download: Capella Marketplace

4. **Filtering**
   - Filter diagrams by properties
   - Included in Capella

5. **Validation**
   - Check model consistency
   - Included in Capella

### Installing Add-ons:

1. In Capella: Help → Install New Software
2. Select "Capella Update Site" or "Capella Marketplace"
3. Find add-on and click "Install"
4. Restart Capella

## Integration Workflow (Complete Loop)

```
1. Design in Capella (MBSE model)
   ↓
2. Export to JSON (capella_export.json)
   ↓
3. Convert to GeoJSON (capella_to_geojson.py)
   ↓
4. Upload to ArcGIS (import_to_arcgis.py)
   ↓
5. Community edits in ArcGIS Online
   ↓
6. Export edits (export_from_arcgis.py)
   ↓
7. Update Capella model (manual or scripted)
   ↓
8. Iterate (repeat)
```

## Troubleshooting

### "Can't export to JSON"
- **Solution**: Install Python4Capella add-on
- Alternative: Use M2Doc to export to text, then parse

### "Properties not showing in export"
- **Solution**: Ensure properties are on entity, not diagram
- Check: Properties view → "Applied Property Values"

### "IDs don't match GeoJSON"
- **Solution**: Manually set `mbseBlockId` custom property
- Use consistent naming convention

### "Model too large"
- **Solution**: Use model fragments
- Split by subsystems (Energy, Ecology, Governance)

## Next Steps

1. ✅ Create Capella project with 6 entities
2. ✅ Add custom properties (mbseBlockId, snaNodeId, etc.)
3. ✅ Create partnerships (exchanges)
4. ✅ Export to JSON
5. ✅ Convert to GeoJSON
6. ✅ Test full workflow (Capella → GeoJSON → ArcGIS)

## References

- [Capella Tutorial](https://www.eclipse.org/capella/tutorials.html)
- [Python4Capella](https://github.com/eclipse/python4capella)
- [M2Doc Documentation](https://www.m2doc.org/)
- [Your GeoJSON Schema](../mbse/exports/monchique_federated_model.geojson)
