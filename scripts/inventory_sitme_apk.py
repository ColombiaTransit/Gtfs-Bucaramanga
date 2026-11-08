#!/usr/bin/env python3
"""Static-only inventory of an independently obtained SITME APK. No requests to app APIs."""
import argparse, hashlib, json, re, subprocess, zipfile
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED = "com.metgroupsas.siumetrolinea"
PATTERNS = {
    "route": r"(?i)route|ruta|itinerar|recorrido|linea|línea",
    "stop": r"(?i)stop|parada|station|estacion|estación",
    "schedule": r"(?i)frequency|frecuencia|horario|schedule|departure|salida|headway",
    "api": r"(?i)api|endpoint|baseurl|graphql|retrofit|dio",
}
URL = re.compile(r"https?://[^\s\x00\x22\x27<>]{5,250}")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apk",required=True)
    ap.add_argument("--output",default="data/reports/sitme_apk_static_inventory.json")
    args=ap.parse_args()
    apk=Path(args.apk)
    data=apk.read_bytes()
    if not zipfile.is_zipfile(apk):
        raise SystemExit("Not an APK/ZIP; refuse analysis")
    aapt=subprocess.run(["aapt","dump","badging",str(apk)],capture_output=True,text=True)
    if aapt.returncode:
        raise SystemExit("aapt could not identify APK package: "+aapt.stderr[:500])
    match=re.search(r"package: name='([^']+)'",aapt.stdout)
    package=match.group(1) if match else None
    if package!=EXPECTED:
        raise SystemExit(f"Package mismatch: expected {EXPECTED}, found {package!r}")
    with zipfile.ZipFile(apk) as z:
        names=z.namelist()
        dex=[n for n in names if re.fullmatch(r"classes\d*\.dex",n)]
        assets=[n for n in names if n.startswith(("assets/","res/raw/"))][:150]
        candidates=set()
        for n in dex+assets:
            if z.getinfo(n).file_size>35_000_000: continue
            blob=z.read(n)
            for url in URL.findall(blob.decode("latin1",errors="ignore")):
                url=url.rstrip(".,);]}")
                parsed=urlsplit(url)
                if parsed.scheme=="https" and parsed.hostname and not any(x in parsed.hostname for x in ("google.com","googleapis.com","facebook.com","w3.org")):
                    # Save host and path only; avoid tokens in URL query/fragment
                    candidates.add(parsed.scheme+"://"+parsed.netloc+parsed.path[:140])
    report={"package":package,"sha256":hashlib.sha256(data).hexdigest(),
            "apk_size_bytes":len(data),"dex_files":dex,"asset_sample":assets,
            "candidate_https_endpoints":sorted(candidates)[:100],
            "notes":["Static analysis only; URLs are code strings, not verified functioning APIs.",
                     "Query parameters, authorization tokens and personal data are not collected.",
                     "Do not interpret endpoints as public or authenticated without validation."]}
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Validated {package}; {len(dex)} DEX files; {len(candidates)} candidate URL strings; report {output}")
if __name__=="__main__":main()
