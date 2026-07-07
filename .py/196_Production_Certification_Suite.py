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
DB_PATH = BASE_DIR / "kik.db"

NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

REQUIRED_CORE = {
    "181": "Production Controller",
    "192": "Resume Engine",
    "193": "Smart Resume Validation",
    "194": "Production Guardian",
    "195": "Runtime Monitor",
}

REQUIRED_PIPELINE = [
    "168", "188", "172", "175", "176", "177", "185",
    "178", "179", "180", "169", "170", "173",
    "182", "183", "184", "190"
]

CERT_RULES = {
    "min_disk_gb": 50,
    "min_db_cards": 1,
    "max_errors": 0,
    "warning_allowed": True,
}


def ensure_dirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def disk_free_gb(path: Path) -> float:
    usage = shutil.disk_usage(str(path))
    return round(usage.free / (1024 ** 3), 2)


def find_latest_file(folder: Path, keyword: str):
    if not folder.exists():
        return None
    files = list(folder.glob(f"*{keyword}*"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def read_text_safe(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        try:
            return path.read_text(encoding="cp1254", errors="ignore")
        except Exception:
            return ""


def detect_status_from_text(text: str):
    upper = text.upper()

    errors = 0
    warnings = 0

    for line in upper.splitlines():
        if "ERROR" in line or "HATA" in line:
            if "ERRORS            : 0" in line:
                continue
            if "ERRORS" in line and ": 0" in line:
                continue
            errors += 1

        if "WARNING" in line or "UYARI" in line:
            warnings += 1

    if "FINAL PASS" in upper or "PASS" in upper or "READY   : TRUE" in upper or "PRODUCTION READY" in upper:
        status = "PASS"
    elif errors > 0:
        status = "FAIL"
    elif warnings > 0:
        status = "WARNING"
    else:
        status = "UNKNOWN"

    return status, errors, warnings


def check_file_presence(prefix: str):
    candidates = []
    for folder in [PY_DIR, REPORT_DIR, STATE_DIR]:
        if folder.exists():
            candidates.extend(folder.glob(f"{prefix}*"))
            candidates.extend(folder.glob(f"*{prefix}*"))

    unique = sorted(set(candidates), key=lambda p: str(p))
    return unique


def check_db():
    result = {
        "exists": DB_PATH.exists(),
        "path": str(DB_PATH),
        "cards": 0,
        "status": "FAIL",
        "message": ""
    }

    if not DB_PATH.exists():
        result["message"] = "kik.db bulunamadı."
        return result

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()

        tables = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        table_names = [t[0] for t in tables]

        if "hukuki_kartlar" not in table_names:
            result["message"] = "hukuki_kartlar tablosu bulunamadı."
            conn.close()
            return result

        count = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]
        conn.close()

        result["cards"] = count
        if count >= CERT_RULES["min_db_cards"]:
            result["status"] = "PASS"
            result["message"] = f"DB aktif. Toplam kart: {count}"
        else:
            result["status"] = "WARNING"
            result["message"] = f"DB var ancak kart sayısı düşük: {count}"

        return result

    except Exception as e:
        result["message"] = f"DB kontrol hatası: {e}"
        return result


def check_core_modules():
    results = {}

    for prefix, name in REQUIRED_CORE.items():
        files = check_file_presence(prefix)
        latest_report = find_latest_file(REPORT_DIR, prefix)
        latest_state = find_latest_file(STATE_DIR, prefix)

        text = ""
        if latest_report:
            text += read_text_safe(latest_report)
        if latest_state:
            text += "\n" + read_text_safe(latest_state)

        status, errors, warnings = detect_status_from_text(text)

        if not files:
            status = "FAIL"

        results[prefix] = {
            "name": name,
            "files_found": len(files),
            "latest_report": str(latest_report) if latest_report else None,
            "latest_state": str(latest_state) if latest_state else None,
            "status": status,
            "errors": errors,
            "warnings": warnings
        }

    return results


def check_pipeline_modules():
    results = {}

    for prefix in REQUIRED_PIPELINE:
        files = check_file_presence(prefix)
        latest_report = find_latest_file(REPORT_DIR, prefix)
        latest_state = find_latest_file(STATE_DIR, prefix)

        text = ""
        if latest_report:
            text += read_text_safe(latest_report)
        if latest_state:
            text += "\n" + read_text_safe(latest_state)

        status, errors, warnings = detect_status_from_text(text)

        if not files:
            status = "FAIL"

        results[prefix] = {
            "files_found": len(files),
            "latest_report": str(latest_report) if latest_report else None,
            "latest_state": str(latest_state) if latest_state else None,
            "status": status,
            "errors": errors,
            "warnings": warnings
        }

    return results


def calculate_score(core, pipeline, db_check, disk_check):
    score = 100
    errors = []
    warnings = []

    if not disk_check["pass"]:
        score -= 20
        errors.append("Disk alanı yetersiz.")

    if db_check["status"] == "FAIL":
        score -= 25
        errors.append("DB kontrolü başarısız.")
    elif db_check["status"] == "WARNING":
        score -= 5
        warnings.append("DB uyarı verdi.")

    for key, item in core.items():
        if item["status"] == "FAIL":
            score -= 12
            errors.append(f"Core modül başarısız: {key} {item['name']}")
        elif item["status"] == "WARNING":
            score -= 3
            warnings.append(f"Core modül warning: {key} {item['name']}")
        elif item["status"] == "UNKNOWN":
            score -= 5
            warnings.append(f"Core modül durumu belirsiz: {key} {item['name']}")

    for key, item in pipeline.items():
        if item["status"] == "FAIL":
            score -= 5
            errors.append(f"Pipeline modül başarısız: {key}")
        elif item["status"] == "WARNING":
            score -= 1
            warnings.append(f"Pipeline modül warning: {key}")
        elif item["status"] == "UNKNOWN":
            score -= 2
            warnings.append(f"Pipeline modül durumu belirsiz: {key}")

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


def write_reports(payload):
    json_path = STATE_DIR / f"196_production_certification_state_{NOW}.json"
    txt_path = REPORT_DIR / f"196_production_certification_raporu_{NOW}.txt"

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    lines = []
    lines.append("=" * 80)
    lines.append("196 PRODUCTION CERTIFICATION SUITE")
    lines.append("=" * 80)
    lines.append(f"Tarih                 : {payload['created_at']}")
    lines.append(f"Certification Score   : {payload['result']['score']} / 100")
    lines.append(f"Final Decision        : {payload['result']['decision']}")
    lines.append(f"Disk Free             : {payload['disk']['free_gb']} GB")
    lines.append(f"DB Status             : {payload['db']['status']}")
    lines.append(f"DB Cards              : {payload['db']['cards']}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("CORE PLATFORM")
    lines.append("-" * 80)

    for key, item in payload["core"].items():
        lines.append(
            f"{key} {item['name']:<30} : {item['status']} "
            f"| files={item['files_found']} | errors={item['errors']} | warnings={item['warnings']}"
        )

    lines.append("")
    lines.append("-" * 80)
    lines.append("PIPELINE")
    lines.append("-" * 80)

    for key, item in payload["pipeline"].items():
        lines.append(
            f"{key:<5} : {item['status']} "
            f"| files={item['files_found']} | errors={item['errors']} | warnings={item['warnings']}"
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
    lines.append("SONUÇ")
    lines.append("-" * 80)

    if payload["result"]["decision"] == "CERTIFIED":
        lines.append("Platform v2.0 Stable adaylığı için uygundur.")
    elif payload["result"]["decision"] == "CONDITIONAL CERTIFIED":
        lines.append("Platform üretime yakın durumdadır ancak warning alanları gözden geçirilmelidir.")
    else:
        lines.append("Platform henüz v2.0 Stable için uygun değildir.")

    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, txt_path


def main():
    ensure_dirs()

    free_gb = disk_free_gb(BASE_DIR)
    disk_check = {
        "free_gb": free_gb,
        "min_required_gb": CERT_RULES["min_disk_gb"],
        "pass": free_gb >= CERT_RULES["min_disk_gb"]
    }

    db_check = check_db()
    core = check_core_modules()
    pipeline = check_pipeline_modules()

    result = calculate_score(core, pipeline, db_check, disk_check)

    payload = {
        "module": "196 Production Certification Suite",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "disk": disk_check,
        "db": db_check,
        "core": core,
        "pipeline": pipeline,
        "result": result
    }

    json_path, txt_path = write_reports(payload)

    print("=" * 80)
    print("196 PRODUCTION CERTIFICATION SUITE TAMAMLANDI")
    print("=" * 80)
    print(f"Certification Score : {result['score']} / 100")
    print(f"Final Decision      : {result['decision']}")
    print(f"Errors              : {len(result['errors'])}")
    print(f"Warnings            : {len(result['warnings'])}")
    print(f"Disk Free           : {free_gb} GB")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()