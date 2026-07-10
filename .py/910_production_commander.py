# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "900"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_master_sdk import ProductionMasterSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "production_master" / "910_production_commander"
MODULE_ID = "910"
MODULE_NAME = "Production Commander"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path,data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    sdk=ProductionMasterSDK(name=MODULE_ID+' '+MODULE_NAME,target=args.target,batch_size=args.batch_size,dry_run=not args.execute)
    res=sdk.run(); val=res['payload']['validation']; queue=res['payload']['queue_plan']; workers=res['payload']['workers']; cost=res['payload']['cost']
    score=val['score']; decision='PRODUCTION COMMANDER READY' if not val['errors'] else 'PRODUCTION COMMANDER BLOCKED'
    analysis={'score':score,'decision':decision,'planned_batch':queue['planned_batch'],'target':args.target,'workers':workers,'cost':cost,'recommendation':'Production Master ready for controlled operation.' if not val['errors'] else 'Production Master blocked.'}
    ts=now_stamp(); output=MODULE_DIR/('910_production_commander.json'); state=MODULE_DIR/('910_production_commander_state_'+ts+'.json'); report=REPORTS/('910_production_commander_raporu_'+ts+'.txt')
    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':res['paths']}
    write_json(output,payload); write_json(state,payload)
    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'Target   : '+str(analysis['target']), 'Batch    : '+str(analysis['planned_batch']), 'Workers  : '+str(analysis['workers']['recommended_workers']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8'); print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__=='__main__': main()
