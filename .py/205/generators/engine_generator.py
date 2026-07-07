# -*- coding: utf-8 -*-
import argparse
import py_compile
from pathlib import Path
from core.config import STATE_DIR, REPORT_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json
from generators.bridge_generator import create_bridge

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
PACKAGE_DIR = PY_DIR / "205"
ENGINES_DIR = PACKAGE_DIR / "engines"


def snake(name):
    out = []
    prev = False
    for ch in name:
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


def camel(name):
    return "".join(p.capitalize() for p in snake(name).split("_") if p)


ENGINE_TEMPLATE = """# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json

ENGINE_DIR = INTELLIGENCE_DIR / "{output_slug}"
ENGINE_OUTPUT_FILE = ENGINE_DIR / "{output_slug}.json"


class {class_name}:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="{engine_name}")

    def analyze(self, normalized):
        return {{
            "status": "SKELETON",
            "message": "{engine_name} analysis logic will be implemented here.",
        }}

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, ENGINE_DIR)
        ts = now_stamp()
        sdk_result = self.sdk.run()
        normalized = sdk_result["payload"]["normalized"]
        analysis = self.analyze(normalized)

        result = {{
            "score": 95,
            "decision": "{decision_name} READY",
            "risk": "LOW",
            "recommendation": "{engine_name} skeleton hazır. Alan özel analiz mantığı eklenmelidir.",
            "executive_summary": "{engine_name} skeleton başarıyla çalıştı.",
        }}

        payload = {{
            "module": "{engine_name}",
            "created_at": now_text(),
            "analysis": analysis,
            "result": result,
            "sdk_reference": sdk_result["paths"],
        }}

        state = STATE_DIR / f"{output_slug}_state_{{ts}}.json"
        report = REPORT_DIR / f"{output_slug}_raporu_{{ts}}.txt"

        write_json(ENGINE_OUTPUT_FILE, payload)
        write_json(state, payload)

        lines = [
            "=" * 80,
            "{decision_name}",
            "=" * 80,
            f"Score          : {{result['score']}} / 100",
            f"Decision       : {{result['decision']}}",
            f"Risk           : {{result['risk']}}",
            "",
            "RECOMMENDATION",
            "-" * 80,
            result["recommendation"],
            "",
            "Dosyalar:",
            str(ENGINE_OUTPUT_FILE),
            str(state),
            str(report),
        ]

        report.write_text("\\n".join(lines), encoding="utf-8")

        return {{
            "payload": payload,
            "result": result,
            "paths": {{
                "output": str(ENGINE_OUTPUT_FILE),
                "state": str(state),
                "report": str(report),
            }}
        }}
"""


MANAGER_TEMPLATE = """# -*- coding: utf-8 -*-
import argparse
from engines.{engine_module} import {class_name}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    engine = {class_name}()
    res = engine.run()
    result = res["result"]

    print("=" * 80)
    print("{decision_name} TAMAMLANDI")
    print("=" * 80)
    print(f"Score          : {{result['score']}} / 100")
    print(f"Decision       : {{result['decision']}}")
    print(f"Risk           : {{result['risk']}}")
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["output"])
    print(res["paths"]["report"])


if __name__ == "__main__":
    main()
"""


