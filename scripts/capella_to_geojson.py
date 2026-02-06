#!/usr/bin/env python3
"""
Convert Capella JSON export to GeoJSON with MBSE-GIS-SNA schema mapping.

This script reads a Capella model export (JSON format) and converts it to 
GeoJSON features with proper ontological mapping.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def convert_capella_to_geojson(capella_json: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Capella entities to GeoJSON features."""
    
    features = []
    entities = capella_json.get("entities", [])
    
    for entity in entities:
        entity_id = entity.get("id")
        entity_name = entity.get("name", "")
        properties = entity.get("properties", {})
        
        # Determine geometry based on entity type
        geometry = determine_geometry(entity_name, properties)
        
        # Map to GeoJSON feature
        feature = {
            "type": "Feature",
            "id": entity_id,
            "geometry": geometry,
            "properties": map_properties(entity, properties)
        }
        
        features.append(feature)
    
    # Create GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "name": capella_json.get("model", "Capella Model"),
        "crs": {
            "type": "name",
            "properties": {
                "name": "EPSG:4326"
            }
        },
        "features": features
    }
    
    return geojson


def determine_geometry(entity_name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Determine geometry type and coordinates based on entity type."""
    
    # Check if geometry is specified in properties
    if "geometry" in properties:
        return properties["geometry"]
    
    # Default geometries for Monchique case study (Portugal)
    # Lon: -8.0 to -7.95, Lat: 37.3 to 37.35
    
    entity_lower = entity_name.lower()
    
    # Municipality → Polygon
    if "municipality" in entity_lower or "monchique" in entity_lower:
        return {
            "type": "Polygon",
            "coordinates": [[
                [-8.0, 37.3],
                [-7.95, 37.3],
                [-7.95, 37.35],
                [-8.0, 37.35],
                [-8.0, 37.3]
            ]]
        }
    
    # Ecological zones → Polygon
    elif "zone" in entity_lower or "eucalyptus" in entity_lower:
        return {
            "type": "Polygon",
            "coordinates": [[
                [-7.97, 37.31],
                [-7.96, 37.31],
                [-7.96, 37.32],
                [-7.97, 37.32],
                [-7.97, 37.31]
            ]]
        }
    
    # Default → Point
    else:
        # Generate point within Monchique bounds
        import random
        lon = -8.0 + random.random() * 0.05
        lat = 37.3 + random.random() * 0.05
        return {
            "type": "Point",
            "coordinates": [lon, lat]
        }


def map_properties(entity: Dict[str, Any], properties: Dict[str, Any]) -> Dict[str, Any]:
    """Map Capella properties to GeoJSON properties with OSDK schema."""
    
    mapped = {}
    
    # Required OSDK properties
    mapped["name"] = entity.get("name", "Unnamed")
    mapped["type"] = infer_type(entity.get("name", ""), properties)
    mapped["level"] = properties.get("level", {}).get("value", "Municipal")
    mapped["sector"] = properties.get("sector", {}).get("value", infer_sector(entity.get("name", "")))
    mapped["mbseBlockId"] = entity.get("id", "UNKNOWN")
    mapped["snaNodeId"] = generate_sna_node_id(entity.get("name", ""))
    mapped["status"] = properties.get("status", {}).get("value", "active")
    
    # Extract all other properties
    for prop_name, prop_data in properties.items():
        if prop_name in ["level", "sector", "status", "geometry"]:
            continue
        
        value = prop_data.get("value")
        if value is not None:
            # Convert property name to snake_case
            mapped_name = to_snake_case(prop_name)
            mapped[mapped_name] = value
    
    return mapped


def infer_type(name: str, properties: Dict[str, Any]) -> str:
    """Infer entity type from name."""
    name_lower = name.lower()
    
    if "municipality" in name_lower:
        return "Municipality"
    elif "micro" in name_lower and "hydro" in name_lower:
        return "Energy.ProjectSite"
    elif "cooperative" in name_lower or "coop" in name_lower:
        return "PrivateEntity"
    elif "zone" in name_lower:
        return "EcologicalZone"
    elif "council" in name_lower or "camara" in name_lower:
        return "PublicEntity"
    elif "tourism" in name_lower or "collective" in name_lower:
        return "CivilSocietyEntity"
    else:
        return "Entity"


def infer_sector(name: str) -> str:
    """Infer sector from entity name."""
    name_lower = name.lower()
    
    if "council" in name_lower or "municipality" in name_lower or "camara" in name_lower:
        return "Public"
    elif "cooperative" in name_lower or "coop" in name_lower:
        return "Private"
    elif "tourism" in name_lower or "collective" in name_lower:
        return "Civil Society"
    elif "zone" in name_lower or "ecological" in name_lower or "eucalyptus" in name_lower:
        return "Environment"
    else:
        return "Unknown"


def generate_sna_node_id(name: str) -> str:
    """Generate SNA node ID from entity name."""
    # Remove spaces, convert to CamelCase with "Node_" prefix
    words = name.split()
    if not words:
        return "Node_Unknown"
    
    camel = "".join(word.capitalize() for word in words)
    return f"Node_{camel}"


def to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    import re
    # Insert underscore before capital letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    # Insert underscore before capital letters followed by lowercase
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def main():
    parser = argparse.ArgumentParser(
        description="Convert Capella JSON export to GeoJSON with OSDK schema"
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to Capella JSON export file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output GeoJSON path (default: mbse/exports/monchique_federated_model.geojson)"
    )
    
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    input_path = Path(args.input)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    output_path = Path(args.output) if args.output else repo_root / "mbse/exports/monchique_federated_model.geojson"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Converting Capella JSON to GeoJSON...")
    print(f"📂 Input: {input_path}")
    
    # Load Capella JSON
    with input_path.open("r", encoding="utf-8") as f:
        capella_data = json.load(f)
    
    # Convert to GeoJSON
    geojson = convert_capella_to_geojson(capella_data)
    
    # Save GeoJSON
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)
    
    print(f"✅ Conversion complete")
    print(f"🗺️  Output: {output_path}")
    print(f"📊 Features: {len(geojson['features'])}")
    
    # Print summary
    print("\n📋 Feature Summary:")
    for feature in geojson["features"]:
        props = feature["properties"]
        print(f"   - {props.get('name')} ({props.get('type')})")
        print(f"     MBSE ID: {props.get('mbseBlockId')}")
        print(f"     SNA ID: {props.get('snaNodeId')}")


if __name__ == "__main__":
    main()
