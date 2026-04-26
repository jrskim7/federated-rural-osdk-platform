# OSDK Agroforestry Module — Extended Technical Brief
## Syntropic Design Geometry, Propagation, Permaculture Process, Mechanisation & Data Sources

**Module:** `agroforestry/`  
**Version:** 1.1.0 — April 2026  
**Maintainer:** JRBD / Conscious Circle  
**Reference case:** Montalma, Monte da Fóia, Monchique, Portugal  

---

## PART 1: EURAF / CONFERENCE PIPELINE REMINDER

**EURAF 2026** (Neuchâtel, 22-26 June 2026):
- Abstract deadline **PASSED** (23 March 2026)
- Conference still worth attending as participant — tracks "Agroforestry systems design" and "Farmer-friendly agroforestry / technology / digitalisation" are directly relevant
- Photo contest open via digitaf.eu

**EURAF 2028** (biannual — location TBC):
- ⏰ **Reminder set:** Begin abstract preparation **September 2027**
- Target abstract deadline: **January 2028**
- Abstract theme: "Federated Territorial Intelligence for Rural Agroforestry Planning — A Systems Engineering Approach Applied to Monchique, Portugal"
- Pre-requisites: Montalma registered on AgroForAdapt + Landfiles by end of 2027

**Other relevant conferences to track:**
- Iberian Agroforestry Pioneer Network (Landfiles) — quarterly webinars, join immediately
- PRIMA / EuroMed agricultural conferences — relevant for Mediterranean agroforestry
- EURAGE / FAO — European sustainable land use

---

## PART 2: EXISTING PLANTS AS STARTING CAPITAL — INVENTORY-FIRST DESIGN PHILOSOPHY

### The Non-Blank-Canvas Principle

Every site assessment begins with what is already there. Existing vegetation is not just context — it is capital: propagation stock, ecological function already in place, and evidence of what the site will support.

The platform should implement an **Existing Inventory Layer** as the mandatory first step in any design workflow, before any new species are suggested. This inventory drives three downstream processes:

1. **Propagation potential** — which existing plants can generate new stock for expansion
2. **Ecological reading** — what existing plants tell you about soil, water, and microclimate
3. **Succession stage identification** — where is the site in its ecological succession timeline?

### Montalma Existing Inventory (to be expanded in field)

| Common name | Scientific name | Location | Condition | Propagation potential | Priority |
|---|---|---|---|---|---|
| Goji Berry | Lycium barbarum | Zone 1 mid-terrace | 1 strong survivor from many cuttings | High — established mother stock | Expand by cutting |
| Fig | Ficus carica | Multiple terrace walls | Established | Very high — hardwood cuttings | Self-propagate now |
| Agave | Agave sp. | Terrace front edge | Established | Medium — pups/offsets | Terrace stabilisation |
| Geranium | Pelargonium sp. | Various | Established | High — stem cuttings | Expand in pest-repellent zones |
| Chuchu/Chayote | Sechium edule | Lower terrace | Established (experimental) | Medium — fruit/tuber | Continue low zone trial |
| Cascading Rosemary | Rosmarinus prostrata | Terrace fronts | Established (experimental) | High — tip cuttings | Expand as terrace-face cover |
| Chestnuts | Castanea sativa | Mountain (native) | Wild | High — acorn/seed, grafting | Propagate from local ecotype |
| Almonds | Prunus dulcis | To confirm | Starter stock held | High — hardwood cutting, grafting | Plant when ready |
| Elderberry | Sambucus nigra | To confirm | Starter stock held | High — hardwood cuttings | Lower water zone |
| Lavender | Lavandula sp. | Starter stock | Multiple | High — softwood cuttings | Expand garrigue layer |
| Oregano | Origanum vulgare | Starter stock | Multiple | Very high — division | Expand aromatic layer |
| Thyme | Thymus sp. | Starter stock | Multiple | Very high — layering/cutting | Ground cover layer |
| Purple Sage | Salvia sp. | Starter stock | Multiple | High — softwood cuttings | Aromatic/pest layer |
| Tagasaste | Cytisus proliferus | Starter stock | Present | High — seed | Nurse plant priority |
| Physalis | Physalis peruviana | Starter stock | Present | High — seed | Annual rotation |
| Macadamia | Macadamia sp. | Starter stock | Present | Medium — air layering | Sheltered zone only |
| Raspberry | Rubus idaeus | Starter stock | Present | Very high — cane division | Lower water zone |
| Juniper | Juniperus sp. | Starter stock | Present | Medium — cuttings | Windbreak priority |

