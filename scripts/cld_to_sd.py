#!/usr/bin/env python3
"""
CLD → SD Bridge (cld_to_sd.py)
================================
Reads a QSEM CLD JSON (qsem/exports/cld_network.json) and scaffolds:
  1. A stock/flow skeleton dict describing stocks, flows, and auxiliaries
  2. An initial-conditions JSON for sd/data/initial_conditions.json
  3. A parameters JSON for sd/data/parameters.json

This closes the gap identified in the SD integration guide:
  "There is currently no automated pathway from CLD polarity structure
   → pysd-compatible model equations."

The scaffold does NOT generate full differential equation syntax — that
requires domain knowledge. It does produce a structured skeleton that maps
directly to sd/models/monchique_rural.py and can serve as a pysd .xmile
authoring template.

Classification heuristics (from CLD polarity and label):
  Stock  : node that is the TARGET of at least one (+) accumulating edge
           and whose label contains a mass/stock keyword (Biomass, Stock,
           Capacity, Pressure, Risk, Resilience)
  Flow   : directed edge between two nodes
  Auxiliary: node that is purely computed — neither a pure accumulator
             nor a pure driver constant

Usage:
    python scripts/cld_to_sd.py \
        --cld qsem/exports/cld_network.json \
        --output-skeleton sd/data/sd_skeleton.json \
        --output-ic sd/data/initial_conditions.json \
        --output-params sd/data/parameters.json
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

# Keywords that suggest a node is a stock (accumulator)
_STOCK_KEYWORDS = {"stock", "biomass", "capacity", "risk", "resilience", "pressure", "reserve"}

# Keywords that suggest a node is a constant parameter rather than a stock
_PARAM_KEYWORDS = {"requirement", "intensity", "area", "pressure", "governance"}


def _is_likely_stock(label: str, in_degree: int, out_degree: int) -> bool:
    lower = label.lower()
    has_keyword = any(k in lower for k in _STOCK_KEYWORDS)
    is_accumulator = in_degree >= 1 and out_degree >= 1
    return has_keyword and is_accumulator


def _is_likely_param(label: str, in_degree: int) -> bool:
    lower = label.lower()
    has_keyword = any(k in lower for k in _PARAM_KEYWORDS)
    return has_keyword and in_degree == 0


def build_skeleton(cld: Dict[str, Any]) -> Dict[str, Any]:
    """
    Derive SD skeleton from CLD elements and connections.
    Returns a dict with keys: stocks, flows, auxiliaries, parameters.
    """
    elements: List[Dict] = cld.get("elements", [])
    connections: List[Dict] = cld.get("connections", [])

    # Build degree maps
    in_deg: Dict[str, int] = {e["id"]: 0 for e in elements}
    out_deg: Dict[str, int] = {e["id"]: 0 for e in elements}
    for conn in connections:
        src = conn.get("from", conn.get("source"))
        tgt = conn.get("to", conn.get("target"))
        if src in out_deg:
            out_deg[src] += 1
        if tgt in in_deg:
            in_deg[tgt] += 1

    stocks: List[Dict] = []
    auxiliaries: List[Dict] = []
    parameters: List[Dict] = []

    for elem in elements:
        eid = elem["id"]
        label = elem.get("label", eid)
        initial = elem.get("attributes", {}).get("value", 0.0)
        ind = in_deg.get(eid, 0)
        outd = out_deg.get(eid, 0)

        if _is_likely_stock(label, ind, outd):
            stocks.append({
                "id": eid,
                "label": label,
                "initial_value": initial,
                "unit": "tbd",
                "note": "Derived as stock: accumulating node with qualifying label",
            })
        elif _is_likely_param(label, ind):
            parameters.append({
                "id": eid,
                "label": label,
                "value": initial,
                "unit": "tbd",
                "note": "Derived as parameter: exogenous driver with no incoming links",
            })
        else:
            auxiliaries.append({
                "id": eid,
                "label": label,
                "initial_value": initial,
                "note": "Derived as auxiliary: computed variable",
            })

    flows: List[Dict] = []
    for conn in connections:
        src = conn.get("from", conn.get("source"))
        tgt = conn.get("to", conn.get("target"))
        polarity = conn.get("attributes", {}).get("polarity", conn.get("polarity", "?"))
        rationale = conn.get("attributes", {}).get("rationale", "")
        flows.append({
            "id": conn.get("id", f"{src}_to_{tgt}"),
            "source": src,
            "target": tgt,
            "polarity": polarity,
            "rationale": rationale,
            "note": f"Flow {'increases' if polarity == '+' else 'decreases'} {tgt}",
        })

    return {
        "metadata": {
            "source_cld": cld.get("metadata", {}).get("name", "unknown"),
            "generated": cld.get("metadata", {}).get("generated", "unknown"),
            "note": (
                "Auto-generated SD skeleton from QSEM CLD. "
                "Review stock/auxiliary classification before building equations."
            ),
        },
        "stocks": stocks,
        "flows": flows,
        "auxiliaries": auxiliaries,
        "parameters": parameters,
    }


def build_initial_conditions(skeleton: Dict[str, Any]) -> Dict[str, float]:
    ic: Dict[str, float] = {}
    for s in skeleton["stocks"]:
        ic[s["id"]] = s["initial_value"]
    for a in skeleton["auxiliaries"]:
        ic[a["id"]] = a.get("initial_value", 0.0)
    return ic


def build_parameters(skeleton: Dict[str, Any]) -> Dict[str, float]:
    return {p["id"]: p["value"] for p in skeleton["parameters"]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert QSEM CLD JSON to SD skeleton.")
    parser.add_argument(
        "--cld",
        default="qsem/exports/cld_network.json",
        help="Path to QSEM CLD JSON",
    )
    parser.add_argument(
        "--output-skeleton",
        default="sd/data/sd_skeleton.json",
        help="Output path for SD skeleton JSON",
    )
    parser.add_argument(
        "--output-ic",
        default="sd/data/initial_conditions.json",
        help="Output path for initial conditions JSON",
    )
    parser.add_argument(
        "--output-params",
        default="sd/data/parameters.json",
        help="Output path for parameters JSON",
    )

    args = parser.parse_args()
    root = Path(__file__).parent.parent

    cld_path = root / args.cld
    if not cld_path.exists():
        raise FileNotFoundError(f"CLD not found: {cld_path}")

    with cld_path.open("r", encoding="utf-8") as f:
        cld = json.load(f)

    skeleton = build_skeleton(cld)
    ic = build_initial_conditions(skeleton)
    params = build_parameters(skeleton)

    def _save(path: Path, data: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  ✅ {path}")

    _save(root / args.output_skeleton, skeleton)
    _save(root / args.output_ic, ic)
    _save(root / args.output_params, params)

    print(f"\nSkeleton summary:")
    print(f"  Stocks      : {len(skeleton['stocks'])}")
    print(f"  Flows       : {len(skeleton['flows'])}")
    print(f"  Auxiliaries : {len(skeleton['auxiliaries'])}")
    print(f"  Parameters  : {len(skeleton['parameters'])}")


if __name__ == "__main__":
    main()
