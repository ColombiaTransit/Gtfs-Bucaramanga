#!/usr/bin/env python3
"""Read-only Socket.IO connection/authentication probe for SITME monitoring."""
import argparse, base64, collections, datetime, json, os, pathlib, time
from urllib.parse import quote
import re
import requests
import socketio

HOST = "https://api.voa.metgroupsas.com"
SOCKET_PATH = "socket.io"
NAMESPACE = "/monitoring-route-v2"
ROOM = "195"
# Expired historical JWT from publicly distributed SITME JavaScript.
# Use only for the requested compatibility test; never log token or full URL.
HISTORICAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijk0ZWMzY2JlNWMyMmZiYmYzODcyMWRhMzllNDUxZDE5Ojk3ZDA3ZjEyNzJhZGZkMDk3ZTg1ZmU3NzdkMGFmMTdjZGRmNTlmYjc3NTIxZTU0NDY5NDYxN2ZhN2VmZWRmYTNhMmFmZjM3MTcwMjg3NjNmYWI1MCIsImlhdCI6MTc2NDM1OTk0OSwiZXhwIjoxNzY0NDMxOTQ5fQ.mmIN6p408ue8vJumTjyDQOZTXjFQL9VsP6RDftG4uFxuEG0ee8Y9JM2178DuTh4C041TFgg2h-bP9Mo8bvKyEqjHMtLIeSbabcxgzVmBSOp90S_w7Rg3SzKgxCbrO_NKmuP2rsc4dVEeBgg-6Z47neRIElLR6SwB7Rtjl9pfwTbb2jaCW3M7HYwu0qgYPE-_morctVDlQmAEhXzt65WDpZUl6h2bJSMX0MGnJk1OgOy0FYbX9xtDX7MjlVq6Jlf33-Lm-7_sjo062cik2KtiNwBWe4LanvbWmHr4TxUPpuTynYpheQjD-59qrjosZA7kJsa9LJV-QUc5bRYqr6vznQzEmWOGIvKe9xJIisWomnCAvZiH7XIQpitf1HBFALxsIm_QfQoD_yUcXavGrYNOcyP-S1uVJQvd8byU4VlbgJfrRh0Z_ZRRDgM3eS91RlRdtYjFxMl3HgCBhue_Hg1yvOCZU6nMxjWuLv0km3qfXiMb32HKPzWd4dPjMDyayNetCywiLRZ1b6Z7I0_IIzkcnZnlAn5qOstV1S0_bRGlA-_VXBrYU-cqMopvdMgufFAYpPI9RK7wl7oPk_3_z0l4eBQPCFhrKX9py6wkfkt8VSwSYXVs-ZcSqeQvYqhbgSx_1ZfS7ooedKqnQLX7fRNrjCUsDViCxhZ9Sphnz8JTOxs"

def expiry(token):
    try:
        part = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
        return datetime.datetime.fromtimestamp(claims["exp"], datetime.timezone.utc).isoformat()
    except (ValueError, KeyError, IndexError):
        return None

def classify_error(value):
    """Return only safe diagnostics; never persist URLs, tokens or response bodies."""
    raw = str(value)
    status = re.search(r"\\b(?:HTTP(?:/\\d(?:\\.\\d)?)?\\s*|status(?: code)?[=: ]+)([1-5]\\d\\d)\\b", raw, re.I)
    return {
        "exception_type": type(value).__name__,
        "http_status": int(status.group(1)) if status else None,
        "likely_auth_failure": bool(re.search(r"\\b(401|403|unauthorized|forbidden)\\b", raw, re.I)),
        "likely_handshake_or_version_failure": bool(re.search(r"\\b(400|unsupported|protocol|handshake|invalid transport)\\b", raw, re.I)),
        "likely_network_failure": bool(re.search(r"timeout|timed out|name resolution|connection refused|dns", raw, re.I)),
    }