def create_engine(engine_id, engine_name, module_name=None, manager_name=None, bridge_name=None, overwrite=True):
    ensure_dirs(STATE_DIR, REPORT_DIR, ENGINES_DIR)

    module_name = module_name or snake(engine_name)
    manager_name = manager_name or f"{module_name}_manager"
    bridge_name = bridge_name or f"{engine_id}_{camel(engine_name)}.py"
    class_name = f"{camel(engine_name)}Engine"
    output_slug = f"{engine_id.lower().replace('.', '_')}_{module_name}"
    decision_name = engine_name.upper()

    engine_path = ENGINES_DIR / f"{module_name}.py"
    manager_path = PACKAGE_DIR / f"{manager_name}.py"

    errors = []
    warnings = []

    if not overwrite:
        for p in [engine_path, manager_path, PY_DIR / bridge_name]:
            if p.exists():
                errors.append(f"Dosya mevcut ve overwrite=False: {p}")

    if not errors:
        engine_path.write_text(
            ENGINE_TEMPLATE.format(
                output_slug=output_slug,
                class_name=class_name,
                engine_name=engine_name,
                decision_name=decision_name,
            ),
            encoding="utf-8",
        )
        manager_path.write_text(
            MANAGER_TEMPLATE.format(
                engine_module=module_name,
                class_name=class_name,
                decision_name=decision_name,
            ),
            encoding="utf-8",
        )

    for p in [engine_path, manager_path]:
        try:
            py_compile.compile(str(p), doraise=True)
        except Exception as e:
            errors.append(f"Syntax hata {p}: {e}")

    bridge_res = None
    if not errors:
        bridge_res = create_bridge(bridge_name, manager_name, "main", overwrite=overwrite)
        if bridge_res["payload"]["errors"]:
            errors.extend(bridge_res["payload"]["errors"])

    score = 100 - min(60, len(errors) * 20) - min(30, len(warnings) * 5)
    score = max(0, score)
    decision = "ENGINE SKELETON READY" if not errors else "ENGINE SKELETON BLOCKED"

    payload = {
        "module": "205.0 SDK Engine Generator",
        "created_at": now_text(),
        "engine_id": engine_id,
        "engine_name": engine_name,
        "engine_module": module_name,
        "manager_module": manager_name,
        "bridge_name": bridge_name,
        "class_name": class_name,
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "paths": {
            "engine": str(engine_path),
            "manager": str(manager_path),
            "bridge": str(PY_DIR / bridge_name),
            "bridge_report": bridge_res["paths"]["report"] if bridge_res else None,
        }
    }

    ts = now_stamp()
    state = STATE_DIR / f"205_0_engine_generator_state_{ts}.json"
    report = REPORT_DIR / f"205_0_engine_generator_raporu_{ts}.txt"
    write_json(state, payload)

    lines = [
        "=" * 80,
        "205.0 SDK ENGINE GENERATOR",
        "=" * 80,
        f"Score       : {score} / 100",
        f"Decision    : {decision}",
        f"Engine ID   : {engine_id}",
        f"Engine Name : {engine_name}",
        f"Module      : {module_name}",
        f"Manager     : {manager_name}",
        f"Bridge      : {bridge_name}",
        "",
        "ERRORS",
        "-" * 80,
    ]
    lines.extend([f"- {e}" for e in errors] if errors else ["Errors: 0"])
    lines += ["", "WARNINGS", "-" * 80]
    lines.extend([f"- {w}" for w in warnings] if warnings else ["Warnings: 0"])
    lines += ["", "Dosyalar:", str(engine_path), str(manager_path), str(PY_DIR / bridge_name), str(state), str(report)]
    report.write_text("\\n".join(lines), encoding="utf-8")

    return {"payload": payload, "paths": {"state": str(state), "report": str(report), **payload["paths"]}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--module", default=None)
    parser.add_argument("--manager", default=None)
    parser.add_argument("--bridge", default=None)
    parser.add_argument("--no-overwrite", action="store_true")
    args = parser.parse_args()

    res = create_engine(
        engine_id=args.engine_id,
        engine_name=args.name,
        module_name=args.module,
        manager_name=args.manager,
        bridge_name=args.bridge,
        overwrite=not args.no_overwrite,
    )
    p = res["payload"]

    print("=" * 80)
    print("205.0 SDK ENGINE GENERATOR TAMAMLANDI")
    print("=" * 80)
    print(f"Score    : {p['score']} / 100")
    print(f"Decision : {p['decision']}")
    print(f"Errors   : {len(p['errors'])}")
    print(f"Warnings : {len(p['warnings'])}")
    print("")
    print("Dosyalar:")
    print(res["paths"]["engine"])
    print(res["paths"]["manager"])
    print(res["paths"]["bridge"])
    print(res["paths"]["report"])


if __name__ == "__main__":
    main()
