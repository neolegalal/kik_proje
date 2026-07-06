# -*- coding: utf-8 -*-
"""
193 - SMART RESUME VALIDATION ENGINE
NeoLegal / KİK Production Platform

Amaç:
- 192 Resume Engine state dosyasında DONE görünen adımların gerçekten güvenli
  şekilde resume edilebilir olup olmadığını kontrol eder.
- Output dosyası var mı?
- Output dosyası boş mu?
- JSONL dosyası okunabilir mi?
- Resume state içinde DONE/RUNNING/FAIL tutarlılığı var mı?
- Kritik adımların output_path kayıtları sağlam mı?

Bu modül production zincirini çalıştırmaz.
181_v14 / 181_v15 gibi controller'lar tarafından resume öncesi güvenlik kontrolü
olarak kullanılmak üzere tasarlanmıştır.

Örnek:
    python ".py\\193_Smart_Resume_Validation.py" 20260707_012406
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
RAPOR_DIR = BASE_DIR / "raporlar"

CRITICAL_OUTPUT_STEPS = {
    "168",
    "188",
    "172",
    "177",
    "179",
}


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_jsonl_file(path: Path) -> bool:
    return path.suffix.lower() == ".jsonl"


def validate_jsonl(path: Path, max_lines_to_check: int = 25) -> Tuple[bool, str, int]:
    if not path.exists():
        return False, "Dosya yok", 0

    if path.stat().st_size <= 0:
        return False, "Dosya boş", 0

    checked = 0
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                checked += 1
                try:
                    json.loads(line)
                except Exception as exc:
                    return False, f"JSONL bozuk satır: {checked} | {exc}", checked
                if checked >= max_lines_to_check:
                    break
    except Exception as exc:
        return False, f"Okuma hatası: {exc}", checked

    if checked == 0:
        return False, "JSONL içinde okunabilir satır yok", checked

    return True, f"JSONL OK | kontrol edilen satır={checked}", checked


def validate_file(path_str: Optional[str]) -> Tuple[bool, str]:
    if not path_str:
        return False, "output_path yok"

    path = Path(path_str)
    if not path.exists():
        return False, f"output_path bulunamadı: {path}"

    if path.stat().st_size <= 0:
        return False, f"output_path boş: {path}"

    if is_jsonl_file(path):
        ok, detail, checked = validate_jsonl(path)
        return ok, detail

    return True, f"Dosya mevcut ve boş değil: {path.stat().st_size} byte"


def load_resume_state(run_id: str) -> Tuple[Path, Optional[Dict[str, Any]]]:
    path = STATE_DIR / f"192_resume_state_{run_id}.json"
    data = read_json(path)
    return path, data


def latest_resume_state() -> Tuple[Optional[Path], Optional[Dict[str, Any]]]:
    files = sorted(STATE_DIR.glob("192_resume_state_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None, None
    path = files[0]
    return path, read_json(path)


def validate_resume_state(state: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "created_at": now(),
        "engine": "193_smart_resume_validation",
        "resume_run_id": state.get("run_id"),
        "resume_status": state.get("status"),
        "resume_final_ready": state.get("final_ready"),
        "batch_limit": state.get("batch_limit"),
        "checks": [],
        "warnings": [],
        "errors": [],
        "resume_safe": False,
        "decision": "FAIL",
    }

    steps = state.get("steps") or {}
    if not isinstance(steps, dict):
        result["errors"].append("steps alanı sözlük değil")
        return result

    if not steps:
        result["warnings"].append("Resume state içinde adım kaydı yok")

    running = []
    failed = []
    done = []

    for step, item in steps.items():
        item = item or {}
        status = str(item.get("status") or "").upper()

        if status == "DONE":
            done.append(step)
        elif status == "RUNNING":
            running.append(step)
        elif status == "FAIL":
            failed.append(step)

        check = {
            "step": step,
            "status": status,
            "output_path": item.get("output_path"),
            "ok": True,
            "detail": "Kontrol gerekmiyor",
        }

        if status == "DONE" and step in CRITICAL_OUTPUT_STEPS:
            ok, detail = validate_file(item.get("output_path"))
            check["ok"] = ok
            check["detail"] = detail
            if not ok:
                result["errors"].append(f"{step}: {detail}")

        elif status == "DONE" and item.get("output_path"):
            ok, detail = validate_file(item.get("output_path"))
            check["ok"] = ok
            check["detail"] = detail
            if not ok:
                result["warnings"].append(f"{step}: {detail}")

        result["checks"].append(check)

    if failed:
        result["errors"].append("FAIL durumunda adım var: " + ", ".join(failed))

    if running:
        result["warnings"].append("RUNNING durumda adım var; resume bu adımdan tekrar çalıştırmalı: " + ", ".join(running))

    if not done:
        result["warnings"].append("DONE adım yok; resume edilecek anlamlı ilerleme yok")

    result["done_steps"] = done
    result["running_steps"] = running
    result["failed_steps"] = failed

    result["resume_safe"] = len(result["errors"]) == 0
    result["decision"] = "PASS" if result["resume_safe"] else "FAIL"
    if result["resume_safe"] and result["warnings"]:
        result["decision"] = "WARNING"

    return result


def write_report(validation: Dict[str, Any], state_path: Path, report_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append("193 SMART RESUME VALIDATION RAPORU")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Tarih              : {now()}")
    lines.append(f"Resume State       : {state_path}")
    lines.append(f"Run ID             : {validation.get('resume_run_id')}")
    lines.append(f"Batch Limit        : {validation.get('batch_limit')}")
    lines.append(f"Resume Status      : {validation.get('resume_status')}")
    lines.append(f"Resume Final Ready : {validation.get('resume_final_ready')}")
    lines.append(f"Decision           : {validation.get('decision')}")
    lines.append(f"Resume Safe        : {'EVET' if validation.get('resume_safe') else 'HAYIR'}")
    lines.append("")

    lines.append("DONE STEPS")
    lines.append("-" * 80)
    done = validation.get("done_steps") or []
    lines.extend([f"- {x}" for x in done] or ["Yok"])
    lines.append("")

    lines.append("RUNNING STEPS")
    lines.append("-" * 80)
    running = validation.get("running_steps") or []
    lines.extend([f"- {x}" for x in running] or ["Yok"])
    lines.append("")

    lines.append("FAILED STEPS")
    lines.append("-" * 80)
    failed = validation.get("failed_steps") or []
    lines.extend([f"- {x}" for x in failed] or ["Yok"])
    lines.append("")

    lines.append("DOSYA KONTROLLERI")
    lines.append("-" * 80)
    for c in validation.get("checks", []):
        lines.append(
            f"{c.get('step'):<10} | {c.get('status'):<8} | "
            f"{'OK' if c.get('ok') else 'FAIL'} | {c.get('detail')}"
        )
    lines.append("")

    lines.append("UYARILAR")
    lines.append("-" * 80)
    lines.extend([f"- {x}" for x in validation.get("warnings", [])] or ["Yok"])
    lines.append("")

    lines.append("HATALAR")
    lines.append("-" * 80)
    lines.extend([f"- {x}" for x in validation.get("errors", [])] or ["Yok"])
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    run_id = sys.argv[1].strip() if len(sys.argv) > 1 else ""

    if run_id:
        state_path, state = load_resume_state(run_id)
    else:
        state_path, state = latest_resume_state()

    if not state_path:
        print("Resume state bulunamadı.")
        return 2

    if not state:
        print(f"Resume state okunamadı: {state_path}")
        return 2

    validation = validate_resume_state(state)

    report_name = f"193_smart_resume_validation_{state.get('run_id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_path = RAPOR_DIR / report_name
    write_report(validation, state_path, report_path)

    validation_state_path = STATE_DIR / f"193_smart_resume_validation_state_{state.get('run_id')}.json"
    validation_state_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    print("193 SMART RESUME VALIDATION TAMAMLANDI")
    print("-" * 80)
    print(f"Run ID       : {state.get('run_id')}")
    print(f"Decision     : {validation.get('decision')}")
    print(f"Resume Safe  : {'EVET' if validation.get('resume_safe') else 'HAYIR'}")
    print(f"Warnings     : {len(validation.get('warnings', []))}")
    print(f"Errors       : {len(validation.get('errors', []))}")
    print("")
    print("Dosyalar:")
    print(validation_state_path)
    print(report_path)

    return 0 if validation.get("resume_safe") else 1


if __name__ == "__main__":
    raise SystemExit(main())
