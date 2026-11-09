# SITME-only GTFS foundation — decision and build

**Decision: 2026-11-09.** The SITME public API is the primary and sufficient source for the current research-stage route geometry, stop inventory, stop order and source GPS. **No OpenStreetMap / Overpass checks are needed or invoked** by the GTFS foundation pipeline. The previous OSM audit is a historical exploratory report only and must not block generation or decide which SITME stops are included. The OSM audit workflow is *not* part of this build.

## Input and identity decisions

- Source: archived SITME `/route/detail/195/2026-11-08` JSON in immutable snapshot. The first successful foundation workflow stores an exact ZIP of this snapshot at `data/sitme/snapshots/sitme-route-snapshot-2026-11-08.zip` so the build remains reproducible after Actions artifacts expire.
- Scope: 12 source routes (`3341,3342,3345,3346,3350–3357`); do not reactivate 2026-ended PTB/PTN based on their presence in old API data.
- The **950 original `STATIONS` occurrences** are preserved in the original per-route `ORDER`; a repeated visit may have the same stop ID as an earlier visit.
- Of **531 unique source `LOCATION_ID`s**, three user-confirmed duplicate identities map as `150873→150965` (Mac Pollo), `150877→150969` (Pretecor), and `163015→163024` (La Vega), yielding **528 canonical stops**. Preserve all 531 original IDs in the crosswalk.
- Two pairs are user-confirmed physically separate: San Carlos `150798/150973` and Carrera 4 `164171/164933`. Do not merge by name or coordinates. Do not change any other identity without evidence.

## GPS and geometry

- Stop `stop_lat` / `stop_lon` use the **first GPS vertex** from the canonical `location_id.COORDINATES` array, exactly as the supplied SITME web JavaScript marks route stations. This is an official **SITME-supplied coordinate**, but it may be on the boundary of a geofence rather than the exact curb-side boarding position. The prior automatically derived polygon midpoint is not used. Coordinates and original record IDs remain traceable to the archived API.
- Each `shapes.txt` row comes directly from `DETAIL` `ORDER`, taking the first GPS vertex of that location. The builder computes cumulative geodesic kilometres for optional `shape_dist_traveled`; this is not a travel-time estimate and is not GraphHopper geometry.
- The combined `RD27/RD15` API route ID `3350` remains **one combined geometry**: don't invent separate directional trip patterns. Its reported outbound Carrera 33/32 vs historical official Carrera 27 discrepancy remains visible and requires review before publication.
- AN3/P18 variants remain those actually represented in the snapshot; no direction/variant splitting is inferred.

## Files produced

Run `.github/workflows/build-sitme-gtfs-base.yml` or:

```sh
python3 scripts/build_sitme_gtfs_base.py \
  --snapshot data/sitme/snapshots/sitme-route-snapshot-2026-11-08.zip \
  --candidates data/sitme/stop_candidates_reconciled_2026-11-09.csv \
  --visits data/sitme/route_stop_visits_reconciled_2026-11-09.csv \
  --output sitme-gtfs-base
```

- `gtfs_base/agency.txt` — managing body (one SITME ID; not a claim that it operates every bus).
- `gtfs_base/routes.txt` — 12 route definitions.
- `gtfs_base/stops.txt` — 528 canonical, named, SITME-sourced GPS positions.
- `gtfs_base/shapes.txt` — 10,699 ordered SITME GPS geometry points.
- `source_audit/route_stop_sequences.csv` — 950 route-specific stop visits, with `shape_pt_sequence` linking to `DETAIL` and source IDs. **This is not `stop_times.txt`.**
- `source_audit/location_id_to_gtfs_stop_id.csv` — auditable mapping of original to canonical IDs.
- `source_audit/build_summary.json` — counts, sources and unresolved publication matters.

## Remaining steps for complete GTFS

This is **not yet a valid complete GTFS Schedule feed**. We still need `trips.txt`, `stop_times.txt`, service calendars (`calendar.txt` or `calendar_dates.txt`) and justified route-specific journey times and departure windows. No guessed first/last trips or frequencies are silently exported. Route variant and RD27 alignment issues need route-specific treatment. The generator does **not** require future OSM validation to proceed.