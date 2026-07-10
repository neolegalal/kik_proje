# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "801"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_safety_gate_sdk import ProductionSafetyGateSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "production_safety_gate" / "811_database_safety_checker"
MODULE_ID = "811"
MODULE_NAME = "Database Safety Checker"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path,data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); args=parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    sdk_result=ProductionSafetyGateSDK(name=MODULE_ID+' '+MODULE_NAME,batch_size=args.batch_size).run(); final=sdk_result['payload']['final']; checks=sdk_result['payload']['checks']
    pass_count=sum(1 for v in checks.values() if v['status']=='PASS'); warn_count=sum(1 for v in checks.values() if v['status']=='WARN')
    decision='DATABASE SAFETY CHECKER READY' if final['decision'] in ('PASS','WARN') else 'DATABASE SAFETY CHECKER BLOCKED'
    analysis={'score':final['score'],'decision':decision,'pass_count':pass_count,'warn_count':warn_count,'check_count':len(checks),'recommendation':'Safety gate ready for controlled pilot execution.' if final['decision']!='FAIL' else 'Safety gate blocked.'}
    ts=now_stamp(); output=MODULE_DIR/('811_database_safety_checker.json'); state=MODULE_DIR/('811_database_safety_checker_state_'+ts+'.json'); report=REPORTS/('811_database_safety_checker_raporu_'+ts+'.txt')
    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}
    write_json(output,payload); write_json(state,payload)
    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'Checks   : '+str(analysis['pass_count'])+' PASS / '+str(analysis['warn_count'])+' WARN', '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8'); print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__=='__main__': main()
