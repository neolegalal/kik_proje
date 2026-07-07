# -*- coding: utf-8 -*-
import argparse
import importlib.util
import py_compile
from pathlib import Path
from core.config import STATE_DIR, REPORT_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
PACKAGE_DIR = PY_DIR / "205"


def render_bridge(manager_module, entry_function):
    return f"""# -*- coding: utf-8 -*-
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent / "205"
sys.path.insert(0, str(PACKAGE_DIR))

from {manager_module} import {entry_function}

if __name__ == "__main__":
    {entry_function}()
"""


def validate_bridge(bridge_path, manager_path, entry_function):
    result = {
        "bridge_exists": bridge_path.exists(),
        "manager_exists": manager_path.exists(),
        "syntax_ok": False,
        "entry_exists": False,
        "errors": [],
        "warnings": [],
    }

    if not bridge_path.exists():
        result["errors"].append(f"Bridge dosyası yok: {bridge_path}")
        return result

    try:
        py_compile.compile(str(bridge_path), doraise=True)
        result["syntax_ok"] = True
    except Exception as e:
        result["errors"].append(f"Bridge syntax hatası: {e}")

    if not manager_path.exists():
        result["errors"].append(f"Manager dosyası yok: {manager_path}")
        return result

    try:
        spec = importlib.util.spec_from_file_location(manager_path.stem, str(manager_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result["entry_exists"] = hasattr(mod, entry_function)
        if not result["entry_exists"]:
            result["errors"].append(f"Manager içinde entry function yok: {entry_function}")
    except Exception as e:
        result["errors"].append(f"Manager import/doğrulama hatası: {e}")

    return result


def create_bridge(module_filename, manager_module, entry_function="main", overwrite=True):
    ensure_dirs(STATE_DIR, REPORT_DIR)

    if not module_filename.endswith(".py"):
        module_filename += ".py"

    bridge_path = PY_DIR / module_filename
    manager_path = PACKAGE_DIR / f"{manager_module}.py"

    errors = []
    warnings = []

    if bridge_path.exists() and not overwrite:
        errors.append(f"Bridge zaten var ve overwrite=False: {bridge_path}")

    if not manager_path.exists():
        errors.append(f"Manager dosyası bulunamadı: {manager_path}")

    if not errors:
        bridge_path.write_text(render_bridge(manager_module, entry_function), encoding="utf-8")

    validation = validate_bridge(bridge_path, manager_path, entry_function)

    errors.extend(validation.get("errors", []))
    warnings.extend(validation.get("warnings", []))

    score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
    score = max(0, score)
    decision = "BRIDGE READY" if not errors else "BRIDGE BLOCKED"

    payload = {
        "module": "205.0 SDK Bridge Generator",
        "created_at": now_text(),
        "bridge_path": str(bridge_path),
        "manager_path": str(manager_path),
        "manager_module": manager_module,
        "entry_function": entry_function,
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "validation": validation,
    }

    ts = now_stamp()
    state = STATE_DIR / f"205_0_bridge_generator_state_{ts}.json"
    report = REPORT_DIR / f"205_0_bridge_generator_raporu_{ts}.txt"
    write_json(state, payload)

    lines = [
        "=" * 80,
        "205.0 SDK BRIDGE GENERATOR",
        "=" * 80,
        f"Score          : {score} / 100",
        f"Decision       : {decision}",
        f"Bridge         : {bridge_path}",
        f"Manager        : {manager_path}",
        f"Entry          : {entry_function}",
        "",
        "VALIDATION",
        "-" * 80,
        f"Bridge Exists  : {validation.get('bridge_exists')}",
        f"Manager Exists : {validation.get('manager_exists')}",
        f"Syntax OK      : {validation.get('syntax_ok')}",
        f"Entry Exists   : {validation.get('entry_exists')}",
        "",
        "ERRORS",
        "-" * 80,
    ]

    if errors:
        for e in errors:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines += ["", "WARNINGS", "-" * 80]
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines += ["", "Dosyalar:", str(state), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")

    return {"payload": payload, "paths": {"bridge": str(bridge_path), "state": str(state), "report": str(report)}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", required=True, help="Bridge dosya adı. Örn: 205_4_DB_Growth_Analytics.py")
    parser.add_argument("--manager", required=True, help="205 paketi içindeki manager modülü. Örn: db_growth_manager")
    parser.add_argument("--entry", default="main")
    parser.add_argument("--no-overwrite", action="store_true")
    args = parser.parse_args()

    res = create_bridge(
        module_filename=args.module,
        manager_module=args.manager,
        entry_function=args.entry,
        overwrite=not args.no_overwrite,
    )

    p = res["payload"]

    print("=" * 80)
    print("205.0 SDK BRIDGE GENERATOR TAMAMLANDI")
    print("=" * 80)
    print(f"Score    : {p['score']} / 100")
    print(f"Decision : {p['decision']}")
    print(f"Errors   : {len(p['errors'])}")
    print(f"Warnings : {len(p['warnings'])}")
    print("")
    print("Dosyalar:")
    print(res["paths"]["bridge"])
    print(res["paths"]["report"])


if __name__ == "__main__":
    main()
