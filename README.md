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
