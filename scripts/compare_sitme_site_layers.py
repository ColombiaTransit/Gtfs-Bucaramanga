#!/usr/bin/env python3
"""Audit public SITME /site/by_client/195 against 2026-11-08 route STATIONS.
Research evidence only. SITE.ID is NOT presumed to equal LOCATION_ID.
"""
import argparse,collections,csv,datetime,io,json,math,os,re,time,unicodedata,urllib.request,zipfile
from pathlib import Path

ROUTES={"3341":"P16S","3342":"P16N","3345":"P8","3346":"P14","3350":"RD27/RD15",
        "3351":"P1","3352":"P2","3353":"P3","3354":"P10","3355":"P18","3356":"AN3","3357":"P19"}
URL="https://apisitme.metrolinea.gov.co/site/by_client/195"
def norm(s):
    return re.sub(r"[^A-Z0-9]+"," ",unicodedata.normalize("NFKD",str(s or "")).encode("ascii","ignore").decode().upper()).strip()
def point(v):
    if isinstance(v,str):
        try:v=json.loads(v)
        except Exception:return None
    if isinstance(v,dict):
        if "lat" in v and ("lng" in v or "lon" in v):
            try:return float(v["lat"]),float(v.get("lng",v.get("lon")))
            except (TypeError,ValueError):return None
        for k in ("COORDINATES","coordinates","location","geometry"):
            if k in v:
                a=point(v[k])
                if a:return a
        return None
    if isinstance(v,list):
        arr=[p for x in v if (p:=point(x))]
        if not arr:return None
        if len(arr)>2 and arr[0]==arr[-1]:arr.pop()
        return sum(x[0] for x in arr)/len(arr),sum(x[1] for x in arr)/len(arr)
    return None
def meters(a,b):
    if a is None or b is None:return None
    lat1,lon1=map(math.radians,a);lat2,lon2=map(math.radians,b)
    h=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 12742000*math.asin(min(1,math.sqrt(h)))
def fromzip(p,name):
    with zipfile.ZipFile(p) as z:
        matches=[x for x in z.namelist() if x==name or x.endswith("/"+name)]
        if len(matches)!=1:raise ValueError("Missing or ambiguous "+name)
        return json.load(io.TextIOWrapper(z.open(matches[0]),encoding="utf-8"))
def fetch():
    headers={"User-Agent":"Mozilla/5.0 (ColombiaTransit stop research)","Referer":"https://sitme.metrolinea.gov.co/rutas",
             "Origin":"https://sitme.metrolinea.gov.co","Accept":"application/json"}
    token=os.environ.get("SITME_API_BEARER_TOKEN","").strip()
    if token:headers["Authorization"]="Bearer "+token
    for trial in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL,headers=headers),timeout=30) as r:
                raw=r.read(25_000_001)
                if len(raw)>25_000_000:raise ValueError("Site payload exceeds 25MB")
                return json.loads(raw)
        except Exception as exc:
            if trial==2:raise RuntimeError("SITME site endpoint unavailable: "+type(exc).__name__+" "+str(exc)[:150]) from exc
            time.sleep(2*(trial+1))
def items(v):
    if isinstance(v,list):return v
    if isinstance(v,dict):
        for key in ("data","sites","items","results","SITES"):
            if key in v:
                if isinstance(v[key],list):return v[key]
                if isinstance(v[key],dict):
                    try:return items(v[key])
                    except ValueError:pass
    raise ValueError("Unexpected /site/by_client JSON structure")
