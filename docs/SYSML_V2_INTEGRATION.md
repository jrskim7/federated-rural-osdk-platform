# SysML v2 Integration Guide for OSDK Platform

This guide explains how to leverage the SysML v2 extensions you have installed in VS Code for your entire federated OSDK workflow.

## Installed SysML v2 Extensions

You have access to these powerful extensions:

```vscode-extensions
jamied.sysml-v2-support,sensmetry.syside-editor,ellidiss.sysml-ellidiss
```

### Extension Capabilities:

1. **jamied.sysml-v2-support** (SysML v2.0 Language Support)
   - Complete SysML v2 syntax highlighting
   - Formatting and validation
   - Navigation and code completion
   - Interactive visualizer

2. **sensmetry.syside-editor** (Syside Editor)
   - Professional modeling support
   - SysML v2 and KerML language support
   - Linting and formatting

3. **ellidiss.sysml-ellidiss** (SysML by Ellidiss)
   - Rich textual editing for SysML v2
   - KerML support

---

## How to Use SysML v2 in Your Workflow

### Option 1: SysML v2 as Primary MBSE Tool (Instead of Capella)

If you prefer working entirely in VS Code, you can use SysML v2 **instead of Capella**:

#### Step 1: Create SysML v2 Model Files

Create `.sysml` files in `mbse/sysml/` directory:

**File: `mbse/sysml/monchique_model.sysml`**

```sysml
package MonchiqueRuralOSDK {
    
    // Import standard library
    import ScalarValues::*;
    
    // Define Municipality
    part def Municipality {
        attribute id : String;
        attribute name : String;
        attribute population : Integer;
        attribute area_ha : Real;
        attribute gdp_euros : Real;
        attribute governanceScore : Real;
        attribute jurisdiction : String;
        attribute level : String;
        attribute sector : String;
        attribute status : String;
        
        // GIS Traceability
        attribute mbseBlockId : String;
        attribute snaNodeId : String;
        attribute geometry : String; // GeoJSON geometry
    }
    
    // Instantiate Monchique
    part monchique : Municipality {
        :>> id = "Municipality_Monchique";
        :>> name = "Monchique";
        :>> population = 8500;
        :>> area_ha = 45000.0;
        :>> gdp_euros = 125000000.0;
        :>> governanceScore = 0.72;
        :>> jurisdiction = "Algarve";
        :>> level = "Municipal";
        :>> sector = "Public";
        :>> status = "active";
        :>> mbseBlockId = "BLK_MUN_001";
        :>> snaNodeId = "Node_Municipality_Monchique";
    }
    
    // Define Energy Project
    part def EnergyProject {
        attribute id : String;
        attribute name : String;
        attribute estimatedOutput_kW : Real;
        attribute minHeadHeight_m : Real;
        attribute requiredFlowRate_m3s : Real;
        attribute suitabilityScore : Real;
        attribute estimatedCost_euros : Real;
        attribute level : String;
        attribute sector : String;
        attribute status : String;
        attribute mbseBlockId : String;
        attribute snaNodeId : String;
    }
    
    part microHydroAlpha : EnergyProject {
        :>> id = "Project_MicroHydro_Alpha";
        :>> name = "Micro-Hydro Dam Site Alpha";
        :>> estimatedOutput_kW = 50.0;
        :>> minHeadHeight_m = 15.0;
        :>> requiredFlowRate_m3s = 0.5;
        :>> suitabilityScore = 0.85;
        :>> estimatedCost_euros = 75000.0;
        :>> level = "Municipal";
        :>> sector = "Private";
        :>> status = "Feasibility_Study";
        :>> mbseBlockId = "BLK_PROJ_ENER_042";
        :>> snaNodeId = "Node_Project_MicroHydro_01";
    }
    
    // Define Cooperative
    part def Cooperative {
        attribute id : String;
        attribute name : String;
        attribute memberCount : Integer;
        attribute managementCapacity : Real;
        attribute revenue_euros : Real;
        attribute grazingIntensity : Real;
        attribute level : String;
        attribute sector : String;
        attribute status : String;
        attribute mbseBlockId : String;
        attribute snaNodeId : String;
        attribute partnershipIds : String[*]; // Array of partner IDs
    }
    
    part algarveCooperative : Cooperative {
        :>> id = "Coop_Algarve";
        :>> name = "Algarve Goat Cooperative";
        :>> memberCount = 45;
        :>> managementCapacity = 0.8;
        :>> revenue_euros = 180000.0;
        :>> grazingIntensity = 0.5;
        :>> level = "Municipal";
        :>> sector = "Private";
        :>> status = "active";
        :>> mbseBlockId = "BLK_ENT_PVT_001";
        :>> snaNodeId = "Node_Coop_Algarve";
        :>> partnershipIds = ("Mun_Camara", "Tourism_Group_B");
    }
    
    // Define connections (for SNA)
    connection def Partnership {
        end source : Cooperative;
        end target : Municipality;
        attribute strength : Real;
    }
    
    connection coopToMunicipality : Partnership connect 
        algarveCooperative to monchique {
        :>> strength = 1.1;
    }
}
```

