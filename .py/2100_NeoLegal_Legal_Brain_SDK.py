# -*- coding: utf-8 -*-
import argparse,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent/"2100"
sys.path.insert(0,str(PACKAGE))
from core.neolegal_legal_brain_sdk import NeoLegalLegalBrainSDK
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case-text",default=None)
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    r=NeoLegalLegalBrainSDK(case_text=a.case_text,master_record_path=a.master_record,execute=a.execute).run()
    v=r["payload"]["validation"]; b=r["payload"]["brain_state"]
    print("="*80); print("2100 NEOLEGAL LEGAL BRAIN SDK TAMAMLANDI"); print("="*80)
    print("Validation            : "+str(v["decision"]))
    print("Score                 : "+str(v["score"])+" / 100")
    print("Thinking Score        : "+str(b["thinking"]["thinking_score"])+" / 100")
    print("Base Probability      : "+str(b["outcomes"]["base_probability"])+" / 100")
    print("Judge View            : "+str(b["judge"]["judicial_leaning"]))
    print("Reflection Confidence : "+str(b["reflection"]["confidence"])+" / 100")
    print(""); print("Dosyalar:")
    for k in ("snapshot","brain_state","dashboard","report"): print(r["paths"][k])
    raise SystemExit(1 if v["errors"] else 0)
if __name__=="__main__": main()
