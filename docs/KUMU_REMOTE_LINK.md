# Kumu Remote JSON Link Setup

## Quick Start: Link Kumu to Live GitHub Data

Your network visualization can **auto-update** whenever you commit changes to GitHub.

---

## 🔗 Remote JSON URL

```
https://raw.githubusercontent.com/jrskim7/federated-rural-osdk-platform/main/sna/exports/kumu_network.json
```

**This URL always points to the latest version** of your network on GitHub.

---

## 📥 Import into Kumu (Web-Based)

### Step 1: Go to Kumu
Visit: https://kumu.io

### Step 2: Create or Open Project
- **New project**: Click "+ New Project"
- **Existing project**: Open the project you want to update

### Step 3: Import from URL
1. Click the **"+"** button (top-left)
2. Select **"Import"**
3. Choose **"From URL"** or **"From JSON URL"**
4. Paste the remote URL:
   ```
   https://raw.githubusercontent.com/jrskim7/federated-rural-osdk-platform/main/sna/exports/kumu_network.json
   ```
5. Click **"Import"**

### Step 4: Configure Auto-Refresh (Optional)
- In Kumu project settings, enable **"Auto-refresh from URL"**
- Set refresh interval (e.g., hourly, daily)
- Kumu will check GitHub for updates automatically

---

## 🔄 Update Workflow

Whenever you want to update the network visualization:

### Method 1: From GeoJSON Edits
```bash
# After community edits in ArcGIS
python scripts/export_from_arcgis.py

# Generate SNA network
python scripts/sna_integration.py

# Commit to GitHub
git add sna/exports/kumu_network.json
git commit -m "Update SNA network from community edits"
git push origin main
```

**Result**: Kumu refreshes automatically (if auto-refresh enabled) or manually refresh in Kumu UI.

### Method 2: Direct Generation
```bash
# Generate from current GeoJSON
python scripts/generate_kumu_remote.py

# Commit to GitHub
git add sna/exports/kumu_network.json
git commit -m "Update Kumu network"
git push origin main
```

---

## 📊 What's Included in the Network

The `kumu_network.json` file contains:

### Elements (Nodes)
- **Municipalities** (e.g., Monchique)
- **Projects** (e.g., Micro-Hydro Dam Sites)
- **Cooperatives** (e.g., Algarve Goat Cooperative)
- **Public Entities** (e.g., Municipal Council)
- **Civil Society** (e.g., Tourism Collective)
- **Ecological Zones** (e.g., Eucalyptus Monoculture)

### Connections (Edges)
- **Partnerships** (from `partnershipIds` in GeoJSON)
- **Collaborations** (inferred from shared projects)
- **Influence** (from `adoptedMethodologies`, `communityApproval`)

### Attributes (Properties)
- **Sector**: Public, Private, Civil Society, Environment
- **Level**: Municipal, District, National
- **Status**: planning, active, completed
- **Budget**: Financial capacity (euros)
- **Population**: Size/reach
- **Capacity**: Management/governance score (0-1)
- **MBSE Block ID**: Traceability to Capella model
- **Degree Centrality**: Network position metric (calculated)
- **Weighted Degree**: Influence metric (calculated)

---

## 🎨 Kumu Visualization Tips

### Color by Sector
```
@settings {
  element-color: categorize("Sector", 
    "Public" blue, 
    "Private" red, 
    "Civil Society" green, 
    "Environment" brown
  );
}
```

### Size by Budget or Population
```
@settings {
  element-size: scale("Budget (€)", 10, 50);
}
```

### Edge Weight by Strength
```
@settings {
  connection-width: scale("strength", 1, 5);
}
```

### Filter by Status
- Use Kumu's filter panel to show only `Status = active`
- Hide inactive or planning entities

---

## 🔐 GitHub Raw URL Details

### How It Works
- GitHub hosts all files in your repository
- The "raw" URL serves the file directly (no HTML wrapper)
- Kumu fetches the JSON from this URL
- URL structure:
  ```
  https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
  ```

