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
| 3350 | RD27 | RD27 | 8/12 | 2023-06 temporary last 19:10 from Portal del Valle; no RD27 times in cited Sep 2024 poster | missing_departures |
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

### Provisional weekday HP/HV classification — user-approved modelling baseline (2026-11-08)

**Decision:** use the previously recorded **historical** hour bands as the starting point for a **provisional** SITME service-planning model. This is an explicit modelling choice, **not** a finding that the 2026 Metrolínea dispatch schedule uses these exact boundaries. It supersedes the earlier research-only decision to leave all working periods unassigned; it does **not** overwrite any historical source or promote inferred boundaries to verified facts.

The model is versioned in [`data/sitme/provisional_peak_valley_windows.csv`](../data/sitme/provisional_peak_valley_windows.csv). Local times use `America/Bogota`; ranges are half-open (`start <= t < end`). **Default scope: provisional weekday (Monday–Friday) classification only.** Saturday, Sunday and public-holiday headway-band transitions remain **unassigned**, even where the latest P19 source discusses peak and valley on those days.

| Local time | Provisional classification | Evidence / inference |
| --- | --- | --- |
| Before 06:00 | **HV** (off-peak) | **Model assumption**: earlier starts exist historically, but no published network-wide 2026 frequency-band boundary |
| 06:00–08:00 | **HP** (peak) | Metrolínea described this as a **demand peak in 2020**; not proof of dispatch frequency bands |
| 08:00–16:00 | **HV** (off-peak) | 2022 described **09:00–16:00** as station valley closure; **08:00–09:00 is extrapolated** |
| 16:00–18:00 | **HP** (peak) | Metrolínea described this as an **afternoon demand peak in 2020**; not proof of programmed 2026 headways |
| After 18:00 | **HV** (off-peak) | 2022 station notice refers to valley from **20:00**; **18:00–20:00 is extrapolated** |

**Interpretation / guardrails:**
1. These five rows **only classify the time of day**. They do **not** authorize service during 00:00–06:00 or 18:00–24:00. Any eventual timetable must **clip every row to the route's independently evidenced first/last departure, day type and validity date**. An unknown service window remains unknown, not 00:00–24:00.
2. The Q1 2026 official route frequencies (HP/HV minutes) remain untouched in `official_schedule_sources.csv`. This table can provisionally map those labels to clock bands **only for research/simulation**, never as a verified current timetable.
3. **P19:** a later 2026-08-31 publication reports different headways from Q1 2026: weekday/Saturday peak **10–12 min** and valley **15 min**, and Sunday/holiday **10, 12 or 15 min**, without assigning precise sub-bands. Do **not** silently choose either 10 or 12 for the whole peak. The provisional weekday band classification may be used for comparison, but the numeric headway remains a range until better evidence exists.
4. **P16N/P16S:** preserve the distinct 2025 all-day 12-minute publication and Q1 2026 HP/HV (7/12) values; using the model does **not** establish the transition date between these schemes.
5. **PTB and PTN:** remain marked discontinued from 2026-05-31; do not apply provisional active service to them merely because the API still exposes their IDs.
6. **Historical exceptions** (P9 in 2020, APD3 in 2018, individual station closures in 2022) are not universal rules and remain in the evidence register with their original periods.
7. The working model has **no GTFS publication status**. This repository remains **research only**; **no generator or feed exists**. If a future generator uses assumed periods, it must explicitly disclose modelling provenance and allow authoritative route/day-type overrides.

**Point 1 decision:** closed **provisionally with documented assumptions**; the request for the actual route/day-type `programación operativa` / `tabla-horaria` remains an evidence gap. Next focus: verify current route-level first and last departures (point 2) before deriving complete usable service windows.

### Point 2 — first and last departure evidence (2026-11-08)

**Status: partly documented, not fully resolved for current 2026 service.** Preserve source **date**, **day type**, **departure location**, and **kind of time** separately. The structured companion is [`data/sitme/first_last_departure_evidence.csv`](../data/sitme/first_last_departure_evidence.csv), containing **29 source-specific rows** and blanks for unavailable times. These are evidence records, not synthesized 2026 GTFS service windows.

#### Key findings — most recent dated sources

1. **P19: full route-level first/last departures published 2026-08-31**, effective 2026-09-01. [Bucaramanga article](https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/) reports:
   - Weekdays **04:48–19:30**.
   - Saturdays **05:00–18:30**.
   - Sundays/holidays **06:00–17:30**.
   These are the best currently found route-specific day-type service-window values (subject to later changes). They are NOT frequency-class transition times.
