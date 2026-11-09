# SITME — OSM boarding-stop and platform positioning audit

Scope: the **528 research-only candidate stops** and **950 ordered stop visits** derived from the immutable **2026-11-08** SITME API snapshot. This is **not** a GTFS generator, nor a verified `stops.txt`.

## Reproducible pipeline

- Workflow: `.github/workflows/audit-sitme-osm-stop-positions.yml` (manual dispatch and automatic run when code changes).
- Script: `scripts/audit_sitme_osm_stop_positions.py` (standard-library Python; network calls only when `--fetch-osm` is selected).
- Inputs: `data/sitme/stop_candidates_reconciled_2026-11-09.csv`, `data/sitme/route_stop_visits_reconciled_2026-11-09.csv`, and archive from [Actions run 42471926616](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42471926616).
- Live OSM stops: Overpass `node/way/relation` features with `highway=bus_stop`, `public_transport=platform|stop_position|station` or `amenity=bus_station` in a computed regional bbox, provenance kept in the workflow artifact.
- Live OSM roads: `way[highway=trunk|primary|secondary|tertiary|residential|unclassified|living_street|service|busway]`, requested separately and **optional** for performance/resilience. The script indexes road segments by coarse spatial cells; comparisons are proximity diagnostics, not proof of platform side.
- **Required private Overpass endpoint:** GitHub organization secret `API_OVERPASS` supplies the full private HTTPS interpreter URL via workflow environment variable `OVERPASS_URL`. The script fails closed when `--fetch-osm` is requested without a valid HTTPS endpoint; **no public Overpass fallback**. The URL and its hostname are never printed in workflow/application logs.
- Browser-like headers (Chrome-style `User-Agent`, `Accept`, `Accept-Language`) accompany form-encoded Overpass QL POST requests. Optional Cloudflare Access organization secrets `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` are sent only when both exist. Optional backward-compatible secrets `OVERPASS_BEARER_TOKEN` and `OVERPASS_EXTRA_HEADERS_JSON` remain supported. Never persist the private URL, tokens or headers into outputs, code or logs.
- Grant this repository access to the organization secret `API_OVERPASS` in GitHub settings if the workflow reports that the secret is unavailable.

## Source hierarchy and caution

1. User-confirmed physically same stop: `150873→150965`, `150877→150969`, `163015→163024`. The 950 original source visits remain intact.
2. User-confirmed **distinct opposite-direction** stop pairs: `150798/150973` (San Carlos) and `164171/164933` (Carrera 4). Never merge them from short distances between SITME geofence polygon centers.
3. Exact OSM bus-stop/platform nodes are stronger *candidate coordinates* than generic `stop_position` points located on the carriageway, while OSM stations can represent a whole station complex. See [OSM GTFS mapping guidance](https://wiki.openstreetmap.org/wiki/GTFS). None certifies actual SITME boarding eligibility.
4. Direction diagnostics use the order of `DETAIL` points around each *individual* route visit. Left/right is relative to travel direction and sensitive to point geometry and dedicated/central platforms; it is not automatically a failing GTFS rule.
5. Names, distance and direction are matched conservatively; candidates with multiple canonical stops on the same OSM feature or an explicit direction conflict are flagged for review. **No additional stop identities are auto-merged.**
6. No A/B/C classification by itself sets `gtfs_stop_ready=true`. There is no published GTFS feed or automatic `stops.txt` export.

## Output files

The workflow uploads the `sitme-osm-stop-qa` artifact containing:

- `stop_osm_quality_2026-11-09.csv`: one row per 528 canonical candidates, nearest plausible OSM feature, confidence, comments and the original geofence center.
- `route_stop_direction_checks_2026-11-09.csv`: one row per 950 SITME visit, proposed OSM feature, distance to route point, estimated left/right of travel, nearby OSM road where available.
- `stop_manual_review_queue_2026-11-09.csv`: higher-priority cases and ambiguous matches.
- `sitme_stop_review_map.html`: filterable Leaflet map for A/B/C classes and route line overlays; requires internet access to load Leaflet and OSM basemap, but data is embedded and can still be inspected in the CSVs.
- `osm_stops_raw.json` and `osm_roads_raw.json` (if fetched), `summary.json`, `stop_osm_audit_report.md`.

On successful OSM retrieval, the workflow copies summary/CSV/Markdown results to `data/sitme/` and `docs/sitme_stop_osm_audit_latest.md`; the larger HTML and raw datasets stay in the GitHub Actions artifact. All output counts and timestamps must be read from the actual workflow artifacts, **never inferred from a synthetic test run**.

## Categories

| Code | Interpretation | GTFS approval |
| --- | --- | --- |
| A_strong_candidate | Mapped OSM platform/bus stop within 25m of source research centroid, normalized name similarity ≥0.80, no identified direction-side contradiction or duplicate conflict | **No**; high-quality candidate only |
| B_probable | Less conclusive nearby OSM evidence (up to 65m) | **No** |
| C_manual_review | Missing/contradictory match, ambiguous direction, or poor similarity/position | **No** |

The thresholds are review triage rules, not authoritative boarding-point tolerances. A missed OSM match is **not** evidence that a SITME stop has ceased service. API station polygons can differ substantially from physical platform points. The route RD27/RD15 outbound corridor mismatch (Carrera 27 vs 33/32) remains unresolved and must be separately reviewed before spatial validation.
