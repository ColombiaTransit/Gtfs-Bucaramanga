#!/usr/bin/env python3
"""Reproduce research-only SITME stops/route visits from the 2026-11-08 snapshot.

No stop position or boarding eligibility is validated. Do not release these
tables as GTFS stops.txt or stop_times.txt without further checks.
"""
import argparse
import csv
import json
import zipfile
from collections import defaultdict
from pathlib import Path

ROUTES = {3341:"P16S",3342:"P16N",3345:"P8",3346:"P14",
          3350:"RD27/RD15",3351:"P1",3352:"P2",3353:"P3",
          3354:"P10",3355:"P18",3356:"AN3",3357:"P19"}

def center(location):
    points = []
    for p in location.get("COORDINATES") or []:
        try: points.append((float(p["lat"]), float(p["lng"])))
        except (ValueError, TypeError, KeyError): continue
    if len(points)>2 and points[0]==points[-1]:points.pop()
    if not points:return "", ""
    return (round(sum(x for x,y in points)/len(points),8),
            round(sum(y for x,y in points)/len(points),8))

def write(path, rows):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",required=True)
    p.add_argument("--decisions",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    with open(args.decisions,encoding="utf-8",newline="") as f:
        decisions=list(csv.DictReader(f))
    assert len(decisions)==5
    aliases={}
    for d in decisions:
        old=d["source_location_id"];new=d["canonical_stop_id"]
        if d["identity_decision"]=="same_physical_stop":
            assert old!=new
            aliases[old]=new
        else:
            assert d["identity_decision"]=="distinct_directional_stop" and old==new
    assert aliases=={"150873":"150965","150877":"150969","163015":"163024"}
    with zipfile.ZipFile(args.snapshot) as z:
        matches=[x for x in z.namelist() if x.endswith("/route_detail.json") or x=="route_detail.json"]
        assert len(matches)==1
        data=json.loads(z.read(matches[0]))["data"]
    locs={}
    visits=[]
    contributing=defaultdict(set)
    for route in data:
        rid=int(route["ROUTE"]["ID"])
        if rid not in ROUTES:continue
        for point in sorted(route["STATIONS"],key=lambda x:int(x["ORDER"])):
            source=str(point["LOCATION_ID"])
            candidate=aliases.get(source,source)
            location=point["location_id"]
            if source in locs:
                assert locs[source]["NAME"]==location["NAME"]
            else:locs[source]=location
            contributing[candidate].add(source)
            visits.append({
               "api_route_id":rid,"route_code":ROUTES[rid],
               "detail_order":point["ORDER"],"detail_record_id":point["ID"],
               "source_location_id":source,"candidate_stop_id":candidate,
               "source_stop_name":location["NAME"],
               "canonicalized":str(source!=candidate).lower(),
               "checkpoint_in_snapshot":"true",
               "boarding_stop_verified":"false","proposed_gtfs_status":"research_only"
            })
    assert len(locs)==531 and len(visits)==950
    stops=[]
    for sid,olds in sorted(contributing.items(),key=lambda x:int(x[0])):
        source=locs[sid]
        lat,lon=center(source)
        stops.append({
            "candidate_stop_id":sid,"stop_name":source["NAME"],
            "centroid_lat_research_only":lat,"centroid_lon_research_only":lon,
            "source_location_ids":";".join(sorted(olds,key=int)),
            "original_location_id_count":len(olds),
            "coordinate_quality":"derived_polygon_centroid_not_verified_stop",
            "boarding_stop_verified":"false","gtfs_stop_ready":"false",
            "notes":"No automatic merge of opposite-direction stops; boarding positions unverified."
        })
    assert len(stops)==528
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    write(out/"stop_candidates_reconciled_2026-11-09.csv",stops)
    write(out/"route_stop_visits_reconciled_2026-11-09.csv",visits)
    print(f"Original LOCATION_IDs={len(locs)} candidate stops={len(stops)} route visits={len(visits)}")

if __name__=="__main__":main()
