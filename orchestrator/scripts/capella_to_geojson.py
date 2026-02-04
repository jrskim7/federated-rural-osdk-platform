"""Convert a simple Capella export JSON to GeoJSON and optionally post to ArcGIS Online."""
import os
import json
from typing import Dict, Any

from arcgis_client import add_features, get_token

DEFAULT_INPUT = os.getenv("MBSE_EXPORT_PATH", "/git_repo/mbse/exports/sample_capella_export.json")
DEFAULT_OUTPUT = os.getenv("OUTPUT_GEOJSON_PATH", "/git_repo/mbse/exports/output_geojson.json")


def convert(mbse_export_path: str = None, output_geojson_path: str = None) -> Dict[str, Any]:
    mbse_export_path = mbse_export_path or DEFAULT_INPUT
    output_geojson_path = output_geojson_path or DEFAULT_OUTPUT

    with open(mbse_export_path, "r") as f:
        data = json.load(f)

    features = []
    for block in data.get("blocks", []):
        geom = block.get("geometry")
        if not geom:
            continue
        props = block.get("properties", {})
        props.update({
            "mbse_id": block.get("mbse_id"),
            "mbse_type": block.get("type"),
            "mbse_name": block.get("name"),
        })
        # GeoJSON feature
        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": props,
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    os.makedirs(os.path.dirname(output_geojson_path), exist_ok=True)
    with open(output_geojson_path, "w") as f:
        json.dump(geojson, f, indent=2)

    # If ArcGIS environment variables are set, try to push
    arcgis_url = os.getenv("ARCGIS_FEATURE_SERVICE_URL")
    arcgis_user = os.getenv("ARCGIS_USERNAME")
    arcgis_pass = os.getenv("ARCGIS_PASSWORD")

    arcgis_response = None
    if arcgis_url and arcgis_user and arcgis_pass:
        token = get_token(arcgis_user, arcgis_pass)
        # Convert GeoJSON features to ArcGIS feature objects (basic conversion)
        arcgis_features = []
        for f in features:
            geom = f["geometry"]
            attr = f["properties"]
            if geom["type"] == "Point":
                arcgis_geom = {"x": geom["coordinates"][0], "y": geom["coordinates"][1], "spatialReference": {"wkid": 4326}}
            else:
                # polygon -> rings
                arcgis_geom = {"rings": geom["coordinates"], "spatialReference": {"wkid": 4326}}
            arcgis_features.append({"attributes": attr, "geometry": arcgis_geom})

        arcgis_response = add_features(arcgis_url, arcgis_features, token)

    return {"geojson_path": output_geojson_path, "feature_count": len(features), "arcgis_response": arcgis_response}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=DEFAULT_INPUT)
    p.add_argument("--output", default=DEFAULT_OUTPUT)
    args = p.parse_args()
    res = convert(args.input, args.output)
    print(json.dumps(res, indent=2))
