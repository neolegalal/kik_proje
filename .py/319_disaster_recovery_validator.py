# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"
SUMMARY_DIR = STATE / "platform_summary"
AUDIT_DIR = STATE / "production_readiness" / '319_disaster_recovery_validator'
MODULE_ID = '319'
MODULE_NAME = 'Disaster Recovery Validator'
VERSION = 'v2.26'
TAG = 'v2.26-disaster-recovery-validator'
MUST_HAVE = ['210', '195', '185']
PATTERNS = ['recovery', 'resume', 'rollback', 'self_healing', 'runtime']

def now_stamp(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def safe_read(path):
    path = Path(path)
    if not path.exists(): return ""
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try: return path.read_text(encoding=enc, errors="ignore")
        except Exception: pass
    return ""
def safe_json(path):
    try: return json.loads(safe_read(path))
    except Exception: return None
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def find_py_by_id(module_id): return list(PY.glob(str(module_id) + "*.py"))
def find_state_by_patterns(patterns):
    hits = []
    if not STATE.exists(): return hits
    for item in STATE.glob("**/*"):
        if not item.is_file(): continue
        low = str(item).lower()
        if any(p.lower() in low for p in patterns):
            hits.append(item)
            if len(hits) >= 50: break
    return hits
def audit_files():
    rows = []
    for module_id in MUST_HAVE:
        hits = find_py_by_id(module_id)
        rows.append({"id": module_id, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
    found = sum(1 for row in rows if row["found"])
    total = len(rows)
    score = round((found / total) * 100, 2) if total else 100
    status = "PASS" if score >= 80 else "WARN" if score >= 60 else "FAIL"
    return {"score": score, "found": found, "total": total, "items": rows, "status": status}
def audit_state():
    hits = find_state_by_patterns(PATTERNS)
    score = 100 if len(hits) >= 5 else 85 if len(hits) >= 2 else 70 if len(hits) >= 1 else 50
    status = "PASS" if score >= 85 else "WARN" if score >= 70 else "FAIL"
    return {"score": score, "match_count": len(hits), "sample": [str(x) for x in hits[:10]], "status": status}
def audit_summaries():
    summaries = []
    if SUMMARY_DIR.exists():
        for item in SUMMARY_DIR.glob("*_production_summary.json"):
            data = safe_json(item)
            if data: summaries.append({"path": str(item), "decision": data.get("final_decision"), "score": data.get("production_score")})
    failed = sum(1 for s in summaries if s.get("decision") == "FAIL")
    passed = sum(1 for s in summaries if s.get("decision") == "PASS")
    score = 100 - min(60, failed * 15)
    status = "PASS" if failed == 0 and passed > 0 else "WARN"
    return {"score": score, "summary_count": len(summaries), "pass": passed, "fail": failed, "status": status}
def create_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    release_path = RELEASES / 'v2.26-disaster-recovery-validator.md'
    release_path.write_text("# " + VERSION + " – " + MODULE_NAME + "\n\nProduction readiness program kapsamında eklendi.\n", encoding="utf-8")
    entry = "# " + VERSION + " – " + MODULE_NAME + "\n\n**Git Tag:** `" + TAG + "`\n\n---\n"
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if VERSION + " – " + MODULE_NAME not in old: CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else: CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| " + VERSION + " | " + MODULE_NAME + " | PASS/WARN |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt: README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([f.name for f in RELEASES.glob("*.md") if f.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + f + " |" for f in files]), encoding="utf-8")
    return release_path
def calculate(audits):
    scores = [v["score"] for v in audits.values()]
    avg = round(sum(scores)/len(scores), 2) if scores else 0
    has_fail = any(v["status"] == "FAIL" for v in audits.values())
    warn = sum(1 for v in audits.values() if v["status"] == "WARN")
    if has_fail: decision, ready = "FAIL", "NO"
    elif avg >= 90: decision, ready = "PASS", "YES"
    elif avg >= 75: decision, ready = "WARN", "LIMITED"
    else: decision, ready = "FAIL", "NO"
    return {"score": avg, "decision": decision, "ready": ready, "warnings": warn}
def main():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    release_path = create_docs()
    audits = {"files": audit_files(), "state": audit_state(), "summaries": audit_summaries()}
    final = calculate(audits)
    ts = now_stamp()
    state_path = AUDIT_DIR / (MODULE_ID + "_disaster_recovery_validator_audit_" + ts + ".json")
    report_path = REPORTS / (MODULE_ID + "_disaster_recovery_validator_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "version": VERSION, "tag": TAG, "audits": audits, "final": final, "release_path": str(release_path)}
    write_json(state_path, payload)
    lines = ["="*80, MODULE_ID + " " + MODULE_NAME.upper(), "="*80, "Production Readiness Score : " + str(final["score"]) + " / 100", "FINAL DECISION             : " + str(final["decision"]), "Production Ready           : " + str(final["ready"]), "Warnings                   : " + str(final["warnings"]), "", "Audit Scores:"]
    for key, val in audits.items(): lines.append("- " + key + " : " + str(val["score"]) + " / 100 [" + val["status"] + "]")
    lines += ["", "Files:", str(state_path), str(report_path), str(release_path), "", "="*80]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(1 if final["decision"] == "FAIL" else 0)
if __name__ == "__main__": main()