**Key lesson from the Goji case:** A single strong survivor from many failed cuttings is a valuable data point AND a valuable asset. The platform should record propagation attempts and success rates, not just plant presence.

---

## PART 3: PLANT PROPAGATION METHODS — PLATFORM KNOWLEDGE BASE

Each species in `species_database.json` should carry a `propagation` object covering all applicable methods. This is the knowledge base for the propagation module.

### Propagation Method Taxonomy

```
VEGETATIVE (asexual — clones of mother plant)
├── Cuttings
│   ├── Softwood (spring — new growth, high humidity needed)
│   ├── Semi-hardwood (summer — partially mature)
│   └── Hardwood (autumn/winter — dormant, most robust)
├── Division (clump-forming plants — oregano, mint, comfrey)
├── Layering
│   ├── Simple layering (bury stem, still attached to mother)
│   ├── Mound/Stool layering (heap soil over crown)
│   └── Air layering (wrap aerial shoot in moist medium)
├── Suckers / Basal shoots (tagasaste, raspberry, fig)
├── Offsets / Pups (agave, banana, aloe)
├── Grafting
│   ├── Whip-and-tongue
│   ├── Cleft graft
│   └── Bud grafting (T-bud, chip bud) — for fruit trees
├── Micropropagation / Tissue culture (advanced — lab setting)
│   ├── Meristem culture
│   └── Callus culture
└── Bulb / Tuber / Rhizome division (lily, potato, mint, ginger)

SEXUAL (seed — genetic variation, some breeding)
├── Direct sowing (in situ — grasses, annuals, nitrogen fixers)
├── Nursery raising (pot on, transplant)
├── Seed stratification (cold for dormancy breaking — chestnuts)
├── Scarification (hard seed coats — carob, tagasaste)
└── Soaking (legumes, carob 12-24h)
```

### Propagation Parameters Per Species (to add to species_database.json)

Each species entry should include:
```json
"propagation": {
  "primary_method": "hardwood_cutting",
  "secondary_methods": ["seed", "layering"],
  "best_season": "autumn_winter",
  "rooting_medium": "perlite_vermiculite_mix",
  "rooting_hormone_required": false,
  "success_rate_typical_pct": 70,
  "time_to_transplant_weeks": 8,
  "seed_stratification": null,
  "seed_scarification": false,
  "notes": "Take 20-25cm cuttings from non-fruiting shoots. Remove lower leaves. Dip in honey or willow water as rooting stimulant alternative."
}
```

### Montalma-Specific Propagation Constraints and Opportunities

**Water availability:** The incomplete dam at the top of the property is a key strategic asset for propagation infrastructure. A mist propagation house requires consistent water. Until the dam is operational, use terrace-level captured water (bunds, small cisterns) for nursery irrigation.

**Bentonite dam note:** Bentonite clay lining is proven and cost-effective but requires:
- Fencing before installation (cattle hoof penetration destroys lining)
- 15cm compacted bentonite layer (0.5kg/m²)
- No root penetration in base zone
- Alternative: HDPE liner + bentonite composite

**Propagation infrastructure sequencing:**
1. Build small (~20m²) shade house from local timber and shade cloth (immediate)
2. Establish mist propagation bench with drip irrigation from existing water point
3. Propagate high-priority species from existing stock (Goji, Fig, Rosemary, Lavender, Sage)
4. Expand dam / water capture as capital allows — this unlocks larger-scale nursery operation

---

