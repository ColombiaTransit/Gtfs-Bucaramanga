#!/usr/bin/env python3
"""Evidence-graded OSM check of SITME stop candidates, *not* a GTFS exporter.

Inputs are versioned research-only SITME CSVs and the 2026-11-08 API snapshot.
Public Overpass data may be supplied from files (preferred for reproducibility),
or downloaded when --fetch-osm is set. No automatic stop merging or approval.

Examples:
  python scripts/audit_sitme_osm_stop_positions.py --snapshot sitme-route-snapshot.zip \
    --candidates data/sitme/stop_candidates_reconciled_2026-11-09.csv \
    --visits data/sitme/route_stop_visits_reconciled_2026-11-09.csv \
    --output osm-stop-audit --fetch-osm
  python scripts/audit_sitme_osm_stop_positions.py ... --osm-stops osm_stops.json --osm-roads osm_roads.json
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

ROUTE_IDS = {3341: 'P16S', 3342: 'P16N', 3345: 'P8', 3346: 'P14',
             3350: 'RD27/RD15', 3351: 'P1', 3352: 'P2', 3353: 'P3',
             3354: 'P10', 3355: 'P18', 3356: 'AN3', 3357: 'P19'}
ALIAS = {'150873': '150965', '150877': '150969', '163015': '163024'}
NEVER_MERGE = {frozenset(('150798', '150973')),
               frozenset(('164171', '164933'))}
STOP_TAGS = {'highway': 'bus_stop', 'public_transport': 'platform'}
ROAD_TYPES = 'trunk|primary|secondary|tertiary|residential|unclassified|living_street|service|busway'
DEFAULT_OVERPASS = 'https://overpass-api.de/api/interpreter'


def csv_rows(path):
    with open(path, newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows, fieldnames):
    with open(path, 'w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def normalized(value):
    value = unicodedata.normalize('NFKD', str(value or '')).encode('ascii', 'ignore').decode().upper()
    value = re.sub(r'[^A-Z0-9]+', ' ', value).strip()
    return ' '.join(x for x in value.split() if x not in {
        'ESTACION', 'PARADERO', 'PARADA', 'INICIO', 'FIN', 'CALLE', 'CARRERA', 'NO'})


def direction(value):
    # S-n means south to north, N-s north to south; does NOT imply same platform.
    m = re.search(r'(?i)(?:^|\W)([NS])\s*[-/]\s*([NS])(?:\W|$)', str(value or ''))
    return m.group(1).upper() + '-' + m.group(2).upper() if m else ''


def name_score(a, b):
    a, b = normalized(a), normalized(b)
    if not a or not b:
        return 0.0
    seq = SequenceMatcher(None, a, b).ratio()
    tokens_a, tokens_b = set(a.split()), set(b.split())
    overlap = len(tokens_a & tokens_b) / max(1, len(tokens_a | tokens_b))
    return max(seq, (seq + overlap) / 2)


def meters(a, b):
    if a is None or b is None:
        return None
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 12742000 * math.asin(min(1.0, math.sqrt(h)))


def xy(latlon, anchor):
    return ((latlon[1]-anchor[1])*111195*math.cos(math.radians(anchor[0])),
            (latlon[0]-anchor[0])*111195)


def project_segment(point, a, b):
    """(distance metres, closest lat/lon, signed cross-track metres) for oriented a->b."""
    px, py = xy(point, a)
    bx, by = xy(b, a)
    n = bx*bx+by*by
    if n < 1e-8:
        return meters(point, a), a, None
    fraction = max(0.0, min(1.0, (px*bx+py*by)/n))
    cross_x, cross_y = fraction*bx, fraction*by
    closest = (a[0]+cross_y/111195,
               a[1]+cross_x/(111195*math.cos(math.radians(a[0]))))
    side = (bx*py-by*px)/math.sqrt(n)  # positive is left of travel direction
    return math.hypot(px-cross_x, py-cross_y), closest, side


def firstpoint(coords):
    if not coords:
        return None
    try:
        v = coords[0]
        return (float(v['lat']), float(v['lng']))
    except (TypeError, ValueError, IndexError, KeyError):
        return None


def centroid(coords):
    try:
        pts = [(float(x['lat']), float(x['lng'])) for x in (coords or [])]
    except (TypeError, ValueError, KeyError):
        return None
    if len(pts)>2 and pts[0] == pts[-1]:
        pts.pop()
    if not pts:
        return None
    return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))


def load_snapshot(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith('/route_detail.json') or n=='route_detail.json']
        if len(names)!=1:
            raise ValueError('Snapshot must contain exactly one route_detail.json')
        all_routes = json.loads(z.read(names[0]))['data']
    routes = {}
    for item in all_routes:
        rid = int(item['ROUTE']['ID'])
        if rid in ROUTE_IDS:
            routes[rid] = sorted(item['DETAIL'], key=lambda v:int(v['ORDER']))
    if set(routes)!=set(ROUTE_IDS):
        raise ValueError('Missing complementary route details: '+str(set(ROUTE_IDS)-set(routes)))
    return routes


def validate_inputs(candidates, visits, details):
    ids = {r['candidate_stop_id'] for r in candidates}
    if len(ids)!=528 or len(candidates)!=528 or len(visits)!=950:
        raise ValueError('Expected immutable 528 candidates / 950 visits; got '+str((len(candidates),len(visits))))
    for c in candidates:
        if c.get('gtfs_stop_ready','false').lower()!='false':
            raise ValueError('Unexpected GTFS-ready stop in research baseline')
    for v in visits:
        if v['candidate_stop_id'] not in ids or int(v['api_route_id']) not in details:
            raise ValueError('Orphan visit '+str(v))
        src, canonical=v['source_location_id'],v['candidate_stop_id']
        if ALIAS.get(src,src)!=canonical:
            raise ValueError(f'Unexpected alias mapping {src}->{canonical}')
    by_route = defaultdict(list)
    for v in visits:
        by_route[int(v['api_route_id'])].append(v)
    for rid, vals in by_route.items():
        source_checks={str(d['ID']):str(d['LOCATION_ID']) for d in details[rid] if int(d.get('IS_CHECKPOINT',0))==1}
        for v in vals:
            if source_checks.get(str(v['detail_record_id']))!=str(v['source_location_id']):
                raise ValueError('Visit not grounded in source snapshot: '+str(v))
    return by_route


def osm_point(record):
    if 'lat' in record and 'lon' in record:
        return (float(record['lat']),float(record['lon']))
    if 'center' in record and 'lat' in record['center'] and 'lon' in record['center']:
        return (float(record['center']['lat']),float(record['center']['lon']))
    geometry = record.get('geometry') or []
    if geometry:
        a=[(float(x['lat']),float(x['lon'])) for x in geometry]
        return (sum(x[0] for x in a)/len(a),sum(x[1] for x in a)/len(a))
    return None


def parse_stops(data):
    seen=set(); out=[]
    for r in data.get('elements',[]):
        ident=(r.get('type'),r.get('id'))
        if ident in seen:continue
        seen.add(ident)
        p=osm_point(r)
        if not p:continue
        tags=r.get('tags') or {}
        kind=('platform' if tags.get('public_transport')=='platform' or tags.get('highway')=='bus_stop'
              else 'stop_position' if tags.get('public_transport')=='stop_position'
              else 'station' if tags.get('public_transport')=='station' or tags.get('amenity')=='bus_station'
              else 'other')
        # Avoid non-bus public_transport=platform nodes when transport mode is explicitly non-bus.
        if tags.get('bus')=='no' and tags.get('highway')!='bus_stop':continue
        out.append({'id':f"{r['type']}/{r['id']}",'point':p,'name':tags.get('name',''),
                    'ref':tags.get('ref',''),'gtfs':tags.get('gtfs:stop_id',''),
                    'kind':kind,'tags':tags})
    return out


def parse_roads(data):
    out=[];seen=set()
    for r in data.get('elements',[]):
        if r.get('type')!='way' or r.get('id') in seen:continue
        seen.add(r['id'])
        if not (r.get('tags') or {}).get('highway'):continue
        pts = [(float(p['lat']),float(p['lon'])) for p in (r.get('geometry') or [])]
        if len(pts)>1:
            out.append({'id':f"way/{r['id']}", 'highway':r['tags']['highway'],
                        'name':(r['tags'].get('name') or ''),'pts':pts})
    return out


def road_index(roads):
    """Return a coarse (roughly 250m) index of roads near each OSM map cell."""
    buckets=defaultdict(list)
    scale=400
    for i, road in enumerate(roads):
        for a,b in zip(road['pts'],road['pts'][1:]):
            a0,a1=sorted((int(math.floor(a[0]*scale)),int(math.floor(b[0]*scale))))
            b0,b1=sorted((int(math.floor(a[1]*scale)),int(math.floor(b[1]*scale))))
            # Long segments span multiple cells, but avoid exploding on bad geometries.
            if (a1-a0+1)*(b1-b0+1)>800:continue
            for x in range(a0-1,a1+2):
                for y in range(b0-1,b1+2):
                    buckets[(x,y)].append((i,a,b))
    return buckets


def nearest_road(point, roads, index, limit=45):
    if not roads:return None
    scale=400
    candidates=index.get((int(math.floor(point[0]*scale)),
                          int(math.floor(point[1]*scale))),[])
    best=None
    for i,a,b in candidates:
        d, _, _=project_segment(point,a,b)
        if d<=limit and (best is None or d<best[0]):best=(d,roads[i])
    return best


def route_passage_diagnostics(visits, details, candidate_positions, osm_matches, roads):
    by_route=defaultdict(list)
    for v in visits:by_route[int(v['api_route_id'])].append(v)
    records=[]
    index=road_index(roads)
    road_cache={}
    for rid, route_visits in by_route.items():
        nodes=details[rid]
        coords=[centroid(d['location_id'].get('COORDINATES')) for d in nodes]
        idx={str(d['ID']):i for i,d in enumerate(nodes)}
        for v in sorted(route_visits,key=lambda x:int(x['detail_order'])):
            i=idx[v['detail_record_id']]; center=coords[i]; tangent=None
            # Prefer a local 10-60 metre segment across this *specific visit*, not across a loop shortcut.
            prior=next((coords[j] for j in range(i-1,max(-1,i-10),-1)
                        if center and coords[j] and 10 <= meters(coords[j],center) <= 140),None)
            future=next((coords[j] for j in range(i+1,min(len(nodes),i+10))
                         if center and coords[j] and 10 <= meters(coords[j],center) <= 140),None)
            if prior and future and 8 < meters(prior,future) < 260:tangent=(prior,future)
            p=candidate_positions[v['candidate_stop_id']]
            osm=osm_matches.get(v['candidate_stop_id'])
            osm_p=osm['point'] if osm else None
            route_distance=round(meters(center,osm_p),1) if center and osm_p else ''
            rel_side='unknown'
            offset=''
            if tangent and osm_p:
                d, _, cross=project_segment(osm_p,*tangent)
                offset=round(cross,1)
                if abs(cross)<4:rel_side='ambiguous_centre_or_geofence'
                else:rel_side='left_of_travel' if cross>0 else 'right_of_travel'
            road_key=osm['id'] if osm else None
            if osm_p and roads and road_key not in road_cache:
                road_cache[road_key]=nearest_road(osm_p,roads,index)
            road=road_cache.get(road_key)
            records.append(dict(api_route_id=rid,route_code=ROUTE_IDS[rid],detail_order=v['detail_order'],
                                source_location_id=v['source_location_id'],candidate_stop_id=v['candidate_stop_id'],
                                source_stop_name=v['source_stop_name'],route_point_lat=(round(center[0],8) if center else ''),
                                route_point_lon=(round(center[1],8) if center else ''),
                                osm_match_id=(osm['id'] if osm else ''),osm_distance_to_route_point_m=route_distance,
                                osm_offset_from_travel_m=offset,possible_side_relative_to_travel=rel_side,
                                osm_nearest_road_id=(road[1]['id'] if road else ''),
                                osm_nearest_road_distance_m=(round(road[0],1) if road else ''),
                                road_side_verified='false',stop_visit_retained='true'))
    return records


def determine_category(c, osm, d, similarity, conflict, route_contexts):
    if osm is None:
        return ('C_manual_review','no_osm_stop_candidate','unknown')
    if conflict:
        return ('C_manual_review','direction_or_match_conflict','unknown')
    tag_candidate=osm['kind']=='platform'
    # Some stops have generic numbered references and no OSM name: avoid A.
    if (tag_candidate and d<=25 and similarity>=0.80 and
            route_contexts and all(x!='left_of_travel' for x in route_contexts if x not in ('unknown','ambiguous_centre_or_geofence'))):
        return ('A_strong_candidate','platform_name_distance_consistent','probable_boarding_location_unverified')
    if d<=65 and (similarity>=0.48 or osm['kind']=='platform'):
        return ('B_probable','near_mapped_stop_but_not_verified','possibly_boarding_location')
    return ('C_manual_review','osm_position_or_name_unconvincing','unknown')


def score_candidates(candidates, stops, visits, details, roads):
    cand_pos={c['candidate_stop_id']:(float(c['centroid_lat_research_only']),
                                        float(c['centroid_lon_research_only'])) for c in candidates}
    # OSM spatial bucketing for fast nearest neighbours, ~200m cells.
    buckets=defaultdict(list)
    for s in stops:
        lat,lon=s['point']; buckets[(round(lat*450),round(lon*450))].append(s)
    candidate_choices={}; choices_by_osm=defaultdict(list)
    rows=[]
    for c in candidates:
        sid=c['candidate_stop_id'];point=cand_pos[sid]
        key=(round(point[0]*450),round(point[1]*450)); found=[]
        for di in range(-2,3):
            for dj in range(-2,3):
                for s in buckets.get((key[0]+di,key[1]+dj),[]):
                    d=meters(point,s['point'])
                    if d<=120:
                        sim=name_score(c['stop_name'],s['name'])
                        orient1=direction(c['stop_name']);orient2=direction(s['name'])
                        dir_conflict=bool(orient1 and orient2 and orient1!=orient2)
                        known_ref = sid in {s['ref'],s['gtfs']} or any(a in {s['ref'],s['gtfs']} for a in c['source_location_ids'].split(';'))
                        quality = (0.42*max(0,1-d/120)+0.43*sim+0.10*int(s['kind']=='platform')+
                                   0.20*int(known_ref)-0.45*int(dir_conflict))
                        found.append((quality,d,sim,dir_conflict,s))
        found.sort(key=lambda x:(-x[0],x[1],x[4]['id']))
        chosen=found[0] if found and found[0][0]>=0.13 else None
        if chosen:
            candidate_choices[sid]=chosen[4]; choices_by_osm[chosen[4]['id']].append(sid)
        rows.append({'candidate_stop_id':sid,'stop_name':c['stop_name'],
                     'source_location_ids':c['source_location_ids'],
                     'research_lat':point[0],'research_lon':point[1],
                     'osm_candidate_id':chosen[4]['id'] if chosen else '',
                     'osm_candidate_name':chosen[4]['name'] if chosen else '',
                     'osm_lat':chosen[4]['point'][0] if chosen else '',
                     'osm_lon':chosen[4]['point'][1] if chosen else '',
                     'osm_feature_kind':chosen[4]['kind'] if chosen else '',
                     'osm_distance_m':round(chosen[1],1) if chosen else '',
                     'osm_name_similarity':round(chosen[2],3) if chosen else '',
                     'osm_direction_conflict':str(chosen[3]).lower() if chosen else '',
                     'alternative_osm_candidates_under_120m':len(found)-int(chosen is not None),
                     'match_conflict':'','category':'','reason':'',
                     'boarding_interpretation':'',
                     'exact_platform_coordinate_verified':'false','boarding_stop_verified':'false',
                     'gtfs_stop_ready':'false','stop_lat_research_only':'','stop_lon_research_only':'',
                     'review_priority':'','review_note':''})
    # Route visit proximity/side evidence, do not equate name labels with travel direction.
    passage=route_passage_diagnostics(visits,details,cand_pos,candidate_choices,roads)
    ctx=defaultdict(list)
    for r in passage:ctx[r['candidate_stop_id']].append(r['possible_side_relative_to_travel'])
    for row in rows:
        sid=row['candidate_stop_id'];osm=candidate_choices.get(sid)
        conflict=''
        if osm:
            sharing=choices_by_osm[osm['id']]
            if len(sharing)>1:
                # Same OSM location is ambiguous for distinct user-confirmed directional stops.
                if any(frozenset((sid,other)) in NEVER_MERGE for other in sharing if other!=sid):
                    conflict='user_confirmed_distinct_stops_collide_osm'
                else:
                    conflict='multiple_canonical_stops_share_osm_candidate'
            if row['osm_direction_conflict']=='true':conflict='direction_label_conflict'
            if int(row['alternative_osm_candidates_under_120m'])>0:
                # close runner-up matching almost as well is potentially ambiguous.
                pass
        row['match_conflict']=conflict
        d=float(row['osm_distance_m']) if row['osm_distance_m']!='' else None
        sim=float(row['osm_name_similarity']) if row['osm_name_similarity']!='' else 0
        cat,reason,boarding=determine_category(row,osm,d,sim,conflict,ctx[sid])
        row['category']=cat;row['reason']=reason;row['boarding_interpretation']=boarding
        row['review_priority']='high' if cat.startswith('C_') or conflict else 'medium' if cat.startswith('B_') else 'low'
        row['review_note']=('OSM platform candidate is not independently confirmed as current SITME boarding point. '
                            'SITME centroid and direction-side estimates may be inaccurate. '
                            'Do not merge opposite platforms or export stop_lat/stop_lon without verification.')
        if osm:
            row['stop_lat_research_only'],row['stop_lon_research_only']=osm['point']
    return rows,passage,candidate_choices


def overpass(query, endpoint, retries=3):
    hdr={'User-Agent':'Mozilla/5.0 (compatible; ColombiaTransit-SITME-GTFS-Research/1.0)',
         'Accept':'application/json','Content-Type':'application/x-www-form-urlencoded'}
    extra=os.environ.get('OVERPASS_EXTRA_HEADERS_JSON','').strip()
    if extra:
        custom=json.loads(extra)
        if not isinstance(custom,dict) or not all(isinstance(k,str) and isinstance(v,str) for k,v in custom.items()):
            raise ValueError('OVERPASS_EXTRA_HEADERS_JSON must be a string-to-string JSON object')
        hdr.update(custom)
    token=os.environ.get('OVERPASS_BEARER_TOKEN','').strip()
    if token:hdr['Authorization']='Bearer '+token
    data=urllib.parse.urlencode({'data':query}).encode('utf-8')
    last=None
    for i in range(retries):
        try:
            req=urllib.request.Request(endpoint,data=data,headers=hdr,method='POST')
            with urllib.request.urlopen(req,timeout=240) as response:
                body=response.read(90000000)
                if len(body)>=90000000:raise ValueError('Overpass response too large (>90MB)')
                parsed=json.loads(body)
                if 'elements' not in parsed:raise ValueError('No Overpass elements property')
                return parsed
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            last=exc
            if i+1<retries:time.sleep(min(30,4*(i+1)))
    raise RuntimeError('Overpass unavailable after retries: '+type(last).__name__)


def get_osm(candidates, args, out):
    lat=[float(x['centroid_lat_research_only']) for x in candidates]
    lon=[float(x['centroid_lon_research_only']) for x in candidates]
    south,west,north,east=min(lat)-0.005,min(lon)-0.005,max(lat)+0.005,max(lon)+0.005
    bbox=','.join(f'{n:.6f}' for n in (south,west,north,east))
    notes=[]
    if args.osm_stops:
        stops=json.loads(Path(args.osm_stops).read_text(encoding='utf-8'))
        notes.append('OSM stop evidence loaded from user-provided snapshot.')
    elif args.fetch_osm:
        query=f'''[out:json][timeout:180];(
          nwr["highway"="bus_stop"]({bbox});
          nwr["public_transport"~"^(platform|stop_position|station)$"]({bbox});
          nwr["amenity"="bus_station"]({bbox});
        );out center tags;'''
        stops=overpass(query,args.overpass_url)
        (out/'osm_stops_raw.json').write_text(json.dumps(stops,ensure_ascii=False),encoding='utf-8')
        notes.append('OSM stops fetched live from configured Overpass API.')
    else:
        stops={'elements':[]};notes.append('OSM stops not fetched; all absence claims are unavailable, not negative evidence.')
    if args.osm_roads:
        roads=json.loads(Path(args.osm_roads).read_text(encoding='utf-8'))
        notes.append('OSM road evidence loaded from user-provided snapshot.')
    elif args.fetch_osm and not args.skip_roads:
        query=f'''[out:json][timeout:240];(
         way["highway"~"^({ROAD_TYPES})$"]({bbox});
        );out geom;'''
        try:
            roads=overpass(query,args.overpass_url,retries=2)
            (out/'osm_roads_raw.json').write_text(json.dumps(roads,ensure_ascii=False),encoding='utf-8')
            notes.append('Road geometry downloaded for direction-side diagnostics; never used to prove boarding.')
        except RuntimeError as exc:
            roads={'elements':[]};notes.append(f'Road Overpass request failed ({exc}); road-side diagnostics unavailable.')
    else:
        roads={'elements':[]};notes.append('Road geometry absent; road-side diagnostics unavailable.')
    return stops,roads,notes,bbox


def safejson(obj):
    return json.dumps(obj,ensure_ascii=False).replace('</','<\\/')


def create_map(out, audit, visits, details, osm_matches):
    # No live calls to APIs from HTML except standard OSM tile/CDN resources.
    features=[]
    for r in audit:
        sid=r['candidate_stop_id']
        osm=osm_matches.get(sid)
        features.append({'id':sid,'name':r['stop_name'],'category':r['category'],
                         'lat':float(r['research_lat']),'lon':float(r['research_lon']),
                         'osm':([osm['point'][0],osm['point'][1]] if osm else None),
                         'osm_id':r['osm_candidate_id'],'osm_distance':r['osm_distance_m'],
                         'reason':r['reason'],'conflict':r['match_conflict']})
    route_lines=[]
    for rid, rows in details.items():
        coords=[]
        for r in rows:
            c=centroid(r['location_id'].get('COORDINATES'))
            if c:coords.append([round(c[0],6),round(c[1],6)])
        route_lines.append({'route':ROUTE_IDS[rid],'id':rid,'coordinates':coords})
    payload=safejson({'stops':features,'routes':route_lines})
    page=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SITME stop evidence QA — research only</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>html,body{height:100%;margin:0;font:14px system-ui,sans-serif}#map{height:100%;width:100%}.pane{position:absolute;top:12px;right:12px;z-index:1000;background:#fff;border-radius:8px;padding:12px;box-shadow:0 1px 10px #7778;max-width:340px}label{display:block;margin:7px 0}h1{font-size:16px;margin:0 0 8px}.note{font-size:12px;max-width:300px;color:#444}.counts{margin-top:8px;font-size:12px}select{max-width:290px}</style></head><body>
<div id="map"><p>Interactive map requires internet access to load Leaflet; the CSV remains complete.</p></div>
<div class="pane"><h1>SITME stop candidates</h1><div class="note">Evidence review, NOT certified GTFS platforms. Dashed connector indicates proposed OSM match; line geometry from SITME is approximate.</div>
<label><input type="checkbox" id="showA" checked/> A — strong match</label>
<label><input type="checkbox" id="showB" checked/> B — probable</label>
<label><input type="checkbox" id="showC" checked/> C — review needed</label>
<label>Route <select id="route"><option value="">All routes</option></select></label>
<label><input id="geom" type="checkbox"/> Show SITME route geometry</label>
<div class="counts" id="count"></div></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>const DATA=__DATA__;
const colors={A:'#168557',B:'#db983c',C:'#cb3d41'};
const map=L.map('map').setView([7.087,-73.111],11);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);
const markerLayer=L.layerGroup().addTo(map),routeLayer=L.layerGroup().addTo(map);
const byStop={};DATA.stops.forEach(s=>byStop[s.id]=s);
const routesForStop={};
const routeSelect=document.getElementById('route');
DATA.routes.forEach(r=>{let opt=document.createElement('option');opt.value=r.id;opt.textContent=r.route;routeSelect.appendChild(opt)});
// Route membership must be provided by explicit visit source ids; not guessed via spatial location.
const visitList=__VISITS__;
visitList.forEach(v=>{(routesForStop[v.candidate_stop_id]??=new Set()).add(String(v.api_route_id))});
function redraw(){markerLayer.clearLayers();routeLayer.clearLayers();const active=new Set(['A','B','C'].filter(k=>document.getElementById('show'+k).checked));const route=routeSelect.value;
let count={A:0,B:0,C:0};for(const s of DATA.stops){const cat=s.category[0];if(!active.has(cat)||route && !(routesForStop[s.id]?.has(route)))continue;count[cat]++;
const mk=L.circleMarker([s.lat,s.lon],{radius:6,weight:2,color:colors[cat],fillOpacity:0.6}).addTo(markerLayer);
const el=document.createElement('div');el.textContent=s.id+' · '+s.name; const d=document.createElement('div');d.textContent='Class: '+s.category+' | '+s.reason+' | OSM: '+(s.osm_id||'none')+' | distance: '+(s.osm_distance||'n/a')+' m';el.appendChild(d);mk.bindPopup(el);
if(s.osm){L.polyline([[s.lat,s.lon],s.osm],{color:colors[cat],weight:1,opacity:0.55,dashArray:'3,4'}).addTo(markerLayer);L.circleMarker(s.osm,{radius:3,color:'#236ab4',fillOpacity:0.9}).addTo(markerLayer)}}
if(document.getElementById('geom').checked){for(const r of DATA.routes){if(route&&String(r.id)!==route)continue;L.polyline(r.coordinates,{color:'#777',weight:2,opacity:0.55}).addTo(routeLayer)}}
document.getElementById('count').textContent=`Shown: A ${count.A}, B ${count.B}, C ${count.C}`}
['showA','showB','showC','route','geom'].forEach(id=>document.getElementById(id).addEventListener('change',redraw));redraw();
</script></body></html>'''
    page=page.replace('__DATA__',payload).replace('__VISITS__',safejson([{'candidate_stop_id':v['candidate_stop_id'],'api_route_id':v['api_route_id']} for v in visits]))
    (out/'sitme_stop_review_map.html').write_text(page,encoding='utf-8')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--snapshot',required=True)
    parser.add_argument('--candidates',required=True)
    parser.add_argument('--visits',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--osm-stops')
    parser.add_argument('--osm-roads')
    parser.add_argument('--fetch-osm',action='store_true')
    parser.add_argument('--skip-roads',action='store_true')
    parser.add_argument('--overpass-url',default=(os.getenv('OVERPASS_URL') or DEFAULT_OVERPASS))
    args=parser.parse_args()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    candidates=csv_rows(args.candidates); visits=csv_rows(args.visits)
    details=load_snapshot(args.snapshot)
    validate_inputs(candidates,visits,details)
    raw_stops,raw_roads,notes,bbox=get_osm(candidates,args,out)
    stops=parse_stops(raw_stops);roads=parse_roads(raw_roads)
    audit,passages,matches=score_candidates(candidates,stops,visits,details,roads)
    assert len(audit)==528 and len(passages)==950
    for p in NEVER_MERGE:
        assert all(x['candidate_stop_id'] in {c['candidate_stop_id'] for c in candidates} for x in audit if x['candidate_stop_id'] in p)
    write_csv(out/'stop_osm_quality_2026-11-09.csv',audit,list(audit[0]))
    write_csv(out/'route_stop_direction_checks_2026-11-09.csv',passages,list(passages[0]))
    manual=[r for r in audit if r['category'].startswith('C_') or r['match_conflict']]
    write_csv(out/'stop_manual_review_queue_2026-11-09.csv',manual,list(audit[0]))
    create_map(out,audit,visits,details,matches)
    counts=Counter(x['category'] for x in audit)
    status=('OSM stop evidence retrieved' if stops else 'No OSM stop evidence available')
    summary={'run_utc':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
             'input_candidates':len(candidates),'input_route_visits':len(visits),
             'osm_stop_features':len(stops),'osm_road_features':len(roads),
             'osm_bbox':bbox,'quality_counts':dict(sorted(counts.items())),
             'manual_review_count':len(manual),'osm_source_status':status,
             'gtfs_ready_count':0,'notes':notes}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    md=['# SITME stop-location evidence audit (research; not published GTFS)','',
        f"Audit timestamp UTC: {summary['run_utc']}", '',
        f"- Source candidates: **{len(candidates)}**, route visits: **{len(visits)}**.",
        f"- OSM transit features: **{len(stops)}**, OSM road ways: **{len(roads)}**.",
        f"- Classes: **{json.dumps(dict(counts),ensure_ascii=False)}**; manual queue: **{len(manual)}**.",
        '- **GTFS-ready stops: 0**. Even strong OSM matches remain candidate evidence, not verified boarding-point coordinates.',
        '- The 950 route visits are retained in source order; no new merges are made.',
        '- Confirmed distinct directional pairs 150798/150973 and 164171/164933 are never auto-merged.',
        '- Exact boarding side and physical point cannot be established from polygon-centroid distances alone.',
        '- Direction-side diagnostics use the SITME DETAIL traversal near each specific visit; they are signals, not proofs.',
        '- Per-stop CSV and interactive map list nearest OSM public-transport features; blue point is the OSM position, coloured point is the SITME polygon centroid.',
        '', '## Data acquisition / limitations', '']
    md.extend('- '+n for n in notes)
    md+=['','## Outputs','',
         '- `stop_osm_quality_2026-11-09.csv` — all 528 stops, candidate match, quality category and uncertainty.',
         '- `route_stop_direction_checks_2026-11-09.csv` — all 950 visits with route-side diagnostics.',
         '- `stop_manual_review_queue_2026-11-09.csv` — priority review candidates.',
         '- `sitme_stop_review_map.html` — interactive inspection map; external Leaflet and OSM tiles require internet.',
         '- `summary.json` — source counts, timestamp, completeness.',
         '', '## Next work','',
         'Review C cases and directional conflicts, then verify actual platform positions from authoritative geometry or operator evidence. Only after this review can `stops.txt` be prepared.']
    (out/'stop_osm_audit_report.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
