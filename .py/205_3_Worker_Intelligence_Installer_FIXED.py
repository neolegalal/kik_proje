# -*- coding: utf-8 -*-
# 205.3 Worker Intelligence Engine Installer - FIXED
# NeoLegal Production Platform

from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "205"

WORKER_MANAGER_CODE = r"""# -*- coding: utf-8 -*-
from core.engine import IntelligenceEngine
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json, clamp

WORKER_DIR = INTELLIGENCE_DIR / "workers"
WORKER_INTELLIGENCE_FILE = WORKER_DIR / "205_3_worker_intelligence.json"
WORKER_SCORE_FILE = WORKER_DIR / "205_3_worker_score.json"
WORKER_RECOMMENDATION_FILE = WORKER_DIR / "205_3_worker_recommendation.json"
WORKER_SUMMARY_FILE = WORKER_DIR / "205_3_worker_executive_summary.json"


class WorkerIntelligenceEngine:
    def __init__(self):
        self.sdk = IntelligenceEngine(engine_name="205.3 Worker Intelligence Engine")

    def analyze_workers(self, normalized):
        workers = normalized.get("workers", {})
        queue = normalized.get("queue", {})

        total = workers.get("total", 0) or 0
        idle = workers.get("idle", 0) or 0
        running = workers.get("running", 0) or 0
        jobs_completed = workers.get("jobs_completed", 0) or 0
        jobs_failed = workers.get("jobs_failed", 0) or 0

        queue_waiting = queue.get("waiting", 0) or 0
        queue_running = queue.get("running", 0) or 0

        utilization_percent = round((running / total) * 100, 2) if total else 0
        idle_percent = round((idle / total) * 100, 2) if total else 0
        failure_rate = round((jobs_failed / (jobs_completed + jobs_failed)) * 100, 2) if (jobs_completed + jobs_failed) else 0

        if total == 0:
            capacity_status = "NO_WORKER"
        elif idle == total and queue_waiting > 0:
            capacity_status = "AVAILABLE_FOR_ASSIGNMENT"
        elif idle == total and queue_waiting == 0 and queue_running == 0:
            capacity_status = "READY_FOR_NEW_BATCH"
        elif running > 0:
            capacity_status = "ACTIVE"
        else:
            capacity_status = "NORMAL"

        return {
            "total": total,
            "idle": idle,
            "running": running,
            "jobs_completed": jobs_completed,
            "jobs_failed": jobs_failed,
            "utilization_percent": utilization_percent,
            "idle_percent": idle_percent,
            "failure_rate": failure_rate,
            "queue_waiting": queue_waiting,
            "queue_running": queue_running,
            "capacity_status": capacity_status,
        }

    def calculate_score(self, analysis):
        score = 100

        if analysis["total"] == 0:
            score -= 60

        if analysis["jobs_failed"] > 0:
            score -= min(35, analysis["jobs_failed"] * 12)

        if analysis["failure_rate"] > 0:
            score -= min(25, analysis["failure_rate"])

        if analysis["queue_waiting"] > 0 and analysis["idle"] == 0:
            score -= 10

        if analysis["capacity_status"] in ("READY_FOR_NEW_BATCH", "AVAILABLE_FOR_ASSIGNMENT"):
            score += 2

        score = round(clamp(score), 2)

        if score >= 90:
            risk = "LOW"
        elif score >= 70:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "worker_score": score,
            "worker_risk": risk,
            "capacity_status": analysis["capacity_status"],
        }

    def recommendation(self, score, analysis):
        if score["worker_risk"] == "HIGH":
            return "Worker riski yüksek. Yeni batch başlatmadan önce worker/queue durumu incelenmelidir."

        if analysis["jobs_failed"] > 0:
            return "Worker failed job geçmişi var. Önce failed job nedenleri incelenmelidir."

        if analysis["capacity_status"] == "AVAILABLE_FOR_ASSIGNMENT":
            return "Waiting job ve idle worker mevcut. Worker assignment çalıştırılabilir."

        if analysis["capacity_status"] == "READY_FOR_NEW_BATCH":
            return "Tüm worker'lar idle ve queue running değil. Kontrollü yeni batch başlatılabilir."

        if analysis["capacity_status"] == "ACTIVE":
            return "Worker'lar aktif çalışıyor. Yeni batch için mevcut işlerin tamamlanması beklenebilir."

        return "Worker durumu normal. Mevcut üretim planı sürdürülebilir."

    def executive_summary(self, analysis, score, recommendation):
        return (
            f"Worker Intelligence sonucuna göre worker skoru {score['worker_score']}/100 ve risk seviyesi "
            f"{score['worker_risk']} olarak hesaplanmıştır. Toplam {analysis['total']} worker tanımlıdır; "
            f"{analysis['idle']} worker idle, {analysis['running']} worker running durumdadır. "
            f"Worker kullanım oranı %{analysis['utilization_percent']}, idle oranı %{analysis['idle_percent']} seviyesindedir. "
            f"Queue tarafında {analysis['queue_waiting']} waiting ve {analysis['queue_running']} running job bulunmaktadır. "
            f"Öneri: {recommendation}"
        )

    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, WORKER_DIR)
        ts = now_stamp()

        sdk_result = self.sdk.run()
        normalized = sdk_result["payload"]["normalized"]

        analysis = self.analyze_workers(normalized)
        score = self.calculate_score(analysis)
        rec = self.recommendation(score, analysis)
        summary = self.executive_summary(analysis, score, rec)

        result = {
            "score": score["worker_score"],
            "decision": "WORKER INTELLIGENCE READY" if score["worker_score"] >= 90 else "WORKER INTELLIGENCE REVIEW",
            "risk": score["worker_risk"],
            "recommendation": rec,
            "executive_summary": summary,
        }

        payload = {
            "module": "205.3 Worker Intelligence Engine",
            "created_at": now_text(),
            "analysis": analysis,
            "score": score,
            "result": result,
            "sdk_reference": sdk_result["paths"],
        }

        state = STATE_DIR / f"205_3_worker_intelligence_state_{ts}.json"
        report = REPORT_DIR / f"205_3_worker_intelligence_raporu_{ts}.txt"

        write_json(WORKER_INTELLIGENCE_FILE, payload)
        write_json(WORKER_SCORE_FILE, score)
        write_json(WORKER_RECOMMENDATION_FILE, {"recommendation": rec})
        write_json(WORKER_SUMMARY_FILE, {"executive_summary": summary})
        write_json(state, payload)

        lines = [
            "=" * 80,
            "205.3 WORKER INTELLIGENCE ENGINE",
            "=" * 80,
            f"Score              : {result['score']} / 100",
            f"Decision           : {result['decision']}",
            f"Risk               : {result['risk']}",
            "",
            "WORKERS",
            "-" * 80,
            f"Total              : {analysis['total']}",
            f"Idle               : {analysis['idle']}",
            f"Running            : {analysis['running']}",
            f"Utilization        : {analysis['utilization_percent']}%",
            f"Idle Percent       : {analysis['idle_percent']}%",
            f"Jobs Completed     : {analysis['jobs_completed']}",
            f"Jobs Failed        : {analysis['jobs_failed']}",
            f"Failure Rate       : {analysis['failure_rate']}%",
            f"Capacity Status    : {analysis['capacity_status']}",
            "",
            "QUEUE CONTEXT",
            "-" * 80,
            f"Queue Waiting      : {analysis['queue_waiting']}",
            f"Queue Running      : {analysis['queue_running']}",
            "",
            "RECOMMENDATION",
            "-" * 80,
            rec,
            "",
            "EXECUTIVE SUMMARY",
            "-" * 80,
            summary,
            "",
            "Dosyalar:",
            str(WORKER_INTELLIGENCE_FILE),
            str(WORKER_SCORE_FILE),
            str(WORKER_RECOMMENDATION_FILE),
            str(WORKER_SUMMARY_FILE),
            str(state),
            str(report),
        ]

        report.write_text("\\n".join(lines), encoding="utf-8")

        return {
            "payload": payload,
            "result": result,
            "paths": {
                "worker": str(WORKER_INTELLIGENCE_FILE),
                "score": str(WORKER_SCORE_FILE),
                "recommendation": str(WORKER_RECOMMENDATION_FILE),
                "summary": str(WORKER_SUMMARY_FILE),
                "state": str(state),
                "report": str(report),
            }
        }


def main():
    engine = WorkerIntelligenceEngine()
    res = engine.run()
    result = res["result"]
    payload = res["payload"]
    analysis = payload["analysis"]

    print("=" * 80)
    print("205.3 WORKER INTELLIGENCE ENGINE TAMAMLANDI")
    print("=" * 80)
    print(f"Score          : {result['score']} / 100")
    print(f"Decision       : {result['decision']}")
    print(f"Risk           : {result['risk']}")
    print(f"Workers Total  : {analysis['total']}")
    print(f"Idle           : {analysis['idle']}")
    print(f"Running        : {analysis['running']}")
    print(f"Utilization    : {analysis['utilization_percent']}%")
    print(f"Capacity       : {analysis['capacity_status']}")
    print("")
    print("Recommendation:")
    print(result["recommendation"])
    print("")
    print("Dosyalar:")
    print(res["paths"]["worker"])
    print(res["paths"]["report"])


if __name__ == "__main__":
    main()
"""

