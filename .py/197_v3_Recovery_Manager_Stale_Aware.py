# -*- coding: utf-8 -*-
r"""
197 v3 - Recovery Manager with Stale Awareness
NeoLegal Production Platform v2.0

Amaç:
- 197 v1 Recovery Manager'ın fazla hassas değerlendirmesini iyileştirmek.
- production_state kayıtlarını active / stale / review olarak sınıflandırmak.
- Eski state dosyalarını kritik recovery hatası gibi değerlendirmemek.
- Read-only çalışır; dosya silmez, taşımaz, değiştirmez.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\197_v3_Recovery_Manager_Stale_Aware.py"
"""

import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

STALE_DAYS = 2
STALE_CUTOFF = datetime.now() - timedelta(days=STALE_DAYS)


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


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

    for f in folder.glob("*.json"):
        result["json_total"] += 1
        if safe_json(f) is None:
            result["json_invalid"] += 1
            result["invalid_files"].append(str(f))
        else:
            result["json_valid"] += 1

    return result


def classify_state_files():
    result = {
        "total_files": 0,
        "active": [],
        "stale": [],
        "review": [],
        "recent_failed": [],
        "recent_running": [],
        "stale_failed": [],
        "stale_running": [],
    }

    if not STATE_DIR.exists():
        return result

    files = sorted([p for p in STATE_DIR.glob("*") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    result["total_files"] = len(files)

    for f in files:
        try:
            modified = datetime.fromtimestamp(f.stat().st_mtime)
            is_stale = modified < STALE_CUTOFF
            name = f.name.lower()
            text = safe_read(f, limit_chars=12000).lower()

            has_running = "running" in name or "running" in text
            has_failed = (
                "fail" in name
                or "error" in name
                or "traceback" in text
                or '"fail"' in text
                or "exception" in text
            )

            rec = {
                "file": str(f),
                "modified": modified.strftime("%Y-%m-%d %H:%M:%S"),
                "stale": is_stale,
                "has_running": has_running,
                "has_failed": has_failed,
            }

            if is_stale:
                result["stale"].append(rec)
                if has_failed:
                    result["stale_failed"].append(rec)
                if has_running:
                    result["stale_running"].append(rec)
            else:
                if has_failed:
                    result["recent_failed"].append(rec)
                    result["review"].append(rec)
                elif has_running:
                    result["recent_running"].append(rec)
                    result["review"].append(rec)
                else:
                    result["active"].append(rec)

        except Exception:
            continue

    return result


def scan_exports():
    export_dirs = [
        BASE_DIR / "exports",
        BASE_DIR / "export",
        BASE_DIR / "web_export",
        BASE_DIR / "rag_export",
        BASE_DIR / "ciktilar",
    ]

    result = {
        "dirs": [],
        "total_files": 0,
        "empty_files": [],
        "small_files": [],
        "invalid_json_exports": [],
    }

    for folder in export_dirs:
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

        result["dirs"].append(info)

    return result


def build_recovery_plan(payload):
    plan = []
    severity = "LOW"

    if payload["db"]["status"] == "FAIL":
        severity = "CRITICAL"
        plan.append({
            "priority": 1,
            "area": "DB",
            "action": "DB okunamadı. Production'a devam edilmeden DB yolu ve tablo yapısı kontrol edilmeli.",
            "auto_fix": False,
        })

    state = payload["state_classification"]

    if state["recent_failed"]:
        severity = "HIGH" if severity != "CRITICAL" else severity
        plan.append({
            "priority": 2,
            "area": "STATE",
            "action": "Güncel failed/error state kayıtları incelenmeli.",
            "auto_fix": False,
            "count": len(state["recent_failed"]),
            "items": state["recent_failed"][:20],
        })

    if state["recent_running"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        plan.append({
            "priority": 3,
            "area": "STATE",
            "action": "Güncel running marker kayıtları var. Aktif üretim yoksa stale-run kabul edilmeden önce son runtime kontrol edilmeli.",
            "auto_fix": False,
            "count": len(state["recent_running"]),
            "items": state["recent_running"][:20],
        })

    if state["stale_failed"] or state["stale_running"]:
        plan.append({
            "priority": 4,
            "area": "STATE_ARCHIVE",
            "action": "Eski failed/running kayıtları tespit edildi. Bunlar kritik hata sayılmadı; istenirse ileride archive/cleanup modülüyle taşınabilir.",
            "auto_fix": False,
            "stale_failed_count": len(state["stale_failed"]),
            "stale_running_count": len(state["stale_running"]),
        })

    if payload["state_json_integrity"]["json_invalid"] > 0:
        severity = "HIGH" if severity in ("LOW", "MEDIUM") else severity
        plan.append({
            "priority": 5,
            "area": "JSON",
            "action": "production_state içinde bozuk JSON var. İlgili dosyalar quarantine planına alınmalı.",
            "auto_fix": False,
            "count": payload["state_json_integrity"]["json_invalid"],
        })

    export = payload["export_scan"]
    if export["empty_files"] or export["invalid_json_exports"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        plan.append({
            "priority": 6,
            "area": "EXPORT",
            "action": "Boş veya bozuk export dosyaları var. Export yeniden üretim planı hazırlanmalı.",
            "auto_fix": False,
            "empty_count": len(export["empty_files"]),
            "invalid_json_count": len(export["invalid_json_exports"]),
        })

    if payload["disk_free_gb"] < 50:
        severity = "HIGH" if severity != "CRITICAL" else severity
        plan.append({
            "priority": 7,
            "area": "DISK",
            "action": "Disk alanı düşük. Production durdurulup temizlik yapılmalı.",
            "auto_fix": False,
        })

    if not plan:
        plan.append({
            "priority": 0,
            "area": "GENERAL",
            "action": "Aktif recovery ihtiyacı yok. Production'a devam edilebilir.",
            "auto_fix": False,
        })

    return {
        "severity": severity,
        "items": sorted(plan, key=lambda x: x["priority"])
    }


def evaluate(payload):
    score = 100
    errors = []
    warnings = []

    db = payload["db"]
    state = payload["state_classification"]
    export = payload["export_scan"]

    if db["status"] == "FAIL":
        score -= 35
        errors.append("DB kritik hata verdi.")
    elif db["status"] == "WARNING":
        score -= 5
        warnings.append("DB warning verdi.")

    if payload["state_json_integrity"]["json_invalid"] > 0:
        penalty = min(25, payload["state_json_integrity"]["json_invalid"] * 5)
        score -= penalty
        errors.append("production_state içinde bozuk JSON var.")

    # Sadece güncel failed/running kritik sayılır. Stale kayıtlar bilgi olarak tutulur.
    if state["recent_failed"]:
        score -= min(20, len(state["recent_failed"]) * 5)
        warnings.append("Güncel failed/error state kayıtları var.")

    if state["recent_running"]:
        score -= min(10, len(state["recent_running"]) * 2)
        warnings.append("Güncel running marker kayıtları var.")

    if state["stale_failed"] or state["stale_running"]:
        warnings.append("Eski failed/running kayıtları arşiv adayı olarak sınıflandırıldı; kritik sayılmadı.")

    if export["empty_files"]:
        score -= min(10, len(export["empty_files"]))
        warnings.append("Boş export dosyası tespit edildi.")

    if export["invalid_json_exports"]:
        score -= min(15, len(export["invalid_json_exports"]) * 3)
        warnings.append("Bozuk JSON export tespit edildi.")

    if payload["disk_free_gb"] < 50:
        score -= 20
        errors.append("Disk alanı yetersiz.")

    score = max(0, min(100, score))

    if errors:
        decision = "RECOVERY REQUIRED"
    elif score >= 95:
        decision = "RECOVERY CLEAN"
    elif score >= 85:
        decision = "RECOVERY LOW REVIEW"
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
    json_path = STATE_DIR / f"197_v3_recovery_manager_state_{NOW}.json"
    txt_path = REPORT_DIR / f"197_v3_recovery_manager_raporu_{NOW}.txt"

    payload["recovery_plan"] = build_recovery_plan(payload)
    payload["result"] = evaluate(payload)

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    st = payload["state_classification"]
    ex = payload["export_scan"]

    lines = []
    lines.append("=" * 80)
    lines.append("197 v3 RECOVERY MANAGER - STALE AWARE")
    lines.append("=" * 80)
    lines.append(f"Tarih                  : {payload['created_at']}")
    lines.append(f"Score                  : {payload['result']['score']} / 100")
    lines.append(f"Decision               : {payload['result']['decision']}")
    lines.append(f"Recovery Severity      : {payload['recovery_plan']['severity']}")
    lines.append(f"Stale Cutoff Days      : {STALE_DAYS}")
    lines.append(f"Disk Free              : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("DB")
    lines.append("-" * 80)
    lines.append(f"DB Status              : {payload['db']['status']}")
    lines.append(f"DB Path                : {payload['db'].get('path')}")
    lines.append(f"DB Table               : {payload['db'].get('table')}")
    lines.append(f"DB Count               : {payload['db'].get('count')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("STATE CLASSIFICATION")
    lines.append("-" * 80)
    lines.append(f"Total State Files      : {st['total_files']}")
    lines.append(f"Active                 : {len(st['active'])}")
    lines.append(f"Stale                  : {len(st['stale'])}")
    lines.append(f"Review                 : {len(st['review'])}")
    lines.append(f"Recent Failed          : {len(st['recent_failed'])}")
    lines.append(f"Recent Running         : {len(st['recent_running'])}")
    lines.append(f"Stale Failed           : {len(st['stale_failed'])}")
    lines.append(f"Stale Running          : {len(st['stale_running'])}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("JSON INTEGRITY")
    lines.append("-" * 80)
    lines.append(f"State JSON Total       : {payload['state_json_integrity']['json_total']}")
    lines.append(f"State JSON Invalid     : {payload['state_json_integrity']['json_invalid']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("EXPORT SCAN")
    lines.append("-" * 80)
    lines.append(f"Export Total Files     : {ex['total_files']}")
    lines.append(f"Empty Files            : {len(ex['empty_files'])}")
    lines.append(f"Small Files            : {len(ex['small_files'])}")
    lines.append(f"Invalid JSON Exports   : {len(ex['invalid_json_exports'])}")
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
    if st["review"]:
        lines.append("-" * 80)
        lines.append("REVIEW FILES")
        lines.append("-" * 80)
        for item in st["review"][:30]:
            lines.append(f"{item['modified']} | failed={item['has_failed']} | running={item['has_running']} | {item['file']}")
        lines.append("")
    lines.append("NOT:")
    lines.append("197 v3 read-only çalışır. Dosya silmez, taşımaz, değiştirmez.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def main():
    ensure_dirs()

    payload = {
        "module": "197 v3 Recovery Manager Stale Aware",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "disk_free_gb": disk_free_gb(),
        "db": discover_db(),
        "state_json_integrity": scan_json_integrity(STATE_DIR),
        "state_classification": classify_state_files(),
        "export_scan": scan_exports(),
    }

    json_path, txt_path = write_outputs(payload)
    result = payload["result"]

    print("=" * 80)
    print("197 v3 RECOVERY MANAGER - STALE AWARE TAMAMLANDI")
    print("=" * 80)
    print(f"Score             : {result['score']} / 100")
    print(f"Decision          : {result['decision']}")
    print(f"Recovery Severity : {payload['recovery_plan']['severity']}")
    print(f"Errors            : {len(result['errors'])}")
    print(f"Warnings          : {len(result['warnings'])}")
    print(f"DB Status         : {payload['db']['status']}")
    print(f"DB Count          : {payload['db'].get('count')}")
    print(f"State Review      : {len(payload['state_classification']['review'])}")
    print(f"Recent Failed     : {len(payload['state_classification']['recent_failed'])}")
    print(f"Recent Running    : {len(payload['state_classification']['recent_running'])}")
    print(f"Stale Files       : {len(payload['state_classification']['stale'])}")
    print(f"Disk Free         : {payload['disk_free_gb']} GB")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
