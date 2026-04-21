# Federated Rural OSDK Platform — Claude Master Context Brief

**Prepared:** 19 April 2026  
**Last amended:** 20 April 2026  
**Purpose:** Paste-ready technical context for qualitative, conceptual, and systems-architecture development.

---

## 1. Project mission

The Federated Rural OSDK Platform is a federated territorial intelligence environment for rural planning and governance. It is designed to connect formal systems engineering, geospatial truth, participatory review, network intelligence, qualitative systems reasoning, and scenario analysis into one interoperable architecture.

The current reference case is **Monchique, Portugal**.

The project is intended to support:
- place-based rural development planning
- parcel-scale land analysis
- governance and stakeholder coordination
- intervention design such as berm corridors and landscape management strategies
- traceable movement from conceptual design to spatial decision support

---

## 2. Core architectural principle

The platform is not a single monolithic model. It is a **federated multi-model stack** in which each discipline provides a different view of the same rural system:

- **MBSE / Capella** provides formal structure, decomposition, interfaces, and requirements logic.
- **QSM / QSEM / CLD** provides qualitative causal reasoning, stakeholder narratives, and feedback structure.
- **System Dynamics** provides temporal behavior and scenario logic.
- **SNA / Kumu** provides actor-network and governance topology.
- **GIS / Cadastre** provides authoritative spatial anchoring.
- **n8n / orchestration** provides automated coordination between tools and outputs.

Each of these should be treated as a federated representation over a shared conceptual schema.

---

## 3. Shared master data schema

All future conceptual work should fit a common master schema composed of:

### Core object types

#### Place / spatial unit
- municipality
- parish / freguesia
- parcel
- corridor
- zone
- intervention area
- project site
- risk surface

#### Actor / institution
- municipality
- landowner
- cooperative
- NGO
- civil protection
- regulator
- utility
- stewardship body
- community organization

#### Asset / infrastructure
- building / edificado
- water point
- access route
- berm
- vegetation strip
- treatment area
- monitoring asset

#### System variable
- fire risk
- fuel load / biomass
- governance capacity
- fragmentation pressure
- accessibility
- support level
- ecological suitability
- water availability

#### Intervention / process
- parcel aggregation
- berm corridor implementation
- clearing / maintenance regime
- restoration effort
- governance coordination process
- stewardship agreement

### Relationship types
- contains
- located_in
- adjacent_to
- owned_by
- managed_by
- influences
- depends_on
- regulates
- collaborates_with
- causes / reinforces / balances
- participates_in
- constrains

This schema should be treated as the foundation for all later blocks, nodes, variables, and architectures.

---

## 4. Current implementation status

### A. Documentation and workflow layer
The repository includes extensive documentation covering:
- quick start and federated workflow guidance
- ArcGIS setup and downstream integration
- Capella setup
- QSEM integration
- SNA / Kumu integration
- system dynamics integration
- webhook and n8n orchestration guidance

This forms the operational handbook for the platform.

### B. MBSE / export layer
The system already exports model content into geospatially usable formats, including:
- federated model GeoJSON
- edited/community-reviewed GeoJSON
- SD-enriched GeoJSON
- change summaries

This is the main bridge from Capella/MBSE structures into GIS and analysis workflows.

### C. GIS cadastral module
A live Portugal cadastre integration has been implemented and tested.

Verified technical details:
- authoritative live source: **DGT OGC API**
- correct collection identifier: **cadastro**
- Portugal endpoint tested live and functioning
- parcel export and indexing workflow working locally

