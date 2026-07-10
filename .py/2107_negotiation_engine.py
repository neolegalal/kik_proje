# -*- coding: utf-8 -*-
import argparse,sys,json
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
sys.path.insert(0,str(BASE/".py"/"2100"))
from core.neolegal_legal_brain_sdk import NeoLegalLegalBrainSDK
MODULE_DIR=BASE/"production_state"/"neolegal_legal_brain"/"2107_negotiation_engine"
REPORTS=BASE/"raporlar"
def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def main():
    p=argparse.ArgumentParser(); p.add_argument("--case-text",default=None); p.add_argument("--master-record",default=None); p.add_argument("--execute",action="store_true")
    a=p.parse_args(); MODULE_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
    r=NeoLegalLegalBrainSDK(name="2107 Negotiation Engine",case_text=a.case_text,master_record_path=a.master_record,execute=a.execute).run()
    v=r["payload"]["validation"]; b=r["payload"]["brain_state"]; audit=r["payload"]["audit"]
    decision="NEGOTIATION ENGINE READY" if not v["errors"] else "NEGOTIATION ENGINE BLOCKED"
    analysis={"score":v["score"],"decision":decision,"thinking_score":b["thinking"]["thinking_score"],"base_probability":b["outcomes"]["base_probability"],"judge_view":b["judge"]["judicial_leaning"],"reflection_confidence":b["reflection"]["confidence"],"audit":audit["status"]}
    stamp=ts(); out=MODULE_DIR/"2107_negotiation_engine.json"; state=MODULE_DIR/("2107_negotiation_engine_state_"+stamp+".json"); rep=REPORTS/("2107_negotiation_engine_raporu_"+stamp+".txt")
    payload={"module_id":"2107","module_name":"Negotiation Engine","analysis":analysis,"sdk_reference":r["paths"]}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); state.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["="*80,"2107 NEGOTIATION ENGINE","="*80,"Score                 : "+str(analysis["score"])+" / 100","Decision              : "+decision,"Thinking Score        : "+str(analysis["thinking_score"])+" / 100","Base Probability      : "+str(analysis["base_probability"])+" / 100","Judge View            : "+str(analysis["judge_view"]),"Reflection Confidence : "+str(analysis["reflection_confidence"])+" / 100","Audit                 : "+str(analysis["audit"])]
    rep.write_text("\n".join(lines),encoding="utf-8"); print("\n".join(lines))
    raise SystemExit(0 if "READY" in decision else 1)
if __name__=="__main__": main()
