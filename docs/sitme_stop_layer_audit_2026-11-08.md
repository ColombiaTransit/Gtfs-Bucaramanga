# SITME stop layer audit — 2026-11-08

> **Correction, 2026-11-09:** 950 route checkpoint visits represent 531 unique LOCATION_IDs. The endpoint contains 526 globally unique IDs; **only five unique IDs** are actually absent. The older 424/370 omission figures describe per-route occurrence differences, not globally missing passenger stops. [Reviewed reconciliation](sitme_stop_site_reconciliation_2026-11-09.md).

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

**Trigger:** User provided a mobile webpage screenshot showing the map layer menu **"Puntos de Recarga"**, **"Estaciones y Paraderos"**, **"Estaciones más cercanas"**, and **"Sitios de Interés"**, with a separate "Seleccione Una Ruta" control. An identical *menu vocabulary* is discoverable on the METSIU/MET GROUP web template at https://juarezbus.chihuahua.gob.mx/rutas . This identifies a likely common UI template **but not the source URL of the user's screenshot** and not proof that the Chihuahua implementation uses Bucaramanga's datasets. **Correction (2026-11-09):** Previously uploaded JavaScript bundles from the exact SITME site were later recovered and inspected; see the verified analysis below. The original sentence was an outdated retrieval error.

**Direct structural checks from our archived Bucaramanga SITME JSON (2026-11-08):**
- In the 12 selected routes, `DETAIL` has **10,699 rows**, of which **950** have `IS_CHECKPOINT=1` and match the embedded `STATIONS` array. The independent `route_stations` response selects only **526** of the 950.
- **All 950 checkpoint records**, including both the **526 endpoint-selected** and **424 endpoint-omitted** entries, have `location_id.CODE=null`; thus that field **does not explain the exclusion**. By contrast, geometry-only rows typically have `location_id.CODE="BREAK"`.
- `location_id.COORDINATES` frequently describes polygons (not verified individual boarding-point coordinates) in **both** sets: **254/526** selected and **300/424** omitted have **37 coordinate vertices**. Both groups have identically shaped underlying checkpoint records, so neither geometry shape nor the checkpoint flag separates the groups.
- The omitted set includes explicitly transit-related names: P14 **"Parada MasxMenos"**, P16S **"Paradero Campo Alegre S-n"** and **"Parada ICP S-n"**, P18 **"Estacion de transferencia Provenza Oriental"**, AN3 **"Portal Norte"** (twice). Those may be genuine public access/transfer sites. **Do not treat omitted checkpoints as non-passenger geometry-only control points**.
- Conversely, many selected records include `Inicio`/`Fin` names. **Do not claim every selected row is a confirmed boarding location** without validation.
- UI category labels **are not** supported evidence that these are implemented as distinct backend `station_type` values; the "nearest stations" layer could be a spatial query over the same station inventory rather than a new stop category.

**Research rule:** Preserve the 950 checkpoint source occurrences and the 526 endpoint selections, but avoid making either subset the final GTFS boarding-stop list. Keep `BREAK` route geometry separate. The exact route page and previously supplied JavaScript have now been identified and inspected. See the resolved frontend analysis below. For remaining backend validation, inspect (1) the click handler for "Estaciones y Paraderos"; (2) request URL(s) and parameters, including route ID and client ID; (3) response schema and status/type flags; (4) how markers and stop-list rows are filtered; and (5) whether route-specific `STATIONS`, global location markers and `route_stations` are different services. Correlate backend IDs with checkpoint `LOCATION_ID`, `ORDER` and `IS_CHECKPOINT` to classify genuine boarding stops. **Frontend JS menu and route rendering are now verified; undocumented backend filtering remains open.**

### Actual SITME `/rutas` JavaScript analysis — 2026-11-09 (verified from previously supplied bundles)

**Source:** The user previously supplied the 2026-11-08 JavaScript build of `https://sitme.metrolinea.gov.co/rutas`. Relevant existing original files were retrieved from the user's Library, not fetched from a different city's template:
- `chunk-TRMRAHU2.js` (localization labels `MAP_OPTIONS.STATIONS_AND_STOPS`, `NEAREST_STATIONS`, `POINTS_OF_RECHARGE`, `POINTS_OF_INTEREST`, API config `https://apisitme.metrolinea.gov.co`, `clientId=195`).
- `chunk-7TJ6VLLM.js` (Angular user-service and route-planner station selector).
- `chunk-UBSKBW72.js` (Angular main map/menu handlers, route map draw functions).

