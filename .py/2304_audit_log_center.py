# -*- coding: utf-8 -*-
import argparse,sys,json
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
sys.path.insert(0,str(BASE/".py"/"2300"))
from core.neolegal_platform_governance_sdk import NeoLegalPlatformGovernanceSDK
MODULE_DIR=BASE/"production_state"/"platform_governance"/"2304_audit_log_center"
REPORTS=BASE/"raporlar"
def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment",default="production")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    MODULE_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
    r=NeoLegalPlatformGovernanceSDK(name="2304 Audit Log Center",environment=a.environment,execute=a.execute).run()
    v=r["payload"]["validation"]; g=r["payload"]["governance_state"]; audit=r["payload"]["audit"]
    decision="AUDIT LOG CENTER READY" if not v["errors"] else "AUDIT LOG CENTER BLOCKED"
    analysis={"score":v["score"],"decision":decision,"security_score":g["security"]["policy_score"],"compliance_score":g["compliance"]["compliance_score"],"environment":g["certificate"]["environment"],"audit":audit["status"]}
    stamp=ts(); out=MODULE_DIR/"2304_audit_log_center.json"; state=MODULE_DIR/("2304_audit_log_center_state_"+stamp+".json"); rep=REPORTS/("2304_audit_log_center_raporu_"+stamp+".txt")
    payload={"module_id":"2304","module_name":"Audit Log Center","analysis":analysis,"sdk_reference":r["paths"]}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); state.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["="*80,"2304 AUDIT LOG CENTER","="*80,"Score            : "+str(analysis["score"])+" / 100","Decision         : "+decision,"Security Score   : "+str(analysis["security_score"])+" / 100","Compliance Score : "+str(analysis["compliance_score"])+" / 100","Environment      : "+str(analysis["environment"]),"Audit            : "+str(analysis["audit"])]
    rep.write_text("\n".join(lines),encoding="utf-8"); print("\n".join(lines))
    raise SystemExit(0 if "READY" in decision else 1)
if __name__=="__main__": main()
