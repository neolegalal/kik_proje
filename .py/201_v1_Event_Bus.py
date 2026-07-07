# -*- coding: utf-8 -*-
r"""
201 v1 - Event Bus
NeoLegal Production Platform v2.0

Amaç:
- Platform olaylarını merkezi bir event log'a yazmak.
- Modüller arası iletişim için temel event altyapısını kurmak.
- JSONL formatında append-only event kaydı oluşturmak.
- Production çalıştırmaz.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Durum:
python ".py\201_v1_Event_Bus.py" --status

Test event yayınla:
python ".py\201_v1_Event_Bus.py" --publish-test

Son eventleri raporla:
python ".py\201_v1_Event_Bus.py" --tail=20
"""

import argparse
import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
EVENT_DIR = STATE_DIR / "event_bus"
EVENT_LOG = EVENT_DIR / "201_event_bus.jsonl"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

KNOWN_EVENT_TYPES = [
    "PlatformStarted",
    "PlatformStopped",
    "HealthChecked",
    "RegistryUpdated",
    "ConfigLoaded",
    "QueueCreated",
    "JobCreated",
    "JobAssigned",
    "JobStarted",
    "JobFinished",
    "JobFailed",
    "WorkerStarted",
    "WorkerFinished",
    "ProductionStarted",
    "ProductionFinished",
    "RecoveryStarted",
    "RecoveryCompleted",
    "CertificationStarted",
    "CertificationPassed",
    "CertificationFailed",
    "DashboardUpdated",
    "SystemWarning",
    "SystemError",
    "TestEvent",
]


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    EVENT_DIR.mkdir(parents=True, exist_ok=True)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def make_event(event_type, source="201 Event Bus", severity="INFO", payload=None, correlation_id=None):
    if payload is None:
        payload = {}

    return {
        "event_id": str(uuid.uuid4()),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "event_type": event_type,
        "source": source,
        "severity": severity,
        "created_at": now_text(),
        "payload": payload,
    }


def publish(event):
    ensure_dirs()
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def read_events(limit=None):
    ensure_dirs()
    if not EVENT_LOG.exists():
        return []

    lines = EVENT_LOG.read_text(encoding="utf-8", errors="ignore").splitlines()
    if limit:
        lines = lines[-limit:]

    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except Exception:
            events.append({
                "event_type": "INVALID_EVENT_LINE",
                "severity": "ERROR",
                "raw": line[:500],
            })
    return events


def event_summary(events):
    by_type = {}
    by_severity = {}
    invalid = 0

    for e in events:
        et = e.get("event_type", "UNKNOWN")
        sev = e.get("severity", "UNKNOWN")
        by_type[et] = by_type.get(et, 0) + 1
        by_severity[sev] = by_severity.get(sev, 0) + 1
        if et == "INVALID_EVENT_LINE":
            invalid += 1

    return {
        "total": len(events),
        "by_type": by_type,
        "by_severity": by_severity,
        "invalid": invalid,
    }


def validate_bus():
    events = read_events()
    summary = event_summary(events)

    score = 100
    errors = []
    warnings = []

    if not EVENT_DIR.exists():
        score -= 30
        errors.append("Event bus klasörü yok.")

    if summary["invalid"] > 0:
        score -= min(30, summary["invalid"] * 5)
        errors.append("Bozuk event satırı var.")

    if not EVENT_LOG.exists():
        warnings.append("Event log henüz oluşmamış.")
        score -= 5

    if disk_free_gb() < 50:
        score -= 20
        errors.append("Disk alanı düşük.")

    score = max(0, min(100, score))

    if errors:
        decision = "EVENT BUS BLOCKED"
    elif score >= 95:
        decision = "EVENT BUS READY"
    elif score >= 80:
        decision = "EVENT BUS REVIEW"
    else:
        decision = "EVENT BUS BLOCKED"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "summary": summary,
    }


def write_report(action, events_tail=None, published_event=None):
    events = read_events()
    validation = validate_bus()
    summary = validation["summary"]

    payload = {
        "module": "201 v1 Event Bus",
        "created_at": now_text(),
        "action": action,
        "base_dir": str(BASE_DIR),
        "event_dir": str(EVENT_DIR),
        "event_log": str(EVENT_LOG),
        "disk_free_gb": disk_free_gb(),
        "known_event_types": KNOWN_EVENT_TYPES,
        "published_event": published_event,
        "tail": events_tail or [],
        "validation": validation,
    }

    json_path = STATE_DIR / f"201_v1_event_bus_state_{NOW}.json"
    txt_path = REPORT_DIR / f"201_v1_event_bus_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("201 v1 EVENT BUS")
    lines.append("=" * 80)
    lines.append(f"Tarih          : {payload['created_at']}")
    lines.append(f"Action         : {action}")
    lines.append(f"Score          : {validation['score']} / 100")
    lines.append(f"Decision       : {validation['decision']}")
    lines.append(f"Disk Free      : {payload['disk_free_gb']} GB")
    lines.append(f"Event Log      : {EVENT_LOG}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("EVENT SUMMARY")
    lines.append("-" * 80)
    lines.append(f"Total Events   : {summary['total']}")
    lines.append(f"Invalid Lines  : {summary['invalid']}")
    lines.append(f"By Severity    : {summary['by_severity']}")
    lines.append(f"By Type        : {summary['by_type']}")
    lines.append("")

    if published_event:
        lines.append("-" * 80)
        lines.append("PUBLISHED EVENT")
        lines.append("-" * 80)
        lines.append(json.dumps(published_event, ensure_ascii=False, indent=2))
        lines.append("")

    if events_tail:
        lines.append("-" * 80)
        lines.append("EVENT TAIL")
        lines.append("-" * 80)
        for e in events_tail:
            lines.append(json.dumps(e, ensure_ascii=False))
        lines.append("")

    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)
    if validation["errors"]:
        for e in validation["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)
    if validation["warnings"]:
        for w in validation["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines.append("")
    lines.append("NOT:")
    lines.append("201 v1 production çalıştırmaz. Event Bus altyapısını kurar ve event log yazar.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(EVENT_LOG))
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return payload, json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--publish-test", action="store_true")
    parser.add_argument("--tail", type=int, default=0)
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    action = "status"
    published = None
    tail = []

    if args.publish_test:
        action = "publish-test"
        published = publish(make_event(
            "TestEvent",
            source="201 v1 Event Bus",
            severity="INFO",
            payload={
                "message": "Event Bus test event",
                "platform": "NeoLegal Production Platform",
            }
        ))

    if args.tail:
        action = f"tail-{args.tail}" if action == "status" else action
        tail = read_events(limit=args.tail)

    payload, json_path, txt_path = write_report(action, tail, published)
    validation = payload["validation"]
    summary = validation["summary"]

    print("=" * 80)
    print("201 v1 EVENT BUS TAMAMLANDI")
    print("=" * 80)
    print(f"Action       : {action}")
    print(f"Score        : {validation['score']} / 100")
    print(f"Decision     : {validation['decision']}")
    print(f"Errors       : {len(validation['errors'])}")
    print(f"Warnings     : {len(validation['warnings'])}")
    print(f"Total Events : {summary['total']}")
    print(f"Invalid      : {summary['invalid']}")
    print("")
    print("Dosyalar:")
    print(EVENT_LOG)
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
