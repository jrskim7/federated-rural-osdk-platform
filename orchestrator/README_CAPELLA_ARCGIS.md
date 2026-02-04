Capella → ArcGIS prototype

Overview
- This prototype reads a small Capella-export-like JSON, converts MBSE blocks with geometry into GeoJSON, and can optionally push features to an ArcGIS Online Feature Service.

Environment
- Add the following to `orchestrator/.env`:
  - ARCGIS_USERNAME=your_arcgis_username
  - ARCGIS_PASSWORD=your_arcgis_password
  - ARCGIS_FEATURE_SERVICE_URL=https://services.arcgis.com/.../FeatureServer/0
  - MBSE_EXPORT_PATH=/git_repo/mbse/exports/sample_capella_export.json
  - OUTPUT_GEOJSON_PATH=/git_repo/mbse/exports/output_geojson.json

Local test (after `docker-compose up -d`):
1. Call the MBSE bridge to run the conversion locally:
   curl -X POST http://localhost:5000/run/capella-to-arcgis -H "Content-Type: application/json" -d '{}' 
2. Check `mbse/exports/output_geojson.json` for the GeoJSON file.
3. If ArcGIS env vars are present, the script will attempt to push features to the ArcGIS layer and include the response in the JSON result.

n8n
- Import `orchestrator/n8n/workflows/002-capella-to-arcgis.json` and activate it. Trigger the webhook at `/webhook/capella-run` to run the job via n8n.

Notes
- This is a minimal prototype to show the flow. For production: add robust geometry mapping, error handling, and field schema validation; ensure credentials are stored securely in secrets; and use PR-based commits for traceability.