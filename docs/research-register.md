# Metrolínea / SITME — source and verification register

Last updated: 2026-11-07. All items below are **leads pending verification**, not accepted facts for the published GTFS.

## Background / scope
- Historic Bucaramanga BRT: Metrolínea; more recent services may use SITME branding.
- Coverage to investigate: Bucaramanga, Floridablanca, Girón and Piedecuesta.
- Keep historic infrastructure and routes distinct from services demonstrably operating on the feed's effective dates.
- This repo must remain separate from the existing AMB TPC collective-route GTFS.

## Candidate route leads (unverified)
| Identifier | Reported context | Status |
| --- | --- | --- |
| PTB | Reported 2025 restart route; reportedly discontinued May 2026 | Verify with official dated source |
| PTN | Reported 2025 restart route; reportedly discontinued May 2026 | Verify with official dated source |
| P19 | Reported Portal Norte–Provenza route | Verify route and active service |
| P1 | Reported Carrera 15 corridor | Verify route and active service |
| P10 | Reported Terminal–Real de Minas–UIS connection | Verify alignment and active service |
| P14 | Reported Terminal–Real de Minas–UIS connection | Verify alignment and active service |

An earlier research lead claimed 12 complementary and 13 integrated routes in May 2026. **Do not treat this as a verified current route inventory.**

## GIS and stop leads
- ArcGIS candidate route layer: https://services6.arcgis.com/KmKGWMjOsgTLFBpe/ArcGIS/rest/services/Rutas_Metrolinea/FeatureServer/0
  - Check availability, license, coordinate reference, feature fields, geometries, dates and whether these represent full route paths or just corridors.
- Zenodo candidate spatial dataset: https://zenodo.org/records/23147409
  - Check provenance, reuse rights, station coordinates and whether stations are operating.
- Historical station/portal inventory and rehabilitation reporting: identify and archive dated primary sources before using any stop in `stops.txt`.

## Required data before GTFS publication
| GTFS | Required verification |
| --- | --- |
| agency.txt | Legal operator / publisher, website, timezone |
| routes.txt | Active route IDs, variants, mode, service status |
| stops.txt | Real active stops/stations with coordinates |
| shapes.txt | Correct ordered geometry for each route variant |
| trips.txt / frequencies.txt | Actual operating service pattern and documented headways |
| calendar.txt / calendar_dates.txt | Days of operation, holidays, validity dates |
| stop_times.txt | Stop sequence and defensible running times |

## Evidence policy
Record each primary source's URL, retrieval date, document date, applicable service period, extraction method and verification status. Do not convert an unverified media claim or historical map into a current GTFS fact. Prefer official SITME/Metrolínea/municipal records. Record unresolved conflicts rather than silently choosing one source.

## Source verification — 2026-11-07

### Official primary source: Metrolínea annual management report 2025
URL: https://www.metrolinea.gov.co/v3.0/sites/default/files/informe_gestion_anual_consolidado_2025_compressed.pdf

The report describes the transitional SITM network and explicitly lists:
- Bucaramanga integrated: 3, 14, 15, 17, 21, 23, 24 (7).
- Floridablanca complementary: P1, P2, P3, P10, P14 (5).
- Piedecuesta complementary: P8, P16, RD27 (3).
- Piedecuesta integrated: 49, 50, 51, 53, 56, 59 (6).
- Girón complementary RG27: **planned**, not confirmed operating.

This yields 21 routes described as operating and one planned route **as reported in the 2025 annual report**. This is NOT a verified current November 2026 list. The report also describes a phased transition for dedicated bus lanes and 11 operating buses plus one spare in phase 1; do not assume those phases have occurred.

### ArcGIS infrastructure layer — historic, not current route shapes
URL: https://services6.arcgis.com/KmKGWMjOsgTLFBpe/ArcGIS/rest/services/Rutas_Metrolinea/FeatureServer/0

Verified metadata: polyline feature layer, supports JSON/GeoJSON/PBF; spatial reference EPSG:3857; object ID field FID; maxRecordCount 2000; fields include TIPO, NOMBRE, METROLINEA, NOM_CORRED, SENTIDO, CODRED and road-infrastructure attributes. The ArcGIS REST metadata reports last edit 2017-06-14. **Classify as historical road/corridor infrastructure**, not validated contemporary GTFS route geometry. Query features and examine actual values and coverage before any mapping.

### Zenodo 2026 spatial dataset — candidate station coordinates
URL: https://zenodo.org/records/23147409
DOI: 10.5281/zenodo.23147409
Published 2026-10-05. Single RAR archive `ANEXO_4_Geolocalizacion_Metrolinea_Bucaramanga.rar` (198 MB), described as containing XLSX, GPKG, QGZ, PDF and PNG with coordinates and cartography of stations and portals. This is a research compilation of infrastructure, not a verified current operating-stop list. Download/extract, inspect attribution and reuse terms, and cross-check each stop's operational status.

### Planning map — future network, not existing service
URL: https://www.amb.gov.co/download/31281/
AMB metropolitan mobility master plan map `Rutas Metrolínea 2025 - Portal Norte` refers to `Rutas escenario 2027`. Keep in a future-scenario layer; do not put proposed routes into current GTFS.

### Next verification tasks
1. Query and export ArcGIS layer 0 in pages to GeoJSON; inventory geometry types, features, names and route/corridor values.
2. Extract Zenodo RAR, inventory station/portal records and deduplicate coordinates.
3. Cross-check 21 report routes and planned RG27 against dated 2026 official notices; distinguish suspended, modified and active variants.
4. Determine whether any actual route shapes, stop sequences and headways can be substantiated from primary sources.
