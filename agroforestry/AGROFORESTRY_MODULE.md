# OSDK Agroforestry Design Module — Architecture Brief

**Module:** `agroforestry/`  
**Version:** 1.0.0 — April 2026  
**Maintainer:** JRBD / Conscious Circle  
**Reference case:** Montalma, Monte da Fóia, Monchique, Portugal  
**Platform context:** Federated Rural OSDK Platform

---

## 1. Vision

The Agroforestry Design Module is a **web-assisted permaculture design environment** integrated into the Federated OSDK Platform. It allows any user — from an individual landowner to a municipality — to move from a GIS site assessment through to a fully specified, implementable agrosilvopastoral landscape plan, with a Bill of Materials (BOM), a Method of Execution List (MEL), and visual stratification outputs.

The module works in both directions:

**Forward:** Site → species selection → stratification design → BOM/MEL → implementation
**Reverse:** Budget → optimised species mix → projected outputs over time

It is the agroforestry equivalent of what the GIS cadastral module is to land analysis: a reusable, country-configurable tool that makes Conscious Circle consulting faster, better, and more scalable.

---

## 2. Design Precedents and Knowledge Sources

### 2.1 Syntropic Agroforestry (Danyadara model, Andalusia)
The Danyadara project in Andalusia demonstrates the core syntropic method for Mediterranean arid conditions:
- Emergent layer: fast-growing pioneer trees (eucalyptus, casuarina) for early shelter
- Pioneer shrubs: tagasaste, myoporum, tree medick, artemisia, rosemary — protect soil and supply early biomass
- Cash crop sequence: Fig → Almond → Apricot → Pomegranate (field-tested syntropic line)
- Vines on living trellises: grapes climbing pepper tree (Roman-inspired)
- Result: barren compacted land → rich topsoil within a decade using chop-and-drop

### 2.2 Native Ground Cover Science (Nature Plants 2024 / Zenodo:3460431)
The AgroForAdapt / University research consortium evaluated 35 native Iberian annual species for:
- Olive farming suitability (trafficability, cover, biodiversity, non-competitive traits)
- Seed farming scalability (mechanisation, yield, market demand)
- Multi-criteria DEXi model scoring

**Top-rated species for Mediterranean systems:**
| Species | DEXi Overall | Olive Farming | Seed Farming | Key Role |
|---|---|---|---|---|
| Bromus hordeaceus | Excellent | Good | Excellent | Living mulch, biomass |
| Bromus scoparius | Excellent | Good | Excellent | Living mulch (compact) |
| Capsella bursa-pastoris | Excellent | Good | Excellent | Dynamic accumulator |
| Misopates orontium | Excellent | Good | Excellent | Pollinator annual |
| Nigella damascena | Excellent | Good | Excellent | Ornamental pollinator |
| Salvia verbenaca | Excellent | Good | Excellent | Aromatic companion |
| Trifolium angustifolium | Excellent | Good | Excellent | Nitrogen fixer |
| Glebionis segetum | Good | Fair | Excellent | Pollinator, mulch |
| Moricandia moricandioides | Good | Fair | Excellent | Ground cover |
| Trachynia distachya | Good | Fair | Excellent | Grass biomass |
| Stachys arvensis | Good | Fair | Excellent | Herb cover |
| Vaccaria hispanica | Good | Fair | Excellent | Ornamental annual |

### 2.3 LIFE AgroForAdapt (ES/CAT/FR, 2021-2026)
EU-LIFE funded project demonstrating agroforestry systems for Mediterranean climate adaptation:
- Demonstrative systems mapped across Spain, Catalonia, and France
- Publications available at agroforadapt.eu/en/publications-agroforadapt/
- BuyAgroforestry marketplace: no Portugal entries — **MASSIVE OPPORTUNITY** for Monchique
- Current network: Spain/Catalonia dominated; Portugal entirely absent from demonstrated map
- Monchique could be registered as the first Portuguese demonstrative site

