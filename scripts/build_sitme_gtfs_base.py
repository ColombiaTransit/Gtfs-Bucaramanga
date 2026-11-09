#!/usr/bin/env python3
"""Build research-stage GTFS geometry/stop foundations exclusively from SITME.

Immutable source: SITME 2026-11-08 route snapshot, reconciled stop and
route-visit CSVs from 2026-11-09. No OpenStreetMap or external API calls.

Outputs agency.txt, stops.txt, routes.txt, shapes.txt and source crosswalks.
No trips, timetable, calendars or public-ready GTFS feed are fabricated.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROUTES = {
    3341: 'P16S', 3342: 'P16N', 3345: 'P8', 3346: 'P14',
    3350: 'RD27/RD15', 3351: 'P1', 3352: 'P2', 3353: 'P3',
    3354: 'P10', 3355: 'P18', 3356: 'AN3', 3357: 'P19',
}
ALIASES = {'150873': '150965', '150877': '150969', '163015': '163024'}
DISTINCT = [set(['150798','150973']), set(['164171','164933'])]


def read_csv(path: str | Path) -> list[dict[str,str]]:
    with Path(path).open('r', encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def load_routes(snapshot: Path) -> dict[int,dict]:
    if snapshot.is_dir():
        matches=list(snapshot.rglob('route_detail.json'))
        assert len(matches)==1, f'Expected single route_detail.json, got {len(matches)}'
        data=json.loads(matches[0].read_text(encoding='utf-8'))
    else:
        with zipfile.ZipFile(snapshot) as z:
            matches=[x for x in z.namelist() if x=='route_detail.json' or x.endswith('/route_detail.json')]
            assert len(matches)==1, f'Expected single route_detail.json, got {len(matches)}'
            data=json.loads(z.read(matches[0]))
    result={int(item['ROUTE']['ID']):item for item in data['data'] if int(item['ROUTE']['ID']) in ROUTES}
    assert set(result)==set(ROUTES), f'Unexpected route IDs: missing={set(ROUTES)-set(result)}'
    return result


def first_gps(location: dict) -> tuple[float,float]:
    """Match SITME frontend marker rule: location_id.COORDINATES[0]."""
    coords=location.get('COORDINATES') or []
    if not coords: raise ValueError(f'Missing location coordinates: {location.get("ID")}')
    lat=float(coords[0]['lat']);lon=float(coords[0]['lng'])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError(f'Coordinates outside valid EPSG:4326 range for {location.get("ID")}')
    return lat,lon


def km(a: tuple[float,float], b: tuple[float,float]) -> float:
    lat1,lon1=map(math.radians,a);lat2,lon2=map(math.radians,b)
    h=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 12742*math.asin(min(1, math.sqrt(h)))


def stop_id(source: str) -> str:
    return f'SITME_{source}'


def rgb(source: str) -> str:
    value=(source or '').lstrip('#')
    return value.upper() if re.fullmatch('[0-9A-Fa-f]{6}',value) else ''


def create(snapshot: Path, candidates_path: Path, visits_path: Path, out: Path) -> dict:
    routes=load_routes(snapshot)
    candidates=read_csv(candidates_path);visits=read_csv(visits_path)
    assert len(candidates)==528 and len(visits)==950, (len(candidates),len(visits))
    by_candidate={v['candidate_stop_id']:v for v in candidates}
    assert len(by_candidate)==len(candidates)
    assert all(all(not ids.issubset(set(v.get('source_location_ids','').split(';'))) for ids in DISTINCT) for v in candidates), 'Opposite directional stops incorrectly merged'

    locations={};geometry=[];route_records=[];points_by_route={};station_detail_index={}
    for rid in sorted(ROUTES):
        r=routes[rid];meta=r['ROUTE']
        assert len(r['DETAIL'])>=len(r['STATIONS'])>0
        rows=sorted(r['DETAIL'],key=lambda x:int(x['ORDER']))
        assert [int(x['ORDER']) for x in rows]==list(range(1,len(rows)+1)),f'Geometry order gaps in {rid}'
        points=[];distance=0.0
        for i,detail in enumerate(rows,1):
            p=first_gps(detail['location_id'])
            if points:distance+=km(points[-1],p)
            points.append(p)
            geometry.append({'shape_id':f'SITME_SHAPE_{rid}', 'shape_pt_lat':f'{p[0]:.8f}',
                             'shape_pt_lon':f'{p[1]:.8f}', 'shape_pt_sequence':i,
                             'shape_dist_traveled':f'{distance:.5f}'})
        points_by_route[rid]=points
        station_detail_index[rid]={str(d['ID']):d for d in rows if int(d.get('IS_CHECKPOINT') or 0)==1}
        desc=(meta.get('DESCRIPTION') or '').strip()
        if desc.lower().startswith(('ruta pretroncal','ruta petroncal','ruta alimentadora')):
            desc=''
        route_records.append({'route_id':f'SITME_ROUTE_{rid}', 'agency_id':'SITME',
                              'route_short_name':ROUTES[rid], 'route_long_name':desc,
                              'route_type':3, 'route_color':rgb(meta.get('COLOR','')),
                              'route_text_color':rgb(meta.get('TEXT_COLOR',''))})
        for item in r['STATIONS']:
            source=str(item['LOCATION_ID']); loc=item['location_id']
            if source in locations:
                assert locations[source]['NAME']==loc['NAME'], f'Conflicting location name {source}'
            else: locations[source]=loc
    assert len(locations)==531, len(locations)
    assert len(geometry)==10699, len(geometry)

    stop_rows=[];alias_rows=[]
    for canonical in sorted(by_candidate,key=int):
        candidate=by_candidate[canonical]
        origins=set(candidate['source_location_ids'].split(';'))
        assert origins and canonical in origins,canonical
        assert {ALIASES.get(source,source) for source in origins}=={canonical}, canonical
        loc=locations[canonical]
        lat,lon=first_gps(loc)
        stop_rows.append({'stop_id':stop_id(canonical), 'stop_name':loc['NAME'],
                          'stop_lat':f'{lat:.8f}', 'stop_lon':f'{lon:.8f}', 'location_type':0})
        for source in sorted(origins,key=int):
            alias_rows.append({'source_location_id':source,'gtfs_stop_id':stop_id(canonical),
                               'source_name':locations[source]['NAME'],
                               'canonical_location_id':canonical,
                               'identity_origin':'user_confirmed_same_physical_stop' if source!=canonical else 'original_sitme_location'})
    assert len(stop_rows)==528 and len(alias_rows)==531

    sequence_rows=[];visit_groups=defaultdict(list)
    for v in visits:
        rid=int(v['api_route_id']);source=v['source_location_id'];canonical=v['candidate_stop_id']
        if rid not in routes or canonical not in by_candidate:
            raise ValueError(f'Unmatched route/stop in visit: {rid} {canonical}')
        if ALIASES.get(source,source)!=canonical:raise ValueError(f'Unexpected alias {source}->{canonical}')
        d=station_detail_index[rid].get(str(v['detail_record_id']))
        if d is None or str(d['LOCATION_ID'])!=source or str(d['ORDER'])!=v['detail_order']:
            raise ValueError(f'Visit disagrees with original SITME DETAIL row: {rid} {source}')
        visit_groups[rid].append(v)
    assert len(visits)==950 and set(visit_groups)==set(ROUTES)
    for rid in sorted(ROUTES):
        by_order=sorted(visit_groups[rid],key=lambda x:int(x['detail_order']))
        orders=[int(x['detail_order']) for x in by_order]
        assert len(orders)==len(set(orders)),f'Duplicate DETAIL order: {rid}'
        expected=sorted([int(x['ORDER']) for x in routes[rid]['STATIONS']])
        assert orders==expected,f'STATIONS sequence differs for {rid}'
        for seq,v in enumerate(by_order,1):
            sequence_rows.append({'route_id':f'SITME_ROUTE_{rid}', 'route_short_name':ROUTES[rid],
                                  'stop_sequence':seq,'stop_id':stop_id(v['candidate_stop_id']),
                                  'shape_id':f'SITME_SHAPE_{rid}',
                                  'shape_pt_sequence':v['detail_order'],
                                  'source_location_id':v['source_location_id'],
                                  'detail_record_id':v['detail_record_id'],
                                  'source_stop_name':v['source_stop_name']})
    assert len(sequence_rows)==950

    gtfs=out/'gtfs_base'; audit=out/'source_audit'
    write_csv(gtfs/'agency.txt',['agency_id','agency_name','agency_url','agency_timezone'],
              [{'agency_id':'SITME','agency_name':'ENTE GESTOR METROLINEA',
                'agency_url':'https://sitme.metrolinea.gov.co/rutas','agency_timezone':'America/Bogota'}])
    write_csv(gtfs/'stops.txt',['stop_id','stop_name','stop_lat','stop_lon','location_type'],stop_rows)
    write_csv(gtfs/'routes.txt',['route_id','agency_id','route_short_name','route_long_name','route_type','route_color','route_text_color'],route_records)
    write_csv(gtfs/'shapes.txt',['shape_id','shape_pt_lat','shape_pt_lon','shape_pt_sequence','shape_dist_traveled'],geometry)
    write_csv(audit/'route_stop_sequences.csv',list(sequence_rows[0]),sequence_rows)
    write_csv(audit/'location_id_to_gtfs_stop_id.csv',list(alias_rows[0]),alias_rows)
    summary={
      'source':'SITME 2026-11-08 immutable route detail snapshot',
      'scope':'12 selected complementary routes only; PTB/PTN not included',
      'external_osm_used':False,'routes':len(route_records),'stops':len(stop_rows),
      'original_location_ids':len(locations),'stop_visits':len(sequence_rows),
      'shape_points':len(geometry),
      'coordinate_method':'official SITME frontend marker convention: first coordinate of location_id.COORDINATES',
      'stop_identity_aliases':ALIASES,
      'distinct_stop_pairs':[sorted(x,key=int) for x in DISTINCT],
      'limitations':[
        'Stop coordinates are SITME geofence vertices, not guaranteed exact platform positions',
        'These four GTFS base tables do not form a complete GTFS feed: trips, stop_times and service calendars are not generated',
        'RD27/RD15 is kept as one combined route geometry; unresolved official Carrera 27 vs API Carrera 33/32 mismatch',
        'P18 and AN3 direction patterns are not separately inferred from the route geometry',
        'All SITME STATIONS visits are retained in the supplied sequence; no per-stop boarding permissions asserted',
      ],
    }
    (audit/'build_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'README.md').write_text(
      '# SITME-only GTFS foundations\n\n'
      'This package uses **only SITME official route, stop and geometry API content** from the archived 2026-11-08 snapshot. No OSM match or external map routing is required.\n\n'
      'The `gtfs_base/` directory contains correctly structured GTFS *base tables* (`agency.txt`, `routes.txt`, `stops.txt`, `shapes.txt`). '
      '**This is not a complete GTFS feed and must not be published as one**: trip departure times, per-trip stop times and calendar/service assignments are still needed.\n\n'
      'The `source_audit/route_stop_sequences.csv` maps every SITME `STATIONS` occurrence to its order in its source route and to the canonical GTFS stop ID. '
      'Repeated visits are intentional, and two opposite-direction pairs remain separate.\n\n'
      'Coordinates follow the actual SITME webpage convention of using `location_id.COORDINATES[0]` as marker positions, '
      'not a geofence centroid; these are official site-provided GPS values but **may not be precise boarding-platform GPS**. '
      'No automatic roadside adjustment is made.\n\n'
      'Known exception: RD27/RD15 API path differs from its historically documented outbound corridor; keep open for operational review.\n',
      encoding='utf-8')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',required=True,type=Path)
    p.add_argument('--candidates',required=True,type=Path)
    p.add_argument('--visits',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    result=create(a.snapshot,a.candidates,a.visits,a.output)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()