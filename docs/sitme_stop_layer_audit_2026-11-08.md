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


### UI category hypothesis and checkpoint-field verification — 2026-11-09

**Trigger:** User provided a mobile webpage screenshot showing the map layer menu **"Puntos de Recarga"**, **"Estaciones y Paraderos"**, **"Estaciones más cercanas"**, and **"Sitios de Interés"**, with a separate "Seleccione Una Ruta" control. An identical *menu vocabulary* is discoverable on the METSIU/MET GROUP web template at https://juarezbus.chihuahua.gob.mx/rutas . This identifies a likely common UI template **but not the source URL of the user's screenshot** and not proof that the Chihuahua implementation uses Bucaramanga's datasets. **No actual JavaScript bundle from the user's photographed page was supplied or inspected**; UI control handlers, backend requests and filtering rules therefore remain unknown.

**Direct structural checks from our archived Bucaramanga SITME JSON (2026-11-08):**
- In the 12 selected routes, `DETAIL` has **10,699 rows**, of which **950** have `IS_CHECKPOINT=1` and match the embedded `STATIONS` array. The independent `route_stations` response selects only **526** of the 950.
- **All 950 checkpoint records**, including both the **526 endpoint-selected** and **424 endpoint-omitted** entries, have `location_id.CODE=null`; thus that field **does not explain the exclusion**. By contrast, geometry-only rows typically have `location_id.CODE="BREAK"`.
- `location_id.COORDINATES` frequently describes polygons (not verified individual boarding-point coordinates) in **both** sets: **254/526** selected and **300/424** omitted have **37 coordinate vertices**. Both groups have identically shaped underlying checkpoint records, so neither geometry shape nor the checkpoint flag separates the groups.
- The omitted set includes explicitly transit-related names: P14 **"Parada MasxMenos"**, P16S **"Paradero Campo Alegre S-n"** and **"Parada ICP S-n"**, P18 **"Estacion de transferencia Provenza Oriental"**, AN3 **"Portal Norte"** (twice). Those may be genuine public access/transfer sites. **Do not treat omitted checkpoints as non-passenger geometry-only control points**.
- Conversely, many selected records include `Inicio`/`Fin` names. **Do not claim every selected row is a confirmed boarding location** without validation.
- UI category labels **are not** supported evidence that these are implemented as distinct backend `station_type` values; the "nearest stations" layer could be a spatial query over the same station inventory rather than a new stop category.

**Research rule:** Preserve the 950 checkpoint source occurrences and the 526 endpoint selections, but avoid making either subset the final GTFS boarding-stop list. Keep `BREAK` route geometry separate. Obtain **the exact route page URL or its HTML/JS bundle** and inspect (1) the click handler for "Estaciones y Paraderos"; (2) request URL(s) and parameters, including route ID and client ID; (3) response schema and status/type flags; (4) how markers and stop-list rows are filtered; and (5) whether route-specific `STATIONS`, global location markers and `route_stations` are different services. Correlate backend IDs with checkpoint `LOCATION_ID`, `ORDER` and `IS_CHECKPOINT` to classify genuine boarding stops. **Do not claim JavaScript source analysis is complete yet.**
