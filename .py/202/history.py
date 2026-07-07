# -*- coding: utf-8 -*-
import json
from config import STATE_DIR, REPORT_DIR, SCHEDULER_DIR, SCHEDULER_HISTORY_FILE
from utils import now_text, now_stamp, ensure_dirs, write_json, safe_read

def append_history(record):
    ensure_dirs(STATE_DIR, REPORT_DIR, SCHEDULER_DIR)
    record["created_at"] = now_text()
    with SCHEDULER_HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def read_history(limit=50):
    ensure_dirs(STATE_DIR, REPORT_DIR, SCHEDULER_DIR)
    if not SCHEDULER_HISTORY_FILE.exists():
        return []
    lines = safe_read(SCHEDULER_HISTORY_FILE).splitlines()
    events = []
    for line in lines[-limit:]:
        try:
            events.append(json.loads(line))
        except Exception:
            events.append({"status":"INVALID_LINE","raw":line[:300]})
    return events

def run(limit=50):
    ensure_dirs(STATE_DIR, REPORT_DIR, SCHEDULER_DIR)
    ts = now_stamp()
    events = read_history(limit=limit)
    invalid = sum(1 for e in events if e.get("status") == "INVALID_LINE")
    result = {"score": 100 if invalid == 0 else 80, "decision": "SCHEDULER HISTORY READY" if invalid == 0 else "SCHEDULER HISTORY REVIEW", "errors": [], "warnings": []}
    state = STATE_DIR / f"202_pkg_history_state_{ts}.json"
    report = REPORT_DIR / f"202_pkg_history_raporu_{ts}.txt"
    payload = {"module":"202 Scheduler History","created_at":now_text(),"history_file":str(SCHEDULER_HISTORY_FILE),"events":events,"result":result}
    write_json(state, payload)
    report.write_text("\n".join([
        "="*80,
        "202 PACKAGE - SCHEDULER HISTORY",
        "="*80,
        f"Score    : {result['score']} / 100",
        f"Decision : {result['decision']}",
        f"Events   : {len(events)}",
        f"Invalid  : {invalid}",
        "",
        "Dosyalar:",
        str(SCHEDULER_HISTORY_FILE),
        str(state),
        str(report),
    ]), encoding="utf-8")
    return {"events": events, "result": result, "paths": {"history": str(SCHEDULER_HISTORY_FILE), "state": str(state), "report": str(report)}}
