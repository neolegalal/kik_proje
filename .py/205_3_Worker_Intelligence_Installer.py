
# 205_3_Worker_Intelligence_Installer.py
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "205"

manager = r"""# -*- coding: utf-8 -*-
import argparse
from core.engine import IntelligenceEngine
from core.utils import now_stamp, now_text, write_json
from core.config import STATE_DIR, REPORT_DIR, INTELLIGENCE_DIR

OUTDIR = INTELLIGENCE_DIR / "workers"

class WorkerIntelligence:
    def run(self):
        sdk = IntelligenceEngine(engine_name="205.3 Worker Intelligence")
        res = sdk.run()
        n = res["payload"]["normalized"]
        w = n.get("workers", {})
        total = w.get("total",0)
        idle = w.get("idle",0)
        running = w.get("running",0)
        util = round((running/total)*100,2) if total else 0
        score = max(0, min(100, 100-(w.get("jobs_failed",0)*10)))
        risk = "LOW" if score>=90 else ("MEDIUM" if score>=70 else "HIGH")
        rec = (
            "Idle worker'lar mevcut. Yeni batch güvenle başlatılabilir."
            if idle>0 else
            "Tüm worker'lar meşgul. Yeni batch planlaması bekletilebilir."
        )
        summary = f"Worker skoru {score}/100. Toplam {total} worker, {idle} idle, {running} running. Kullanım %{util}. Öneri: {rec}"
        payload={
            "module":"205.3 Worker Intelligence",
            "created_at":now_text(),
            "workers":{"total":total,"idle":idle,"running":running,"utilization_percent":util},
            "result":{"score":score,"risk":risk,"decision":"WORKER INTELLIGENCE READY","recommendation":rec,"executive_summary":summary}
        }
        OUTDIR.mkdir(parents=True, exist_ok=True)
        ts=now_stamp()
        write_json(OUTDIR/"205_3_worker_intelligence.json",payload)
        state=STATE_DIR/f"205_3_worker_intelligence_state_{ts}.json"
        write_json(state,payload)
        report=REPORT_DIR/f"205_3_worker_intelligence_raporu_{ts}.txt"
        report.write_text(summary,encoding="utf-8")
        print("="*80)
        print("205.3 WORKER INTELLIGENCE ENGINE TAMAMLANDI")
        print("="*80)
        print(f"Score        : {score} / 100")
        print(f"Decision     : WORKER INTELLIGENCE READY")
        print(f"Risk         : {risk}")
        print(f"Workers      : {total}")
        print(f"Idle         : {idle}")
        print(f"Running      : {running}")
        print("")
        print("Recommendation:")
        print(rec)
        print("")
        print("Dosyalar:")
        print(OUTDIR/"205_3_worker_intelligence.json")
        print(report)

if __name__=="__main__":
    argparse.ArgumentParser().parse_args()
    WorkerIntelligence().run()
"""

bridge = """# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR=Path(__file__).resolve().parent/"205"
sys.path.insert(0,str(PACKAGE_DIR))
from worker_intelligence_manager import *
"""

(PKG/"worker_intelligence_manager.py").write_text(manager,encoding="utf-8")
(PY/"205_3_Worker_Intelligence.py").write_text(bridge,encoding="utf-8")
print("="*80)
print("205.3 WORKER INTELLIGENCE INSTALLER TAMAMLANDI")
print("="*80)
print("Eklenen dosyalar:")
print(PKG/"worker_intelligence_manager.py")
print(PY/"205_3_Worker_Intelligence.py")
print("\nŞimdi çalıştır:")
print(r'python ".py\205_3_Worker_Intelligence.py"')
