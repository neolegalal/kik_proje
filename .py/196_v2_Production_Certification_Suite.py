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

NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

CORE = {
    "181": "Production Controller",
    "192": "Resume Engine",
    "193": "Smart Resume Validation",
    "194": "Production Guardian",
    "195": "Runtime Monitor",
}

PIPELINE = [
    "168", "188", "172", "175", "176", "177", "185",
    "178", "179", "180", "169", "170", "173",
    "182", "183", "184", "190"
]

DB_CANDIDATES = [
    BASE_DIR / "kik.db",
    BASE_DIR / "data" / "kik.db",
    BASE_DIR / "db" / "kik.db",
    BASE_DIR / "database" / "kik.db",
    BASE_DIR / "production_state" / "kik.db",
]


def ensure_dirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def safe_read(path: Path):
    for enc in ["utf-8", "utf-8-sig", "cp1254", "latin-1"]:
        try:
            return path.read_text(encoding=enc, errors="ignore")
        except Exception:
            pass
    return ""


def safe_json(path: Path):
    try:
        return json.loads(safe_read(path))
    except Exception:
        return None


def latest_files(prefix: str):
    files = []

    for folder in [PY_DIR, REPORT_DIR, STATE_DIR]:
        if folder.exists():
            files.extend(folder.glob(f"{prefix}*"))
            files.extend(folder.glob(f"*{prefix}*"))

    files = list(set(files))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def latest_report_or_state(prefix: str):
    candidates = []

    for folder in [REPORT_DIR, STATE_DIR]:
        if folder.exists():
            candidates.extend(folder.glob(f"{prefix}*"))
            candidates.extend(folder.glob(f"*{prefix}*"))

    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def disk_check():
    usage = shutil.disk_usage(str(BASE_DIR))
    free_gb = round(usage.free / (1024 ** 3), 2)

    return {
        "free_gb": free_gb,
        "status": "PASS" if free_gb >= 50 else "FAIL"
    }


def discover_db():
    found = []

    for candidate in DB_CANDIDATES:
        if candidate.exists():
            found.append(candidate)

    for candidate in BASE_DIR.rglob("*.db"):
        if "kik" in candidate.name.lower():
            found.append(candidate)

    found = list(set(found))
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if not found:
        return {
            "status": "FAIL",
            "path": None,
            "cards": 0,
            "message": "KİK veritabanı bulunamadı."
        }

    db_path = found[0]

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()

        tables = [
            x[0] for x in cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]

        preferred_tables = [
            "hukuki_kartlar",
            "kararlar",
            "kik_kararlari",
            "cards",
            "legal_cards"
        ]

        selected_table = None

        for t in preferred_tables:
            if t in tables:
                selected_table = t
                break

        if not selected_table and tables:
            selected_table = tables[0]

        if not selected_table:
            conn.close()
            return {
                "status": "FAIL",
                "path": str(db_path),
                "cards": 0,
                "message": "DB var ancak tablo bulunamadı."
            }

        count = cur.execute(f"SELECT COUNT(*) FROM {selected_table}").fetchone()[0]
        conn.close()

        return {
            "status": "PASS" if count > 0 else "WARNING",
            "path": str(db_path),
            "table": selected_table,
            "cards": count,
            "message": f"DB bulundu. Tablo: {selected_table}, kayıt: {count}"
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "path": str(db_path),
            "cards": 0,
            "message": f"DB okunamadı: {e}"
        }


def normalize_status(value):
    if value is None:
        return None

    text = str(value).upper()

    if any(x in text for x in ["CERTIFIED", "PASS", "READY", "FINISHED", "OK", "TRUE", "EVET"]):
        if "NOT CERTIFIED" in text:
            return "FAIL"
        return "PASS"

    if any(x in text for x in ["WARNING", "WARN", "UYARI"]):
        return "WARNING"

    if any(x in text for x in ["FAIL", "ERROR", "FALSE", "HAYIR", "BLOCK"]):
        return "FAIL"

    return None


def extract_status_from_json(data):
    if not isinstance(data, dict):
        return None

    keys = [
        "decision",
        "final_decision",
        "runtime_decision",
        "production_ready",
        "final_ready",
        "resume_status",
        "resume_safe",
        "status",
        "result",
    ]

    for key in keys:
        if key in data:
            status = normalize_status(data.get(key))
            if status:
                return status

    for value in data.values():
        if isinstance(value, dict):
            status = extract_status_from_json(value)
            if status:
                return status

    return None


def extract_status_from_text(text):
    upper = text.upper()

    strong_pass = [
        "FINAL PASS",
        "PRODUCTION READY   : TRUE",
        "181 FINAL READY   : TRUE",
        "RESUME STATUS     : FINISHED",
        "RESUME SAFE       : EVET",
        "BLOCK FAILURES    : 0",
        "ERRORS            : 0",
        "ERRORS              : 0",
        "TAMAMLANDI",
        "PASS"
    ]

    strong_warning = [
        "WARNING",
        "UYARI"
    ]

    strong_fail = [
        "FINAL DECISION        : NOT CERTIFIED",
        "DECISION              : FAIL",
        "RUNTIME DECISION      : FAIL",
        "BLOCK FAILURE",
        "TRACEBACK",
        "EXCEPTION"
    ]

    for token in strong_fail:
        if token in upper:
            return "FAIL"

    for token in strong_pass:
        if token in upper:
            return "PASS"

    for token in strong_warning:
        if token in upper:
            return "WARNING"

    return "UNKNOWN"


