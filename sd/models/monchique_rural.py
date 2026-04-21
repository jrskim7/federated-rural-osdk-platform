#!/usr/bin/env python3
"""
Monchique Rural SD Model
========================
Native Python stock-and-flow model for the Monchique case study.

Stocks and structure are derived from the QSEM CLD in qsem/exports/cld_network.json.
This model is pysd-compatible in interface (run() returns a pandas DataFrame) and
can be replaced by a pysd.read_vensim() call if a .mdl file is produced.

Stocks (accumulating variables, from CLD):
  - Biomass_Stock       [tons]       — accumulates growth, depleted by grazing and fire
  - Fire_Risk           [0–1]        — state variable tracking landscape fire susceptibility

Auxiliaries (computed each step, from CLD):
  - Management_Capacity [0–1]
  - Suitability         [0–1]

Constants (parameters, set at initialisation):
  - Community_Governance, Governance_Capacity, Economic_Resilience,
    Grazing_Intensity, Water_Requirement, Tourism_Pressure, Grazable_Area

Scenario presets:
  baseline     — CLD initial values as-is
  intervention — improved governance, reduced grazing intensity
  pessimistic  — low governance, high tourism pressure, drought

Usage:
    from sd.models.monchique_rural import MonchiqueModel
    model = MonchiqueModel()
    df = model.run(run_length=50)
    print(df.tail())
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pandas as pd  # noqa: F401
    _PANDAS = True
except (ImportError, Exception):
    _PANDAS = False


# ---------------------------------------------------------------------------
# Default initial conditions (sourced from cld_network.json initial values)
# ---------------------------------------------------------------------------

DEFAULTS: Dict[str, float] = {
    "Biomass_Stock": 1000.0,       # tons
    "Fire_Risk": 0.75,             # index 0-1
    "Community_Governance": 0.72,  # index 0-1
    "Governance_Capacity": 2_500_000.0,  # euros budget
    "Economic_Resilience": 180_000.0,    # euros revenue
    "Management_Capacity": 0.8,    # index 0-1 (also a stock/auxiliary)
    "Grazing_Intensity": 0.5,      # index 0-1
    "Grazable_Area": 35.0,         # ha
    "Tourism_Pressure": 23.0,      # member count proxy
    "Water_Requirement": 0.5,      # m³/s
    "Suitability": 0.85,           # project suitability index
}

SCENARIO_OVERRIDES: Dict[str, Dict[str, float]] = {
    "baseline": {},
    "intervention": {
        "Community_Governance": 0.90,
        "Grazing_Intensity": 0.25,
        "Tourism_Pressure": 15.0,
        "Governance_Capacity": 3_500_000.0,
    },
    "pessimistic": {
        "Community_Governance": 0.40,
        "Grazing_Intensity": 0.75,
        "Tourism_Pressure": 45.0,
        "Governance_Capacity": 1_200_000.0,
        "Economic_Resilience": 80_000.0,
    },
}


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


@dataclass
class ModelState:
    Biomass_Stock: float
    Fire_Risk: float
    Management_Capacity: float
    Suitability: float
    # constants — held fixed across steps
    Community_Governance: float
    Governance_Capacity: float
    Economic_Resilience: float
    Grazing_Intensity: float
    Grazable_Area: float
    Tourism_Pressure: float
    Water_Requirement: float

    def as_dict(self, t: int) -> Dict[str, Any]:
        return {
            "t": t,
            "Biomass_Stock": self.Biomass_Stock,
            "Fire_Risk": self.Fire_Risk,
            "Management_Capacity": self.Management_Capacity,
            "Suitability": self.Suitability,
            "Community_Governance": self.Community_Governance,
            "Governance_Capacity": self.Governance_Capacity,
            "Economic_Resilience": self.Economic_Resilience,
            "Grazing_Intensity": self.Grazing_Intensity,
            "Tourism_Pressure": self.Tourism_Pressure,
            "Water_Requirement": self.Water_Requirement,
        }


class MonchiqueModel:
    """
    Stock-and-flow model for the Monchique rural landscape system.

    The model implements the 9 causal links from the QSEM CLD with their
    confirmed polarities:

    CLD link                                    Polarity    Mechanism
    Grazing_Intensity → Biomass_Stock           (-)         grazing depletes biomass
    Biomass_Stock → Fire_Risk                   (+)         fuel load drives risk
    Governance_Capacity → Fire_Risk             (-)         institutional fire reduction
    Management_Capacity → Fire_Risk             (-)         active risk management
    Tourism_Pressure → Fire_Risk                (+)         pressure elevates risk
    Fire_Risk → Suitability                     (-)         risk lowers project viability
    Economic_Resilience → Management_Capacity   (+)         revenue enables management
    Community_Governance → Management_Capacity  (+)         governance improves coordination
    Water_Requirement → Suitability             (-)         higher demand reduces feasibility
    """

    def __init__(self, scenario: str = "baseline", params: Optional[Dict[str, float]] = None) -> None:
        init = {**DEFAULTS, **SCENARIO_OVERRIDES.get(scenario, {}), **(params or {})}
        self._init = init
        self._scenario = scenario

    def _initial_state(self) -> ModelState:
        p = self._init
        return ModelState(
            Biomass_Stock=p["Biomass_Stock"],
            Fire_Risk=p["Fire_Risk"],
            Management_Capacity=p["Management_Capacity"],
            Suitability=p["Suitability"],
            Community_Governance=p["Community_Governance"],
            Governance_Capacity=p["Governance_Capacity"],
            Economic_Resilience=p["Economic_Resilience"],
            Grazing_Intensity=p["Grazing_Intensity"],
            Grazable_Area=p["Grazable_Area"],
            Tourism_Pressure=p["Tourism_Pressure"],
            Water_Requirement=p["Water_Requirement"],
        )

    @staticmethod
    def _step(s: ModelState, dt: float = 1.0) -> ModelState:
        # --- Auxiliaries (updated first from current state) ---

        # Management_Capacity driven by Economic_Resilience and Community_Governance
        # CLD: Economic_Resilience(+) and Community_Governance(+) both drive MC
        gov_norm = _clamp(s.Governance_Capacity / 5_000_000.0)  # normalise budget 0-1
        econ_norm = _clamp(s.Economic_Resilience / 500_000.0)
        mc_next = _clamp(
            0.20
            + 0.40 * s.Community_Governance   # CLD: Community_Governance(+)→MC
            + 0.30 * econ_norm                 # CLD: Economic_Resilience(+)→MC
            + 0.10 * gov_norm
        )

        # --- Stocks ---

        # Biomass_Stock: growth - grazing loss - fire loss
        # CLD: Grazing_Intensity(-) → Biomass_Stock
        growth_rate = 0.04 + 0.02 * s.Community_Governance
        grazing_loss = s.Biomass_Stock * s.Grazing_Intensity * 0.04  # CLD (-)
        fire_loss = s.Biomass_Stock * s.Fire_Risk * 0.015
        biomass_next = max(0.0, s.Biomass_Stock + dt * (
            s.Biomass_Stock * growth_rate - grazing_loss - fire_loss
        ))

        # Fire_Risk: driven by biomass (fuel), opposed by governance + management
        # CLD links: Biomass(+), Governance(-), Management(-), Tourism(+)
        biomass_norm = _clamp(s.Biomass_Stock / 2000.0)  # normalise 0-1
        tourism_norm = _clamp(s.Tourism_Pressure / 100.0)
        fire_next = _clamp(
            s.Fire_Risk + dt * (
                0.08 * biomass_norm              # CLD: Biomass_Stock(+)→Fire_Risk
                + 0.05 * tourism_norm            # CLD: Tourism_Pressure(+)→Fire_Risk
                - 0.12 * gov_norm                # CLD: Governance_Capacity(-)→Fire_Risk
                - 0.15 * mc_next                 # CLD: Management_Capacity(-)→Fire_Risk
            )
        )

        # Suitability: reduced by fire risk and water requirement mismatch
        # CLD: Fire_Risk(-), Water_Requirement(-)
        suitability_next = _clamp(
            0.30
            + 0.50 * (1.0 - fire_next)           # CLD: Fire_Risk(-)→Suitability
            + 0.20 * (1.0 - s.Water_Requirement)  # CLD: Water_Requirement(-)→Suitability
        )

        return ModelState(
            Biomass_Stock=round(biomass_next, 3),
            Fire_Risk=round(fire_next, 4),
            Management_Capacity=round(mc_next, 4),
            Suitability=round(suitability_next, 4),
            Community_Governance=s.Community_Governance,
            Governance_Capacity=s.Governance_Capacity,
            Economic_Resilience=s.Economic_Resilience,
            Grazing_Intensity=s.Grazing_Intensity,
            Grazable_Area=s.Grazable_Area,
            Tourism_Pressure=s.Tourism_Pressure,
            Water_Requirement=s.Water_Requirement,
        )

    def run(self, run_length: int = 50, dt: float = 1.0):
        """
        Run the model for `run_length` time steps.

        Returns a pandas DataFrame (if pandas is installed) or a list of dicts.
        Interface matches pysd model.run() return convention.
        """
        state = self._initial_state()
        records = [state.as_dict(0)]
        for t in range(1, run_length + 1):
            state = self._step(state, dt=dt)
            records.append(state.as_dict(t))

        if _PANDAS:
            import pandas as pd  # noqa: PLC0415
            df = pd.DataFrame(records).set_index("t")
            df.index.name = "Time"
            return df

        return records


def load_params_from_cld(cld_path: Path) -> Dict[str, float]:
    """Extract initial parameter values from a QSEM CLD JSON file."""
    with cld_path.open("r", encoding="utf-8") as f:
        cld = json.load(f)
    params: Dict[str, float] = {}
    for element in cld.get("elements", []):
        eid = element["id"]
        val = element.get("attributes", {}).get("value")
        if val is not None:
            params[eid] = float(val)
    return params


if __name__ == "__main__":
    import sys

    scenario = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    model = MonchiqueModel(scenario=scenario)
    results = model.run(run_length=30)

    if _PANDAS:
        print(results[["Biomass_Stock", "Fire_Risk", "Management_Capacity", "Suitability"]].to_string())
    else:
        for row in results[-5:]:
            print(row)
