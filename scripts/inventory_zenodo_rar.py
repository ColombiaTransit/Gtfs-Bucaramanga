#!/usr/bin/env python3
"""Inventory safely extracted Metrolínea Zenodo RAR contents; no GTFS assumptions."""
import argparse
import csv
import json
import sqlite3
from collections import Counter
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    root = args.root.resolve()
    files = []
    gpkg_layers = []
    gpkg_column_details = []
    station_records = []
    xlsx_sheets = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        suffix = path.suffix.lower()
        files.append({"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "extension": suffix})
        if suffix == ".gpkg":
            try:
                con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
                try:
                    for table, kind, identifier, srs_id in con.execute("SELECT table_name, data_type, identifier, srs_id FROM gpkg_contents"):
                        gpkg_layers.append({"file": path.relative_to(root).as_posix(), "table": table, "type": kind, "identifier": identifier, "srs_id": srs_id})
                        if table.replace("_", "").isalnum():
                            cols = [row[1] for row in con.execute('PRAGMA table_info("' + table.replace('"', '""') + '")')]
                            safe = '"' + table.replace('"', '""') + '"'
                            row_count = con.execute("SELECT COUNT(*) FROM " + safe).fetchone()[0]
                            non_geom = [c for c in cols if c.lower() not in ("geom", "geometry", "shape")]
                            preview_cols = non_geom[:12]
                            sample = []
                            if preview_cols:
                                sql_cols = ", ".join('"' + c.replace('"', '""') + '"' for c in preview_cols)
                                for record in con.execute("SELECT " + sql_cols + " FROM " + safe + " LIMIT 8"):
                                    sample.append(dict(zip(preview_cols, [str(v)[:150] if v is not None else None for v in record])))
                            gpkg_column_details.append({"file": path.relative_to(root).as_posix(), "table": table, "rows": row_count, "columns": cols, "sample": sample})
                            if table.lower() == "coordenadasmetrolinea":
                                for row in con.execute("SELECT fid, MUNICIPIO, NOMBRE, TIPO, LATITUD, LONGITUD, \"FOTOS (CANT)\", OPERATIVA, TERMINADA FROM " + safe + " ORDER BY fid"):
                                    station_records.append(dict(zip(("fid", "municipio", "nombre", "tipo", "latitud", "longitud", "fotos_cant", "operativa", "terminada"), row)))
                finally:
                    con.close()
            except (sqlite3.Error, OSError) as exc:
                gpkg_layers.append({"file": path.relative_to(root).as_posix(), "error": str(exc)})
        if suffix == ".xlsx":
            try:
                import openpyxl
                wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
                try:
                    for sheet in wb:
                        header = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
                        xlsx_sheets.append({"file": path.relative_to(root).as_posix(), "sheet": sheet.title,
                                            "rows": sheet.max_row, "columns": sheet.max_column,
                                            "header": [str(x) if x is not None else "" for x in header],
                                            "sample": [[str(v)[:150] if v is not None else None for v in row] for row in list(sheet.iter_rows(min_row=2, max_row=min(sheet.max_row or 1, 9), values_only=True))]})
                finally:
                    wb.close()
            except Exception as exc:
                xlsx_sheets.append({"file": path.relative_to(root).as_posix(), "error": str(exc)})
    if station_records:
        csv_path = args.output.parent / "zenodo_metrolinea_stations.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(station_records[0]))
            writer.writeheader()
            writer.writerows(station_records)
        print("Exported", len(station_records), "station records to", csv_path)
    report = {"source": "https://zenodo.org/records/23147409",
              "classification": "research infrastructure; operational status unverified",
              "file_count": len(files), "extensions": dict(Counter(f["extension"] for f in files)),
              "files": files, "gpkg_layers": gpkg_layers, "gpkg_column_details": gpkg_column_details, "station_records": station_records, "station_operational_counts": dict(Counter(str(x["operativa"]) for x in station_records)), "xlsx_sheets": xlsx_sheets}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"files": files, "gpkg_column_details": gpkg_column_details, "xlsx_sheets": xlsx_sheets}, ensure_ascii=False, indent=2)[:30000])

if __name__ == "__main__":
    main()
