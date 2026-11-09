# SITME stop layer audit — 2026-11-08

Snapshot source: ColombiaTransit/Gtfs-Bucaramanga Actions run **42471926616**, artifact **13613444443** (`sitme-route-snapshot`). 12 active-inventory complementary routes (excluding historical PTB and two PTN entries). Generated via `scripts/audit_sitme_stop_layers.py` using only standard-library Python.

## Verified cross-layer results

- **10,699** DETAIL geometry rows across 12 routes; **950** checkpoint rows, **950** matching embedded STATIONS rows, **526** independently returned `route_stations` rows.
- Every embedded STATIONS row corresponds by original record ID, ORDER and LOCATION_ID to a DETAIL checkpoint; all 526 endpoint records also match this way (no endpoint-only orphan records).
- The **424** DETAIL checkpoints absent from the endpoint comprise **370** different locations excluded from the endpoint and **54** extra visits to locations in DETAIL (including revisits to locations excluded by the endpoint). The reason column in the extra-checkpoint CSV identifies whether the location exists in the endpoint; it does not automatically establish the type of stop.
- Every route's DETAIL order is contiguous, every NEXT_LOCATION_ID links to the next row, and coordinate data is present for endpoint candidates. This proves **internal sequence consistency**, not correct roads or active passenger stops.
- The endpoint has **526** per-route location references with **526** distinct LOCATION_IDs, even though spatially similar stops exist across routes. **Do not treat each ID as a validated distinct physical platform.**
- All **526** endpoint candidate locations have multipoint/polygon coordinates. Derived research centroids are for collision detection only, **not directly approved GTFS stop_lat/stop_lon**.
- **46** cross-route candidate pairs have centroids within 30 meters; only **6** have identical punctuation/accent-normalized names. These are review pairs, **not confirmed duplicates**. Inbound/outbound platforms must remain separate if appropriate.
- `route_stations.json` contains 529 total rows across all 15 API routes; **3** are PTB/PTN archival entries, excluded from the provisional 12.

## Safe automatic normalization now

1. Sort each route's DETAIL and endpoint-selected rows numerically by ORDER (the raw endpoint list is not consistently ordered).
2. Match records between layers by DETAIL row ID plus ORDER and LOCATION_ID, **without inventing stops**.
3. Use endpoint rows as the preliminary *candidate selection*, retaining raw names and IDs and separately recording normalized comparison labels.
4. Compute optional *research-only* centroids for multi-vertex location geometry, retaining an explicit unverified-coordinate status.
5. Keep each additional checkpoint separately for manual/API-semantics review rather than treating every checkpoint as a passenger stop.

## Remaining review priorities

- **P14, P16S, P16N, P1:** large numbers of distinct DETAIL checkpoints excluded from the station endpoint. Confirm whether the endpoint is an intentionally filtered passenger-stop set, whether those locations are valid stops, and whether revisions/route variants account for the difference.
- **P18 and AN3:** loop repeats and terminal checkpoints cannot be naively converted to a stop_times sequence; check outbound/inbound pattern and source representation. **RD27/RD15:** API 3350 includes the complete loop, but the Carrera 33/32 vs official Carrera 27 outbound geometry conflict is unresolved.
- **P19:** six extra checkpoint occurrences but no additional unique LOCATION_IDs beyond the endpoint; this suggests repetition rather than a missing-stop inventory for this route.
- Resolve the **46** proximity pairs before stop deduplication. Some similar names or distances describe opposite platforms, not duplicates.
- Validate the actual point for each boarding platform before generating GTFS `stops.txt`; validate service operation, direction-specific stop order and time data before `stop_times.txt`.

## Output files

- `stop_layer_summary_2026-11-08.csv` — per-route reconciliation and topology checks
- `stop_endpoint_candidates_2026-11-08.csv` — all candidate selections and research-only approximate centroids
- `stop_additional_checkpoints_2026-11-08.csv` — full list of excluded checkpoint occurrences and review categories
- `stop_spatial_review_2026-11-08.csv` — 30 m proximity candidate pairs, never automatic merges
- `stop_technical_issues_2026-11-08.csv` — direct schema/topology mismatches if discovered

**Status:** research audit complete. No source snapshot has been changed, and no GTFS generator or feed has been created from these unverified coordinates.