#!/usr/bin/env python3
"""
fetch_cadastro.py
=================
Generic cadastral data fetcher for the Federated Rural OSDK Platform.
Uses gis_cadastre_registry.json to auto-configure endpoints per country.

Supports:
  - OGC API Features (modern REST)
  - WFS 2.0 (classic OGC)
  - Direct URL download (bulk GeoJSON/shapefile)

Usage:
  python fetch_cadastro.py --country PT --bbox "-8.65,37.20,-8.45,37.38"
  python fetch_cadastro.py --country ES --bbox "-3.72,40.40,-3.62,40.47"
  python fetch_cadastro.py --country BR --bbox "-43.2,-22.95,-43.1,-22.85"
  python fetch_cadastro.py --country PT --bbox "-8.65,37.20,-8.45,37.38" --output data/monchique.geojson

Author: JRBD / Conscious Circle
"""

import json
import time
import argparse
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install requests: pip install requests --break-system-packages")
    sys.exit(1)

REGISTRY_PATH = Path(__file__).parent / "gis_cadastre_registry.json"
DEFAULT_OUTPUT = Path("mbse/exports/cadastro_{country}_{timestamp}.geojson")
PAGE_LIMIT = 100


def load_registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_country_config(registry: dict, iso: str) -> dict:
    iso = iso.upper()
    for region in registry["regions"].values():
        if "countries" in region and iso in region["countries"]:
            return region["countries"][iso]
    return None


def fetch_ogc_api(base_url: str, collection: str, bbox: str,
                  limit: int = PAGE_LIMIT, api_key: str = None,
                  max_pages: int = None) -> list:
    """Fetch features from OGC API Features endpoint with pagination."""
    all_features = []
    offset = 0
    page = 1
    url = f"{base_url.rstrip('/')}/collections/{collection}/items"

    while True:
        params = {"f": "json", "bbox": bbox, "limit": limit, "offset": offset}
        if api_key:
            params["api_key"] = api_key
        headers = {}

        print(f"  [OGC API] Page {page} (offset={offset}, url={url})")
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(f"  HTTP {resp.status_code}: {e}")
            if resp.status_code == 401:
                print("  -> This source requires authentication. See registry for docs.")
            break
        except requests.RequestException as e:
            print(f"  Request error: {e}")
            break

        data = resp.json()
        features = data.get("features", [])
        all_features.extend(features)

        matched = data.get("numberMatched", "?")
        print(f"  Got {len(features)} features (total matched: {matched})")

        if max_pages is not None and page >= max_pages:
            break

        links = data.get("links", [])
        next_link = next((l["href"] for l in links if l.get("rel") == "next"), None)
        if not next_link or len(features) < limit:
            break

        offset += limit
        page += 1
        time.sleep(0.3)

    return all_features


def fetch_wfs(base_url: str, layer: str, bbox: str,
              crs: str = "EPSG:4326", limit: int = PAGE_LIMIT,
              max_pages: int = None) -> list:
    """Fetch features from WFS 2.0 endpoint."""
    all_features = []
    start_index = 0
    page = 1

    while True:
        params = {
            "SERVICE": "WFS",
            "VERSION": "2.0.0",
            "REQUEST": "GetFeature",
            "TYPENAMES": layer,
            "SRSNAME": crs,
            "BBOX": bbox,
            "outputFormat": "application/json",
            "count": limit,
            "startIndex": start_index,
        }

        print(f"  [WFS] startIndex={start_index}")
        try:
            resp = requests.get(base_url, params=params, timeout=45)
            resp.raise_for_status()
        except requests.HTTPError as e:
            print(f"  HTTP {resp.status_code}: {e}")
            if resp.status_code in [401, 403]:
                print("  -> Authentication required. Check registry docs.")
            break
        except requests.RequestException as e:
            print(f"  Request error: {e}")
            break

        try:
            data = resp.json()
        except json.JSONDecodeError:
            print(f"  Non-JSON response (may be WMS tile server or auth wall).")
            print(f"  Response preview: {resp.text[:300]}")
            break

        features = data.get("features", [])
        all_features.extend(features)
        print(f"  Got {len(features)} features")

        if max_pages is not None and page >= max_pages:
            break

        if len(features) < limit:
            break
        start_index += limit
        page += 1
        time.sleep(0.3)

    return all_features


