# -*- coding: utf-8 -*-
import json
from config import BASE_DIR, STATE_DIR, REPORT_DIR, LOG_DIR, PLATFORM_LOG_FILE, VALID_LEVELS
from utils import now_text, now_stamp, ensure_dirs, disk_free_gb, write_json

def read_logs(limit=None):
    ensure_dirs(STATE_DIR, REPORT_DIR, LOG_DIR)
    if not PLATFORM_LOG_FILE.exists():
        return [], []
    lines = PLATFORM_LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    if limit:
        lines = lines[-limit:]
    records = []
    invalid = []
    for i, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            rec["_line_no"] = i
            records.append(rec)
        except Exception:
            invalid.append({"line_no": i, "raw": line[:500]})
    return records, invalid

def summarize(records, invalid):
    by_level = {}
    by_source = {}
    missing_required = []
    required = ["log_id", "correlation_id", "level", "source", "message", "created_at", "payload"]
    for r in records:
        for field in required:
            if field not in r:
                missing_required.append({"line_no": r.get("_line_no"), "missing": field})
        level = r.get("level", "UNKNOWN")
        source = r.get("source", "UNKNOWN")
        by_level[level] = by_level.get(level, 0) + 1
        by_source[source] = by_source.get(source, 0) + 1
    problem_logs = [r for r in records if str(r.get("level", "")).upper() in ("WARNING", "ERROR", "CRITICAL")]
    return {
        "total": len(records),
        "invalid": len(invalid),
        "missing_required": len(missing_required),
        "by_level": by_level,
        "by_source": by_source,
        "problem_logs": problem_logs,
        "missing_required_samples": missing_required[:20],
    }

def evaluate(summary):
    score = 100
    errors = []
    warnings = []
    if summary["total"] == 0:
        score -= 20
        warnings.append("Log dosyası boş.")
    if summary["invalid"] > 0:
        score -= min(30, summary["invalid"] * 5)
        errors.append(f"Bozuk log satırı var: {summary['invalid']}")
    if summary["missing_required"] > 0:
        score -= min(20, summary["missing_required"] * 3)
        warnings.append(f"Zorunlu alan eksik log var: {summary['missing_required']}")
    err_count = summary["by_level"].get("ERROR", 0) + summary["by_level"].get("CRITICAL", 0)
    warn_count = summary["by_level"].get("WARNING", 0)
    if err_count:
        score -= min(25, err_count * 5)
        errors.append(f"ERROR/CRITICAL log var: {err_count}")
    if warn_count:
        score -= min(10, warn_count * 2)
        warnings.append(f"WARNING log var: {warn_count}")
    score = max(0, min(100, score))
    decision = "LOGGER AUDIT REVIEW" if errors else ("LOGGER AUDIT CLEAN" if score >= 95 else "LOGGER AUDIT LOW REVIEW")
    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}

def run(limit=50, problems=False):
    ensure_dirs(STATE_DIR, REPORT_DIR, LOG_DIR)
    ts = now_stamp()
    records, invalid = read_logs(limit=None)
    summary = summarize(records, invalid)
    result = evaluate(summary)

    if problems:
        display = summary["problem_logs"][-limit:]
    else:
        display = records[-limit:]

    state = STATE_DIR / f"203_logger_audit_state_{ts}.json"
    report = REPORT_DIR / f"203_logger_audit_raporu_{ts}.txt"
    payload = {
        "module": "203 Central Logger Auditor",
        "created_at": now_text(),
        "log_file": str(PLATFORM_LOG_FILE),
        "disk_free_gb": disk_free_gb(BASE_DIR),
        "summary": {k:v for k,v in summary.items() if k != "problem_logs"},
        "display_logs": display,
        "result": result,
    }
    write_json(state, payload)

    lines = [
        "="*80,
        "203 CENTRAL LOGGER AUDITOR",
        "="*80,
        f"Score          : {result['score']} / 100",
        f"Decision       : {result['decision']}",
        f"Total Logs     : {summary['total']}",
        f"Invalid Lines  : {summary['invalid']}",
        f"Problem Logs   : {len(summary['problem_logs'])}",
        f"By Level       : {summary['by_level']}",
        f"By Source      : {summary['by_source']}",
        "",
        "DISPLAY LOGS",
        "-"*80,
    ]
    for r in display:
        lines.append(f"{r.get('created_at')} | {r.get('level')} | {r.get('source')} | {r.get('message')}")
    lines += [
        "",
        "ERRORS",
        "-"*80,
    ]
    if result["errors"]:
        for e in result["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")
    lines += [
        "",
        "WARNINGS",
        "-"*80,
    ]
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")
    lines += [
        "",
        "Dosyalar:",
        str(PLATFORM_LOG_FILE),
        str(state),
        str(report),
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    return {"summary": summary, "result": result, "paths": {"log": str(PLATFORM_LOG_FILE), "state": str(state), "report": str(report)}}
