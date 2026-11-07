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
