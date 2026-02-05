#!/usr/bin/env python3
"""
Generate Kumu Network JSON from GeoJSON and host on GitHub
This creates a remote-linkable JSON that Kumu can auto-refresh from
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def extract_sna_network_from_geojson(geojson_path):
    """Extract SNA nodes and edges from GeoJSON features"""
    
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)
    
    nodes = []
    edges = []
    
    # Extract nodes from features
    for feature in geojson['features']:
        props = feature['properties']
        
        node = {
            "id": props.get('snaNodeId', feature.get('id')),
            "label": props.get('name', feature.get('id')),
            "type": props.get('type', 'Entity'),
            "sector": props.get('sector', 'Unknown'),
            "level": props.get('level', 'Municipal'),
            "status": props.get('status', 'active'),
        }
        
        # Add domain-specific attributes
        if 'population' in props:
            node['population'] = props['population']
        if 'budget_euros' in props:
            node['budget'] = props['budget_euros']
        if 'memberCount' in props:
            node['members'] = props['memberCount']
        if 'governanceScore' in props:
            node['governance'] = props['governanceScore']
        if 'managementCapacity' in props:
            node['capacity'] = props['managementCapacity']
        
        nodes.append(node)
        
        # Extract edges from partnershipIds
        if 'partnershipIds' in props and props['partnershipIds']:
            source_id = props.get('snaNodeId', feature.get('id'))
            for partner_id in props['partnershipIds']:
                edge = {
                    "from": source_id,
                    "to": partner_id,
                    "type": "partnership",
                    "strength": 1.0
                }
                edges.append(edge)
    
    return nodes, edges

def generate_kumu_json(nodes, edges, metadata=None):
    """Generate Kumu-compatible JSON with elements and connections"""
    
    elements = []
    connections = []
    
    # Convert nodes to Kumu elements
    for node in nodes:
        element = {
            "label": node['label'],
            "type": node.get('type', 'Entity'),
            "id": node['id'],
            "attributes": {
                "sector": node.get('sector', ''),
                "level": node.get('level', ''),
                "status": node.get('status', ''),
            }
        }
        
        # Add optional attributes
        if 'population' in node:
            element['attributes']['population'] = node['population']
        if 'budget' in node:
            element['attributes']['budget'] = node['budget']
        if 'members' in node:
            element['attributes']['members'] = node['members']
        if 'governance' in node:
            element['attributes']['governance'] = node['governance']
        if 'capacity' in node:
            element['attributes']['capacity'] = node['capacity']
        
        elements.append(element)
    
    # Convert edges to Kumu connections
    for edge in edges:
        connection = {
            "from": edge['from'],
            "to": edge['to'],
            "type": edge.get('type', 'partnership'),
            "attributes": {
                "strength": edge.get('strength', 1.0)
            }
        }
        connections.append(connection)
    
    # Create Kumu JSON structure
    kumu_data = {
        "elements": elements,
        "connections": connections
    }
    
    if metadata:
        kumu_data['metadata'] = metadata
    
    return kumu_data

def main():
    repo_root = Path(__file__).parent.parent
    
    # Input: GeoJSON with SNA properties
    geojson_path = repo_root / "mbse/exports/monchique_federated_model.geojson"
    
    # Output: Kumu JSON for remote linking
    output_path = repo_root / "sna/exports/kumu_network.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Generating Kumu Network JSON for remote linking...")
    print(f"📂 Input: {geojson_path}")
    
    # Extract network
    nodes, edges = extract_sna_network_from_geojson(geojson_path)
    
    print(f"✅ Extracted {len(nodes)} nodes and {len(edges)} edges")
    
    # Generate Kumu JSON
    metadata = {
        "name": "Monchique Rural OSDK Network",
        "description": "Federated MBSE-GIS-SNA network for Monchique rural development",
        "generated": datetime.now().isoformat(),
        "source": "federated-rural-osdk-platform",
        "github": "https://github.com/jrskim7/federated-rural-osdk-platform"
    }
    
    kumu_data = generate_kumu_json(nodes, edges, metadata)
    
    # Save to file
    with open(output_path, 'w') as f:
        json.dump(kumu_data, f, indent=2)
    
    print(f"✅ Kumu JSON saved: {output_path}")
    print(f"\n📊 Network Summary:")
    print(f"   Elements: {len(kumu_data['elements'])}")
    print(f"   Connections: {len(kumu_data['connections'])}")
    
    # Generate GitHub raw URL
    github_raw_url = "https://raw.githubusercontent.com/jrskim7/federated-rural-osdk-platform/main/sna/exports/kumu_network.json"
    
    print(f"\n🔗 Remote Link URL (for Kumu):")
    print(f"   {github_raw_url}")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Commit and push this file to GitHub:")
    print(f"      git add sna/exports/kumu_network.json")
    print(f"      git commit -m 'Add Kumu network JSON for remote linking'")
    print(f"      git push origin main")
    print(f"")
    print(f"   2. In Kumu (https://kumu.io):")
    print(f"      → Create new project or open existing")
    print(f"      → Click '+' → 'Import' → 'From URL'")
    print(f"      → Paste: {github_raw_url}")
    print(f"      → Kumu will auto-refresh whenever GitHub file updates")
    print(f"")
    print(f"   3. Update network anytime:")
    print(f"      → Edit GeoJSON (add partnerships, change attributes)")
    print(f"      → Run: python scripts/generate_kumu_remote.py")
    print(f"      → Git commit + push")
    print(f"      → Kumu refreshes automatically")

if __name__ == "__main__":
    main()
