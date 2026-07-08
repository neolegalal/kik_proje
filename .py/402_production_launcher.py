# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "400"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_os_sdk import ProductionOSSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
OS_DIR = STATE / "production_os" / "402_production_launcher"
MODULE_ID = "402"
MODULE_NAME = "Production Launcher"
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
def analyze(payload):
    validation = payload['validation']
    plan = payload['plan']
    operations = plan.get('operations', [])
    ready_ops = sum(1 for i in operations if i.get('status') == 'READY')
    total_ops = len(operations)
    readiness = round((ready_ops / total_ops) * 100, 2) if total_ops else 100
    score = min(100, round((validation.get('score', 0) * 0.6) + (readiness * 0.4), 2))
    decision = 'PRODUCTION LAUNCHER READY' if not validation.get('errors') else 'PRODUCTION LAUNCHER REVIEW'
    return {'score': score, 'decision': decision, 'readiness': readiness, 'ready_operations': ready_ops, 'total_operations': total_ops, 'recommendation': plan.get('message')}
def main():
    OS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    sdk_result = ProductionOSSDK(name=MODULE_ID + ' ' + MODULE_NAME).run()
    analysis = analyze(sdk_result['payload'])
    ts = now_stamp()
    output = OS_DIR / ('402_production_launcher.json')
    state = OS_DIR / ('402_production_launcher_state_' + ts + '.json')
    report = REPORTS / ('402_production_launcher_raporu_' + ts + '.txt')
    payload = {'created_at': now_text(), 'module_id': MODULE_ID, 'module_name': MODULE_NAME, 'analysis': analysis, 'sdk_reference': sdk_result['paths']}
    write_json(output, payload)
    write_json(state, payload)
    lines = ['='*80, MODULE_ID + ' ' + MODULE_NAME.upper(), '='*80, 'Score    : ' + str(analysis['score']) + ' / 100', 'Decision : ' + str(analysis['decision']), 'ReadyOps : ' + str(analysis['ready_operations']) + ' / ' + str(analysis['total_operations']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]
    report.write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines))
    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)
if __name__ == '__main__': main()
