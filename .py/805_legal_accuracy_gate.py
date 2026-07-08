# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "800"
sys.path.insert(0, str(PACKAGE_DIR))
from core.real_production_engine_sdk import RealProductionEngineSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "real_production_engine" / "805_legal_accuracy_gate"
MODULE_ID = "805"
MODULE_NAME = "Legal Accuracy Gate"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path,data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def analyze(payload):
    validation=payload['validation']; plan=payload['plan']; queue=plan.get('queue',[]); chain=plan.get('chain_modules',[])
    planned=sum(1 for i in queue if 'PLANNED' in i.get('runtime_status',''))
    total=len(queue); queue_score=round((planned/total)*100,2) if total else 0
    chain_score=100 if len(chain)>=5 else 80 if len(chain)>=3 else 60
    score=min(100, round(validation.get('score',0)*0.55 + queue_score*0.25 + chain_score*0.20, 2))
    decision='LEGAL ACCURACY GATE READY' if not validation.get('errors') else 'LEGAL ACCURACY GATE REVIEW'
    return {'score':score,'decision':decision,'queue_score':queue_score,'chain_score':chain_score,'planned':planned,'total':total,'chain_modules':len(chain),'recommendation':plan.get('message')}
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    sdk_result=RealProductionEngineSDK(name=MODULE_ID+' '+MODULE_NAME, batch_size=args.batch_size, dry_run=not args.execute).run(); analysis=analyze(sdk_result['payload'])
    ts=now_stamp(); output=MODULE_DIR/('805_legal_accuracy_gate.json'); state=MODULE_DIR/('805_legal_accuracy_gate_state_'+ts+'.json'); report=REPORTS/('805_legal_accuracy_gate_raporu_'+ts+'.txt')
    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}
    write_json(output,payload); write_json(state,payload)
    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'Queue    : '+str(analysis['planned'])+' / '+str(analysis['total']), 'ChainMod : '+str(analysis['chain_modules']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8'); print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__=='__main__': main()
