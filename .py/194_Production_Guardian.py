# -*- coding: utf-8 -*-
"""
194 - PRODUCTION GUARDIAN
NeoLegal / KİK Production Platform

Amaç:
- Büyük üretim başlamadan önce ortam güvenliği ve production hazırlığını kontrol eder.
- 181 v14/v15 gibi controller'lar öncesinde çalıştırılabilir.
- Hedef: 1000+ batch ve uzun süreli üretimlerden önce çevresel riskleri yakalamak.

Kontrol ettiği başlıklar:
1. Gerekli klasörler var mı?
2. Klasörler yazılabilir mi?
3. Disk boş alanı yeterli mi?
4. Kritik script dosyaları mevcut mu?
5. Resume / Smart Resume dosyaları mevcut mu?
6. DB dosyası mevcut mu?
7. Riskli secret dosyaları proje kökünde duruyor mu?
8. Son resume state okunabiliyor mu?
9. Production çıktı klasörleri erişilebilir mi?

Kullanım:
    python ".py\\194_Production_Guardian.py"

İsteğe bağlı:
    python ".py\\194_Production_Guardian.py" 1000

Buradaki 1000 hedef batch limitidir; disk ve hazırlık değerlendirmesinde rapora yazılır.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"

DIRS_REQUIRED = {
    "production_logs": BASE_DIR / "production_logs",
    "production_state": BASE_DIR / "production_state",
    "raporlar": BASE_DIR / "raporlar",
    "uretim_output": BASE_DIR / "uretim_output",
    "uretim_input": BASE_DIR / "uretim_input",
    "exports": BASE_DIR / "exports",
    "docs": BASE_DIR / "docs",
}

CRITICAL_SCRIPTS = {
    "181_v14": PY_DIR / "181_v14_Final_Master_Production_Controller.py",
    "192": PY_DIR / "192_Resume_Engine.py",
    "193": PY_DIR / "193_Smart_Resume_Validation.py",
    "168": PY_DIR / "168_v2_Production_Format_Revizyonu_Runner.py",
    "188": PY_DIR / "188_Production_Auto_Cleaner.py",
    "172": PY_DIR / "172_AI_Kalite_Hakemi.py",
    "175": PY_DIR / "175_v2_AI_Hukuki_Mesele_Kapsam_Analiz_Motoru.py",
    "176": PY_DIR / "176_Hukuki_Mesele_Onceliklendirme_Motoru.py",
    "177": PY_DIR / "177_Hukuki_Dogruluk_Hakemi.py",
    "178": PY_DIR / "178_Akilli_Kart_Birlestirme_Hakemi.py",
    "179": PY_DIR / "179_Kart_Optimizasyon_Motoru.py",
    "180": PY_DIR / "180_v2_Karar_Karmasiklik_Analiz_Motoru.py",
    "169": PY_DIR / "169_Production_DB_Importer_Revizyonu.py",
    "170": PY_DIR / "170_RAG_Web_Export_Motoru_Revizyonu.py",
    "173": PY_DIR / "173_v2_Master_Acceptance_Test.py",
    "182": PY_DIR / "182_v2_Production_Drift_Analiz_Motoru.py",
    "183": PY_DIR / "183_Production_Sampling_QA.py",
    "184": PY_DIR / "184_v4_Production_Dashboard.py",
    "190": PY_DIR / "190_v2_Production_Supervisor.py",
}

DB_CANDIDATES = [
    BASE_DIR / "kik_database.db",
    BASE_DIR / "kik.db",
    PY_DIR / "kik.db",
    PY_DIR / "kik_kararlar.db",
]

SECRET_PATTERNS = [
    "sk-*.txt",
    "*api_key*",
    "*apikey*",
    "*.env",
    ".env",
]


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_read_json(path: Path) -> Tuple[bool, str]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True, "JSON okunabilir"
    except Exception as exc:
        return False, f"JSON okunamadı: {exc}"


def add_check(checks: List[Dict[str, Any]], name: str, ok: bool, level: str, detail: str) -> None:
    checks.append({
        "name": name,
        "ok": bool(ok),
        "level": level,
        "detail": detail,
    })


def writable_test(path: Path) -> Tuple[bool, str]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test_file = path / f".guardian_write_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tmp"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        return True, "Yazılabilir"
    except Exception as exc:
        return False, f"Yazılamıyor: {exc}"


def check_disk_space(target_batch: int) -> Tuple[bool, str, float]:
    usage = shutil.disk_usage(BASE_DIR)
    free_gb = round(usage.free / (1024 ** 3), 2)

    # Muhafazakâr eşik:
    # - Küçük testler için minimum 20 GB.
    # - Büyük üretim için batch başına yaklaşık 0.02 GB güvenlik payı.
    # 1000 batch için 20 GB + 20 GB = 40 GB önerir.
    required_gb = max(20.0, round(20.0 + target_batch * 0.02, 2))
    ok = free_gb >= required_gb

    return ok, f"Boş alan={free_gb} GB | Önerilen minimum={required_gb} GB", free_gb


def find_latest_resume_state() -> Tuple[Path | None, Dict[str, Any] | None, str]:
    state_dir = DIRS_REQUIRED["production_state"]
    files = sorted(state_dir.glob("192_resume_state_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None, None, "Resume state yok"
    path = files[0]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return path, data, "Son resume state okunabilir"
    except Exception as exc:
        return path, None, f"Son resume state okunamadı: {exc}"


def scan_secret_files() -> List[Path]:
    found: List[Path] = []
    for pattern in SECRET_PATTERNS:
        found.extend(BASE_DIR.glob(pattern))
        found.extend(PY_DIR.glob(pattern))
    # Benzersizleştir
    unique = []
    seen = set()
    for p in found:
        key = str(p).lower()
        if key not in seen and p.exists():
            seen.add(key)
            unique.append(p)
    return unique


def run_guardian(target_batch: int) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    add_check(checks, "base_dir_exists", BASE_DIR.exists(), "BLOCK", f"BASE_DIR={BASE_DIR}")
    add_check(checks, "py_dir_exists", PY_DIR.exists(), "BLOCK", f"PY_DIR={PY_DIR}")

    for name, path in DIRS_REQUIRED.items():
        add_check(checks, f"dir_exists_{name}", path.exists(), "BLOCK", str(path))
        ok_w, detail_w = writable_test(path)
        add_check(checks, f"dir_writable_{name}", ok_w, "BLOCK", f"{path} | {detail_w}")

    ok_disk, detail_disk, free_gb = check_disk_space(target_batch)
    add_check(checks, "disk_space", ok_disk, "BLOCK", detail_disk)

    for name, script in CRITICAL_SCRIPTS.items():
        add_check(checks, f"script_exists_{name}", script.exists(), "BLOCK", str(script))

    db_existing = [p for p in DB_CANDIDATES if p.exists()]
    add_check(
        checks,
        "database_exists",
        len(db_existing) > 0,
        "BLOCK",
        "Bulunan DB: " + (", ".join(str(p) for p in db_existing) if db_existing else "Yok")
    )

    gitignore = BASE_DIR / ".gitignore"
    add_check(checks, "gitignore_exists", gitignore.exists(), "WARN", str(gitignore))
    if gitignore.exists():
        txt = gitignore.read_text(encoding="utf-8", errors="ignore")
        add_check(checks, "gitignore_has_secrets", "sk-*.txt" in txt and "*.env" in txt, "WARN", "Secret kalıpları .gitignore içinde")
        add_check(checks, "gitignore_has_outputs", "production_logs/" in txt and "uretim_output/" in txt, "WARN", "Production output klasörleri .gitignore içinde")

    secrets = scan_secret_files()
    # Secret dosyası bulunması doğrudan blok değil; çünkü localde bilinçli tutuluyor olabilir.
    # Ama proje kökünde durması güvenlik uyarısıdır.
    add_check(
        checks,
        "local_secret_files",
        len(secrets) == 0,
        "WARN",
        "Bulunan local secret/riskli dosyalar: " + (", ".join(str(p) for p in secrets) if secrets else "Yok")
    )

    latest_state_path, latest_state, latest_state_detail = find_latest_resume_state()
    add_check(
        checks,
        "latest_resume_state_readable",
        latest_state is not None or latest_state_path is None,
        "WARN",
        latest_state_detail + (f" | {latest_state_path}" if latest_state_path else "")
    )

    if latest_state:
        status = latest_state.get("status")
        last_done = latest_state.get("last_done_step")
        add_check(
            checks,
            "latest_resume_state_status",
            status in {"FINISHED", "RUNNING", "INTERRUPTED", "FAILED", "CREATED"},
            "WARN",
            f"status={status} | last_done_step={last_done}"
        )

    block_failures = [c for c in checks if c["level"] == "BLOCK" and not c["ok"]]
    warnings = [c for c in checks if c["level"] == "WARN" and not c["ok"]]

    decision = "PASS"
    if block_failures:
        decision = "FAIL"
    elif warnings:
        decision = "WARNING"

    return {
        "engine": "194_production_guardian",
        "created_at": now(),
        "target_batch": target_batch,
        "decision": decision,
        "ready_for_production": decision in {"PASS", "WARNING"},
        "free_gb": free_gb,
        "block_failures": block_failures,
        "warnings": warnings,
        "checks": checks,
    }


def write_report(result: Dict[str, Any], state_path: Path, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("194 PRODUCTION GUARDIAN RAPORU")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Tarih                  : {now()}")
    lines.append(f"Target Batch           : {result.get('target_batch')}")
    lines.append(f"Decision               : {result.get('decision')}")
    lines.append(f"Production Ready        : {'EVET' if result.get('ready_for_production') else 'HAYIR'}")
    lines.append(f"Free Disk               : {result.get('free_gb')} GB")
    lines.append("")

    lines.append("BLOCK FAILURES")
    lines.append("-" * 80)
    blocks = result.get("block_failures") or []
    if blocks:
        for c in blocks:
            lines.append(f"- {c.get('name')} | {c.get('detail')}")
    else:
        lines.append("Yok")
    lines.append("")

    lines.append("WARNINGS")
    lines.append("-" * 80)
    warns = result.get("warnings") or []
    if warns:
        for c in warns:
            lines.append(f"- {c.get('name')} | {c.get('detail')}")
    else:
        lines.append("Yok")
    lines.append("")

    lines.append("TÜM KONTROLLER")
    lines.append("-" * 80)
    for c in result.get("checks", []):
        lines.append(
            f"{c.get('name'):<35} | {c.get('level'):<5} | "
            f"{'OK' if c.get('ok') else 'FAIL'} | {c.get('detail')}"
        )
    lines.append("")

    lines.append("DOSYALAR")
    lines.append("-" * 80)
    lines.append(f"State : {state_path}")
    lines.append(f"Rapor : {report_path}")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    target_batch = 1000
    if len(sys.argv) > 1:
        try:
            target_batch = int(sys.argv[1])
        except Exception:
            pass

    result = run_guardian(target_batch)

    run_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    state_path = DIRS_REQUIRED["production_state"] / f"194_production_guardian_state_{run_tag}.json"
    report_path = DIRS_REQUIRED["raporlar"] / f"194_production_guardian_raporu_{run_tag}.txt"

    state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(result, state_path, report_path)

    print("194 PRODUCTION GUARDIAN TAMAMLANDI")
    print("-" * 80)
    print(f"Target Batch      : {target_batch}")
    print(f"Decision          : {result.get('decision')}")
    print(f"Production Ready  : {'EVET' if result.get('ready_for_production') else 'HAYIR'}")
    print(f"Block Failures    : {len(result.get('block_failures') or [])}")
    print(f"Warnings          : {len(result.get('warnings') or [])}")
    print("")
    print("Dosyalar:")
    print(state_path)
    print(report_path)

    return 0 if result.get("ready_for_production") else 1


if __name__ == "__main__":
    raise SystemExit(main())
