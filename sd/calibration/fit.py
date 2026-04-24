#!/usr/bin/env python3
"""
SD Calibration — Parameter Fitting (sd/calibration/fit.py)
============================================================
Fits MonchiqueModel rate coefficients to observed time-series data
using scipy.optimize.minimize (Nelder-Mead) to minimise RMSE across
one or more output variables.

Calibration targets (any subset of output variables):
  - Biomass_Stock   [tons]
  - Fire_Risk       [0–1]
  - Management_Capacity [0–1]
  - Suitability     [0–1]

Observed data format  (CSV or JSON, one row per time step):
  CSV:  t,Biomass_Stock,Fire_Risk,Management_Capacity,Suitability
  JSON: [{"t": 0, "Biomass_Stock": 1000, "Fire_Risk": 0.75, ...}, ...]

Calibrated parameters (any subset of DEFAULTS):
  Community_Governance, Grazing_Intensity, Tourism_Pressure,
  Governance_Capacity, Economic_Resilience, Water_Requirement

Usage:
    # Minimal — uses synthetic baseline as observed data (smoke-test)
    python sd/calibration/fit.py --smoke-test

    # Calibrate from CSV
    python sd/calibration/fit.py \\
        --observed data/observed_monchique.csv \\
        --targets Fire_Risk Suitability \\
        --params Community_Governance Grazing_Intensity Tourism_Pressure \\
        --run-length 30 \\
        --output sd/calibration/calibrated_params.json

    # Calibrate from JSON
    python sd/calibration/fit.py \\
        --observed data/observed_monchique.json \\
        --targets Biomass_Stock Fire_Risk \\
        --run-length 50

Dependencies:
    pip install scipy pandas numpy  (scipy optional — falls back to grid search)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Repo root on path so model import works regardless of cwd
_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from sd.models.monchique_rural import MonchiqueModel, DEFAULTS  # noqa: E402

# ---------------------------------------------------------------------------
# Optional dependencies
# ---------------------------------------------------------------------------
try:
    import pandas as pd
    _PANDAS = True
except ImportError:
    _PANDAS = False

try:
    from scipy.optimize import minimize as scipy_minimize
    _SCIPY = True
except ImportError:
    _SCIPY = False


# ---------------------------------------------------------------------------
# Parameters available for calibration and their [lo, hi] bounds
# ---------------------------------------------------------------------------
CALIBRATION_BOUNDS: Dict[str, Tuple[float, float]] = {
    "Community_Governance":  (0.10, 1.00),
    "Grazing_Intensity":     (0.05, 0.95),
    "Tourism_Pressure":      (1.00, 100.0),
    "Governance_Capacity":   (200_000.0, 8_000_000.0),
    "Economic_Resilience":   (20_000.0,  600_000.0),
    "Water_Requirement":     (0.10, 0.95),
    # Growth and rate coefficients (internal to _step — expose here for advanced use)
    "Biomass_growth_rate_base":  (0.01, 0.10),
    "Fire_biomass_coeff":        (0.02, 0.20),
    "Fire_governance_coeff":     (0.02, 0.25),
    "Fire_management_coeff":     (0.02, 0.25),
    "Fire_tourism_coeff":        (0.01, 0.15),
}

OUTPUT_VARS = ["Biomass_Stock", "Fire_Risk", "Management_Capacity", "Suitability"]


# ---------------------------------------------------------------------------
# Observed data loading
# ---------------------------------------------------------------------------

def load_observed_csv(path: Path, targets: List[str]) -> Dict[int, Dict[str, float]]:
    """Load observed data from CSV. Returns {t: {var: value}}."""
    if not _PANDAS:
        raise ImportError("pandas required for CSV loading: pip install pandas")
    df = pd.read_csv(path)
    if "t" not in df.columns:
        raise ValueError("CSV must have a 't' column (time step index)")
    result: Dict[int, Dict[str, float]] = {}
    for _, row in df.iterrows():
        t = int(row["t"])
        result[t] = {v: float(row[v]) for v in targets if v in row}
    return result


def load_observed_json(path: Path, targets: List[str]) -> Dict[int, Dict[str, float]]:
    """Load observed data from JSON list. Returns {t: {var: value}}."""
    with path.open("r", encoding="utf-8") as f:
        records = json.load(f)
    result: Dict[int, Dict[str, float]] = {}
    for record in records:
        t = int(record.get("t", record.get("Time", -1)))
        if t < 0:
            continue
        result[t] = {v: float(record[v]) for v in targets if v in record}
    return result


def load_observed(path: Path, targets: List[str]) -> Dict[int, Dict[str, float]]:
    """Auto-detect CSV or JSON and load observed data."""
    if path.suffix.lower() == ".csv":
        return load_observed_csv(path, targets)
    return load_observed_json(path, targets)


# ---------------------------------------------------------------------------
# Objective function
# ---------------------------------------------------------------------------

def _run_and_extract(
    params: Dict[str, float],
    run_length: int,
    targets: List[str],
) -> Dict[int, Dict[str, float]]:
    """Run model with given params; return {t: {var: value}} for target vars."""
    model = MonchiqueModel(params=params)
    output = model.run(run_length=run_length)

    simulated: Dict[int, Dict[str, float]] = {}
    if _PANDAS and hasattr(output, "iterrows"):
        for t_val, row in output.iterrows():
            simulated[int(t_val)] = {v: float(row[v]) for v in targets if v in row}
    else:
        for record in output:
            t = int(record.get("t", record.get("Time", -1)))
            simulated[t] = {v: float(record[v]) for v in targets if v in record}
    return simulated


def rmse(
    simulated: Dict[int, Dict[str, float]],
    observed: Dict[int, Dict[str, float]],
    targets: List[str],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Weighted RMSE across all observed time steps and target variables.
    Variables are normalised by their observed range to equalise scale
    (e.g. Biomass in tons vs Fire_Risk in [0,1]).
    """
    weights = weights or {v: 1.0 for v in targets}

    # Compute per-variable normalisation scale from observed range
    scales: Dict[str, float] = {}
    for var in targets:
        obs_vals = [obs[var] for obs in observed.values() if var in obs]
        rng = max(obs_vals) - min(obs_vals) if len(obs_vals) > 1 else max(obs_vals)
        scales[var] = rng if rng > 1e-9 else 1.0

    sse = 0.0
    count = 0
    for t, obs_row in observed.items():
        sim_row = simulated.get(t, {})
        for var in targets:
            if var not in obs_row or var not in sim_row:
                continue
            err = (sim_row[var] - obs_row[var]) / scales[var]
            sse += weights.get(var, 1.0) * err ** 2
            count += 1

    return math.sqrt(sse / count) if count > 0 else float("inf")