**Verified HTTP methods and purpose (all from `chunk-7TJ6VLLM.js`):**
| Client method | Request path | Use confirmed in client |
|---|---|---|
| `getRoutesDetail(clientId, date)` | `GET /route/detail/{clientId}/{date}` | Gets `DETAIL` and `STATIONS` for selected-route rendering |
| `getStationsRoutes(clientId, date)` | `GET /route/stations/{clientId}/{date}` | Supplies route-planner `getStations()` selector; `getStations()` collapses duplicate `location_id.NAME` values |
| `getSitesInterest(clientId)` | `GET /site/by_client/{clientId}` | Supplies **map-layer points of interest**, separately from route checkpoints |
| `getAllStationsByClient(clientId)` | `GET /geo_zone/stations_by_client/{clientId}` | Defined in API service; do not assume the shown menu calls it |
| `getStationsPlanYourTrip(clientId)` | `GET /site/stations-plan/by_client/{clientId}` | Defined in API service; not established as the shown layer's source |

**Verified map option handlers (all from `chunk-UBSKBW72.js`):**
- `stationsAndStops()`: calls **`getSitesInterest(clientId)`** then only selects `r.geozoneType.NAME=="Terminal de transporte" || r.geozoneType.NAME=="Estación"`. Despite the Spanish label **"Estaciones y Paraderos"**, there is **no explicit `"Paradero"` type in this filter**. Whether named paraderos are classified as "Estación" in API data requires checking the response.
- `getNearestStations()`: same **`getSitesInterest`** response, filters `geozoneType.NAME=="Estación"`, then divides sites by **5 km** great-circle proximity from user location.
- `chargingPoints()`: same **`getSitesInterest`** response, filters `geozoneType.NAME=="Centro Comercial"`. It is not demonstrated to filter a dedicated top-up terminal type.
- `pointsInterest()`: same **`getSitesInterest`**, filters `geozoneCategory.NAME=="Sitios de interés"`. It is distinct from stop records.

**Critical route-marker finding:** `selectRoute()` calls `getMarkersRoute()`, which iterates `for (let i of e.STATIONS ?? [])` using **every embedded route `STATIONS` entry**, with **no explicit extra stop-category filter** in this draw method. Markers use `i.location_id.COORDINATES[0]` and `i.location_id.NAME`, with a `bus-stop.png` icon and sequential marker label. `getPolylines()` separately uses every `DETAIL[].location_id.COORDINATES`. The first coordinate of a polygon used by the website is **not proof of a correct GTFS stop point**.

**Implications for the existing 2026-11-08 12-route audit:**
1. The **950 embedded `STATIONS` checkpoint occurrences** are the candidate stop sequence that the official UI actually paints when a route is selected. The **526 records** from `/route/stations` are a **different client-facing API selection**, and its data is used by the trip planner, **not** as the sole route-map marker inventory. Preserve all 950 in the audit, including repeat passages; keep each original `LOCATION_ID`/`ORDER`.
2. The map's **global category layer** is `/site/by_client/195`, not `/route/stations/195/{date}`, so **it does not explain or validate the server-side 950-vs-526 discrepancy**. Avoid merging all three endpoint families into one presumed station-type enum.
3. The route map drawing code does not guarantee all 950 are *operable boarding/alighting stops*; for instance, route start/end markers and intermediate checkpoints still need GTFS stop usability checks, and the API may encode platforms or transfer visits differently. Do not publish them blindly in `stops.txt`.
4. **Remaining technical unknown:** server-side selection rules for `/route/stations`, `/site/by_client` data content and site-to-`LOCATION_ID` identity relationships. The browser source code establishes what the **client** requests and displays, not undocumented backend business rules.

**Research status:** The *frontend JavaScript analysis and meaning of the menu filters are now resolved*. The **server-side omission of 424 checkpoint occurrences** remains an open data-model question. The next targeted task is reconcile `STATIONS` by `LOCATION_ID` and route `ORDER` against `/site/by_client/195` and `/route/stations/195/{date}`; classify route checkpoint versus actual GTFS boarding point by evidence, not by which subset an API returned.
