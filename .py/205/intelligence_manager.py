# -*- coding: utf-8 -*-
import argparse
from config_intelligence import (
    STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR,
    INTELLIGENCE_SCHEMA_FILE, INTELLIGENCE_CONTRACT_FILE, INTELLIGENCE_OUTPUT_FILE,
    METRICS_SNAPSHOT, METRICS_HISTORY, DASHBOARD_METRICS, TREND_FILE
)
from utils import now_stamp, now_text, ensure_dirs, safe_json, write_json
from intelligence_schema import INTELLIGENCE_INPUT_SCHEMA, INTELLIGENCE_OUTPUT_SCHEMA, ENGINE_CONTRACTS

def source_status():
    sources = {
        "metrics_snapshot": METRICS_SNAPSHOT,
        "metrics_history": METRICS_HISTORY,
        "dashboard_metrics": DASHBOARD_METRICS,
        "trend_file": TREND_FILE,
    }
    out = {}
    for key, path in sources.items():
        out[key] = {
            "path": str(path),
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else 0,
        }
    return out

def validate_framework():
    errors = []
    warnings = []

    sources = source_status()
    for key, info in sources.items():
        if not info["exists"]:
            warnings.append(f"Kaynak eksik: {key}")
        elif info["size"] == 0:
            warnings.append(f"Kaynak boş: {key}")

    if len(ENGINE_CONTRACTS) != 10:
        errors.append("Beklenen 10 intelligence engine contract tanımlı değil.")

    ids = [x.get("engine_id") for x in ENGINE_CONTRACTS]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate engine_id var.")

    required_outputs = [
        "production_analytics",
        "queue_intelligence",
        "worker_intelligence",
        "event_intelligence",
        "logger_intelligence",
        "forecast",
        "stability",
        "executive_summary",
    ]

    for key in required_outputs:
        if key not in INTELLIGENCE_OUTPUT_SCHEMA:
            errors.append(f"Output schema eksik: {key}")

    score = 100 - min(60, len(errors) * 15) - min(30, len(warnings) * 3)
    score = max(0, score)

    decision = "INTELLIGENCE FRAMEWORK BLOCKED" if errors else (
        "INTELLIGENCE FRAMEWORK READY" if score >= 90 else "INTELLIGENCE FRAMEWORK REVIEW"
    )

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "sources": sources,
    }

def run():
    ensure_dirs(STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR)
    ts = now_stamp()
    validation = validate_framework()

    framework = {
        "module": "205 v2 Trend Intelligence Framework",
        "created_at": now_text(),
        "input_schema": INTELLIGENCE_INPUT_SCHEMA,
        "output_schema": INTELLIGENCE_OUTPUT_SCHEMA,
        "engine_contracts": ENGINE_CONTRACTS,
        "validation": validation,
    }

    state = STATE_DIR / f"205_v2_intelligence_framework_state_{ts}.json"
    report = REPORT_DIR / f"205_v2_intelligence_framework_raporu_{ts}.txt"

    write_json(INTELLIGENCE_SCHEMA_FILE, {
        "input_schema": INTELLIGENCE_INPUT_SCHEMA,
        "output_schema": INTELLIGENCE_OUTPUT_SCHEMA,
    })
    write_json(INTELLIGENCE_CONTRACT_FILE, {"engine_contracts": ENGINE_CONTRACTS})
    write_json(INTELLIGENCE_OUTPUT_FILE, framework)
    write_json(state, framework)

    lines = [
        "="*80,
        "205 v2 TREND INTELLIGENCE FRAMEWORK",
        "="*80,
        f"Score           : {validation['score']} / 100",
        f"Decision        : {validation['decision']}",
        f"Errors          : {len(validation['errors'])}",
        f"Warnings        : {len(validation['warnings'])}",
        f"Engine Contracts: {len(ENGINE_CONTRACTS)}",
        "",
        "SOURCE STATUS",
        "-"*80,
    ]

    for key, info in validation["sources"].items():
        lines.append(f"{key:<20} : exists={info['exists']} | size={info['size']} | {info['path']}")

    lines += [
        "",
        "ENGINE CONTRACTS",
        "-"*80,
    ]

    for item in ENGINE_CONTRACTS:
        lines.append(f"{item['engine_id']:<6} | {item['name']:<28} | {item['status']}")

    lines += [
        "",
        "ERRORS",
        "-"*80,
    ]

    if validation["errors"]:
        for e in validation["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines += [
        "",
        "WARNINGS",
        "-"*80,
    ]

    if validation["warnings"]:
        for w in validation["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines += [
        "",
        "NOT:",
        "205 v2 bu sürümde hesaplama yapmaz; Intelligence Framework ve engine sözleşmelerini kurar.",
        "",
        "Dosyalar:",
        str(INTELLIGENCE_SCHEMA_FILE),
        str(INTELLIGENCE_CONTRACT_FILE),
        str(INTELLIGENCE_OUTPUT_FILE),
        str(state),
        str(report),
    ]

    report.write_text("\n".join(lines), encoding="utf-8")

    return {
        "framework": framework,
        "result": validation,
        "paths": {
            "schema": str(INTELLIGENCE_SCHEMA_FILE),
            "contracts": str(INTELLIGENCE_CONTRACT_FILE),
            "framework": str(INTELLIGENCE_OUTPUT_FILE),
            "state": str(state),
            "report": str(report),
        }
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    res = run()
    result = res["result"]

    print("="*80)
    print("205 v2 TREND INTELLIGENCE FRAMEWORK TAMAMLANDI")
    print("="*80)
    print(f"Score           : {result['score']} / 100")
    print(f"Decision        : {result['decision']}")
    print(f"Errors          : {len(result['errors'])}")
    print(f"Warnings        : {len(result['warnings'])}")
    print(f"Engine Contracts: {len(res['framework']['engine_contracts'])}")
    print("")
    print("Dosyalar:")
    print(res["paths"]["schema"])
    print(res["paths"]["contracts"])
    print(res["paths"]["framework"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