### 2.4 Iberian Agroforestry Social Network (Landfiles / EFI)
- "Comunidad de sistemas agroforestales y cultivos mixtos" — 157 members (2024), 2/3 farmers
- Hosted on Landfiles (450+ agroecological groups, 9,000 members)
- Projects: LIFE AgroForAdapt, Transition-MED, DigitAF, Agromix, Gov4All
- Quarterly webinars — farmers describe estates, systems, lessons learned
- Spain's EURAF representative since 2024
- **Monchique opportunity**: register as PT node, attend webinars, connect to EU funding network

### 2.5 EURAF 2026 Conference
- 8th European Agroforestry Conference, Neuchâtel, Switzerland, 22-26 June 2026
- Montalma case study + Federated OSDK Platform = submittable abstract
- Deadline likely March-April 2026 (check euraf.net)
- This would be the first international presentation of the platform

---

## 3. Module Architecture

The module is structured as six interconnected layers, mirroring the master OSDK schema:

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: GIS Site Assessment (existing OSDK GIS module)        │
│  Inputs: parcel boundaries, slope, aspect, soil, DEM, cadastre  │
│  Outputs: site_profile.json (slope_zone, moisture, exposure)    │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Species Database (species_database.json)              │
│  35 native annuals (DEXi evaluated) + 40+ perennial crops       │
│  Filterable by: stratum, role, suitability, slope_zone,         │
│  drought_tolerance, frost_tolerance, water_use, DEXi score      │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Stratification Composer (Web GUI)                     │
│  User selects species per stratum layer                         │
│  Visualisation: cross-section profile + plan view               │
│  Outputs: design_composition.json                               │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Guild Compatibility Engine                             │
│  Checks guild_partners, juglone sensitivity, invasive_risk      │
│  Flags incompatibilities, suggests alternatives                 │
│  Outputs: guild_validation_report.json                          │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: BOM + MEL Generator                                   │
│  Bill of Materials: species × quantity × spacing × area         │
│  Method of Execution: phased planting calendar                  │
│  Implementation routes: Quadriga, manual, mechanised            │
│  Outputs: BOM.csv, MEL.md, planting_calendar.ics               │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer 6: Scenario Projections (SD module integration)          │
│  Biomass accumulation, yield projections, carbon, fire risk     │
│  Budget-to-output reverse mode                                  │
│  Outputs: scenario_projections.json → SD module                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Stratification System (7+1 Layers)

The standard permaculture seven-layer system, adapted for Monchique conditions:

| Layer | Code | Height | Monchique Species |
|---|---|---|---|
| Emergent canopy | E | >10m | Chestnut (Castanea), Walnut (Juglans), Carob (Ceratonia), Cork Oak |
| Canopy | C | 5-10m | Olive, Fig, Almond, Apricot, Pomegranate, Macadamia |
| Understory | U | 2-5m | Elderberry, Juniper, Tagasaste, Goji, Pride of Madeira |
| Shrub | S | 0.5-2m | Lavender, Sage, Buddleia, Rosemary, Goji |
| Herbaceous | H | <0.5m | Oregano, Thyme, Salvia verbenaca, Nigella, Bromus spp., Trifolium |
| Ground cover | G | Creeping | Creeping thyme, Capsella, Bromus scoparius (low) |
| Vine | V | Climbing | Chayote, Grapes, Passionfruit |
| Rhizosphere | R | Underground | Potato (early years), Comfrey (miner) |

---

## 5. Slope Zone Planning (Montalma-specific)

South-facing 30-40° slope, Monte da Fóia (400-900m), 1000-2000mm rainfall:

