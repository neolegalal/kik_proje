# -*- coding: utf-8 -*-
r"""
201 v2 - Event Publisher Integration
NeoLegal Production Platform v2.0

Amaç:
- Platformdaki son state dosyalarını okuyup Event Bus'a standart event olarak yayınlamak.
- 200 Core, 199 Health/Orchestrator, 198 Worker Execution, 197 Recovery sonuçlarını event'e dönüştürmek.
- Production çalıştırmaz.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Dry-run:
python ".py\201_v2_Event_Publisher_Integration.py"

Gerçek publish:
python ".py\201_v2_Event_Publisher_Integration.py" --publish
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


EVENT_SOURCES = [
    {
        "name": "PlatformCore",
        "pattern": "200_pkg_core_state_*.json",
        "event_type": "PlatformCoreChecked",
        "decision_path": ["result", "decision"],
        "score_path": ["result", "score"],
    },
    {
        "name": "PlatformCoreV1",
        "pattern": "200_v1_platform_core_state_*.json",
        "event_type": "PlatformCoreChecked",
        "decision_path": ["result", "decision"],
        "score_path": ["result", "score"],
    },
    {
        "name": "Configuration",
        "pattern": "200_v2_configuration_manager_state_*.json",
        "event_type": "ConfigLoaded",
        "decision_path": ["validation", "decision"],
        "score_path": ["validation", "score"],
    },
    {
        "name": "PlatformHealth",
        "pattern": "199_v2_platform_health_state_*.json",
        "event_type": "HealthChecked",
        "decision_path": ["result", "decision"],
        "score_path": ["result", "score"],
    },
    {
        "name": "Orchestrator",
        "pattern": "199_v3_orchestrator_state_*.json",
        "event_type": "OrchestratorCompleted",
        "decision_path": ["result", "decision"],
        "score_path": ["result", "score"],
    },
    {
        "name": "WorkerExecution",
        "pattern": "198_v3_controlled_worker_execution_state_*.json",
        "event_type": "WorkerExecutionCompleted",
        "decision_path": ["result", "decision"],
        "score_path": ["result", "score"],
    },
    {
        "name": "Recovery",
        "pattern": "197_v4_recovery_manager_state_*.json",
        "event_type": "RecoveryCompleted",
        "decision_path": ["result", "decision"],
        "score_path": ["result", "score"],
    },
    {
        "name": "DynamicCertification",
        "pattern": "196B_v2_controlled_dynamic_state_*.json",
        "event_type": "CertificationPassed",
        "decision_path": ["result", "decision"],
        "score_path": ["result", "score"],
    },
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


def safe_read(path: Path, limit_chars=1000000):
    if not path or not path.exists():
        return ""
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")[:limit_chars]
        except Exception:
            pass
    return ""


def safe_json(path: Path):
    try:
        return json.loads(safe_read(path))
    except Exception:
        return None


def latest_file(pattern):
    files = list(STATE_DIR.glob(pattern))
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def get_nested(data, path, default=None):
    cur = data
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    return cur


def severity_from_decision(decision):
    text = str(decision or "").upper()
    if any(x in text for x in ["BLOCKED", "FAILED", "INVALID", "REQUIRED", "NOT CERTIFIED"]):
        return "ERROR"
    if any(x in text for x in ["REVIEW", "WARNING", "CONDITIONAL"]):
        return "WARNING"
    return "INFO"


def make_event(event_type, source, payload, severity="INFO", correlation_id=None):
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
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def collect_events():
    collected = []

    for src in EVENT_SOURCES:
        f = latest_file(src["pattern"])
        if not f:
            collected.append({
                "source": src["name"],
                "status": "MISSING",
                "event": None,
                "message": f"State bulunamadı: {src['pattern']}"
            })
            continue

        data = safe_json(f)
        if not data:
            collected.append({
                "source": src["name"],
                "status": "INVALID_JSON",
                "event": None,
                "file": str(f),
                "message": "State JSON okunamadı."
            })
            continue

        decision = get_nested(data, src["decision_path"])
        score = get_nested(data, src["score_path"])

        payload = {
            "state_file": str(f),
            "decision": decision,
            "score": score,
            "module": data.get("module"),
            "created_at": data.get("created_at"),
        }

        # Bazı özel alanları da ekleyelim
        if src["name"] == "WorkerExecution":
            op = data.get("operation", {})
            payload.update({
                "job_id": op.get("job_id"),
                "worker_id": op.get("worker_id"),
                "batch_size": op.get("batch_size"),
                "db_delta": op.get("db_delta"),
            })

        if src["name"] == "Orchestrator":
            op = (data.get("latest_worker_state_data") or {}).get("operation", {})
            payload.update({
                "job_id": op.get("job_id"),
                "db_delta": op.get("db_delta"),
            })

        event = make_event(
            event_type=src["event_type"],
            source=src["name"],
            severity=severity_from_decision(decision),
            payload=payload,
        )

        collected.append({
            "source": src["name"],
            "status": "READY",
            "event": event,
            "file": str(f),
            "message": "Event hazırlandı."
        })

    return collected


def event_log_summary():
    if not EVENT_LOG.exists():
        return {"total": 0, "invalid": 0, "by_type": {}, "by_severity": {}}

    total = 0
    invalid = 0
    by_type = {}
    by_severity = {}

    for line in EVENT_LOG.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        total += 1
        try:
            e = json.loads(line)
            et = e.get("event_type", "UNKNOWN")
            sv = e.get("severity", "UNKNOWN")
            by_type[et] = by_type.get(et, 0) + 1
            by_severity[sv] = by_severity.get(sv, 0) + 1
        except Exception:
            invalid += 1

    return {"total": total, "invalid": invalid, "by_type": by_type, "by_severity": by_severity}


def evaluate(collected, publish_mode):
    score = 100
    errors = []
    warnings = []

    missing = [x for x in collected if x["status"] == "MISSING"]
    invalid = [x for x in collected if x["status"] == "INVALID_JSON"]
    ready = [x for x in collected if x["status"] == "READY"]

    if invalid:
        score -= min(40, len(invalid) * 10)
        errors.append(f"Okunamayan state JSON sayısı: {len(invalid)}")

    if missing:
        score -= min(20, len(missing) * 2)
        warnings.append(f"Eksik state kaynağı sayısı: {len(missing)}")

    if not ready:
        score -= 40
        errors.append("Publish edilecek event bulunamadı.")

    if not publish_mode:
        score -= 5
        warnings.append("Dry-run: eventler log'a yazılmadı.")

    if disk_free_gb() < 50:
        score -= 20
        errors.append("Disk alanı düşük.")

    score = max(0, min(100, score))

    if errors:
        decision = "EVENT PUBLISHER BLOCKED"
    elif score >= 95:
        decision = "EVENT PUBLISHER READY"
    elif score >= 80:
        decision = "EVENT PUBLISHER REVIEW"
    else:
        decision = "EVENT PUBLISHER BLOCKED"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "ready_count": len(ready),
        "missing_count": len(missing),
        "invalid_count": len(invalid),
    }


def write_report(collected, published_events, publish_mode):
    validation = evaluate(collected, publish_mode)
    summary = event_log_summary()

    payload = {
        "module": "201 v2 Event Publisher Integration",
        "created_at": now_text(),
        "publish_mode": publish_mode,
        "event_log": str(EVENT_LOG),
        "disk_free_gb": disk_free_gb(),
        "collected": collected,
        "published_count": len(published_events),
        "published_events": published_events,
        "event_log_summary": summary,
        "validation": validation,
    }

    json_path = STATE_DIR / f"201_v2_event_publisher_state_{NOW}.json"
    txt_path = REPORT_DIR / f"201_v2_event_publisher_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("201 v2 EVENT PUBLISHER INTEGRATION")
    lines.append("=" * 80)
    lines.append(f"Tarih            : {payload['created_at']}")
    lines.append(f"Publish Mode     : {publish_mode}")
    lines.append(f"Score            : {validation['score']} / 100")
    lines.append(f"Decision         : {validation['decision']}")
    lines.append(f"Ready Events     : {validation['ready_count']}")
    lines.append(f"Published        : {len(published_events)}")
    lines.append(f"Missing Sources  : {validation['missing_count']}")
    lines.append(f"Invalid Sources  : {validation['invalid_count']}")
    lines.append(f"Event Log Total  : {summary['total']}")
    lines.append(f"Invalid Log Lines: {summary['invalid']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("COLLECTED EVENTS")
    lines.append("-" * 80)
    for item in collected:
        ev = item.get("event")
        lines.append(f"{item['source']:<24} : {item['status']:<12} | {ev.get('event_type') if ev else '-'} | {item.get('message')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("EVENT LOG SUMMARY")
    lines.append("-" * 80)
    lines.append(f"By Severity : {summary['by_severity']}")
    lines.append(f"By Type     : {summary['by_type']}")
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
    lines.append("201 v2 production çalıştırmaz. Son state dosyalarını event'e dönüştürür.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(EVENT_LOG))
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    return payload, json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    collected = collect_events()
    published_events = []

    if args.publish:
        for item in collected:
            if item["status"] == "READY" and item.get("event"):
                publish(item["event"])
                published_events.append(item["event"])

    payload, json_path, txt_path = write_report(collected, published_events, args.publish)
    validation = payload["validation"]
    summary = payload["event_log_summary"]

    print("=" * 80)
    print("201 v2 EVENT PUBLISHER INTEGRATION TAMAMLANDI")
    print("=" * 80)
    print(f"Publish Mode : {args.publish}")
    print(f"Score        : {validation['score']} / 100")
    print(f"Decision     : {validation['decision']}")
    print(f"Ready Events : {validation['ready_count']}")
    print(f"Published    : {len(published_events)}")
    print(f"Errors       : {len(validation['errors'])}")
    print(f"Warnings     : {len(validation['warnings'])}")
    print(f"Log Total    : {summary['total']}")
    print("")
    print("Dosyalar:")
    print(EVENT_LOG)
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
