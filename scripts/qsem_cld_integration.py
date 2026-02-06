#!/usr/bin/env python3
"""
QSEM causal loop diagram (CLD) integration.

- Loads GeoJSON
- Builds a CLD network (nodes + causal links)
- Writes CLD JSON (Kumu-compatible) + summary markdown
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def load_geojson(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def compute_factors(geojson: Dict[str, Any]) -> Dict[str, float]:
    features = geojson.get("features", [])
    factors: Dict[str, float] = {}

    for feature in features:
        props = feature.get("properties", {})
        ftype = props.get("type")

        if ftype == "EcologicalZone":
            factors["Biomass Stock"] = float(props.get("biomassStock_tons", 0))
            factors["Fire Risk"] = float(props.get("fireRiskIndex", 0.5))
            factors["Grazable Area"] = float(props.get("grazableArea_ha", props.get("area_ha", 0)))

        if ftype == "PrivateEntity":
            factors["Grazing Intensity"] = float(props.get("grazingIntensity", 0.4))
            factors["Management Capacity"] = float(props.get("managementCapacity", 0.6))
            factors["Economic Resilience"] = float(props.get("revenue_euros", 0))

        if ftype == "PublicEntity":
            factors["Governance Capacity"] = float(props.get("budget_euros", 0))

        if ftype == "CivilSocietyEntity":
            factors["Tourism Pressure"] = float(props.get("memberCount", 0))

        if ftype == "Energy.ProjectSite":
            factors["Suitability"] = float(props.get("suitabilityScore", 0.5))
            factors["Water Requirement"] = float(props.get("requiredFlowRate_m3s", 0.5))

        if ftype == "Municipality":
            factors["Community Governance"] = float(props.get("governanceScore", 0.6))

    return factors


def build_cld(factors: Dict[str, float]) -> Dict[str, Any]:
    timestamp = datetime.utcnow().isoformat() + "Z"

    nodes = []
    for key, value in factors.items():
        nodes.append({
            "id": key.replace(" ", "_"),
            "label": key,
            "value": value,
        })

    links = [
        {"source": "Grazing_Intensity", "target": "Biomass_Stock", "polarity": "-", "rationale": "Grazing reduces biomass"},
        {"source": "Biomass_Stock", "target": "Fire_Risk", "polarity": "+", "rationale": "More biomass increases fuel load"},
        {"source": "Governance_Capacity", "target": "Fire_Risk", "polarity": "-", "rationale": "Better governance reduces fire risk"},
        {"source": "Management_Capacity", "target": "Fire_Risk", "polarity": "-", "rationale": "Improved management reduces risk"},
        {"source": "Tourism_Pressure", "target": "Fire_Risk", "polarity": "+", "rationale": "Higher tourism pressure elevates risk"},
        {"source": "Fire_Risk", "target": "Suitability", "polarity": "-", "rationale": "Risk lowers project suitability"},
        {"source": "Economic_Resilience", "target": "Management_Capacity", "polarity": "+", "rationale": "Revenue supports management"},
        {"source": "Community_Governance", "target": "Management_Capacity", "polarity": "+", "rationale": "Governance improves coordination"},
        {"source": "Water_Requirement", "target": "Suitability", "polarity": "-", "rationale": "Higher requirements reduce feasibility"},
    ]

    # Convert to Kumu-compatible JSON
    elements = []
    for node in nodes:
        elements.append({
            "id": node["id"],
            "label": node["label"],
            "type": "Factor",
            "attributes": {
                "value": node["value"],
            },
        })

    connections = []
    for idx, link in enumerate(links):
        connections.append({
            "id": f"cld_{idx}",
            "from": link["source"],
            "to": link["target"],
            "type": "causal",
            "attributes": {
                "polarity": link["polarity"],
                "rationale": link["rationale"],
            },
        })

    return {
        "metadata": {
            "name": "Monchique QSEM CLD",
            "generated": timestamp,
            "description": "Causal loop diagram derived from GeoJSON factors",
        },
        "elements": elements,
        "connections": connections,
        "rawFactors": factors,
    }


def build_summary_markdown(cld: Dict[str, Any]) -> str:
    lines = [
        "# QSEM Causal Loop Diagram Summary",
        "",
        f"Generated: {cld['metadata']['generated']}",
        "",
        "## Factors",
    ]

    for element in cld.get("elements", []):
        label = element.get("label")
        value = element.get("attributes", {}).get("value")
        lines.append(f"- {label}: {value}")

    lines.extend([
        "",
        "## Links",
    ])

    for connection in cld.get("connections", []):
        polarity = connection.get("attributes", {}).get("polarity")
        rationale = connection.get("attributes", {}).get("rationale")
        lines.append(f"- {connection.get('from')} → {connection.get('to')} ({polarity}): {rationale}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate QSEM CLD from GeoJSON.")
    parser.add_argument(
        "--input",
        type=str,
        default="mbse/exports/monchique_federated_model.geojson",
        help="Input GeoJSON path",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output CLD JSON path (default: qsem/output/cld_network_<timestamp>.json)",
    )
    parser.add_argument(
        "--export",
        type=str,
        default="qsem/exports/cld_network.json",
        help="Canonical export path for remote linking",
    )
    parser.add_argument(
        "--summary",
        type=str,
        default="",
        help="Output summary markdown path (default: qsem/output/cld_summary_<timestamp>.md)",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    input_path = repo_root / args.input

    if not input_path.exists():
        raise FileNotFoundError(f"Input GeoJSON not found: {input_path}")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = repo_root / (args.output or f"qsem/output/cld_network_{timestamp}.json")
    export_path = repo_root / args.export
    summary_path = repo_root / (args.summary or f"qsem/output/cld_summary_{timestamp}.md")

    geojson = load_geojson(input_path)
    factors = compute_factors(geojson)
    cld = build_cld(factors)

    save_json(output_path, cld)
    save_json(export_path, cld)

    summary_text = build_summary_markdown(cld)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as f:
        f.write(summary_text)

    print("✅ QSEM CLD integration complete")
    print(f"📂 Input: {input_path}")
    print(f"🧭 CLD JSON: {output_path}")
    print(f"📌 Canonical export: {export_path}")
    print(f"📝 Summary: {summary_path}")


if __name__ == "__main__":
    main()
