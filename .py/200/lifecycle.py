# -*- coding: utf-8 -*-
from config import STATE_DIR, REPORT_DIR
from utils import now_stamp, now_text, ensure_dirs, write_json

def run(action="startup"):
    ensure_dirs(STATE_DIR, REPORT_DIR)
    ts = now_stamp()
    allowed = ["startup", "shutdown", "maintenance", "status"]
    status = "PASS" if action in allowed else "FAIL"
    result = {
        "score": 100 if status == "PASS" else 0,
        "decision": "LIFECYCLE READY" if status == "PASS" else "LIFECYCLE INVALID",
        "errors": [] if status == "PASS" else [f"Geçersiz lifecycle action: {action}"],
        "warnings": [],
    }
    payload = {"module": "200 Package Lifecycle Manager", "created_at": now_text(), "action": action, "status": status, "result": result}
    state = STATE_DIR / f"200_pkg_lifecycle_state_{ts}.json"
    report = REPORT_DIR / f"200_pkg_lifecycle_raporu_{ts}.txt"
    write_json(state, payload)
    report.write_text("\n".join([
        "="*80,
        "200 PACKAGE - LIFECYCLE MANAGER",
        "="*80,
        f"Action   : {action}",
        f"Score    : {result['score']} / 100",
        f"Decision : {result['decision']}",
        "",
        "Dosyalar:",
        str(state),
        str(report),
    ]), encoding="utf-8")
    return {"payload": payload, "result": result, "paths": {"state": str(state), "report": str(report)}}
