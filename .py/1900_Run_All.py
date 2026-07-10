# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1900", "NeoLegal Evolution Platform SDK", [sys.executable, str(BASE / ".py" / "1900_NeoLegal_Evolution_Platform_SDK.py")]),
    ("1901", "Knowledge Graph Population", [sys.executable, str(BASE / ".py" / "1901_knowledge_graph_population.py")]),
    ("1902", "Contradiction Finder", [sys.executable, str(BASE / ".py" / "1902_contradiction_finder.py")]),
    ("1903", "Legal Pattern Discovery", [sys.executable, str(BASE / ".py" / "1903_legal_pattern_discovery.py")]),
    ("1904", "AI Learning Dataset Builder", [sys.executable, str(BASE / ".py" / "1904_ai_learning_dataset_builder.py")]),
    ("1905", "Knowledge Confidence Engine", [sys.executable, str(BASE / ".py" / "1905_knowledge_confidence_engine.py")]),
    ("1906", "Self Validation Engine", [sys.executable, str(BASE / ".py" / "1906_self_validation_engine.py")]),
    ("1907", "Hallucination Detector", [sys.executable, str(BASE / ".py" / "1907_hallucination_detector.py")]),
    ("1908", "Evidence Collector", [sys.executable, str(BASE / ".py" / "1908_evidence_collector.py")]),
    ("1909", "Continuous Learning Engine", [sys.executable, str(BASE / ".py" / "1909_continuous_learning_engine.py")]),
    ("1910", "Evolution Certificate", [sys.executable, str(BASE / ".py" / "1910_evolution_certificate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-text', default=None)
    parser.add_argument('--mode', default='general')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1900 NEOLEGAL EVOLUTION PLATFORM RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = cmd + ['--mode', args.mode]
        if args.sample_text: full += ['--sample-text', args.sample_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1900 NeoLegal Evolution Platform','mode':args.mode,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1900_neolegal_evolution_platform_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1900 NEOLEGAL EVOLUTION PLATFORM SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(42)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
