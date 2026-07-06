# -*- coding: utf-8 -*-
"""
195 - PRODUCTION RUNTIME MONITOR
NeoLegal / KİK Production Platform

Amaç:
- Production sırasında veya sonrasında sistemin anlık durumunu özetler.
- 181 Controller state, 192 Resume state, 193 Smart Resume Validation,
  194 Guardian çıktıları ve disk durumunu birlikte raporlar.
- v2.0 Architecture içindeki Runtime Monitor katmanının ilk sürümüdür.

Kullanım:
    python ".py\\195_Production_Runtime_Monitor.py"

İsteğe bağlı run_id:
    python ".py\\195_Production_Runtime_Monitor.py" 20260707_012406
"""

from __future__ import annotations

import glob
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List


BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
RAPOR_DIR = BASE_DIR / "raporlar"
LOG_DIR = BASE_DIR / "production_logs"
EXPORT_DIR = BASE_DIR / "exports"
URETIM_OUTPUT_DIR = BASE_DIR / "uretim_output"


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_json(path: Optional[Path]) -> Optional[Dict[str, Any]]:
    if not path or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def latest_file(pattern: str) -> Optional[Path]:
    files = glob.glob(pattern)
    if not files:
        return None
    return Path(max(files, key=lambda p: Path(p).stat().st_mtime))


def find_by_run_id(prefix: str, run_id: str) -> Optional[Path]:
    # Önce doğrudan dosya adında run_id ara
    files = glob.glob(str(STATE_DIR / f"{prefix}*{run_id}*.json"))
    if files:
        return Path(max(files, key=lambda p: Path(p).stat().st_mtime))
    return None


def file_size_mb(path: Optional[Path]) -> float:
    if not path or not path.exists():
        return 0.0
    return round(path.stat().st_size / (1024 * 1024), 3)


def disk_status() -> Dict[str, Any]:
    u = shutil.disk_usage(BASE_DIR)
    total = round(u.total / (1024 ** 3), 2)
    free = round(u.free / (1024 ** 3), 2)
    used = round(u.used / (1024 ** 3), 2)
    pct = round((u.used / u.total) * 100, 2) if u.total else 0
    return {
        "total_gb": total,
        "used_gb": used,
        "free_gb": free,
        "used_percent": pct,
    }


