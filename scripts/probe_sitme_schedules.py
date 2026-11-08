#!/usr/bin/env python3
"""Probe whether SITME provides schedules on selected future service dates."""
import datetime as dt
import json
import pathlib
import urllib.error
import urllib.request

BASE = "https://apisitme.metrolinea.gov.co"
CLIENT = 195
DATES = ["2026-11-09", "2026-11-10", "2026-11-14", "2026-11-15", "2026-11-16"]
FIELDS = ("ROUTE_SCHEDULLE", "ROUTE_SCHEDULLE_NOVELTY", "ROUTE_DISPATCHS")


def main():
    output = pathlib.Path("data/sitme/schedule-probe-2026-11")
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for date in DATES:
        dt.date.fromisoformat(date)
        url = f"{BASE}/route/detail/{CLIENT}/{date}"
        row = {"date": date, "weekday": dt.date.fromisoformat(date).strftime("%A"), "endpoint": url}
        try:
            request = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "ColombiaTransit-GTFS-research/1.0",
            })
            with urllib.request.urlopen(request, timeout=90) as response:
                payload = json.load(response)
            records = payload if isinstance(payload, list) else payload.get("data")
            if not isinstance(records, list):
                raise ValueError("Unexpected response shape: expected route list")
            row["status"] = "ok"
            row["route_count"] = len(records)
            row["fields"] = {}
            for field in FIELDS:
                present = [item for item in records if field in item]
                nonempty = [item for item in present if item.get(field)]
                row["fields"][field] = {
                    "present_routes": len(present),
                    "nonempty_routes": len(nonempty),
                    "total_entries": sum(len(item[field]) if isinstance(item[field], list) else 1 for item in nonempty),
                    "nonempty_route_ids": [
                        str((item.get("ROUTE") or {}).get("ID") or "") for item in nonempty
                    ],
                }
            print(f"{date}: {len(records)} routes; " + ", ".join(
                f"{field}={row['fields'][field]['nonempty_routes']}/{len(records)}"
                for field in FIELDS
            ))
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError, json.JSONDecodeError) as exc:
            row["status"] = "error"
            row["error"] = str(exc)
            print(f"WARNING {date}: {exc}")
        results.append(row)
    (output / "report.json").write_text(
        json.dumps({"client_id": CLIENT, "results": results}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = ["# SITME future-date schedule probe", "", "No GTFS timetable assumptions are made from empty fields.", "",
             "| Date | Routes | ROUTE_SCHEDULLE | ROUTE_SCHEDULLE_NOVELTY | ROUTE_DISPATCHS | Status |",
             "|---|---:|---:|---:|---:|---|"]
    for r in results:
        fields = r.get("fields", {})
        counts = [str(fields[f]["nonempty_routes"]) if f in fields else "—" for f in FIELDS]
        lines.append(f"| {r['date']} | {r.get('route_count', '—')} | " +
                     " | ".join(counts) + f" | {r['status']} |")
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if any(r["status"] != "ok" for r in results):
        raise SystemExit("One or more dates could not be checked; see artifact for details")


if __name__ == "__main__":
    main()