2. **P16N and P16S: two distinct 2025 primary sources**:
   - Metrolínea's [2025-07-30 launch article](https://www.metrolinea.gov.co/v3.0/node/2232) publishes **route operating hours 04:20–19:30**, Monday–Sunday, 12-minute frequencies. The article does not give a specific departure station for those headline times.
   - The official [Q3 2025 report (printed page 88, PDF page index 88)](https://www.metrolinea.gov.co/v3.0/sites/default/files/informe_de_gestion_concejo_tercer_trimestre_compressed-1.pdf) contains a *Portal Piedecuesta* **first/last trip table** for P16N and P16S: weekday **04:45–21:00**, Saturday **04:45–20:30**, holiday **P16N 04:45–20:00** and **P16S 04:45–21:00**. These **station-specific** records cannot be silently compared to a whole-route operating-hours claim as if both described the same starting terminal.
3. **P8/P08**: the same Q3 2025 *Portal Piedecuesta* table gives **last trip** weekday **22:40**, Saturday **21:40**, holiday **20:30**, but marks the **first trip N/A**. Do not infer a P8 first-trip time from that table. These values refer to Portal Piedecuesta, not necessarily the route's full-day terminal dispatch window.
4. **All-route last trips at stations, from 2026-08-04:** [Metrolínea's post-vacation announcement](https://dev.metrolinea.gov.co/v3.0/sitme-normaliza-sus-horarios-de-operacion-desde-este-martes-4-de-agosto-2296) announces weekday last departing services at Portal del Norte **21:30**, Parque Estación UIS **21:50**, Provenza Occidental **22:10**, Portal Piedecuesta **22:40**. These are **station-level system announcements**, not a schedule for any specified route. **Never apply 22:40 to P8/P16 merely because that time appears for Portal Piedecuesta.**
5. **Six route fiches from September 2024 (historical only):** [official 2024 route poster, page 1](https://www.metrolinea.gov.co/v3.0/sites/default/files/2024/9/09/archivos_articulo/rutas_pdf.docx.pdf) prints the following **HORA INICIO/HORA FIN**, without specifying a day-type and direction-specific dispatch table:

| Route | Sep 2024 published start | Sep 2024 published end | Caution |
| --- | --- | --- | --- |
| P1 | 05:00 | 20:20 | historic whole-route fiche |
| P2 | 04:40 | 21:40 | historic whole-route fiche |
| P3 | 04:40 | 21:50 | historic whole-route fiche |
| P8 | 04:30 | 20:00 | historic whole-route fiche; note later 2025 portal-specific P8 evening values |
| P10 | 04:50 | 20:50 | historic whole-route fiche |
| P14 | 04:50 | 20:50 | historic whole-route fiche |

**Correction to previous register:** `RD27 05:00–20:00` had been attributed to this September 2024 poster. **The poster does not list RD27**, so the claimed 2024 times are **withdrawn as unsupported** and removed from `official_schedule_sources.csv`. The [temporary June 2023 vacation notice](https://metrolinea.gov.co/v3.0/el-sitm-metrolinea-adelanta-cierre-de-operacion-por-temporada-vacacional-2066) gives a last RD27 departure at **19:10 from Portal del Valle**, only for that temporary historical regime. No current RD27 first/last departure has been verified.
6. **AN3 and P18:** no route-specific first/last trip clock times located in the official publications reviewed for 2025–2026. The Q1 2026 operating-plan frequency table is NOT a full timetable. AN3's earlier 2022 service history must not be used to infer 2026 hours: [Metrolínea launched AN3 in February 2022](https://www.metrolinea.gov.co/v3.0/node/1833), and later 2022 socialization records refer to suspension in April 2022; the Q1 2026 register again describes AN3 under a changed operator. Preserve dates rather than merge different historical incarnations.

#### Current coverage and next work

- **2026 route-specific weekday/saturday/holiday first and last:** P19 only (one of 12 complementary route codes).
- **2025 station-specific portal times:** P16N/P16S/P8; useful but not directly comparable to a route terminal's first/last dispatch.
- **2024 historical full-route service-hour references:** P1/P2/P3/P8/P10/P14; may be considered as **unverified model candidates only after an explicit research decision**, never promoted automatically.
- **Gaps:** current terminal departures, direction, day type and effective dates for P1/P2/P3/P8/P10/P14/RD27/P16N/P16S/AN3/P18; especially no meaningful recent route-level times for AN3/P18 and no corroborated first/last for RD27. PTB/PTN remain excluded pending evidence of reinstatement.
- **Target for follow-up:** 2026 **`programación operativa` / `tabla-horaria`** and route-end terminal dispatch sheets; the last departure from a *station* must be linked to an actual route ID, direction and terminal before inclusion.
- **No GTFS generator or published GTFS feed exists in this repository.** No generator code is modified by this registration.

## Historical route poster baseline and dated change tracking (2026-11-08)

**User-approved source policy:** the Metrolínea [`NUEVAS RUTAS DEL MASIVO 2024` official poster](https://www.metrolinea.gov.co/v3.0/sites/default/files/2024/9/09/archivos_articulo/rutas_pdf.docx.pdf) is the **reference starting point** for this project. We **preserve all 12 poster entries** as a dated, immutable historical baseline, then track later changes **as independent dated events**. This is a **research baseline**, not a statement that every 2024 route or timetable still operates in 2026.

Files:
- **[2024 official baseline](../data/sitme/baseline_routes_2024.csv)** — complete 12-route transcription of poster's route codes, origin/destination, `HORA INICIO`, `HORA FIN` and `FRECUENCIA` (minutes); `day_type` is `not_specified` because the poster does not specify one. A min/max range is retained where the poster prints it. Only the six matching public route codes are linked to API IDs from the 2026-11-08 snapshot.
- **[Dated change log](../data/sitme/route_change_log.csv)** — **19 entries** recording observed changes/new route publications, 2026 Q1 operational-program frequency classifications and confirmed route termination notices, with source date, effective date when known, day type, source scope and original URL.
- **[2026 API inventory and source comparison](../data/sitme/official_schedule_sources.csv)** — 15 API records (14 public codes); do not treat an API row as a live trip.
- **[First/last departure evidence](../data/sitme/first_last_departure_evidence.csv)** — source-specific departure records, including station times, which do not automatically override the origin-terminal's route operating hours.
- **[Historical provisional peak/off-peak clock model](../data/sitme/provisional_peak_valley_windows.csv)** — separately marked assumptions, not verified 2026 scheduling periods.

### Complete 2024 route poster baseline

| Route | Poster first | Poster last | Poster frequency (min) | 2026 SITME API code observed? |
| --- | --- | --- | --- | --- |
| RDF | 04:50 | 21:50 | 10 | No |
| AP9 | 04:45 | 22:15 | 12–15 | No |
| P1 | 05:00 | 20:20 | 15 | Yes |
| P2 | 04:40 | 21:40 | 15 | Yes |
| P3 | 04:40 | 21:50 | 15 | Yes |
| P8 | 04:30 | 20:00 | 15 | Yes, API spells `P08` |
| P10 | 04:50 | 20:50 | 10 | Yes |
| P14 | 04:50 | 20:50 | 10 | Yes |
| P17 | 05:00 | 19:00 | 10–12 | No |
| MORRO | 05:00 | 20:00 | 12 | No |
| 44 | 05:00 | 19:00 | 15 | No |
| D15 | 04:40 | 20:00 | 15 | No |

The poster does **not** include RD27, P16N, P16S, P18, P19, AN3, PTB or PTN. Absence from the poster does **not** prove those routes did not exist; absence from the 2026 API of RDF/AP9/P17/MORRO/44/D15 does **not** prove their legal termination. These are **different-date inventories**, not a definitive list of openings and closures.

### Reading the change log (do not conflate evidence types)

- **2025-07-30:** two new complementary route publications for P16N/P16S: `04:20–19:30`, 12 minutes, Monday–Sunday. This route-level source is not a Portal Piedecuesta-specific dispatch table.
- **Q1 2026:** 12 complementary route codes have HP/HV programmed headways in the official report, with **no proven effective date, specific day type, or clock boundary**. This is recorded as an `operational_model_peak_offpeak` event rather than a verified, dispatch-level schedule update. Differences from the 2024 poster are **historical comparisons**, not verified dates of frequency change.
- **2026-05-31:** PTB and PTN exit operation per Metrolínea's 2026-05-29 notice; it remains true even though the 2026-11-08 API retains PTB and two PTN records.
- **2026-09-01:** later published P19 route-level day-type windows replace the older source for that route/period: weekdays `04:48–19:30`, Saturdays `05:00–18:30`, Sundays/holidays `06:00–17:30`. Peak is **10–12 min** and off-peak **15 min** on weekdays/Saturdays; Sunday/holiday published 10/12/15 min values lack clock assignments.
- **P16 terminal ambiguity:** 2025 Q3 *Portal Piedecuesta* departures are separately stored in `first_last_departure_evidence.csv`. Do not overwrite `04:20–19:30` headline route hours with station departure values.
- **No baseline RDF/AP9/P17/MORRO/44/D15 change evidence** has been verified; leave their present-day status **unknown**, not inactive-by-inference.

### Future update procedure

1. Identify the **specific route code**, normalize public aliases only (`P8 ↔ P08`), and preserve distinct API IDs.
2. For each new document, add a **new event** to `route_change_log.csv` with publication date, effective date **only if explicitly stated**, day type, source URL, before/after *comparability* and scope (route-level vs station-level vs proposed operating model). Do **not** overwrite `baseline_routes_2024.csv`.
3. When sources conflict, retain both dated records. Prefer later **explicitly applicable** route-specific operational sources **only for the same field and scope**; distinguish programmed HP/HV frequencies, published route operating times, actual terminal dispatches and station departure cutoffs.
4. Do not treat the 2024 poster's start and end times as verified 2026 first/last trips. Use them as **fallback research candidates** for missing 2026 windows; flag any subsequent use as assumption.
5. The working model of weekday peak/valley periods remains provisional, and Saturdays, Sundays and holidays are not assigned inferred frequency bands without an explicit policy.
6. **GTFS generator: not yet created.** These registers only establish the research and change-management basis for a future GTFS build.

### PTB and PTN historical service-window addendum — 2026-11-08

**Correction to earlier point-2 gap inventory:** PTB **does** have a documented historical operating window from an official 2026 source. PTN has a **secondary (Moovit), undated/stale candidate**; the latter is **not** official confirmation. Neither route should enter the active service calendar after the [2026-05-31 closure](https://dev.metrolinea.gov.co/v3.0/sitme-ajusta-sus-rutas-para-servirle-mejor-partir-del-31-de-mayo-2283).

**PTB, from Bucaramanga's [official 2026-04-07 article](https://www.bucaramanga.gov.co/noticias/sitme-pone-en-operacion-la-nueva-ruta-ptb-eje-estrategico-de-la-movilidad-en-bucaramanga/), service started 2026-04-06:**

| Day type | Published route operating hours | Published headway |
| --- | --- | --- |
| Monday–Friday | **05:00–22:00** | **10 min** |
| Saturday | **05:00–21:00** | **15 min** |
| Sunday/public holiday | **05:30–20:00** | **25 min** |

The 2026 Q1 management report [PDF](https://concejobga.cloud/descargas1/CONTROL_POLITICO_METROLINEA_GESTION_ABRIL_2026.pdf) documents **different programmed intervals for PTB** (weekday HP/HV 10/12; Saturday 15; Sunday/holiday 20). This is a **source discrepancy**: an earlier operating-plan table vs a later route-launch announcement. Keep both by date/scope; use the later official dated announcement as PTB's published service-hour reference for **April–May 2026**, not as verified terminal dispatch times. The route was discontinued from 2026-05-31.

**PTN secondary candidate:** [Moovit PTN schedule page](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-ptn-Bucaramanga-4324-3595156-308529268-0) displays **Monday–Saturday 05:00–21:00 with 12-minute frequency; Sunday: no service**. The web page does not provide an unambiguous **historical validity date** and still describes PTN service despite the official 2026-05-31 cessation. Treat as a **stale third-party historical candidate**, not proof that PTN operated those hours on any particular day or that either PTN API ID 3317 vs 3343 uses that exact window. The [2025 Q4 report](https://www.metrolinea.gov.co/v3.0/sites/default/files/informe_gestion_concejo_4_trim_2025_0.pdf) describes a **projected** PTN+ frequency range of **7–12 minutes** with full fleet, without confirmed day-type dispatch windows. **Official PTN first/last departure remains unverified.**

Both are appended as separate source-specific rows to [`first_last_departure_evidence.csv`](../data/sitme/first_last_departure_evidence.csv) and as **4 further events** to the [dated change log](../data/sitme/route_change_log.csv); the 2024 baseline remains unchanged.

### Point 2 follow-up — closing three missing-window research leads (2026-11-08)

**Decision:** for the purpose of the **provisional, historically grounded research baseline**, RD27, P18 and AN3 now have **complete candidate daily service windows**, sourced from secondary **Moovit** route timetable pages. The source pages do **not** give a reliable timetable effective-date history; these values are not confirmed as 2026 operator dispatchs. This supersedes the previous **"no usable window found"** research status for these three routes, but **does not** mean their exact present-day timetables or weekday/holiday calendars have been verified. The 2024 poster remains the **baseline only for routes on that poster**; none of these three appears on it.

| API route | Provisional candidate service hours | Days shown by Moovit | Moovit published headway (secondary, not adopted) | Q1 2026 official programmed HP/HV minutes (retained) |
| --- | --- | --- | --- | --- |
| **RD27** (`3350`) | **05:00–20:00** | Monday–Sunday | 30 | **8/12** |
| **P18** (`3355`) | **05:00–20:00** | Monday–Friday; Sat/Sun listed without service | 50 | **30/30** |
| **AN3** (`3356`) | **05:00–19:48** | Monday–Saturday; Sun listed without service | 20 | **10/12** |

**Sources / provenance, checked 2026-11-08:**
- [Moovit RD27, Portal del Valle → Parque Estación UIS](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-rd27-Bucaramanga-4324-3277577-301161825-0): 05:00–20:00 daily. Not a demonstrated **terminal-specific first/last dispatch** for all RD27 route variants or dates.
- [Moovit P18, Provenza Oriental ⇄ Terrazas](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-p18-Bucaramanga-4324-926178-350266610-0): 05:00–20:00 weekdays only. This is an operating span of the described loop, not exact dispatch by stop.
- [Moovit AN3, María Paz ⇄ Bosconia](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-an3-Bucaramanga-4324-926180-337429893-0) and [Moovit AN3, Portal Norte ⇄ Bosconia](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-an3-Bucaramanga-4324-926180-344193123-0): **two different circular patterns** each list 05:00–19:48 Monday–Saturday and no service Sunday. This is NOT proof there are two SITME API route IDs: the 2026-11-08 snapshot has a single AN3 ID `3356`. Preserve the pattern distinction for future stop-sequence reconciliation.
- [Caracol Radio, 2022-02-12 AN3 inauguration coverage](https://caracol.com.co/emisora/2022/02/12/bucaramanga/1644677416_039364.html) reports a **historical 05:00–21:00** system-standard window for the launch planned from 2022-02-14. This is a separate time-period and secondary account; **the days of operation are not stated**. Do not overwrite the undated Moovit 19:48 or claim the 2022 window is current.
- [Metrolínea Q1 2026 operating report, pp. 15–16](https://concejobga.cloud/descargas1/CONTROL_POLITICO_METROLINEA_GESTION_ABRIL_2026.pdf) retains official **route-specific programmed** peak/valley frequencies. Do not use Moovit frequency values (30, 50, 20) to replace the official HP/HV (8/12, 30/30, 10/12).
- Official [SITME deviation notice, 2026-10-14](https://www.bucaramanga.gov.co/noticias/sitme-informa-sobre-desvios-operacionales-por-jornada-de-protestas-en/) uses `RD27-15` alongside other routes. **Check how the combined RD27/RD15 operation maps to API route `3350` before claiming that every 2026 service uses the historical separate RD27 span.** This notice confirms route-identifier context, **not** first/last trip times.

**Data updates (append-only where appropriate):**
- [`first_last_departure_evidence.csv`](../data/sitme/first_last_departure_evidence.csv): **5 new source-specific rows** (RD27, P18, two AN3 patterns, and separate 2022 AN3 historical item) — now **34** evidence records.
- [`route_change_log.csv`](../data/sitme/route_change_log.csv): **4 new evidence events** (three undated Moovit candidate windows plus separate 2022 AN3 report) — now **27** recorded events. No false `effective_from` is assigned to Moovit.
- [`official_schedule_sources.csv`](../data/sitme/official_schedule_sources.csv): the three API route rows are now classified `secondary_window_candidate_only` with first/last **candidate** clock values and their source IDs; `eligible_for_current_gtfs_without_more_evidence` remains **No** for every affected row.
- [`baseline_routes_2024.csv`](../data/sitme/baseline_routes_2024.csv) is **unchanged**.

**Point 2 practical status: historic/provisional window coverage is now complete for the 12 2026 Q1 complementary routes** (6 from 2024 official poster, P16N/P16S from 2025 operator publication, P19 from later 2026 municipality publication, and RD27/P18/AN3 from secondary Moovit evidence). PTB has an official Apr–May 2026 historical window; PTN has only a secondary undated historic candidate. This is **baseline completeness**, not the same as verifying all day types, route-specific terminal departures, daily active service, or exact timetable validity. Retain those gaps for future primary-source checking.

**Next research phase:** point 3, reconcile which route codes/patterns were actually operated on the intended reference date. No GTFS generator or published feed has been created.

## Point 3 — operational route and variant verification (snapshot 2026-11-08)

**Research principle:** a route returned by the SITME API is a route *database entry*, **not** proof of active passenger operation. The previous [run 42471926616 snapshot](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42471926616) was rechecked **directly using the locally supplied** `sitme-route-snapshot.zip` (`2026-11-08/route_detail.json`, `route_stations.json`, `inventory.json`). It contains **15 route records / 14 distinct public codes**. All 15 have `ROUTE.VISIBLE=1`, including PTB and both PTN rows that were explicitly ceased as of May 31. For **all 15 records**, `ROUTE_DISPATCHS=[]`, `ROUTE_SCHEDULLE=[]` and `ROUTE_SCHEDULLE_NOVELTY=[]`. **Neither visibility nor presence of geometry/stops is evidence of actual dated dispatch.**

Two new structured results are the source of truth for this verification stage:
- [`data/sitme/route_operational_status_2026-11-08.csv`](../data/sitme/route_operational_status_2026-11-08.csv): **21 entries** — 15 exact API IDs + the six 2024-poster-only route codes; explicit source evidence/status per record.
- [`data/sitme/route_variant_review_2026-11-08.csv`](../data/sitme/route_variant_review_2026-11-08.csv): **8 detailed variant and identification cases**, including confirmed aliases and unresolved source equivalences.
These are **status observations**, not edits to or replacements for [`baseline_routes_2024.csv`](../data/sitme/baseline_routes_2024.csv) or a GTFS generator (none exists).

### 2026-11-08 API snapshot: source-graded operation status

| Classification | API records | Distinct codes | Interpretation |
| --- | --- | --- | --- |
| **2026 primary-source operation evidence** | 10 | **P1 P2 P3 P8 (API `P08`) P10 P14 P16N P16S RD27 P19** | Later official notices explicitly identify service/corridor or planned event diversions for those routes. Not a check of live vehicle trips at 2026-11-08  |
| **Only Q1 2026 planning + API (+secondary timetable data)** | 2 | **P18 AN3** | Have documented planned frequencies, geometry and route names, and secondary Moovit timetables, but no independently confirmed later official operation date found. **Do not mark definitively active or cancelled** |
| **Explicitly ended 2026-05-31** | 3 | **PTB PTN** | Official 2026-05-29 announcement explicitly removes these services on 2026-05-31; API still exposes PTB (3302), PTN (3317), PTN (3343). **Do not count as active** |
| **Only September 2024 poster, not in API inventory** | 6 additional historic codes | **RDF AP9 P17 MORRO 44 D15** | Absence from this API snapshot is not legal proof of termination, nor proof that an integrated TPC descendant is absent |

**2026 official operational sources and evidence limits:**
- **2026-10-16**, Bucaramanga municipality [Media Maratón diversion notice](https://www.bucaramanga.gov.co/noticias/metrolinea-informa-desvios-del-sitm-por-media-maraton-fcv/) lists complementary **P1, P2, P3, P8, RD27-15** among the routes affected by the October 17/18 event. These are recent evidence of planned operation, not confirmed actual GPS operation for every calendar date.
- **2026-10-14**, Bucaramanga municipality [protest diversion notice](https://www.bucaramanga.gov.co/noticias/sitme-informa-sobre-desvios-operacionales-por-jornada-de-protestas-en/) explicitly identifies **P3, P14, P16N, P16S, RD27-15** separately, strongly arguing **against treating the previously discussed P16N/P16S unification as completed**.
- **2026-05-29**, [Metrolínea operator closure notice](https://dev.metrolinea.gov.co/v3.0/sitme-ajusta-sus-rutas-para-servirle-mejor-partir-del-31-de-mayo-2283): **PTB and PTN end on 2026-05-31**; replacement service through **P19**, **P1**, **P10 and P14**. The same notice says 12 complementary and 13 integrated routes as a system-level claim; this is **not** a named current 12-route roster.
- **2026-08-31**, [municipal P19 announcement](https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/): confirms P19 route and distinct direction tracings with service changes effective **2026-09-01**. Earlier Q1 P19 headway 8/12 and later published headway 10–12/15 are both retained with dates.
- **Q1 2026**, [official Metrolínea management report (PDF report pages 13–16)](https://concejobga.cloud/descargas1/CONTROL_POLITICO_METROLINEA_GESTION_ABRIL_2026.pdf) enumerates the twelve *planning-model* routes, including P18 and AN3. Parts of the document explicitly describe expansion and **routes projected under the transition**. The table alone **does not verify individual actual operations on November 8**, and must not be interpreted as a date-resolved dispatch log.

### Internal API variants and identity caveats

1. **PTN API IDs are not identical copies.** `3317` has a Portal Norte **round-trip geometry with 597 DETAIL elements and 28 STATIONS rows**; `3343` is a Provenza Oriental → Portal Norte **directional geometry with 156 DETAIL and 14 STATIONS rows**. The source contains both `VISIBLE=1` in November despite May cessation. Keep **both historical IDs with separate geometries**; a shared public `PTN` code does not make two independent active public services.
2. **RD27/RD15 direction pairing.** Official [2022-09-01 launch notice](https://metrolinea.gov.co/v3.0/se-implementa-la-ruta-rd27-y-rd15-entre-portal-del-valle-y-el-parque-estacion-uis-1972) documents **RD27 outward via carrera 27**, **RD15 return via carrera 15**, joining Portal del Valle and UIS. October 2026 notices use the combined designation **RD27-15**. SITME API code `RD27` (ID `3350`) has **1,047 DETAIL elements and 94 STATIONS rows** covering a loop from Portal del Valle back to that portal. Its **directional stop sequence and exact current mapping still need verification**; do not invent an independent RD15 API record or double count trips.
3. **P16N and P16S remain distinct in official notices dated October 2026.** Q1 planning's future **P16** unification was a *proposal*, not evidence of a completed replacement.
4. **P08 is public P8.** One API ID `3345`, no second P8 service.
5. **AN3** has one API ID `3356` (421 DETAIL / 16 STATIONS), but secondary Moovit describes more than one circular pattern. An official Q1 2026 trace includes Bosconia, Portal Norte and María Paz. Do not generate new variants or active runs until matched to the same stop sequence.
6. **2024 P17 and Q1 2026 planned P17 are not automatically the same route**: 2024 fiche describes a Café Madrid/Provenza/Porvenir service; the 2026 proposal describes Oasis–Centro–UIS. Likewise, **2024 MORRO** may relate to integrated **03 Morro**, but no ID and service-lineage equivalence has been proved.
7. **Out-of-snapshot planning mentions:** the Q1 2026 report also contains proposals and descriptions for `P20`, `P17`, `PT2`, `PT3` and `RG27`. They are **not included among the 15 API route records**; this is not evidence that these services never existed, but no current trips should be inferred for them from the planning section alone.

### Remaining point-3 checks

1. **P18 and AN3:** find a post-Q1-2026 operator route roster, operating log or independent verifiable official dated operation notice. Moovit route listings are secondary timetable evidence; operating today remains **unconfirmed**.
2. **RD27-15:** inspect 2026 route geometry and ordered stations for the outbound/inbound pattern relationship, especially how RD15 maps onto API `3350`.
3. **AN3:** establish whether two apparent Moovit loops are true distinct stopping patterns or presentation variants of API `3356`.
4. **2024 historical routes and proposed 2026 changes:** track separate changes/crosswalks; do not add routes to the current GTFS scope solely because of a poster, API presence or proposal.
5. **Official AMB legal scope:** the AMB [2026 Secretaría General register](https://www.amb.gov.co/resoluciones-secretaria-general-2026/) lists **Resolution 000349 of October 26, 2026**, extending/redefining Metrolínea's operator authorization in the context of Resolution 000058/2026 and SITME. The **actual article-level provisions and route annexes have not been reviewed** in this verification; the listing proves the document exists, not which routes were operational.
6. The **15 existing route–station discrepancy warnings** from the SITME scraper remain a later stop-matching quality task. An API `STATIONS` entry is not yet a verified GTFS `stop_times` sequence.

**Point 3 research status: in progress**, with confirmed closure of PTB/PTN, primary-source operation evidence for 10 2026 complementary route codes, and unresolved actual operation of P18/AN3 and some directional variant mappings. **No GTFS generator exists.**

## Point 3 — historical versus active routes: 2026-11-08 assessment

**Scope and interpretation.** We assessed **all 15 API records** in the SITME 2026-11-08 route inventory (14 public codes: `PTN` appears twice) against dated **official 2026 operation announcements**, and, where absent, secondary Moovit listings. The result is recorded row-by-row in [`data/sitme/route_activity_assessment_2026-11-08.csv`](../data/sitme/route_activity_assessment_2026-11-08.csv). **A route record with stops in the API is not proof of a live bus, and official announcements dated before 8 November cannot prove the presence of trips on the actual reference day.** Status is therefore "recently officially documented operation", not "real-time active now".

### Evidence-driven classification of the 15 API records

| Status class | API records | Public route codes | Assessment |
| --- | ---: | --- | --- |
| Recent 2026 official operation notice | **9** | **P1, P2, P3, P8 (`P08` in API), P10, P14, P16N, P16S, P19** | Strong basis for continuing service in the research model, barring later cancellations |
| Recent official notice with unresolved route-code matching | **1** | **RD27** API vs **RD27-15** in October 2026 | The combined label is officially mentioned in service detours; verify whether API route 3350 is the same route, a combined route, a directional variant, or a changed designation. Do not double-count RD27 and RD15 |
| 2026 API + Q1 planning table + secondary route listing only | **2** | **P18, AN3** | Active candidates, but no post-Q1 official confirmation found in examined publications; neither automatically exclude nor assert current operation |
| Officially withdrawn as of 2026-05-31 | **3** | **PTB** ID 3302; **PTN** IDs 3317 and 3343 | Historical records only. Two PTN IDs do not establish two independent live services |

**Note:** there are **12 complementary codes** in the official Q1 2026 plan, but the API additionally retains three discontinued PTB/PTN records. The official [2026-05-29 operator notice](https://mail.metrolinea.gov.co/v3.0/sitme-ajusta-sus-rutas-para-servirle-mejor-partir-del-31-de-mayo-2283) says the post-adjustment network consists of 12 complementary and 13 integrated routes. The 2026 API set is **not a complete census of all 13 integrated routes** and this assessment does not cover those separate integrated routes.

### Official 2026 citations that support operation by route

| Route codes | Most relevant official 2026 evidence | Evidence date and interpretation |
| --- | --- | --- |
| P1, P2, P3, P8, **RD27-15** | [Bucaramanga Metrolínea diversion for FCV marathon](https://www.bucaramanga.gov.co/noticias/metrolinea-informa-desvios-del-sitm-por-media-maraton-fcv/) | **2026-10-16**, named as services affected on 17–18 October; **RD27-15 label is not proven to map 1:1 to API RD27** |
| P3, P14, P16N, P16S, **RD27-15** | [Bucaramanga protest diversion](https://www.bucaramanga.gov.co/noticias/sitme-informa-sobre-desvios-operacionales-por-jornada-de-protestas-en/) | **2026-10-14**, specifically named; supports that P16N/P16S still had distinct operation identifiers in October despite earlier planned consolidation |
| P8, P14, P16N, P16S | [Bucaramanga Feria Bonita diversions](https://www.bucaramanga.gov.co/noticias/sitme-anuncia-cambios-temporales-en-la-operacion-por-cierres-viales/) | **2026-09-04**, specific route names and temporary diversion |
| P10, P14, P19, P1 | [Metrolínea 2026-05-29 change after end of PTB/PTN](https://mail.metrolinea.gov.co/v3.0/sitme-ajusta-sus-rutas-para-servirle-mejor-partir-del-31-de-mayo-2283) | Continues P10/P14 corridor, P1 center link, P19 replacement coverage starting 2026-05-31 |
| P19 | [Bucaramanga 2026-08-31 route and timetable publication](https://www.bucaramanga.gov.co/noticias/ruta-complementaria-p19-incorpora-nuevos-medios-de-pago-y-fortalece/) | More recent **2026-09-01** route-specific service and fare validator implementation |
| PTB, PTN | [Metrolínea 2026-05-29 service withdrawal](https://mail.metrolinea.gov.co/v3.0/sitme-ajusta-sus-rutas-para-servirle-mejor-partir-del-31-de-mayo-2283) | Both officially cease operating from **2026-05-31**; retain historical windows from point 2 |
| P18, AN3 | [P18 Moovit](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-p18-Bucaramanga-4324-926178-350266610-0), [AN3 Moovit](https://moovitapp.com/index/es-419/transporte_p%C3%BAblico-line-an3-Bucaramanga-4324-926180-337429893-0) | Secondary route listings **with no reliable source-effective date**; Q1 2026 official planning table and 2026-11-08 API entries independently support *candidate* status but not confirmed current operation |

### Open data-quality and network-scope tasks

1. **RD27 vs RD27-15:** 2026-08-03 [operator diversion](https://www.bucaramanga.gov.co/noticias/sitme-informa-desvios-operacionales-por-cierre-temporal-de-la-autopista-entre-floridablanca-y-piedecuesta/) prints `RD27 -15`; the October official bulletins print `RD27-15`. This supports a possible service combination or merged identifier but **does not resolve mapping** to `3350 RD27` or the distinct `RD15` name in third-party stop data. Verify alignment, stopping pattern, geometry and operator dispatch identity before treating as one or two GTFS routes.
2. **P16N and P16S:** both independently named in September and October 2026 operator notices. The Q1 2026 planning suggestion that the two **might merge** was not an implemented merger by the October notices.
3. **PTN duplicate ID:** `3317` and `3343` are preserved as separate *API record identities* and both share the discontinued PTN public code. Do not create two public routes from these rows.
4. **P18 and AN3:** investigate whether these are actually dispatched in 2026, and whether `AN3` Moovit contains two actual service patterns or only third-party itinerary representations. No official 2026 post-Q1 operation notice found in this phase; these remain **not yet confirmed**, rather than deemed inactive.
5. **2024 poster-only codes** (`RDF`, `AP9`, `P17`, `MORRO`, `44`, `D15`) are **missing from this limited 15-record API snapshot**. That does **not** prove that any of these ceased to exist: some could belong to the integrated network or have different route codes. Preserve poster baseline and investigate separately only if expanding research scope.
6. **Integrated services:** 13 complementary-to-network integrated routes are separately mentioned by the operator. Do not misinterpret the **15-record API snapshot** as the whole network; include separate discovery/route inventory work later.
7. **Research vs publication:** even the nine strongly supported routes have **no confirmed actual 2026-11-08 trip log**, day-by-day holiday service, or validated direction and stop sequence. Source evidence does **not** imply GTFS publication readiness. **No GTFS generator has been created.**

**Point 3 result:** among the **15 API records**, **9** have recent official same-code operation evidence, **1** has recent official evidence under a changed/combined code, **2** remain source-supported *candidates only*, and **3** are explicitly withdrawn. Further research should prioritize **P18, AN3, RD27-15/3350 matching**, then the **13 integrated lines** (separate from this 15-record API sample).

### SITME live monitoring WebSocket probe — workflow run 42521353570

**Run:** [Probe SITME monitoring WebSocket, 2026-11-08 20:40–20:41 UTC](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42521353570) — GitHub Actions job **successful**, artifact [`sitme-websocket-probe` (ID 13633522089)](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42521353570/artifacts/13633522089). The JSON report was inspected (not just the job status). It is a **read-only connectivity probe**, not GTFS output or a verified activity inventory.

| Report field | Recorded value | Interpretation |
| --- | --- | --- |
| Monitoring host / namespace | `https://api.voa.metgroupsas.com` / `/monitoring-route-v2` | Monitoring endpoint identified |
| Engine.IO v4 HTTP polling | HTTP **200**, valid Engine.IO open packet | Polling handshake supported |
| Engine.IO v3 HTTP polling | HTTP **200**, but **not** a valid Engine.IO open packet | No proof of EIO3-compatible polling |
| Socket.IO connected | `connected=true`, `engineio_connected=true` | WebSocket and namespace connection succeeded |
| Subscription | `subscription_sent=true` | Client **emitted** `subscribeToMonitoringContraint`; report does **not** confirm server accepted the subscription |
| Events | `{}` (none) | **No realtime data received** during 40-second listening window |
| Selected route | **PTB / 3302** | Script selects **first API route** when `route_id` is blank; PTB has officially ceased from **2026-05-31**, so it is unsuitable for active-route monitoring validation |
| Room | `195` | Default clientId/room supplied |
| Token source/expiry | `historical_js`; expiry **2025-11-29T15:59:09Z** | No `SITME_MONITORING_TOKEN` secret supplied; hard-coded historical token **expired almost a year before the run**. Socket.IO connection success does **not** prove authorization to receive monitoring events |
| Errors | `error_type=null`, `connect_error=false` | Probe ran without an exception; no events is still an unresolved data result |

**Conclusion for point 3:** The monitoring transport endpoint is reachable, and namespace connection works, but **no bus operation, active vehicle, route-specific trip, or monitoring payload was confirmed**. Hence this run **does not upgrade P18, AN3, RD27 or any other route to "live-verified"**.

**Prioritized follow-up experiment:** run the existing manual workflow with **explicit route ID of a recently officially documented route**, e.g. **P19 = 3357** or **P16N = 3342**, not the automatically selected retired PTB 3302; supply a legitimately obtained **current** monitoring token via the existing Actions secret if authentication is required; listen up to the workflow's maximum of **120 seconds**. Inspect `events` and `event_field_names` in the **sanitized** artifact and then separately validate event timestamps, route IDs and service days. A successful socket connect or emitted subscription should not be reported as verified live feed.

**Implementation note:** the probe currently emits the room identifier `195` to `subscribeToMonitoringContraint`, while `route_id` only selects the route-specific event name and is not included in the emitted subscription payload. Therefore confirm the provider's subscription semantics from authorized client code before inferring that picking a different route ID changes the server's subscription. Avoid logging credentials or full token-bearing URLs.

### Second live-monitoring WebSocket probe — workflow run 42521884064

**Run:** [`42521884064`, 2026-11-08 20:47–20:49 UTC](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42521884064), workflow **Probe SITME monitoring WebSocket**, job result **success**; [sanitized artifact `sitme-websocket-probe` ID `13633389087`](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42521884064/artifacts/13633389087) downloaded and `report.json` independently inspected.

**Experiment changed from previous [run 42521353570](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42521353570):** explicit **`route_id=3357` (P19)**, `room=195`, `listen_seconds=120` (previously auto-selected discontinued PTB 3302 for 40 seconds). This is a deliberately more relevant observation target but **not** a guaranteed active trip during the exact test.

| Check | Actual new run result |
| --- | --- |
| Engine.IO 4 polling handshake | HTTP 200, valid Engine.IO open packet |
| Engine.IO 3 polling handshake | HTTP 200, **not** a valid open packet |
| Socket.IO `/monitoring-route-v2` | Connected; `connected=true`, `engineio_connected=true` |
| `subscribeToMonitoringContraint` | Client says **sent**; no positive acknowledgement of subscription recorded |
| Selected route/room | **3357 (P19)** / **195** |
| Captured monitoring events | **0**: `events={}`, `event_field_names={}` |
| Runtime or connect error | None recorded, `error_type=null`, `connect_error=false` |
| Authentication token | `token_source=historical_js`; JWT expiry **2025-11-29 15:59:09 UTC**, i.e. expired by test time |
| Execution | GitHub job successful = client ran, **not** server dispatch or route activity verified |

**Interpretation:** A longer probe against P19 still received zero events, so **the first run's choice of retired PTB alone does not explain the outcome**. However, this second run provides **no active vehicle data** and cannot establish that P19 has no operating trips, nor that the monitoring endpoint lacks data. The test's historical token is expired; the server may allow namespace connection without authorizing data broadcasts. Subscription details also warrant validation: present code emits **room 195** and uses `route_id` only to construct an event listener, not the emitted payload. Other possible causes include timing or an incorrect room/event subscription.

**Recommended next controlled test:** provide a **fresh legitimately obtained token** using the existing `SITME_MONITORING_TOKEN` GitHub Actions secret; keep route **P19 3357** and room **195** for the first token-only comparison. Verify subscription acknowledgement/event names in the official client, and inspect only sanitized event fields and counts. Do **not** treat successful connection or a 0-event run as definitive activity-status evidence or republish credentials. Do **not** override point 3 activity classifications based on this run.

