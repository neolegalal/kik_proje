# -*- coding: utf-8 -*-
import sys
from config import BASE_DIR, STATE_DIR, REPORT_DIR, PACKAGE_199_MANAGER, MIN_DISK_GB
from utils import now_stamp, now_text, ensure_dirs, disk_free_gb, run_command, write_json
from config_manager import run as run_config

def preflight():
    return {
        "package_199_manager_exists": PACKAGE_199_MANAGER.exists(),
        "status": "PASS" if PACKAGE_199_MANAGER.exists() else "FAIL",
        "message": "199 Package Manager bulundu." if PACKAGE_199_MANAGER.exists() else "199 Package Manager bulunamadı.",
    }

def run_199(mode="all", timeout=600):
    if mode == "health":
        args = ["--health"]
    elif mode == "registry":
        args = ["--registry"]
    else:
        args = ["--all"]
    return run_command([sys.executable, str(PACKAGE_199_MANAGER)] + args, cwd=BASE_DIR, timeout=timeout)

def evaluate(pre, config_result, manager_result, free_gb):
    score = 100
    errors = []
    warnings = []
    if pre["status"] != "PASS":
        score -= 35
        errors.append(pre["message"])
    if config_result["decision"] != "CONFIG READY":
        score -= 15
        warnings.append(f"Config sonucu: {config_result['decision']}")
    if manager_result:
        if manager_result["status"] != "PASS":
            score -= 30
            errors.append("199 Package Manager çalıştırılamadı.")
        else:
            out = (manager_result.get("stdout_tail") or "").upper()
            if "REGISTRY READY" in out and "PLATFORM READY" in out:
                pass
            else:
                score -= 8
                warnings.append("199 Package çıktısında READY sinyali tam görülmedi.")
    else:
        score -= 5
        warnings.append("199 Package Manager çalıştırılmadı.")
    if free_gb < MIN_DISK_GB:
        score -= 20
        errors.append("Disk alanı düşük.")
    score = max(0, min(100, score))
    decision = "CORE BLOCKED" if errors else ("CORE READY" if score >= 95 else "CORE REVIEW")
    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}

def run(mode="status"):
    ensure_dirs(STATE_DIR, REPORT_DIR)
    ts = now_stamp()
    free = disk_free_gb(BASE_DIR)
    config_run = run_config(force=False)
    pre = preflight()
    mgr = run_199("all" if mode in ["status", "plan"] else mode) if pre["status"] == "PASS" else None
    result = evaluate(pre, config_run["result"], mgr, free)
    payload = {"module": "200 Package Core", "created_at": now_text(), "mode": mode, "disk_free_gb": free, "preflight": pre, "config_result": config_run["result"], "manager_result": mgr, "result": result}
    state = STATE_DIR / f"200_pkg_core_state_{ts}.json"
    report = REPORT_DIR / f"200_pkg_core_raporu_{ts}.txt"
    write_json(state, payload)
    report.write_text("\n".join([
        "="*80,
        "200 PACKAGE - PLATFORM CORE",
        "="*80,
        f"Mode     : {mode}",
        f"Score    : {result['score']} / 100",
        f"Decision : {result['decision']}",
        f"Errors   : {len(result['errors'])}",
        f"Warnings : {len(result['warnings'])}",
        f"Disk     : {free} GB",
        "",
        "Dosyalar:",
        str(state),
        str(report),
    ]), encoding="utf-8")
    return {"payload": payload, "result": result, "paths": {"state": str(state), "report": str(report)}}
