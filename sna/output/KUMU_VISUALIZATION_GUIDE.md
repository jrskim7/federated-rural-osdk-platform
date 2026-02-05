# Kumu Network Visualization Guide

Generated: 2026-02-05 17:22:27

## Import to Kumu

1. **Go to Kumu**: https://kumu.io
2. **Create Project**: Click "New Project" → "Import from JSON"
3. **Upload**: Select `kumu_network_TIMESTAMP.json`
4. **Wait**: Kumu will parse and display your network

## Recommended Decorations

### Element Sizing
```
@settings {
  element-size: scale("degree centrality", 20, 50);
}
```
This makes more connected actors larger.

### Element Coloring by Sector
```
element[sector="Public"] {
  color: #3498db;
  label-color: #2c3e50;
}

element[sector="Private"] {
  color: #e74c3c;
  label-color: #2c3e50;
}

element[sector="Civil Society"] {
  color: #2ecc71;
  label-color: #2c3e50;
}

element[sector="Environment"] {
  color: #8e44ad;
  label-color: #2c3e50;
}
```

### Connection Styling by Weight
```
connection {
  width: scale("weight", 1, 5);
  color: #95a5a6;
}

connection[weight > 1.2] {
  color: #27ae60;  /* Strong partnerships = green */
  style: dashed;
}
```

### Labels
```
element {
  font-size: 16;
  font-weight: bold;
}
```

## Layouts

Try these layouts (Settings → Layout):

1. **Force-directed**: Best for showing clusters
2. **Radial**: Good for highlighting central actors
3. **Concentric**: Organize by degree centrality

## Filters

Create filters to explore:

- **By Sector**: Filter to show only Public or Private actors
- **By Capacity**: Show only high-capacity organizations
- **Strong Partnerships**: Filter connections where Weight > 1.0

## Analysis Features

Use Kumu's built-in metrics:

- **Betweenness Centrality**: Identifies brokers/bridges
- **Closeness Centrality**: Measures overall network influence
- **Clustering**: Detect communities within network

## Sharing

- Click "Share" to get public link
- Embed in websites or reports
- Export as PNG/SVG for presentations

## Next Steps

1. Add more actor attributes from GeoJSON
2. Include temporal data (track changes over time)
3. Link to external data sources (ArcGIS dashboards, MBSE models)
