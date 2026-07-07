# -*- coding: utf-8 -*-
r"""
201 v3 - Event Bus Viewer / Auditor
NeoLegal Production Platform v2.0

Amaç:
- 201_event_bus.jsonl dosyasını okumak.
- Event türleri, severity dağılımı, son eventler ve hata/warning olaylarını raporlamak.
- Event Bus bütünlüğünü denetlemek.
- Production çalıştırmaz.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Genel audit:
python ".py\201_v3_Event_Bus_Viewer_Auditor.py"

Son 20 event:
python ".py\201_v3_Event_Bus_Viewer_Auditor.py" --tail=20

Sadece error/warning:
python ".py\201_v3_Event_Bus_Viewer_Auditor.py" --problems
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
EVENT_DIR = STATE_DIR / "event_bus"
EVENT_LOG = EVENT_DIR / "201_event_bus.jsonl"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_DIR.mkdir(parents=True, exist_ok=True)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def read_events():
    ensure_dirs()
    if not EVENT_LOG.exists():
        return [], []

    events = []
    invalid_lines = []

    lines = EVENT_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()

    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        try:
            event = json.loads(line)
            event["_line_no"] = idx
            events.append(event)
        except Exception:
            invalid_lines.append({
                "line_no": idx,
                "raw": line[:500]
            })

    return events, invalid_lines


def summarize(events, invalid_lines):
    by_type = {}
    by_source = {}
    by_severity = {}
    correlation_ids = {}
    missing_required = []

    required_fields = ["event_id", "correlation_id", "event_type", "source", "severity", "created_at", "payload"]

    for e in events:
        for field in required_fields:
            if field not in e:
                missing_required.append({
                    "line_no": e.get("_line_no"),
                    "missing": field,
                    "event": e
                })

        et = e.get("event_type", "UNKNOWN")
        src = e.get("source", "UNKNOWN")
        sev = e.get("severity", "UNKNOWN")
        cid = e.get("correlation_id", "UNKNOWN")

        by_type[et] = by_type.get(et, 0) + 1
        by_source[src] = by_source.get(src, 0) + 1
        by_severity[sev] = by_severity.get(sev, 0) + 1
        correlation_ids[cid] = correlation_ids.get(cid, 0) + 1

    problem_events = [
        e for e in events
        if str(e.get("severity", "")).upper() in ("ERROR", "WARNING", "CRITICAL")
    ]

    latest_events = sorted(
        events,
        key=lambda e: str(e.get("created_at", "")),
        reverse=True
    )

    return {
        "total_events": len(events),
        "invalid_lines": len(invalid_lines),
        "missing_required_count": len(missing_required),
        "by_type": by_type,
        "by_source": by_source,
        "by_severity": by_severity,
        "problem_events": problem_events,
        "latest_events": latest_events,
        "missing_required": missing_required,
        "correlation_count": len(correlation_ids),
    }


def evaluate(summary):
    score = 100
    errors = []
    warnings = []

    if summary["total_events"] == 0:
        score -= 20
        warnings.append("Event log boş.")

    if summary["invalid_lines"] > 0:
        score -= min(30, summary["invalid_lines"] * 5)
        errors.append(f"Bozuk event satırı var: {summary['invalid_lines']}")

    if summary["missing_required_count"] > 0:
        score -= min(20, summary["missing_required_count"] * 3)
        warnings.append(f"Zorunlu alanı eksik event var: {summary['missing_required_count']}")

    error_count = summary["by_severity"].get("ERROR", 0) + summary["by_severity"].get("CRITICAL", 0)
    warning_count = summary["by_severity"].get("WARNING", 0)

    if error_count > 0:
        score -= min(25, error_count * 5)
        errors.append(f"ERROR/CRITICAL event var: {error_count}")

    if warning_count > 0:
        score -= min(10, warning_count * 2)
        warnings.append(f"WARNING event var: {warning_count}")

    score = max(0, min(100, score))

    if errors:
        decision = "EVENT BUS AUDIT REVIEW"
    elif score >= 95:
        decision = "EVENT BUS AUDIT CLEAN"
    elif score >= 80:
        decision = "EVENT BUS AUDIT LOW REVIEW"
    else:
        decision = "EVENT BUS AUDIT REVIEW"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
    }


def write_report(args, events, invalid_lines, summary, result):
    tail_count = args.tail or 10

    if args.problems:
        display_events = summary["problem_events"][-tail_count:]
    else:
        display_events = summary["latest_events"][:tail_count]

    payload = {
        "module": "201 v3 Event Bus Viewer Auditor",
        "created_at": now_text(),
        "event_log": str(EVENT_LOG),
        "disk_free_gb": disk_free_gb(),
        "tail": tail_count,
        "problems_only": args.problems,
        "summary": {
            "total_events": summary["total_events"],
            "invalid_lines": summary["invalid_lines"],
            "missing_required_count": summary["missing_required_count"],
            "by_type": summary["by_type"],
            "by_source": summary["by_source"],
            "by_severity": summary["by_severity"],
            "problem_event_count": len(summary["problem_events"]),
            "correlation_count": summary["correlation_count"],
        },
        "display_events": display_events,
        "invalid_line_samples": invalid_lines[:20],
        "result": result,
    }

    json_path = STATE_DIR / f"201_v3_event_bus_auditor_state_{NOW}.json"
    txt_path = REPORT_DIR / f"201_v3_event_bus_auditor_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("201 v3 EVENT BUS VIEWER / AUDITOR")
    lines.append("=" * 80)
    lines.append(f"Tarih                 : {payload['created_at']}")
    lines.append(f"Score                 : {result['score']} / 100")
    lines.append(f"Decision              : {result['decision']}")
    lines.append(f"Event Log             : {EVENT_LOG}")
    lines.append(f"Total Events          : {summary['total_events']}")
    lines.append(f"Invalid Lines         : {summary['invalid_lines']}")
    lines.append(f"Missing Required      : {summary['missing_required_count']}")
    lines.append(f"Problem Events        : {len(summary['problem_events'])}")
    lines.append(f"Correlation Count     : {summary['correlation_count']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("DISTRIBUTION")
    lines.append("-" * 80)
    lines.append(f"By Severity           : {summary['by_severity']}")
    lines.append(f"By Type               : {summary['by_type']}")
    lines.append(f"By Source             : {summary['by_source']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("DISPLAY EVENTS")
    lines.append("-" * 80)

    if display_events:
        for e in display_events:
            lines.append(
                f"{e.get('created_at')} | {e.get('severity')} | "
                f"{e.get('event_type')} | {e.get('source')} | "
                f"line={e.get('_line_no')}"
            )
            payload_short = e.get("payload", {})
            if isinstance(payload_short, dict):
                lines.append(f"  payload: {json.dumps(payload_short, ensure_ascii=False)[:500]}")
    else:
        lines.append("Gösterilecek event yok.")

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
    lines.append("201 v3 production çalıştırmaz. Event log'u okur ve audit raporu üretir.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(EVENT_LOG))
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return payload, json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tail", type=int, default=10)
    parser.add_argument("--problems", action="store_true")
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    events, invalid_lines = read_events()
    summary = summarize(events, invalid_lines)
    result = evaluate(summary)
    payload, json_path, txt_path = write_report(args, events, invalid_lines, summary, result)

    print("=" * 80)
    print("201 v3 EVENT BUS VIEWER / AUDITOR TAMAMLANDI")
    print("=" * 80)
    print(f"Score           : {result['score']} / 100")
    print(f"Decision        : {result['decision']}")
    print(f"Errors          : {len(result['errors'])}")
    print(f"Warnings        : {len(result['warnings'])}")
    print(f"Total Events    : {summary['total_events']}")
    print(f"Problem Events  : {len(summary['problem_events'])}")
    print(f"Invalid Lines   : {summary['invalid_lines']}")
    print("")
    print("Dosyalar:")
    print(EVENT_LOG)
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
