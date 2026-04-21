#!/usr/bin/env python3
"""
SD Sensitivity Analysis (sd/analysis/sensitivity.py)
=====================================================
One-at-a-time (OAT) and scenario-comparison sensitivity analysis
for the MonchiqueModel.

Outputs:
  - sensitivity_report_<timestamp>.json  in sd/output/
  - Prints a ranked table of parameter influence on key output variables

Usage:
    python sd/analysis/sensitivity.py
    python sd/analysis/sensitivity.py --run-length 50 --sweep-steps 11
    python sd/analysis/sensitivity.py --output sd/output/custom_sensitivity.json
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add repo root to path so the model can be imported regardless of cwd
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sd.models.monchique_rural import MonchiqueModel, DEFAULTS


# Parameters to sweep and their plausible [min, max] ranges
SWEEP_PARAMS: Dict[str, tuple] = {
    "Community_Governance": (0.2, 1.0),
    "Grazing_Intensity": (0.1, 0.9),
    "Tourism_Pressure": (5.0, 80.0),
    "Governance_Capacity": (500_000.0, 6_000_000.0),
    "Economic_Resilience": (50_000.0, 500_000.0),
    "Water_Requirement": (0.2, 0.9),
}

# Output variables to track at end of run
OUTPUT_VARS = ["Biomass_Stock", "Fire_Risk", "Management_Capacity", "Suitability"]


def _linspace(lo: float, hi: float, steps: int) -> List[float]:
    if steps <= 1:
        return [(lo + hi) / 2]
    step = (hi - lo) / (steps - 1)
    return [lo + i * step for i in range(steps)]


def run_oat_sweep(run_length: int = 50, sweep_steps: int = 9) -> Dict[str, Any]:
    """
    One-at-a-time sensitivity: vary each parameter across its range while
    holding all others at their default value.

    Returns a dict of results keyed by parameter name.
    """
    results: Dict[str, Any] = {}

    for param, (lo, hi) in SWEEP_PARAMS.items():
        values = _linspace(lo, hi, sweep_steps)
        param_results = []

        for val in values:
            model = MonchiqueModel(params={param: val})
            output = model.run(run_length=run_length)

            if isinstance(output, list):
                last = output[-1]
            else:
                last = output.iloc[-1].to_dict()

            param_results.append({
                "param_value": round(val, 4),
                **{k: round(last[k], 4) for k in OUTPUT_VARS if k in last},
            })

        # Compute range (max - min) for each output as influence metric
        influence = {}
        for var in OUTPUT_VARS:
            vals = [r[var] for r in param_results if var in r]
            if vals:
                influence[var] = round(max(vals) - min(vals), 4)

        results[param] = {
            "sweep": param_results,
            "influence": influence,
        }

    return results


def run_scenario_comparison(run_length: int = 50) -> Dict[str, Any]:
    """
    Compare baseline, intervention, and pessimistic scenario trajectories.
    Returns final-step outputs per scenario.
    """
    comparison: Dict[str, Any] = {}
    for scenario in ("baseline", "intervention", "pessimistic"):
        model = MonchiqueModel(scenario=scenario)
        output = model.run(run_length=run_length)

        if isinstance(output, list):
            final = output[-1]
            trajectory = output
        else:
            final = output.iloc[-1].to_dict()
            trajectory = [
                {k: round(v, 4) for k, v in row.items()}
                for row in output.reset_index().to_dict("records")
            ]

        comparison[scenario] = {
            "final": {k: round(final[k], 4) for k in OUTPUT_VARS if k in final},
            "trajectory": trajectory,
        }

    return comparison


def rank_parameters(oat_results: Dict[str, Any], target_var: str = "Fire_Risk") -> List[Dict]:
    """Rank parameters by their influence on `target_var`."""
    ranked = []
    for param, data in oat_results.items():
        influence = data["influence"].get(target_var, 0.0)
        ranked.append({"parameter": param, "influence_on_" + target_var: influence})
    ranked.sort(key=lambda x: list(x.values())[1], reverse=True)
    return ranked


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SD sensitivity analysis.")
    parser.add_argument("--run-length", type=int, default=50)
    parser.add_argument("--sweep-steps", type=int, default=9)
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    root = Path(__file__).parent.parent.parent

    print("⏳ Running OAT sensitivity sweep…")
    oat = run_oat_sweep(run_length=args.run_length, sweep_steps=args.sweep_steps)

    print("⏳ Running scenario comparison…")
    scenarios = run_scenario_comparison(run_length=args.run_length)

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "config": {
            "run_length": args.run_length,
            "sweep_steps": args.sweep_steps,
            "swept_parameters": list(SWEEP_PARAMS.keys()),
            "output_variables": OUTPUT_VARS,
        },
        "oat_sensitivity": oat,
        "scenario_comparison": scenarios,
        "parameter_rankings": {
            var: rank_parameters(oat, target_var=var)
            for var in OUTPUT_VARS
        },
    }

    out_path = root / (args.output or f"sd/output/sensitivity_report_{timestamp}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Sensitivity report written to: {out_path}")
    print("\nParameter rankings by influence on Fire_Risk:")
    for row in report["parameter_rankings"]["Fire_Risk"]:
        param = row["parameter"]
        influence = row.get("influence_on_Fire_Risk", 0)
        print(f"  {param:<35} Δ={influence:.4f}")

    print("\nScenario comparison (final step):")
    for scenario, data in scenarios.items():
        final = data["final"]
        print(f"  {scenario:<15} Biomass={final.get('Biomass_Stock','?'):>8}  "
              f"FireRisk={final.get('Fire_Risk','?'):.3f}  "
              f"Suitability={final.get('Suitability','?'):.3f}")


if __name__ == "__main__":
    main()
