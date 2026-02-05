#!/usr/bin/env python3
"""
Social Network Analysis (SNA) Integration
Extracts actor relationships from GeoJSON features and generates network graphs
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
import csv

class SNANetworkBuilder:
    def __init__(self):
        self.nodes = {}  # {node_id: {attributes}}
        self.edges = []  # [{source, target, weight, type, attributes}]
        
    def extract_actors_from_geojson(self, geojson_path: str):
        """Extract actor nodes from GeoJSON features"""
        
        print(f"📊 Extracting actors from: {geojson_path}")
        
        with open(geojson_path, 'r') as f:
            data = json.load(f)
        
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            
            # Extract node if it has snaNodeId
            sna_node_id = props.get('snaNodeId')
            if sna_node_id:
                self.nodes[sna_node_id] = {
                    'id': sna_node_id,
                    'name': props.get('name', 'Unknown'),
                    'type': props.get('type', 'Unknown'),
                    'sector': props.get('sector', 'Unknown'),
                    'level': props.get('level', 'Unknown'),
                    'status': props.get('status', 'Unknown'),
                    'mbseBlockId': props.get('mbseBlockId', ''),
                    'featureId': feature.get('id', ''),
                    # Actor-specific attributes
                    'population': props.get('population', props.get('memberCount', 0)),
                    'budget': props.get('budget_euros', 0),
                    'capacity': props.get('managementCapacity', props.get('governanceScore', 0.5)),
                    'adoptedMethodologies': props.get('adoptedMethodologies', []),
                    'partnershipIds': props.get('partnershipIds', [])
                }
        
        print(f"✅ Extracted {len(self.nodes)} actor nodes")
        return self.nodes
    
    def build_partnership_network(self):
        """Build edges from partnershipIds relationships"""
        
        print(f"🔗 Building partnership network...")
        
        edge_count = 0
        for node_id, node_data in self.nodes.items():
            partner_ids = node_data.get('partnershipIds', [])
            
            for partner_ref in partner_ids:
                # Map partnership references to snaNodeIds
                # Example: "Coop_Algarve" → "Node_Coop_Algarve"
                # or "Mun_Camara" → "Node_Mun_Camara"
                
                # Try exact match first
                partner_node_id = None
                for potential_id in self.nodes.keys():
                    if partner_ref in potential_id or potential_id in partner_ref:
                        partner_node_id = potential_id
                        break
                
                if partner_node_id and partner_node_id in self.nodes:
                    # Create edge
                    edge = {
                        'source': node_id,
                        'target': partner_node_id,
                        'type': 'partnership',
                        'weight': 1.0,  # Base weight
                        'bidirectional': True
                    }
                    
                    # Avoid duplicates (bidirectional)
                    reverse_exists = any(
                        e['source'] == partner_node_id and e['target'] == node_id
                        for e in self.edges
                    )
                    
                    if not reverse_exists:
                        self.edges.append(edge)
                        edge_count += 1
        
        print(f"✅ Created {edge_count} partnership edges")
        return self.edges
    
    def calculate_trust_weights(self, change_summary_path: str = None):
        """
        Calculate trust/influence weights based on community validation
        Increases edge weight if both parties validated a common feature
        """
        
        if not change_summary_path or not os.path.exists(change_summary_path):
            print("⚠️  No change summary provided, using default weights")
            return
        
        print(f"📈 Calculating trust weights from: {change_summary_path}")
        
        with open(change_summary_path, 'r') as f:
            changes = json.load(f)
        
        # Example: If a feature was validated by community, increase trust
        # between actors who participated
        participants = changes.get('participants', [])
        
        if participants:
            print(f"   Community meeting with {len(participants)} participants")
            
            # Increase trust between all participant pairs
            for i, p1 in enumerate(participants):
                for p2 in participants[i+1:]:
                    # Find edges connecting these participants
                    for edge in self.edges:
                        source_name = self.nodes[edge['source']]['name']
                        target_name = self.nodes[edge['target']]['name']
                        
                        # Check if participant names match node names
                        if (p1 in source_name or source_name in p1) and \
                           (p2 in target_name or target_name in p2):
                            edge['weight'] += 0.3  # Trust boost
                            edge['validation_event'] = changes.get('session', 'Community Meeting')
                            print(f"   ✅ Trust +0.3: {source_name} ↔ {target_name}")
        
        # Check for modified features with community approval
        for modification in changes.get('modified', []):
            if 'communityApproval' in str(modification.get('changes', {})):
                # Boost all edges (general community consensus)
                for edge in self.edges:
                    edge['weight'] += 0.1
                print(f"   ✅ Community approval bonus +0.1 to all edges")
                break
    
    def calculate_centrality_metrics(self):
        """Calculate basic centrality metrics for each node"""
        
        print(f"📊 Calculating centrality metrics...")
        
        # Degree centrality (number of connections)
        for node_id in self.nodes:
            degree = sum(
                1 for e in self.edges
                if e['source'] == node_id or e['target'] == node_id
            )
            self.nodes[node_id]['degree_centrality'] = degree
            
            # Weighted degree (sum of edge weights)
            weighted_degree = sum(
                e['weight'] for e in self.edges
                if e['source'] == node_id or e['target'] == node_id
            )
            self.nodes[node_id]['weighted_degree'] = round(weighted_degree, 2)
        
        # Identify central actors
        central_actors = sorted(
            self.nodes.items(),
            key=lambda x: x[1]['degree_centrality'],
            reverse=True
        )[:3]
        
        print(f"✅ Top 3 central actors:")
        for node_id, data in central_actors:
            print(f"   • {data['name']}: {data['degree_centrality']} connections (weight: {data['weighted_degree']})")
        
        return self.nodes
    
    def export_to_csv(self, output_dir: Path):
        """Export nodes and edges to CSV (for Gephi/Kumu import)"""
        
        nodes_file = output_dir / "sna_nodes.csv"
        edges_file = output_dir / "sna_edges.csv"
        
        # Export nodes
        with open(nodes_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'type', 'sector', 'level', 'status',
                'degree_centrality', 'weighted_degree', 'capacity',
                'population', 'budget', 'mbseBlockId'
            ])
            writer.writeheader()
            for node in self.nodes.values():
                writer.writerow({
                    'id': node['id'],
                    'name': node['name'],
                    'type': node['type'],
                    'sector': node['sector'],
                    'level': node['level'],
                    'status': node['status'],
                    'degree_centrality': node.get('degree_centrality', 0),
                    'weighted_degree': node.get('weighted_degree', 0),
                    'capacity': node['capacity'],
                    'population': node['population'],
                    'budget': node['budget'],
                    'mbseBlockId': node['mbseBlockId']
                })
        
        # Export edges
        with open(edges_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'source', 'target', 'type', 'weight', 'bidirectional', 'validation_event'
            ])
            writer.writeheader()
            for edge in self.edges:
                writer.writerow({
                    'source': edge['source'],
                    'target': edge['target'],
                    'type': edge['type'],
                    'weight': edge['weight'],
                    'bidirectional': edge.get('bidirectional', True),
                    'validation_event': edge.get('validation_event', '')
                })
        
        print(f"✅ Exported CSV files:")
        print(f"   Nodes: {nodes_file}")
        print(f"   Edges: {edges_file}")
        
        return nodes_file, edges_file
    
    def export_to_graphml(self, output_path: Path):
        """Export to GraphML format (for Gephi)"""
        
        print(f"📝 Exporting to GraphML: {output_path}")
        
        graphml = ['<?xml version="1.0" encoding="UTF-8"?>']
        graphml.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns">')
        graphml.append('  <key id="name" for="node" attr.name="name" attr.type="string"/>')
        graphml.append('  <key id="type" for="node" attr.name="type" attr.type="string"/>')
        graphml.append('  <key id="sector" for="node" attr.name="sector" attr.type="string"/>')
        graphml.append('  <key id="centrality" for="node" attr.name="degree_centrality" attr.type="int"/>')
        graphml.append('  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>')
        graphml.append('  <graph id="G" edgedefault="undirected">')
        
        # Add nodes
        for node_id, node in self.nodes.items():
            graphml.append(f'    <node id="{node_id}">')
            graphml.append(f'      <data key="name">{node["name"]}</data>')
            graphml.append(f'      <data key="type">{node["type"]}</data>')
            graphml.append(f'      <data key="sector">{node["sector"]}</data>')
            graphml.append(f'      <data key="centrality">{node.get("degree_centrality", 0)}</data>')
            graphml.append('    </node>')
        
        # Add edges
        for i, edge in enumerate(self.edges):
            graphml.append(f'    <edge id="e{i}" source="{edge["source"]}" target="{edge["target"]}">')
            graphml.append(f'      <data key="weight">{edge["weight"]}</data>')
            graphml.append('    </edge>')
        
        graphml.append('  </graph>')
        graphml.append('</graphml>')
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(graphml))
        
        print(f"✅ GraphML exported: {output_path}")
        return output_path
    
    def generate_summary_report(self, output_path: Path):
        """Generate human-readable summary of network analysis"""
        
        report = []
        report.append("=" * 80)
        report.append("SOCIAL NETWORK ANALYSIS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        report.append(f"Network Overview:")
        report.append(f"  • Total Actors: {len(self.nodes)}")
        report.append(f"  • Total Partnerships: {len(self.edges)}")
        report.append(f"  • Average Connections per Actor: {len(self.edges) * 2 / len(self.nodes):.1f}")
        report.append("")
        
        # Sector breakdown
        sectors = {}
        for node in self.nodes.values():
            sector = node['sector']
            sectors[sector] = sectors.get(sector, 0) + 1
        
        report.append("Actor Distribution by Sector:")
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  • {sector}: {count}")
        report.append("")
        
        # Central actors
        central = sorted(self.nodes.items(), key=lambda x: x[1].get('degree_centrality', 0), reverse=True)[:5]
        report.append("Top 5 Central Actors (by degree):")
        for i, (node_id, node) in enumerate(central, 1):
            report.append(f"  {i}. {node['name']} ({node['sector']})")
            report.append(f"     Connections: {node.get('degree_centrality', 0)}, Weighted: {node.get('weighted_degree', 0)}")
        report.append("")
        
        # Partnership strengths
        strong_partnerships = sorted(self.edges, key=lambda x: x['weight'], reverse=True)[:5]
        report.append("Top 5 Strongest Partnerships:")
        for i, edge in enumerate(strong_partnerships, 1):
            source_name = self.nodes[edge['source']]['name']
            target_name = self.nodes[edge['target']]['name']
            report.append(f"  {i}. {source_name} ↔ {target_name}")
            report.append(f"     Weight: {edge['weight']:.2f}, Type: {edge['type']}")
            if 'validation_event' in edge:
                report.append(f"     Validated: {edge['validation_event']}")
        report.append("")
        
        report.append("=" * 80)
        
        report_text = '\n'.join(report)
        
        with open(output_path, 'w') as f:
            f.write(report_text)
        
        print(f"✅ Summary report: {output_path}")
        print("\n" + report_text)
        
        return output_path


def main():
    repo_root = Path(__file__).parent.parent
    exports_dir = repo_root / "mbse/exports"
    sna_output_dir = repo_root / "sna/output"
    sna_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize network builder
    builder = SNANetworkBuilder()
    
    # Find latest edited GeoJSON (or use original)
    edited_files = sorted(exports_dir.glob("monchique_federated_model_edited_*.geojson"))
    if edited_files:
        geojson_file = edited_files[-1]  # Most recent
        print(f"📂 Using edited GeoJSON: {geojson_file.name}")
    else:
        geojson_file = exports_dir / "monchique_federated_model.geojson"
        print(f"📂 Using original GeoJSON: {geojson_file.name}")
    
    # Extract actors
    builder.extract_actors_from_geojson(geojson_file)
    
    # Build partnership network
    builder.build_partnership_network()
    
    # Calculate trust weights from change summary (if available)
    change_summaries = sorted(exports_dir.glob("change_summary_*.json"))
    if change_summaries:
        builder.calculate_trust_weights(change_summaries[-1])
    
    # Calculate centrality metrics
    builder.calculate_centrality_metrics()
    
    # Export formats
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # CSV (Gephi/Kumu)
    builder.export_to_csv(sna_output_dir)
    
    # GraphML (Gephi)
    graphml_path = sna_output_dir / f"sna_network_{timestamp}.graphml"
    builder.export_to_graphml(graphml_path)
    
    # Summary report
    report_path = sna_output_dir / f"sna_report_{timestamp}.txt"
    builder.generate_summary_report(report_path)
    
    print(f"\n✨ SNA Integration Complete!")
    print(f"📁 Output directory: {sna_output_dir}")
    print(f"\n🎯 Next Steps:")
    print(f"  1. Import sna_nodes.csv and sna_edges.csv into Gephi or Kumu")
    print(f"  2. Apply layout algorithm (Force Atlas 2, Fruchterman-Reingold)")
    print(f"  3. Color nodes by sector, size by degree centrality")
    print(f"  4. Visualize partnership strengths (edge thickness = weight)")

if __name__ == "__main__":
    main()
