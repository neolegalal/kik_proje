# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1950", "Unified Decision Processor SDK", [sys.executable, str(BASE / ".py" / "1950_Unified_Decision_Processor_SDK.py")]),
    ("1951", "Dispute Topic Splitter", [sys.executable, str(BASE / ".py" / "1951_dispute_topic_splitter.py")]),
    ("1952", "Decision Metadata Reader", [sys.executable, str(BASE / ".py" / "1952_decision_metadata_reader.py")]),
    ("1953", "Per Topic Legal Analyzer", [sys.executable, str(BASE / ".py" / "1953_per_topic_legal_analyzer.py")]),
    ("1954", "Engine Chain Orchestrator", [sys.executable, str(BASE / ".py" / "1954_engine_chain_orchestrator.py")]),
    ("1955", "Master Record Builder", [sys.executable, str(BASE / ".py" / "1955_master_record_builder.py")]),
    ("1956", "Web Card Exporter", [sys.executable, str(BASE / ".py" / "1956_web_card_exporter.py")]),
    ("1957", "Rag Context Exporter", [sys.executable, str(BASE / ".py" / "1957_rag_context_exporter.py")]),
    ("1958", "Unified Quality Gate", [sys.executable, str(BASE / ".py" / "1958_unified_quality_gate.py")]),
    ("1959", "Pilot Batch Runner", [sys.executable, str(BASE / ".py" / "1959_pilot_batch_runner.py")]),
    ("1960", "Production Pilot Certificate", [sys.executable, str(BASE / ".py" / "1960_production_pilot_certificate.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--decision-text', default=None)
    parser.add_argument('--batch-size', type=int, default=10)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print('=' * 80)
    print('1950 UNIFIED DECISION PROCESSOR RUN ALL BASLADI')
    print('=' * 80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        full = cmd + ['--batch-size', str(args.batch_size)]
        if args.decision_text: full += ['--decision-text', args.decision_text]
        if args.execute: full.append('--execute')
        print('\n>>> ' + ' '.join(full))
        result = subprocess.run(full, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'1950 Unified Decision Processor','execute':args.execute,'batch_size':args.batch_size,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'1950_unified_decision_processor_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n'+'='*80); print('1950 UNIFIED DECISION PROCESSOR SUMMARY'); print('='*80)
    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])
    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision=='PASS' else 1)
if __name__=='__main__': main()
