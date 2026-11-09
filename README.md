# Bucaramanga — Metrolínea / SITME GTFS research

This repository collects source evidence and verified inputs for a future GTFS Schedule feed covering Bucaramanga's Metrolínea / SITME mass-transit services.

**Status:** research only. No current route, stop, frequency, or timetable data has been verified for publication. This project is separate from the TPC urban collective service feed in `ColombiaTransit/Gtfs-bucaramanga-urbana`.

## Research priorities
1. Confirm the currently operating SITME/Metrolínea network and its official operator(s).
2. Identify authoritative route lists, route variants, and service dates.
3. Evaluate GIS route geometry and stations/stops against current operations.
4. Find documented first/last departures, frequencies, travel times and calendars.
5. Build GTFS only from traceable evidence, with explicit assumptions and validation.

See [research register](docs/research-register.md).

## Schedule research baseline and change history
The official [September 2024 Metrolínea route poster](https://www.metrolinea.gov.co/v3.0/sites/default/files/2024/9/09/archivos_articulo/rutas_pdf.docx.pdf) is the **dated historical baseline**; all later route changes and scheduling evidence are recorded separately. This baseline is **not** a verified current timetable.

- [2024 route poster — 12 original route records](data/sitme/baseline_routes_2024.csv)
- [Dated changes and official operational-model observations](data/sitme/route_change_log.csv)
- [15 route variants from the 2026-11-08 SITME API snapshot](data/sitme/official_schedule_sources.csv)
- [First and last departures by source, day type and departure location](data/sitme/first_last_departure_evidence.csv)
- [Operational status by route and 2026-11-08 API ID](data/sitme/route_operational_status_2026-11-08.csv)
- [Route-variant and identity issues](data/sitme/route_variant_review_2026-11-08.csv)
- [Provisional historical peak/off-peak clock-time model](data/sitme/provisional_peak_valley_windows.csv)

See the [central research register](docs/research-register.md) for source hierarchy, conflicts, unknowns, and outstanding verification. No GTFS generator or published feed exists yet.

## Stop data reconciliation (2026-11-09)

The [12-route SITME stop-layer audit](docs/sitme_stop_layer_audit_2026-11-08.md) checks the unmodified November 8 snapshot: 10,699 DETAIL points, 950 checkpoint/STATIONS rows and 526 matching `route_stations` candidate records. It records 424 additional checkpoint visits, 46 proximity-review pairs and no broken API ordering/linkage. **These are research-only candidate records, not an approved GTFS stop list.**

- [Per-route counts](data/sitme/stop_layer_summary_2026-11-08.csv)
- [Candidate stop records](data/sitme/stop_endpoint_candidates_2026-11-08.csv)
- [Additional checkpoint review](data/sitme/stop_additional_checkpoints_2026-11-08.csv)
- [Cross-route proximity review](data/sitme/stop_spatial_review_2026-11-08.csv)
- [Re-run audit script](scripts/audit_sitme_stop_layers.py)

**November 9 update:** Global LOCATION_ID reconciliation reduces the apparent 424 unmatched checkpoint occurrences to **five unique missing location IDs**; 419 occurrences are repeated uses of already known IDs. The live `site/by_client/195` response contains only 10 map-site objects, not a full stop list. See [reviewed reconciliation](docs/sitme_stop_site_reconciliation_2026-11-09.md) and [automated site comparison](docs/sitme_site_layer_comparison.md).

Next: validate the five truly missing location IDs, precise platform coordinates, P18/AN3 loop stop orders and RD27/RD15 Carrera 27 geometry before GTFS generation.
