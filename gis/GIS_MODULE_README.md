# GIS Data Acquisition Module — Global Cadastral Registry

**Module path:** `gis/`  
**Part of:** Federated Rural OSDK Platform  
**Maintainer:** JRBD / Conscious Circle  
**Version:** 1.0.0 (April 2026)

---

## Purpose

This module solves the **first-mile problem** of any GIS-based rural development analysis: how to get authoritative land parcel boundaries for any country, programmatically, and pipe them into the OSDK analytical pipeline.

It provides:
1. `gis_cadastre_registry.json` — a queryable database of cadastral data sources for 45 countries + global fallbacks
2. `query_cadastre_registry.py` — interactive CLI to explore the database
3. `fetch_cadastro.py` — generic fetcher that auto-configures per country

This module is the entry point for **Portfolio Project 1** (Ethical Supply Chain Dashboard), the **Monchique Rural Network** GIS layer, and future Conscious Circle international consulting engagements.

---

## Quick Start

```bash
cd ~/Documents/GitHub/federated-rural-osdk-platform
source .venv/bin/activate

# 1. Query the registry
python gis/query_cadastre_registry.py --country PT      # Portugal lookup
python gis/query_cadastre_registry.py --list            # all countries
python gis/query_cadastre_registry.py --access open     # only open sources
python gis/query_cadastre_registry.py --global-fallbacks

# 2. Fetch Monchique cadastral parcels (Portugal — open, CC-BY 4.0)
python gis/fetch_cadastro.py \
  --country PT \
  --bbox "-8.65,37.20,-8.45,37.38" \
  --output mbse/exports/monchique_cadastro_predial.geojson

# 3. Inspect schema before full fetch
python gis/fetch_cadastro.py \
  --country PT \
  --bbox "-8.65,37.20,-8.45,37.38" \
  --inspect-only

# 4. Test the endpoint live in browser
# https://ogcapi.dgterritorio.gov.pt/collections/CadastroPredial/items?f=json&bbox=-8.65,37.20,-8.45,37.38&limit=5
```

---

## Registry Coverage

| Region | Countries | Primary Open WFS | Registration Required | Restricted/Manual |
|--------|-----------|------------------|-----------------------|-------------------|
| Western Europe | 17 | PT, ES, FR, AT, CH, NO, DK, PL, CZ | NL, SE, FI, DE (some) | IT, IE (partial) |
| North America | 3 | — | CA (provincial) | US (county-level), MX |
| South America | 6 | — | CO, EC | BR (SIGEF open), AR, CL, PE |
| Africa | 6 | ZA | — | KE, NG, ET, MA, GH |
| East Asia | 3 | — | KR | JP (partial), CN |
| South/SE Asia | 4 | — | — | IN, ID, PH, VN |
| Middle East | 3 | IL | TR | EG |
| Oceania | 2 | AU (state), NZ | — | — |

**Global fallbacks:** OSM Overpass API, World Bank Land Portal, FAO GAUL, GADM, ESA WorldCover, Global Forest Watch, RCMRD (East Africa), UN OCHA HDX.

---

## Access Tiers

| Tier | Meaning | Examples |
|------|---------|---------| 
| `open` | Free, no auth, machine-readable | PT, ES, FR, AT, NZ |
| `open_registration` | Free API key required | NL, FI, SE, DK, CA-BC |
| `restricted` | Government/institutional access | IT (vector), CN, GH |
| `commercial` | Paid licence required | US (Regrid), CL |
| `manual` | No API — download or digitise | NG, ET, VN |
| `partial` | Some layers open | IE, IN (state-wise) |

---

## For Each Country: What to Expect

### Portugal (PT) — Recommended first test ✅
- **Source:** DGT OGC API (CC-BY 4.0, no auth)
- **Coverage:** Continental Portugal — all prédios rústicos and urbanos
- **Precision:** 40–230cm EMQ (vectorised from analogue sections)
- **Attributes:** NIC (unique parcel ID), secção, artigo, área, natureza (rústico/urbano)
- **Monchique BBOX:** `-8.65,37.20,-8.45,37.38`

