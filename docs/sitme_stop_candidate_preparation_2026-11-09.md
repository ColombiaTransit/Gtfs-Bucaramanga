# SITME — preliminary stop identities and route passages (2026-11-09)

Source: immutable 2026-11-08 SITME route detail snapshot; manual user-confirmed mapping from `stop_identity_decisions_2026-11-09.csv`.

- **950** original checkpoint passages across **12** routes, **531** original `LOCATION_ID`s.
- **Three** user-confirmed aliases: `150873 → 150965`, `150877 → 150969`, and `163015 → 163024`.
- **Two** pairs explicitly kept separate: San Carlos S-n `150798` vs N-s `150973`, Carrera 4 Calle 0 S-n `164171` vs N-s `164933`. Other potentially duplicated same-direction sites remain unreviewed.
- **528** candidate canonical stop identities after exactly these three aliases. This is *not* a proven final GTFS boarding-stop count.
- **950** ordered route visits remain, including repeated visits to the same physical stop and historic `LOCATION_ID` references. P16N La Vega retains two visits at `ORDER 87` and `ORDER 969`.
- Original `STATIONS` array records and route `ORDER` values are never overwritten.
- Candidate coordinates are simple **polygon centroids** from the API, not exact platform locations; no record has `gtfs_stop_ready=true`.
- **Crucial:** a polygon-centroid distance of approximately 9 m between `164171` and `164933` does not establish a 9 m physical boarding-stop distance. User confirms they are **different** locations and cannot be merged.
- The alias mapping changes identity only. It does not assert boarding eligibility for all 950 records, GTFS `stop_times`, service calendars, trip directions, travel times or headways.

Generated files: `stop_candidates_reconciled_2026-11-09.csv` and `route_stop_visits_reconciled_2026-11-09.csv` (research-only CSVs).