BRIDGE_CODE = r"""# -*- coding: utf-8 -*-
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent / "205"
sys.path.insert(0, str(PACKAGE_DIR))

from worker_intelligence_manager import main

if __name__ == "__main__":
    main()
"""

def main():
    if not (PKG / "core").exists():
        raise SystemExit("205 Intelligence SDK bulunamadı. Önce 205_0_Intelligence_SDK_Installer.py çalıştırılmalı.")

    PKG.mkdir(parents=True, exist_ok=True)
    (PKG / "worker_intelligence_manager.py").write_text(WORKER_MANAGER_CODE, encoding="utf-8")
    (PY / "205_3_Worker_Intelligence.py").write_text(BRIDGE_CODE, encoding="utf-8")

    print("=" * 80)
    print("205.3 WORKER INTELLIGENCE ENGINE FIXED INSTALLER TAMAMLANDI")
    print("=" * 80)
    print("Yazılan dosyalar:")
    print(PKG / "worker_intelligence_manager.py")
    print(PY / "205_3_Worker_Intelligence.py")
    print("")
    print("Şimdi çalıştır:")
    print(r'cd /d C:\Users\MSI\Desktop\kik_proje')
    print(r'python ".py\205_3_Worker_Intelligence.py"')

if __name__ == "__main__":
    main()
