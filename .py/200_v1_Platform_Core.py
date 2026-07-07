# -*- coding: utf-8 -*-
r"""
200 v1 - Platform Core
NeoLegal Production Platform v2.0

Amaç:
- Platformun ana giriş noktası olmak.
- 199 Package Manager'ı çağırmak.
- Registry + Health kontrollerini merkezi olarak yürütmek.
- Core kararını üretmek.
- Bu v1 sürümü production çalıştırmaz.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

python ".py\200_v1_Platform_Core.py" --status
python ".py\200_v1_Platform_Core.py" --health
python ".py\200_v1_Platform_Core.py" --registry
python ".py\200_v1_Platform_Core.py" --plan
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
ADR_DIR = BASE_DIR / "docs" / "decisions"

PACKAGE_MANAGER = PY_DIR / "199_Package_Manager.py"
PACKAGE_DIR = PY_DIR / "199"

NOW = datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ADR_DIR.mkdir(parents=True, exist_ok=True)


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def run_command(command, timeout=600):
    started = time.time()
    try:
        proc = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout
        )
        return {
            "executed": True,
            "timeout": False,
            "returncode": proc.returncode,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": proc.stdout[-12000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-12000:] if proc.stderr else "",
            "status": "PASS" if proc.returncode == 0 else "FAIL",
        }
    except subprocess.TimeoutExpired as e:
        return {
            "executed": True,
            "timeout": True,
            "returncode": None,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": (e.stdout or "")[-12000:] if isinstance(e.stdout, str) else "",
            "stderr_tail": (e.stderr or "")[-12000:] if isinstance(e.stderr, str) else "",
            "status": "TIMEOUT",
        }
    except Exception as e:
        return {
            "executed": True,
            "timeout": False,
            "returncode": None,
            "elapsed_seconds": round(time.time() - started, 2),
            "stdout_tail": "",
            "stderr_tail": str(e),
            "status": "FAIL",
        }


def preflight():
    required_package_files = [
        PACKAGE_DIR / "config.py",
        PACKAGE_DIR / "utils.py",
        PACKAGE_DIR / "registry.py",
        PACKAGE_DIR / "health.py",
        PACKAGE_DIR / "manager.py",
    ]

    package_files = []
    missing = []

    for p in required_package_files:
        item = {"path": str(p), "exists": p.exists()}
        package_files.append(item)
        if not p.exists():
            missing.append(str(p))

    return {
        "package_manager_exists": PACKAGE_MANAGER.exists(),
        "package_dir_exists": PACKAGE_DIR.exists(),
        "package_files": package_files,
        "missing": missing,
        "status": "PASS" if PACKAGE_MANAGER.exists() and PACKAGE_DIR.exists() and not missing else "FAIL",
    }


def build_command(mode):
    if mode == "registry":
        return [sys.executable, str(PACKAGE_MANAGER), "--registry"]
    if mode == "health":
        return [sys.executable, str(PACKAGE_MANAGER), "--health"]
    if mode in ("status", "plan"):
        return [sys.executable, str(PACKAGE_MANAGER), "--all"]
    return [sys.executable, str(PACKAGE_MANAGER), "--all"]


def evaluate(payload):
    score = 100
    errors = []
    warnings = []

    pf = payload["preflight"]
    if pf["status"] != "PASS":
        score -= 40
        errors.append("199 Package preflight başarısız.")

    if payload["disk_free_gb"] < 50:
        score -= 20
        errors.append("Disk alanı 50 GB altında.")

    rr = payload.get("package_run_result")
    if rr:
        if rr["status"] != "PASS":
            score -= 30
            errors.append("199 Package Manager çalıştırılamadı.")
        else:
            out = (rr.get("stdout_tail") or "").upper()
            if "REGISTRY READY" in out and "PLATFORM READY" in out:
                pass
            elif "PLATFORM READY" in out:
                warnings.append("Platform READY bulundu ancak registry sonucu ayrıca doğrulanmalı.")
                score -= 3
            else:
                warnings.append("199 çıktısında beklenen READY sinyali tam görülemedi.")
                score -= 8
    else:
        warnings.append("Package Manager çalıştırılmadı.")
        score -= 5

    score = max(0, min(100, score))

    if errors:
        decision = "CORE BLOCKED"
    elif score >= 95:
        decision = "CORE READY"
    elif score >= 80:
        decision = "CORE REVIEW"
    else:
        decision = "CORE BLOCKED"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
    }


def write_outputs(payload):
    json_path = STATE_DIR / f"200_v1_platform_core_state_{NOW}.json"
    txt_path = REPORT_DIR / f"200_v1_platform_core_raporu_{NOW}.txt"

    payload["result"] = evaluate(payload)

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    result = payload["result"]
    pf = payload["preflight"]
    rr = payload.get("package_run_result")

    lines = []
    lines.append("=" * 80)
    lines.append("200 v1 PLATFORM CORE")
    lines.append("=" * 80)
    lines.append(f"Tarih           : {payload['created_at']}")
    lines.append(f"Mode            : {payload['mode']}")
    lines.append(f"Score           : {result['score']} / 100")
    lines.append(f"Decision        : {result['decision']}")
    lines.append(f"Disk Free       : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("PREFLIGHT")
    lines.append("-" * 80)
    lines.append(f"199 Manager     : {PACKAGE_MANAGER}")
    lines.append(f"Exists          : {pf['package_manager_exists']}")
    lines.append(f"199 Package Dir : {PACKAGE_DIR}")
    lines.append(f"Exists          : {pf['package_dir_exists']}")
    lines.append(f"Missing Files   : {len(pf['missing'])}")
    if pf["missing"]:
        for m in pf["missing"]:
            lines.append(f"- {m}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("199 PACKAGE RUN")
    lines.append("-" * 80)
    if rr:
        lines.append(f"Status          : {rr.get('status')}")
        lines.append(f"Return Code     : {rr.get('returncode')}")
        lines.append(f"Elapsed Seconds : {rr.get('elapsed_seconds')}")
        lines.append("")
        lines.append("STDOUT TAIL")
        lines.append(rr.get("stdout_tail") or "")
        lines.append("")
        lines.append("STDERR TAIL")
        lines.append(rr.get("stderr_tail") or "")
    else:
        lines.append("Package Manager çalıştırılmadı.")
    lines.append("")
    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)
    if result["errors"]:
        for e in result["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")
    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")
    lines.append("")
    lines.append("NOT:")
    lines.append("200 v1 production çalıştırmaz. Platform çekirdeği başlangıç kontrolüdür.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--registry", action="store_true")
    parser.add_argument("--plan", action="store_true")
    return parser.parse_args()


def resolve_mode(args):
    if args.health:
        return "health"
    if args.registry:
        return "registry"
    if args.plan:
        return "plan"
    return "status"


def main():
    ensure_dirs()
    args = parse_args()
    mode = resolve_mode(args)

    pf = preflight()
    rr = None

    if pf["status"] == "PASS":
        command = build_command(mode)
        rr = run_command(command, timeout=600)
    else:
        command = None

    payload = {
        "module": "200 v1 Platform Core",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "mode": mode,
        "disk_free_gb": disk_free_gb(),
        "preflight": pf,
        "package_command": " ".join(command) if command else None,
        "package_run_result": rr,
    }

    json_path, txt_path = write_outputs(payload)
    result = payload["result"]

    print("=" * 80)
    print("200 v1 PLATFORM CORE TAMAMLANDI")
    print("=" * 80)
    print(f"Mode      : {mode}")
    print(f"Score     : {result['score']} / 100")
    print(f"Decision  : {result['decision']}")
    print(f"Errors    : {len(result['errors'])}")
    print(f"Warnings  : {len(result['warnings'])}")
    print(f"Disk Free : {payload['disk_free_gb']} GB")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
