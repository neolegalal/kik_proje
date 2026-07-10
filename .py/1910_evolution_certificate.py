# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1900"
sys.path.insert(0, str(PACKAGE_DIR))
from core.neolegal_evolution_platform_sdk import NeoLegalEvolutionPlatformSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "neolegal_evolution_platform" / "1910_evolution_certificate"
MODULE_ID = "1910"
MODULE_NAME = "Evolution Certificate"
def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = NeoLegalEvolutionPlatformSDK(name=MODULE_ID + " " + MODULE_NAME, sample_text=args.sample_text, mode=args.mode, execute=args.execute).run()
    val = res["payload"]["validation"]
    evo = res["payload"]["evolution"]
    decision = "EVOLUTION CERTIFICATE READY" if not val["errors"] else "EVOLUTION CERTIFICATE BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "confidence": evo["confidence"]["confidence_score"], "hallucination_risk": evo["hallucination"]["hallucination_risk"], "evidence_count": evo["evidence"]["evidence_count"], "audit": evo["audit"]["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "1910_evolution_certificate.json"
    state = MODULE_DIR / ("1910_evolution_certificate_state_" + ts + ".json")
    report = REPORTS / ("1910_evolution_certificate_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score              : " + str(analysis["score"]) + " / 100", "Decision           : " + str(analysis["decision"]), "Confidence         : " + str(analysis["confidence"]) + " / 100", "Hallucination Risk : " + str(analysis["hallucination_risk"]) + " / 100", "Evidence Count     : " + str(analysis["evidence_count"]), "Audit              : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
