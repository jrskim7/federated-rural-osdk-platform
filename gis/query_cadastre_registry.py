#!/usr/bin/env python3
"""
query_cadastre_registry.py
==========================
Interactive CLI query tool for the Global Cadastral Data Registry.
Part of the Federated Rural OSDK Platform — GIS Data Acquisition Module.

Usage:
  python query_cadastre_registry.py                    # interactive menu
  python query_cadastre_registry.py --country PT       # single country lookup
  python query_cadastre_registry.py --region europe_western
  python query_cadastre_registry.py --access open      # filter by access tier
  python query_cadastre_registry.py --list             # list all countries
  python query_cadastre_registry.py --export PT        # export fetch config for country
  python query_cadastre_registry.py --global-fallbacks # show global fallback sources

Author: JRBD / Conscious Circle
"""

import json
import argparse
import sys
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent / "gis_cadastre_registry.json"


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        print(f"ERROR: Registry not found at {REGISTRY_PATH}")
        sys.exit(1)
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def get_all_countries(registry: dict) -> dict:
    """Return flat dict of {ISO2: {country_data, region_label}}."""
    result = {}
    for region_key, region in registry["regions"].items():
        label = region.get("label", region_key)
        if "countries" not in region:
            continue
        for iso, data in region["countries"].items():
            result[iso] = {**data, "_region": label, "_region_key": region_key}
    return result


def print_country(iso: str, data: dict, verbose: bool = True):
    """Pretty-print a country entry."""
    name = data.get("name", iso)
    region = data.get("_region", "")
    print(f"\n{'='*60}")
    print(f"  {iso} — {name}  [{region}]")
    print(f"{'='*60}")

    ps = data.get("primary_source", {})
    if ps:
        print(f"\n  PRIMARY SOURCE: {ps.get('name', 'N/A')}")
        print(f"  Type:           {ps.get('type', 'N/A')}")
        print(f"  Access:         {ps.get('access', 'N/A')}")
        license_val = ps.get('license', '')
        if license_val:
            print(f"  License:        {license_val}")
        base_url = ps.get('base_url') or ps.get('wfs_url') or ps.get('api_url') or ''
        if base_url:
            print(f"  Base URL:       {base_url}")
        collection = ps.get('collection') or ps.get('layer') or ''
        if collection:
            print(f"  Collection:     {collection}")
        test_url = ps.get('test_url', '')
        if test_url:
            print(f"  Test URL:       {test_url}")
        notes = ps.get('notes', '')
        if notes:
            print(f"  Notes:          {notes}")
        docs = ps.get('docs', '')
        if docs:
            print(f"  Docs:           {docs}")

    if verbose:
        secondary = data.get("secondary_sources", [])
        if secondary:
            print(f"\n  SECONDARY SOURCES ({len(secondary)}):")
            for s in secondary:
                print(f"    • {s.get('name', '?')} [{s.get('access', '?')}]")
                if s.get('url') or s.get('base_url'):
                    print(f"      {s.get('url') or s.get('base_url', '')}")

        bbox = data.get("bbox_country", "")
        if bbox:
            print(f"\n  Country BBOX:  {bbox}")

        inspire = data.get("inspire_node", "")
        if inspire:
            print(f"  INSPIRE Node:  {inspire}")

        extra_notes = data.get("notes", "")
        if extra_notes:
            print(f"  Notes:         {extra_notes}")


def export_fetch_config(iso: str, data: dict) -> dict:
    """Generate a machine-readable fetch config for fetch_cadastro.py."""
    ps = data.get("primary_source", {})
    config = {
        "country_iso": iso,
        "country_name": data.get("name", iso),
        "access_tier": ps.get("access", "unknown"),
        "source_type": ps.get("type", "unknown"),
        "base_url": ps.get("base_url") or ps.get("wfs_url") or ps.get("api_url") or "",
        "collection": ps.get("collection") or ps.get("layer") or "",
        "crs": ps.get("crs", "EPSG:4326"),
        "bbox_country": data.get("bbox_country", ""),
        "attribution": ps.get("attribution", f"Source: {ps.get('name', '')}"),
        "license": ps.get("license", "unknown"),
        "docs": ps.get("docs", ""),
        "notes": ps.get("notes", ""),
    }
    return config