**Added April 2026 — Global Cadastral Registry (`gis/` module):**
- `gis/gis_cadastre_registry.json`: queryable database of cadastral sources for 45 countries across 9 regions plus 10 global fallback sources. Covers OGC API, WFS, WMS, bulk download, and manual routes. Access tiers: open, open_registration, restricted, commercial, manual. CC-BY 4.0 and license metadata per source.
- `gis/query_cadastre_registry.py`: interactive CLI — `--country`, `--list`, `--access`, `--global-fallbacks`, `--export` flags.
- `gis/fetch_cadastro.py`: generic OGC API + WFS fetcher, auto-configured per country from the registry, with pagination and error handling.
- `gis/GIS_MODULE_README.md`: full documentation with QGIS/ArcGIS integration, attribution table, and pipeline connection instructions.

This module is designed to be reusable for Conscious Circle international consulting engagements in any country.

### D. Monchique QGIS analysis layer
A ready-to-use local QGIS project has been created for Monchique.

Verified current state:
- Monchique municipality boundary loaded
- 3 internal parish/freguesia boundaries loaded
- clipped Monchique cadastre loaded
- **10,543** parcels in the current clipped municipal cadastre
- satellite basemap integrated
- misplaced conceptual demo overlays removed from the operational layout

### E. Property portfolio / analysis backend
A parcel selection and property portfolio workflow has been added.

It can:
- search parcels by cadastral reference
- search by label or numeric parcel id
- filter by administrative unit
- filter by area range
- append selected parcels into a portfolio layer
- generate a summary markdown file
- generate a fragmentation baseline report

This supports future work such as property portfolio development and berm corridor scenario analysis.

---

## 5. Technical multidisciplinary integration model

### 5.1 MBSE / Capella integration

**Role:** formal architecture backbone.

This layer should represent:
- stable system modules
- requirements and traceability
- interfaces and exchanges
- functional decomposition
- system boundaries and subsystem roles

In this project, Capella-derived blocks should correspond to durable components such as:
- cadastral ingestion subsystem
- territorial intelligence subsystem
- participatory validation subsystem
- analytics subsystem
- orchestration subsystem
- reporting/dashboard subsystem

**Modeling rule:** only create MBSE components that can later map to a real entity, process, asset, or service in the shared schema.

---

### 5.2 QSM / QSEM / CLD integration

**Role:** qualitative causal logic and narrative reasoning layer.

This layer captures:
- stakeholder interpretations
- feedback loops
- governance tensions
- leverage points
- problem framing
- causal hypotheses for interventions

It already has implementation traces in the repo through CLD exports and QSEM output files.

**Mapping rule:**
- causal factors should map to shared system variables
- feedback loops should map to typed relationship structures
- qualitative statements should be convertible into SD variables, SNA edges, or GIS-relevant intervention logic

This is essential for keeping qualitative reasoning compatible with later formalization.

---

### 5.3 System Dynamics integration

**Role:** time-based scenario engine.

This layer supports reasoning about:
- how fragmentation evolves over time
- how management capacity changes risk
- how interventions influence fire exposure, biomass, access, and suitability
- what reinforcing or balancing processes shape rural outcomes

Current project implementation already includes SD integration scripts and SD reports.

**Modeling rule:**
- stocks should represent accumulations or system states
- flows should represent change processes
- auxiliaries should represent management, ecological, social, or policy modifiers
- every SD variable should link to the shared schema and, ideally, to a measurable indicator

---

### 5.4 SNA / Kumu integration

**Role:** actor-network and governance topology layer.

This layer is used to represent:
- who collaborates with whom
- institutional bottlenecks
- trust and influence patterns
- dependency chains
- central or peripheral actors in implementation

Current repo implementation already includes:
- Kumu exports
- GraphML and CSV outputs
- node/edge tables
- SNA reports

**Modeling rule:** node types and edge types should always be explicit and typed, for example:
- nodes: actor, institution, landholding cluster, project, governance body, infrastructure owner
- edges: collaborates_with, funds, regulates, depends_on, manages, informs, constrains

This keeps the network model interoperable with downstream tooling.

---

### 5.5 GIS / cadastre integration

**Role:** authoritative spatial grounding layer.

This is the territorial substrate that anchors all other model views to real geography.

