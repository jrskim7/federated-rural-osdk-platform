# Social Network Analysis (SNA) Integration

## Overview

The SNA integration extracts actor relationships from GeoJSON features, calculates network metrics, and generates visualizations showing partnership strength, trust, and influence within the Monchique rural development ecosystem.

## What It Does

1. **Extracts Actors**: Identifies all entities with `snaNodeId` from GeoJSON
2. **Builds Partnerships**: Creates edges from `partnershipIds` relationships
3. **Calculates Trust**: Weights edges based on community validation events
4. **Computes Metrics**: Degree centrality, weighted degree, betweenness
5. **Exports Formats**: CSV (Gephi), GraphML (Gephi), JSON (Kumu)
6. **Generates Reports**: Human-readable network summary

## Quick Start

### Run SNA Analysis

```bash
# From repository root
python .venv/bin/python scripts/sna_integration.py
```

**Output:**
- `sna/output/sna_nodes.csv` - Actor nodes with attributes
- `sna/output/sna_edges.csv` - Partnership edges with weights
- `sna/output/sna_network_TIMESTAMP.graphml` - Gephi format
- `sna/output/sna_report_TIMESTAMP.txt` - Summary report

### Export for Web Visualization (Kumu)

```bash
python .venv/bin/python scripts/sna_export_kumu.py
```

**Output:**
- `sna/output/kumu_network_TIMESTAMP.json` - Kumu import file
- `sna/output/KUMU_VISUALIZATION_GUIDE.md` - Styling guide

## Data Schema

### Node Attributes

Every actor node contains:

| Attribute | Type | Description | Source |
|-----------|------|-------------|--------|
| `id` | string | Unique SNA node ID | `snaNodeId` from GeoJSON |
| `name` | string | Actor display name | `name` from GeoJSON |
| `type` | string | Entity type (Municipality, Cooperative, etc.) | `type` |
| `sector` | string | Public, Private, Civil Society, Environment | `sector` |
| `level` | string | Municipal, District, National | `level` |
| `status` | string | active, inactive, planning | `status` |
| `degree_centrality` | int | Number of direct connections | Calculated |
| `weighted_degree` | float | Sum of edge weights | Calculated |
| `capacity` | float | Management/governance capacity (0-1) | `capacity` or `governanceScore` |
| `population` | int | Population or member count | `population` or `memberCount` |
| `budget` | int | Budget in euros | `budget_euros` |
| `mbseBlockId` | string | Link to Capella MBSE model | `mbseBlockId` |

### Edge Attributes

Every partnership edge contains:

| Attribute | Type | Description |
|-----------|------|-------------|
| `source` | string | Source node ID |
| `target` | string | Target node ID |
| `type` | string | Partnership type (currently all "partnership") |
| `weight` | float | Strength (1.0 base, boosted by validation) |
| `bidirectional` | boolean | True (partnerships are mutual) |
| `validation_event` | string | Community meeting that validated relationship |

## Trust Calculation

Partnership weights are dynamically calculated based on:

### Base Weight: 1.0
All partnerships start with weight 1.0

### Community Validation Boost: +0.3
If both actors participated in same community meeting:
- Extracted from `change_summary_*.json`
- Identifies participants from meeting metadata
- Matches participant names to actor names
- Adds +0.3 to edge weight

### Community Approval Boost: +0.1
If features were validated with `communityApproval`:
- All edges receive +0.1 (general trust boost)
- Indicates successful community consensus

### Example
```
Initial: Municipality ↔ Cooperative = 1.0
After community meeting: = 1.3 (both participated)
After project approval: = 1.4 (community consensus)
```

## Visualization

### Gephi (Desktop Software)

1. **Download Gephi**: https://gephi.org
2. **Import Network**:
   - File → Open → Select `sna_network_TIMESTAMP.graphml`
   - Or import both `sna_nodes.csv` and `sna_edges.csv`

3. **Layout**:
   - Layout → Force Atlas 2
   - Run until network stabilizes
   - Apply "Prevent Overlap"

4. **Styling**:
   - **Node Size**: Ranking → degree_centrality → Min 10, Max 50
   - **Node Color**: Partition → sector → Choose color scheme:
     - Public = Blue
     - Private = Red
     - Civil Society = Green
     - Environment = Purple
   - **Edge Thickness**: Ranking → weight → Min 1, Max 5
   - **Edge Color**: #95a5a6 (gray), strong partnerships (#27ae60 green)

5. **Analysis**:
   - Statistics → Network Diameter → Run
   - Statistics → Modularity → Run (detect communities)
   - Statistics → Betweenness Centrality → Run (identify brokers)

6. **Export**:
   - File → Export → SVG/PDF for reports
   - File → Export → PNG for presentations

### Kumu (Web-Based)

1. **Upload to Kumu**:
   - Go to https://kumu.io
   - Create New Project → Import from JSON
   - Upload `kumu_network_TIMESTAMP.json`

2. **Apply Decorations** (see `KUMU_VISUALIZATION_GUIDE.md`):
   ```
   @settings {
     element-size: scale("degree centrality", 20, 50);
   }
   
   element[sector="Public"] { color: #3498db; }
   element[sector="Private"] { color: #e74c3c; }
   element[sector="Civil Society"] { color: #2ecc71; }
   
   connection {
     width: scale("weight", 1, 5);
   }
   ```

3. **Share**:
   - Click "Share" → Get public link
   - Embed in websites or ArcGIS dashboards

## Integration with Federated Workflow

### Triggered by GeoJSON Changes

When community edits are committed to GitHub:

