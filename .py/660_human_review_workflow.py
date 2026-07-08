# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "600"
sys.path.insert(0, str(PACKAGE_DIR))
from core.intelligent_production_engine_sdk import IntelligentProductionEngineSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
IPE_DIR = STATE / "intelligent_production_engine" / "660_human_review_workflow"
MODULE_ID = "660"
MODULE_NAME = "Human Review Workflow"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path,data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def analyze(payload):
    validation=payload['validation']; plan=payload['plan']; operations=plan.get('operations',[])
    ready=sum(1 for i in operations if i.get('status') in ('READY','PLANNED','OPTIONAL_MISSING'))
    total=len(operations); readiness=round((ready/total)*100,2) if total else 100
    score=min(100, round(validation.get('score',0)*0.58 + readiness*0.42, 2))
    decision='HUMAN REVIEW WORKFLOW READY' if not validation.get('errors') else 'HUMAN REVIEW WORKFLOW REVIEW'
    return {'score':score,'decision':decision,'readiness':readiness,'ready_operations':ready,'total_operations':total,'recommendation':plan.get('message')}
def main():
    IPE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    sdk_result=IntelligentProductionEngineSDK(name=MODULE_ID+' '+MODULE_NAME).run(); analysis=analyze(sdk_result['payload'])
    ts=now_stamp(); output=IPE_DIR/('660_human_review_workflow.json'); state=IPE_DIR/('660_human_review_workflow_state_'+ts+'.json'); report=REPORTS/('660_human_review_workflow_raporu_'+ts+'.txt')
    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}
    write_json(output,payload); write_json(state,payload)
    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'ReadyOps : '+str(analysis['ready_operations'])+' / '+str(analysis['total_operations']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8'); print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__=='__main__': main()
