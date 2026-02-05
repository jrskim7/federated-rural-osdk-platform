#!/usr/bin/env python3
"""
Export edits from ArcGIS Online Feature Layer back to GeoJSON
Enables participatory feedback loop: MBSE → ArcGIS → GeoJSON → GitHub → Orchestration
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import requests
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from dotenv import load_dotenv

# Load environment variables from orchestrator/.env
env_path = Path(__file__).parent.parent / "orchestrator" / ".env"
load_dotenv(env_path)

ARCGIS_USERNAME = os.getenv("ARCGIS_USERNAME")
ARCGIS_PASSWORD = os.getenv("ARCGIS_PASSWORD")
ARCGIS_ORG_URL = os.getenv("ARCGIS_ORG_URL", "https://www.arcgis.com")
ARCGIS_FEATURE_SERVICE_URL = os.getenv("ARCGIS_FEATURE_SERVICE_URL")

def find_feature_layer_by_name(gis, layer_name="Monchique Federated OSDK Model"):
    """Find feature layer by name in ArcGIS Online"""
    print(f"🔍 Searching for feature layer: {layer_name}")
    
    # Search for items
    search_results = gis.content.search(query=f"title:{layer_name}", item_type="Feature Service")
    
    if search_results:
        for item in search_results:
            print(f"✅ Found: {item.title} (ID: {item.id})")
            # Get the feature layer
            try:
                feature_service = FeatureLayer.fromitem(item, index=0)
                return feature_service
            except:
                # Try getting the feature collection
                if hasattr(item, 'layers'):
                    return item.layers[0]
    
    print(f"❌ Feature layer '{layer_name}' not found")
    return None

def export_feature_layer_to_geojson(feature_layer, output_path, include_edit_metadata=True):
    """Export feature layer from ArcGIS to GeoJSON with edit tracking"""
    
    print(f"📥 Exporting features from ArcGIS Online...")
    
    features_list = []
    
    try:
        # Query all features
        query_result = feature_layer.query(
            where="1=1",  # Get all features
            return_all_records=True,
            out_fields="*"  # All fields
        )
        
        print(f"📊 Retrieved {len(query_result.features)} features")
        
        for idx, feature in enumerate(query_result.features):
            geojson_feature = {
                "type": "Feature",
                "id": feature.attributes.get("OBJECTID", idx),
                "geometry": feature.geometry if hasattr(feature, 'geometry') and feature.geometry else None,
                "properties": feature.attributes
            }
            
            # Add edit metadata
            if include_edit_metadata:
                geojson_feature["properties"]["_arcgis_export_timestamp"] = datetime.now().isoformat()
                geojson_feature["properties"]["_arcgis_objectid"] = feature.attributes.get("OBJECTID")
                # Try to get edit time if available
                if "EditDate" in feature.attributes:
                    geojson_feature["properties"]["_last_edited"] = feature.attributes["EditDate"]
            
            features_list.append(geojson_feature)
        
        # Create FeatureCollection
        geojson_output = {
            "type": "FeatureCollection",
            "name": "Monchique Federated OSDK Model - Participatory Edits",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "EPSG:4326"
                }
            },
            "features": features_list
        }
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(geojson_output, f, indent=2)
        
        print(f"✅ GeoJSON exported: {output_path}")
        print(f"📊 Total features: {len(features_list)}")
        
        return geojson_output
        
    except Exception as e:
        print(f"❌ Error exporting features: {e}")
        return None

def compare_geojson_versions(original_path, edited_path):
    """Compare original and edited GeoJSON to identify changes"""
    
    print(f"\n📊 Comparing versions...")
    
    with open(original_path, 'r') as f:
        original = json.load(f)
    
    with open(edited_path, 'r') as f:
        edited = json.load(f)
    
    original_by_id = {f["id"]: f for f in original["features"]}
    edited_by_id = {f["id"]: f for f in edited["features"]}
    
    changes = {
        "modified": [],
        "added": [],
        "removed": []
    }
    
    # Check for modified features
    for feat_id, edited_feat in edited_by_id.items():
        if feat_id in original_by_id:
            original_feat = original_by_id[feat_id]
            # Compare properties
            if original_feat["properties"] != edited_feat["properties"]:
                changes["modified"].append({
                    "id": feat_id,
                    "name": edited_feat["properties"].get("name"),
                    "changes": {
                        key: {
                            "from": original_feat["properties"].get(key),
                            "to": edited_feat["properties"].get(key)
                        }
                        for key in edited_feat["properties"].keys()
                        if original_feat["properties"].get(key) != edited_feat["properties"].get(key)
                    }
                })
    
    # Check for added features
    for feat_id, feat in edited_by_id.items():
        if feat_id not in original_by_id:
            changes["added"].append({
                "id": feat_id,
                "name": feat["properties"].get("name")
            })
    
    # Check for removed features
    for feat_id, feat in original_by_id.items():
        if feat_id not in edited_by_id:
            changes["removed"].append({
                "id": feat_id,
                "name": feat["properties"].get("name")
            })
    
    # Print summary
    print(f"\n📝 Change Summary:")
    print(f"  ✏️  Modified: {len(changes['modified'])} features")
    if changes['modified']:
        for change in changes['modified']:
            print(f"     - {change['name']} (ID: {change['id']})")
            for key, vals in change['changes'].items():
                print(f"       {key}: {vals['from']} → {vals['to']}")
    
    print(f"  ✨ Added: {len(changes['added'])} features")
    if changes['added']:
        for change in changes['added']:
            print(f"     - {change['name']} (ID: {change['id']})")
    
    print(f"  🗑️  Removed: {len(changes['removed'])} features")
    if changes['removed']:
        for change in changes['removed']:
            print(f"     - {change['name']} (ID: {change['id']})")
    
    return changes

def main():
    # Authenticate
    print("🔐 Authenticating with ArcGIS Online...")
    try:
        gis = GIS(ARCGIS_ORG_URL, ARCGIS_USERNAME, ARCGIS_PASSWORD)
        print(f"✅ Authenticated as {gis.users.me.username}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)
    
    # Find feature layer
    feature_layer = find_feature_layer_by_name(gis, "Monchique Federated OSDK Model")
    if not feature_layer:
        print("❌ Cannot proceed without feature layer")
        sys.exit(1)
    
    # Export to GeoJSON
    output_dir = Path(__file__).parent.parent / "mbse/exports"
    output_path = output_dir / f"monchique_federated_model_edited_{datetime.now().strftime('%Y%m%d_%H%M%S')}.geojson"
    
    geojson_data = export_feature_layer_to_geojson(feature_layer, output_path)
    
    if geojson_data:
        print(f"\n✨ Successfully exported from ArcGIS Online!")
        print(f"📂 Output: {output_path}")
        
        # Compare with original if it exists
        original_path = output_dir / "monchique_federated_model.geojson"
        if original_path.exists():
            changes = compare_geojson_versions(original_path, output_path)
            
            # Save change summary
            summary_path = output_dir / f"change_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_path, 'w') as f:
                json.dump(changes, f, indent=2)
            print(f"📋 Change summary: {summary_path}")
        
        print(f"\n🔄 Next steps:")
        print(f"  1. Review changes in {output_path}")
        print(f"  2. Commit to GitHub: git add mbse/exports/ && git commit -m 'Community edits from ArcGIS participatory session'")
        print(f"  3. Push to trigger n8n workflow for downstream analysis")
    else:
        print("❌ Failed to export feature layer")
        sys.exit(1)

if __name__ == "__main__":
    main()