#### Step 2: Create SysML to GeoJSON Converter

**File: `scripts/sysml_to_geojson.py`**

```python
#!/usr/bin/env python3
"""
Convert SysML v2 textual models to GeoJSON.
Uses SysML v2 API Server for parsing.
"""

import argparse
import json
import subprocess
from pathlib import Path

def parse_sysml_file(sysml_path: Path) -> dict:
    """Parse SysML v2 file using Language Server Protocol."""
    # This would use the SysML v2 API/LSP to parse the model
    # For now, use simple text parsing as example
    
    features = []
    current_part = None
    
    with open(sysml_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # Parse part definitions
        if line.startswith('part ') and ':' in line:
            # Extract part instance
            parts = line.split()
            part_name = parts[1].rstrip(':')
            part_type = parts[2] if len(parts) > 2 else 'Part'
            current_part = {
                'id': part_name,
                'type': part_type,
                'properties': {}
            }
        
        # Parse attribute bindings
        elif line.startswith(':>>') and current_part:
            # Extract attribute name and value
            attr_line = line[3:].strip()
            if '=' in attr_line:
                attr_name, attr_value = attr_line.split('=', 1)
                attr_name = attr_name.strip()
                attr_value = attr_value.strip().rstrip(';').strip('"')
                current_part['properties'][attr_name] = attr_value
        
        # End of part definition
        elif line == '}' and current_part:
            # Convert to GeoJSON feature
            feature = convert_to_feature(current_part)
            if feature:
                features.append(feature)
            current_part = None
    
    return {
        'type': 'FeatureCollection',
        'name': 'SysML v2 Model Export',
        'crs': {
            'type': 'name',
            'properties': {'name': 'EPSG:4326'}
        },
        'features': features
    }

def convert_to_feature(part: dict) -> dict:
    """Convert SysML part to GeoJSON feature."""
    props = part['properties']
    
    # Determine geometry (default Point for now)
    geometry = {
        'type': 'Point',
        'coordinates': [-8.0, 37.3]  # Default Monchique location
    }
    
    # Override with actual geometry if specified
    if 'geometry' in props:
        # Parse GeoJSON geometry string
        try:
            geometry = json.loads(props['geometry'])
        except:
            pass
    
    return {
        'type': 'Feature',
        'id': props.get('id', part['id']),
        'geometry': geometry,
        'properties': {
            k: v for k, v in props.items()
            if k != 'geometry'
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='mbse/exports/monchique_federated_model.geojson')
    args = parser.parse_args()
    
    sysml_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"🔄 Converting SysML v2 to GeoJSON...")
    print(f"📂 Input: {sysml_path}")
    
    geojson = parse_sysml_file(sysml_path)
    
    with open(output_path, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"✅ Conversion complete")
    print(f"🗺️  Output: {output_path}")
    print(f"📊 Features: {len(geojson['features'])}")

if __name__ == '__main__':
    main()
```

#### Step 3: Integrate into Workflow

Update your workflow to use SysML v2:

1. **Model in VS Code** (using SysML v2 extensions)
2. **Convert to GeoJSON**: `python scripts/sysml_to_geojson.py --input mbse/sysml/monchique_model.sysml`
3. **Continue existing workflow**: Import to ArcGIS, SNA, SD, QSEM, etc.

