# Systems Dynamics GitHub Reference & OSDK Integration Guide

**Author:** John Roy Ballossini Dommett  
**Project:** Federated Rural OSDK Platform — SD Module  
**Date:** April 2026  
**Version:** 1.0

---

## 1. Purpose

This document serves two purposes:

1. **Reference list** of 34 GitHub repositories identified from a systematic scan of SD-related open-source work
2. **Integration guide** for incorporating SD modelling into the OSDK pipeline, with attention to the existing `sd/` module and its relationship to the `qsem/` (CLD) module

---

## 2. OSDK Module Context

Your OSDK platform already contains two distinct but related modules:

| Module | Location | Function | Status |
|--------|----------|----------|--------|
| `qsem/` | QSEM module | Qualitative Systems Engineering Modelling — Causal Loop Diagrams (CLDs), feedback structure mapping | Active |
| `sd/` | SD module | Quantitative simulation — stocks, flows, rates, time-series outputs | Active (`sd_report_20260206_001942.json` confirms runs) |
| `scripts/sd_integration.py` | scripts/ | Integration bridge between SD outputs and rest of platform | Active |

**These are NOT duplicates.** The QSEM/CLD layer is the qualitative causal structure; the SD layer is the numerical simulation built on top of that structure. The intended workflow is:

```
Field Data → CLD (QSEM) → SD Model → Simulation Output → GIS Alignment → Report
```

The `sd_aligned.geojson` and `sd_aligned_points/polygons.geojson` files in `qgis/generated/` confirm GIS-SD spatial alignment is already happening.

---

## 3. GitHub Repository Reference List

### 3.1 Classification Framework

Repositories are classified across four dimensions relevant to your pipeline:

- **Type**: Simulation engine / Modelling tool / Visualisation / Educational / Specialist
- **Language**: Primary implementation language
- **Relevance**: Direct / Adjacent / Reference
- **Integration potential**: High / Medium / Low

---

### 3.2 Full Repository Table