def list_all(registry: dict, access_filter: str = None):
    """Print a table of all countries."""
    countries = get_all_countries(registry)
    print(f"\n{'ISO':<6} {'Country':<25} {'Region':<22} {'Access':<20} {'Type'}")
    print("-" * 95)
    for iso in sorted(countries.keys()):
        data = countries[iso]
        ps = data.get("primary_source", {})
        access = ps.get("access", "?")
        src_type = ps.get("type", "?")
        if access_filter and access != access_filter:
            continue
        print(f"{iso:<6} {data.get('name',''):<25} {data.get('_region',''):<22} {access:<20} {src_type}")
    print(f"\nTotal: {len(countries)} countries")


def show_global_fallbacks(registry: dict):
    """Print global fallback sources."""
    fb = registry["regions"].get("global_fallbacks", {})
    sources = fb.get("sources", [])
    print(f"\n{'='*60}")
    print("  GLOBAL FALLBACK SOURCES")
    print(f"{'='*60}")
    print(f"  {fb.get('description', '')}")
    print()
    for s in sources:
        print(f"  • {s['name']}")
        print(f"    Access: {s['access']}  |  Type: {s['type']}")
        url = s.get('url') or s.get('endpoint') or ''
        if url:
            print(f"    URL:    {url}")
        print(f"    Notes:  {s.get('notes', '')}")
        print()


def interactive_menu(registry: dict):
    """Simple interactive menu."""
    countries = get_all_countries(registry)
    while True:
        print("\n=== Global Cadastral Registry ===")
        print("1. Lookup country by ISO code")
        print("2. List all countries")
        print("3. Filter by access tier (open / open_registration / restricted / commercial / manual)")
        print("4. Show global fallback sources")
        print("5. Export fetch config for country")
        print("6. Exit")
        choice = input("\nChoice: ").strip()

        if choice == "1":
            iso = input("ISO-2 code (e.g. PT, ES, BR): ").strip().upper()
            if iso in countries:
                print_country(iso, countries[iso])
            else:
                print(f"  Not found: {iso}. Use --list to see all codes.")

        elif choice == "2":
            list_all(registry)

        elif choice == "3":
            tier = input("Access tier: ").strip()
            list_all(registry, access_filter=tier)

        elif choice == "4":
            show_global_fallbacks(registry)

        elif choice == "5":
            iso = input("ISO-2 code: ").strip().upper()
            if iso in countries:
                config = export_fetch_config(iso, countries[iso])
                print(json.dumps(config, indent=2, ensure_ascii=False))
            else:
                print(f"  Not found: {iso}")

        elif choice == "6":
            break


def main():
    parser = argparse.ArgumentParser(
        description="Query the Global Cadastral Data Registry for OSDK GIS workflows"
    )
    parser.add_argument("--country", "-c", help="ISO-2 country code (e.g. PT)")
    parser.add_argument("--region", "-r", help="Region key (e.g. europe_western)")
    parser.add_argument("--access", "-a", help="Filter by access tier")
    parser.add_argument("--list", "-l", action="store_true", help="List all countries")
    parser.add_argument("--export", "-e", help="Export fetch config for ISO-2 country")
    parser.add_argument("--global-fallbacks", "-g", action="store_true")
    args = parser.parse_args()

    registry = load_registry()
    countries = get_all_countries(registry)

    if args.country:
        iso = args.country.upper()
        if iso in countries:
            print_country(iso, countries[iso])
        else:
            print(f"Not found: {iso}")
            sys.exit(1)

    elif args.region:
        region = registry["regions"].get(args.region)
        if not region:
            print(f"Region not found: {args.region}")
            sys.exit(1)
        for iso, data in region.get("countries", {}).items():
            data["_region"] = region.get("label", args.region)
            print_country(iso, data, verbose=False)

    elif args.list or args.access:
        list_all(registry, access_filter=args.access)

    elif args.export:
        iso = args.export.upper()
        if iso in countries:
            config = export_fetch_config(iso, countries[iso])
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print(f"Not found: {iso}")
            sys.exit(1)

    elif args.global_fallbacks:
        show_global_fallbacks(registry)

    else:
        interactive_menu(registry)


if __name__ == "__main__":
    main()
