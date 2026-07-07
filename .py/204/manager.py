# -*- coding: utf-8 -*-
import argparse
from collector import collect_all
from evaluator import evaluate
from config import STATE_DIR, REPORT_DIR, METRICS_DIR, METRICS_STORE, METRICS_HISTORY
from utils import now_stamp, now_text, ensure_dirs, write_json, append_jsonl
from dashboard import run as run_dashboard

def write_report(metrics, result):
    ensure_dirs(STATE_DIR, REPORT_DIR, METRICS_DIR)
    ts = now_stamp()
    payload = {
        "module": "204 Metrics & Monitoring",
        "created_at": now_text(),
        "metrics": metrics,
        "result": result,
    }
    state = STATE_DIR / f"204_metrics_state_{ts}.json"
    report = REPORT_DIR / f"204_metrics_raporu_{ts}.txt"

    write_json(METRICS_STORE, payload)
    write_json(state, payload)
    append_jsonl(METRICS_HISTORY, payload)

    lines = [
        "="*80,
        "204 METRICS & MONITORING",
        "="*80,
        f"Score              : {result['score']} / 100",
        f"Decision           : {result['decision']}",
        f"Errors             : {len(result['errors'])}",
        f"Warnings           : {len(result['warnings'])}",
        "",
        "SYSTEM",
        "-"*80,
        f"Disk Free          : {metrics['disk'].get('free_gb')} GB",
        f"DB Count           : {metrics['db'].get('count')}",
        f"DB Status          : {metrics['db'].get('status')}",
        "",
        "QUEUE / WORKERS",
        "-"*80,
        f"Queue Total        : {metrics['queue'].get('total')}",
        f"Queue Waiting      : {metrics['queue'].get('waiting')}",
        f"Queue Running      : {metrics['queue'].get('running')}",
        f"Queue Finished     : {metrics['queue'].get('finished')}",
        f"Queue Failed       : {metrics['queue'].get('failed')}",
        f"Completion Rate    : {metrics['queue'].get('completion_rate')}%",
        f"Workers Total      : {metrics['workers'].get('total')}",
        f"Workers Idle       : {metrics['workers'].get('idle')}",
        f"Workers Running    : {metrics['workers'].get('running')}",
        "",
        "EVENTS / LOGS",
        "-"*80,
        f"Event Total        : {metrics['events'].get('total')}",
        f"Event Invalid      : {metrics['events'].get('invalid')}",
        f"Event Severity     : {metrics['events'].get('by_severity')}",
        f"Log Total          : {metrics['logs'].get('total')}",
        f"Log Invalid        : {metrics['logs'].get('invalid')}",
        f"Log Level          : {metrics['logs'].get('by_severity')}",
        "",
        "Dosyalar:",
        str(METRICS_STORE),
        str(METRICS_HISTORY),
        str(state),
        str(report),
    ]

    report.write_text("\n".join(lines), encoding="utf-8")
    return {"payload": payload, "paths": {"store": str(METRICS_STORE), "history": str(METRICS_HISTORY), "state": str(state), "report": str(report)}}

def run_snapshot():
    metrics = collect_all()
    result = evaluate(metrics)
    return write_report(metrics, result)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()

    if args.dashboard:
        res = run_dashboard()
        result = res["result"]
        dash = res["payload"].get("dashboard") or {}
        print("="*80)
        print("204 v2 METRICS DASHBOARD DATA TAMAMLANDI")
        print("="*80)
        print(f"Score          : {result['score']} / 100")
        print(f"Decision       : {result['decision']}")
        print(f"Errors         : {len(result['errors'])}")
        print(f"Warnings       : {len(result['warnings'])}")
        if dash:
            print(f"DB Count       : {dash['system']['db_count']}")
            print(f"Queue Total    : {dash['queue']['total']}")
            print(f"Workers Total  : {dash['workers']['total']}")
            print(f"Events Total   : {dash['events']['total']}")
            print(f"Logs Total     : {dash['logs']['total']}")
        print("")
        print("Dosyalar:")
        print(res["paths"]["dashboard"])
        print(res["paths"]["report"])
        return

    res = run_snapshot()
    result = res["payload"]["result"]
    metrics = res["payload"]["metrics"]

    print("="*80)
    print("204 METRICS & MONITORING TAMAMLANDI")
    print("="*80)
    print(f"Score           : {result['score']} / 100")
    print(f"Decision        : {result['decision']}")
    print(f"Errors          : {len(result['errors'])}")
    print(f"Warnings        : {len(result['warnings'])}")
    print(f"DB Count        : {metrics['db'].get('count')}")
    print(f"Queue Total     : {metrics['queue'].get('total')}")
    print(f"Queue Finished  : {metrics['queue'].get('finished')}")
    print(f"Workers Total   : {metrics['workers'].get('total')}")
    print(f"Event Total     : {metrics['events'].get('total')}")
    print(f"Log Total       : {metrics['logs'].get('total')}")
    print("")
    print("Dosyalar:")
    print(res["paths"]["store"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
