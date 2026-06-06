import json
import urllib.request
from cvss import CVSS3, CVSS4  # pip install cvss

def osv_query(vuln_id: str):
    req = urllib.request.Request(
        "https://api.osv.dev/v1/vulns/" + vuln_id,
        headers={"Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        # print(f"Error querying OSV for {vuln_id}: {e}")
        return None

def to_severity(score: float | None):
    if score is None:
        return "UNKNOWN"
    if score >= 9.0:
        return "CRITICAL"
    if score >= 7.0:
        return "HIGH"
    if score >= 4.0:
        return "MEDIUM"
    if score > 0.0:
        return "LOW"
    return "UNKNOWN"

def cvss_vector_to_score(vector: str) -> float | None:
    if not vector:
        return None
    try:
        if vector.startswith("CVSS:4.0/"):
            return float(CVSS4(vector).scores()[0])
        if vector.startswith("CVSS:3."):
            return float(CVSS3(vector).scores()[0])
        return None
    except Exception:
        return None

def pick_best_cvss(osv: dict) -> tuple[float | None, str | None, str | None]:
    best_v3 = (None, None, None)
    for s in (osv.get("severity") or []):
        stype = s.get("type")
        vector = s.get("score")
        score = cvss_vector_to_score(vector or "")
        if score is None:
            continue
        if stype == "CVSS_V4":
            return (score, stype, vector)
        if stype == "CVSS_V3" and best_v3[0] is None:
            best_v3 = (score, stype, vector)
    return best_v3

data = json.load(open("pip-audit-report.json", "r", encoding="utf-8"))

# CVE -> aliases(GHSA) マップを作る
cve_to_aliases: dict[str, list[str]] = {}
ids = set()
for pkg in data.get("dependencies", []):
    for v in pkg.get("vulns", []):
        vid = v.get("id")
        if not vid:
            continue
        ids.add(vid)
        cve_to_aliases.setdefault(vid, [])
        for a in (v.get("aliases") or []):
            cve_to_aliases[vid].append(a)

ids = sorted(ids)
print(f"Found {len(ids)} unique CVE IDs:")

for vid in ids:
    osv = osv_query(vid)

    used_id = vid
    if not osv:
        # CVEが404なら alias(GHSA) を順に試す
        for a in cve_to_aliases.get(vid, []):
            osv = osv_query(a)
            if osv:
                used_id = a
                break

    if not osv:
        print(vid, "UNKNOWN", None, "(no OSV entry via CVE or aliases)")
        continue

    score, stype, vector = pick_best_cvss(osv)
    print(vid, to_severity(score), score, stype, vector, f"(osv_id={used_id})")