The platform now supports:
- municipal and internal boundaries
- parcel-level cadastre
- selection of individual parcels into dedicated layers
- portfolio building for later intervention analysis
- reserved scenario layers such as berm corridor analysis
- global cadastral data acquisition for any country via the `gis/` module

**Design rule:** conceptual objects should be locatable wherever possible. If a block, variable, intervention, or governance process has spatial relevance, it should ultimately be mappable to a parcel, corridor, project site, or administrative unit.

---

## 6. Orchestration and data flow

The orchestration layer is intended to automate the transfer of information across the multidisciplinary stack.

### Current orchestration components
- Docker Compose infrastructure
- n8n workflows
- webhook-based pipeline steps
- MBSE bridge scripts

### Intended high-level pipeline
1. MBSE / model content is exported or updated
2. GeoJSON or structured outputs are generated
3. spatial features are loaded into GIS / QGIS / ArcGIS
4. participatory edits are captured
5. SNA, SD, and QSEM analyses run downstream
6. outputs are fed back into visualization, reporting, and decision support

This architecture supports a traceable, iterative, federated loop rather than a one-way export chain.

---

## 7. Current Monchique-specific operational picture

The Monchique case now has a functioning local analysis environment with:
- satellite basemap
- municipality boundary
- 3 freguesia boundaries
- 10,543 clipped cadastral parcels
- property portfolio selection workflow
- fragmentation report baseline
- reserved berm corridor scenario layer
- global cadastral registry for extending the approach to other countries

The current operational emphasis is on using real cadastral polygons for property portfolio development and later corridor or fragmentation analysis.

---

## 8. Constraints and known limitations

### Historical parcel lineage
The current open cadastral feed provides present parcel geometry and attributes but does not provide a rich public historical inheritance/subdivision timeline.

A serious longitudinal fragmentation study will likely require additional archival or registry sources.

### Built structures / Edificado
The municipal web tool exposes useful built-structure layers, including legally recognized buildings, but these have not yet been integrated into the current local workflow.

### Conceptual-to-spatial precision
The project has already removed misleading demo overlays from the main Monchique layout. Future conceptual elements should only be reintroduced when they map properly to the shared schema and, ideally, to real spatial units.

---

## 9. Design instructions for future Claude work

When generating new conceptual models, system architectures, blocks, loops, or nodes, Claude should follow these rules:

### Rule 1 — schema fit
Every concept should fit one or more of the master schema categories:
- place
- actor
- asset
- variable
- intervention
- relationship

### Rule 2 — multidisciplinary compatibility
A useful concept should be expressible in at least two of these lenses:
- MBSE
- QSM / CLD
- SD
- SNA
- GIS

### Rule 3 — traceability
Every major element should be traceable to at least one of:
- a system function
- a spatial unit
- a governance relationship
- a measurable indicator
- a scenario role

### Rule 4 — no isolated abstractions
Avoid introducing blocks or variables that cannot later become:
- a data field
- a graph node
- a GIS layer
- a scenario component
- a requirement or interface in MBSE

### Rule 5 — later formalization
Conceptual development should remain convertible into implementation structures such as:
- Capella components
- SD variables
- SNA nodes/edges
- GIS polygons or layers
- reporting/dashboard outputs

---

## 10. High-value conceptual development directions

The most promising near-term conceptual directions are:

### A. Fragmentation architecture
Develop a formal explanation of how intergenerational parcel division creates:
- sliver parcels
- management inefficiency
- governance complexity
- ecological and fire-risk vulnerability
- intervention difficulty

**Current status:** 10,543 Monchique parcels available in QGIS. Fragmentation baseline report scaffolded. Analytical work not yet started.

### B. Berm corridor architecture
Develop a cross-disciplinary system concept tying together:
- corridor geometry and placement
- affected parcels and landholders
- governance and implementation actors
- scenario logic and SD outcomes
- operational stewardship requirements