## PART 4: SYNTROPIC GEOMETRY — THE TRIANGLE SYSTEM

This is the core spatial design grammar for the platform's visualisation engine.

### The Above-Ground Triangle (Side View)

Syntropic systems use stratification that arranges plants vertically according to their light requirements and temporally according to their role in succession. The visual geometry that results from this is a **stacking triangle** where:

```
SIDE VIEW OF A SYNTROPIC LINE:

Height
  |         /\
E |        /  \   Emergent (Chestnut, Carob, Walnut)
  |       /    \
C |      / Crop \  Canopy (Olive, Almond, Fig, Apricot)
  |     /        \
U |    /  Support  \ Understory (Tagasaste, Elderberry, Juniper)
  |   /             \
S |  /  Herbs/Cover  \ Shrub/Herb (Lavender, Sage, Thyme)
  | /                 \
G |/___________________\ Ground cover (Bromus, Trifolium, Thyme creeping)
  ←── intra-row width ──→
```

The triangle represents the **light cone** — at full canopy the highest species casts light onto the lower species in a predictable geometric relationship. The rule is: each lower stratum must receive sufficient light diffused from the gaps between the taller stratum above it.

### The Below-Ground Inverted Triangle (Root System)

```
BELOW GROUND:
Ground level ___________________________________
             \                                 /
              \       Annual roots             /
               \    (herbs, ground cover)     /
                \                            /
                 \    Shrub layer roots      /
                  \                        /
                   \   Tree tap roots     /
                    \                   /
                     \  Deep tap roots /
                      \               /
                       \  (Walnut,   /
                        \  Carob,   /
                         \Chestnut /
                          \_______/
```

The deeper the root, the more access to subsoil minerals and moisture — this is the **dynamic accumulator principle** expressed geometrically. Root diversity = nutrient diversity = no competition at the soil chemistry level.

The combined above + below ground shape is a **double diamond** or **hexagonal form** — the most stable natural structure, found from bee honeycombs to carbon molecules. This is literally what a healthy plant community looks like in cross-section.

### The Top-View Triangle (Plan View — Crown Projection)

```
TOP VIEW (looking down at mature canopy):

   E1          E2
    ◉ ←4-6m→  ◉
   / \        / \
  /   \      /   \
C1    C2   C3    C4       (canopy species circles = crown spread)
◎    ◎    ◎    ◎
  \/      \/
  U1      U2              (understory — fits in the gaps)
  ○       ○
    S1  S2  S3             (shrub/herb — fills remaining space)
    •   •   •
```