def summarize_resume_state(state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not state:
        return {
            "exists": False,
            "status": None,
            "last_done_step": None,
            "done_steps": [],
            "running_steps": [],
            "failed_steps": [],
            "resume_count": 0,
        }

    steps = state.get("steps") or {}
    done = []
    running = []
    failed = []

    if isinstance(steps, dict):
        for k, v in steps.items():
            status = str((v or {}).get("status") or "").upper()
            if status == "DONE":
                done.append(k)
            elif status == "RUNNING":
                running.append(k)
            elif status == "FAIL":
                failed.append(k)

    return {
        "exists": True,
        "run_id": state.get("run_id"),
        "status": state.get("status"),
        "final_ready": state.get("final_ready"),
        "last_done_step": state.get("last_done_step"),
        "done_steps": done,
        "running_steps": running,
        "failed_steps": failed,
        "resume_count": state.get("resume_count", 0),
    }


def summarize_181_state(state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not state:
        return {
            "exists": False,
            "final_ready": None,
            "overall_ok": None,
            "limit": None,
            "steps": [],
        }

    steps = state.get("steps") or []
    failed = []
    nonblocking = []
    ok_steps = []

    if isinstance(steps, list):
        for s in steps:
            if not s.get("ok") and not s.get("non_blocking"):
                failed.append(s.get("step"))
            elif s.get("non_blocking") and not s.get("ok"):
                nonblocking.append(s.get("step"))
            elif s.get("ok"):
                ok_steps.append(s.get("step"))

    return {
        "exists": True,
        "run_id": state.get("run_id"),
        "limit": state.get("limit"),
        "final_ready": state.get("final_ready_for_large_production"),
        "overall_ok": state.get("overall_ok"),
        "recovered_steps": state.get("recovered_steps") or [],
        "ok_steps": ok_steps,
        "failed_steps": failed,
        "nonblocking_warnings": nonblocking,
        "output_168": state.get("output_168"),
        "optimized_output": state.get("optimized_output"),
        "recommendation": state.get("recommendation"),
    }


def get_runtime_snapshot(run_id: Optional[str] = None) -> Dict[str, Any]:
    if run_id:
        state_181_path = find_by_run_id("181_v14_final_master_controller_state_", run_id) or find_by_run_id("181_v13_final_master_controller_state_", run_id)
        resume_path = find_by_run_id("192_resume_state_", run_id)
        smart_path = find_by_run_id("193_smart_resume_validation_state_", run_id)
    else:
        state_181_path = latest_file(str(STATE_DIR / "181_v14_final_master_controller_state_*.json")) or latest_file(str(STATE_DIR / "181_v13_final_master_controller_state_*.json"))
        resume_path = latest_file(str(STATE_DIR / "192_resume_state_*.json"))
        smart_path = latest_file(str(STATE_DIR / "193_smart_resume_validation_state_*.json"))

    guardian_path = latest_file(str(STATE_DIR / "194_production_guardian_state_*.json"))

    state_181 = read_json(state_181_path)
    resume_state = read_json(resume_path)
    smart_state = read_json(smart_path)
    guardian_state = read_json(guardian_path)

    latest_log = latest_file(str(LOG_DIR / "181_v14_final_master_controller_log_*.txt")) or latest_file(str(LOG_DIR / "181_v13_final_master_controller_log_*.txt"))
    latest_report = latest_file(str(RAPOR_DIR / "181_v14_final_master_controller_raporu_*.txt")) or latest_file(str(RAPOR_DIR / "181_v13_final_master_controller_raporu_*.txt"))
    latest_export_web = latest_file(str(EXPORT_DIR / "web_export_170_*.jsonl"))
    latest_export_rag = latest_file(str(EXPORT_DIR / "rag_export_170_*.jsonl"))
    latest_179 = latest_file(str(URETIM_OUTPUT_DIR / "179_optimized_production_output_*.jsonl"))

    snap = {
        "engine": "195_production_runtime_monitor",
        "created_at": now(),
        "requested_run_id": run_id,
        "disk": disk_status(),
        "paths": {
            "181_state": str(state_181_path) if state_181_path else None,
            "192_resume_state": str(resume_path) if resume_path else None,
            "193_smart_resume_state": str(smart_path) if smart_path else None,
            "194_guardian_state": str(guardian_path) if guardian_path else None,
            "latest_log": str(latest_log) if latest_log else None,
            "latest_report": str(latest_report) if latest_report else None,
            "latest_web_export": str(latest_export_web) if latest_export_web else None,
            "latest_rag_export": str(latest_export_rag) if latest_export_rag else None,
            "latest_179_output": str(latest_179) if latest_179 else None,
        },
        "file_sizes_mb": {
            "latest_web_export": file_size_mb(latest_export_web),
            "latest_rag_export": file_size_mb(latest_export_rag),
            "latest_179_output": file_size_mb(latest_179),
        },
        "controller": summarize_181_state(state_181),
        "resume": summarize_resume_state(resume_state),
        "smart_resume": {
            "exists": bool(smart_state),
            "decision": smart_state.get("decision") if smart_state else None,
            "resume_safe": smart_state.get("resume_safe") if smart_state else None,
            "warnings": len(smart_state.get("warnings", [])) if smart_state else None,
            "errors": len(smart_state.get("errors", [])) if smart_state else None,
        },
        "guardian": {
            "exists": bool(guardian_state),
            "decision": guardian_state.get("decision") if guardian_state else None,
            "ready_for_production": guardian_state.get("ready_for_production") if guardian_state else None,
            "block_failures": len(guardian_state.get("block_failures", [])) if guardian_state else None,
            "warnings": len(guardian_state.get("warnings", [])) if guardian_state else None,
        },
    }

    # Genel runtime kararı
    errors: List[str] = []
    warnings: List[str] = []

    if not snap["controller"]["exists"]:
        warnings.append("181 controller state bulunamadı")

    if snap["controller"]["exists"] and snap["controller"]["final_ready"] is False:
        errors.append("181 final_ready=False")

    if snap["resume"]["exists"] and snap["resume"]["failed_steps"]:
        errors.append("Resume failed step var: " + ", ".join(snap["resume"]["failed_steps"]))

    if snap["smart_resume"]["exists"] and snap["smart_resume"]["resume_safe"] is False:
        errors.append("Smart Resume güvenli değil")

    if snap["guardian"]["exists"] and snap["guardian"]["ready_for_production"] is False:
        errors.append("Guardian production ready değil")

    if snap["disk"]["free_gb"] < 20:
        errors.append("Disk boş alanı 20 GB altında")

    if snap["disk"]["free_gb"] < 50:
        warnings.append("Disk boş alanı 50 GB altında")

    if snap["resume"]["exists"] and snap["resume"]["running_steps"]:
        warnings.append("Resume state içinde RUNNING adım var: " + ", ".join(snap["resume"]["running_steps"]))

    snap["runtime_errors"] = errors
    snap["runtime_warnings"] = warnings
    snap["runtime_decision"] = "PASS"
    if errors:
        snap["runtime_decision"] = "FAIL"
    elif warnings:
        snap["runtime_decision"] = "WARNING"

    return snap


def write_report(snapshot: Dict[str, Any], report_path: Path, state_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    c = snapshot.get("controller", {})
    r = snapshot.get("resume", {})
    s = snapshot.get("smart_resume", {})
    g = snapshot.get("guardian", {})
    d = snapshot.get("disk", {})

    lines: List[str] = []
    lines.append("195 PRODUCTION RUNTIME MONITOR RAPORU")
    lines.append("=" * 80)
    lines.append("")
    lines.append(f"Tarih                : {snapshot.get('created_at')}")
    lines.append(f"Runtime Decision     : {snapshot.get('runtime_decision')}")
    lines.append(f"Requested Run ID     : {snapshot.get('requested_run_id')}")
    lines.append("")

    lines.append("DISK")
    lines.append("-" * 80)
    lines.append(f"Toplam               : {d.get('total_gb')} GB")
    lines.append(f"Kullanılan           : {d.get('used_gb')} GB")
    lines.append(f"Boş                  : {d.get('free_gb')} GB")
    lines.append(f"Kullanım             : %{d.get('used_percent')}")
    lines.append("")

    lines.append("181 CONTROLLER")
    lines.append("-" * 80)
    lines.append(f"Var mı               : {'EVET' if c.get('exists') else 'HAYIR'}")
    lines.append(f"Run ID               : {c.get('run_id')}")
    lines.append(f"Limit                : {c.get('limit')}")
    lines.append(f"Final Ready          : {c.get('final_ready')}")
    lines.append(f"Overall OK           : {c.get('overall_ok')}")
    lines.append(f"Recovered Steps      : {', '.join(c.get('recovered_steps') or []) if c.get('recovered_steps') else 'Yok'}")
    lines.append(f"Failed Steps         : {', '.join(c.get('failed_steps') or []) if c.get('failed_steps') else 'Yok'}")
    lines.append(f"NonBlocking Warning  : {', '.join(c.get('nonblocking_warnings') or []) if c.get('nonblocking_warnings') else 'Yok'}")
    lines.append(f"Öneri                : {c.get('recommendation')}")
    lines.append("")

    lines.append("192 RESUME")
    lines.append("-" * 80)
    lines.append(f"Var mı               : {'EVET' if r.get('exists') else 'HAYIR'}")
    lines.append(f"Run ID               : {r.get('run_id')}")
    lines.append(f"Status               : {r.get('status')}")
    lines.append(f"Final Ready          : {r.get('final_ready')}")
    lines.append(f"Last Done Step       : {r.get('last_done_step')}")
    lines.append(f"Resume Count         : {r.get('resume_count')}")
    lines.append(f"Done Steps           : {', '.join(r.get('done_steps') or []) if r.get('done_steps') else 'Yok'}")
    lines.append(f"Running Steps        : {', '.join(r.get('running_steps') or []) if r.get('running_steps') else 'Yok'}")
    lines.append(f"Failed Steps         : {', '.join(r.get('failed_steps') or []) if r.get('failed_steps') else 'Yok'}")
    lines.append("")

    lines.append("193 SMART RESUME")
    lines.append("-" * 80)
    lines.append(f"Var mı               : {'EVET' if s.get('exists') else 'HAYIR'}")
    lines.append(f"Decision             : {s.get('decision')}")
    lines.append(f"Resume Safe          : {s.get('resume_safe')}")
    lines.append(f"Warnings             : {s.get('warnings')}")
    lines.append(f"Errors               : {s.get('errors')}")
    lines.append("")

    lines.append("194 GUARDIAN")
    lines.append("-" * 80)
    lines.append(f"Var mı               : {'EVET' if g.get('exists') else 'HAYIR'}")
    lines.append(f"Decision             : {g.get('decision')}")
    lines.append(f"Production Ready     : {g.get('ready_for_production')}")
    lines.append(f"Block Failures       : {g.get('block_failures')}")
    lines.append(f"Warnings             : {g.get('warnings')}")
    lines.append("")

    lines.append("RUNTIME WARNINGS")
    lines.append("-" * 80)
    lines.extend([f"- {x}" for x in snapshot.get("runtime_warnings", [])] or ["Yok"])
    lines.append("")

    lines.append("RUNTIME ERRORS")
    lines.append("-" * 80)
    lines.extend([f"- {x}" for x in snapshot.get("runtime_errors", [])] or ["Yok"])
    lines.append("")

    lines.append("DOSYALAR")
    lines.append("-" * 80)
    for k, v in snapshot.get("paths", {}).items():
        lines.append(f"{k:<24}: {v}")
    lines.append(f"Runtime State         : {state_path}")
    lines.append(f"Runtime Report        : {report_path}")

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    run_id = sys.argv[1].strip() if len(sys.argv) > 1 else None
    snapshot = get_runtime_snapshot(run_id)

    tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = run_id or "latest"
    state_path = STATE_DIR / f"195_runtime_monitor_state_{suffix}_{tag}.json"
    report_path = RAPOR_DIR / f"195_runtime_monitor_raporu_{suffix}_{tag}.txt"

    state_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(snapshot, report_path, state_path)

    print("195 PRODUCTION RUNTIME MONITOR TAMAMLANDI")
    print("-" * 80)
    print(f"Runtime Decision  : {snapshot.get('runtime_decision')}")
    print(f"Run ID            : {snapshot.get('requested_run_id') or snapshot.get('resume', {}).get('run_id')}")
    print(f"Disk Free         : {snapshot.get('disk', {}).get('free_gb')} GB")
    print(f"181 Final Ready   : {snapshot.get('controller', {}).get('final_ready')}")
    print(f"Resume Status     : {snapshot.get('resume', {}).get('status')}")
    print(f"Smart Resume      : {snapshot.get('smart_resume', {}).get('decision')}")
    print(f"Guardian          : {snapshot.get('guardian', {}).get('decision')}")
    print(f"Warnings          : {len(snapshot.get('runtime_warnings', []))}")
    print(f"Errors            : {len(snapshot.get('runtime_errors', []))}")
    print("")
    print("Dosyalar:")
    print(state_path)
    print(report_path)

    return 0 if snapshot.get("runtime_decision") in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
