# Federated Rural OSDK Platform

## About
A federated, model-driven platform that turns rural infrastructure, governance, and ecosystem projects into a unified, analyzable system using MBSE, GeoJSON, and automated downstream analytics.

## Purpose
Build a federated, model-driven platform that connects rural infrastructure, governance, and ecosystem projects into a unified, data-rich system for analysis, collaboration, and decision support.

## Scope
This repository covers the end-to-end modeling and integration pipeline, including:
- **MBSE modeling** (Capella and SysML v2 pathways)
- **GeoJSON schema alignment** for the OSDK data model
- **System Dynamics** updates and scenario analysis
- **QSEM causal loop diagram generation**
- **SNA network exports** for stakeholder relationship analysis
- **ArcGIS Experience Builder** dashboard configuration
- **n8n orchestration** for automated data flows
- **Narrative extraction** from qualitative text into structured model entities

## Approach
The platform follows a **federated modeling approach**:
1. **Model creation** in MBSE tools or SysML v2 textual models.
2. **Schema mapping** into the OSDK GeoJSON format.
3. **Downstream analysis** using SD and QSEM pipelines.
4. **Visualization** through ArcGIS and Kumu.
5. **Automation** via n8n workflows and integration scripts.
6. **Narrative-to-model extraction** for qualitative inputs.

## Key Components
- **MBSE**: Capella setup and SysML v2 integration guides.
- **Converters**: Capella/SysML v2 to GeoJSON scripts.
- **Analysis**: SD and QSEM integration scripts and outputs.
- **Visualization**: ArcGIS Experience Builder configuration and Kumu exports.
- **Automation**: Orchestrated workflows for data refresh and analysis.

## Where to Start
- Project status: [STATUS_REPORT.md](STATUS_REPORT.md)
- Technical summary: [TEAM_SUMMARY.md](TEAM_SUMMARY.md)
- SysML v2 workflow: [docs/SYSML_V2_INTEGRATION.md](docs/SYSML_V2_INTEGRATION.md)
- Capella setup: [docs/CAPELLA_PROJECT_SETUP.md](docs/CAPELLA_PROJECT_SETUP.md)

## Current Focus
- Testing SysML v2 and Capella extraction pipelines
- Narrative-to-model extraction via open-source LLMs
- ArcGIS Experience Builder dashboard build-out
