# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "700"
sys.path.insert(0, str(PACKAGE_DIR))
from core.pilot_production_launcher_sdk import PilotProductionLauncherSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
PILOT_MODULE_DIR = STATE / "pilot_production" / "709_pilot_auditor"
MODULE_ID = "709"
MODULE_NAME = "Pilot Auditor"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path,data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def analyze(payload):
    validation=payload['validation']; plan=payload['plan']; queue=plan.get('queue',[])
    planned=sum(1 for i in queue if 'PLANNED' in i.get('runtime_status',''))
    total=len(queue); queue_score=round((planned/total)*100,2) if total else 0
    score=min(100, round(validation.get('score',0)*0.65 + queue_score*0.35, 2))
    decision='PILOT AUDITOR READY' if not validation.get('errors') else 'PILOT AUDITOR REVIEW'
    return {'score':score,'decision':decision,'queue_score':queue_score,'planned':planned,'total':total,'recommendation':plan.get('message')}
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    PILOT_MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    sdk_result=PilotProductionLauncherSDK(name=MODULE_ID+' '+MODULE_NAME, batch_size=args.batch_size, dry_run=not args.execute).run(); analysis=analyze(sdk_result['payload'])
    ts=now_stamp(); output=PILOT_MODULE_DIR/('709_pilot_auditor.json'); state=PILOT_MODULE_DIR/('709_pilot_auditor_state_'+ts+'.json'); report=REPORTS/('709_pilot_auditor_raporu_'+ts+'.txt')
    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}
    write_json(output,payload); write_json(state,payload)
    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'Queue    : '+str(analysis['planned'])+' / '+str(analysis['total']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8'); print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__=='__main__': main()