**Key rule:** Crown circles of the same stratum must NOT overlap at maturity (light competition). Crown circles of adjacent lower strata CAN overlap with higher strata crowns (they're under the canopy). Between two emergent trees, the space should form two opposing half-triangles meeting at their tips — ensuring light reaches ground level at the midpoint.

### The Terrace Cross-Section (Monchique-specific geometry)

```
CROSS-SECTION OF 5-8m TERRACE (viewed from the side):

        ROCK WALL (thermal mass, windbreak)
        ║
        ║  ← 20-30cm
        ║  Climbing/hanging species on wall face
        ║  (grapes, passionfruit, cape gooseberry)
        ║
        ║← 2m →║← syntropic main line (E/C/U triangle) ←
        ║                                              ║
        ║  QUADRIGA access path (1.2-2m clearance)     ║
        ║                                              ║
        ╠══════════════════════════════════════════════╣
        ║                                              ║
        ║  Productive front rows (declining in height) ║
        ║  Zone: lavender → oregano → thyme → edge     ║
        ║  (driest zone at terrace edge)               ║
        ║                                              ║
        ║← 1.2m Quadriga width →                      ║
        ╚══════════════════════════════════════════════╝
        ← TERRACE EDGE (driest, most exposed) ←
```

**Terrace front zone (currently experimentally planted):**
- Agave (excellent — xeric, structural, propagates by pups)
- Geranium (good — pest repellent, adaptable)
- Chuchu (lower terraces only — moisture-dependent)
- Cascading Rosemary (excellent — drought tolerant, aromatic, erosion control)

**Suggested additions for terrace face/front zone:**
- *Aptenia cordifolia* (Ice plant) — succulent, xeric, erosion control
- *Santolina chamaecyparissus* (Cotton Lavender) — aromatic, drought, grey foliage
- *Centranthus ruber* (Red Valerian) — drought, pollinator, self-seeds on walls
- *Sedum sp.* (Stonecrop) — wall coloniser, xeric
- *Artemisia arborescens* (Tree Wormwood) — aromatic, pest repellent, drought
- *Aloe vera* — medicinal, xeric, propagates by pups
- *Carpobrotus edulis* (caution: invasive in some contexts) — but excellent coverage

### Intra-Row and Inter-Row Spacing Principles

**Syntropic main line spacing (backed against terrace wall):**
- Emergent species (Chestnut, Carob): 6-8m apart (final crown diameter ~6m)
- Canopy species between emergent: 3-4m (Fig, Almond, Olive)
- Understory between canopy: 1.5-2m (Tagasaste, Elderberry)
- All planted as close as 0.5m initially — thinned/pruned over time (succession)
- Distance from wall: 1.5-2m (Quadriga maintenance access to wall side)

**Front productive rows (bio-intensive commercial spacing):**
- Lavender: 60-80cm × 60-80cm (commercial production density)
- Oregano: 30-40cm × 30-40cm
- Thyme: 20-30cm × 20-30cm (creeping) or 40cm × 40cm (upright)
- Between rows: minimum 70cm (Quadriga narrow mode at 1.2m straddles one row)
- Row orientation: parallel to terrace contour (never up-down slope)

**Inter-row path spacing for Quadriga:**
- Minimum path width: 1.2m (Quadriga narrow chassis)
- Preferred path width: 1.5m (comfortable operational clearance)
- Row width: 0.8-1.2m planted bed
- System module: 1.5m path + 1.0m bed = 2.5m repeating unit

---

## PART 5: QUADRIGA INTEGRATION — DESIGN FOR MECHANISATION

### The Mechanisation-First Design Principle

The single biggest failure in residential and community agroforestry is designing a beautiful, functional system that can only be maintained by large collective labour. The platform must enforce a **mechanisation constraint** at the design stage, not as an afterthought.

**Every design output must validate:**
- [ ] Minimum row spacing ≥ 1.2m (Quadriga narrow mode)
- [ ] Preferred row spacing ≥ 1.5m (operational clearance)
- [ ] Syntropic main line set 1.5-2m from terrace wall (maintenance access)
- [ ] No overhead obstacles < 2m in Quadriga travel paths
- [ ] Cover crop height in paths ≤ 40cm (Quadriga 80cm clearance — currently TBC/V&V pending)
- [ ] Minimum turning radius accommodated at terrace ends
- [ ] Access point to each terrace defined in the layout

### Quadriga Technical Parameters (Current R&D Status — Pending V&V)

| Parameter | Current Design | Status | Notes |
|---|---|---|---|
| Narrow chassis width | 1.2m | Proposed | Minimum working mode |
| Wide chassis width | 2.0m | Proposed | For wider inter-row work |
| Chassis adjustability range | 1.2-2.0m | Pending V&V | Key MBSE requirement |
| Ground clearance | 80cm | Proposed, TBC | Cover crop compatibility |
| Terrain capability | Steep terraces, 30-40° | Under development | Serra de Monchique target |
| Drive system | Electric, 6/8 wheel | Options under evaluation | OEM Chinese platforms as alternatives for large-scale |
| Payload capacity | TBC | TBC | Compost delivery, spraying, mowing |
| Implements | Mow, crimp-roll, compost spread, spray | Planned | Modular implement system |

**MBSE V&V requirements to be raised for chassis adjustability:**
- REQ-QUAD-001: Chassis shall be adjustable between 1.2m and 2.0m width without tools
- REQ-QUAD-002: Chassis adjustment shall be achievable by single operator in < 5 minutes
- REQ-QUAD-003: All wheel positions shall maintain equal contact pressure at any chassis width
- REQ-QUAD-004: Ground clearance of 80cm shall be maintained at all chassis widths
- (Create these as Capella requirements in MBSE module)

### Quadriga Operations Model

**Cover crop management (primary Quadriga task):**
The Quadriga operates in two path types on a terrace:
1. **Syntropic line path** (2m wide, behind main planting): mow/crimp-roll nitrogen fixer cover crops on a rotation to provide chop-and-drop into the planting zone
2. **Front row inter-paths** (1.2-1.5m wide): drive between productive herb/ground cover rows, straddling plants at 80cm clearance

**Compost delivery logistics:**
Two models under evaluation:
- **Model A (pre-positioning):** Quadriga pre-delivers 1m³ agriboxes to one-per-row locations across the field, then returns to dispense compost row by row — avoids continuous back-and-forth to central compost station
- **Model B (relay supply):** OEM 6/8-wheel transport platform collects compost from composting centre and delivers to Quadriga in field — Quadriga operates continuously without returning to base

Model A is more immediately achievable. Model B requires investment in OEM transport platform (~€8,000-15,000 for Chinese 6-wheel electric platforms) and is appropriate for larger-scale operations (>2ha).

---

## PART 6: PERMACULTURE DESIGN PROCESS AS MBSE ACTIVITY SEQUENCE

Bill Mollison's permaculture design methodology, converted to a formal MBSE activity sequence for the platform:

### Phase 1: OBSERVATION (Weeks 1-12 minimum)
**MBSE equivalent:** Context analysis, stakeholder analysis, boundary definition

Activities:
- [ ] Walk the site at all times of day and season — record sun/shadow patterns
- [ ] Map water flow after heavy rain (where does water go? where does it pool?)
- [ ] Identify existing vegetation and ecology — the inventory layer
- [ ] Record frost pockets (visual ice formation patterns)
- [ ] Identify wind corridors — observe smoke, grass movement
- [ ] Soil test: pH, texture, compaction, organic matter, water retention
- [ ] Document with photos geotagged to GIS parcel layer

**Platform deliverable:** `site_observations.json` — feeds site_profile and slope zone classification

### Phase 2: ZONE AND SECTOR ANALYSIS
**MBSE equivalent:** System decomposition, interface definition

```
ZONE MAP:
Zone 0: House/habitation (daily visited)
Zone 1: Kitchen garden, nursery, high-care plants (daily management)
Zone 2: Main productive orchard, guilds, regular management (weekly)
Zone 3: Extensive food forest, less intervention (monthly)
Zone 4: Managed woodland, timber, foraging (seasonal)
Zone 5: Wilderness / natural succession — observe only

SECTOR MAP:
Hot sector (sun arc) ← SOUTH at Montalma = most exposed
Cold sector (winter wind) ← identify prevailing wind direction
Fire sector (fire risk approach direction) ← critical for Monchique
Water sector (natural drainage lines)
Noise/road sector
Wildlife corridor sector
View/aesthetics sector
```

**Platform deliverable:** `zone_sector_map.geojson` — GIS layer overlaid on cadastral parcels

### Phase 3: DESIGN (The composition step)
**MBSE equivalent:** System architecture, requirements allocation, interface specification

This is the step where the Stratification Composer (web GUI) is used:
- Assign species to zones and strata
- Apply triangle geometry and spacing logic
- Validate guild compatibility
- Generate BOM/MEL

### Phase 4: IMPLEMENTATION (Phased execution)
**MBSE equivalent:** System integration, incremental build

Phased as per BOM template: Phase 0 → 1 → 2 → 3 → 4 → 5

### Phase 5: EVALUATION AND ITERATION
**MBSE equivalent:** Verification, validation, requirements confirmation, lessons learned

Annual review cycle:
- What survived/thrived? What failed?
- Update propagation success rates in species_database.json
- Update site_observations.json with new seasonal data
- Adjust BOM/MEL for next planting season

---

## PART 7: PLANT HARDINESS AND CLIMATE ZONE DATA SOURCES

### USDA Plant Hardiness Zone (Global Standard)
- **What it is:** 26 zones based on average annual minimum temperature (10°F bands). Zone 1 = coldest, Zone 13 = hottest.
- **Monchique zone:** Zone 10a-10b (minimum temperatures -1°C to +4°C) — mild, frost-occasional
- **Open data source:** PRISM Climate Group — bulk download of PHZ data (shapefiles, rasters)
- **API:** `phzmapi.org/{ZIPCODE}.json` (US only) — for global use, query Open-Meteo for annual minimum temp and compute zone
- **GitHub:** `waldoj/frostline` — parser for USDA PHZ data
- **EU equivalent:** European climate zones mapped at `climate.copernicus.eu` (Copernicus C3S)

### Plant Databases with Hardiness Data

| Database | Coverage | API | License | Best for |
|---|---|---|---|---|
| USDA PLANTS | US native + introduced | Yes (REST) | Public domain | North America |
| Plants For A Future (PFAF) | ~7,000 useful plants | No public API (scrape) | Open | Permaculture species |
| Kew Plants of the World Online (POWO) | ~1.4M taxa | Yes (REST) | CC-BY | Taxonomy, distribution |
| Open Tree of Life | Phylogenetic | Yes | CC0 | Relationships |
| Tela Botanica | Europe (FR/Iberian) | WFS | Open | Iberian native species |
| Flora-On | Portugal-specific | API | CC-BY-SA | Portuguese native plants |
| GBIF | Global distribution | Yes (REST) | CC-BY | Occurrence data |
| PlantNet | ID via image | API | Research | Field identification |
| TRY Plant Trait Database | Functional traits | Request | CC-BY | Trait-based ecology |
| Open-Meteo | Climate data by lat/lon | Yes (free) | Open | Compute hardiness zone for any location |

### Flora-On (Portugal-specific — most relevant for Monchique)
- URL: `https://flora-on.pt`
- API: `https://flora-on.pt/api/` — query by species name, location, habitat
- Returns: Portuguese distribution, phenology, habitat associations
- Use case: validate which species are native/naturalised in Monchique area
- This should be a primary data source for species_database.json Portuguese entries

### Computing Hardiness Zone for Any Global Location
```python
import requests

def get_hardiness_zone(lat: float, lon: float) -> dict:
    """
    Compute USDA hardiness zone from Open-Meteo historical climate data.
    Returns zone string (e.g., '10a') and min temp.
    """
    # Get 10-year average annual minimum temperature
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": "2014-01-01",
        "end_date": "2023-12-31",
        "daily": "temperature_2m_min",
        "timezone": "auto"
    }
    r = requests.get(url, params=params).json()
    temps = r["daily"]["temperature_2m_min"]
    avg_annual_min = min(temps)  # approximate

    # USDA zone lookup (°C thresholds)
    zones = [
        (-45.6, "1a"), (-42.8, "1b"), (-40.0, "2a"), (-37.2, "2b"),
        (-34.4, "3a"), (-31.7, "3b"), (-28.9, "4a"), (-26.1, "4b"),
        (-23.3, "5a"), (-20.6, "5b"), (-17.8, "6a"), (-15.0, "6b"),
        (-12.2, "7a"), (-9.4, "7b"), (-6.7, "8a"), (-3.9, "8b"),
        (-1.1, "9a"), (1.7, "9b"), (4.4, "10a"), (7.2, "10b"),
        (10.0, "11a"), (12.8, "11b"), (15.6, "12a"), (18.3, "12b"), (21.1, "13")
    ]
    for threshold, zone in zones:
        if avg_annual_min >= threshold:
            return {"zone": zone, "avg_annual_min_c": round(avg_annual_min, 1)}
    return {"zone": "13+", "avg_annual_min_c": round(avg_annual_min, 1)}

# Monchique result: Zone 10a-10b (min ~-1 to +2°C)
```

---

## PART 8: HYDROLOGICAL MODULE INTEGRATION

The agroforestry system is fundamentally a **water management system** expressed as vegetation. This is not a metaphor — trees are literal water pumps and retention infrastructure. The platform needs a dedicated hydrological module that integrates with the agroforestry module at every scale.

### Hierarchical Water Management Schema

```
Scale        Water management element          Agroforestry linkage
──────────   ──────────────────────────────   ─────────────────────────
Individual   Planting hole bund               Tree establishment
  parcel     Swale (on-contour drainage ditch) Backs each syntropic row
             Check dam in drainage line        Moisture retention
             Mulch layer                       Evaporation reduction

Terrace      Terrace wall as water retainer   Backs syntropic main line
             Terrace lip bund                 Holds rainfall on terrace
             Collection cistern per terrace   Nursery/irrigation source
             Seepage from wall into soil       Capillary water benefit

Property     Main dam / reservoir (Montalma)  Nursery water + micro-irrigation
             Spring / ribeira connection       Perennial water access
             Perimeter swale system            Catchment from upslope

Community    Shared water infrastructure      Inter-parcel coordination
             Municipal water rights           Governance module (SNA)

Municipality Watershed management             Fire risk, flood control
             River corridor restoration       Berm corridor module
```

### Montalma Dam — Technical Notes

**Current status:** Semi-constructed, stalled (waterproofing costs/logistics)

**Bentonite lining option:**
- Application rate: 5-10kg/m² (powdered bentonite) OR 4-6kg/m² (sodium bentonite GCL liner)
- Critical: fence before any bentonite work — cattle hoof puncture destroys lining permanently
- Compaction sequence: 10cm sub-base, 2cm bentonite layer, 5cm protective soil cover
- Bio-polymer alternative: Polyacrylamide (PAM) + bentonite hybrid — reduces rate to 1-2kg/m²
- Best local contractor resource: Check FENAREG (Federação Nacional de Regantes de Portugal)

**Dam sizing guidance:**
- Rule of thumb: 1 ha of agroforestry requires ~150-300m³ storage for supplemental irrigation
- Montalma area estimate: 2-5 ha active development = 300-1500m³ target capacity
- Recommend topographic survey of existing dam to calculate current capacity

---

## PART 9: SUCCESSION STAGING — MAKING THE DESIGN A LIVING MODEL

The key insight from Götsch's syntropic methodology is that the design is not static — it is a **succession script** that unfolds over time. The MBSE model must represent this as a temporal sequence.

### Three Succession Systems (Götsch framework)

| System | Stage | Characteristics | Montalma timeline |
|---|---|---|---|
| Colonisation | Pioneer | Fast-growing, soil-building species. High density, high biomass production, high pruning. | Year 0-3 |
| Accumulation | Secondary | Medium-lived productive species establish. Pioneer species pruned heavily to feed soil. | Year 3-10 |
| Abundance | Climax | Long-lived productive trees dominate. Support species maintained at reduced height. | Year 10+ |

### Species Succession Role Classification

Each species in `species_database.json` should carry:
```json
"succession_role": "pioneer | secondary | climax",
"life_cycle": "annual | biennial | short_perennial | long_perennial | permanent",
"replacement_at": "Year 2-3 (thinned) | Year 5-7 (removed) | permanent",
"chop_drop_frequency": "monthly | quarterly | annual | never"
```

**Montalma succession plan:**
- **Year 1:** Dense pioneer planting — Tagasaste (N-fix), Bromus grasses, Salvia verbenaca, Trifolium. Potatoes in alleys. Windbreak Juniper on ridge.
- **Year 2-3:** Tagasaste aggressively chopped (not removed) — biomass feeds tree rows. Canopy species (Olive, Carob, Almond, Fig) establishing.
- **Year 3-5:** Secondary productive layer consolidating. Potatoes phased out. Aromatic herbs expanding.
- **Year 5-10:** Main canopy closing. Understory species (Elderberry, Goji) thriving under dappled light. Macadamia establishing in sheltered zone.
- **Year 10+:** Abundance system. Chestnut and Walnut producing. Syntropic lines fully functional. Minimal external input required.

---

## PART 10: PLATFORM DATA SCHEMA ADDITIONS (for `species_database.json`)

Add these fields to every species entry:

```json
{
  "hardiness_zone_usda": "9b-11a",
  "min_temp_tolerance_c": -3.5,
  "max_temp_tolerance_c": 40,
  "chilling_hours_required": 0,
  "flora_on_url": "https://flora-on.pt/index.php#/species/Salvia_verbenaca",
  "pfaf_url": "https://pfaf.org/user/Plant.aspx?LatinName=Salvia+verbenaca",
  "succession_role": "secondary",
  "life_cycle": "short_perennial",
  "chop_drop_frequency": "annual",
  "replacement_at": "permanent",
  "propagation": {
    "primary_method": "seed",
    "secondary_methods": ["division", "softwood_cutting"],
    "best_season": "spring_autumn",
    "rooting_medium": "standard_potting_mix",
    "rooting_hormone_required": false,
    "success_rate_typical_pct": 80,
    "time_to_transplant_weeks": 6,
    "seed_stratification": null,
    "seed_scarification": false,
    "notes": ""
  },
  "mechanisation_compatible": true,
  "quadriga_clearance_required_cm": 5,
  "max_managed_height_cm": 55,
  "terrace_zone_placement": "front_rows",
  "wall_face_suitable": false
}
```

---

## PART 11: OPEN QUESTIONS — INTERACTIVE CLARIFICATION NEEDED

Before finalising the module, the following need your input:

**Q1 — Montalma inventory completeness:** The inventory table above is based on what has come up in our conversations. Is this accurate? What have I missed? In particular: are there any native trees already established on the property (oak, strawberry tree, other natives) that should be recorded as primary ecological capital?

**Q2 — Dam dimensions:** What is the approximate surface area and depth of the current dam excavation? This determines the bentonite volume and whether the current structure is worth completing.

**Q3 — Terrace count and dimensions:** Approximately how many terraces exist at Montalma, and what is the average width? This determines the inter-row spacing module and Quadriga operational sequence.

**Q4 — Quadriga chassis adjustability:** Is the 1.2-2.0m chassis range physically confirmed by current prototyping, or is this aspirational? This determines the minimum row spacing standard for all designs generated by the platform.

**Q5 — Zone 1 nursery space:** Where is the designated nursery/propagation space at Montalma? The Goji mother plant is in Zone 1 mid-terrace — is there a dedicated nursery terrace adjacent to the water point?

**Q6 — Climbing/wall species:** You mentioned experimenting with species on the terrace wall faces. Is the Chayote on the wall face or at the base? And are there any specific structural limitations on what can go on the rock walls (mortar condition, height, sun exposure)?

**Q7 — Cover crop in inter-row paths:** Are you currently sowing any cover crops in the Quadriga travel paths, or are they bare soil? What do you want there — mowable grass, clover, or kept bare?

---

## PART 12: COMMIT CHECKLIST

Files to commit to `agroforestry/`:
- [x] `AGROFORESTRY_MODULE.md` — core module architecture (v1.0)
- [x] `AGROFORESTRY_MODULE_EXTENDED.md` — this document (v1.1)
- [x] `species_database.json` — species with attributes (v1.0, to be updated with propagation fields)
- [x] `BOM_template.csv` — bill of materials template
- [ ] `guild_compositions.json` — (next session)
- [ ] `site_inventory_montalma.json` — (fill from field observations)
- [ ] `propagation_protocols.md` — (attach books when provided)
- [ ] `quadriga_mbse_requirements.md` — (derive from Capella, session TBC)
- [ ] `hydrological_integration.md` — (dam + swale system, session TBC)

---

*Federated Rural OSDK Platform v1.1 | Conscious Circle | April 2026*
*Based on Ernst Götsch syntropic methodology, AgroForAdapt LIFE project data, Nature Plants 2024 DEXi study, and Montalma field observations*
