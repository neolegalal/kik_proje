
# -*- coding: utf-8 -*-
import argparse
import py_compile
from pathlib import Path
from core.config import STATE_DIR, REPORT_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "207"
MODULES = PKG / "modules"
TESTS = PKG / "tests"

def snake(text):
    out = []
    prev = False
    for ch in text:
        if ch.isalnum():
            if ch.isupper() and prev:
                out.append("_")
            out.append(ch.lower())
            prev = ch.islower() or ch.isdigit()
        else:
            if out and out[-1] != "_":
                out.append("_")
            prev = False
    return "".join(out).strip("_")

def camel(text):
    return "".join(p.capitalize() for p in snake(text).split("_") if p)

ENGINE_TEMPLATE = '''# -*- coding: utf-8 -*-
from core.sdk import ExecutionSDK
from core.config import STATE_DIR, REPORT_DIR, EXECUTION_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json

MODULE_DIR = EXECUTION_DIR / "{safe_id}_{module_slug}"
OUTPUT_FILE = MODULE_DIR / "{safe_id}_{module_slug}.json"

class {class_name}:
    def __init__(self):
        self.sdk = ExecutionSDK(name="{module_id} {module_name}")

    def analyze(self, context, plan):
        return {{
            "module_id": "{module_id}",
            "module_name": "{module_name}",
            "status": "SKELETON_READY",
            "context": context,
            "plan": plan
        }}

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR)
        ts = now_stamp()
        sdk_result = self.sdk.run()
        context = sdk_result["payload"]["context"]
        plan = sdk_result["payload"]["plan"]
        validation = sdk_result["payload"]["validation"]
        analysis = self.analyze(context, plan)

        result = {{
            "score": validation["score"],
            "decision": "{module_upper} READY" if not validation["errors"] else "{module_upper} REVIEW",
            "risk": context.get("scheduler_risk"),
            "recommendation": plan.get("message")
        }}

        payload = {{
            "module": "{module_id} {module_name}",
            "created_at": now_text(),
            "analysis": analysis,
            "result": result,
            "sdk_reference": sdk_result["paths"]
        }}

        state = STATE_DIR / f"{safe_id}_{module_slug}_state_{{ts}}.json"
        report = REPORT_DIR / f"{safe_id}_{module_slug}_raporu_{{ts}}.txt"

        write_json(OUTPUT_FILE, payload)
        write_json(state, payload)

        lines = [
            "=" * 80,
            "{module_id} {module_name}".upper(),
            "=" * 80,
            "Score    : " + str(result["score"]) + " / 100",
            "Decision : " + str(result["decision"]),
            "Risk     : " + str(result["risk"]),
            "",
            "Recommendation:",
            str(result["recommendation"]),
            "",
            "Dosyalar:",
            str(OUTPUT_FILE),
            str(state),
            str(report)
        ]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {{"payload": payload, "result": result, "paths": {{"output": str(OUTPUT_FILE), "state": str(state), "report": str(report)}}}}
'''

MANAGER_TEMPLATE = '''# -*- coding: utf-8 -*-
import argparse
from modules.{module_slug}.engine import {class_name}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    res = {class_name}().run()
    result = res["result"]

    print("=" * 80)
    print("{module_title} TAMAMLANDI")
    print("=" * 80)
    print("Score    : " + str(result["score"]) + " / 100")
    print("Decision : " + str(result["decision"]))
    print("Risk     : " + str(result["risk"]))
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["output"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
'''

BRIDGE_TEMPLATE = '''# -*- coding: utf-8 -*-
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent / "207"
sys.path.insert(0, str(PACKAGE_DIR))

from {manager_module} import main

if __name__ == "__main__":
    main()
'''

DASHBOARD_TEMPLATE = '''# -*- coding: utf-8 -*-
def build_dashboard(payload):
    result = payload.get("result", {{}})
    return {{
        "module": "{module_id} {module_name}",
        "score": result.get("score"),
        "decision": result.get("decision"),
        "risk": result.get("risk"),
        "recommendation": result.get("recommendation")
    }}
'''

STATE_TEMPLATE = '''# -*- coding: utf-8 -*-
def initial_state():
    return {{
        "module": "{module_id} {module_name}",
        "status": "INITIALIZED",
        "last_run": None
    }}
'''

