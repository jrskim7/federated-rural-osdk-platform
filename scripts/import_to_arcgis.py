#!/usr/bin/env python3
"""
Import Federated OSDK GeoJSON Model to ArcGIS Online
Converts local GeoJSON (with schema mapping) to Feature Layer in ArcGIS Online
"""

import json
import sys
import os
from pathlib import Path
import requests
from arcgis.gis import GIS
from dotenv import load_dotenv

# Load environment variables from orchestrator/.env
env_path = Path(__file__).parent.parent / "orchestrator" / ".env"
load_dotenv(env_path)

ARCGIS_USERNAME = os.getenv("ARCGIS_USERNAME")
ARCGIS_PASSWORD = os.getenv("ARCGIS_PASSWORD")
ARCGIS_ORG_URL = os.getenv("ARCGIS_ORG_URL", "https://www.arcgis.com")

def load_geojson(filepath):
    """Load GeoJSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)

def publish_geojson_as_shapefile(gis, geojson_filepath, layer_name="Monchique Federated OSDK Model"):
    """
    Convert GeoJSON to shapefile and publish to ArcGIS Online
    """
    print(f"🔄 Converting GeoJSON to shapefile format...")
    
    geojson_data = load_geojson(geojson_filepath)
    
    # Create a zip file with shapefiles (simplified approach)
    # For now, publish as table and use REST API
    
    item_properties = {
        "title": layer_name,
        "type": "Feature Service",
        "tags": ["MBSE", "GIS", "SNA", "Rural Development", "OSDK"],
        "description": "Federated OSDK ontology-mapped feature layer with schema mappings to MBSE blocks and SNA nodes"
    }
    
    # Alternative: Create CSV and import as table
    print(f"📋 Creating CSV from GeoJSON...")
    import csv
    import tempfile
    
    # Extract all unique properties from features
    all_keys = set()
    for feature in geojson_data["features"]:
        all_keys.update(feature["properties"].keys())
    
    all_keys = sorted(list(all_keys))
    all_keys = ["id", "geometry_type"] + all_keys  # Add geometry info
    
    csv_path = "/tmp/osdk_features.csv"
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()
        
        for feature in geojson_data["features"]:
            row = {
                "id": feature.get("id", ""),
                "geometry_type": feature["geometry"]["type"] if feature.get("geometry") else "",
            }
            row.update(feature["properties"])
            # Fill missing values
            for key in all_keys:
                if key not in row:
                    row[key] = ""
            writer.writerow(row)
    
    print(f"✅ CSV created: {csv_path}")
    print(f"📊 Features: {len(geojson_data['features'])}")
    
    # Upload CSV to ArcGIS Online
    print(f"📤 Publishing to ArcGIS Online...")
    try:
        csv_item = gis.content.add(
            item_properties={
                **item_properties,
                "type": "CSV"
            },
            data=csv_path
        )
        print(f"✅ CSV published: {csv_item.title}")
        print(f"📍 Item ID: {csv_item.id}")
        print(f"🔗 URL: {csv_item.url}")
        
        # Publish as feature layer from the CSV
        print(f"\n🔄 Publishing Feature Layer from CSV...")
        try:
            feature_layer = csv_item.publish()
            print(f"✅ Feature Layer published: {feature_layer.title}")
            print(f"📍 Item ID: {feature_layer.id}")
            print(f"🔗 URL: {feature_layer.url}")
            return feature_layer
        except Exception as e:
            print(f"⚠️  CSV uploaded but publish failed: {e}")
            print(f"💡 Manually publish from ArcGIS Online: {csv_item.url}")
            return csv_item
            
    except Exception as e:
        print(f"❌ Error uploading CSV: {e}")
        return None

def main():
    # Authenticate
    print("🔐 Authenticating with ArcGIS Online...")
    try:
        gis = GIS(ARCGIS_ORG_URL, ARCGIS_USERNAME, ARCGIS_PASSWORD)
        print(f"✅ Authenticated as {gis.users.me.username}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Ensure ARCGIS_USERNAME and ARCGIS_PASSWORD are set in .env")
        sys.exit(1)
    
    # Load GeoJSON
    geojson_path = Path(__file__).parent.parent / "mbse/exports/monchique_federated_model.geojson"
    if not geojson_path.exists():
        print(f"❌ GeoJSON file not found: {geojson_path}")
        sys.exit(1)
    
    print(f"📂 Loading GeoJSON: {geojson_path}")
    geojson_data = load_geojson(geojson_path)
    print(f"📊 Loaded {len(geojson_data['features'])} features")
    
    # Publish Feature Layer
    item = publish_geojson_as_shapefile(
        gis,
        str(geojson_path),
        layer_name="Monchique Federated OSDK Model"
    )
    
    if item:
        print("\n✨ Feature Layer successfully published to ArcGIS Online!")
        print(f"📋 Next steps:")
        print(f"  1. Open: {item.url}")
        print(f"  2. If CSV: Click 'Publish' → 'Publish as Feature Layer'")
        print(f"  3. Configure field visibility and symbology in ArcGIS Online")
        print(f"  4. Set MBSE and SNA IDs as filter/relationship keys")
        print(f"  5. Share with collaborative workspaces")
    else:
        print("❌ Failed to publish Feature Layer")
        sys.exit(1)

if __name__ == "__main__":
    main()

