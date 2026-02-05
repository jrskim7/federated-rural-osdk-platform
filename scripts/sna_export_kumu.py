#!/usr/bin/env python3
"""
Export SNA data to Kumu.io format (JSON)
Kumu is a web-based network visualization platform
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def export_to_kumu_json(nodes_data: dict, edges_data: list, output_path: Path):
    """
    Export network to Kumu JSON format
    Kumu structure: {elements: [{id, attributes}], connections: [{from, to, attributes}]}
    """
    
    print(f"🎨 Exporting to Kumu JSON format...")
    
    kumu_data = {
        "elements": [],
        "connections": []
    }
    
    # Convert nodes to Kumu elements
    for node_id, node in nodes_data.items():
        element = {
            "_id": node_id,
            "label": node['name'],
            "type": node['type'],
            "tags": [node['sector'], node['level']],
            "description": f"{node['type']} - {node['sector']}",
            "attributes": {
                "Sector": node['sector'],
                "Level": node['level'],
                "Status": node['status'],
                "Degree Centrality": node.get('degree_centrality', 0),
                "Weighted Degree": node.get('weighted_degree', 0),
                "Capacity": node['capacity'],
                "Population": node['population'],
                "Budget (€)": node['budget'],
                "MBSE Block ID": node['mbseBlockId']
            }
        }
        kumu_data["elements"].append(element)
    
    # Convert edges to Kumu connections
    for i, edge in enumerate(edges_data):
        connection = {
            "_id": f"connection_{i}",
            "from": edge['source'],
            "to": edge['target'],
            "label": edge['type'],
            "direction": "mutual" if edge.get('bidirectional') else "directed",
            "attributes": {
                "Type": edge['type'],
                "Weight": edge['weight'],
                "Validation Event": edge.get('validation_event', '')
            }
        }
        kumu_data["connections"].append(connection)
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(kumu_data, f, indent=2)
    
    print(f"✅ Kumu JSON exported: {output_path}")
    print(f"\n📋 To import into Kumu:")
    print(f"  1. Go to https://kumu.io")
    print(f"  2. Create new project → Import → JSON")
    print(f"  3. Upload: {output_path.name}")
    print(f"  4. Decorate:")
    print(f"     • Size by: 'Degree Centrality' or 'Weighted Degree'")
    print(f"     • Color by: 'Sector' (Public=Blue, Private=Red, Civil=Green)")
    print(f"     • Connection thickness by: 'Weight'")
    
    return output_path


def create_kumu_visualization_guide(output_path: Path):
    """Create a Markdown guide for Kumu visualization"""
    
    guide = f"""# Kumu Network Visualization Guide

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Import to Kumu

1. **Go to Kumu**: https://kumu.io
2. **Create Project**: Click "New Project" → "Import from JSON"
3. **Upload**: Select `kumu_network_TIMESTAMP.json`
4. **Wait**: Kumu will parse and display your network

## Recommended Decorations

### Element Sizing
```
@settings {{
  element-size: scale("degree centrality", 20, 50);
}}
```
This makes more connected actors larger.

### Element Coloring by Sector
```
element[sector="Public"] {{
  color: #3498db;
  label-color: #2c3e50;
}}

element[sector="Private"] {{
  color: #e74c3c;
  label-color: #2c3e50;
}}

element[sector="Civil Society"] {{
  color: #2ecc71;
  label-color: #2c3e50;
}}

element[sector="Environment"] {{
  color: #8e44ad;
  label-color: #2c3e50;
}}
```

### Connection Styling by Weight
```
connection {{
  width: scale("weight", 1, 5);
  color: #95a5a6;
}}

connection[weight > 1.2] {{
  color: #27ae60;  /* Strong partnerships = green */
  style: dashed;
}}
```

### Labels
```
element {{
  font-size: 16;
  font-weight: bold;
}}
```

## Layouts

Try these layouts (Settings → Layout):

1. **Force-directed**: Best for showing clusters
2. **Radial**: Good for highlighting central actors
3. **Concentric**: Organize by degree centrality

## Filters

Create filters to explore:

- **By Sector**: Filter to show only Public or Private actors
- **By Capacity**: Show only high-capacity organizations
- **Strong Partnerships**: Filter connections where Weight > 1.0

## Analysis Features

Use Kumu's built-in metrics:

- **Betweenness Centrality**: Identifies brokers/bridges
- **Closeness Centrality**: Measures overall network influence
- **Clustering**: Detect communities within network

## Sharing

- Click "Share" to get public link
- Embed in websites or reports
- Export as PNG/SVG for presentations

## Next Steps

1. Add more actor attributes from GeoJSON
2. Include temporal data (track changes over time)
3. Link to external data sources (ArcGIS dashboards, MBSE models)
"""
    
    with open(output_path, 'w') as f:
        f.write(guide)
    
    print(f"✅ Kumu guide: {output_path}")
    return output_path


def main():
    """Run Kumu export on latest SNA analysis"""
    
    repo_root = Path(__file__).parent.parent
    sna_output_dir = repo_root / "sna/output"
    
    # Load nodes and edges from CSV (already generated by sna_integration.py)
    nodes_csv = sna_output_dir / "sna_nodes.csv"
    edges_csv = sna_output_dir / "sna_edges.csv"
    
    if not nodes_csv.exists() or not edges_csv.exists():
        print("❌ Error: Run sna_integration.py first to generate network data")
        print("   Command: python scripts/sna_integration.py")
        sys.exit(1)
    
    # Parse CSV to dict
    import csv
    
    nodes_data = {}
    with open(nodes_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nodes_data[row['id']] = {
                'name': row['name'],
                'type': row['type'],
                'sector': row['sector'],
                'level': row['level'],
                'status': row['status'],
                'degree_centrality': int(row['degree_centrality']),
                'weighted_degree': float(row['weighted_degree']),
                'capacity': float(row['capacity']),
                'population': int(float(row['population'])) if row['population'] else 0,
                'budget': int(float(row['budget'])) if row['budget'] else 0,
                'mbseBlockId': row['mbseBlockId']
            }
    
    edges_data = []
    with open(edges_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            edges_data.append({
                'source': row['source'],
                'target': row['target'],
                'type': row['type'],
                'weight': float(row['weight']),
                'bidirectional': row['bidirectional'] == 'True',
                'validation_event': row.get('validation_event', '')
            })
    
    # Export to Kumu JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    kumu_json_path = sna_output_dir / f"kumu_network_{timestamp}.json"
    export_to_kumu_json(nodes_data, edges_data, kumu_json_path)
    
    # Create visualization guide
    guide_path = sna_output_dir / "KUMU_VISUALIZATION_GUIDE.md"
    create_kumu_visualization_guide(guide_path)
    
    print(f"\n✨ Kumu export complete!")
    print(f"📁 Files created:")
    print(f"   • {kumu_json_path}")
    print(f"   • {guide_path}")

if __name__ == "__main__":
    main()