### For This Project
- **Owner**: jrskim7
- **Repo**: federated-rural-osdk-platform
- **Branch**: main
- **Path**: sna/exports/kumu_network.json

**Full URL**:
```
https://raw.githubusercontent.com/jrskim7/federated-rural-osdk-platform/main/sna/exports/kumu_network.json
```

### Security Note
- This URL is **public** (anyone with link can view)
- To restrict access:
  - Make repo private
  - Use GitHub token authentication in Kumu (if supported)
  - Or host JSON elsewhere with access control

---

## 🚀 Advanced: Automated Updates

### Option A: GitHub Action (Auto-Generate on Push)
Create `.github/workflows/update-kumu-network.yml`:

```yaml
name: Update Kumu Network

on:
  push:
    paths:
      - 'mbse/exports/**'
      - 'sna/output/**'

jobs:
  update-network:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Generate Kumu JSON
        run: |
          pip install networkx
          python scripts/sna_integration.py
          python scripts/generate_kumu_remote.py
      
      - name: Commit updated JSON
        run: |
          git config user.name "GitHub Action"
          git config user.email "action@github.com"
          git add sna/exports/kumu_network.json
          git commit -m "Auto-update Kumu network from latest data" || true
          git push
```

### Option B: n8n Workflow Node
Add to n8n Workflow 003:
1. After "Commit GeoJSON File" node
2. Add "Execute Command" node:
   ```bash
   python scripts/sna_integration.py
   python scripts/generate_kumu_remote.py
   ```
3. Add "GitHub Commit" node to commit `kumu_network.json`

**Result**: Every time GeoJSON is updated, Kumu network auto-updates too.

---

## 📋 File Structure

```
sna/
├── exports/
│   └── kumu_network.json          ← Remote-linkable file (canonical)
└── output/
    ├── kumu_network_TIMESTAMP.json ← Historical versions
    ├── sna_nodes.csv               ← Node list (Gephi compatible)
    ├── sna_edges.csv               ← Edge list (Gephi compatible)
    └── sna_network_TIMESTAMP.graphml ← Full network (NetworkX)
```

---

## 🛠️ Troubleshooting

### "Kumu can't access the URL"
- **Check GitHub is public**: Repo must be public or Kumu needs token
- **Verify URL**: Copy-paste from this guide, ensure no typos
- **Test in browser**: Paste URL in browser, should show raw JSON

### "Network looks empty"
- **Check JSON structure**: Open `kumu_network.json` in editor
- **Verify `partnershipIds`**: Ensure GeoJSON features have partnerships
- **Re-generate**: Run `python scripts/generate_kumu_remote.py`

### "Updates not showing in Kumu"
- **Refresh manually**: Click "Refresh" in Kumu import settings
- **Clear cache**: Kumu may cache old version
- **Check GitHub commit**: Verify `kumu_network.json` was pushed
- **GitHub propagation**: Wait 1-2 minutes for GitHub CDN

---

## 📚 References

- [Kumu JSON Import Docs](https://docs.kumu.io/guides/import.html#json)
- [GitHub Raw URLs](https://docs.github.com/en/repositories/working-with-files/using-files/viewing-a-file#viewing-or-copying-the-raw-file-content)
- [Kumu Advanced Formatting](https://docs.kumu.io/guides/advanced-formatting.html)

---

## ✅ Next Steps

1. **Commit this file to GitHub**:
   ```bash
   git add sna/exports/kumu_network.json docs/KUMU_REMOTE_LINK.md
   git commit -m "Add Kumu remote JSON link for live network updates"
   git push origin main
   ```

2. **Import into Kumu**:
   - Go to https://kumu.io
   - Import from URL (use link above)

3. **Test the workflow**:
   - Edit a GeoJSON feature (add partnership)
   - Run `python scripts/sna_integration.py`
   - Commit + push
   - Refresh Kumu → see changes

4. **Enable auto-refresh** (optional):
   - Kumu project settings → Auto-refresh → Enable
   - Set interval → Daily

**Result**: Your Kumu network map is now live-linked to GitHub and updates automatically! 🎉
