# -*- coding: utf-8 -*-
import argparse
from config import STATE_DIR, REPORT_DIR, TREND_DIR, TREND_FILE, TREND_HISTORY
from utils import now_stamp, now_text, ensure_dirs, write_json, append_jsonl
from trend import build_trends
from evaluator import evaluate

def run():
    ensure_dirs(STATE_DIR, REPORT_DIR, TREND_DIR)
    ts = now_stamp()
    trends = build_trends()
    result = evaluate(trends)

    payload = {
        "module": "205 Metrics History & Trend Engine",
        "created_at": now_text(),
        "trends": trends,
        "result": result,
    }

    state = STATE_DIR / f"205_metrics_trends_state_{ts}.json"
    report = REPORT_DIR / f"205_metrics_trends_raporu_{ts}.txt"

    write_json(TREND_FILE, payload)
    write_json(state, payload)
    append_jsonl(TREND_HISTORY, payload)

    current = trends.get("current", {})
    growth = trends.get("growth", {})
    quality = trends.get("quality", {})
    source = trends.get("source", {})

    lines = [
        "="*80,
        "205 METRICS HISTORY & TREND ENGINE",
        "="*80,
        f"Score              : {result['score']} / 100",
        f"Decision           : {result['decision']}",
        f"Errors             : {len(result['errors'])}",
        f"Warnings           : {len(result['warnings'])}",
        "",
        "SOURCE",
        "-"*80,
        f"History Rows       : {source.get('history_rows')}",
        f"History Invalid    : {source.get('history_invalid')}",
        f"Has Snapshot       : {source.get('has_latest_snapshot')}",
        f"Has Dashboard Data : {source.get('has_dashboard_metrics')}",
        "",
        "CURRENT",
        "-"*80,
        f"DB Count           : {current.get('db_count')}",
        f"Queue Total        : {current.get('queue_total')}",
        f"Queue Finished     : {current.get('queue_finished')}",
        f"Queue Failed       : {current.get('queue_failed')}",
        f"Completion Rate    : {current.get('queue_completion_rate')}%",
        f"Workers Total      : {current.get('workers_total')}",
        f"Event Total        : {current.get('event_total')}",
        f"Log Total          : {current.get('log_total')}",
        "",
        "GROWTH",
        "-"*80,
        f"DB Delta           : {growth.get('db_delta')}",
        f"Event Delta        : {growth.get('event_delta')}",
        f"Log Delta          : {growth.get('log_delta')}",
        f"Queue Finished Δ   : {growth.get('queue_finished_delta')}",
        "",
        "QUALITY",
        "-"*80,
        f"Average Score      : {quality.get('avg_score')}",
        f"Latest Score       : {quality.get('latest_score')}",
        f"Latest Decision    : {quality.get('latest_decision')}",
        "",
        "ERRORS",
        "-"*80,
    ]

    if result["errors"]:
        for e in result["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines += ["", "WARNINGS", "-"*80]
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines += [
        "",
        "Dosyalar:",
        str(TREND_FILE),
        str(TREND_HISTORY),
        str(state),
        str(report),
    ]

    report.write_text("\n".join(lines), encoding="utf-8")
    return {"payload": payload, "result": result, "paths": {"trend": str(TREND_FILE), "history": str(TREND_HISTORY), "state": str(state), "report": str(report)}}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trend", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    res = run()
    result = res["result"]
    trends = res["payload"]["trends"]
    current = trends.get("current", {})
    growth = trends.get("growth", {})

    print("="*80)
    print("205 METRICS HISTORY & TREND ENGINE TAMAMLANDI")
    print("="*80)
    print(f"Score           : {result['score']} / 100")
    print(f"Decision        : {result['decision']}")
    print(f"Errors          : {len(result['errors'])}")
    print(f"Warnings        : {len(result['warnings'])}")
    print(f"DB Count        : {current.get('db_count')}")
    print(f"DB Delta        : {growth.get('db_delta')}")
    print(f"Event Delta     : {growth.get('event_delta')}")
    print(f"Log Delta       : {growth.get('log_delta')}")
    print("")
    print("Dosyalar:")
    print(res["paths"]["trend"])
    print(res["paths"]["report"])

if __name__ == "__main__":
    main()
