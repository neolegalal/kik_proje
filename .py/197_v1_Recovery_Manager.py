# -*- coding: utf-8 -*-
r"""
197 v1 - Recovery Manager
NeoLegal Production Platform v2.0

Amaç:
- Production sırasında oluşabilecek yarım/kırık/şüpheli çıktıları tespit etmek.
- DB, export, report ve production_state klasörlerini sağlık açısından taramak.
- Otomatik silme/düzeltme yapmadan önce güvenli recovery planı üretmek.
- Bu v1 sürümü "read-only" çalışır; veri değiştirmez.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\197_v1_Recovery_Manager.py"
"""

import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
REPORT_DIR = BASE_DIR / "raporlar"
STATE_DIR = BASE_DIR / "production_state"
EXPORT_DIRS = [
    BASE_DIR / "exports",
    BASE_DIR / "export",
    BASE_DIR / "web_export",
    BASE_DIR / "rag_export",
    BASE_DIR / "ciktilar",
]
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def safe_read(path: Path, limit_chars=20000):
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")[:limit_chars]
        except Exception:
            pass
    return ""


def safe_json(path: Path):
    try:
        return json.loads(safe_read(path, limit_chars=5_000_000))
    except Exception:
        return None


def discover_db():
    candidates = []
    for p in BASE_DIR.rglob("*.db"):
        if "kik" in p.name.lower():
            candidates.append(p)

    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if not candidates:
        return {
            "status": "FAIL",
            "path": None,
            "table": None,
            "count": 0,
            "message": "KİK DB bulunamadı."
        }

    db_path = candidates[0]

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        tables = [x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

        table = None
        for t in ("hukuki_kartlar", "kararlar", "kik_kararlari", "cards", "legal_cards"):
            if t in tables:
                table = t
                break

        if not table and tables:
            table = tables[0]

        if not table:
            conn.close()
            return {
                "status": "FAIL",
                "path": str(db_path),
                "table": None,
                "count": 0,
                "message": "DB var ancak tablo bulunamadı."
            }

        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()

        return {
            "status": "PASS" if count > 0 else "WARNING",
            "path": str(db_path),
            "table": table,
            "count": count,
            "message": f"DB bulundu. Tablo={table}, kayıt={count}"
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "path": str(db_path),
            "table": None,
            "count": 0,
            "message": f"DB okunamadı: {e}"
        }


def scan_json_integrity(folder: Path):
    result = {
        "folder": str(folder),
        "exists": folder.exists(),
        "json_total": 0,
        "json_valid": 0,
        "json_invalid": 0,
        "invalid_files": [],
    }

    if not folder.exists():
        return result

    files = list(folder.glob("*.json"))
    result["json_total"] = len(files)

    for f in files:
        data = safe_json(f)
        if data is None:
            result["json_invalid"] += 1
            result["invalid_files"].append(str(f))
        else:
            result["json_valid"] += 1

    return result


def scan_state_runs():
    result = {
        "state_dir_exists": STATE_DIR.exists(),
        "running_markers": [],
        "failed_markers": [],
        "resume_markers": [],
        "latest_states": [],
    }

    if not STATE_DIR.exists():
        return result

    all_files = sorted(STATE_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)

    for f in all_files[:50]:
        result["latest_states"].append(str(f))

    for f in all_files:
        name = f.name.lower()
        text = safe_read(f, limit_chars=8000).lower() if f.is_file() else ""

        if "running" in name or '"running"' in text or "status" in text and "running" in text:
            result["running_markers"].append(str(f))

        if "fail" in name or "error" in name or "traceback" in text or '"fail"' in text:
            result["failed_markers"].append(str(f))

        if "resume" in name or "resume" in text:
            result["resume_markers"].append(str(f))

    return result


def scan_reports():
    result = {
        "report_dir_exists": REPORT_DIR.exists(),
        "txt_total": 0,
        "suspect_reports": [],
        "latest_reports": [],
    }

    if not REPORT_DIR.exists():
        return result

    txts = sorted(REPORT_DIR.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    result["txt_total"] = len(txts)
    result["latest_reports"] = [str(p) for p in txts[:30]]

    suspect_tokens = [
        "traceback",
        "exception",
        "critical",
        "not certified",
        "dynamic not certified",
        "fail",
        "hata",
    ]

    for f in txts:
        text = safe_read(f, limit_chars=15000).lower()
        if any(tok in text for tok in suspect_tokens):
            result["suspect_reports"].append(str(f))

    return result


def scan_exports():
    result = {
        "export_dirs": [],
        "total_files": 0,
        "empty_files": [],
        "small_files": [],
        "invalid_json_exports": [],
    }

    for folder in EXPORT_DIRS:
        info = {
            "path": str(folder),
            "exists": folder.exists(),
            "files": 0,
        }

        if folder.exists():
            files = [p for p in folder.rglob("*") if p.is_file()]
            info["files"] = len(files)
            result["total_files"] += len(files)

            for f in files:
                try:
                    size = f.stat().st_size
                except Exception:
                    size = 0

                if size == 0:
                    result["empty_files"].append(str(f))
                elif size < 20:
                    result["small_files"].append(str(f))

                if f.suffix.lower() == ".json" and safe_json(f) is None:
                    result["invalid_json_exports"].append(str(f))

        result["export_dirs"].append(info)

    return result


def build_recovery_plan(payload):
    plan = []
    severity = "LOW"

    if payload["db"]["status"] == "FAIL":
        severity = "CRITICAL"
        plan.append({
            "priority": 1,
            "area": "DB",
            "action": "DB yolu ve tablo yapısı kontrol edilmeli. Production'a devam edilmemeli.",
            "auto_fix": False
        })

    if payload["state_scan"]["failed_markers"]:
        severity = "HIGH" if severity != "CRITICAL" else severity
        plan.append({
            "priority": 2,
            "area": "STATE",
            "action": "Failed/error state dosyaları incelenmeli; gerekiyorsa ilgili RUN_ID resume veya rollback planına alınmalı.",
            "auto_fix": False,
            "items": payload["state_scan"]["failed_markers"][:20]
        })

    if payload["state_scan"]["running_markers"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        plan.append({
            "priority": 3,
            "area": "STATE",
            "action": "Eski running marker dosyaları varsa stale run olabilir. Son runtime ile karşılaştırılmalı.",
            "auto_fix": False,
            "items": payload["state_scan"]["running_markers"][:20]
        })

    invalid_json_total = (
        payload["state_json_integrity"]["json_invalid"]
        + payload["report_json_integrity"]["json_invalid"]
    )

    if invalid_json_total > 0:
        severity = "HIGH" if severity in ("LOW", "MEDIUM") else severity
        plan.append({
            "priority": 4,
            "area": "JSON",
            "action": "Bozuk JSON dosyaları ayrılmalı veya yeniden üretilmeli.",
            "auto_fix": False,
            "count": invalid_json_total
        })

    if payload["export_scan"]["empty_files"] or payload["export_scan"]["invalid_json_exports"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        plan.append({
            "priority": 5,
            "area": "EXPORT",
            "action": "Boş veya bozuk export dosyaları yeniden export edilmelidir.",
            "auto_fix": False,
            "empty_count": len(payload["export_scan"]["empty_files"]),
            "invalid_json_count": len(payload["export_scan"]["invalid_json_exports"])
        })

    if payload["disk_free_gb"] < 50:
        severity = "HIGH" if severity != "CRITICAL" else severity
        plan.append({
            "priority": 6,
            "area": "DISK",
            "action": "Disk alanı 50 GB altına düşmüş. Production durdurulmalı ve temizlik yapılmalı.",
            "auto_fix": False
        })

    if not plan:
        plan.append({
            "priority": 0,
            "area": "GENERAL",
            "action": "Kritik recovery ihtiyacı tespit edilmedi. Production'a devam edilebilir.",
            "auto_fix": False
        })

    return {
        "severity": severity,
        "items": sorted(plan, key=lambda x: x["priority"])
    }


def evaluate(payload):
    score = 100
    errors = []
    warnings = []

    if payload["db"]["status"] == "FAIL":
        score -= 35
        errors.append("DB kritik hata verdi.")
    elif payload["db"]["status"] == "WARNING":
        score -= 10
        warnings.append("DB warning verdi.")

    if payload["state_json_integrity"]["json_invalid"] > 0:
        score -= min(25, payload["state_json_integrity"]["json_invalid"] * 5)
        errors.append("production_state içinde bozuk JSON var.")

    if payload["report_json_integrity"]["json_invalid"] > 0:
        score -= min(10, payload["report_json_integrity"]["json_invalid"] * 2)
        warnings.append("raporlar içinde bozuk JSON var.")

    if payload["state_scan"]["failed_markers"]:
        score -= min(20, len(payload["state_scan"]["failed_markers"]) * 2)
        warnings.append("Failed/error marker tespit edildi.")

    if payload["export_scan"]["empty_files"]:
        score -= min(10, len(payload["export_scan"]["empty_files"]))
        warnings.append("Boş export dosyası tespit edildi.")

    if payload["export_scan"]["invalid_json_exports"]:
        score -= min(15, len(payload["export_scan"]["invalid_json_exports"]) * 3)
        warnings.append("Bozuk JSON export tespit edildi.")

    if payload["disk_free_gb"] < 50:
        score -= 20
        errors.append("Disk alanı yetersiz.")

    score = max(0, min(100, score))

    if errors:
        decision = "RECOVERY REQUIRED"
    elif score >= 90:
        decision = "RECOVERY CLEAN"
    elif score >= 75:
        decision = "RECOVERY REVIEW"
    else:
        decision = "RECOVERY REQUIRED"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings
    }


def write_outputs(payload):
    json_path = STATE_DIR / f"197_v1_recovery_manager_state_{NOW}.json"
    txt_path = REPORT_DIR / f"197_v1_recovery_manager_raporu_{NOW}.txt"

    payload["recovery_plan"] = build_recovery_plan(payload)
    payload["result"] = evaluate(payload)

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("197 v1 RECOVERY MANAGER")
    lines.append("=" * 80)
    lines.append(f"Tarih                : {payload['created_at']}")
    lines.append(f"Score                : {payload['result']['score']} / 100")
    lines.append(f"Decision             : {payload['result']['decision']}")
    lines.append(f"Recovery Severity    : {payload['recovery_plan']['severity']}")
    lines.append(f"Disk Free            : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("DB")
    lines.append("-" * 80)
    lines.append(f"DB Status            : {payload['db']['status']}")
    lines.append(f"DB Path              : {payload['db'].get('path')}")
    lines.append(f"DB Table             : {payload['db'].get('table')}")
    lines.append(f"DB Count             : {payload['db'].get('count')}")
    lines.append(f"DB Message           : {payload['db'].get('message')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("JSON INTEGRITY")
    lines.append("-" * 80)
    lines.append(f"State JSON Total     : {payload['state_json_integrity']['json_total']}")
    lines.append(f"State JSON Invalid   : {payload['state_json_integrity']['json_invalid']}")
    lines.append(f"Report JSON Total    : {payload['report_json_integrity']['json_total']}")
    lines.append(f"Report JSON Invalid  : {payload['report_json_integrity']['json_invalid']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("STATE SCAN")
    lines.append("-" * 80)
    lines.append(f"Running Markers      : {len(payload['state_scan']['running_markers'])}")
    lines.append(f"Failed Markers       : {len(payload['state_scan']['failed_markers'])}")
    lines.append(f"Resume Markers       : {len(payload['state_scan']['resume_markers'])}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("EXPORT SCAN")
    lines.append("-" * 80)
    lines.append(f"Export Total Files   : {payload['export_scan']['total_files']}")
    lines.append(f"Empty Files          : {len(payload['export_scan']['empty_files'])}")
    lines.append(f"Small Files          : {len(payload['export_scan']['small_files'])}")
    lines.append(f"Invalid JSON Exports : {len(payload['export_scan']['invalid_json_exports'])}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("RECOVERY PLAN")
    lines.append("-" * 80)
    for item in payload["recovery_plan"]["items"]:
        lines.append(f"[P{item['priority']}] {item['area']} - {item['action']}")
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
    lines.append("NOT:")
    lines.append("197 v1 read-only çalışır. Hiçbir dosya silmez/değiştirmez.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def main():
    ensure_dirs()

    payload = {
        "module": "197 v1 Recovery Manager",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "disk_free_gb": disk_free_gb(),
        "db": discover_db(),
        "state_json_integrity": scan_json_integrity(STATE_DIR),
        "report_json_integrity": scan_json_integrity(REPORT_DIR),
        "state_scan": scan_state_runs(),
        "report_scan": scan_reports(),
        "export_scan": scan_exports(),
    }

    json_path, txt_path = write_outputs(payload)
    result = payload["result"]

    print("=" * 80)
    print("197 v1 RECOVERY MANAGER TAMAMLANDI")
    print("=" * 80)
    print(f"Score             : {result['score']} / 100")
    print(f"Decision          : {result['decision']}")
    print(f"Recovery Severity : {payload['recovery_plan']['severity']}")
    print(f"Errors            : {len(result['errors'])}")
    print(f"Warnings          : {len(result['warnings'])}")
    print(f"DB Status         : {payload['db']['status']}")
    print(f"DB Count          : {payload['db'].get('count')}")
    print(f"Disk Free         : {payload['disk_free_gb']} GB")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
