#!/usr/bin/env python3
"""
System Dynamics (SD) integration for the Federated OSDK workflow.

- Loads GeoJSON
- Runs a simple stock/flow update for biomass, grazing, fire risk
- Estimates water availability and suitability for micro-hydro
- Writes updated GeoJSON + SD report
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


def save_geojson(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_lookup(features: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for feature in features:
        feature_id = feature.get("id")
        if feature_id:
            lookup[feature_id] = feature
    return lookup


def get_first_by_type(features: List[Dict[str, Any]], feature_type: str) -> Dict[str, Any]:
    for feature in features:
        props = feature.get("properties", {})
        if props.get("type") == feature_type:
            return feature
    return {}


def compute_sd_updates(geojson: Dict[str, Any], rainfall_index: float) -> Dict[str, Any]:
    features = geojson.get("features", [])
    lookup = build_lookup(features)

    municipality = get_first_by_type(features, "Municipality")
    coop = lookup.get("Coop_Algarve", {}) or get_first_by_type(features, "PrivateEntity")
    council = lookup.get("Mun_Camara", {}) or get_first_by_type(features, "PublicEntity")
    tourism = lookup.get("Tourism_Group_B", {}) or get_first_by_type(features, "CivilSocietyEntity")
    project = get_first_by_type(features, "Energy.ProjectSite")

    muni_props = municipality.get("properties", {})
    coop_props = coop.get("properties", {})
    council_props = council.get("properties", {})
    tourism_props = tourism.get("properties", {})
    project_props = project.get("properties", {})

    governance_score = float(muni_props.get("governanceScore", 0.6))
    management_capacity = float(coop_props.get("managementCapacity", 0.6))
    grazing_intensity = float(coop_props.get("grazingIntensity", 0.4))
    member_count = float(coop_props.get("memberCount", 30))
    council_budget = float(council_props.get("budget_euros", 0))
    tourism_members = float(tourism_props.get("memberCount", 0))

    community_support = clamp(
        0.3
        + 0.4 * management_capacity
        + 0.2 * governance_score
        + 0.00000002 * council_budget
    )

    sd_report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rainfallIndex": rainfall_index,
        "communitySupportIndex": community_support,
        "featureUpdates": [],
    }

    for feature in features:
        props = feature.get("properties", {})
        if props.get("type") == "EcologicalZone":
            biomass = float(props.get("biomassStock_tons", 0))
            fire_risk = float(props.get("fireRiskIndex", 0.5))
            grazable_area = float(props.get("grazableArea_ha", props.get("area_ha", 0)))

            growth_rate = clamp(0.04 + 0.03 * governance_score)
            grazing_pressure = clamp(grazing_intensity * (member_count / 50.0))

            biomass_growth = biomass * growth_rate
            biomass_grazing = biomass * grazing_pressure * 0.03
            biomass_fire_loss = biomass * fire_risk * 0.015
            biomass_next = max(0.0, biomass + biomass_growth - biomass_grazing - biomass_fire_loss)

            fire_risk_next = clamp(
                fire_risk
                + 0.15 * grazing_pressure
                + 0.10 * (tourism_members / 50.0)
                - 0.20 * governance_score
                - 0.10 * management_capacity
            )

            grazing_capacity = grazable_area * 0.6

            props["sd_biomassStock_tons"] = round(biomass_next, 2)
            props["sd_fireRiskIndex"] = round(fire_risk_next, 3)
            props["sd_grazingCapacity_tons"] = round(grazing_capacity, 2)
            props["sd_timestamp"] = sd_report["timestamp"]

            sd_report["featureUpdates"].append({
                "id": feature.get("id"),
                "type": props.get("type"),
                "biomassNext": biomass_next,
                "fireRiskNext": fire_risk_next,
                "grazingCapacity": grazing_capacity,
            })

        if props.get("type") == "Energy.ProjectSite":
            required_flow = float(props.get("requiredFlowRate_m3s", 0.5))
            water_availability = clamp(
                0.2
                + 0.5 * rainfall_index
                + 0.2 * governance_score
                + 0.1 * (1.0 - required_flow)
            )

            suitability = float(props.get("suitabilityScore", 0.5))
            suitability_next = clamp(
                suitability
                + 0.2 * (water_availability - required_flow)
                + 0.15 * community_support
            )

            props["sd_waterAvailability_m3s"] = round(water_availability, 3)
            props["sd_suitabilityScore"] = round(suitability_next, 3)
            props["sd_timestamp"] = sd_report["timestamp"]

            sd_report["featureUpdates"].append({
                "id": feature.get("id"),
                "type": props.get("type"),
                "waterAvailability": water_availability,
                "suitabilityNext": suitability_next,
            })

    return sd_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run System Dynamics integration on GeoJSON.")
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
        help="Output GeoJSON path (default: mbse/exports/monchique_federated_model_sd_<timestamp>.geojson)",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="",
        help="Output report JSON path (default: sd/output/sd_report_<timestamp>.json)",
    )
    parser.add_argument(
        "--rainfall-index",
        type=float,
        default=0.6,
        help="Rainfall index (0-1) used in water availability estimate",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    input_path = repo_root / args.input

    if not input_path.exists():
        raise FileNotFoundError(f"Input GeoJSON not found: {input_path}")

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = repo_root / (args.output or f"mbse/exports/monchique_federated_model_sd_{timestamp}.geojson")
    report_path = repo_root / (args.report or f"sd/output/sd_report_{timestamp}.json")

    geojson = load_geojson(input_path)
    sd_report = compute_sd_updates(geojson, rainfall_index=args.rainfall_index)

    save_geojson(output_path, geojson)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(sd_report, f, indent=2)

    print("✅ System Dynamics integration complete")
    print(f"📂 Input: {input_path}")
    print(f"🗺️  Updated GeoJSON: {output_path}")
    print(f"📄 Report: {report_path}")


if __name__ == "__main__":
    main()
