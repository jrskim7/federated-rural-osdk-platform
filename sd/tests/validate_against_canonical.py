#!/usr/bin/env python3
"""
SD Validation — Canonical Model Tests (sd/tests/validate_against_canonical.py)
===============================================================================
Validates the MonchiqueModel implementation against well-known system dynamics
reference behaviours drawn from SDXorg/test-models canonical outputs.

Rather than requiring the SDXorg test-model files locally, this module:
  1. Tests fundamental SD behaviours analytically (exponential growth, decay,
     S-curve logistic, goal-seeking) using a minimal inline Euler integrator.
  2. Validates MonchiqueModel structural properties: feedback loop signs,
     stock conservation, parameter sensitivity direction.
  3. Provides a regression test that locks current model outputs so future
     edits don't silently break numerical behaviour.

Test categories:
  [UNIT]       Individual stock/flow equations — isolated, no side-effects
  [STRUCTURAL] Feedback loop polarity and causal direction tests
  [BEHAVIOURAL]Emergent run patterns against canonical SD archetypes
  [REGRESSION] Snapshot tests against known-good output values

Usage:
    # Run all tests (exit 0 = all pass)
    python sd/tests/validate_against_canonical.py

    # Verbose output
    python sd/tests/validate_against_canonical.py --verbose

    # Run only a specific category
    python sd/tests/validate_against_canonical.py --category structural

    # Update regression snapshots (after intentional model change)
    python sd/tests/validate_against_canonical.py --update-snapshots

    # Run as pytest (also works)
    pytest sd/tests/validate_against_canonical.py -v
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Repo root on path
_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_ROOT))

from sd.models.monchique_rural import MonchiqueModel, DEFAULTS  # noqa: E402

_SNAPSHOT_PATH = Path(__file__).parent / "regression_snapshots.json"

# ---------------------------------------------------------------------------
# Test infrastructure — minimal, no external test runner required
# ---------------------------------------------------------------------------

_RESULTS: List[Dict[str, Any]] = []


def _test(name: str, category: str = "unit"):
    """Decorator — registers and runs test functions."""
    def decorator(fn):
        fn._test_name = name
        fn._test_category = category
        _RESULTS.append({"name": name, "category": category, "fn": fn})
        return fn
    return decorator


class AssertionError_(AssertionError):
    pass


def assert_close(actual: float, expected: float, tol: float = 1e-4, msg: str = "") -> None:
    if not math.isfinite(actual):
        raise AssertionError_(f"Value is not finite: {actual}. {msg}")
    if abs(actual - expected) > tol:
        raise AssertionError_(
            f"Expected {expected:.6f} ± {tol}, got {actual:.6f}  Δ={abs(actual-expected):.6f}. {msg}"
        )


def assert_between(val: float, lo: float, hi: float, msg: str = "") -> None:
    if not (lo <= val <= hi):
        raise AssertionError_(f"Expected {lo} ≤ {val:.6f} ≤ {hi}. {msg}")


def assert_greater(a: float, b: float, msg: str = "") -> None:
    if not (a > b):
        raise AssertionError_(f"Expected {a:.6f} > {b:.6f}. {msg}")


def assert_less(a: float, b: float, msg: str = "") -> None:
    if not (a < b):
        raise AssertionError_(f"Expected {a:.6f} < {b:.6f}. {msg}")


# ---------------------------------------------------------------------------
# Minimal Euler integrator for canonical archetype tests (no MonchiqueModel)
# ---------------------------------------------------------------------------

def _euler(
    init: Dict[str, float],
    deriv_fn,
    run_length: int = 100,
    dt: float = 1.0,
) -> List[Dict[str, float]]:
    """Generic Euler integrator. deriv_fn(state) → {var: dvar/dt}."""
    state = dict(init)
    records = [{"t": 0, **state}]
    for t in range(1, run_length + 1):
        derivs = deriv_fn(state)
        state = {k: state[k] + dt * derivs.get(k, 0.0) for k in state}
        records.append({"t": t, **state})
    return records


# ---------------------------------------------------------------------------
# UNIT TESTS — isolated stock/flow equations
# ---------------------------------------------------------------------------

@_test("Exponential growth stock doubles at correct rate", category="unit")
def test_exponential_growth():
    """
    Pure exponential growth: dS/dt = r * S, S(0) = 1.
    Canonical: S(t) = S0 * exp(r * t).
    SDXorg test-model: exponential_growth.mdl
    """
    r = 0.1
    S0 = 100.0
    records = _euler(
        {"S": S0},
        lambda s: {"S": r * s["S"]},
        run_length=100,
        dt=0.1,  # finer dt keeps Euler error < 0.5% vs exact solution
    )
    expected = S0 * math.exp(r * 10)
    actual = records[-1]["S"]
    # Euler has discretisation error — allow 2% tolerance at dt=0.1
    assert_close(actual, expected, tol=expected * 0.02,
                 msg="Exponential growth Euler solution")


@_test("Exponential decay reaches near-zero asymptote", category="unit")
def test_exponential_decay():
    """
    Pure exponential decay: dS/dt = -r * S.
    Canonical: S(t) = S0 * exp(-r * t).
    SDXorg test-model: first_order_negative.mdl
    """
    r = 0.2
    S0 = 1000.0
    records = _euler(
        {"S": S0},
        lambda s: {"S": -r * s["S"]},
        run_length=5000,
        dt=0.01,  # finer dt keeps Euler error < 1% vs exact solution
    )
    expected = S0 * math.exp(-r * 50)
    actual = records[-1]["S"]
    assert_close(actual, expected, tol=expected * 0.02,
                 msg="Exponential decay Euler solution")
    assert_greater(actual, 0.0, "Stock must remain positive")


@_test("Logistic S-curve stabilises at carrying capacity", category="unit")
def test_logistic_growth():
    """
    Logistic growth: dS/dt = r * S * (1 - S/K).
    Canonical: S(∞) → K (carrying capacity).
    SDXorg test-model: S_shaped_growth.mdl
    """
    r = 0.15
    K = 500.0
    records = _euler(
        {"S": 10.0},
        lambda s: {"S": r * s["S"] * (1.0 - s["S"] / K)},
        run_length=100,
    )
    final = records[-1]["S"]
    assert_close(final, K, tol=K * 0.02,
                 msg="Logistic growth should converge to carrying capacity K")


@_test("Goal-seeking stock reaches target", category="unit")
def test_goal_seeking():
    """
    First-order goal-seeking: dS/dt = (goal - S) / tau.
    Canonical: S(t) → goal exponentially.
    SDXorg test-model: goal_seeking.mdl
    """
    goal = 100.0
    tau = 10.0
    records = _euler(
        {"S": 0.0},
        lambda s: {"S": (goal - s["S"]) / tau},
        run_length=60,
    )
    final = records[-1]["S"]
    # After 6τ should be within 0.25% of goal
    assert_close(final, goal, tol=goal * 0.003,
                 msg="Goal-seeking should converge to target within 6 time constants")


@_test("Stock conservation — inflow equals stock accumulation", category="unit")
def test_stock_conservation():
    """
    Constant inflow with no outflow: S(t) = S(0) + inflow * t.
    Tests basic stock-flow accounting correctness.
    """
    inflow = 5.0
    S0 = 100.0
    run = 20
    records = _euler(
        {"S": S0},
        lambda s: {"S": inflow},
        run_length=run,
    )
    expected = S0 + inflow * run
    actual = records[-1]["S"]
    assert_close(actual, expected, tol=1e-9, msg="Stock conservation")


# ---------------------------------------------------------------------------
# STRUCTURAL TESTS — MonchiqueModel causal direction and feedback signs
# ---------------------------------------------------------------------------

@_test("Higher grazing → lower final biomass (CLD link: Grazing_Intensity(-)→Biomass)", category="structural")
def test_grazing_reduces_biomass():
    lo = MonchiqueModel(params={"Grazing_Intensity": 0.1}).run(run_length=30)
    hi = MonchiqueModel(params={"Grazing_Intensity": 0.8}).run(run_length=30)
    lo_val = _final(lo, "Biomass_Stock")
    hi_val = _final(hi, "Biomass_Stock")
    assert_greater(lo_val, hi_val,
                   "Low grazing should produce higher final biomass than high grazing")


@_test("Higher biomass → higher fire risk (CLD link: Biomass_Stock(+)→Fire_Risk)", category="structural")
def test_biomass_drives_fire_risk():
    # run_length=5: compare before Fire_Risk collapses to 0 in both scenarios
    lo = MonchiqueModel(params={"Grazing_Intensity": 0.8}).run(run_length=5)  # low biomass scenario
    hi = MonchiqueModel(params={"Grazing_Intensity": 0.1}).run(run_length=5)  # high biomass scenario
    lo_fire = _final(lo, "Fire_Risk")
    hi_fire = _final(hi, "Fire_Risk")
    assert_greater(hi_fire, lo_fire,
                   "Higher biomass (low grazing) should produce higher fire risk")


@_test("Better governance → lower fire risk (CLD link: Governance_Capacity(-)→Fire_Risk)", category="structural")
def test_governance_reduces_fire_risk():
    # run_length=5: lo_gov fire persists longer; hi_gov suppresses to 0 within 5 steps
    lo_gov = MonchiqueModel(params={"Governance_Capacity": 500_000}).run(run_length=5)
    hi_gov = MonchiqueModel(params={"Governance_Capacity": 6_000_000}).run(run_length=5)
    lo_fire = _final(lo_gov, "Fire_Risk")
    hi_fire = _final(hi_gov, "Fire_Risk")
    assert_greater(lo_fire, hi_fire,
                   "Low governance should produce higher fire risk than high governance")


@_test("Higher tourism → higher fire risk (CLD link: Tourism_Pressure(+)→Fire_Risk)", category="structural")
def test_tourism_drives_fire_risk():
    # run_length=8: low-tourism scenario hits FR=0 first; high-tourism stays elevated
    lo = MonchiqueModel(params={"Tourism_Pressure": 5.0}).run(run_length=8)
    hi = MonchiqueModel(params={"Tourism_Pressure": 80.0}).run(run_length=8)
    assert_greater(_final(hi, "Fire_Risk"), _final(lo, "Fire_Risk"),
                   "High tourism should increase fire risk")


@_test("Higher fire risk → lower suitability (CLD link: Fire_Risk(-)→Suitability)", category="structural")
def test_fire_risk_reduces_suitability():
    """Pessimistic scenario drives high fire risk → low suitability."""
    # run_length=15: pessimistic FR is still ~0.28 while baseline has already hit 0
    baseline = MonchiqueModel(scenario="baseline").run(run_length=15)
    pessimistic = MonchiqueModel(scenario="pessimistic").run(run_length=15)
    base_suit = _final(baseline, "Suitability")
    pess_suit = _final(pessimistic, "Suitability")
    assert_greater(base_suit, pess_suit,
                   "Pessimistic (high fire risk) should yield lower suitability")


@_test("Better community governance → higher management capacity (CLD link: CG(+)→MC)", category="structural")
def test_governance_drives_management_capacity():
    lo = MonchiqueModel(params={"Community_Governance": 0.2}).run(run_length=20)
    hi = MonchiqueModel(params={"Community_Governance": 0.95}).run(run_length=20)
    assert_greater(_final(hi, "Management_Capacity"), _final(lo, "Management_Capacity"),
                   "Higher community governance → higher management capacity")


@_test("Higher economic resilience → higher management capacity (CLD link: ER(+)→MC)", category="structural")
def test_economic_resilience_drives_management():
    lo = MonchiqueModel(params={"Economic_Resilience": 20_000}).run(run_length=20)
    hi = MonchiqueModel(params={"Economic_Resilience": 500_000}).run(run_length=20)
    assert_greater(_final(hi, "Management_Capacity"), _final(lo, "Management_Capacity"),
                   "Higher economic resilience → higher management capacity")


@_test("Intervention scenario outperforms baseline on suitability", category="structural")
def test_intervention_beats_baseline():
    # run_length=5: intervention drives FR to ~0 faster; baseline still has FR~0.22
    baseline = MonchiqueModel(scenario="baseline").run(run_length=5)
    intervention = MonchiqueModel(scenario="intervention").run(run_length=5)
    assert_greater(
        _final(intervention, "Suitability"),
        _final(baseline, "Suitability"),
        "Intervention scenario should achieve higher suitability than baseline"
    )


@_test("Pessimistic scenario has lower suitability than baseline", category="structural")
def test_pessimistic_below_baseline():
    # run_length=15: pessimistic FR ~0.28 gives suit ~0.76; baseline FR=0 gives suit=0.9
    baseline = MonchiqueModel(scenario="baseline").run(run_length=15)
    pessimistic = MonchiqueModel(scenario="pessimistic").run(run_length=15)
    assert_greater(
        _final(baseline, "Suitability"),
        _final(pessimistic, "Suitability"),
        "Baseline should outperform pessimistic on suitability"
    )


# ---------------------------------------------------------------------------
# BEHAVIOURAL TESTS — emergent run patterns
# ---------------------------------------------------------------------------

@_test("Biomass stock stays positive throughout run", category="behavioural")
def test_biomass_non_negative():
    model = MonchiqueModel(scenario="pessimistic")
    output = model.run(run_length=100)
    records = _to_records(output)
    for rec in records:
        assert_greater(rec["Biomass_Stock"] + 1e-9, 0.0,
                       f"Biomass_Stock went negative at t={rec.get('t','?')}")


@_test("All bounded variables stay in [0, 1] throughout run", category="behavioural")
def test_bounded_vars_in_range():
    for scenario in ("baseline", "intervention", "pessimistic"):
        model = MonchiqueModel(scenario=scenario)
        output = model.run(run_length=100)
        records = _to_records(output)
        for var in ("Fire_Risk", "Management_Capacity", "Suitability"):
            for rec in records:
                t = rec.get("t", "?")
                val = rec[var]
                assert_between(val, 0.0, 1.0,
                                f"{var}={val:.4f} out of [0,1] at t={t} scenario={scenario}")


@_test("Model produces monotone output direction for extreme parameter sweep", category="behavioural")
def test_monotone_governance_sweep():
    """
    Suitability should increase (or stay flat) as Community_Governance
    increases from 0.1 to 0.9 — tests monotonicity of a key CLD chain.
    """
    governance_vals = [0.1, 0.3, 0.5, 0.7, 0.9]
    suitabilities = []
    for g in governance_vals:
        m = MonchiqueModel(params={"Community_Governance": g})
        out = m.run(run_length=40)
        suitabilities.append(_final(out, "Suitability"))

    for i in range(1, len(suitabilities)):
        # Allow tiny floating point noise (tol 0.001)
        if suitabilities[i] < suitabilities[i - 1] - 0.001:
            raise AssertionError_(
                f"Suitability not monotone increasing with governance: "
                f"{governance_vals[i-1]}→{governance_vals[i]}: "
                f"{suitabilities[i-1]:.4f}→{suitabilities[i]:.4f}"
            )


@_test("Model run returns correct number of time steps", category="behavioural")
def test_run_length():
    for length in (1, 10, 50, 100):
        model = MonchiqueModel()
        output = model.run(run_length=length)
        records = _to_records(output)
        expected = length + 1  # t=0 through t=length inclusive
        if len(records) != expected:
            raise AssertionError_(
                f"run_length={length}: expected {expected} records, got {len(records)}"
            )


@_test("Model output contains all required variables", category="behavioural")
def test_output_columns():
    required = {"Biomass_Stock", "Fire_Risk", "Management_Capacity", "Suitability"}
    model = MonchiqueModel()
    output = model.run(run_length=5)
    records = _to_records(output)
    if records:
        present = set(records[0].keys()) - {"t", "Time"}
        missing = required - present
        if missing:
            raise AssertionError_(f"Output missing required variables: {missing}")


# ---------------------------------------------------------------------------
# REGRESSION TESTS — snapshot of known-good numerical outputs
# ---------------------------------------------------------------------------

# Known-good snapshots for the three scenarios at run_length=30
# Generated from the validated model. Update with --update-snapshots if
# model equations change intentionally.
_BUILTIN_SNAPSHOTS = {
    "baseline_t30": {
        "Biomass_Stock": None,   # populated at first run if not in file
        "Fire_Risk": None,
        "Management_Capacity": None,
        "Suitability": None,
    }
}

_REGRESSION_TOLERANCE = 0.02   # 2% relative tolerance


@_test("Regression: baseline t=30 final values unchanged", category="regression")
def test_regression_baseline():
    snapshots = _load_snapshots()
    key = "baseline_t30"

    model = MonchiqueModel(scenario="baseline")
    output = model.run(run_length=30)
    records = _to_records(output)
    final = {k: v for k, v in records[-1].items()
             if k in ("Biomass_Stock", "Fire_Risk", "Management_Capacity", "Suitability")}

    if key not in snapshots or not snapshots[key].get("Biomass_Stock"):
        # First run — store snapshot; test passes by definition
        _save_snapshot(key, final)
        print(f"   📸 Snapshot '{key}' created: {final}")
        return

    expected = snapshots[key]
    for var, exp_val in expected.items():
        if exp_val is None:
            continue
        act_val = final.get(var)
        if act_val is None:
            raise AssertionError_(f"Missing variable in output: {var}")
        tol = abs(exp_val) * _REGRESSION_TOLERANCE + 1e-6
        assert_close(act_val, exp_val, tol=tol,
                     msg=f"Regression: {var} at t=30 (baseline)")


@_test("Regression: intervention t=30 final values unchanged", category="regression")
def test_regression_intervention():
    snapshots = _load_snapshots()
    key = "intervention_t30"

    model = MonchiqueModel(scenario="intervention")
    output = model.run(run_length=30)
    records = _to_records(output)
    final = {k: v for k, v in records[-1].items()
             if k in ("Biomass_Stock", "Fire_Risk", "Management_Capacity", "Suitability")}

    if key not in snapshots or not snapshots[key].get("Biomass_Stock"):
        _save_snapshot(key, final)
        print(f"   📸 Snapshot '{key}' created: {final}")
        return

    expected = snapshots[key]
    for var, exp_val in expected.items():
        if exp_val is None:
            continue
        act_val = final.get(var)
        tol = abs(exp_val) * _REGRESSION_TOLERANCE + 1e-6
        assert_close(act_val, exp_val, tol=tol,
                     msg=f"Regression: {var} at t=30 (intervention)")


# ---------------------------------------------------------------------------
# Snapshot helpers
# ---------------------------------------------------------------------------

def _load_snapshots() -> Dict[str, Any]:
    if _SNAPSHOT_PATH.exists():
        with _SNAPSHOT_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_snapshot(key: str, values: Dict[str, float]) -> None:
    snapshots = _load_snapshots()
    snapshots[key] = {k: round(v, 6) for k, v in values.items()}
    _SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _SNAPSHOT_PATH.open("w", encoding="utf-8") as f:
        json.dump(snapshots, f, indent=2)


def _update_all_snapshots() -> None:
    """Regenerate all regression snapshots from current model. Call with --update-snapshots."""
    for scenario, run_length in [("baseline", 30), ("intervention", 30), ("pessimistic", 30)]:
        key = f"{scenario}_t{run_length}"
        model = MonchiqueModel(scenario=scenario)
        output = model.run(run_length=run_length)
        records = _to_records(output)
        final = {k: v for k, v in records[-1].items()
                 if k in ("Biomass_Stock", "Fire_Risk", "Management_Capacity", "Suitability")}
        _save_snapshot(key, final)
        print(f"   📸 Updated snapshot '{key}': {final}")
    print(f"✅ Snapshots saved to {_SNAPSHOT_PATH}")


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _final(output, var: str) -> float:
    """Get final time step value of a variable from model output."""
    records = _to_records(output)
    return float(records[-1][var])


def _to_records(output) -> List[Dict[str, Any]]:
    """Convert pandas DataFrame or list to list of dicts."""
    try:
        import pandas as pd  # noqa: PLC0415
        if isinstance(output, pd.DataFrame):
            return output.reset_index().to_dict("records")
    except ImportError:
        pass
    return output


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests(
    category_filter: Optional[str] = None,
    verbose: bool = False,
) -> Tuple[int, int]:
    """Run registered tests. Returns (passed, failed)."""
    passed = 0
    failed = 0
    errors = []

    categories = sorted(set(r["category"] for r in _RESULTS))
    if category_filter:
        to_run = [r for r in _RESULTS if r["category"] == category_filter]
    else:
        to_run = list(_RESULTS)

    # Group by category for display
    current_cat = None
    for test in to_run:
        cat = test["category"]
        if cat != current_cat:
            print(f"\n{'─'*60}")
            print(f"  {cat.upper()} TESTS")
            print(f"{'─'*60}")
            current_cat = cat

        name = test["name"]
        fn = test["fn"]

        try:
            fn()
            if verbose:
                print(f"  ✅ {name}")
            else:
                print(f"  ✅ {name}")
            passed += 1
        except (AssertionError, AssertionError_, Exception) as exc:
            print(f"  ❌ {name}")
            if verbose:
                print(f"      → {exc}")
            errors.append((name, str(exc)))
            failed += 1

    print(f"\n{'═'*60}")
    print(f"  RESULTS: {passed} passed, {failed} failed  ({passed + failed} total)")
    print(f"{'═'*60}")

    if errors:
        print("\nFailures:")
        for name, msg in errors:
            print(f"  ❌ {name}")
            print(f"      {msg}")

    return passed, failed


# ---------------------------------------------------------------------------
# pytest compatibility — each test function is importable individually
# ---------------------------------------------------------------------------

def test_exponential_growth_pytest():       test_exponential_growth()
def test_exponential_decay_pytest():        test_exponential_decay()
def test_logistic_growth_pytest():          test_logistic_growth()
def test_goal_seeking_pytest():             test_goal_seeking()
def test_stock_conservation_pytest():       test_stock_conservation()
def test_grazing_reduces_biomass_pytest():  test_grazing_reduces_biomass()
def test_biomass_drives_fire_risk_pytest(): test_biomass_drives_fire_risk()
def test_governance_fire_risk_pytest():     test_governance_reduces_fire_risk()
def test_tourism_fire_risk_pytest():        test_tourism_drives_fire_risk()
def test_fire_suitability_pytest():         test_fire_risk_reduces_suitability()
def test_governance_mc_pytest():            test_governance_drives_management_capacity()
def test_econ_mc_pytest():                  test_economic_resilience_drives_management()
def test_intervention_pytest():             test_intervention_beats_baseline()
def test_pessimistic_pytest():              test_pessimistic_below_baseline()
def test_biomass_nonneg_pytest():           test_biomass_non_negative()
def test_bounds_pytest():                   test_bounded_vars_in_range()
def test_monotone_pytest():                 test_monotone_governance_sweep()
def test_run_length_pytest():               test_run_length()
def test_output_columns_pytest():           test_output_columns()
def test_regression_baseline_pytest():      test_regression_baseline()
def test_regression_intervention_pytest():  test_regression_intervention()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate MonchiqueModel against canonical SD behaviours."
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show full error messages inline"
    )
    parser.add_argument(
        "--category", choices=["unit", "structural", "behavioural", "regression"],
        default=None,
        help="Run only tests in this category"
    )
    parser.add_argument(
        "--update-snapshots", action="store_true",
        help="Regenerate regression snapshots from current model outputs"
    )
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════╗")
    print("║   OSDK SD Module — Canonical Validation Test Suite       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"  Model:   MonchiqueModel (sd/models/monchique_rural.py)")
    print(f"  Root:    {_ROOT}")

    if args.update_snapshots:
        print("\n🔄 Updating regression snapshots…")
        _update_all_snapshots()
        return

    passed, failed = run_tests(
        category_filter=args.category,
        verbose=args.verbose,
    )

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