```
RIDGE (>700m)
├── Wind exposure: EXTREME
├── Solar: MAXIMUM
├── Moisture: LOWEST
├── Primary: Juniper windbreaks, Carob, first tagasaste rows
└── Ground: Lavender, Thyme, Salvia verbenaca, Bromus

UPPER TERRACE (600-700m)  
├── Wind: HIGH (protected by ridge windbreak)
├── Solar: VERY HIGH
├── Moisture: LOW
├── Primary: Carob, Olive, Pomegranate, Fig (drought anchor species)
├── Support: Tagasaste nurse rows, Pride of Madeira
└── Ground: Lavender, Oregano, Sage, Thyme, Nigella, Salvia verbenaca

MID TERRACE (500-600m) — THE SWEET SPOT
├── Wind: MODERATE (sheltered)
├── Solar: HIGH — excellent fruit quality zone
├── Moisture: MODERATE (organic matter accumulation from above)
├── Primary: Almond, Walnut, Chestnut (needs deeper soil)
├── Support: Tagasaste, Elderberry (drier end), Goji
└── Ground: Salvia verbenaca, Trifolium angustifolium, Capsella, Potatoes (yr1-4)

LOWER TERRACE / BASE (400-500m) — WATER HARVESTING ZONE  
├── Wind: LOW (most sheltered)
├── Solar: GOOD — morning/afternoon shade opportunity
├── Moisture: HIGHEST
├── Frost risk: MODERATE (thermal inversion — watch frost pockets)
├── Primary: Chestnut, Walnut, Fig (rich conditions), Elderberry, Apricot
├── Sensitive: Macadamia (here only — sheltered microclimate), Chayote
└── Ground: Raspberry, Physalis, Comfrey, Mint (confined), Trifolium
```

---

## 6. Guild Compositions

### Guild A — Upper Terrace Drought Guild
**Anchor:** Carob + Olive  
**Support:** Juniper (windbreak), Tagasaste (N-fix + mulch)  
**Ground:** Lavender + Thyme + Salvia verbenaca + Bromus hordeaceus  
**Function:** Zero-irrigation system once established. Fire-resistant management zone.

### Guild B — Mid Terrace Fruit Guild  
**Anchor:** Almond + Walnut  
**Support:** Tagasaste, Salvia verbenaca  
**Ground:** Trifolium angustifolium (N-fix), Capsella (dynamic accumulator), Nigella damascena (pollinator)  
**Note:** Keep juglone-sensitive species away from Walnut. Use juglone-tolerant companions only.

### Guild C — Syntropic Fruit Line (Danyadara model)
**Sequence:** Fig → Almond → Apricot → Pomegranate  
**Emergent:** Tagasaste (pioneer), potentially Casuarina or native pioneer species  
**Vines:** Grapes on living trellises  
**Ground:** Aromatic carpet (Oregano + Thyme + Lavender)  
**Function:** Mimics Danyadara Andalusia model, proven on rocky poor soils.

### Guild D — Water Zone Guild  
**Anchor:** Chestnut + Elderberry  
**Support:** Comfrey (dynamic accumulator), Raspberry  
**Vine:** Chayote (at base)  
**Ground:** Mint (confined), Trifolium, Strawberry  
**Function:** Highest productivity zone. Water-retentive lower terrace.

### Guild E — Apricot Guild (specific to Montalma)
**Anchor:** Apricot  
**N-fixers:** Tagasaste, Trifolium angustifolium  
**Dynamic accumulators:** Comfrey, Capsella bursa-pastoris  
**Pollinators:** Lavender, Nigella, Salvia verbenaca  
**Pest repellents:** Sage, Garlic, Chives  
**Ground cover:** Strawberry, Bromus scoparius  
**Note:** Avoid frost pockets for apricot blossom.

---

## 7. Web GUI UX/UI Specification

### 7.1 User Types (SNA Nodes)
Following the platform's SNA node typology, the tool serves:
- Individual / household (Montalma landowner)
- Community / cooperative (Monchique rural network)
- Community of communities (regional network)
- Municipality (Câmara Municipal de Monchique)
- Research / NGO (Conscious Circle, EFI, AgroForAdapt)
- Each user type gets a tailored starting template

