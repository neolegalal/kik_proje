# -*- coding: utf-8 -*-
import json
import uuid
from config import BASE_DIR, STATE_DIR, REPORT_DIR, LOG_DIR, PLATFORM_LOG_FILE, VALID_LEVELS
from utils import now_text, now_stamp, ensure_dirs, disk_free_gb, write_json

def make_log(level="INFO", source="203 Logger", message="", payload=None, correlation_id=None):
    level = str(level).upper()
    if level not in VALID_LEVELS:
        level = "INFO"

    return {
        "log_id": str(uuid.uuid4()),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "level": level,
        "source": source,
        "message": message,
        "created_at": now_text(),
        "payload": payload or {},
    }

def write_log(record):
    ensure_dirs(STATE_DIR, REPORT_DIR, LOG_DIR)
    with PLATFORM_LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record

def test_log():
    record = make_log(
        level="INFO",
        source="203 Central Logger",
        message="Central logger test log",
        payload={"platform": "NeoLegal Production Platform", "test": True},
    )
    return write_log(record)

def run_test():
    ensure_dirs(STATE_DIR, REPORT_DIR, LOG_DIR)
    ts = now_stamp()
    record = test_log()
    result = {"score": 100, "decision": "LOGGER READY", "errors": [], "warnings": []}
    state = STATE_DIR / f"203_logger_test_state_{ts}.json"
    report = REPORT_DIR / f"203_logger_test_raporu_{ts}.txt"
    payload = {
        "module": "203 Central Logger Test",
        "created_at": now_text(),
        "log_file": str(PLATFORM_LOG_FILE),
        "disk_free_gb": disk_free_gb(BASE_DIR),
        "record": record,
        "result": result,
    }
    write_json(state, payload)
    report.write_text("\n".join([
        "="*80,
        "203 CENTRAL LOGGER TEST",
        "="*80,
        f"Score    : {result['score']} / 100",
        f"Decision : {result['decision']}",
        f"Log File : {PLATFORM_LOG_FILE}",
        "",
        "LOG RECORD",
        "-"*80,
        json.dumps(record, ensure_ascii=False, indent=2),
        "",
        "Dosyalar:",
        str(PLATFORM_LOG_FILE),
        str(state),
        str(report),
    ]), encoding="utf-8")
    return {"record": record, "result": result, "paths": {"log": str(PLATFORM_LOG_FILE), "state": str(state), "report": str(report)}}
