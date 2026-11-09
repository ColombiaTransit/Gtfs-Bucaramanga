# SITME public map sites versus route checkpoint locations

Retrieved: 2026-11-09T09:48:09.312539+00:00

- Map site records: **10**
- Unique route LOCATION_IDs: **531**
- Route checkpoint occurrences: **950**
- Route locations with any site match: **1**
- Route locations without site match: **530**

## Map site types

- Dependencias de gobierno: 2
- Estación: 6
- Parque: 2

## Match classifications

- name_within_100m: 1
- spatial_only_review: 4
- unmatched: 5

## Global route LOCATION_ID reconciliation

- Route STATIONS: **950** visits using **531** unique LOCATION_IDs.
- Repeated checkpoint visits across these IDs: **419**.
- /route/stations: **526** unique LOCATION_IDs, one row each.
- Truly missing from /route/stations: **5** unique LOCATION_IDs.

### Five location IDs for focused research

- 150798 — San Carlos S-n (P8; 1 visit(s))
- 150873 — Mac Pollo N-s (P8; 1 visit(s))
- 150877 — Pretecor N-s (P16N;P16S; 2 visit(s))
- 163015 — Parada la VEGA S-n. (P16N; 1 visit(s))
- 164171 — Carrera 4 Calle 0 S-n. (P16S; 1 visit(s))

## Interpretation

Only explicit LOCATION_ID matches or unique exact-name-and-nearby-coordinate matches are linked. Matches remain research associations, not confirmed GTFS boarding platforms. SITE.ID alone is never used as a route LOCATION_ID. Absence from the site catalog does not prove a route STATIONS entry is unusable. Spatial-only and ambiguous cases require human review.

Source: public /site/by_client/195 response compared with immutable 2026-11-08 route snapshot.
