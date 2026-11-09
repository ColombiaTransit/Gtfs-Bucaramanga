# SITME — map-site catalog and route station reconciliation (2026-11-09)

## Provenance

- Live public endpoint: `GET https://apisitme.metrolinea.gov.co/site/by_client/195`, fetched successfully by [GitHub Actions](../.github/workflows/audit-sitme-site-layer.yml) on **2026-11-09**.
- Route evidence: immutable [2026-11-08 API snapshot](https://github.com/ColombiaTransit/Gtfs-Bucaramanga/actions/runs/42471926616/artifacts/13613444443), with `route_detail.json` and `route_stations.json`.
- [Machine-readable site associations](../data/sitme/site_layer_matches.csv), [per-location crosswalk](../data/sitme/route_location_site_crosswalk.csv), and [automatic summary](sitme_site_layer_comparison.md).
- Geometric distances below use **derived checkpoint polygon centroids** (not GTFS boarding-point positions). Site map markers and route polygons have different spatial semantics.

## Main correction: 424 excluded checkpoint occurrences ≠ 424 omitted stops

The 12 selected routes contain **950 route STATIONS/checkpoint occurrences but only 531 distinct LOCATION_ID values**. Thus **419 are revisits of existing LOCATION_IDs**, across routes and sometimes within a loop.

The `/route/stations/195/2026-11-08` endpoint contains **526 records and exactly 526 distinct LOCATION_ID values**, with no duplication. Every endpoint LOCATION_ID is present among the 531 distinct IDs in the 12 route STATIONS arrays. Therefore **only 5 distinct IDs are truly missing from the endpoint**; 419 other occurrence differences are explained by LOCATION_ID reuse.

The earlier per-route audit's **424 endpoint-omitted checkpoint occurrences** and **370 distinct locations missing per route** are mathematically correct *in their per-route counting scope*, but **do not represent 424 or 370 globally missing boarding locations**. The per-route approach conflated shared stops across routes with absent stations. This global identity reconciliation supersedes that interpretation.

### Five missing distinct route LOCATION_IDs (focus list)

| LOCATION_ID | Display name | Route(s) and order | Checkpoint occurrences | Notes |
| --- | --- | --- | ---: | --- |
| `150798` | San Carlos S-n | P8, order 322 | 1 | `IS_CHECKPOINT=1`; missing from `/route/stations` |
| `150873` | Mac Pollo N-s | P8, order 1439 | 1 | `IS_CHECKPOINT=1`; missing from `/route/stations` |
| `150877` | Pretecor N-s | P16S 732; P16N 847 | 2 | One shared LOCATION_ID on two routes |
| `163015` | Parada la VEGA S-n. | P16N, order 87 | 1 | Explicit 'Parada' name; geometry has 3 vertices |
| `164171` | Carrera 4 Calle 0 S-n. | P16S, order 44 | 1 | `IS_CHECKPOINT=1`; geometry has 5 vertices |

All five have `location_id.CODE=null`, not `BREAK`. **Do not automatically exclude them from GTFS**: investigate why the `route/stations` response omitted them, verify operation/boarding usability and direction, and retain them in the canonical route checkpoint audit.

## `/site/by_client/195` is a limited POI / station-display layer

The live response returned **10 site objects**, with `geozoneType.NAME`:

| Type | Count |
| --- | ---: |
| Estación | 6 |
| Parque | 2 |
| Dependencias de gobierno | 2 |
| **Total** | **10** |

The separate `geozoneCategory.NAME` is **Rutas** for the six stations and **Sitios de interés** for the four non-station objects. None of these uses the route `LOCATION_ID` as an explicit foreign key in the returned matching CSV. The site object's own `ID` is **not** a route LOCATION_ID. The website menu's `Estaciones y Paraderos` filter applies to the site `geozoneType`, not to all 531 route locations.

The automatic matching method produced **one exact normalized name within 100 m** (Estación UIS ↔ `150943`, 27.2 m), **four spatial-only candidates within 30 m** requiring identity review, and five not automatically linked (including Portal Norte at 90.4 m). That is **not** evidence of 530 invalid route stops: most route stops are simply not represented in this 10-object global map-site collection.

### Six station markers: nearby checkpoint candidates, not approved matches

| Public site marker | Nearby route LOCATION_ID(s) | Approx. distance | Interpretation |
| --- | --- | --- | --- |
| Estación Temprana | `150880` Portal de Piedecuesta N-s | 18.3 m | Different names; possible vicinity/alias only, needs verification |
| Estación San Mateo | `150948` Estación San Mateo Ns; `151003` S-n; `151156` N-s | 2.3 / 12.9 / 21.8 m | **Multiple direction/platform candidates**, not a single stop identity |
| Estación Portal Norte | `151273` Portal Norte | 90.4 m | Similar name; site marker and boarding location are spatially offset |
| Estación Provenza Oriental | `151149` and `150817` Provenza Oriental | 21.1 / 23.2 m | Multiple route-specific checkpoint IDs for nearby boarding area |
| Estación Provenza Occ | `150863` Provenza Occidental | 24.1 m | Plausible site-to-station reference; no explicit same-ID link |
| Estación UIS | `150839` Transferencia Parque Estación UIS; `150943` ESTACION UIS | 14.3 / 27.2 m | More than one candidate; exact-name match alone is insufficient |

Nearby names and distances support **candidate associations** only. They do not establish that all corresponding checkpoint locations are boarding platforms or that a stop's GTFS coordinate should equal the public-site marker. A single station site could represent a larger station complex served by several direction-specific GTFS stops.

## Decisions / next work

1. **Close** the question whether 424 additional checkpoint records are 424 missing stops. They are not; there are **only 5 globally missing LOCATION_IDs** from the 526-row endpoint.
2. **Close** the hypothesis that `/site/by_client/195` represents a complete passenger-stop list. It is a **10-object global map display/POI catalog**, not suitable as `stops.txt`.
3. Preserve the full **950 ordered checkpoint occurrences** to reconstruct route-specific stop sequences and retain **531 unique LOCATION_IDs** as the deduplication-key candidate pool. A candidate must still be validated before it becomes a GTFS boarding stop.
4. **Investigate only the 5 omitted unique IDs** as a focused server-response anomaly. Keep station complexes/platform direction distinctions and do not conflate first polygon vertices with actual boarding coordinates.
5. If additional data is needed, inspect the distinct `/geo_zone/stations_by_client/195` and `/site/stations-plan/by_client/195` endpoints present in the supplied JavaScript. Their semantics and availability have **not** been verified here.

**Status:** direct API comparison complete; five-LOCATION_ID exception list ready; GTFS `stops.txt` not yet generated.

### Physical-stop ID decision — user verification (2026-11-09)

The 5 omitted source LOCATION_ID values were manually reconciled with candidate nearby locations by the user. **Do not use distances between derived polygon centroids to merge two stops or infer that they are on the same roadside.**

| Omitted LOCATION_ID | Compared LOCATION_ID | Verified relationship | Preparation decision |
|---|---|---|---|
| 150798 San Carlos S-n | 150973 San Carlos N-s | **Different direction; opposite sides of road** | Keep separate; no merge |
| 150873 Mac Pollo N-s | 150965 Mac Pollo N-s | **Same physical stop** | Canonical ID 150965 |
| 150877 Pretecor N-s | 150969 Pretecor N-s | **Same physical stop** | Canonical ID 150969 |
| 163015 Parada la VEGA S-n | 163024 Parada la VEGA S-n | **Same physical stop** | Canonical ID 163024; retain both P16N route visits (orders 87 and 969) |
| 164171 Carrera 4 Calle 0 S-n | 164933 Carrera 4 No. 0-30 N-s | **Different physical stops; user reports physical separation too great for merger, with at least a different road side** | Keep separate; no merge |

**Important qualification:** Distances such as ~9 m between 164171 and 164933 reported by the earlier script are distances between *derived coordinate centers of polygons*. They are **not verified stop-to-stop boarding-point distances** and must not override the user's direct assessment. A further `150914 San Carlos S-n` is present in the source; do not automatically equate it to 150798, which has a different source ID, until reviewed.

The five source IDs must remain in the unchanged 950 route-STATIONS/checkpoint visits; the three confirmed same-stop relationships are candidate GTFS stop identity *aliases*, not permission to delete route visits. Applying only those three identities to the 531 original unique LOCATION_IDs produces **528 tentative candidate stops**, all requiring precise boarding-coordinate and usability verification; it does **not** establish a final GTFS stops.txt count.

**Machine-readable decision file:** [stop_identity_decisions_2026-11-09.csv](../data/sitme/stop_identity_decisions_2026-11-09.csv). The 2026-11-08 immutable API snapshot and earlier evidence remain intact.