def check_module(prefix: str, name: str = ""):
    files = latest_files(prefix)
    latest = latest_report_or_state(prefix)

    if not files:
        return {
            "name": name,
            "status": "FAIL",
            "files_found": 0,
            "latest": None,
            "message": "Dosya bulunamadı."
        }

    status = "UNKNOWN"
    source = None

    for f in files[:10]:
        if f.suffix.lower() == ".json":
            data = safe_json(f)
            s = extract_status_from_json(data)
            if s:
                status = s
                source = str(f)
                break

    if status == "UNKNOWN" and latest:
        text = safe_read(latest)
        status = extract_status_from_text(text)
        source = str(latest)

    return {
        "name": name,
        "status": status,
        "files_found": len(files),
        "latest": source or (str(latest) if latest else None),
        "message": "OK" if status in ["PASS", "WARNING"] else "Kontrol gerekli."
    }


def score_all(core_results, pipeline_results, db, disk):
    score = 100
    errors = []
    warnings = []

    if disk["status"] != "PASS":
        score -= 20
        errors.append("Disk alanı yetersiz.")

    if db["status"] == "FAIL":
        score -= 25
        errors.append("DB kontrolü başarısız.")
    elif db["status"] == "WARNING":
        score -= 5
        warnings.append("DB var ancak kayıt sayısı düşük.")

    for key, item in core_results.items():
        if item["status"] == "FAIL":
            score -= 10
            errors.append(f"Core FAIL: {key} {item['name']}")
        elif item["status"] == "WARNING":
            score -= 2
            warnings.append(f"Core WARNING: {key} {item['name']}")
        elif item["status"] == "UNKNOWN":
            score -= 4
            warnings.append(f"Core UNKNOWN: {key} {item['name']}")

    for key, item in pipeline_results.items():
        if item["status"] == "FAIL":
            score -= 4
            errors.append(f"Pipeline FAIL: {key}")
        elif item["status"] == "WARNING":
            score -= 1
            warnings.append(f"Pipeline WARNING: {key}")
        elif item["status"] == "UNKNOWN":
            score -= 2
            warnings.append(f"Pipeline UNKNOWN: {key}")

    score = max(0, min(100, score))

    if errors:
        decision = "NOT CERTIFIED"
    elif score >= 90:
        decision = "CERTIFIED"
    elif score >= 75:
        decision = "CONDITIONAL CERTIFIED"
    else:
        decision = "NOT CERTIFIED"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings
    }


def write_report(payload):
    json_path = STATE_DIR / f"196_v2_production_certification_state_{NOW}.json"
    txt_path = REPORT_DIR / f"196_v2_production_certification_raporu_{NOW}.txt"

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    lines = []
    lines.append("=" * 80)
    lines.append("196 v2 PRODUCTION CERTIFICATION SUITE")
    lines.append("=" * 80)
    lines.append(f"Tarih                 : {payload['created_at']}")
    lines.append(f"Certification Score   : {payload['result']['score']} / 100")
    lines.append(f"Final Decision        : {payload['result']['decision']}")
    lines.append(f"Disk Free             : {payload['disk']['free_gb']} GB")
    lines.append(f"DB Status             : {payload['db']['status']}")
    lines.append(f"DB Path               : {payload['db'].get('path')}")
    lines.append(f"DB Cards              : {payload['db'].get('cards')}")
    lines.append(f"DB Message            : {payload['db'].get('message')}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("CORE PLATFORM")
    lines.append("-" * 80)

    for key, item in payload["core"].items():
        lines.append(
            f"{key} {item['name']:<30} : {item['status']} "
            f"| files={item['files_found']} | latest={item['latest']}"
        )

    lines.append("")
    lines.append("-" * 80)
    lines.append("PIPELINE")
    lines.append("-" * 80)

    for key, item in payload["pipeline"].items():
        lines.append(
            f"{key:<5} : {item['status']} "
            f"| files={item['files_found']} | latest={item['latest']}"
        )

    lines.append("")
    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)

    if payload["result"]["errors"]:
        for e in payload["result"]["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)

    if payload["result"]["warnings"]:
        for w in payload["result"]["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("SONUC")
    lines.append("-" * 80)

    if payload["result"]["decision"] == "CERTIFIED":
        lines.append("Platform v2.0 Stable adayligi icin uygundur.")
    elif payload["result"]["decision"] == "CONDITIONAL CERTIFIED":
        lines.append("Platform uretime yakin durumdadir. Warning alanlari gozden gecirilmelidir.")
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
    db = discover_db()

    core_results = {}
    for prefix, name in CORE.items():
        core_results[prefix] = check_module(prefix, name)

    pipeline_results = {}
    for prefix in PIPELINE:
        pipeline_results[prefix] = check_module(prefix)

    result = score_all(core_results, pipeline_results, db, disk)

    payload = {
        "module": "196 v2 Production Certification Suite",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "disk": disk,
        "db": db,
        "core": core_results,
        "pipeline": pipeline_results,
        "result": result
    }

    json_path, txt_path = write_report(payload)

    print("=" * 80)
    print("196 v2 PRODUCTION CERTIFICATION SUITE TAMAMLANDI")
    print("=" * 80)
    print(f"Certification Score : {result['score']} / 100")
    print(f"Final Decision      : {result['decision']}")
    print(f"Errors              : {len(result['errors'])}")
    print(f"Warnings            : {len(result['warnings'])}")
    print(f"Disk Free           : {disk['free_gb']} GB")
    print(f"DB Status           : {db['status']}")
    print(f"DB Path             : {db.get('path')}")
    print(f"DB Cards            : {db.get('cards')}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()