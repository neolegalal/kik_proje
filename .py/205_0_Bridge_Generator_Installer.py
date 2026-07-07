# -*- coding: utf-8 -*-
# 205.0 SDK Bridge Generator Installer

from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "205"
GENERATORS = PKG / "generators"

BRIDGE_GENERATOR_CODE = '# -*- coding: utf-8 -*-\nimport argparse\nimport importlib.util\nimport py_compile\nfrom pathlib import Path\nfrom core.config import STATE_DIR, REPORT_DIR\nfrom core.utils import ensure_dirs, now_stamp, now_text, write_json\n\nBASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")\nPY_DIR = BASE_DIR / ".py"\nPACKAGE_DIR = PY_DIR / "205"\n\n\ndef render_bridge(manager_module, entry_function):\n    return f"""# -*- coding: utf-8 -*-\nimport sys\nfrom pathlib import Path\n\nPACKAGE_DIR = Path(__file__).resolve().parent / "205"\nsys.path.insert(0, str(PACKAGE_DIR))\n\nfrom {manager_module} import {entry_function}\n\nif __name__ == "__main__":\n    {entry_function}()\n"""\n\n\ndef validate_bridge(bridge_path, manager_path, entry_function):\n    result = {\n        "bridge_exists": bridge_path.exists(),\n        "manager_exists": manager_path.exists(),\n        "syntax_ok": False,\n        "entry_exists": False,\n        "errors": [],\n        "warnings": [],\n    }\n\n    if not bridge_path.exists():\n        result["errors"].append(f"Bridge dosyası yok: {bridge_path}")\n        return result\n\n    try:\n        py_compile.compile(str(bridge_path), doraise=True)\n        result["syntax_ok"] = True\n    except Exception as e:\n        result["errors"].append(f"Bridge syntax hatası: {e}")\n\n    if not manager_path.exists():\n        result["errors"].append(f"Manager dosyası yok: {manager_path}")\n        return result\n\n    try:\n        spec = importlib.util.spec_from_file_location(manager_path.stem, str(manager_path))\n        mod = importlib.util.module_from_spec(spec)\n        spec.loader.exec_module(mod)\n        result["entry_exists"] = hasattr(mod, entry_function)\n        if not result["entry_exists"]:\n            result["errors"].append(f"Manager içinde entry function yok: {entry_function}")\n    except Exception as e:\n        result["errors"].append(f"Manager import/doğrulama hatası: {e}")\n\n    return result\n\n\ndef create_bridge(module_filename, manager_module, entry_function="main", overwrite=True):\n    ensure_dirs(STATE_DIR, REPORT_DIR)\n\n    if not module_filename.endswith(".py"):\n        module_filename += ".py"\n\n    bridge_path = PY_DIR / module_filename\n    manager_path = PACKAGE_DIR / f"{manager_module}.py"\n\n    errors = []\n    warnings = []\n\n    if bridge_path.exists() and not overwrite:\n        errors.append(f"Bridge zaten var ve overwrite=False: {bridge_path}")\n\n    if not manager_path.exists():\n        errors.append(f"Manager dosyası bulunamadı: {manager_path}")\n\n    if not errors:\n        bridge_path.write_text(render_bridge(manager_module, entry_function), encoding="utf-8")\n\n    validation = validate_bridge(bridge_path, manager_path, entry_function)\n\n    errors.extend(validation.get("errors", []))\n    warnings.extend(validation.get("warnings", []))\n\n    score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)\n    score = max(0, score)\n    decision = "BRIDGE READY" if not errors else "BRIDGE BLOCKED"\n\n    payload = {\n        "module": "205.0 SDK Bridge Generator",\n        "created_at": now_text(),\n        "bridge_path": str(bridge_path),\n        "manager_path": str(manager_path),\n        "manager_module": manager_module,\n        "entry_function": entry_function,\n        "score": score,\n        "decision": decision,\n        "errors": errors,\n        "warnings": warnings,\n        "validation": validation,\n    }\n\n    ts = now_stamp()\n    state = STATE_DIR / f"205_0_bridge_generator_state_{ts}.json"\n    report = REPORT_DIR / f"205_0_bridge_generator_raporu_{ts}.txt"\n    write_json(state, payload)\n\n    lines = [\n        "=" * 80,\n        "205.0 SDK BRIDGE GENERATOR",\n        "=" * 80,\n        f"Score          : {score} / 100",\n        f"Decision       : {decision}",\n        f"Bridge         : {bridge_path}",\n        f"Manager        : {manager_path}",\n        f"Entry          : {entry_function}",\n        "",\n        "VALIDATION",\n        "-" * 80,\n        f"Bridge Exists  : {validation.get(\'bridge_exists\')}",\n        f"Manager Exists : {validation.get(\'manager_exists\')}",\n        f"Syntax OK      : {validation.get(\'syntax_ok\')}",\n        f"Entry Exists   : {validation.get(\'entry_exists\')}",\n        "",\n        "ERRORS",\n        "-" * 80,\n    ]\n\n    if errors:\n        for e in errors:\n            lines.append(f"- {e}")\n    else:\n        lines.append("Errors: 0")\n\n    lines += ["", "WARNINGS", "-" * 80]\n    if warnings:\n        for w in warnings:\n            lines.append(f"- {w}")\n    else:\n        lines.append("Warnings: 0")\n\n    lines += ["", "Dosyalar:", str(state), str(report)]\n    report.write_text("\\n".join(lines), encoding="utf-8")\n\n    return {"payload": payload, "paths": {"bridge": str(bridge_path), "state": str(state), "report": str(report)}}\n\n\ndef main():\n    parser = argparse.ArgumentParser()\n    parser.add_argument("--module", required=True, help="Bridge dosya adı. Örn: 205_4_DB_Growth_Analytics.py")\n    parser.add_argument("--manager", required=True, help="205 paketi içindeki manager modülü. Örn: db_growth_manager")\n    parser.add_argument("--entry", default="main")\n    parser.add_argument("--no-overwrite", action="store_true")\n    args = parser.parse_args()\n\n    res = create_bridge(\n        module_filename=args.module,\n        manager_module=args.manager,\n        entry_function=args.entry,\n        overwrite=not args.no_overwrite,\n    )\n\n    p = res["payload"]\n\n    print("=" * 80)\n    print("205.0 SDK BRIDGE GENERATOR TAMAMLANDI")\n    print("=" * 80)\n    print(f"Score    : {p[\'score\']} / 100")\n    print(f"Decision : {p[\'decision\']}")\n    print(f"Errors   : {len(p[\'errors\'])}")\n    print(f"Warnings : {len(p[\'warnings\'])}")\n    print("")\n    print("Dosyalar:")\n    print(res["paths"]["bridge"])\n    print(res["paths"]["report"])\n\n\nif __name__ == "__main__":\n    main()\n'
RUNNER_CODE = '# -*- coding: utf-8 -*-\nimport sys\nfrom pathlib import Path\n\nPACKAGE_DIR = Path(__file__).resolve().parent / "205"\nsys.path.insert(0, str(PACKAGE_DIR))\n\nfrom generators.bridge_generator import main\n\nif __name__ == "__main__":\n    main()\n'

