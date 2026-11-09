# SITME stop-location evidence audit (research; not published GTFS)

Audit timestamp UTC: 2026-11-09T17:23:49+00:00

- Source candidates: **528**, route visits: **950**.
- OSM transit features: **156**, OSM road ways: **11495**.
- Classes: **{"C_manual_review": 503, "B_probable": 23, "A_strong_candidate": 2}**; manual queue: **503**.
- **GTFS-ready stops: 0**. Even strong OSM matches remain candidate evidence, not verified boarding-point coordinates.
- The 950 route visits are retained in source order; no new merges are made.
- Confirmed distinct directional pairs 150798/150973 and 164171/164933 are never auto-merged.
- Exact boarding side and physical point cannot be established from polygon-centroid distances alone.
- Direction-side diagnostics use the SITME DETAIL traversal near each specific visit; they are signals, not proofs.
- Per-stop CSV and interactive map list nearest OSM public-transport features; blue point is the OSM position, coloured point is the SITME polygon centroid.

## Data acquisition / limitations

- OSM stops fetched live from configured Overpass API.
- Road geometry downloaded for direction-side diagnostics; never used to prove boarding.

## Outputs

- `stop_osm_quality_2026-11-09.csv` — all 528 stops, candidate match, quality category and uncertainty.
- `route_stop_direction_checks_2026-11-09.csv` — all 950 visits with route-side diagnostics.
- `stop_manual_review_queue_2026-11-09.csv` — priority review candidates.
- `sitme_stop_review_map.html` — interactive inspection map; external Leaflet and OSM tiles require internet.
- `summary.json` — source counts, timestamp, completeness.

## Next work

Review C cases and directional conflicts, then verify actual platform positions from authoritative geometry or operator evidence. Only after this review can `stops.txt` be prepared.