| # | Repository | Description | Type | Language | Relevance | Integration Potential |
|---|-----------|-------------|------|----------|-----------|----------------------|
| 1 | [SDXorg/pysd](https://github.com/SDXorg/pysd) | Run Vensim and Stella models in Python. The de facto Python SD engine. Reads `.mdl` / `.xmile` files and converts to numpy/pandas. | Simulation Engine | Python | **Direct** | **High** |
| 2 | [SDXorg/PySD-Cookbook](https://github.com/SDXorg/PySD-Cookbook) | Jupyter notebooks of SD analysis recipes using pysd — data integration, sensitivity analysis, calibration. | Educational / Recipes | Python (Jupyter) | **Direct** | **High** |
| 3 | [SDXorg/test-models](https://github.com/SDXorg/test-models) | Canonical SD models (SIR, Bass Diffusion, Lotka-Volterra, etc.) in Vensim and Stella with validated outputs. Reference benchmarks. | Reference / Validation | Multi | **Direct** | **High** |
| 4 | [transentis/bptk_py](https://github.com/transentis/bptk_py) | Business Prototyping Toolkit — SD + Agent-Based in Python. Cleaner API than pysd for combined SD/ABM models. Step/continuous simulation. | Simulation Engine | Python | **Direct** | **High** |
| 5 | [transentis/bptk_py_tutorial](https://github.com/transentis/bptk_py_tutorial) | Tutorial notebooks for bptk_py. Model building workflow, visualisation, scenario comparison. | Educational | Python (Jupyter) | Direct | Medium |
| 6 | [bpowers/simlin](https://github.com/bpowers/simlin) | Web-based SD modelling tool with visual drag-and-drop diagram editor. Exports to XMILE. | Modelling Tool | TypeScript/Go | Adjacent | Medium |
| 7 | [climateinteractive/SDEverywhere](https://github.com/climateinteractive/SDEverywhere) | Transpiles Vensim `.mdl` files to C, JavaScript, and WebAssembly. Enables SD models as web widgets. | Transpiler / Web | C / JavaScript | Adjacent | Medium |
| 8 | [JimDuggan/SDMR](https://github.com/JimDuggan/SDMR) | Resources for "System Dynamics Modeling with R" textbook. Full SD workflow in R using deSolve. | Educational / Reference | R | Reference | Low |
| 9 | [JimDuggan/SDWorkshop](https://github.com/JimDuggan/SDWorkshop) | Workshop materials accompanying SDMR. Includes model files and exercises. | Educational | R | Reference | Low |
| 10 | [jandraor/readsdr](https://github.com/jandraor/readsdr) | Translates Stella and Vensim models into R (Stan/deSolve). Bridge for Bayesian calibration of SD models. | Converter | R | Adjacent | Low |
| 11 | [iiasa/Felix-Model](https://github.com/iiasa/Felix-Model) | FeliX — global integrated Earth system SD model (economy, energy, population, climate). Complex, real-world SD at scale. | Reference Model | Vensim / Python | Reference | Low |
| 12 | [wzh1895/ASDM](https://github.com/wzh1895/ASDM) | Agile System Dynamics Modelling framework — lightweight Python SD without Vensim dependency. | Simulation Engine | Python | **Direct** | **High** |
| 13 | [wzh1895/Stock-and-Flow-in-Python](https://github.com/wzh1895/Stock-and-Flow-in-Python) | Semi-automatic SD model conceptualisation from text/data to stock-and-flow structure. | Modelling Tool | Python | **Direct** | Medium |
| 14 | [bear96/System-Dynamics-Bot](https://github.com/bear96/System-Dynamics-Bot) | LLM-powered CLD generator — text input → causal loop diagram. Directly relevant to QSEM→SD pipeline. | AI / NLP | Python | **Direct** | **High** |
| 15 | [lzim/mtl](https://github.com/lzim/mtl) | Modeling to Learn — participatory SD for healthcare teams. Multi-model, multi-stakeholder SD framework. | Domain Model | R / Shiny | Reference | Low |
| 16 | [TUD-RST/symbtools](https://github.com/TUD-RST/symbtools) | Symbolic manipulation for control theory and SD — analytical differentiation, linearisation, transfer functions. | Specialist | Python | Adjacent | Low |
| 17 | [Ting-TingGao/Network-SDE-Inference](https://github.com/Ting-TingGao/Network-SDE-Inference) | Infer interpretable stochastic SD from experimental data using neural ODEs. | Research | Python | Reference | Low |
| 18 | [cselab/G-LED](https://github.com/cselab/G-LED) | Generative learning for high-dimensional complex system dynamics forecasting. | Research / ML | Python | Reference | Low |
| 19 | [kby24/AIDD](https://github.com/kby24/AIDD) | Automated discovery of interaction dynamics in large networked dynamical systems. | Research | Python | Reference | Low |
| 20 | [cyrusmaher/CauseMap.jl](https://github.com/cyrusmaher/CauseMap.jl) | Causal inference in nonlinear dynamical systems using convergent cross-mapping. | Specialist | Julia | Adjacent | Low |
| 21 | [JuliaDynamics/InteractiveDynamics.jl](https://github.com/JuliaDynamics/InteractiveDynamics.jl) | Interactive visual applications for complex dynamical systems in Julia. | Visualisation | Julia | Adjacent | Low |
| 22 | [Merck/ReactiveDynamics.jl](https://github.com/Merck/ReactiveDynamics.jl) | Reaction network dynamical systems in Julia — chemical/biological focus. | Specialist | Julia | Reference | Low |
| 23 | [bslMS/BusinessSimulation](https://github.com/bslMS/BusinessSimulation) | Modelica-based SD library for business, economics, ecology. Formal block-diagram approach. | Simulation Engine | Modelica | Reference | Low |
| 24 | [sdlabs/libsd](https://github.com/sdlabs/libsd) | Lightweight C library for SD simulation. Useful if embedding SD in a C/embedded context. | Library | C | Reference | Low |
| 25 | [MathWorks-Teaching-Resources/Transfer-Function-Analysis-of-Dynamic-Systems](https://github.com/MathWorks-Teaching-Resources/Transfer-Function-Analysis-of-Dynamic-Systems) | MATLAB courseware for transfer function analysis in control/SD courses. | Educational | MATLAB | Reference | Low |
| 26 | [highperformancecoder/minsky](https://github.com/highperformancecoder/minsky) | Economics SD modelling with Godley tables and monetary flows. Unique finance-first SD tool. | Modelling Tool | C++ | Adjacent | Low |
| 27 | [modelica-3rdparty/SystemDynamics](https://github.com/modelica-3rdparty/SystemDynamics) | Modelica implementation of Forrester-style SD models. | Library | Modelica | Reference | Low |
| 28 | [concord-consortium/building-models](https://github.com/concord-consortium/building-models) | Educational web tool for building SD models visually. STEM education focus. | Educational Tool | JavaScript | Reference | Low |
| 29 | [Dragoon-Lab/LaitsV3](https://github.com/Dragoon-Lab/LaitsV3) | Tutoring system for SD model construction. Pedagogical SD authoring. | Educational | JavaScript | Reference | Low |
| 30 | [erizhang/systemdynamics](https://github.com/erizhang/systemdynamics) | Instructor guide repository for SD courses. | Educational | — | Reference | Low |
| 31 | [gregorbj/FSDM](https://github.com/gregorbj/FSDM) | Fuzzy Systems Dynamics Model — SD with fuzzy logic for uncertain parameters. | Specialist | R | Adjacent | Low |
| 32 | [databricks-industry-solutions/digital-twin](https://github.com/databricks-industry-solutions/digital-twin) | IoT digital twin using Databricks + real-time sensor data. SD not primary but system dynamics of physical assets. | Platform | Python / Spark | Adjacent | Low |
| 33 | [douthwja01/OpenMAS](https://github.com/douthwja01/OpenMAS) | Multi-agent simulator in MATLAB for decentralised intelligent systems. | Specialist | MATLAB | Reference | Low |
| 34 | [UppASD/UppASD](https://github.com/UppASD/UppASD) | Atomistic spin dynamics simulation (physics). Not SE-relevant. | Specialist | Fortran | Reference — no | None |

---

### 3.3 Priority Shortlist (High Integration Potential)

| Priority | Repository | Why |
|----------|-----------|-----|
| ⭐⭐⭐ | **pysd** | Standard Python SD engine; reads Vensim/Stella; direct pandas output; mature ecosystem |
| ⭐⭐⭐ | **PySD-Cookbook** | Ready-made recipes for calibration, sensitivity, data integration with SD models |
| ⭐⭐⭐ | **SDXorg/test-models** | Validated benchmark models to test your SD module against canonical outputs |
| ⭐⭐ | **bptk_py** | Cleaner API, combined SD+ABM; better if you want agent-based rural stakeholder dynamics |
| ⭐⭐ | **ASDM** | Lightweight, no Vensim dependency; good for embedded/portable SD in OSDK |
| ⭐⭐ | **System-Dynamics-Bot** | LLM-to-CLD pipeline — directly connects your QSEM CLD module to SD model generation |
| ⭐ | **simlin** | Web-based diagram editor; could serve as visual front-end for model building |
| ⭐ | **SDEverywhere** | If you want to publish SD models as web widgets in your OSDK dashboard |

---

## 4. QSEM vs SD Module — Clarification

These are complementary, not duplicate:

```
QSEM Module (Qualitative)          SD Module (Quantitative)
─────────────────────────          ────────────────────────
Causal Loop Diagrams               Stock & Flow models
Feedback loop identification       Differential equations
Polarity (+/−) mapping             Rate parameters
Mental model capture               Simulation over time
→ Output: CLD JSON / diagram       → Output: time-series, JSON report

        ↕ handoff via sd_integration.py
```

The `sd_integration.py` script in `scripts/` is the bridge — it takes QSEM output (CLD structure) and scaffolds the SD model variables from it.

**Gap identified:** There is currently no automated pathway from CLD polarity structure → pysd-compatible model equations. The `bear96/System-Dynamics-Bot` approach (or a custom version using Claude API) could close this gap.

---

## 5. Integration Roadmap for OSDK SD Module

### Phase 1: Foundation (Week 1–2)

1. **Install pysd** into the OSDK `.venv`:
   ```bash
   cd /Users/jrbd/Documents/GitHub/federated-rural-osdk-platform
   source .venv/bin/activate
   pip install pysd
   ```

2. **Validate existing SD module** against canonical test-models:
   ```bash
   git clone https://github.com/SDXorg/test-models
   # Run SIR model through your sd/ module and compare to test-models/SIR canonical output
   ```

3. **Review sd_integration.py** — identify current input/output contract

### Phase 2: CLD→SD Bridge (Week 3–4)

4. **Map QSEM CLD output** (variables + polarities) to pysd-compatible stock/flow skeleton
   - Each accumulating variable in CLD → Stock
   - Each causal edge with rate semantics → Flow
   - Each auxiliary driver → Auxiliary variable

5. **Parameterise from OSDK data** — wire the GIS data, cadastral data, network data to SD parameters:
   - Population stocks ← GIS census layers
   - Land use flows ← Cadastral change data (DGT API)
   - Economic rates ← Conscious Circle project data

### Phase 3: Outputs & Visualisation (Week 5–6)

6. **SD → GIS alignment** (already partially working per `sd_aligned.geojson`) — formalise the pipeline
7. **SD → Report** — ensure `sd_report_*.json` feeds into the OSDK reporting layer
8. **Optional: SDEverywhere** — compile model to WebAssembly for browser-based scenario explorer

### Phase 4: Portfolio Quality (MDEF prep)

9. **Add scenario comparison** (using PySD-Cookbook recipes) — business-as-usual vs intervention scenarios for Monchique
10. **SHAP/sensitivity analysis** on SD parameters — connects to Portfolio Project 2 (Predictive Compliance Model)
11. **Document in SysML** — use the SD module as a test case for SysMLv2 behavioural diagrams

---

## 6. Feature Consolidation Matrix

Features worth extracting from priority repos for OSDK:

| Feature | Source Repo | Implementation in OSDK |
|---------|------------|----------------------|
| `.mdl` / `.xmile` file reading | pysd | Add to `sd/` module — import existing Vensim models |
| Sensitivity analysis | PySD-Cookbook | `sd/analysis/sensitivity.py` |
| Monte Carlo simulation | PySD-Cookbook | `sd/analysis/monte_carlo.py` |
| Calibration to data | PySD-Cookbook | `sd/calibration/fit.py` — calibrate against OSDK field data |
| CLD-to-SD scaffolding | System-Dynamics-Bot | `scripts/cld_to_sd.py` — uses Claude API |
| Web scenario explorer | SDEverywhere | `dashboard/sd_widget/` — optional |
| Canonical test cases | test-models | `tests/sd/` — CI validation |
| Combined SD+ABM | bptk_py | Future: `sd/agents/` for stakeholder behaviour |
| Fuzzy parameters | FSDM | Future: `sd/uncertainty/` for incomplete rural data |

---

## 7. Recommended `sd/` Directory Structure

```
sd/
├── models/
│   ├── monchique_rural.py       # Current Monchique model
│   ├── monchique_rural.mdl      # Vensim equivalent (if needed)
│   └── templates/
│       ├── basic_srp.py         # Stock-Rate-Population template
│       └── land_use.py          # Land use change template
├── data/
│   ├── parameters.json          # Calibrated parameters
│   └── initial_conditions.json  # Starting stock values
├── analysis/
│   ├── sensitivity.py
│   ├── monte_carlo.py
│   └── scenarios.py
├── calibration/
│   └── fit.py
├── output/
│   └── sd_report_20260206_001942.json  # (existing)
├── tests/
│   └── validate_against_canonical.py
└── README.md
```

---

## 8. Quick-Start Code Snippet

Minimal pysd integration into your existing `sd_integration.py`:

```python
import pysd
import pandas as pd

def run_sd_model(model_path: str, params: dict, run_length: int = 100) -> pd.DataFrame:
    """
    Load and run a pysd-compatible model (.mdl or .xmile).
    
    Args:
        model_path: Path to .mdl or .xmile file
        params: Dict of parameter overrides {'param_name': value}
        run_length: Simulation time steps
    
    Returns:
        DataFrame of simulation results (time × variables)
    """
    model = pysd.read_vensim(model_path)  # or read_xmile() for XMILE format
    results = model.run(params=params, return_timestamps=range(run_length))
    return results


def cld_to_sd_skeleton(cld_json: dict) -> dict:
    """
    Convert QSEM CLD output to SD model skeleton.
    Stocks: nodes with net accumulation (in-flows > out-flows in CLD)
    Flows: edges with rate semantics
    """
    stocks = []
    flows = []
    auxiliaries = []
    
    for node in cld_json.get('nodes', []):
        if node.get('type') == 'stock':
            stocks.append(node['label'])
        elif node.get('type') == 'auxiliary':
            auxiliaries.append(node['label'])
    
    for edge in cld_json.get('edges', []):
        if edge.get('semantic') == 'flow':
            flows.append({
                'name': f"{edge['source']}_to_{edge['target']}",
                'source': edge['source'],
                'target': edge['target'],
                'polarity': edge.get('polarity', '+')
            })
    
    return {
        'stocks': stocks,
        'flows': flows,
        'auxiliaries': auxiliaries
    }
```

---

## 9. Notes on Existing OSDK SD Outputs

From the file structure scan:

- `sd/output/sd_report_20260206_001942.json` — live run output from February 2026
- `qgis/generated/sd_aligned.geojson` — SD variables spatially joined to geographic features
- `mbse/exports/monchique_federated_model_sd_*.geojson` — SD model exported as part of MBSE federated model

This confirms your SD module already runs and produces structured output. The integration roadmap above builds on this foundation rather than starting from scratch.

---

## 10. Resources to Add to SERAPH RAG Pipeline

Consider indexing these alongside your SE literature:

- Sterman, J. (2000). *Business Dynamics* — the primary SD textbook
- Forrester, J.W. (1961). *Industrial Dynamics* — foundational
- pysd documentation: https://pysd.readthedocs.io/
- SDXorg test model outputs: canonical validation reference
- Vensim model exchange format (XMILE) spec: ISO/IEC 19506

---

*Document generated from systematic GitHub scan (34 repos, pages 1–12 of SD keyword results) and OSDK platform filesystem review.*  
*Next review: after Phase 2 CLD→SD bridge implementation.*
