# -*- coding: utf-8 -*-
from .config import SCHEDULER_DIR, SCHEDULER_SNAPSHOT, SCHEDULER_HISTORY, SCHEDULER_DASHBOARD, SCHEDULER_DECISIONS, REPORT_DIR, STATE_DIR
from .utils import ensure_dirs, now_stamp, write_json, append_jsonl

class SchedulerExporter:
    def export(self, payload, name="206_0_scheduler_sdk"):
        ensure_dirs(SCHEDULER_DIR, REPORT_DIR, STATE_DIR)
        ts = now_stamp()
        state = STATE_DIR / f"{name}_state_{ts}.json"
        report = REPORT_DIR / f"{name}_raporu_{ts}.txt"
        write_json(SCHEDULER_SNAPSHOT, payload)
        write_json(state, payload)
        append_jsonl(SCHEDULER_HISTORY, payload)
        append_jsonl(SCHEDULER_DECISIONS, payload.get("decision", {}))
        dashboard = {"scheduler_status": payload.get("validation", {}).get("decision"), "last_decision": payload.get("decision", {}).get("decision"), "recommended_batch_size": payload.get("decision", {}).get("recommended_batch_size"), "risk": payload.get("decision", {}).get("risk"), "context": payload.get("context", {})}
        write_json(SCHEDULER_DASHBOARD, dashboard)
        lines = ["="*80, "206.0 SCHEDULER SDK", "="*80, "Validation : " + str(payload.get("validation", {}).get("decision")), "Decision   : " + str(payload.get("decision", {}).get("decision")), "Risk       : " + str(payload.get("decision", {}).get("risk")), "Batch Size : " + str(payload.get("decision", {}).get("recommended_batch_size")), "", "Reason:", str(payload.get("decision", {}).get("reason")), "", "Dosyalar:", str(SCHEDULER_SNAPSHOT), str(SCHEDULER_DASHBOARD), str(state), str(report)]
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"snapshot": str(SCHEDULER_SNAPSHOT), "dashboard": str(SCHEDULER_DASHBOARD), "state": str(state), "report": str(report)}
