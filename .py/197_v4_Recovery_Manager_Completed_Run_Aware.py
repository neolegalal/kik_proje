# -*- coding: utf-8 -*-
r"""
197 v4 - Recovery Manager Completed-Run Aware
NeoLegal Production Platform v2.0

Amaç:
- 197 v3'te review çıkan state dosyalarını daha akıllı sınıflandırmak.
- Başarılı tamamlanan 196B, 192, 193, 195 gibi state dosyalarını false-positive olarak ayırmak.
- 196 v1/v3 gibi NOT CERTIFIED sonuçlarını "historical certification failure" olarak sınıflandırmak.
- Read-only çalışır; dosya silmez, taşımaz, değiştirmez.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\197_v4_Recovery_Manager_Completed_Run_Aware.py"
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


def safe_read(path: Path, limit_chars=200000):
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


def text_has_any(text, tokens):
    return any(t in text for t in tokens)


def classify_semantic_status(file_path: Path, data, text: str):
    name = file_path.name.lower()
    t = text.lower()

    # Başarılı dynamic certification kayıtları
    if "196b_v2_controlled_dynamic_state" in name:
        if "dynamic certified" in t and '"errors": []' in t:
            return "completed_success", "196B dynamic certification completed successfully"

    # Resume state: FINISHED veya OK ise running kelimesi geçse bile tamamlanmış kabul edilir.
    if "192_resume_state" in name:
        if text_has_any(t, ["finished", '"status": "finished"', '"resume_status": "finished"', "resume ok", "final pass"]):
            return "completed_success", "Resume state finished"
        if text_has_any(t, ['"final_ready": true', '"completed": true']):
            return "completed_success", "Resume state completed"

    # Runtime monitor: final ready true / finished / errors 0 ise tamamlanmış
    if "195_runtime_monitor_state" in name:
        if text_has_any(t, ['"final_ready": true', "resume status", "finished", '"errors": 0', '"errors": []']):
            return "completed_success", "Runtime monitor completed"

    # Smart Resume Validation: warning olabilir ama fail değilse review değildir.
    if "193_smart_resume_validation_state" in name:
        if text_has_any(t, ["warning", "resume safe", "evet", '"errors": 0', '"errors": []']):
            return "completed_warning", "Smart resume validation completed with warning"

    # Recovery manager'ın kendi state'i, içinde running kelimesi geçebilir.
    if "197_v" in name and "recovery_manager_state" in name:
        if text_has_any(t, ["recovery clean", "recovery review", "recovery low review", '"errors": []']):
            return "completed_warning", "Recovery manager completed"

    # 196 v1/v3 not certified: bu gerçek production failure değil, tarihsel sertifikasyon denemesidir.
    if name.startswith("196") and "certification" in name:
        if "not certified" in t or '"decision": "not certified"' in t:
            return "historical_certification_failure", "Old certification attempt failed; not active production failure"
        if "conditional certified" in t or "certified" in t:
            return "completed_warning", "Certification completed"

    # Genel başarı sinyalleri
    if text_has_any(t, [
        "dynamic certified",
        "certified",
        "final pass",
        "pass",
        "finished",
        "tamamlandi",
        "tamamlandı",
        '"errors": []',
        '"errors": 0',
        '"returncode": 0',
    ]):
        # NOT CERTIFIED özel durumunu yukarıda yakalamadığımızsa fail kabul edelim.
        if "not certified" in t:
            return "historical_certification_failure", "Not certified but historical/non-production"
        return "completed_success", "Generic completed state"

    # Gerçek hata sinyalleri
    if text_has_any(t, ["traceback", "exception", '"status": "fail"', '"decision": "fail"', "critical"]):
        return "active_failure", "Active failure tokens found"

    # Running var ama completed sinyali yok.
    if "running" in name or "running" in t:
        return "active_running_review", "Running token without completion signal"

    if "fail" in name or "error" in name or '"fail"' in t:
        return "active_failure", "Failure token without historical/completed signal"

    return "normal", "No risk token"


def classify_state_files():
    result = {
        "total_files": 0,
        "active_normal": [],
        "stale": [],
        "completed_success": [],
        "completed_warning": [],
        "historical_certification_failure": [],
        "active_failure": [],
        "active_running_review": [],
        "review": [],
    }

    if not STATE_DIR.exists():
        return result

    files = sorted([p for p in STATE_DIR.glob("*") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
    result["total_files"] = len(files)

    for f in files:
        try:
            modified = datetime.fromtimestamp(f.stat().st_mtime)
            is_stale = modified < STALE_CUTOFF
            text = safe_read(f)
            data = safe_json(f) if f.suffix.lower() == ".json" else None
            semantic_status, reason = classify_semantic_status(f, data, text)

            rec = {
                "file": str(f),
                "modified": modified.strftime("%Y-%m-%d %H:%M:%S"),
                "stale": is_stale,
                "semantic_status": semantic_status,
                "reason": reason,
            }

            if is_stale:
                result["stale"].append(rec)
                continue

            if semantic_status == "completed_success":
                result["completed_success"].append(rec)
            elif semantic_status == "completed_warning":
                result["completed_warning"].append(rec)
            elif semantic_status == "historical_certification_failure":
                result["historical_certification_failure"].append(rec)
            elif semantic_status == "active_failure":
                result["active_failure"].append(rec)
                result["review"].append(rec)
            elif semantic_status == "active_running_review":
                result["active_running_review"].append(rec)
                result["review"].append(rec)
            else:
                result["active_normal"].append(rec)

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
    st = payload["state_classification"]
    ex = payload["export_scan"]

    if payload["db"]["status"] == "FAIL":
        severity = "CRITICAL"
        plan.append({
            "priority": 1,
            "area": "DB",
            "action": "DB okunamadı. Production'a devam edilmemeli.",
            "auto_fix": False,
        })

    if payload["state_json_integrity"]["json_invalid"] > 0:
        severity = "HIGH" if severity != "CRITICAL" else severity
        plan.append({
            "priority": 2,
            "area": "JSON",
            "action": "production_state içinde bozuk JSON var. Quarantine planı gerekli.",
            "auto_fix": False,
            "count": payload["state_json_integrity"]["json_invalid"],
        })

    if st["active_failure"]:
        severity = "HIGH" if severity != "CRITICAL" else severity
        plan.append({
            "priority": 3,
            "area": "STATE",
            "action": "Aktif hata olabilecek state dosyaları incelenmeli.",
            "auto_fix": False,
            "count": len(st["active_failure"]),
            "items": st["active_failure"][:20],
        })

    if st["active_running_review"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        plan.append({
            "priority": 4,
            "area": "STATE",
            "action": "Tamamlanma sinyali bulunmayan güncel running state dosyaları incelenmeli.",
            "auto_fix": False,
            "count": len(st["active_running_review"]),
            "items": st["active_running_review"][:20],
        })

    if st["historical_certification_failure"]:
        plan.append({
            "priority": 5,
            "area": "CERTIFICATION_HISTORY",
            "action": "Eski başarısız sertifikasyon denemeleri tarihsel kayıt olarak sınıflandırıldı; aktif production hatası sayılmadı.",
            "auto_fix": False,
            "count": len(st["historical_certification_failure"]),
        })

    if st["stale"]:
        plan.append({
            "priority": 6,
            "area": "STATE_ARCHIVE",
            "action": "Eski state dosyaları arşiv adayıdır. v5 cleanup/quarantine modülünde taşınabilir.",
            "auto_fix": False,
            "count": len(st["stale"]),
        })

    if ex["empty_files"] or ex["invalid_json_exports"]:
        severity = "MEDIUM" if severity == "LOW" else severity
        plan.append({
            "priority": 7,
            "area": "EXPORT",
            "action": "Boş veya bozuk export dosyaları yeniden export planına alınmalı.",
            "auto_fix": False,
            "empty_count": len(ex["empty_files"]),
            "invalid_json_count": len(ex["invalid_json_exports"]),
        })

    if payload["disk_free_gb"] < 50:
        severity = "HIGH" if severity != "CRITICAL" else severity
        plan.append({
            "priority": 8,
            "area": "DISK",
            "action": "Disk alanı düşük. Production durdurulmalı.",
            "auto_fix": False,
        })

    if not plan:
        plan.append({
            "priority": 0,
            "area": "GENERAL",
            "action": "Aktif recovery ihtiyacı yok.",
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
    st = payload["state_classification"]
    ex = payload["export_scan"]

    if payload["db"]["status"] == "FAIL":
        score -= 35
        errors.append("DB kritik hata verdi.")
    elif payload["db"]["status"] == "WARNING":
        score -= 5
        warnings.append("DB warning verdi.")

    if payload["state_json_integrity"]["json_invalid"] > 0:
        score -= min(25, payload["state_json_integrity"]["json_invalid"] * 5)
        errors.append("production_state içinde bozuk JSON var.")

    if st["active_failure"]:
        score -= min(25, len(st["active_failure"]) * 8)
        warnings.append("Aktif failure olabilecek state dosyası var.")

    if st["active_running_review"]:
        score -= min(12, len(st["active_running_review"]) * 3)
        warnings.append("Tamamlanma sinyali bulunmayan running state dosyası var.")

    if st["historical_certification_failure"]:
        warnings.append("Eski başarısız sertifikasyon denemeleri tarihsel kayıt olarak ayrıldı.")

    if st["stale"]:
        warnings.append("Eski state dosyaları arşiv adayı olarak ayrıldı.")

    if ex["empty_files"]:
        score -= min(10, len(ex["empty_files"]))
        warnings.append("Boş export dosyası tespit edildi.")

    if ex["invalid_json_exports"]:
        score -= min(15, len(ex["invalid_json_exports"]) * 3)
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
    json_path = STATE_DIR / f"197_v4_recovery_manager_state_{NOW}.json"
    txt_path = REPORT_DIR / f"197_v4_recovery_manager_raporu_{NOW}.txt"

    payload["recovery_plan"] = build_recovery_plan(payload)
    payload["result"] = evaluate(payload)

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    st = payload["state_classification"]
    ex = payload["export_scan"]

    lines = []
    lines.append("=" * 80)
    lines.append("197 v4 RECOVERY MANAGER - COMPLETED RUN AWARE")
    lines.append("=" * 80)
    lines.append(f"Tarih                         : {payload['created_at']}")
    lines.append(f"Score                         : {payload['result']['score']} / 100")
    lines.append(f"Decision                      : {payload['result']['decision']}")
    lines.append(f"Recovery Severity             : {payload['recovery_plan']['severity']}")
    lines.append(f"Stale Cutoff Days             : {STALE_DAYS}")
    lines.append(f"Disk Free                     : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("DB")
    lines.append("-" * 80)
    lines.append(f"DB Status                     : {payload['db']['status']}")
    lines.append(f"DB Path                       : {payload['db'].get('path')}")
    lines.append(f"DB Table                      : {payload['db'].get('table')}")
    lines.append(f"DB Count                      : {payload['db'].get('count')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("STATE CLASSIFICATION")
    lines.append("-" * 80)
    lines.append(f"Total State Files             : {st['total_files']}")
    lines.append(f"Active Normal                 : {len(st['active_normal'])}")
    lines.append(f"Completed Success             : {len(st['completed_success'])}")
    lines.append(f"Completed Warning             : {len(st['completed_warning'])}")
    lines.append(f"Historical Cert Failures      : {len(st['historical_certification_failure'])}")
    lines.append(f"Active Failure                : {len(st['active_failure'])}")
    lines.append(f"Active Running Review         : {len(st['active_running_review'])}")
    lines.append(f"Review Total                  : {len(st['review'])}")
    lines.append(f"Stale                         : {len(st['stale'])}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("JSON / EXPORT")
    lines.append("-" * 80)
    lines.append(f"State JSON Total              : {payload['state_json_integrity']['json_total']}")
    lines.append(f"State JSON Invalid            : {payload['state_json_integrity']['json_invalid']}")
    lines.append(f"Export Total Files            : {ex['total_files']}")
    lines.append(f"Empty Export Files            : {len(ex['empty_files'])}")
    lines.append(f"Invalid JSON Exports          : {len(ex['invalid_json_exports'])}")
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

    if st["active_failure"] or st["active_running_review"]:
        lines.append("-" * 80)
        lines.append("ACTIVE REVIEW FILES")
        lines.append("-" * 80)
        for item in (st["active_failure"] + st["active_running_review"])[:30]:
            lines.append(f"{item['modified']} | {item['semantic_status']} | {item['reason']} | {item['file']}")
        lines.append("")

    lines.append("NOT:")
    lines.append("197 v4 read-only çalışır. Dosya silmez, taşımaz, değiştirmez.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def main():
    ensure_dirs()

    payload = {
        "module": "197 v4 Recovery Manager Completed Run Aware",
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
    st = payload["state_classification"]

    print("=" * 80)
    print("197 v4 RECOVERY MANAGER - COMPLETED RUN AWARE TAMAMLANDI")
    print("=" * 80)
    print(f"Score                    : {result['score']} / 100")
    print(f"Decision                 : {result['decision']}")
    print(f"Recovery Severity        : {payload['recovery_plan']['severity']}")
    print(f"Errors                   : {len(result['errors'])}")
    print(f"Warnings                 : {len(result['warnings'])}")
    print(f"DB Status                : {payload['db']['status']}")
    print(f"DB Count                 : {payload['db'].get('count')}")
    print(f"Completed Success        : {len(st['completed_success'])}")
    print(f"Completed Warning        : {len(st['completed_warning'])}")
    print(f"Historical Cert Failures : {len(st['historical_certification_failure'])}")
    print(f"Active Failure           : {len(st['active_failure'])}")
    print(f"Active Running Review    : {len(st['active_running_review'])}")
    print(f"Stale Files              : {len(st['stale'])}")
    print(f"Disk Free                : {payload['disk_free_gb']} GB")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