```
1. Community edits feature in ArcGIS
   ↓
2. export_from_arcgis.py → GeoJSON + change_summary.json
   ↓
3. git commit + push
   ↓
4. GitHub webhook → n8n Workflow 005
   ↓
5. sna_integration.py runs automatically
   ↓
6. Network metrics updated
   ↓
7. Results → GitHub issue or notification
```

### n8n Workflow 005

Located at: `orchestrator/n8n/workflows/005-sna-analysis-on-commit.json`

**Nodes:**
1. GitHub Webhook - Receives push events
2. Check if SNA Should Run - Detects GeoJSON changes
3. Run SNA Integration - Executes analysis script
4. Export to Kumu - Generates web visualization
5. Read SNA Report - Parses results
6. Create GitHub Issue (optional) - Posts summary
7. Respond Success - Returns status

**To Import**:
1. Open n8n at http://localhost:5678
2. Workflows → Import from File
3. Select `005-sna-analysis-on-commit.json`
4. Activate workflow

## Use Cases

### 1. Identify Key Actors
**Goal**: Find central actors for community engagement

**Method**:
- Sort nodes by `degree_centrality`
- Top 3-5 actors are network hubs
- Engage these actors first for project buy-in

**Example from Monchique**:
```
1. Algarve Goat Cooperative (2 connections, weight 2.2)
2. Municipal Council (2 connections, weight 2.2)
3. Tourism Collective (2 connections, weight 2.2)
```

### 2. Measure Partnership Strength
**Goal**: Validate which partnerships are actively collaborating

**Method**:
- Sort edges by `weight`
- Weight > 1.2 = strong partnership (validated)
- Weight = 1.0 = formal but not recently active

**Insight**: Focus resources on strengthening weak partnerships

### 3. Detect Communities
**Goal**: Identify sub-groups within network

**Method** (Gephi):
- Statistics → Modularity → Run
- Partition → Modularity Class → Apply colors
- Each color = a community cluster

**Use**: Design targeted interventions per community

### 4. Find Brokers/Bridges
**Goal**: Identify actors connecting different groups

**Method** (Gephi):
- Statistics → Betweenness Centrality → Run
- Sort nodes by betweenness
- High betweenness = bridge between communities

**Value**: These actors are critical for information flow

### 5. Track Trust Over Time
**Goal**: Monitor how partnerships evolve with community meetings

**Method**:
- Run SNA before/after community meetings
- Compare edge weights over time
- Identify strengthened vs weakened partnerships

**Export**: Time-series graph showing trust evolution

## Extending SNA

### Add New Node Types

Edit GeoJSON to include new entities with `snaNodeId`:

```json
{
  "type": "Feature",
  "id": "NGO_WaterAlliance",
  "properties": {
    "name": "Water Conservation Alliance",
    "type": "NGO",
    "sector": "Civil Society",
    "snaNodeId": "Node_NGO_WaterAlliance",
    "partnershipIds": ["Mun_Camara", "Tourism_Group_B"]
  }
}
```

Re-run `sna_integration.py` → New node appears in network

### Add New Edge Types

Currently only "partnership". Can extend to:

- **Funding**: Financial flows between actors
- **Information**: Knowledge sharing
- **Resource**: Material/service exchange
- **Influence**: Power relationships

Modify `sna_integration.py` → `build_partnership_network()` to detect new edge types from GeoJSON properties.

### Custom Metrics

Add to `calculate_centrality_metrics()`:

```python
# Eigenvector centrality
# Closeness centrality
# PageRank
# Community detection (Louvain)
```

Use NetworkX library for advanced metrics.

## Troubleshooting

### "Extracted 0 actor nodes"
- **Cause**: GeoJSON features missing `snaNodeId`
- **Fix**: Add `snaNodeId` to all actor features in GeoJSON

### "Created 0 partnership edges"
- **Cause**: No `partnershipIds` in properties
- **Fix**: Add `partnershipIds: ["Actor1", "Actor2"]` to features

### "Trust weights not calculating"
- **Cause**: Missing `change_summary_*.json`
- **Fix**: Ensure community edits generate change summary

### Gephi won't open GraphML
- **Cause**: XML syntax error
- **Fix**: Validate with `xmllint sna_network_*.graphml`

### Kumu import fails
- **Cause**: Invalid JSON structure
- **Fix**: Validate with `jsonlint kumu_network_*.json`

## Next Steps

### Immediate
- ✅ SNA integration scripts created
- ✅ CSV, GraphML, Kumu exports working
- ✅ n8n workflow 005 ready
- ⏳ Import network into Gephi/Kumu
- ⏳ Create first visualization

### Soon
- ⏳ Add temporal analysis (track changes over time)
- ⏳ Integrate with ArcGIS dashboards (embed Kumu)
- ⏳ Auto-generate network metrics in GeoJSON properties
- ⏳ Link SNA to System Dynamics (actors → SD agents)
- ⏳ Link SNA to QSEM (actors → causal loop factors)

### Future
- ⏳ Real-time network updates (websocket sync)
- ⏳ Predictive modeling (forecast partnership evolution)
- ⏳ Sentiment analysis from meeting notes
- ⏳ Network resilience analysis

## References

- **NetworkX**: https://networkx.org/ (Python network analysis)
- **Gephi**: https://gephi.org/ (Desktop visualization)
- **Kumu**: https://kumu.io/ (Web-based visualization)
- **GraphML Spec**: http://graphml.graphdrawing.org/
- **SNA Metrics**: https://en.wikipedia.org/wiki/Social_network_analysis
