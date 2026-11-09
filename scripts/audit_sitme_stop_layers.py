#!/usr/bin/env python3
"""Rebuild SITME API stop-layer audit reports from the immutable Actions snapshot.

Usage:
  python scripts/audit_sitme_stop_layers.py --snapshot sitme-route-snapshot.zip --output out/
  python scripts/audit_sitme_stop_layers.py --snapshot 2026-11-08/ --output out/

Research only: derived centroids are NOT verified GTFS stop coordinates.
"""
import argparse
import csv
import io
import json
import math
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROUTES = {"3341": "P16S", "3342": "P16N", "3345": "P8", "3346": "P14",
          "3350": "RD27/RD15", "3351": "P1", "3352": "P2", "3353": "P3",
          "3354": "P10", "3355": "P18", "3356": "AN3", "3357": "P19"}

def load(snapshot, filename):
    snapshot = Path(snapshot)
    if snapshot.suffix.lower() == ".zip" and snapshot.is_file():
        with zipfile.ZipFile(snapshot) as archive:
            matches = [n for n in archive.namelist() if n == filename or n.endswith("/" + filename)]
            if len(matches) != 1:
                raise ValueError("Ambiguous archive file: " + filename)
            with archive.open(matches[0]) as stream:
                return json.load(io.TextIOWrapper(stream, encoding="utf-8"))
    candidates = [snapshot / filename] + list(snapshot.glob("*/" + filename))
    matches = [p for p in candidates if p.is_file()]
    if len(matches) != 1:
        raise ValueError("Ambiguous local file: " + filename)
    return json.loads(matches[0].read_text(encoding="utf-8"))

def normalized(name):
    name = unicodedata.normalize("NFKD", name or "")
    name = name.encode("ascii", "ignore").decode("ascii").upper()
    return re.sub(r"[^A-Z0-9]+", " ", name).strip()

def center(row):
    coords = (row.get("location_id") or {}).get("COORDINATES") or []
    if len(coords) > 2 and coords[0] == coords[-1]:
        coords = coords[:-1]
    if not coords:
        return None
    try:
        lat = sum(float(p["lat"]) for p in coords) / len(coords)
        lon = sum(float(p["lng"]) for p in coords) / len(coords)
        return (lat, lon) if -90 <= lat <= 90 and -180 <= lon <= 180 else None
    except (TypeError, ValueError, KeyError):
        return None

def separation(a, b):
    return math.hypot(111195 * (a[0] - b[0]),
                      111195 * math.cos(math.radians((a[0] + b[0]) / 2)) * (a[1] - b[1]))