def write_geojson(features: list, output_path: Path, attribution: str, iso: str):
    geojson = {
        "type": "FeatureCollection",
        "name": f"cadastro_{iso.lower()}",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "attribution": attribution,
        "feature_count": len(features),
        "features": features,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Wrote {len(features)} features -> {output_path}")


def inspect_first_feature(features: list):
    if not features:
        print("  No features returned.")
        return
    feat = features[0]
    geom_type = feat.get("geometry", {}).get("type", "?")
    props = feat.get("properties", {})
    print(f"\n  Sample feature:")
    print(f"  Geometry type: {geom_type}")
    print(f"  Properties ({len(props)}):")
    for k, v in list(props.items())[:12]:
        print(f"    {k}: {v}")
    if len(props) > 12:
        print(f"    ... and {len(props)-12} more")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch cadastral parcel data for any country using the OSDK registry"
    )
    parser.add_argument("--country", "-c", required=True, help="ISO-2 country code")
    parser.add_argument(
        "--bbox", "-b", required=True,
        help="Bounding box: lon_min,lat_min,lon_max,lat_max (WGS84)"
    )
    parser.add_argument("--output", "-o", help="Output GeoJSON path")
    parser.add_argument("--api-key", "-k", help="API key if required")
    parser.add_argument("--limit", type=int, default=PAGE_LIMIT, help="Features per page")
    parser.add_argument("--inspect-only", action="store_true",
                        help="Fetch 1 feature and inspect schema only")
    args = parser.parse_args()

    iso = args.country.upper()
    registry = load_registry()
    country_data = get_country_config(registry, iso)

    if not country_data:
        print(f"Country not found in registry: {iso}")
        print("Run: python query_cadastre_registry.py --list")
        sys.exit(1)

    ps = country_data.get("primary_source", {})
    src_type = ps.get("type", "unknown")
    access = ps.get("access", "unknown")
    base_url = ps.get("base_url") or ps.get("wfs_url") or ""
    collection = ps.get("collection") or ps.get("layer") or ""
    attribution = ps.get("attribution", f"Source: {ps.get('name', iso)}")
    crs = ps.get("crs", "EPSG:4326")

    print(f"\n{'='*60}")
    print(f"  Fetching: {country_data.get('name', iso)} ({iso})")
    print(f"  Source:   {ps.get('name', '?')}")
    print(f"  Type:     {src_type}  |  Access: {access}")
    print(f"  BBOX:     {args.bbox}")
    print(f"{'='*60}\n")

    if access in ("restricted", "commercial"):
        print(f"  Warning: This source is '{access}'. You may need credentials or a licence.")
        print(f"  Docs: {ps.get('docs', 'see registry')}\n")
        cont = input("  Continue anyway? (y/N): ").strip().lower()
        if cont != "y":
            sys.exit(0)

    if access == "manual":
        print("  This country has no public API.")
        print(f"  Notes: {ps.get('notes', '')}")
        print(f"  Docs:  {ps.get('docs', '')}")
        print("\n  Alternatives:")
        for alt in country_data.get("secondary_sources", []):
            print(f"    - {alt.get('name')} -- {alt.get('url') or alt.get('base_url','')}")
        sys.exit(1)

    if args.inspect_only:
        args.limit = 1

    features = []
    if "ogc_api" in src_type:
        features = fetch_ogc_api(
            base_url,
            collection,
            args.bbox,
            limit=args.limit,
            api_key=args.api_key,
            max_pages=1 if args.inspect_only else None,
        )
    elif "wfs" in src_type:
        features = fetch_wfs(
            base_url,
            collection,
            args.bbox,
            crs=crs,
            limit=args.limit,
            max_pages=1 if args.inspect_only else None,
        )
    else:
        print(f"  Source type '{src_type}' requires manual download.")
        print(f"  See: {ps.get('docs', '')}")
        sys.exit(1)

    if args.inspect_only:
        inspect_first_feature(features)
        return

    if not features:
        print("\n  No features returned. Possible causes:")
        print("  - BBOX outside coverage area")
        print("  - Authentication required (check registry docs)")
        print("  - Collection name changed (check endpoint manually)")
        print(f"  Test URL: {ps.get('test_url', 'N/A')}")
        sys.exit(1)

    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path(f"mbse/exports/cadastro_{iso.lower()}_{ts}.geojson")

    write_geojson(features, output_path, attribution, iso)
    inspect_first_feature(features)

    print(f"\n  Attribution required: {attribution}")
    print(f"  License: {ps.get('license', 'see registry')}")


if __name__ == "__main__":
    main()
