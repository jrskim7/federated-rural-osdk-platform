# ArcGIS Experience Builder Dashboard Setup

This guide walks through creating an integrated Experience Builder dashboard that combines spatial maps, network diagrams, system dynamics outputs, and causal loop analysis.

## Overview

An **ArcGIS Experience Builder** dashboard consolidates all analysis results into a single, interactive interface:

1. **Map Panel** - Spatial features with fire risk, suitability, and ecosystem status
2. **Network Panel** - Partnership graph (from SNA)
3. **System Dynamics Panel** - Biomass, grazing, water availability trends
4. **Causal Loop Panel** - QSEM CLD visualization
5. **Audit Trail Panel** - Change history from GeoJSON
6. **Metrics Panel** - KPIs and governance indicators

## Prerequisites

- ArcGIS Online account (https://ccgisonline.maps.arcgis.com)
- Published Feature Layer "Monchique Federated OSDK Model"
- Kumu account for network visualization (optional)
- Experience Builder access (included with ArcGIS Online)

## Step 1: Prepare Data in ArcGIS Online

### 1.1 Feature Layer (Already Done)
Your GeoJSON is published as a CSV feature layer. To add the SD results:

```bash
python scripts/sd_integration.py
python scripts/import_to_arcgis.py --output sd_results.geojson
```

Then in ArcGIS Online:
- Open Feature Layer item
- Click "Data" tab
- Add the SD columns as new fields (if needed)
- Or re-publish with updated CSV

### 1.2 Create a Map

1. Go to https://ccgisonline.maps.arcgis.com
2. Click "Create" → "Web Map"
3. Add your Feature Layer "Monchique Federated OSDK Model"
4. Configure symbology:
   - Color by `fireRiskIndex` (red for high risk)
   - Size by `population` or `area_ha`
   - Label by `name`
5. Save as "Monchique OSDK Map"

### 1.3 Create Layers for Each Analysis

**Fire Risk Layer:**
- Feature Layer with symbol by `fireRiskIndex` 
- Graduated colors: Green (0-0.33), Yellow (0.33-0.67), Red (0.67-1.0)

**Suitability Layer:**
- Feature Layer with symbol by `suitabilityScore`
- Size scale: 10px (0.0) → 50px (1.0)

**Ecosystem Layer:**
- EcologicalZone features with symbol by `biomassStock_tons`
- Popup shows SD updates

## Step 2: Create Experience Builder App

### 2.1 Create New Experience

1. Go to ArcGIS Online
2. Click "Create" → "Experience Builder"
3. Choose "Blank" template
4. Name: "Monchique OSDK Dashboard"
5. Click "Create"

### 2.2 Add Title & Description

In the header:
- Title: "Monchique Rural OSDK Platform"
- Subtitle: "Integrated MBSE-GIS-SNA-SD-QSEM Analysis"

### 2.3 Create 5 Panels (Tabs or Cards)

**Panel 1: Spatial Map**
- Widget: "Map" (your Monchique OSDK Map)
- Interactions: Enable popups, feature selection
- Add layer toggle for Risk/Suitability/Ecosystem views
- Show SD results in popup (biomass, fire risk, water availability)

**Panel 2: Network Diagram**
- Widget: "Embed" or "Web page"
- URL: Link to Kumu project (if published)
  - https://kumu.io/jrskim7/monchique-osdk
  - Or embed code from Kumu "Share" button
- Title: "Partnership Network (SNA)"
- Shows municipalities, cooperatives, councils, tourism actors, projects

**Panel 3: System Dynamics Outputs**
- Widget: "Table" or "Dashboard"
- Data: SD report JSON (converted to table format)
- Columns:
  - Feature Name
  - Biomass Stock (tons)
  - Fire Risk Index
  - Grazing Capacity
  - Water Availability
  - Suitability Score
- Filters: Select by feature type or sector

**Panel 4: Causal Loop Diagram**
- Widget: "Embed" or "Web page"
- URL: Link to Kumu CLD
  - https://kumu.io/jrskim7/monchique-osdk-cld
- Title: "QSEM Causal Loop Diagram"
- Shows factors and causal links (biomass → fire risk, etc.)

**Panel 5: Audit Trail & Metadata**
- Widget: "Table" (from change_summary.json)
- Columns:
  - Timestamp
  - Feature
  - Property
  - Old Value
  - New Value
  - Editor
  - Note
- Filter: Select by date range or feature
- Shows complete edit history for compliance

## Step 3: Configure Interactions

### 3.1 Map-to-Table Linking

1. Select Map widget
2. "Configure" → "Data Actions"
3. Create action: "Show Details"
4. Link to Table (System Dynamics panel)
5. Match by: `id` (feature ID)

Result: Click a feature on map → SD table shows that feature's data

### 3.2 Add Filters (Optional)

Create dashboard filters to show:
- By Sector: Public, Private, Civil Society, Environment
- By Status: active, planning, completed
- By Risk Level: Low (0-0.33), Medium, High
- By Governance: Strong, Medium, Weak

## Step 4: Add Interactivity

### 4.1 Feature Popups

Edit Feature Layer popup template:

```html
<h3>{name}</h3>
<p><b>Type:</b> {type}</p>
<p><b>Sector:</b> {sector}</p>
<p><b>Status:</b> {status}</p>

<b>System Dynamics Results:</b>
<ul>
  <li>Fire Risk: {sd_fireRiskIndex}</li>
  <li>Biomass: {sd_biomassStock_tons} tons</li>
  <li>Suitability: {sd_suitabilityScore}</li>
</ul>

<b>MBSE Traceability:</b>
<p>Block ID: {mbseBlockId}</p>
<p>SNA Node: {snaNodeId}</p>
```

### 4.2 Legend

Add legend showing:
- Fire Risk color scale
- Suitability size scale
- Sector icons
- SD metric ranges

## Step 5: Share & Permissions

1. Click "Share" (top-right)
2. Settings:
   - "Everyone (public)" or "Specific people"
   - Permissions: "View" (read-only) or "Edit" (allow changes)
3. Copy embed code if embedding elsewhere
4. Share link: https://ccgisonline.maps.arcgis.com/apps/experiencebuilder/experience/...

## Step 6: Integrate into Federated Workflow

### 6.1 Update Experience on GeoJSON Changes

In n8n Workflow 003, add final step:

**Node: "Update Experience"**
- Type: HTTP request
- Method: POST
- URL: ArcGIS Online Feature Layer REST API
- Updates feature properties after SD/QSEM analysis
- Triggers Experience auto-refresh

```bash
curl -X POST https://services.arcgis.com/.../features/updateFeatures \
  -d "adds=[updated_feature_json]" \
  -d "token=YOUR_AGOL_TOKEN"
```

### 6.2 Scheduled Refreshes (Optional)

In ArcGIS Online, set Feature Layer to refresh every 1 hour:
- Feature Layer settings
- "Refresh" → "Every 1 hour"
- Experience auto-shows latest data

## Example Dashboard Layout

```
┌─────────────────────────────────────────────────────┐
│  Monchique Rural OSDK Platform                      │
│  Integrated MBSE-GIS-SNA-SD-QSEM Analysis          │
└─────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────┐
│  Spatial Map         │  Network Diagram     │
│  (Risk/Suitability)  │  (Partnerships)      │
│                      │                      │
│                      │                      │
├──────────────────────┼──────────────────────┤
│  System Dynamics     │  Causal Loop         │
│  (Biomass/Grazing)   │  (QSEM CLD)          │
│                      │                      │
├──────────────────────┴──────────────────────┤
│  Audit Trail / Change History               │
│  (Feature edits with metadata)              │
└──────────────────────────────────────────────┘
```

## Advanced Features

### 1. Temporal Analysis
- Add time slider (if Feature Layer has timestamps)
- Show changes over time (before/after community edits)

### 2. Alerts & Notifications
- High fire risk zones → red alert
- Suitability score > 0.9 → green highlight
- Custom alerts on policy violations

### 3. Export Capabilities
- "Download Report" button → PDF export
- Includes map snapshot, metrics, audit trail
- Sent to stakeholders automatically

### 4. Mobile-Responsive
- Experience Builder auto-responds
- Mobile users can view read-only dashboard
- Full edit access on desktop

## Files to Upload to ArcGIS Online

1. **Feature Layer** (already done)
   - Source: `mbse/exports/monchique_federated_model.geojson`
   - Type: CSV → Feature Layer

2. **System Dynamics Results** (new)
   - Source: `mbse/exports/monchique_federated_model_sd_<timestamp>.geojson`
   - Add as separate Feature Layer or merge fields

3. **Audit Trail** (new)
   - Source: `change_summary_*.json`
   - Create table layer with edit history

4. **Web Map** (new)
   - Layer: Feature Layer
   - Symbology: By fireRiskIndex, suitabilityScore

5. **Experience Builder App** (new)
   - Combines all above with network & CLD embeds

## Next Steps

1. ✅ Create Feature Layer (done)
2. ✅ Create Map (do in ArcGIS Online)
3. 🔄 Create Experience Builder app
4. 🔄 Link to Kumu network visualization
5. 🔄 Integrate into n8n workflow
6. 🔄 Set up auto-refresh on edits
7. 🔄 Share with community stakeholders

## References

- [ArcGIS Experience Builder Docs](https://doc.arcgis.com/en/experience-builder/)
- [Configure Data Actions](https://doc.arcgis.com/en/experience-builder/configure-widgets/data-actions.htm)
- [Feature Layer Popups](https://doc.arcgis.com/en/arcgis-online/create-maps/pop-ups.htm)
- [Your Kumu Projects](#) (will provide URL after creation)