README = """# 205.0 SDK Bridge Generator

205.x Intelligence motorları için bridge dosyalarını otomatik üretir.

Örnek:
python ".py\\205_Bridge_Generator.py" --module 205_4_DB_Growth_Analytics.py --manager db_growth_manager
"""

def main():
    if not (PKG / "core").exists():
        raise SystemExit("205 Intelligence SDK bulunamadı. Önce 205_0_Intelligence_SDK_Installer.py çalıştırılmalı.")

    GENERATORS.mkdir(parents=True, exist_ok=True)
    (GENERATORS / "__init__.py").write_text("", encoding="utf-8")
    (GENERATORS / "bridge_generator.py").write_text(BRIDGE_GENERATOR_CODE, encoding="utf-8")
    (PKG / "README_205_BRIDGE_GENERATOR.md").write_text(README, encoding="utf-8")
    (PY / "205_Bridge_Generator.py").write_text(RUNNER_CODE, encoding="utf-8")

    print("=" * 80)
    print("205.0 SDK BRIDGE GENERATOR INSTALLER TAMAMLANDI")
    print("=" * 80)
    print("Eklenen dosyalar:")
    print(GENERATORS / "bridge_generator.py")
    print(PY / "205_Bridge_Generator.py")
    print("")
    print("Test komutu:")
    print(r'python ".py\205_Bridge_Generator.py" --module 205_3_Worker_Intelligence.py --manager worker_intelligence_manager')

if __name__ == "__main__":
    main()
