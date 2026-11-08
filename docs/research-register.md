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


### Zenodo extraction: verified workflow run 42418470730 (2026-11-07)
- Run: https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42418470730
- Artifact: https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42418470730/artifacts/13592088158
- Extraction completed successfully: 12 original files, one GeoPackage table, one Excel worksheet.
- `metrolineanodes.gpkg`: table `coordenadasmetrolinea` has **24 records**; fields `fid`, `geom`, `MUNICIPIO`, `NOMBRE`, `TIPO`, `LATITUD`, `LONGITUD`, `FOTOS (CANT)`, `OPERATIVA`, `TERMINADA`.
- First eight observed: Quebrada Seca (NO), San Mateo (NO), Chorreras (NO), La Rosita (NO), La Isla (NO), Diamante (NO), Provenza Central (SI), Provenza Oriental (SI); all eight `TERMINADA=SI`. These are research dataset classifications, **not independently verified live status**.
- `ANEXO33_COORDENADAS METROLINEA.xlsx`: sheet `Hoja1`, 28 rows / 9 columns, blank first row, column headers in row 2. First observed entries match the GPKG station records.
- Other original files: two photographic geolocation PDFs; `MAPA ACTUALIZADO METROLINEA 2026.pdf`; three QGIS project files; two proposal maps in PDF and PNG versions; one additional map PDF. These have **not** been reviewed for routes or stop sequences.
- Next: enumerate all 24 stations, compare XLSX vs GPKG, validate coordinates and operational statuses, inspect QGIS layer references and maps, then cross-check active service with dated official sources.


### SITME Android app — candidate operational data source (2026-11-08)
- Google Play: https://play.google.com/store/apps/details?id=com.metgroupsas.siumetrolinea
- Package: `com.metgroupsas.siumetrolinea`; publisher: MET GROUP S.A.S.; Play listing last updated 2026-05-13.
- Play listing explicitly advertises available transit routes, nearby stations, origin-destination trip planning, transfers, estimated times, service notices and alerts. This does **not** independently establish availability of raw route shapes, stop sequences, exact headways or downloadable schedules.
- Research next step: obtain APK from an authorized source and statically inspect app network configuration, route/station models, API base URLs and data schemas; document evidence and redact credentials. No authentication bypass or collection of personal/payment data. Compare route IDs/stations with the Zenodo GIS and official route publications.
- Distinguish this package from `com.metgroupsas.metsiuapp` (METSIU), another app by the same publisher; do not conflate their datasets.

## Consolidated official SITME schedule evidence (2026-11-08)

This section is the **canonical central research register** for identified official SITME route/frequency/window evidence as of 2026-11-08. Its machine-readable 15-record companion is [`data/sitme/official_schedule_sources.csv`](../data/sitme/official_schedule_sources.csv). The CSV is a **research input, not a deployable GTFS timetable**. Local timezone: America/Bogota.

### Evidence classification

