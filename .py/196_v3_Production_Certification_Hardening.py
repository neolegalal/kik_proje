import os
import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
REPORT_DIR = BASE_DIR / "raporlar"
STATE_DIR = BASE_DIR / "production_state"
DOCS_DIR = BASE_DIR / "docs"

NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

CORE = {
    "181": "Production Controller",
    "192": "Resume Engine",
    "193": "Smart Resume Validation",
    "194": "Production Guardian",
    "195": "Runtime Monitor",
    "196": "Production Certification Suite",
}

PIPELINE = [
    "168", "188", "172", "175", "176", "177", "185",
    "178", "179", "180", "169", "170", "173",
    "182", "183", "184", "190"
]

OPTIONAL_DOCS = [
    DOCS_DIR / "architecture",
    DOCS_DIR / "decisions",
    DOCS_DIR / "runbooks",
    DOCS_DIR / "releases",
]

DB_CANDIDATE_NAMES = ["kik.db", "neolegal.db", "production.db"]
PREFERRED_TABLES = ["hukuki_kartlar", "kararlar", "kik_kararlari", "cards", "legal_cards"]


def ensure_dirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def safe_read(path: Path) -> str:
    for enc in ["utf-8", "utf-8-sig", "cp1254", "latin-1"]:
        try:
            return path.read_text(encoding=enc, errors="ignore")
        except Exception:
            continue
    return ""


def safe_json(path: Path):
    try:
        return json.loads(safe_read(path))
    except Exception:
        return None


def disk_check():
    usage = shutil.disk_usage(str(BASE_DIR))
    free_gb = round(usage.free / (1024 ** 3), 2)
    if free_gb >= 100:
        status = "PASS"
    elif free_gb >= 50:
        status = "WARNING"
    else:
        status = "FAIL"
    return {"free_gb": free_gb, "status": status, "min_required_gb": 50, "ideal_gb": 100}


def find_db_files():
    found = []
    for name in DB_CANDIDATE_NAMES:
        for p in BASE_DIR.rglob(name):
            found.append(p)
    found = list(set(found))
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