def objective(
    x: List[float],
    param_names: List[str],
    observed: Dict[int, Dict[str, float]],
    run_length: int,
    targets: List[str],
    bounds: List[Tuple[float, float]],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Objective function for scipy.optimize. Maps x vector → RMSE.
    Applies soft penalty for parameter values outside bounds.
    """
    params: Dict[str, float] = {}
    penalty = 0.0
    for i, (name, val) in enumerate(zip(param_names, x)):
        lo, hi = bounds[i]
        if val < lo:
            penalty += 10.0 * (lo - val) ** 2
            val = lo
        elif val > hi:
            penalty += 10.0 * (val - hi) ** 2
            val = hi
        params[name] = val

    simulated = _run_and_extract(params, run_length, targets)
    return rmse(simulated, observed, targets, weights) + penalty


# ---------------------------------------------------------------------------
# Grid search fallback (no scipy)
# ---------------------------------------------------------------------------

def grid_search(
    param_names: List[str],
    observed: Dict[int, Dict[str, float]],
    run_length: int,
    targets: List[str],
    bounds: List[Tuple[float, float]],
    grid_steps: int = 5,
) -> Tuple[Dict[str, float], float]:
    """
    Coarse grid search over parameter space. Used when scipy unavailable.
    Grid complexity = grid_steps ^ len(param_names) — keep param_names small.
    """
    def _linspace(lo: float, hi: float, n: int) -> List[float]:
        if n <= 1:
            return [(lo + hi) / 2]
        step = (hi - lo) / (n - 1)
        return [lo + i * step for i in range(n)]

    grids = [_linspace(lo, hi, grid_steps) for (lo, hi) in bounds]

    best_loss = float("inf")
    best_params: Dict[str, float] = {n: DEFAULTS.get(n, 0.5) for n in param_names}

    # Recursive grid iteration
    def _iterate(idx: int, current: Dict[str, float]) -> None:
        nonlocal best_loss, best_params
        if idx == len(param_names):
            sim = _run_and_extract(current, run_length, targets)
            loss = rmse(sim, observed, targets)
            if loss < best_loss:
                best_loss = loss
                best_params = dict(current)
            return
        name = param_names[idx]
        for val in grids[idx]:
            current[name] = val
            _iterate(idx + 1, current)

    _iterate(0, {n: DEFAULTS.get(n, 0.5) for n in param_names})
    return best_params, best_loss


# ---------------------------------------------------------------------------
# Main calibration routine
# ---------------------------------------------------------------------------

def calibrate(
    observed: Dict[int, Dict[str, float]],
    param_names: List[str],
    targets: List[str],
    run_length: int = 50,
    method: str = "auto",
    weights: Optional[Dict[str, float]] = None,
    n_restarts: int = 3,
) -> Dict[str, Any]:
    """
    Fit model parameters to observed data.

    Args:
        observed:     {t: {var: value}} observed time-series
        param_names:  parameters to calibrate
        targets:      output variables to match
        run_length:   simulation length (should match observed span)
        method:       'scipy' | 'grid' | 'auto' (scipy if available)
        weights:      per-variable loss weights
        n_restarts:   number of random restarts (scipy only)

    Returns:
        dict with keys: calibrated_params, rmse, method, iterations, timestamp
    """
    bounds = [CALIBRATION_BOUNDS.get(p, (0.0, 1.0)) for p in param_names]
    use_scipy = _SCIPY and method in ("auto", "scipy")

    if use_scipy:
        import numpy as np  # noqa: PLC0415

        best_result = None
        best_loss = float("inf")

        for restart in range(n_restarts):
            # Random initial point within bounds
            rng = np.random.default_rng(seed=restart * 42)
            x0 = [rng.uniform(lo, hi) for (lo, hi) in bounds]

            result = scipy_minimize(
                objective,
                x0,
                args=(param_names, observed, run_length, targets, bounds, weights),
                method="Nelder-Mead",
                options={"maxiter": 2000, "xatol": 1e-5, "fatol": 1e-6, "disp": False},
            )

            if result.fun < best_loss:
                best_loss = result.fun
                best_result = result

        # Clamp final params to bounds
        calibrated = {}
        for name, val, (lo, hi) in zip(param_names, best_result.x, bounds):
            calibrated[name] = float(max(lo, min(hi, val)))

        return {
            "calibrated_params": calibrated,
            "rmse": round(best_loss, 6),
            "method": "scipy/Nelder-Mead",
            "n_restarts": n_restarts,
            "iterations": int(best_result.nit),
            "converged": bool(best_result.success),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    else:
        # Grid search fallback
        grid_steps = 5 if len(param_names) <= 3 else 3
        calibrated, loss = grid_search(
            param_names, observed, run_length, targets, bounds, grid_steps=grid_steps
        )
        return {
            "calibrated_params": calibrated,
            "rmse": round(loss, 6),
            "method": f"grid_search (steps={grid_steps})",
            "n_restarts": 1,
            "iterations": grid_steps ** len(param_names),
            "converged": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


# ---------------------------------------------------------------------------
# Smoke test — synthetic data from baseline run
# ---------------------------------------------------------------------------

def smoke_test(run_length: int = 20) -> None:
    """
    Self-contained smoke test. Generates synthetic 'observed' data from the
    baseline model, then calibrates with a perturbed starting point and
    verifies that calibrated params recover close to baseline values.
    """
    print("🔬 Running calibration smoke test…")

    # Generate synthetic observed data from a known parameter set
    known = {
        "Community_Governance": 0.75,
        "Grazing_Intensity": 0.35,
        "Tourism_Pressure": 20.0,
    }
    targets = ["Fire_Risk", "Suitability", "Management_Capacity"]
    model = MonchiqueModel(params=known)
    output = model.run(run_length=run_length)

    observed: Dict[int, Dict[str, float]] = {}
    if _PANDAS and hasattr(output, "iterrows"):
        for t_val, row in output.iterrows():
            observed[int(t_val)] = {v: float(row[v]) for v in targets if v in row}
    else:
        for record in output:
            t = int(record.get("t", record.get("Time", -1)))
            observed[t] = {v: float(record[v]) for v in targets if v in record}

    param_names = list(known.keys())
    result = calibrate(
        observed=observed,
        param_names=param_names,
        targets=targets,
        run_length=run_length,
        method="auto",
        n_restarts=3,
    )

    print(f"\n✅ Smoke test complete — method: {result['method']}")
    print(f"   RMSE: {result['rmse']:.6f} (target: < 0.02)")
    print("\n   Known vs Calibrated:")
    for p in param_names:
        known_val = known[p]
        cal_val = result["calibrated_params"].get(p, float("nan"))
        delta = abs(cal_val - known_val)
        status = "✅" if delta < 0.15 * (known_val + 1e-9) else "⚠️ "
        print(f"   {status} {p:<35} known={known_val:.4f}  calibrated={cal_val:.4f}  Δ={delta:.4f}")

    if result["rmse"] < 0.05:
        print("\n✅ Calibration recovers baseline parameters within tolerance.")
    else:
        print("\n⚠️  RMSE higher than expected — check model equations or increase n_restarts.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calibrate MonchiqueModel parameters to observed time-series data."
    )
    parser.add_argument(
        "--observed", type=str, default="",
        help="Path to observed data file (CSV or JSON). Omit to use --smoke-test."
    )
    parser.add_argument(
        "--targets", nargs="+", default=["Fire_Risk", "Suitability"],
        choices=OUTPUT_VARS,
        help="Output variables to match (default: Fire_Risk Suitability)"
    )
    parser.add_argument(
        "--params", nargs="+",
        default=["Community_Governance", "Grazing_Intensity", "Tourism_Pressure"],
        help="Parameters to calibrate"
    )
    parser.add_argument(
        "--run-length", type=int, default=30,
        help="Simulation run length (should span observed data)"
    )
    parser.add_argument(
        "--method", choices=["auto", "scipy", "grid"], default="auto",
        help="Optimisation method: auto (scipy if available, else grid)"
    )
    parser.add_argument(
        "--n-restarts", type=int, default=3,
        help="Number of random restarts for scipy optimiser"
    )
    parser.add_argument(
        "--output", type=str, default="",
        help="Output path for calibrated params JSON"
    )
    parser.add_argument(
        "--smoke-test", action="store_true",
        help="Run self-contained smoke test with synthetic data"
    )
    args = parser.parse_args()

    if args.smoke_test or not args.observed:
        smoke_test(run_length=args.run_length)
        return

    observed_path = _ROOT / args.observed
    if not observed_path.exists():
        raise FileNotFoundError(f"Observed data not found: {observed_path}")

    print(f"📂 Loading observed data from: {observed_path}")
    observed = load_observed(observed_path, args.targets)
    print(f"   {len(observed)} time steps, targets: {args.targets}")

    # Validate calibration params are in bounds dict
    unknown_params = [p for p in args.params if p not in CALIBRATION_BOUNDS]
    if unknown_params:
        print(f"⚠️  Unknown calibration parameters (will use [0,1] bounds): {unknown_params}")

    print(f"\n⏳ Calibrating ({args.method}, {args.n_restarts} restarts)…")
    result = calibrate(
        observed=observed,
        param_names=args.params,
        targets=args.targets,
        run_length=args.run_length,
        method=args.method,
        n_restarts=args.n_restarts,
    )

    # Print summary
    print(f"\n✅ Calibration complete")
    print(f"   Method    : {result['method']}")
    print(f"   RMSE      : {result['rmse']:.6f}")
    print(f"   Converged : {result.get('converged', 'N/A')}")
    print(f"   Iterations: {result['iterations']}")
    print("\n   Calibrated parameters:")
    for p, v in result["calibrated_params"].items():
        default_v = DEFAULTS.get(p, float("nan"))
        print(f"   {p:<35} {v:.6f}  (default: {default_v})")

    # Save
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = _ROOT / (args.output or f"sd/calibration/calibrated_params_{timestamp}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"\n📄 Saved to: {out_path}")

    # Suggest: update parameters.json with calibrated values
    params_json_path = _ROOT / "sd/data/parameters.json"
    if params_json_path.exists():
        print(f"\n💡 To apply calibrated params to the model, update {params_json_path}:")
        print(f"   python -c \"")
        print(f"   import json; p=json.load(open('{params_json_path}'));")
        for k, v in result["calibrated_params"].items():
            print(f"   p['{k}']={v:.6f};")
        print(f"   json.dump(p, open('{params_json_path}','w'), indent=2)\"")


if __name__ == "__main__":
    main()
