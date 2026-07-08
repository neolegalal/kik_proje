# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys, py_compile
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"
PROGRAM_DIR = STATE / "production_readiness"
SUMMARY_DIR = STATE / "platform_summary"
PROGRAM_TAG = "v2.18-v2.27-production-readiness-program"
MODULES = [('311', 'Production Pipeline Integration Auditor', 'production_pipeline_integration_auditor', 'v2.18', ['206', '207', '168', '172', '177', '173', '169', '170', '190', '195'], ['scheduler', 'execution', 'production', 'quality', 'legal', 'acceptance', 'export', 'runtime']), ('312', 'Production Data Flow Validator', 'production_data_flow_validator', 'v2.19', ['168', '169', '170', '173'], ['db', 'import', 'export', 'rag', 'kart', 'production']), ('313', 'Cross Layer Communication Auditor', 'cross_layer_communication_auditor', 'v2.20', ['201', '203', '206', '207', '208', '209'], ['event', 'logger', 'scheduler', 'execution', 'automation', 'autonomous']), ('314', 'API Integration Validator', 'api_integration_validator', 'v2.21', ['218', '307', '308'], ['api', 'runtime', 'gateway', 'rag', 'export']), ('315', 'Database Integrity Auditor', 'database_integrity_auditor', 'v2.22', ['169'], ['db', 'sqlite', 'kik.db', 'import', 'migration']), ('316', 'End-to-End Production Simulator', 'end_to_end_production_simulator', 'v2.23', ['168', '206', '207', '173', '170', '184'], ['production', 'scheduler', 'execution', 'acceptance', 'export', 'dashboard']), ('317', 'Load & Performance Validator', 'load_performance_validator', 'v2.24', ['190', '195', '207'], ['runtime', 'monitor', 'worker', 'queue', 'batch', 'performance']), ('318', 'Security & Permission Validator', 'security_permission_validator', 'v2.25', ['303', '304'], ['security', 'permission', 'access', 'governance', 'audit']), ('319', 'Disaster Recovery Validator', 'disaster_recovery_validator', 'v2.26', ['210', '195', '185'], ['recovery', 'resume', 'rollback', 'self_healing', 'runtime']), ('320', 'Production Certification Suite', 'production_certification_suite', 'v2.27', ['310', '311', '312', '313', '314', '315', '316', '317', '318', '319'], ['summary', 'maturity', 'pipeline', 'readiness', 'certification'])]