**Current status:** scenario layer reserved in QGIS. Architecture not yet developed.

### C. Governance operating model
Define which actors must coordinate across municipal, landholding, ecological, and civil protection functions and how the platform supports that coordination.

**Current status:** SNA nodes and edges exist for Monchique cooperative/municipality/entity level. Operating model not yet formalised.

### D. Edificado / built-asset integration
Prepare a schema extension for legally recognized buildings and their relationship to parcels, access, services, and exposure.

**Current status:** not started. Municipal web portal exposes this layer; integration pending.

---

## 11. Broader SERAPH / personal context

This platform sits within the larger **SERAPH** personal development system:

- **ASEP exam target:** 31 August 2026 — hard deadline, binary outcome.
- **MDEF / Fab Lab Barcelona application:** early 2027, for September 2027 start.
- **Conscious Circle consulting:** active, revenue-generating. Sports Signage (€2,500–3,000/mo) + Conscious Circle (ramping). The platform is a live Conscious Circle consulting asset.
- **ORBIT finance module:** local SERAPH finance dashboard (Flask/HTML), tracking income and runway toward MDEF tuition (€11,000 Sep 2027 + €22,000 Sep 2028).

### Notion workspace overview (as of 20 April 2026)
Key pages visible via Notion MCP:
- **Federated OSDK Model** — main project page (last edited 19 April 2026)
- **Conscious Circle Deliverables** — active deliverables tracker
- **Location Intelligence** — spatial/GIS intelligence page
- **Learning** — study and course tracking
- **GIS WIKI** — GIS reference page
- **DataSources** — data sources catalogue
- **MIT SysML (database)** — projects tracker with MIT course entries
- **Job & Work Opportunity Applications** — pipeline tracker
- **Solar Algarve, Quadriga, Biochar, Fire** — active or pending project pages
- **EURAF 2026 application** — conference application (June 2026, Neuchâtel)
- **SDG Hyperlocal Data Pipeline Project** — potential Conscious Circle service
- **JRBDs Website 2026** — personal portfolio website planning

The Notion workspace is currently being restructured to interlink with SERAPH, ORBIT, and this platform via MCP. The restructuring should treat Notion as the **human-readable narrative layer** for content that lives technically in GitHub and the local SERAPH/OSDK stack.

---

## 12. Prioritisation guidance (April 2026)

The three parallel tracks and their relative urgency:

| Track | Deadline | Current risk |
|-------|----------|-------------|
| ASEP exam | 31 Aug 2026 | Study hours being crowded out by platform work |
| MDEF portfolio | Early 2027 | No visible end-to-end output exists yet |
| Conscious Circle / OSDK platform | Flexible | Absorbing disproportionate energy |

**Recommended next actions in order:**
1. Protect the 08:00–09:00 daily ASEP study block without exception.
2. Produce one visible, explainable portfolio output from the 10,543 Monchique parcels (fragmentation analysis notebook). This is what MDEF reviewers need to see.
3. Commit the ARCHITECTURE.md to the repo so the platform narrative is preserved and shareable. ✅ Done 20 April 2026.
4. Notion restructuring: treat as a background task, not a blocker. Connect pages to GitHub via links, not by rebuilding the platform inside Notion.
5. Web GUI / Mapbox interface: post-ASEP work.

---

## 13. One-paragraph technical summary

The Federated Rural OSDK Platform is a federated territorial intelligence architecture that integrates Capella-based MBSE, qualitative systems mapping, system dynamics, social network analysis, GIS/cadastre, and orchestration workflows through a common master schema of places, actors, assets, variables, interventions, and relationships. Its current Monchique implementation provides a functioning parcel-level analysis environment with live cadastral data, portfolio selection capability, a global cadastral data registry covering 45 countries, and a structured pathway for future qualitative and technical systems development. The platform is a live asset for Conscious Circle rural development consulting and a core component of the MDEF portfolio application.
