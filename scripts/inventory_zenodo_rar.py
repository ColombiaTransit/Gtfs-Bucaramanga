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
                                            "header": [str(x) if x is not None else "" for x in header]})
                finally:
                    wb.close()
            except Exception as exc:
                xlsx_sheets.append({"file": path.relative_to(root).as_posix(), "error": str(exc)})
    report = {"source": "https://zenodo.org/records/23147409",
              "classification": "research infrastructure; operational status unverified",
              "file_count": len(files), "extensions": dict(Counter(f["extension"] for f in files)),
              "files": files, "gpkg_layers": gpkg_layers, "xlsx_sheets": xlsx_sheets}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Inventoried {len(files)} files; {len(gpkg_layers)} GPKG layers; {len(xlsx_sheets)} XLSX sheets")

if __name__ == "__main__":
    main()
