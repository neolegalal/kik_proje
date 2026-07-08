# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "500"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_data_factory_sdk import ProductionDataFactorySDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
FACTORY_DIR = STATE / "production_data_factory" / "501_data_source_registry"
MODULE_ID = "501"
MODULE_NAME = "Data Source Registry"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path,data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def analyze(payload):
    validation=payload['validation']; plan=payload['plan']; operations=plan.get('operations',[])
    ready=sum(1 for i in operations if i.get('status') in ('READY','PLANNED','OPTIONAL_MISSING'))
    total=len(operations); readiness=round((ready/total)*100,2) if total else 100
    score=min(100, round(validation.get('score',0)*0.65 + readiness*0.35, 2))
    decision='DATA SOURCE REGISTRY READY' if not validation.get('errors') else 'DATA SOURCE REGISTRY REVIEW'
    return {'score':score,'decision':decision,'readiness':readiness,'ready_operations':ready,'total_operations':total,'recommendation':plan.get('message')}
def main():
    FACTORY_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    sdk_result=ProductionDataFactorySDK(name=MODULE_ID+' '+MODULE_NAME).run(); analysis=analyze(sdk_result['payload'])
    ts=now_stamp(); output=FACTORY_DIR/('501_data_source_registry.json'); state=FACTORY_DIR/('501_data_source_registry_state_'+ts+'.json'); report=REPORTS/('501_data_source_registry_raporu_'+ts+'.txt')
    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}
    write_json(output,payload); write_json(state,payload)
    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'ReadyOps : '+str(analysis['ready_operations'])+' / '+str(analysis['total_operations']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8'); print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__=='__main__': main()