### Spain (ES) — Best in class ✅
- **Source:** Catastro WFS (CC-BY 4.0 non-commercial free)
- **Coverage:** All Spain, urban + rústico
- **Reference:** `nationalCadastralReference` (14-char RC) links to fiscal data

### France (FR) — Requires free API key
- **Source:** IGN Géoportail WFS
- **Bulk alternative:** `cadastre.data.gouv.fr` — GeoJSON per commune, no auth
- **Best for large areas:** bulk download by département

### Brazil (BR) — Use CAR for rural work ✅
- **SIGEF** for certified rural parcels (free WFS)
- **CAR** (Cadastro Ambiental Rural) is essential for Amazon/rural analysis — free shapefile per state
- Download from: `car.gov.br/publico/imoveis/index`

### United States (US) — County-level only
- No national open cadastre
- **Regrid/Loveland:** best national API (commercial, free tier limited)
- For open work: use state portals (CA, NY, FL well-covered)
- **PLSS** (Public Land Survey) for western states (federal lands)

### Africa — Use global fallbacks
- **South Africa (ZA):** best cadastre in sub-Saharan Africa
- **Others:** World Bank Land Portal + RCMRD regional portal + OSM
- For forest/land concessions: Global Forest Watch

---

## Adding a New Country

Edit `gis_cadastre_registry.json` and add an entry under the appropriate region:

```json
"XX": {
  "name": "Country Name",
  "inspire_node": "https://national-geoportal.xx",
  "primary_source": {
    "name": "Source Name",
    "type": "ogc_api | wfs | wms_only | bulk_download | manual | restricted",
    "access": "open | open_registration | restricted | commercial | manual | partial",
    "license": "CC-BY 4.0",
    "base_url": "https://...",
    "collection": "LayerName",
    "crs": "EPSG:4326",
    "coverage": "description",
    "attributes": ["field1", "field2"],
    "attribution": "Required attribution string",
    "test_url": "https://... test URL",
    "notes": "Any important caveats",
    "docs": "https://official-docs"
  },
  "bbox_country": "lon_min,lat_min,lon_max,lat_max"
}
```

---

## Integration with OSDK Pipeline

After fetching cadastral data, pipe it into the existing platform:

```bash
# 1. Fetch parcels
python gis/fetch_cadastro.py --country PT --bbox "..." --output mbse/exports/monchique_cadastro_predial.geojson

# 2. Run downstream analysis
python scripts/sna_integration.py
python scripts/sd_integration.py
python scripts/qsem_cld_integration.py

# 3. Push to ArcGIS Online
python scripts/import_to_arcgis.py

# 4. Trigger n8n orchestration (Workflow 006)
```

---

## QGIS Integration

Add DGT as a live WFS layer in QGIS:

1. Layer → Add Layer → Add WFS Layer
2. URL: `https://ogcapi.dgterritorio.gov.pt` (OGC API mode)
3. Enable feature paging → Connect
4. Select `CadastroPredial` → Add
5. Set scale visibility (recommended: only show at 1:10,000 or larger)

For Spain: `https://ovc.catastro.meh.es/INSPIRE/wfs/CadastralParcel`  
For France: `https://wxs.ign.fr/cadastrals/geoportail/wfs` (requires API key in headers)

---

## ArcGIS Online Integration

1. Map → Add → Add Layer from Web
2. WFS URL: `https://ogcapi.dgterritorio.gov.pt/collections/CadastroPredial/items?f=json&bbox=...`
3. Or publish `monchique_cadastro_predial.geojson` as Feature Layer via `import_to_arcgis.py`

---

## Attribution Requirements

| Country | Required Attribution |
|---------|---------------------|
| PT | "Carta Cadastral Digital – SNIC – DGT" (CC-BY 4.0) |
| ES | "Dirección General del Catastro" |
| FR | "IGN – Géoportail" (Licence Ouverte Etalab 2.0) |
| AT | "BEV – Bundesamt für Eich- und Vermessungswesen" (CC-BY 4.0) |
| NZ | "Land Information New Zealand" (CC-BY 4.0) |
| AU | "Geoscape Australia" (CC-BY 4.0) |

---

*Last updated: April 2026 | Federated Rural OSDK Platform v1.0*
