# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1800", "Next Generation NeoLegal AI SDK", [sys.executable, str(BASE / ".py" / "1800_Next_Generation_NeoLegal_SDK.py")]),
    ("1801", "NeoLegal Copilot", [sys.executable, str(BASE / ".py" / "1801_copilot.py")]),
    ("1802", "Knowledge Graph Engine", [sys.executable, str(BASE / ".py" / "1802_knowledge_graph_engine.py")]),
    ("1803", "Legal Time Machine", [sys.executable, str(BASE / ".py" / "1803_legal_time_machine.py")]),
    ("1804", "Multi Agent Legal AI", [sys.executable, str(BASE / ".py" / "1804_multi_agent_legal_ai.py")]),
    ("1805", "Prediction Simulation Engine", [sys.executable, str(BASE / ".py" / "1805_prediction_simulation_engine.py")]),
    ("1806", "Next Generation Integration Layer", [sys.executable, str(BASE / ".py" / "1806_next_generation_integration_layer.py")]),
    ("1807", "Next Generation QA Auditor", [sys.executable, str(BASE / ".py" / "1807_next_generation_qa_auditor.py")]),
    ("1808", "Next Generation Dashboard", [sys.executable, str(BASE / ".py" / "1808_next_generation_dashboard.py")]),
    ("1809", "Next Generation Release Manager", [sys.executable, str(BASE / ".py" / "1809_next_generation_release_manager.py")]),
    ("1810", "Next Generation Certificate", [sys.executable, str(BASE / ".py" / "1810_next_generation_certificate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case-text', default=None)
    parser.add_argument('--mode', default='general')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1800 NEXT GENERATION NEOLEGAL AI RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = cmd + ['--mode', args.mode]
        if args.case_text: full += ['--case-text', args.case_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1800 Next Generation NeoLegal AI','mode':args.mode,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1800_next_generation_neolegal_ai_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1800 NEXT GENERATION NEOLEGAL AI SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(44)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