REPORT_TEMPLATE = '''# -*- coding: utf-8 -*-
def build_report(payload):
    result = payload.get("result", {{}})
    return "\\n".join([
        "{module_id} {module_name}",
        "=" * 80,
        "Score: " + str(result.get("score")),
        "Decision: " + str(result.get("decision")),
        "Risk: " + str(result.get("risk"))
    ])
'''

TEST_TEMPLATE = '''# -*- coding: utf-8 -*-
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))

from modules.{module_slug}.engine import {class_name}

def test_run():
    res = {class_name}().run()
    assert "result" in res
    assert "paths" in res
    assert res["result"]["score"] is not None

if __name__ == "__main__":
    test_run()
    print("TEST PASS: {module_slug}")
'''

def create_module(module_id, module_name, bridge_name=None, overwrite=True):
    ensure_dirs(STATE_DIR, REPORT_DIR, MODULES, TESTS)
    module_slug = snake(module_name)
    class_name = camel(module_name) + "Module"
    manager_name = module_slug + "_manager"
    safe_id = module_id.replace(".", "_")
    bridge_name = bridge_name or (safe_id + "_" + camel(module_name) + ".py")
    module_dir = MODULES / module_slug

    files = {
        module_dir / "__init__.py": "",
        module_dir / "engine.py": ENGINE_TEMPLATE.format(safe_id=safe_id, module_slug=module_slug, class_name=class_name, module_id=module_id, module_name=module_name, module_upper=module_name.upper()),
        module_dir / "dashboard.py": DASHBOARD_TEMPLATE.format(module_id=module_id, module_name=module_name),
        module_dir / "state.py": STATE_TEMPLATE.format(module_id=module_id, module_name=module_name),
        module_dir / "report.py": REPORT_TEMPLATE.format(module_id=module_id, module_name=module_name),
        PKG / (manager_name + ".py"): MANAGER_TEMPLATE.format(module_slug=module_slug, class_name=class_name, module_title=(module_id + " " + module_name).upper()),
        PY / bridge_name: BRIDGE_TEMPLATE.format(manager_module=manager_name),
        TESTS / ("test_" + module_slug + ".py"): TEST_TEMPLATE.format(module_slug=module_slug, class_name=class_name)
    }

    errors = []
    warnings = []
    if not overwrite:
        for p in files:
            if p.exists():
                errors.append("Dosya mevcut: " + str(p))

    if not errors:
        for p, content in files.items():
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            if p.suffix == ".py":
                try:
                    py_compile.compile(str(p), doraise=True)
                except Exception as e:
                    errors.append("Syntax hata " + str(p) + ": " + str(e))

    score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
    decision = "MODULE GENERATED" if not errors else "MODULE GENERATION BLOCKED"

    payload = {
        "module": "207.0 Execution Module Generator",
        "created_at": now_text(),
        "target_module": module_id + " " + module_name,
        "module_slug": module_slug,
        "class_name": class_name,
        "manager": manager_name,
        "bridge": bridge_name,
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "files": [str(p) for p in files]
    }

    ts = now_stamp()
    state = STATE_DIR / ("207_0_module_generator_state_" + ts + ".json")
    report = REPORT_DIR / ("207_0_module_generator_raporu_" + ts + ".txt")
    write_json(state, payload)

    lines = ["="*80, "207.0 EXECUTION MODULE GENERATOR", "="*80, "Score    : " + str(score) + " / 100", "Decision : " + decision, "Target   : " + module_id + " " + module_name, "Errors   : " + str(len(errors)), "Warnings : " + str(len(warnings)), "", "FILES", "-"*80]
    lines.extend([str(p) for p in files])
    if errors:
        lines += ["", "ERRORS", "-"*80] + errors
    report.write_text("\n".join(lines), encoding="utf-8")
    return {"payload": payload, "paths": {"state": str(state), "report": str(report), "bridge": str(PY / bridge_name)}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--bridge", default=None)
    parser.add_argument("--no-overwrite", action="store_true")
    args = parser.parse_args()
    res = create_module(args.module_id, args.name, args.bridge, overwrite=not args.no_overwrite)
    p = res["payload"]
    print("=" * 80)
    print("207.0 EXECUTION MODULE GENERATOR TAMAMLANDI")
    print("=" * 80)
    print("Score    : " + str(p["score"]) + " / 100")
    print("Decision : " + p["decision"])
    print("Errors   : " + str(len(p["errors"])))
    print("Warnings : " + str(len(p["warnings"])))
    print("")
    print("Bridge:")
    print(res["paths"]["bridge"])
    print("Report:")
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
