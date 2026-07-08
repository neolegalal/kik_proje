# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "550"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_factory_runtime_sdk import ProductionFactoryRuntimeSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
RUNTIME_DIR = STATE / "production_factory_runtime" / "557_resume_runtime"
MODULE_ID = "557"
MODULE_NAME = "Resume Runtime"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path,data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def analyze(payload):
    validation=payload['validation']; plan=payload['plan']; operations=plan.get('operations',[])
    ready=sum(1 for i in operations if i.get('status') in ('READY','PLANNED','OPTIONAL_MISSING'))
    total=len(operations); readiness=round((ready/total)*100,2) if total else 100
    score=min(100, round(validation.get('score',0)*0.6 + readiness*0.4, 2))
    decision='RESUME RUNTIME READY' if not validation.get('errors') else 'RESUME RUNTIME REVIEW'
    return {'score':score,'decision':decision,'readiness':readiness,'ready_operations':ready,'total_operations':total,'recommendation':plan.get('message')}
def main():
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    sdk_result=ProductionFactoryRuntimeSDK(name=MODULE_ID+' '+MODULE_NAME).run(); analysis=analyze(sdk_result['payload'])
    ts=now_stamp(); output=RUNTIME_DIR/('557_resume_runtime.json'); state=RUNTIME_DIR/('557_resume_runtime_state_'+ts+'.json'); report=REPORTS/('557_resume_runtime_raporu_'+ts+'.txt')
    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}
    write_json(output,payload); write_json(state,payload)
    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'ReadyOps : '+str(analysis['ready_operations'])+' / '+str(analysis['total_operations']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8'); print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__=='__main__': main()
