# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ('311', 'Production Pipeline Integration Auditor', [sys.executable, str(BASE / ".py" / '311_production_pipeline_integration_auditor.py')]),
    ('312', 'Production Data Flow Validator', [sys.executable, str(BASE / ".py" / '312_production_data_flow_validator.py')]),
    ('313', 'Cross Layer Communication Auditor', [sys.executable, str(BASE / ".py" / '313_cross_layer_communication_auditor.py')]),
    ('314', 'API Integration Validator', [sys.executable, str(BASE / ".py" / '314_api_integration_validator.py')]),
    ('315', 'Database Integrity Auditor', [sys.executable, str(BASE / ".py" / '315_database_integrity_auditor.py')]),
    ('316', 'End-to-End Production Simulator', [sys.executable, str(BASE / ".py" / '316_end_to_end_production_simulator.py')]),
    ('317', 'Load & Performance Validator', [sys.executable, str(BASE / ".py" / '317_load_performance_validator.py')]),
    ('318', 'Security & Permission Validator', [sys.executable, str(BASE / ".py" / '318_security_permission_validator.py')]),
    ('319', 'Disaster Recovery Validator', [sys.executable, str(BASE / ".py" / '319_disaster_recovery_validator.py')]),
    ('320', 'Production Certification Suite', [sys.executable, str(BASE / ".py" / '320_production_certification_suite.py')]),
]
def now_text(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def main():
    print("="*80); print("311-320 PRODUCTION READINESS PROGRAM RUN ALL BASLADI"); print("="*80)
    rows=[]; passed=0; failed=0
    for mid, name, cmd in COMMANDS:
        print("\n>>> " + " ".join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        status = "PASS" if result.returncode == 0 else "FAIL"
        if status == "PASS": passed += 1
        else: failed += 1
        rows.append({"module_id": mid, "name": name, "status": status, "returncode": result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={"created_at":now_text(),"program":"311-320 Production Readiness Program","modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}
    summary_path=SUMMARY_DIR/"311_320_production_readiness_summary.json"; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "="*80); print("311-320 PRODUCTION READINESS SUMMARY"); print("="*80)
    for row in rows: print(row["module_id"] + " " + row["name"].ljust(45) + " " + row["status"])
    print("-"*80); print("Modules Passed    : " + str(passed) + " / " + str(total)); print("Modules Failed    : " + str(failed)); print("Program Score     : " + str(score) + " / 100"); print("FINAL RESULT      : " + decision); print("Production Ready  : " + ready); print(""); print("Summary JSON:"); print(summary_path); print("="*80)
    raise SystemExit(0 if decision == "PASS" else 1)
if __name__ == "__main__": main()
