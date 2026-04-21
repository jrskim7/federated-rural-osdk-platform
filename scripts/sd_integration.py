#!/usr/bin/env python3
"""
System Dynamics (SD) integration for the Federated OSDK workflow.

- Loads GeoJSON
- Runs the MonchiqueModel (sd/models/monchique_rural.py) for multi-step simulation
- Falls back to single-step heuristic computation if the model module is unavailable
- Writes updated GeoJSON + SD report

New flags (added during SD GitHub Reference integration, April 2026):
  --scenario       baseline | intervention | pessimistic  (default: baseline)
  --run-length     number of simulation time steps        (default: 1 for legacy compat)
  --model-output   path for model time-series JSON        (optional)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- Attempt to import the native SD model ---------------------------------
_SD_MODEL_AVAILABLE = False
try:
    _repo_root_for_import = Path(__file__).parent.parent
    if str(_repo_root_for_import) not in sys.path:
        sys.path.insert(0, str(_repo_root_for_import))
    from sd.models.monchique_rural import MonchiqueModel, load_params_from_cld  # noqa: E402
    _SD_MODEL_AVAILABLE = True
except ImportError:
    pass


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


def run_model_simulation(
    scenario: str,
    run_length: int,
    cld_path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    Run the MonchiqueModel for multi-step simulation.
    Returns final-step values as a dict, or None if model unavailable.
    Falls back gracefully so legacy heuristic path is unaffected.
    """
    if not _SD_MODEL_AVAILABLE:
        return None

    params = {}
    if cld_path and cld_path.exists():
        try:
            params = load_params_from_cld(cld_path)
        except Exception:
            pass

    model = MonchiqueModel(scenario=scenario, params=params)
    output = model.run(run_length=run_length)

    if isinstance(output, list):
        return output[-1]
    # pandas DataFrame
    return output.iloc[-1].to_dict()


def compute_sd_updates(
    geojson: Dict[str, Any],
    rainfall_index: float,
    model_final: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
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
        "sdModelOutput": model_final or {},
        "featureUpdates": [],
    }

    # If a multi-step model run is available, override heuristic stock values
    if model_final:
        biomass_override = model_final.get("Biomass_Stock")
        fire_override = model_final.get("Fire_Risk")
        suitability_override = model_final.get("Suitability")
    else:
        biomass_override = fire_override = suitability_override = None

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

            # Prefer multi-step model outputs when available
            if biomass_override is not None:
                biomass_next = biomass_override
            if fire_override is not None:
                fire_risk_next = fire_override

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

            if suitability_override is not None:
                suitability_next = suitability_override

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
    parser.add_argument(
        "--scenario",
        type=str,
        default="baseline",
        choices=["baseline", "intervention", "pessimistic"],
        help="Scenario preset for MonchiqueModel",
    )
    parser.add_argument(
        "--run-length",
        type=int,
        default=1,
        help="Number of simulation time steps for MonchiqueModel (1 = legacy single-step)",
    )
    parser.add_argument(
        "--model-output",
        type=str,
        default="",
        help="Optional path to write MonchiqueModel time-series JSON",
    )
    parser.add_argument(
        "--cld",
        type=str,
        default="qsem/exports/cld_network.json",
        help="QSEM CLD JSON used to seed model parameters",
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

    # Run multi-step model if available
    cld_path = repo_root / args.cld
    model_final = run_model_simulation(
        scenario=args.scenario,
        run_length=args.run_length,
        cld_path=cld_path,
    )

    # Optionally write model time-series
    if model_final and args.model_output:
        model_ts_path = repo_root / args.model_output
        model_ts_path.parent.mkdir(parents=True, exist_ok=True)
        # Re-run to get full trajectory
        if _SD_MODEL_AVAILABLE:
            m = MonchiqueModel(scenario=args.scenario)
            ts = m.run(run_length=args.run_length)
            model_ts_path.parent.mkdir(parents=True, exist_ok=True)
            with model_ts_path.open("w", encoding="utf-8") as f:
                if isinstance(ts, list):
                    json.dump(ts, f, indent=2)
                else:
                    json.dump(ts.reset_index().to_dict("records"), f, indent=2)

    sd_report = compute_sd_updates(geojson, rainfall_index=args.rainfall_index, model_final=model_final)

    save_geojson(output_path, geojson)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(sd_report, f, indent=2)

    print("✅ System Dynamics integration complete")
    print(f"📂 Input: {input_path}")
    print(f"🗺️  Updated GeoJSON: {output_path}")
    print(f"📄 Report: {report_path}")
    if model_final:
        print(f"🔬 Scenario: {args.scenario} | Run length: {args.run_length} steps | MonchiqueModel active")
    else:
        print("⚠️  MonchiqueModel not available — legacy heuristic mode used")


if __name__ == "__main__":
    main()