---

### Option 2: SysML v2 as Complement to Capella

Use SysML v2 for **specific aspects** while keeping Capella as primary:

#### Use Case 1: Requirements Management

**File: `mbse/sysml/requirements.sysml`**

```sysml
package MonchiqueRequirements {
    
    requirement def SystemRequirement {
        attribute id : String;
        attribute text : String;
        subject stakeholder : Stakeholder;
    }
    
    requirement fireRiskReduction : SystemRequirement {
        :>> id = "REQ-001";
        :>> text = "System shall reduce fire risk by 30% within 5 years";
    }
    
    requirement waterAvailability : SystemRequirement {
        :>> id = "REQ-002";
        :>> text = "Micro-hydro project shall have minimum 0.5 m³/s water flow";
    }
    
    // Link requirements to Capella blocks
    satisfy fireRiskReduction by EucalyptusZone_12;
    satisfy waterAvailability by MicroHydro_Alpha;
}
```

#### Use Case 2: Parametric Analysis

**File: `mbse/sysml/constraints.sysml`**

```sysml
package MonchiqueConstraints {
    
    import ISQ::*;
    
    // Define constraint for fire risk
    constraint def FireRiskModel {
        in biomass : Real;
        in grazingPressure : Real;
        in governanceScore : Real;
        out fireRisk : Real;
        
        fireRisk == 0.5 + 0.3 * (biomass / 1000.0) 
                  - 0.2 * governanceScore 
                  + 0.1 * grazingPressure;
    }
    
    // Define constraint for suitability
    constraint def SuitabilityModel {
        in waterAvailability : Real;
        in communitySupport : Real;
        in fireRisk : Real;
        out suitability : Real;
        
        suitability == 0.4 * waterAvailability 
                     + 0.4 * communitySupport 
                     - 0.2 * fireRisk;
    }
    
    // Apply constraints to parts
    part eucalyptusZone {
        attribute biomass = 1000.0;
        attribute grazingPressure = 0.5;
        attribute governanceScore = 0.72;
        attribute fireRisk : Real;
        
        constraint fireRiskCalc : FireRiskModel {
            in biomass = eucalyptusZone.biomass;
            in grazingPressure = eucalyptusZone.grazingPressure;
            in governanceScore = eucalyptusZone.governanceScore;
            out fireRisk = eucalyptusZone.fireRisk;
        }
    }
}
```

#### Use Case 3: State Machines (for Workflow)

**File: `mbse/sysml/workflows.sysml`**

```sysml
package MonchiqueWorkflows {
    
    state def ProjectLifecycle {
        entry; then planning;
        
        state planning;
        state feasibility;
        state design;
        state implementation;
        state operation;
        
        transition planning_to_feasibility
            first planning
            accept CommunityApprovalEvent
            then feasibility;
        
        transition feasibility_to_design
            first feasibility
            if suitabilityScore > 0.8
            then design;
        
        transition design_to_implementation
            first design
            accept FundingApprovalEvent
            then implementation;
    }
    
    part microHydroProject : EnergyProject {
        attribute lifecycle : ProjectLifecycle;
    }
}
```

---

## Workflow Comparison

### Capella Workflow
```
Capella IDE (Eclipse)
    ↓
Export to JSON (Python4Capella)
    ↓
Convert to GeoJSON (capella_to_geojson.py)
    ↓
Continue federated workflow
```

### SysML v2 Workflow (All in VS Code)
```
Edit .sysml files (VS Code with extensions)
    ↓
Convert to GeoJSON (sysml_to_geojson.py)
    ↓
Continue federated workflow
```

### Hybrid Workflow (Best of Both)
```
Capella: Architecture + Functional Analysis
    ↓
SysML v2: Requirements + Constraints + State Machines
    ↓
Merge to GeoJSON
    ↓
Continue federated workflow
```

---

## Advantages of Each Approach

### Capella Advantages:
- ✅ Mature, industry-proven tool
- ✅ Arcadia method built-in
- ✅ Comprehensive viewpoints
- ✅ Excellent diagram generation
- ✅ Large user community

