# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("2050", "Validation Benchmark Platform SDK", [sys.executable, str(BASE / ".py" / "2050_Validation_Benchmark_Platform_SDK.py")]),
    ("2051", "Gold Standard Builder", [sys.executable, str(BASE / ".py" / "2051_gold_standard_builder.py")]),
    ("2052", "Benchmark Runner", [sys.executable, str(BASE / ".py" / "2052_benchmark_runner.py")]),
    ("2053", "Accuracy Analyzer", [sys.executable, str(BASE / ".py" / "2053_accuracy_analyzer.py")]),
    ("2054", "Legal Consistency Checker", [sys.executable, str(BASE / ".py" / "2054_legal_consistency_checker.py")]),
    ("2055", "Explainability Engine", [sys.executable, str(BASE / ".py" / "2055_explainability_engine.py")]),
    ("2056", "Benchmark Dashboard", [sys.executable, str(BASE / ".py" / "2056_benchmark_dashboard.py")]),
    ("2057", "Human Validation Center", [sys.executable, str(BASE / ".py" / "2057_human_validation_center.py")]),
    ("2058", "Continuous Benchmark Engine", [sys.executable, str(BASE / ".py" / "2058_continuous_benchmark_engine.py")]),
    ("2059", "Scientific Report Generator", [sys.executable, str(BASE / ".py" / "2059_scientific_report_generator.py")]),
    ("2060", "Validation Certificate", [sys.executable, str(BASE / ".py" / "2060_validation_certificate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold-standard', default=None)
    parser.add_argument('--master-record', default=None)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('2050 VALIDATION & BENCHMARK PLATFORM RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = list(cmd)
        if args.gold_standard: full += ['--gold-standard', args.gold_standard]
        if args.master_record: full += ['--master-record', args.master_record]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'2050 Validation Benchmark Platform','execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'2050_validation_benchmark_platform_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('2050 VALIDATION & BENCHMARK PLATFORM SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(42)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
