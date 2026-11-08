#!/usr/bin/env python3
"""Read-only SITME route/station snapshot scraper and quality inventory."""
import argparse
import collections
import datetime as dt
import json
import pathlib
import urllib.error
import urllib.request

BASE = "https://apisitme.metrolinea.gov.co"
CLIENT = 195

def fetch(path, timeout=60):
    request = urllib.request.Request(
        BASE + path,
        headers={"Accept": "application/json", "User-Agent": "ColombiaTransit-GTFS-research/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)

def records(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        value = payload.get("data")
        if isinstance(value, list):
            return value
    raise ValueError("Unexpected SITME response: expected list or object with data list")

def catalog_comparison(routes, stations, route_catalog, station_catalog):
    def route_id(x):
        return str((x.get("ROUTE") or {}).get("ID") or x.get("ROUTE_ID") or x.get("ID") or "")
    def stop_id(x):
        nested = x.get("location_id") or {}
        if not isinstance(nested, dict):
            nested = {}
        return str(x.get("LOCATION_ID") or nested.get("ID") or x.get("ID") or "")
    dated_routes = {route_id(x) for x in routes}
    catalog_routes = {route_id(x) for x in route_catalog}
    dated_stops = {stop_id(x) for x in stations}
    catalog_stops = {stop_id(x) for x in station_catalog}
    for ids in (dated_routes, catalog_routes, dated_stops, catalog_stops):
        ids.discard("")
    return {
        "route_catalog_rows": len(route_catalog),
        "station_catalog_rows": len(station_catalog),
        "dated_route_ids_missing_in_catalog": sorted(dated_routes - catalog_routes),
        "catalog_route_ids_missing_in_dated_response": sorted(catalog_routes - dated_routes),
        "dated_station_ids_missing_in_catalog": sorted(dated_stops - catalog_stops),
        "catalog_station_ids_missing_in_dated_response": sorted(catalog_stops - dated_stops),
        "note": "Catalog presence does not prove active service. Check ID semantics.",
    }

def inventory(routes, stations, date):
    summary = {"date": date, "client_id": CLIENT, "route_count": len(routes),
               "station_rows": len(stations), "routes": [], "warnings": []}
    codes = collections.defaultdict(list)
    station_ids_by_route = collections.defaultdict(set)
    for row in stations:
        station_ids_by_route[str(row.get("ROUTE_ID"))].add(str(row.get("LOCATION_ID")))
    for item in routes:
        route = item.get("ROUTE") or {}
        rid = str(route.get("ID"))
        code = str(route.get("CODE") or "")
        codes[code].append(rid)
        detail = item.get("DETAIL") or []
        stops = item.get("STATIONS") or []
        detail_stops = [p for p in detail if p.get("IS_CHECKPOINT") == 1 and
                        (p.get("location_id") or {}).get("NAME") != "BREAKPOINT"]
        orders = [p.get("ORDER") for p in detail if isinstance(p.get("ORDER"), (int, float))]
        summary["routes"].append({
            "route_id": rid, "code": code, "name": route.get("NAME"),
            "company": item.get("COMPANY_NAME"),
            "detail_points": len(detail), "detail_checkpoints": len(detail_stops),
            "stations_in_detail_response": len(stops),
            "station_rows_in_stations_endpoint": sum(1 for x in stations if str(x.get("ROUTE_ID")) == rid),
            "distinct_station_ids_in_stations_endpoint": len(station_ids_by_route[rid]),
            "detail_orders_unique": len(orders) == len(set(orders)),
            "has_schedule": bool(item.get("ROUTE_SCHEDULLE")),
            "has_dispatches": bool(item.get("ROUTE_DISPATCHS")),
        })
    for code, ids in sorted(codes.items()):
        if len(ids) > 1:
            summary["warnings"].append({"type": "duplicate_route_code", "code": code, "route_ids": ids})
    for row in summary["routes"]:
        if not row["detail_orders_unique"]:
            summary["warnings"].append({"type": "duplicate_detail_order", "route_id": row["route_id"]})
        if row["stations_in_detail_response"] != row["station_rows_in_stations_endpoint"]:
            summary["warnings"].append({"type": "station_count_mismatch", "route_id": row["route_id"]})
    return summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="SITME service date YYYY-MM-DD")
    parser.add_argument("--output", default="data/sitme", help="Snapshot output directory")
    parser.add_argument("--routes-file", help="Use previously downloaded route-detail JSON instead of network")
    parser.add_argument("--stations-file", help="Use previously downloaded stations JSON instead of network")
    parser.add_argument("--route-catalog-file", help="Optional local /route JSON")
    parser.add_argument("--station-catalog-file", help="Optional local station catalog JSON")
    args = parser.parse_args()
    dt.date.fromisoformat(args.date)
    if bool(args.routes_file) != bool(args.stations_file):
        parser.error("Provide both --routes-file and --stations-file, or neither")
    if args.routes_file:
        routes_payload = json.loads(pathlib.Path(args.routes_file).read_text(encoding="utf-8"))
        stations_payload = json.loads(pathlib.Path(args.stations_file).read_text(encoding="utf-8"))
    else:
        routes_payload = fetch(f"/route/detail/{CLIENT}/{args.date}")
        stations_payload = fetch(f"/route/stations/{CLIENT}/{args.date}")
    route_catalog_payload = (json.loads(pathlib.Path(args.route_catalog_file).read_text(encoding="utf-8"))
                             if args.route_catalog_file else fetch("/route"))
    station_catalog_payload = (json.loads(pathlib.Path(args.station_catalog_file).read_text(encoding="utf-8"))
                               if args.station_catalog_file else fetch(f"/geo_zone/stations_by_client/{CLIENT}"))
    routes, stations = records(routes_payload), records(stations_payload)
    route_catalog, station_catalog = records(route_catalog_payload), records(station_catalog_payload)
    target = pathlib.Path(args.output) / args.date
    target.mkdir(parents=True, exist_ok=True)
    report = inventory(routes, stations, args.date)
    report["catalog_comparison"] = catalog_comparison(routes, stations, route_catalog, station_catalog)
    for name, data in (("route_detail.json", routes_payload), ("route_stations.json", stations_payload),
                       ("route_catalog.json", route_catalog_payload),
                       ("station_catalog.json", station_catalog_payload),
                       ("inventory.json", report)):
        (target / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"SITME {args.date}: {len(routes)} route variants; {len(stations)} station rows; "
          f"{len(report['warnings'])} quality warnings")
    print(f"Catalogs: {len(route_catalog)} route rows, {len(station_catalog)} station rows")
    for warning in report["warnings"]:
        print("WARNING:", json.dumps(warning, ensure_ascii=False))

if __name__ == "__main__":
    main()
