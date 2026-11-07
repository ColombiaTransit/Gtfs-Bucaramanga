#!/usr/bin/env python3
"""Export historic Metrolínea ArcGIS road/corridor polylines for research, not GTFS."""
import argparse
import collections
import json
import urllib.parse
import urllib.request
from pathlib import Path

URL = "https://services6.arcgis.com/KmKGWMjOsgTLFBpe/ArcGIS/rest/services/Rutas_Metrolinea/FeatureServer/0/query"

def fetch(params):
    url = URL + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ColombiaTransit-GTFS-research/1.0"}), timeout=90) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=Path("data/raw/arcgis_metrolinea_corridors.geojson"))
    ap.add_argument("--report", type=Path, default=Path("data/reports/arcgis_metrolinea_inventory.json"))
    args = ap.parse_args()
    count = fetch({"where": "1=1", "returnCountOnly": "true", "f": "json"})["count"]
    features = []
    offset = 0
    while offset < count:
        page = fetch({"where": "1=1", "outFields": "*", "returnGeometry": "true",
                      "outSR": 4326, "resultOffset": offset, "resultRecordCount": 1000,
                      "orderByFields": "FID ASC", "f": "geojson"})
        chunk = page.get("features", [])
        if not chunk:
            raise RuntimeError(f"Empty ArcGIS page at offset {offset}, expected {count}")
        features.extend(chunk)
        offset += len(chunk)
    if len(features) != count:
        raise RuntimeError(f"Count mismatch: expected {count}, received {len(features)}")
    summary = {"source_url": URL.rsplit("/query", 1)[0],
               "classification": "historical infrastructure; not validated GTFS shapes",
               "source_last_edit": "2017-06-14 (ArcGIS metadata)",
               "feature_count": count,
               "geometry_types": dict(collections.Counter(
                   (f.get("geometry") or {}).get("type") for f in features)),
               "field_value_counts": {
                   key: dict(collections.Counter(str(f.get("properties", {}).get(key)) for f in features).most_common(100))
                   for key in ("TIPO", "NOMBRE", "METROLINEA", "NOM_CORRED")
               }}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False), encoding="utf-8")
    args.report.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exported {count} historical features to {args.output}")

if __name__ == "__main__":
    main()