def save_csv(path, fields, records):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, help="Downloaded snapshot ZIP or extracted directory")
    parser.add_argument("--output", required=True, help="Destination directory")
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    inventory = load(args.snapshot, "inventory.json")
    stamp = inventory["date"]
    detail = {str(x["ROUTE"]["ID"]): x for x in load(args.snapshot, "route_detail.json")["data"]}
    station_api = load(args.snapshot, "route_stations.json")
    endpoint = defaultdict(list)
    for row in station_api:
        endpoint[str(row["ROUTE_ID"])].append(row)

    summary, candidates, extra, collisions, issues, positioned = [], [], [], [], [], []
    for route_id, code in ROUTES.items():
        data = detail[route_id]
        points = sorted(data["DETAIL"], key=lambda x: int(x["ORDER"]))
        checkpoints = [x for x in points if int(x["IS_CHECKPOINT"]) == 1]
        embedded = data["STATIONS"]
        chosen = sorted(endpoint[route_id], key=lambda x: int(x["ORDER"]))
        by_id = {x["ID"]: x for x in checkpoints}
        def identical(r):
            match = by_id.get(r["ID"])
            return match is not None and str(match["ORDER"]) == str(r["ORDER"]) and match["LOCATION_ID"] == r["LOCATION_ID"]
        embedded_ok = len(embedded) == len(checkpoints) and all(map(identical, embedded))
        endpoint_ok = all(map(identical, chosen))
        orders_wrong = sum(int(r["ORDER"]) != n for n, r in enumerate(points, 1))
        chain_wrong = sum(a["NEXT_LOCATION_ID"] != b["LOCATION_ID"] for a, b in zip(points, points[1:]))
        selected_row_ids = {x["ID"] for x in chosen}
        selected_ids = {x["LOCATION_ID"] for x in chosen}
        loc_counts = Counter(x["LOCATION_ID"] for x in checkpoints)
        loc_ids = set(loc_counts)
        bad = sum(center(x) is None for x in chosen)
        multipoint = sum(len((x.get("location_id") or {}).get("COORDINATES") or []) > 1 for x in chosen)
        summary.append(dict(route=code, api_id=route_id, detail_points=len(points),
            detail_checkpoint_rows=len(checkpoints), embedded_station_rows=len(embedded),
            endpoint_station_rows=len(chosen), endpoint_unique_location_ids=len(selected_ids),
            checkpoint_unique_location_ids=len(loc_ids),
            additional_checkpoint_rows=len(checkpoints)-len(chosen),
            additional_distinct_locations=len(loc_ids-selected_ids),
            repeated_checkpoint_occurrences=len(checkpoints)-len(loc_ids),
            endpoint_id_order_location_matches=endpoint_ok,
            embedded_stations_exact_checkpoint_subset=embedded_ok,
            endpoint_duplicate_location_ids=len(chosen)-len(selected_ids),
            detail_order_gaps=orders_wrong, detail_broken_links=chain_wrong,
            endpoint_missing_coordinates=bad, endpoint_multipoint_geometry=multipoint,
            status="research_consistent_not_gtfs_ready" if embedded_ok and endpoint_ok and not (orders_wrong or chain_wrong or bad) else "needs_technical_review"))
        if not embedded_ok or not endpoint_ok or orders_wrong or chain_wrong or bad:
            issues.append(dict(route=code, issue="API consistency", detail="Check embedded/endpoint IDs, topology or coordinates"))
        for x in chosen:
            loc = x.get("location_id") or {}
            coordinates = loc.get("COORDINATES") or []
            c = center(x)
            candidate = dict(route=code, api_id=route_id, detail_order=x["ORDER"],
                detail_id=x["ID"], location_id=x["LOCATION_ID"], name=loc.get("NAME",""),
                normalized_name=normalized(loc.get("NAME","")), geometry_vertices=len(coordinates),
                research_centroid_lat=f"{c[0]:.7f}" if c else "",
                research_centroid_lon=f"{c[1]:.7f}" if c else "",
                geometry_status="derived_polygon_centroid_not_verified_stop" if c else "missing_or_invalid",
                gtfs_stop_ready="No",
                comment="Endpoint-selected checkpoint; candidate, not validated boarding stop or precise coordinate")
            candidates.append(candidate)
            if c:
                positioned.append((candidate, c))
        for x in checkpoints:
            if x["ID"] in selected_row_ids:
                continue
            extra.append(dict(route=code, api_id=route_id, detail_order=x["ORDER"],
                detail_id=x["ID"], location_id=x["LOCATION_ID"],
                name=(x.get("location_id") or {}).get("NAME",""),
                reason="duplicate_visit_to_endpoint_location" if x["LOCATION_ID"] in selected_ids else "checkpoint_location_not_in_station_endpoint",
                repeated_location_count_in_checkpoints=loc_counts[x["LOCATION_ID"]],
                action="Review source semantics; do not automatically add to GTFS stops or trips"))

    for i, (a, ca) in enumerate(positioned):
        for b, cb in positioned[i+1:]:
            if a["api_id"] == b["api_id"]:
                continue
            d = separation(ca, cb)
            if d < 30:
                same = a["normalized_name"].replace(" ", "") == b["normalized_name"].replace(" ", "")
                collisions.append(dict(route_a=a["route"], route_b=b["route"],
                    location_id_a=a["location_id"], location_id_b=b["location_id"],
                    name_a=a["name"], name_b=b["name"], centroid_distance_m=f"{d:.1f}",
                    normalized_names_equal="yes" if same else "no",
                    status="manual_review_keep_separate_until_verified"))

    save_csv(out / f"stop_layer_summary_{stamp}.csv",
        ["route","api_id","detail_points","detail_checkpoint_rows","embedded_station_rows",
         "endpoint_station_rows","endpoint_unique_location_ids","checkpoint_unique_location_ids",
         "additional_checkpoint_rows","additional_distinct_locations","repeated_checkpoint_occurrences",
         "endpoint_id_order_location_matches","embedded_stations_exact_checkpoint_subset",
         "endpoint_duplicate_location_ids","detail_order_gaps","detail_broken_links",
         "endpoint_missing_coordinates","endpoint_multipoint_geometry","status"], summary)
    save_csv(out / f"stop_endpoint_candidates_{stamp}.csv",
        ["route","api_id","detail_order","detail_id","location_id","name","normalized_name",
         "geometry_vertices","research_centroid_lat","research_centroid_lon","geometry_status",
         "gtfs_stop_ready","comment"], candidates)
    save_csv(out / f"stop_additional_checkpoints_{stamp}.csv",
        ["route","api_id","detail_order","detail_id","location_id","name","reason",
         "repeated_location_count_in_checkpoints","action"], extra)
    save_csv(out / f"stop_spatial_review_{stamp}.csv",
        ["route_a","route_b","location_id_a","location_id_b","name_a","name_b",
         "centroid_distance_m","normalized_names_equal","status"], collisions)
    save_csv(out / f"stop_technical_issues_{stamp}.csv", ["route","issue","detail"], issues)
    print(f"Routes={len(summary)} DETAIL={sum(x['detail_points'] for x in summary)} "
          f"checkpoint={len(extra)+len(candidates)} endpoint={len(candidates)} "
          f"extra={len(extra)} proximity_pairs={len(collisions)} technical_issues={len(issues)}")
    print("Read the separately versioned docs/sitme_stop_layer_audit_2026-11-08.md for interpretation.")

if __name__ == "__main__":
    main()