def inspect_db():
    db_files = find_db_files()
    if not db_files:
        return {"status": "FAIL", "path": None, "table": None, "cards": 0, "message": "DB bulunamadi."}

    best = None
    for db_path in db_files:
        try:
            conn = sqlite3.connect(str(db_path))
            cur = conn.cursor()
            tables = [x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
            selected = None
            for t in PREFERRED_TABLES:
                if t in tables:
                    selected = t
                    break
            if not selected and tables:
                selected = tables[0]
            count = 0
            if selected:
                count = cur.execute(f"SELECT COUNT(*) FROM {selected}").fetchone()[0]
            conn.close()
            candidate = {"path": str(db_path), "table": selected, "cards": count, "tables": tables}
            if best is None or candidate["cards"] > best["cards"]:
                best = candidate
        except Exception:
            continue

    if not best:
        return {"status": "FAIL", "path": str(db_files[0]), "table": None, "cards": 0, "message": "DB bulundu ancak okunamadi."}

    cards = best["cards"]
    if cards >= 10000:
        status = "PASS"
    elif cards > 0:
        status = "WARNING"
    else:
        status = "FAIL"

    return {
        "status": status,
        "path": best["path"],
        "table": best["table"],
        "cards": cards,
        "message": f"DB okundu. Tablo: {best['table']}, kayit: {cards}",
    }


def list_module_files(prefix: str):
    files = []
    for folder in [PY_DIR, REPORT_DIR, STATE_DIR]:
        if folder.exists():
            files.extend(folder.glob(f"{prefix}*"))
            files.extend(folder.glob(f"*{prefix}*"))
    files = list(set(files))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def normalize_status(value):
    if value is None:
        return None
    text = str(value).upper().strip()

    if any(x in text for x in ["NOT CERTIFIED", "FAIL", "FAILED", "FALSE", "HAYIR", "BLOCKED", "ERROR"]):
        if "ERRORS              : 0" in text or "ERRORS            : 0" in text:
            return None
        return "FAIL"

    if any(x in text for x in ["CONDITIONAL CERTIFIED", "WARNING", "WARN", "UYARI"]):
        return "WARNING"

    if any(x in text for x in ["CERTIFIED", "PASS", "READY", "FINISHED", "OK", "TRUE", "EVET", "TAMAMLANDI"]):
        return "PASS"

    return None


def extract_from_json(data):
    if not isinstance(data, dict):
        return None

    priority_keys = [
        "final_decision", "decision", "runtime_decision", "production_ready",
        "final_ready", "resume_status", "resume_safe", "status", "result"
    ]

    for key in priority_keys:
        if key in data:
            s = normalize_status(data.get(key))
            if s:
                return s
            if isinstance(data.get(key), dict):
                s = extract_from_json(data.get(key))
                if s:
                    return s

    for value in data.values():
        if isinstance(value, dict):
            s = extract_from_json(value)
            if s:
                return s
    return None


def extract_from_text(text: str):
    upper = text.upper()

    fail_tokens = [
        "TRACEBACK", "EXCEPTION", "FINAL DECISION        : NOT CERTIFIED",
        "DECISION            : FAIL", "RUNTIME DECISION     : FAIL",
        "BLOCK FAILURES      : 1", "BLOCK FAILURE"
    ]
    for token in fail_tokens:
        if token in upper:
            return "FAIL"

    pass_tokens = [
        "FINAL PASS", "PRODUCTION READY", "181 FINAL READY   : TRUE",
        "RESUME STATUS     : FINISHED", "RESUME SAFE", "BLOCK FAILURES    : 0",
        "ERRORS            : 0", "ERRORS              : 0", "TAMAMLANDI", "PASS"
    ]
    for token in pass_tokens:
        if token in upper:
            return "PASS"

    warning_tokens = ["WARNING", "UYARI", "CONDITIONAL"]
    for token in warning_tokens:
        if token in upper:
            return "WARNING"

    return "UNKNOWN"


def check_module(prefix: str, name: str = ""):
    files = list_module_files(prefix)
    if not files:
        return {"name": name, "status": "FAIL", "files_found": 0, "source": None, "message": "Modul dosyasi bulunamadi."}

    script_exists = any((f.parent == PY_DIR and f.suffix.lower() == ".py") for f in files)
    if not script_exists:
        # Some old modules may be report-only in test folders; do not hard-fail if reports exist.
        script_note = "Script bulunamadi, rapor/state uzerinden degerlendirildi."
    else:
        script_note = "Script bulundu."

    # Prefer newest json state/report.
    for f in files[:20]:
        if f.suffix.lower() == ".json":
            data = safe_json(f)
            s = extract_from_json(data)
            if s:
                return {"name": name, "status": s, "files_found": len(files), "source": str(f), "message": script_note}

    for f in files[:20]:
        if f.suffix.lower() in [".txt", ".log", ".md", ".json"]:
            s = extract_from_text(safe_read(f))
            if s != "UNKNOWN":
                return {"name": name, "status": s, "files_found": len(files), "source": str(f), "message": script_note}

    return {"name": name, "status": "UNKNOWN", "files_found": len(files), "source": str(files[0]), "message": script_note + " Net sonuc bulunamadi."}


def docs_check():
    result = {}
    for folder in OPTIONAL_DOCS:
        result[str(folder)] = "PASS" if folder.exists() else "WARNING"
    return result


def score(core, pipeline, db, disk, docs):
    value = 100
    errors = []
    warnings = []

    if disk["status"] == "FAIL":
        value -= 20
        errors.append("Disk alani kritik seviyede.")
    elif disk["status"] == "WARNING":
        value -= 5
        warnings.append("Disk alani ideal seviyenin altinda.")

    if db["status"] == "FAIL":
        value -= 25
        errors.append("DB kontrolu basarisiz.")
    elif db["status"] == "WARNING":
        value -= 5
        warnings.append("DB kart sayisi dusuk veya pilot seviyede.")

    for key, item in core.items():
        if item["status"] == "FAIL":
            value -= 10
            errors.append(f"Core FAIL: {key} {item['name']}")
        elif item["status"] == "UNKNOWN":
            value -= 3
            warnings.append(f"Core UNKNOWN: {key} {item['name']}")
        elif item["status"] == "WARNING":
            value -= 1
            warnings.append(f"Core WARNING: {key} {item['name']}")

    for key, item in pipeline.items():
        if item["status"] == "FAIL":
            value -= 3
            errors.append(f"Pipeline FAIL: {key}")
        elif item["status"] == "UNKNOWN":
            value -= 1
            warnings.append(f"Pipeline UNKNOWN: {key}")
        elif item["status"] == "WARNING":
            warnings.append(f"Pipeline WARNING: {key}")

    for folder, st in docs.items():
        if st != "PASS":
            warnings.append(f"Dokumantasyon klasoru eksik: {folder}")

    value = max(0, min(100, value))

    if errors:
        decision = "NOT CERTIFIED"
    elif value >= 90:
        decision = "CERTIFIED"
    elif value >= 75:
        decision = "CONDITIONAL CERTIFIED"
    else:
        decision = "NOT CERTIFIED"

    return {"score": value, "decision": decision, "errors": errors, "warnings": warnings}


def write_outputs(payload):
    json_path = STATE_DIR / f"196_v3_certification_hardening_state_{NOW}.json"
    txt_path = REPORT_DIR / f"196_v3_certification_hardening_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("196 v3 PRODUCTION CERTIFICATION HARDENING")
    lines.append("=" * 80)
    lines.append(f"Tarih                 : {payload['created_at']}")
    lines.append(f"Certification Score   : {payload['result']['score']} / 100")
    lines.append(f"Final Decision        : {payload['result']['decision']}")
    lines.append(f"Errors                : {len(payload['result']['errors'])}")
    lines.append(f"Warnings              : {len(payload['result']['warnings'])}")
    lines.append(f"Disk Free             : {payload['disk']['free_gb']} GB")
    lines.append(f"DB Status             : {payload['db']['status']}")
    lines.append(f"DB Path               : {payload['db']['path']}")
    lines.append(f"DB Table              : {payload['db'].get('table')}")
    lines.append(f"DB Cards              : {payload['db']['cards']}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("CORE PLATFORM")
    lines.append("-" * 80)
    for key, item in payload["core"].items():
        lines.append(f"{key} {item['name']:<32} : {item['status']:<8} | files={item['files_found']} | source={item['source']}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("PIPELINE")
    lines.append("-" * 80)
    for key, item in payload["pipeline"].items():
        lines.append(f"{key:<5} : {item['status']:<8} | files={item['files_found']} | source={item['source']}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)
    if payload["result"]["errors"]:
        lines.extend([f"- {x}" for x in payload["result"]["errors"]])
    else:
        lines.append("Errors: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)
    if payload["result"]["warnings"]:
        lines.extend([f"- {x}" for x in payload["result"]["warnings"]])
    else:
        lines.append("Warnings: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("SONUC")
    lines.append("-" * 80)
    if payload["result"]["decision"] == "CERTIFIED":
        lines.append("Platform v2.0 Stable adayligi icin uygundur.")
    elif payload["result"]["decision"] == "CONDITIONAL CERTIFIED":
        lines.append("Platform uretime yakin durumdadir. Warning alanlari giderildikten sonra v2.0 Stable etiketi onerilir.")
    else:
        lines.append("Platform henuz v2.0 Stable icin uygun degildir.")

    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def main():
    ensure_dirs()
    disk = disk_check()
    db = inspect_db()
    core = {k: check_module(k, v) for k, v in CORE.items()}
    pipeline = {k: check_module(k) for k in PIPELINE}
    docs = docs_check()
    result = score(core, pipeline, db, disk, docs)

    payload = {
        "module": "196 v3 Production Certification Hardening",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "disk": disk,
        "db": db,
        "docs": docs,
        "core": core,
        "pipeline": pipeline,
        "result": result,
    }

    json_path, txt_path = write_outputs(payload)

    print("=" * 80)
    print("196 v3 PRODUCTION CERTIFICATION HARDENING TAMAMLANDI")
    print("=" * 80)
    print(f"Certification Score : {result['score']} / 100")
    print(f"Final Decision      : {result['decision']}")
    print(f"Errors              : {len(result['errors'])}")
    print(f"Warnings            : {len(result['warnings'])}")
    print(f"Disk Free           : {disk['free_gb']} GB")
    print(f"DB Status           : {db['status']}")
    print(f"DB Path             : {db['path']}")
    print(f"DB Cards            : {db['cards']}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