def write(path,rows):
    if not rows:return
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--sites",help="Optional downloaded site JSON for offline reproduction")
    args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    raw=json.loads(Path(args.sites).read_text()) if args.sites else fetch()
    data=items(raw)
    (out/"site_by_client_195_raw.json").write_text(json.dumps(raw,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    route=fromzip(args.snapshot,"route_detail.json");route=route.get("data",route)
    endpoint=fromzip(args.snapshot,"route_stations.json")
    if isinstance(endpoint,dict):endpoint=endpoint.get("data",endpoint)
    selected={(str(p.get("ROUTE_ID")),str(p.get("ID"))) for p in endpoint}
    loc={};visits=collections.defaultdict(list)
    for routeobj in route:
        rid=str(routeobj["ROUTE"]["ID"])
        if rid not in ROUTES:continue
        for cp in routeobj.get("STATIONS",[]):
            li=cp.get("location_id") or {}
            lid=str(cp.get("LOCATION_ID") or li.get("ID") or "")
            if not lid:continue
            if lid not in loc:loc[lid]={"name":li.get("NAME",""),"norm":norm(li.get("NAME")),
                                      "coord":point(li.get("COORDINATES")),"routes":set()}
            loc[lid]["routes"].add(ROUTES[rid])
            visits[lid].append((rid,cp.get("ORDER"),(rid,str(cp.get("ID"))) in selected))
    rows=[];links=collections.defaultdict(list)
    for site in data:
        if not isinstance(site,dict):continue
        name=site.get("NAME") or site.get("name") or "";coord=point(site.get("COORDINATES") or site.get("coordinates"))
        geo=site.get("geozoneType") or {};cat=site.get("geozoneCategory") or {}
        geo=geo.get("NAME","") if isinstance(geo,dict) else str(geo)
        cat=cat.get("NAME","") if isinstance(cat,dict) else str(cat)
        explicit=site.get("LOCATION_ID") or site.get("location_id")
        if isinstance(explicit,dict):explicit=explicit.get("ID")
        explicit=str(explicit) if explicit is not None else ""
        same=[(lid,meters(coord,x["coord"])) for lid,x in loc.items() if norm(name) and norm(name)==x["norm"]]
        nearby=sorted([(lid,d) for lid,d in same if d is not None and d<=100],key=lambda x:x[1])
        closest=sorted([(lid,meters(coord,x["coord"])) for lid,x in loc.items() if coord and x["coord"]],
                       key=lambda x:x[1])[:3] if coord else []
        if explicit in loc:method="explicit_location_id";match=explicit;d=meters(coord,loc[match]["coord"])
        elif len(nearby)==1:method="name_within_100m";match,d=nearby[0]
        elif len(nearby)>1:method="ambiguous_name_nearby";match="";d=None
        elif closest and closest[0][1]<=30:method="spatial_only_review";match="";d=closest[0][1]
        elif len(same)==1:method="name_only_review";match="";d=same[0][1]
        else:method="unmatched";match="";d=None
        row={"site_id":site.get("ID",site.get("id","")),"site_name":name,"geozone_type":geo,
             "geozone_category":cat,"site_lat":coord[0] if coord else "",
             "site_lon":coord[1] if coord else "","explicit_location_id":explicit,
             "matched_location_id":match,"method":method,"distance_m":round(d,1) if d is not None else "",
             "nearby_location_ids":";".join(t[0] for t in closest)}
        rows.append(row)
        if match:links[match].append(row)
    joined=[]
    for lid,x in loc.items():
        v=visits[lid];s=links.get(lid,[])
        joined.append({"location_id":lid,"route_checkpoint_name":x["name"],
                       "routes":";".join(sorted(x["routes"])),"checkpoint_visits":len(v),
                       "route_stations_selected_visits":sum(x[2] for x in v),
                       "site_matches":len(s),"site_ids":";".join(str(t["site_id"]) for t in s),
                       "site_types":";".join(sorted({t["geozone_type"] for t in s})),
                       "site_categories":";".join(sorted({t["geozone_category"] for t in s})),
                       "gtfs_boarding_stop_verified":"No"})
    write(out/"site_matches.csv",rows);write(out/"route_location_site_crosswalk.csv",joined)
    types=collections.Counter(r["geozone_type"] for r in rows)
    methods=collections.Counter(r["method"] for r in rows)
    summary={"source_url":URL,"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "site_records":len(rows),"route_location_ids":len(loc),"route_checkpoint_visits":sum(map(len,visits.values())),
             "route_locations_with_site_match":len(links),"route_locations_without_site_match":len(loc)-len(links),
             "site_type_counts":dict(types),"matching_methods":dict(methods),"gtfs_ready":False}
    (out/"comparison_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    md=["# SITME public map sites versus route checkpoint locations","",
        f"Retrieved: {summary['utc']}","",
        f"- Map site records: **{len(rows)}**",
        f"- Unique route LOCATION_IDs: **{len(loc)}**",
        f"- Route checkpoint occurrences: **{summary['route_checkpoint_visits']}**",
        f"- Route locations with any site match: **{len(links)}**",
        f"- Route locations without site match: **{len(loc)-len(links)}**",
        "","## Map site types",""]
    md += [f"- {k or '(empty)'}: {n}" for k,n in sorted(types.items())]
    md += ["","## Match classifications",""]
    md += [f"- {k}: {n}" for k,n in sorted(methods.items())]
    md += ["","## Interpretation","",
           "Only explicit LOCATION_ID matches or unique exact-name-and-nearby-coordinate matches are linked. "
           "Matches remain research associations, not confirmed GTFS boarding platforms. "
           "SITE.ID alone is never used as a route LOCATION_ID. "
           "Absence from the site catalog does not prove a route STATIONS entry is unusable. "
           "Spatial-only and ambiguous cases require human review.","",
           "Source: public /site/by_client/195 response compared with immutable 2026-11-08 route snapshot."]
    (out/"site_layer_comparison.md").write_text("\n".join(md)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