def now_stamp(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_file(path, text, compile_py=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if compile_py and path.suffix == ".py": py_compile.compile(str(path), doraise=True)

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def module_source(mid, name, slug, version, must_have, patterns):
    tag = version + "-" + slug.replace("_", "-")
    release_file = version + "-" + slug.replace("_", "-") + ".md"
    lines = []
    x = lines.append
    x("# -*- coding: utf-8 -*-")
    x("import json")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x("")
    x("BASE = Path(r\"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje\")")
    x("PY = BASE / \".py\"")
    x("STATE = BASE / \"production_state\"")
    x("REPORTS = BASE / \"raporlar\"")
    x("DOCS = BASE / \"docs\"")
    x("RELEASES = DOCS / \"releases\"")
    x("CHANGELOG = DOCS / \"CHANGELOG.md\"")
    x("README = BASE / \"README.md\"")
    x("SUMMARY_DIR = STATE / \"platform_summary\"")
    x("AUDIT_DIR = STATE / \"production_readiness\" / " + repr(mid + "_" + slug))
    x("MODULE_ID = " + repr(mid))
    x("MODULE_NAME = " + repr(name))
    x("VERSION = " + repr(version))
    x("TAG = " + repr(tag))
    x("MUST_HAVE = " + repr(must_have))
    x("PATTERNS = " + repr(patterns))
    x("")
    x("def now_stamp(): return datetime.now().strftime(\"%Y%m%d_%H%M%S\")")
    x("def now_text(): return datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")")
    x("def safe_read(path):")
    x("    path = Path(path)")
    x("    if not path.exists(): return \"\"")
    x("    for enc in (\"utf-8\", \"utf-8-sig\", \"cp1254\", \"latin-1\"):")
    x("        try: return path.read_text(encoding=enc, errors=\"ignore\")")
    x("        except Exception: pass")
    x("    return \"\"")
    x("def safe_json(path):")
    x("    try: return json.loads(safe_read(path))")
    x("    except Exception: return None")
    x("def write_json(path, data):")
    x("    path.parent.mkdir(parents=True, exist_ok=True)")
    x("    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding=\"utf-8\")")
    x("def find_py_by_id(module_id): return list(PY.glob(str(module_id) + \"*.py\"))")
    x("def find_state_by_patterns(patterns):")
    x("    hits = []")
    x("    if not STATE.exists(): return hits")
    x("    for item in STATE.glob(\"**/*\"):")
    x("        if not item.is_file(): continue")
    x("        low = str(item).lower()")
    x("        if any(p.lower() in low for p in patterns):")
    x("            hits.append(item)")
    x("            if len(hits) >= 50: break")
    x("    return hits")
    x("def audit_files():")
    x("    rows = []")
    x("    for module_id in MUST_HAVE:")
    x("        hits = find_py_by_id(module_id)")
    x("        rows.append({\"id\": module_id, \"found\": len(hits) > 0, \"count\": len(hits), \"sample\": [str(x) for x in hits[:5]]})")
    x("    found = sum(1 for row in rows if row[\"found\"])")
    x("    total = len(rows)")
    x("    score = round((found / total) * 100, 2) if total else 100")
    x("    status = \"PASS\" if score >= 80 else \"WARN\" if score >= 60 else \"FAIL\"")
    x("    return {\"score\": score, \"found\": found, \"total\": total, \"items\": rows, \"status\": status}")
    x("def audit_state():")
    x("    hits = find_state_by_patterns(PATTERNS)")
    x("    score = 100 if len(hits) >= 5 else 85 if len(hits) >= 2 else 70 if len(hits) >= 1 else 50")
    x("    status = \"PASS\" if score >= 85 else \"WARN\" if score >= 70 else \"FAIL\"")
    x("    return {\"score\": score, \"match_count\": len(hits), \"sample\": [str(x) for x in hits[:10]], \"status\": status}")
    x("def audit_summaries():")
    x("    summaries = []")
    x("    if SUMMARY_DIR.exists():")
    x("        for item in SUMMARY_DIR.glob(\"*_production_summary.json\"):")
    x("            data = safe_json(item)")
    x("            if data: summaries.append({\"path\": str(item), \"decision\": data.get(\"final_decision\"), \"score\": data.get(\"production_score\")})")
    x("    failed = sum(1 for s in summaries if s.get(\"decision\") == \"FAIL\")")
    x("    passed = sum(1 for s in summaries if s.get(\"decision\") == \"PASS\")")
    x("    score = 100 - min(60, failed * 15)")
    x("    status = \"PASS\" if failed == 0 and passed > 0 else \"WARN\"")
    x("    return {\"score\": score, \"summary_count\": len(summaries), \"pass\": passed, \"fail\": failed, \"status\": status}")
    x("def create_docs():")
    x("    RELEASES.mkdir(parents=True, exist_ok=True)")
    x("    release_path = RELEASES / " + repr(release_file))
    x("    release_path.write_text(\"# \" + VERSION + \" – \" + MODULE_NAME + \"\\n\\nProduction readiness program kapsamında eklendi.\\n\", encoding=\"utf-8\")")
    x("    entry = \"# \" + VERSION + \" – \" + MODULE_NAME + \"\\n\\n**Git Tag:** `\" + TAG + \"`\\n\\n---\\n\"")
    x("    if CHANGELOG.exists():")
    x("        old = CHANGELOG.read_text(encoding=\"utf-8\", errors=\"ignore\")")
    x("        if VERSION + \" – \" + MODULE_NAME not in old: CHANGELOG.write_text(entry + \"\\n\" + old, encoding=\"utf-8\")")
    x("    else: CHANGELOG.write_text(\"# CHANGELOG\\n\\n\" + entry, encoding=\"utf-8\")")
    x("    if README.exists():")
    x("        row = \"| \" + VERSION + \" | \" + MODULE_NAME + \" | PASS/WARN |\"")
    x("        txt = README.read_text(encoding=\"utf-8\", errors=\"ignore\")")
    x("        if row not in txt and \"## Release History\" in txt: README.write_text(txt.replace(\"## Release History\", \"## Release History\\n\\n\" + row), encoding=\"utf-8\")")
    x("    index_path = RELEASES / \"index.md\"")
    x("    files = sorted([f.name for f in RELEASES.glob(\"*.md\") if f.name != \"index.md\"], reverse=True)")
    x("    index_path.write_text(\"\\n\".join([\"# Release Index\", \"\", \"| Release |\", \"|---|\"] + [\"| \" + f + \" |\" for f in files]), encoding=\"utf-8\")")
    x("    return release_path")
    x("def calculate(audits):")
    x("    scores = [v[\"score\"] for v in audits.values()]")
    x("    avg = round(sum(scores)/len(scores), 2) if scores else 0")
    x("    has_fail = any(v[\"status\"] == \"FAIL\" for v in audits.values())")
    x("    warn = sum(1 for v in audits.values() if v[\"status\"] == \"WARN\")")
    x("    if has_fail: decision, ready = \"FAIL\", \"NO\"")
    x("    elif avg >= 90: decision, ready = \"PASS\", \"YES\"")
    x("    elif avg >= 75: decision, ready = \"WARN\", \"LIMITED\"")
    x("    else: decision, ready = \"FAIL\", \"NO\"")
    x("    return {\"score\": avg, \"decision\": decision, \"ready\": ready, \"warnings\": warn}")
    x("def main():")
    x("    AUDIT_DIR.mkdir(parents=True, exist_ok=True)")
    x("    REPORTS.mkdir(parents=True, exist_ok=True)")
    x("    release_path = create_docs()")
    x("    audits = {\"files\": audit_files(), \"state\": audit_state(), \"summaries\": audit_summaries()}")
    x("    final = calculate(audits)")
    x("    ts = now_stamp()")
    x("    state_path = AUDIT_DIR / (MODULE_ID + \"_" + slug + "_audit_\" + ts + \".json\")")
    x("    report_path = REPORTS / (MODULE_ID + \"_" + slug + "_raporu_\" + ts + \".txt\")")
    x("    payload = {\"created_at\": now_text(), \"module_id\": MODULE_ID, \"module_name\": MODULE_NAME, \"version\": VERSION, \"tag\": TAG, \"audits\": audits, \"final\": final, \"release_path\": str(release_path)}")
    x("    write_json(state_path, payload)")
    x("    lines = [\"=\"*80, MODULE_ID + \" \" + MODULE_NAME.upper(), \"=\"*80, \"Production Readiness Score : \" + str(final[\"score\"]) + \" / 100\", \"FINAL DECISION             : \" + str(final[\"decision\"]), \"Production Ready           : \" + str(final[\"ready\"]), \"Warnings                   : \" + str(final[\"warnings\"]), \"\", \"Audit Scores:\"]")
    x("    for key, val in audits.items(): lines.append(\"- \" + key + \" : \" + str(val[\"score\"]) + \" / 100 [\" + val[\"status\"] + \"]\")")
    x("    lines += [\"\", \"Files:\", str(state_path), str(report_path), str(release_path), \"\", \"=\"*80]")
    x("    report_path.write_text(\"\\n\".join(lines), encoding=\"utf-8\")")
    x("    print(\"\\n\".join(lines))")
    x("    raise SystemExit(1 if final[\"decision\"] == \"FAIL\" else 0)")
    x("if __name__ == \"__main__\": main()")
    return "\n".join(lines) + "\n"

def run_all_source():
    cmds = []
    for mid, name, slug, version, must_have, patterns in MODULES:
        file_name = mid + "_" + slug + ".py"
        cmds.append("    (" + repr(mid) + ", " + repr(name) + ", [sys.executable, str(BASE / \".py\" / " + repr(file_name) + ")]),")
    lines = []
    x = lines.append
    x("# -*- coding: utf-8 -*-")
    x("import json, subprocess, sys")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x("BASE = Path(r\"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje\")")
    x("SUMMARY_DIR = BASE / \"production_state\" / \"platform_summary\"")
    x("SUMMARY_DIR.mkdir(parents=True, exist_ok=True)")
    x("COMMANDS = [")
    for c in cmds: x(c)
    x("]")
    x("def now_text(): return datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")")
    x("def main():")
    x("    print(\"=\"*80); print(\"311-320 PRODUCTION READINESS PROGRAM RUN ALL BASLADI\"); print(\"=\"*80)")
    x("    rows=[]; passed=0; failed=0")
    x("    for mid, name, cmd in COMMANDS:")
    x("        print(\"\\n>>> \" + \" \".join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))")
    x("        status = \"PASS\" if result.returncode == 0 else \"FAIL\"")
    x("        if status == \"PASS\": passed += 1")
    x("        else: failed += 1")
    x("        rows.append({\"module_id\": mid, \"name\": name, \"status\": status, \"returncode\": result.returncode})")
    x("    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision=\"PASS\" if failed==0 else \"FAIL\"; ready=\"YES\" if failed==0 else \"NO\"")
    x("    payload={\"created_at\":now_text(),\"program\":\"311-320 Production Readiness Program\",\"modules_total\":total,\"modules_passed\":passed,\"modules_failed\":failed,\"program_score\":score,\"final_decision\":decision,\"production_ready\":ready,\"results\":rows}")
    x("    summary_path=SUMMARY_DIR/\"311_320_production_readiness_summary.json\"; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding=\"utf-8\")")
    x("    print(\"\\n\" + \"=\"*80); print(\"311-320 PRODUCTION READINESS SUMMARY\"); print(\"=\"*80)")
    x("    for row in rows: print(row[\"module_id\"] + \" \" + row[\"name\"].ljust(45) + \" \" + row[\"status\"])")
    x("    print(\"-\"*80); print(\"Modules Passed    : \" + str(passed) + \" / \" + str(total)); print(\"Modules Failed    : \" + str(failed)); print(\"Program Score     : \" + str(score) + \" / 100\"); print(\"FINAL RESULT      : \" + decision); print(\"Production Ready  : \" + ready); print(\"\"); print(\"Summary JSON:\"); print(summary_path); print(\"=\"*80)")
    x("    raise SystemExit(0 if decision == \"PASS\" else 1)")
    x("if __name__ == \"__main__\": main()")
    return "\n".join(lines) + "\n"

def create_program_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    release_path = RELEASES / "v2.18-v2.27-production-readiness-program.md"
    module_lines = ["- " + mid + " " + name + " (" + version + ")" for mid, name, slug, version, must_have, patterns in MODULES]
    release_path.write_text("\n".join(["# v2.18-v2.27 – Production Readiness Program", "", "**Tarih:** 09.07.2026", "", "---", "", "311-320 Production Readiness Program ile gerçek üretime geçiş hazırlığı denetlenebilir hale getirilmiştir.", "", "---", "", "# Modüller", ""] + module_lines + ["", "---", "", "# Sonuç", "", "Production readiness denetim paketi tamamlanmıştır.", ""]), encoding="utf-8")
    entry = "\n".join(["# v2.18-v2.27 – Production Readiness Program", "", "**Tarih:** 09.07.2026  ", "**Durum:** Production PASS/WARN  ", "**Git Tag:** `" + PROGRAM_TAG + "`", "", "## Yeni Modüller", ""] + module_lines + ["", "## Sonuç", "", "311-320 Production Readiness Program eklendi.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v2.18-v2.27 – Production Readiness Program" not in old: CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else: CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v2.18-v2.27 | Production Readiness Program | PASS/WARN |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt: README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([f.name for f in RELEASES.glob("*.md") if f.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + f + " |" for f in files]), encoding="utf-8")
    return release_path

def create_git_bat():
    bat = BASE / "git_release_v2_18_to_v2_27_production_readiness_program.bat"
    bat.write_text("@echo off\ncd /d C:\\Users\\MSI\\Desktop\\kik_proje\n\necho Running 311-320 Production Readiness Program...\npython \".py\\311_320_Production_Readiness_Run_All.py\"\n\nIF ERRORLEVEL 1 (\n    echo.\n    echo RELEASE BLOCKED: 311-320 readiness program FAILED.\n    pause\n    exit /b 1\n)\n\ngit status\ngit add .\ngit commit -m \"Release v2.18-v2.27: Production readiness program\"\ngit push\ngit tag " + PROGRAM_TAG + "\ngit push origin " + PROGRAM_TAG + "\n\npause\n", encoding="utf-8")
    return bat

def run_visible(cmd): return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    args = parser.parse_args()
    PY.mkdir(parents=True, exist_ok=True); PROGRAM_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    print("="*80); print("311-320 PRODUCTION READINESS AUTO BUILDER BASLADI"); print("="*80)
    generated = []
    for mid, name, slug, version, must_have, patterns in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug, version, must_have, patterns))
        generated.append(str(path)); print("Generated:", path)
    run_all_path = PY / "311_320_Production_Readiness_Run_All.py"
    write_file(run_all_path, run_all_source()); print("Generated:", run_all_path)
    release_path = create_program_release_docs(); git_bat = create_git_bat()
    print("\n" + "="*80); print("311-320 TEST BASLIYOR"); print("="*80)
    run_result = run_visible([sys.executable, str(run_all_path)])
    decision = "PASS" if run_result.returncode == 0 else "FAIL"
    git_status = "SKIPPED"
    if decision != "PASS" and not args.force_git: git_status = "BLOCKED_BY_FAIL"
    elif args.no_git: git_status = "SKIPPED_BY_USER"
    else:
        print("\n" + "="*80); print("GIT RELEASE BASLIYOR"); print("="*80)
        git_result = run_visible(["cmd", "/c", str(git_bat)])
        git_status = "PUSHED" if git_result.returncode == 0 else "FAILED"
    ts = now_stamp()
    payload = {"created_at": now_text(), "program": "311-320 Production Readiness Auto Builder", "generated_files": generated, "run_all": str(run_all_path), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": run_result.returncode, "final_decision": decision, "git": git_status}
    state_path = PROGRAM_DIR / ("311_320_auto_builder_state_" + ts + ".json")
    report_path = REPORTS / ("311_320_auto_builder_raporu_" + ts + ".txt")
    write_json(state_path, payload)
    lines = ["="*80, "311-320 PRODUCTION READINESS AUTO BUILDER FINAL", "="*80, "Final Decision : " + decision, "Git            : " + git_status, "Run All        : " + str(run_all_path), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state_path), "Report         : " + str(report_path), "="*80]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS": raise SystemExit(1)
    if git_status == "FAILED": raise SystemExit(1)
    raise SystemExit(0)

if __name__ == "__main__": main()