### 7.2 UX Flow (Forward Mode — Design)
```
Step 1: SITE PROFILE
  ├── Load from GIS parcel or enter manually
  ├── Inputs: area (ha), slope (%), aspect, altitude, rainfall, soil type
  └── Auto-generates: site_profile.json with slope zone classification

Step 2: INTENT SELECTION  
  ├── Primary goal: food forest / productive orchard / fire resilience / carbon / biodiversity
  ├── Scale: household / smallholder / commercial
  └── Implementation method: manual / Quadriga / mechanised / professional service

Step 3: SPECIES COMPOSER
  ├── Auto-suggested palette based on site profile
  ├── User can add/remove species per stratum layer
  ├── Toggle view: by stratum layer / by ecological role / by cash value / by DEXi score
  └── Guild compatibility check runs in real-time

Step 4: STRATIFICATION VISUALISER
  ├── Cross-section profile view (SVG/Canvas)
  ├── Plan view (top-down, showing spacing)
  ├── Slope-zone heatmap (which species goes where on the slope)
  └── Export: PNG / SVG / PDF blueprint

Step 5: BOM + MEL
  ├── Bill of Materials: species, quantity, planting stock type, source, unit cost, total
  ├── Method of Execution: phased calendar (Year 1-5 installation sequence)
  ├── Watering, mulching, pruning schedule
  └── Export: CSV, PDF, iCal

Step 6: SCENARIO PROJECTIONS
  ├── 10-year biomass, yield, and fire risk projections
  ├── CO2 sequestration estimate
  └── Revenue projection by species category
```

### 7.3 UX Flow (Reverse Mode — Budget to Output)
```
Input: budget (€), area (ha), implementation method
Output: recommended species mix + projected timeline + yield estimate
Logic: species database × unit cost × quantity per ha → optimise for budget
```

### 7.4 Visual Style
Inspired by landscape architecture practice but technically grounded:
- Not photorealistic renders — use illustrated cross-section profiles
- Layer-coded colour palette per stratum (E=dark green, C=medium green, etc.)
- Species represented as stylised silhouette icons (SVG library)
- Print-quality PDF export for field use
- Future: optional AI-assisted photorealistic visual of "mature system" for stakeholder presentations

---

## 8. BOM / MEL Template

### Bill of Materials (BOM) fields
| Field | Description |
|---|---|
| species_code | Internal code from species_database.json |
| common_name | Common name |
| scientific_name | Latin binomial |
| stratum | Layer code |
| qty_per_ha | Recommended planting density |
| qty_total | For this site area |
| stock_type | seed / plug / bare_root / pot / cutting |
| source | nursery / self-propagated / wild collection |
| unit_cost_eur | Approximate per unit |
| total_cost_eur | qty_total × unit_cost |
| planting_phase | Year 1 / Year 2 / Year 3+ |
| slope_zone | Where on slope |
| notes | Special instructions |

### Method of Execution List (MEL) phases

**Phase 0 — Site Preparation (Pre-plant)**
- Topographic survey and contour mapping
- Soil test (pH, nutrients, water retention)
- Swale / water-bund layout on contour lines
- Access track planning for Quadriga / machinery

**Phase 1 — Windbreak and Nitrogen Fixers (Year 1, Autumn)**
- Plant Juniper on ridge and upper terrace margins
- Plant Tagasaste rows along upper terrace contours (living windbreak + N-fix)
- Sow Bromus hordeaceus / B. scoparius as living mulch on all terraces
- Plant Salvia verbenaca, Trifolium angustifolium across mid terraces

**Phase 2 — Main Canopy (Year 1-2, Winter-Spring)**  
- Plant Carob, Olive, Pomegranate, Fig on upper terraces
- Plant Almond, Walnut on mid terraces
- Plant Chestnut, Elderberry on lower terraces
- Interplant Potatoes in alleys between young trees

**Phase 3 — Understory and Cash Herbs (Year 2-3)**
- Plant Goji, Pride of Madeira, Lavender, Oregano, Thyme
- Plant Apricot (mid-lower terrace, frost-protected positions)
- Establish Comfrey, Capsella in dynamic accumulator positions

**Phase 4 — Sensitive Species (Year 3-4, established microclimate)**
- Plant Macadamia in most sheltered lower microclimate
- Plant Chayote, Raspberry at terrace base / water zone
- Confine Mint near water source

