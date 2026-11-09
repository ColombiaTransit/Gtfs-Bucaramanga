# SITME public map sites versus route checkpoint locations

Retrieved: 2026-11-09T09:44:42.234127+00:00

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

## Interpretation

Only explicit LOCATION_ID matches or unique exact-name-and-nearby-coordinate matches are linked. Matches remain research associations, not confirmed GTFS boarding platforms. SITE.ID alone is never used as a route LOCATION_ID. Absence from the site catalog does not prove a route STATIONS entry is unusable. Spatial-only and ambiguous cases require human review.

Source: public /site/by_client/195 response compared with immutable 2026-11-08 route snapshot.