### SysML v2 Advantages:
- ✅ **All in VS Code** (no context switching)
- ✅ Text-based (Git-friendly, diffable)
- ✅ Programmatic generation easier
- ✅ Modern language features
- ✅ Better integration with your existing workflow
- ✅ Live syntax checking while editing

---

## Recommended Hybrid Approach for Your Project

### Phase 1: Architecture (Use Capella)
- Define operational entities
- Create system blocks
- Model functional exchanges
- Generate architecture diagrams

**Why**: Capella excels at architecture visualization and multi-layer modeling.

### Phase 2: Requirements & Constraints (Use SysML v2)
- Define requirements in `.sysml` files
- Create parametric constraints (fire risk, suitability)
- Link to Capella blocks via IDs
- Track in Git with clear diffs

**Why**: Text-based requirements are easier to manage in version control.

### Phase 3: Behavior (Use SysML v2)
- State machines for project workflows
- Activity diagrams for processes
- Sequence diagrams for interactions

**Why**: SysML v2 has better behavior modeling than Capella's operational analysis.

### Phase 4: Integration (Use Both)
- Export Capella → JSON
- Export SysML v2 → JSON
- Merge both in `scripts/merge_models.py`
- Convert unified model → GeoJSON

---

## Quick Start: SysML v2 in VS Code

### 1. Create Your First SysML v2 File

```bash
mkdir -p mbse/sysml
code mbse/sysml/monchique_model.sysml
```

Start with the example above (Municipality + Energy Project).

### 2. Use Extension Features

- **F2**: Rename symbol (across entire model)
- **Ctrl+Space**: Auto-completion
- **F12**: Go to definition
- **Shift+F12**: Find all references
- **Ctrl+Shift+F**: Format document

### 3. Validate Your Model

The extensions provide real-time validation. Check the Problems panel (Cmd+Shift+M) for errors.

### 4. Export to GeoJSON

Once you're happy with the model:

```bash
python scripts/sysml_to_geojson.py \
  --input mbse/sysml/monchique_model.sysml \
  --output mbse/exports/monchique_from_sysml.geojson
```

---

## Integration with n8n Workflow

Add a step to Workflow 003 to handle both Capella and SysML v2:

**New Node: "Detect Model Type"**
- If file is `.sysml` → run `sysml_to_geojson.py`
- If file is `.json` (Capella export) → run `capella_to_geojson.py`
- Output: Unified GeoJSON for downstream analysis

---

## Resources

### SysML v2 Learning:
- [SysML v2 Release](https://github.com/Systems-Modeling/SysML-v2-Release)
- [SysML v2 Textual Notation](https://github.com/Systems-Modeling/SysML-v2-Release/tree/master/doc)
- [Extension Documentation](https://marketplace.visualstudio.com/items?itemName=jamied.sysml-v2-support)

### Capella Resources:
- [Capella Documentation](https://www.eclipse.org/capella/documentation.html)
- [Your Setup Guide](CAPELLA_PROJECT_SETUP.md)

---

## Recommendation for Your Project

**Start with SysML v2 in VS Code** because:

1. ✅ You already have VS Code workflow established
2. ✅ Your team is comfortable with text-based formats
3. ✅ Git integration is critical for your federated workflow
4. ✅ The extensions you installed are excellent
5. ✅ Easier to automate (Python scripts can generate `.sysml` files)

**Add Capella later** if you need:
- Complex multi-layer architecture views
- Formal Arcadia method compliance
- Rich diagram generation for stakeholder presentations

**Best of both**: Use SysML v2 for daily modeling, generate Capella diagrams for documentation.

---

## Next Steps

1. **Try SysML v2 first**:
   ```bash
   mkdir -p mbse/sysml
   # Create monchique_model.sysml with example above
   ```

2. **Test conversion**:
   ```bash
   python scripts/sysml_to_geojson.py --input mbse/sysml/monchique_model.sysml
   ```

3. **Compare with existing GeoJSON**:
   ```bash
   diff mbse/exports/monchique_federated_model.geojson \
        mbse/exports/monchique_from_sysml.geojson
   ```

4. **Decide**: Stick with SysML v2 or add Capella later

Would you like me to create the full SysML v2 model file and converter script to get you started?