- **Observed API inventory:** GitHub Actions [run 42471926616](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42471926616/artifacts/13613444443) produced 15 route records (14 distinct codes) and 529 route-station endpoint rows for 2026-11-08. The API reported no populated `ROUTE_SCHEDULLE` or `ROUTE_DISPATCHS` for any of the 15. Presence of an API record does **not** prove present-day operation.
- **Official planning/programming:** [Metrolínea Q1 2026 management report, PDF pp. 15–16](https://concejobga.cloud/descargas1/CONTROL_POLITICO_METROLINEA_GESTION_ABRIL_2026.pdf) lists *Frecuencia HP/HV* for 12 complementary routes in the **SITM Metrolínea–TPC complementarity** operating model. These values describe the reported operating scheme/planning context; they are **not independently verified November 2026 dispatches**. The participating TPC companies in this scheme must not be confused with an ordinary TPC feed.
- **Superseding service change:** [Metrolínea notice of 2026-05-29](https://www.metrolinea.gov.co/v3.0/sitme-ajusta-sus-rutas-para-servirle-mejor-partir-del-31-de-mayo-2283) explicitly states **PTB and PTN leave service from 2026-05-31**. Both PTN API records and the PTB record therefore remain in the research inventory only. Do not publish them as active without newer evidence of reinstatement.
- **Later route publication:** the [2026-08-31 P19 announcement](https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/) has later, different headways and day-type departures than the Q1 planning table. The figures below are transcribed from the 2026-11-08 source-research notes; recheck the original article before any GTFS activation.
- **Historical references:** [P16N/P16S launch bulletin, 2025-07-30](https://www.metrolinea.gov.co/v3.0/node/2232) and [Metrolínea route fiches, September 2024](https://www.metrolinea.gov.co/v3.0/sites/default/files/2024/9/09/archivos_articulo/rutas_pdf.docx.pdf) provide dated frequency or first/last reference times. They must **not** be silently carried forward into 2026.

### Route-level source inventory

| API ID | API code | Public code | Q1 2026 HP/HV (min) | Other official timing evidence | Assessment for current GTFS |
| --- | --- | --- | --- | --- | --- |
| 3302 | PTB | PTB | — | — | ceased_2026_05_31 |
| 3317 | PTN | PTN | — | — | ceased_2026_05_31 |
| 3341 | P16S | P16S | 7/12 | 2025-07-30: 12 min, 04:20–19:30, Monday–Sunday | requires_current_confirmation |
| 3342 | P16N | P16N | 7/12 | 2025-07-30: 12 min, 04:20–19:30, Monday–Sunday | requires_current_confirmation |
| 3343 | PTN | PTN | — | — | ceased_2026_05_31 |
| 3345 | P08 | P8 | 8/12 | Sep 2024: 04:30–20:00 | historical_departures_only |
| 3346 | P14 | P14 | 12/15 | Sep 2024: 04:50–20:50 | historical_departures_only |
| 3350 | RD27 | RD27 | 8/12 | Sep 2024: 05:00–20:00 | historical_departures_only |
| 3351 | P1 | P1 | 10/12 | Sep 2024: 05:00–20:20 | historical_departures_only |
| 3352 | P2 | P2 | 10/12 | Sep 2024: 04:40–21:40 | historical_departures_only |
| 3353 | P3 | P3 | 8/12 | Sep 2024: 04:40–21:50 | historical_departures_only |
| 3354 | P10 | P10 | 8/10 | Sep 2024: 04:50–20:50 | historical_departures_only |
| 3355 | P18 | P18 | 30/30 | — | missing_departures |
| 3356 | AN3 | AN3 | 10/12 | — | missing_departures |
| 3357 | P19 | P19 | 8/12 | 2026-08-31: weekday/Sat peak 10–12 min, valley 15; Sun/holiday 10/12/15; starts 04:48/05:00/06:00, ends 19:30/18:30/17:30 by day type | newer_official_2026_publication |

**Conflict handling and qualifications:**
1. **P19:** Q1 2026 planning says 8/12 minutes; the later 2026-08-31 publication says peak **10–12** and valley **15** minutes for weekdays/Saturdays. Keep both facts with their dates; the later announcement controls the dated published pattern, but peak/dal clock boundaries are unknown. Different Sunday/holiday intervals are not mapped to known clock windows.
2. **P16N / P16S:** 2025 bulletin says constant 12-minute frequency, 04:20–19:30, Monday–Sunday. Q1 2026 report says 7/12 minutes and describes an eventual **future P16 merger**; the 2026-11-08 API still has separate records, not proof that the merger occurred.
3. **P08 / P8:** record the original API code `P08` and the public report's `P8` as aliases; do not change the stable API ID `3345`.
4. **PTN duplication:** API IDs `3317` and `3343` both use `PTN`; investigate as distinct internal variants, never as two independently confirmed operating routes.
5. **API quality:** inventory has **16 warnings**: one duplicate PTN code and a `station_count_mismatch` for **all 15** records. API detail checkpoints and route/stations endpoint rows have different semantics; do not infer final stop sequences until reconciled.
6. **Station last departures:** the 2026-08-04 restoration of last station departures is **not** a set of per-route `last_departure` values.

### Historical legal context — AMB Resolution 000017, 2014-01-17

The user-supplied 16-page AMB Resolution 000017 modifies SITM feeder alignments **AB2 and AB3** and includes historic route fiches. Examples already extracted from its tables (field **`FRECUENCIA MAXIMA (Min.)`**, not a proven constant headway):

| Route | 2014 first departure | 2014 last departure | 2014 maximum interval (min) |
| --- | --- | --- | --- |
| T1 | 05:30 | 21:00 | 10 |
| T3 | 04:40 | 22:15 | 10 |
| P1 | 04:40 | 22:00 | 12 |
| P6 | 05:00 | 21:30 | 7 |
| P8 | 04:45 | 22:00 | 10 |
| P10 | 05:00 | 22:00 | 10 |
| AP1 | 04:40 | 23:00 | 10 |
| APD1 | 04:15 | 23:00 | 12 |

The resolution also discusses special early/late feeder intervals, Sunday/holiday flexibility, and coordination of headways **by corridor**. These do not justify using a single all-day per-route frequency in a contemporary feed. **Source integrity flag:** the considerations mention a June 2014 letter despite the stated 2014-01-17 date; verify the administrative chronology before relying on effective-date conclusions. This is a **partial historical extract**, not a full transcription of every route in the resolution.

### Source index (retrieved/reviewed 2026-11-08)

| ID | Source and dated scope |
| --- | --- |
| `API_2026_11_08` | https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42471926616/artifacts/13613444443 |
| `Q1_2026` | https://concejobga.cloud/descargas1/CONTROL_POLITICO_METROLINEA_GESTION_ABRIL_2026.pdf |
| `STOP_2026_05_29` | https://www.metrolinea.gov.co/v3.0/sitme-ajusta-sus-rutas-para-servirle-mejor-partir-del-31-de-mayo-2283 |
| `P16_2025_07_30` | https://www.metrolinea.gov.co/v3.0/node/2232 |
| `P19_2026_08_31` | https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/ |
| `FICHES_2024_09` | https://www.metrolinea.gov.co/v3.0/sites/default/files/2024/9/09/archivos_articulo/rutas_pdf.docx.pdf |
| `AMB_2014_000017` | https://www.amb.gov.co/rutas/ |

### Outstanding verification before GTFS publication

1. Obtain exact clock boundaries for `hora pico` and `hora valle` (route and day type) rather than inventing generic peak hours.
2. Confirm whether the Q1 2026 programmed headways were actually operated and identify any later route-specific overrides.
3. Confirm current first and last dispatches for P1, P2, P3, P8, P10, P14, RD27, P18 and AN3; keep 2024 values historical.
4. Keep PTB and both PTN API records out of active 2026-11-08 service pending formal reinstatement evidence.
5. Reconcile the route-station quality warnings and distinguish planning geometry and API checkpoints from confirmed stop sequences.
6. Exclude unverified calendar/day-type assumptions; do not create GTFS `frequencies.txt` or `stop_times.txt` directly from this evidence ledger.

### Focused investigation: peak/off-peak clock boundaries (2026-11-08)

**Research outcome: the exact switch-over clock times for the 12 complementary routes in the current 2026 model remain UNKNOWN.** The Q1 2026 [official management report, PDF pages 15–16](https://concejobga.cloud/descargas1/CONTROL_POLITICO_METROLINEA_GESTION_ABRIL_2026.pdf) gives route-specific **HP/HV headways** but **no time-of-day bands**. The [2026-08-31 municipal P19 notice](https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/) likewise distinguishes peak/valley frequencies but does not state when each applies. A review of the [2025 annual report](https://www.metrolinea.gov.co/v3.0/sites/default/files/informe_gestion_anual_consolidado_2025_compressed.pdf) did not reveal a supported current clock-boundary definition. **Do not populate `frequencies.txt.start_time` or `end_time` from a guessed universal peak period.**

The documented **historical** time references below must retain source date, applicable route, and meaning. The machine-readable trace is in [`data/sitme/peak_valley_window_evidence.csv`](../data/sitme/peak_valley_window_evidence.csv).

| Source / regime | Exact documented times | What they mean | Can be used as 2026 HP/HV boundaries? |
| --- | --- | --- | --- |
| [Metrolínea, 2018-06-14 vacation adjustment](https://www.metrolinea.gov.co/v3.0/metrolinea-ajustara-su-operacion-por-temporada-vacacional-1364) | APD3 08:30–11:42; 14:06–17:18; 19:42–21:18 | Three **route-specific temporary valley operating windows** from 2018-06-15 | **No** |
| [Metrolínea, 2020-05-03 economic reopening](https://www.metrolinea.gov.co/v3.0/el-sistema-metrolinea-ajusta-su-operacion-ante-la-reactivacion-economica-1583) | 06:00–08:00; 16:00–18:00 | **Observed passenger demand peaks in 2020 COVID conditions**, not a dispatch programming calendar | **No** |
| [Metrolínea, 2020-06-01 changed service](https://metrolinea.gov.co/v3.0/node/1590) | P9 05:40–07:40 (morning, south→north) and 15:40–18:40 (afternoon, opposite direction); T3 04:40–08:40 | **Route-specific peak-only operation** for the 2020 temporary network | **No** |
| [Metrolínea, 2022-08-26 station notice](https://www.metrolinea.gov.co/v3.0/estaciones-estancia-mensuli-campoalegre-y-espanolita-cerraran-en-horas-valle-1971) | Four Piedecuesta stations closed 09:00–16:00 and again from 20:00 | **Station staffing/closure rule** for valley hours from 2022-08-29, **not** the scheduled per-route headway bands | **No** |
| [Metrolínea, 2022 complementarity proposal V3 (document pp. 44–45)](https://concejobga.cloud/descargas/RESPUESTA_METROLINEA_PROPOSICION_93_3_2022.pdf) | No boundaries | Has **three distinct frequency columns HP / HI-HF / HV**. Column labels are confirmed; do not infer HI/HF clock boundaries. It is also a **proposal**. | **No** |
| [Metrolínea, 2024 Q4 report](https://metrolinea.gov.co/v3.0/sites/default/files/informe_de_gestion_cuarto_trimestre_2024_ok_firmado.pdf) | No verified boundaries | Route-level HP/HV frequency and cycle tables, without evidence of actual period switch times | **No** |
| [Metrolínea, Q1 2026 report](https://concejobga.cloud/descargas1/CONTROL_POLITICO_METROLINEA_GESTION_ABRIL_2026.pdf) | No boundaries | Official route-level HP/HV headways for 12 complementary routes | **No** |
| [Bucaramanga, 2026-08-31 P19](https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/) | No peak/valley switch times | Day-type headways and first/last departures; terms **hora pico**, **hora valle** lack clock boundaries | **No** |

**Why this matters:** Metrolínea's [official glossary](https://www.metrolinea.gov.co/v3.0/node/363) defines `Franjas Horarias` as ranges in which a uniform frequency applies, and `Tabla-Horaria` as a precise dispatch table (and arrivals at stations). Thus the best next **primary-source target** is the dated **`programación operativa` / `tabla-horaria` / `plan de servicios` / dispatch sheets** for the 2026 complementary network, with **route ID, direction, working day/Saturday/Sunday-holiday, and each HP/HV transition**. Ask specifically for the current program used for P1, P2, P3, P8, P10, P14, RD27, P16N, P16S, P18, AN3, and P19.

**Status:** `current_peak_window_confirmed=false` and `current_valley_window_confirmed=false` for all 12 complementary routes. Historical traces are preserved only for future comparison; no assumptions or edits to the GTFS generator were made.

