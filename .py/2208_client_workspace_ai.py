# -*- coding: utf-8 -*-
import argparse,sys,json
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
sys.path.insert(0,str(BASE/".py"/"2200"))
from core.neolegal_autonomous_legal_expert_sdk import NeoLegalAutonomousLegalExpertSDK
MODULE_DIR=BASE/"production_state"/"autonomous_legal_expert"/"2208_client_workspace_ai"
REPORTS=BASE/"raporlar"
def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case-text",default=None)
    p.add_argument("--client-name",default="Pilot Client")
    p.add_argument("--case-name",default="Pilot Procurement Case")
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    MODULE_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
    r=NeoLegalAutonomousLegalExpertSDK(name="2208 Client Workspace AI",case_text=a.case_text,client_name=a.client_name,case_name=a.case_name,master_record_path=a.master_record,execute=a.execute).run()
    v=r["payload"]["validation"]; e=r["payload"]["expert_state"]; audit=r["payload"]["audit"]
    decision="CLIENT WORKSPACE AI READY" if not v["errors"] else "CLIENT WORKSPACE AI BLOCKED"
    analysis={"score":v["score"],"decision":decision,"issue_count":e["intake"]["issue_count"],"evidence_risk":e["evidence"]["risk"],"success_probability":e["prediction"]["success_probability"],"audit":audit["status"]}
    stamp=ts(); out=MODULE_DIR/"2208_client_workspace_ai.json"; state=MODULE_DIR/("2208_client_workspace_ai_state_"+stamp+".json"); rep=REPORTS/("2208_client_workspace_ai_raporu_"+stamp+".txt")
    payload={"module_id":"2208","module_name":"Client Workspace AI","analysis":analysis,"sdk_reference":r["paths"]}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); state.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["="*80,"2208 CLIENT WORKSPACE AI","="*80,"Score               : "+str(analysis["score"])+" / 100","Decision            : "+decision,"Issue Count         : "+str(analysis["issue_count"]),"Evidence Risk       : "+str(analysis["evidence_risk"]),"Success Probability : "+str(analysis["success_probability"])+" / 100","Audit               : "+str(analysis["audit"])]
    rep.write_text("\n".join(lines),encoding="utf-8"); print("\n".join(lines))
    raise SystemExit(0 if "READY" in decision else 1)
if __name__=="__main__": main()