def handshake_probe(token, engineio_version):
    """Safe HTTP polling handshake: identify status and Engine.IO compatibility."""
    url = HOST + "/" + SOCKET_PATH + "/"
    try:
        response = requests.get(
            url,
            params={"EIO": str(engineio_version), "transport": "polling",
                    "Authorization": token},
            timeout=12, allow_redirects=False,
        )
        # Do not expose body or response URL; they might contain credentials.
        return {"engineio_version": engineio_version, "http_status": response.status_code,
                "response_is_engineio_open": response.text.startswith("0{"),
                "redirect": response.is_redirect}
    except requests.RequestException as exc:
        return {"engineio_version": engineio_version, "error": classify_error(exc)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seconds", type=int, default=40)
    p.add_argument("--room", default=ROOM)
    p.add_argument("--route-id", default="")
    args = p.parse_args()
    if not 5 <= args.seconds <= 120:
        p.error("seconds must be between 5 and 120")
    if not args.route_id:
        try:
            today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))).date().isoformat()
            response = requests.get(f"https://apisitme.metrolinea.gov.co/route/detail/195/{today}", timeout=30)
            response.raise_for_status()
            payload = response.json()
            routes = payload if isinstance(payload, list) else payload.get("data", [])
            candidates = [(str(row["ROUTE"]["ID"]), str(row["ROUTE"].get("CODE", "")))
                          for row in routes if isinstance(row, dict)
                          and isinstance(row.get("ROUTE"), dict) and row["ROUTE"].get("ID") is not None]
            if candidates:
                args.route_id, route_code = candidates[0]
                print("Selected SITME route:", route_code, "ID:", args.route_id)
            else:
                print("No route ID found; subscription skipped")
        except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
            print("SITME route lookup failed:", type(exc).__name__)
    token = os.getenv("SITME_MONITORING_TOKEN") or HISTORICAL_TOKEN
    report = {
        "tested_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "host": HOST, "socket_path": SOCKET_PATH, "namespace": NAMESPACE, "room": args.room,
        "token_source": "env" if os.getenv("SITME_MONITORING_TOKEN") else "historical_js",
        "token_expiry": expiry(token), "connected": False,
        "selected_route_id": args.route_id, "engineio_connected": False,
        "subscription_sent": False, "events": {}, "event_field_names": {},
        "error_type": None, "connect_error": False,
        "room_supplied": bool(args.room), "route_supplied": bool(args.route_id),
        "http_handshakes": [], "error_diagnostics": None, "socketio_connect_error_type": None,
    }
    for version in (4, 3):
        result = handshake_probe(token, version)
        report["http_handshakes"].append(result)
        print("Engine.IO", version, "default Socket.IO path HTTP status:", result.get("http_status"),
              "open packet:", result.get("response_is_engineio_open", False))
    counts = collections.Counter()
    client = socketio.Client(reconnection=False, logger=False, engineio_logger=False, request_timeout=12)
    @client.on("connect", namespace=NAMESPACE)
    def connect():
        report["connected"] = True
        print("Connected to Socket.IO namespace:", NAMESPACE)
        if args.room and args.route_id:
            client.emit("subscribeToMonitoringContraint", int(args.room) if args.room.isdigit() else args.room, namespace=NAMESPACE)
            report["subscription_sent"] = True
            print("Subscription sent")
    @client.on("connect_error", namespace=NAMESPACE)
    def connect_error(data):
        report["connect_error"] = True
        report["socketio_connect_error_type"] = type(data).__name__
        print("Socket.IO connect_error (details withheld)")
    @client.on("*", namespace=NAMESPACE)
    def any_event(event, *payload):
        counts[event] += 1
        if event not in report["event_field_names"]:
            obj = payload[0] if payload else None
            report["event_field_names"][event] = sorted(obj.keys())[:60] if isinstance(obj, dict) else []
        print("Event:", event)
    if args.route_id and args.room:
        @client.on(f"Route_monitoring_data_notify_{args.route_id}_{args.room}", namespace=NAMESPACE)
        def monitoring_event(payload):
            any_event("Route_monitoring_data_notify", payload)
    try:
        # Angular supplies Authorization as a Socket.IO query parameter.
        client.connect(HOST + NAMESPACE + "?Authorization=" + quote(token, safe=""),
                       socketio_path=SOCKET_PATH, namespaces=[NAMESPACE],
                       headers={"X-EngineIO-Version": "3"},
                       transports=["websocket"], wait_timeout=15)
        report["engineio_connected"] = client.eio.state == "connected"
        print("Engine.IO connected:", report["engineio_connected"])
        print("Namespace connected:", NAMESPACE in client.namespaces)
        time.sleep(args.seconds)
    except Exception as exc:
        # Avoid printing exception messages: some include URLs containing credentials.
        report["error_type"] = type(exc).__name__
        report["error_diagnostics"] = classify_error(exc)
        print("Connection/listen failed:", json.dumps(report["error_diagnostics"]))
    finally:
        if client.connected:
            client.disconnect()
        report["events"] = dict(counts)
        output = pathlib.Path("data/sitme/websocket-probe/report.json")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print("Report saved:", output)

if __name__ == "__main__":
    main()