**Phase 5 — Transition (Year 4-5)**
- Remove Potato alleys as canopy closes
- Introduce Physalis, additional fruiting shrubs
- Establish seed production plots for native annual species (nursery income stream)

---

## 9. Nursery Integration

### Montalma Agroforestry Nursery — Strategic Rationale
The species database creates a natural nursery business model:
- Propagate the 35 native annual species for seed sale (commercial market)
- Propagate tagasaste, lavender, salvia verbenaca, trifolium for regional agroforestry projects
- Register on AgroForAdapt BuyAgroforestry portal (currently zero Portugal entries)
- Connect to Iberian Agroforestry Pioneer Network (Landfiles platform, 157 members)
- Become the Portuguese node in the EU LIFE network

**Highest-value nursery species (by DEXi seed farming score + market demand):**
1. Salvia verbenaca — Excellent DEXi, High market demand
2. Nigella damascena — Excellent DEXi, High market demand
3. Capsella bursa-pastoris — Excellent DEXi, High demand
4. Glebionis segetum — Excellent seed farming, High demand
5. Bromus scoparius — Highest seed yield in dataset (224,496 seeds/m²)
6. Trifolium angustifolium — N-fix, clover market
7. Echium plantagineum — Good pollinator, growing demand
8. Medicago polymorpha — Excellent yield potential, high demand

---

## 10. Integration with Federated OSDK Platform

### 10.1 GIS Module → Agroforestry Module
```python
# site_profile from GIS assessment
site = {
  "parcel_id": "MON-045",
  "area_ha": 2.3,
  "slope_pct": 35,
  "aspect": "south",
  "altitude_m": 580,
  "rainfall_mm": 1400,
  "soil_type": "foite_schist_acidic",
  "frost_risk": "low_moderate"
}
# → auto-assigns slope zones → filters species_database.json
```

### 10.2 SNA Module → Agroforestry Module
- Landowners in SNA graph map to Montalma parcels in GIS
- Cooperative membership links to shared nursery production
- Municipal actors link to CAP subsidy eligibility for agroforestry

### 10.3 SD Module → Agroforestry Module
- System dynamics scenario: biomass accumulation over 10 years
- Fire risk reduction under different species compositions
- Governance scenarios: collective vs individual management

### 10.4 MBSE → Agroforestry Module
- Agroforestry system = MBSE system architecture
- Species = components
- Guilds = subsystems
- Ecological roles = functions
- Phenological calendar = operational sequence

---

## 11. AgroForAdapt Portugal Opportunity

The AgroForAdapt demonstrative systems map currently shows **zero Portuguese entries**. This is simultaneously a gap and an opportunity.

**Immediate actions:**
1. Register Montalma as a proposed Portuguese demonstrative site via agroforadapt.eu/en/contact/
2. Contact LIFE AgroForAdapt team — offer to be Portugal case study partner
3. Join the Landfiles "Comunidad de sistemas agroforestales y cultivos mixtos" network
4. Submit abstract to EURAF 2026 (Neuchâtel, June 2026) — Monchique case study + OSDK Platform
5. Engage Câmara Municipal de Monchique as institutional co-partner

**Positioning:** Monchique is the only European municipality with a formally documented systems engineering approach to rural agroforestry planning. The OSDK platform is the analytical backbone that no other Portuguese site has.

---

## 12. Files in this Module

| File | Description |
|---|---|
| `AGROFORESTRY_MODULE.md` | This document — full architecture and specification |
| `species_database.json` | 40+ species with full attributes, DEXi scores, production traits |
| `montalma_design_v1.json` | Montalma site-specific design composition (TBD) |
| `guild_compositions.json` | Tested guild configurations for Monchique conditions |
| `BOM_template.csv` | Bill of Materials template |
| `MEL_template.md` | Method of Execution List template |
| `nursery_species_ranking.csv` | Species ranked by nursery commercial potential |

---

*Federated Rural OSDK Platform v1.0 | Conscious Circle | April 2026*
