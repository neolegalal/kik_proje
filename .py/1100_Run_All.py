# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("1100", "Decision Processing Pipeline SDK", [sys.executable, str(BASE / ".py" / "1100_Decision_Processing_Pipeline_SDK.py")]),
    ("1101", "Decision Source Reader", [sys.executable, str(BASE / ".py" / "1101_decision_source_reader.py")]),
    ("1102", "Text Normalizer", [sys.executable, str(BASE / ".py" / "1102_text_normalizer.py")]),
    ("1103", "Decision Metadata Extractor", [sys.executable, str(BASE / ".py" / "1103_decision_metadata_extractor.py")]),
    ("1104", "Question Title Generator", [sys.executable, str(BASE / ".py" / "1104_question_title_generator.py")]),
    ("1105", "Decision Summary Generator", [sys.executable, str(BASE / ".py" / "1105_decision_summary_generator.py")]),
    ("1106", "Result Summary Generator", [sys.executable, str(BASE / ".py" / "1106_result_summary_generator.py")]),
    ("1107", "Keyword Legislation Tagger", [sys.executable, str(BASE / ".py" / "1107_keyword_legislation_tagger.py")]),
    ("1108", "Card Quality Gate", [sys.executable, str(BASE / ".py" / "1108_card_quality_gate.py")]),
    ("1109", "Web Rag Card Builder", [sys.executable, str(BASE / ".py" / "1109_web_rag_card_builder.py")]),
    ("1110", "Decision Pipeline Auditor", [sys.executable, str(BASE / ".py" / "1110_decision_pipeline_auditor.py")]),
]
def now_text(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--batch-size", type=int, default=10); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    print("=" * 80); print("1100 DECISION PROCESSING PIPELINE RUN ALL BASLADI"); print("=" * 80)
    rows = []; passed = 0; failed = 0
    for module_id, name, cmd in COMMANDS:
        full = cmd + ["--batch-size", str(args.batch_size)]
        if args.execute: full.append("--execute")
        print("\n>>> " + " ".join(full)); result = subprocess.run(full, cwd=str(BASE))
        status = "PASS" if result.returncode == 0 else "FAIL"
        passed += 1 if status == "PASS" else 0; failed += 1 if status == "FAIL" else 0
        rows.append({"module_id": module_id, "name": name, "status": status, "returncode": result.returncode})
    total = len(COMMANDS); score = round((passed / total) * 100, 2) if total else 0; decision = "PASS" if failed == 0 else "FAIL"; ready = "YES" if failed == 0 else "NO"
    payload = {"created_at": now_text(), "program": "1100 Decision Processing Pipeline", "batch_size": args.batch_size, "execute": args.execute, "modules_total": total, "modules_passed": passed, "modules_failed": failed, "program_score": score, "final_decision": decision, "production_ready": ready, "results": rows}
    summary_path = SUMMARY_DIR / "1100_decision_processing_pipeline_summary.json"; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 80); print("1100 DECISION PROCESSING PIPELINE SUMMARY"); print("=" * 80)
    for row in rows: print(row["module_id"] + " " + row["name"].ljust(40) + " " + row["status"])
    print("-" * 80); print("Modules Passed    : " + str(passed) + " / " + str(total)); print("Modules Failed    : " + str(failed)); print("Program Score     : " + str(score) + " / 100"); print("FINAL RESULT      : " + decision); print("Production Ready  : " + ready); print(""); print("Summary JSON:"); print(summary_path); print("=" * 80)
    raise SystemExit(0 if decision == "PASS" else 1)
if __name__ == "__main__": main()
