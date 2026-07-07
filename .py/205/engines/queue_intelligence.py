# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

QUEUE_DIR = INTELLIGENCE_DIR / "queue"
QUEUE_INTELLIGENCE_FILE = QUEUE_DIR / "205_2_queue_intelligence.json"
QUEUE_SCORE_FILE = QUEUE_DIR / "205_2_queue_score.json"
QUEUE_RECOMMENDATION_FILE = QUEUE_DIR / "205_2_queue_recommendation.json"
QUEUE_SUMMARY_FILE = QUEUE_DIR / "205_2_queue_executive_summary.json"

class QueueIntelligenceEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.2 Queue Intelligence Engine")

    def analyze_backlog(self, normalized):
        queue = normalized.get("queue", {})
        workers = normalized.get("workers", {})

        total = queue.get("total", 0) or 0
        waiting = queue.get("waiting", 0) or 0
        running = queue.get("running", 0) or 0
        finished = queue.get("finished", 0) or 0
        failed = queue.get("failed", 0) or 0
        retry = queue.get("retry", 0) or 0
        idle_workers = workers.get("idle", 0) or 0

        active_backlog = waiting + running + retry
        unresolved = waiting + running + failed + retry

        if failed > 0:
            backlog_risk = "HIGH"
        elif active_backlog > 0 and idle_workers == 0:
            backlog_risk = "MEDIUM"
        else:
            backlog_risk = "LOW"

        return {
            "total": total,
            "waiting": waiting,
            "running": running,
            "finished": finished,
            "failed": failed,
            "retry": retry,
            "active_backlog": active_backlog,
            "unresolved": unresolved,
            "backlog_risk": backlog_risk,
        }

    def analyze_completion(self, normalized):
        queue = normalized.get("queue", {})
        total = queue.get("total", 0) or 0
        finished = queue.get("finished", 0) or 0
        failed = queue.get("failed", 0) or 0
        completion_rate = queue.get("completion_rate", 0) or 0
        failure_rate = round((failed / total) * 100, 2) if total else 0

        if failure_rate > 10:
            status = "WEAK"
        elif completion_rate >= 80 and failed == 0:
            status = "STRONG"
        elif completion_rate >= 50:
            status = "NORMAL"
        else:
            status = "EARLY_OR_LOW_PROGRESS"

        return {
            "completion_rate": completion_rate,
            "failure_rate": failure_rate,
            "finished": finished,
            "failed": failed,
            "completion_status": status,
        }

    def analyze_worker_fit(self, normalized):
        workers = normalized.get("workers", {})
        queue = normalized.get("queue", {})

        total_workers = workers.get("total", 0) or 0
        idle_workers = workers.get("idle", 0) or 0
        running_workers = workers.get("running", 0) or 0
        waiting = queue.get("waiting", 0) or 0
        running_jobs = queue.get("running", 0) or 0

        if total_workers == 0:
            fit = "NO_WORKER"
        elif idle_workers > 0 and waiting > 0:
            fit = "CAPACITY_AVAILABLE_FOR_WAITING"
        elif idle_workers == total_workers and running_jobs == 0:
            fit = "CAPACITY_READY"
        elif running_workers > 0:
            fit = "WORKERS_ACTIVE"
        else:
            fit = "NORMAL"

        utilization = round((running_workers / total_workers) * 100, 2) if total_workers else 0

        return {
            "worker_total": total_workers,
            "worker_idle": idle_workers,
            "worker_running": running_workers,
            "worker_utilization_percent": utilization,
            "worker_queue_fit": fit,
        }

    def calculate_queue_score(self, backlog, completion, worker_fit):
        score = 100

        if backlog["failed"] > 0:
            score -= min(40, backlog["failed"] * 15)

        if backlog["retry"] > 0:
            score -= min(20, backlog["retry"] * 8)

        if completion["failure_rate"] > 0:
            score -= min(25, completion["failure_rate"])

        if backlog["active_backlog"] > 0 and worker_fit["worker_idle"] == 0:
            score -= 8

        if worker_fit["worker_total"] == 0:
            score -= 30

        if completion["completion_status"] == "STRONG":
            score += 2

        score = round(clamp(score), 2)

        if score >= 90:
            risk = "LOW"
        elif score >= 70:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "queue_score": score,
            "queue_risk": risk,
            "completion_status": completion["completion_status"],
            "backlog_risk": backlog["backlog_risk"],
        }

    def recommendation(self, score, backlog, completion, worker_fit):
        if score["queue_risk"] == "HIGH":
            return "Queue risk yüksek. Yeni batch başlatmadan önce failed/retry job kayıtları incelenmeli."

        if backlog["failed"] > 0:
            return "Failed job bulundu. Önce recovery/retry planı uygulanmalı."

        if backlog["waiting"] > 0 and worker_fit["worker_idle"] > 0:
            return "Waiting job ve idle worker mevcut. Worker assignment çalıştırılabilir."

        if backlog["active_backlog"] == 0 and worker_fit["worker_idle"] == worker_fit["worker_total"]:
            return "Queue aktif backlog içermiyor ve worker'lar idle. Kontrollü yeni batch oluşturulabilir."

        if completion["completion_status"] == "EARLY_OR_LOW_PROGRESS":
            return "Queue erken aşamada veya completion düşük. Bir sonraki üretim öncesi status tekrar kontrol edilmeli."

        return "Queue normal görünüyor. Mevcut scheduler/worker planı sürdürülebilir."

    def executive_summary(self, backlog, completion, worker_fit, score, recommendation):
        return (
            f"Queue Intelligence sonucuna göre queue skoru {score['queue_score']}/100 ve risk seviyesi {score['queue_risk']} olarak hesaplanmıştır. "
            f"Toplam {backlog['total']} job içinde {backlog['finished']} finished, {backlog['waiting']} waiting, "
            f"{backlog['running']} running, {backlog['failed']} failed ve {backlog['retry']} retry job bulunmaktadır. "
            f"Completion rate %{completion['completion_rate']}, failure rate %{completion['failure_rate']} seviyesindedir. "
            f"Worker kapasitesi açısından {worker_fit['worker_total']} worker tanımlı, {worker_fit['worker_idle']} worker idle durumdadır. "
            f"Öneri: {recommendation}"
        )

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, QUEUE_DIR)
        ts = now_stamp()

        sdk_result = self.sdk.run()
        normalized = sdk_result["payload"]["normalized"]

        backlog = self.analyze_backlog(normalized)
        completion = self.analyze_completion(normalized)
        worker_fit = self.analyze_worker_fit(normalized)
        score = self.calculate_queue_score(backlog, completion, worker_fit)
        rec = self.recommendation(score, backlog, completion, worker_fit)
        summary = self.executive_summary(backlog, completion, worker_fit, score, rec)

        result = {
            "score": score["queue_score"],
            "decision": "QUEUE INTELLIGENCE READY" if score["queue_score"] >= 90 else "QUEUE INTELLIGENCE REVIEW",
            "risk": score["queue_risk"],
            "recommendation": rec,
            "executive_summary": summary,
        }

        payload = {
            "module": "205.2 Queue Intelligence Engine",
            "created_at": now_text(),
            "backlog": backlog,
            "completion": completion,
            "worker_fit": worker_fit,
            "score": score,
            "result": result,
            "sdk_reference": sdk_result["paths"],
        }

        state = STATE_DIR / f"205_2_queue_intelligence_state_{ts}.json"
        report = REPORT_DIR / f"205_2_queue_intelligence_raporu_{ts}.txt"

        write_json(QUEUE_INTELLIGENCE_FILE, payload)
        write_json(QUEUE_SCORE_FILE, score)
        write_json(QUEUE_RECOMMENDATION_FILE, {"recommendation": rec})
        write_json(QUEUE_SUMMARY_FILE, {"executive_summary": summary})
        write_json(state, payload)

        lines = [
            "="*80,
            "205.2 QUEUE INTELLIGENCE ENGINE",
            "="*80,
            f"Score             : {result['score']} / 100",
            f"Decision          : {result['decision']}",
            f"Risk              : {result['risk']}",
            "",
            "BACKLOG",
            "-"*80,
            f"Total             : {backlog['total']}",
            f"Waiting           : {backlog['waiting']}",
            f"Running           : {backlog['running']}",
            f"Finished          : {backlog['finished']}",
            f"Failed            : {backlog['failed']}",
            f"Retry             : {backlog['retry']}",
            f"Active Backlog    : {backlog['active_backlog']}",
            f"Backlog Risk      : {backlog['backlog_risk']}",
            "",
            "COMPLETION",
            "-"*80,
            f"Completion Rate   : {completion['completion_rate']}%",
            f"Failure Rate      : {completion['failure_rate']}%",
            f"Status            : {completion['completion_status']}",
            "",
            "WORKER FIT",
            "-"*80,
            f"Workers Total     : {worker_fit['worker_total']}",
            f"Workers Idle      : {worker_fit['worker_idle']}",
            f"Workers Running   : {worker_fit['worker_running']}",
            f"Utilization       : {worker_fit['worker_utilization_percent']}%",
            f"Fit               : {worker_fit['worker_queue_fit']}",
            "",
            "RECOMMENDATION",
            "-"*80,
            rec,
            "",
            "EXECUTIVE SUMMARY",
            "-"*80,
            summary,
            "",
            "Dosyalar:",
            str(QUEUE_INTELLIGENCE_FILE),
            str(QUEUE_SCORE_FILE),
            str(QUEUE_RECOMMENDATION_FILE),
            str(QUEUE_SUMMARY_FILE),
            str(state),
            str(report),
        ]

        report.write_text("\n".join(lines), encoding="utf-8")

        return {
            "payload": payload,
            "result": result,
            "paths": {
                "queue": str(QUEUE_INTELLIGENCE_FILE),
                "score": str(QUEUE_SCORE_FILE),
                "recommendation": str(QUEUE_RECOMMENDATION_FILE),
                "summary": str(QUEUE_SUMMARY_FILE),
                "state": str(state),
                "report": str(report),
            }
        }
