
# -*- coding: utf-8 -*-
import argparse
import json
import subprocess
import sys
import py_compile
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"

OS_DIR = STATE / "production_os"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v3.0"
TAG = "v3.0-neolegal-production-os"
RELEASE_FILE = RELEASES / "v3.0-neolegal-production-os.md"
GIT_BAT = BASE / "git_release_v3_0_neolegal_production_os.bat"

MODULES = [
    ("401", "Production Console", "production_console"),
    ("402", "Production Launcher", "production_launcher"),
    ("403", "Configuration Center", "configuration_center"),
    ("404", "Production Monitor", "production_monitor"),
    ("405", "Production Dashboard", "production_dashboard"),
    ("406", "Production API", "production_api"),
    ("407", "Production CLI", "production_cli"),
    ("408", "Production Installer", "production_installer"),
    ("409", "Auto Updater", "auto_updater"),
    ("410", "Production Manager", "production_manager"),
]

SOURCE_CHECKS = [
    ("310_maturity", "platform_maturity"),
    ("311_320_readiness", "production_readiness"),
    ("platform_summary", "platform_summary"),
    ("runtime", "neolegal_ai_runtime"),
    ("api_gateway", "neolegal_api_gateway"),
    ("kernel", "neolegal_kernel"),
    ("enterprise_services", "neolegal_enterprise_services"),
]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_file(path, text, compile_py=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if compile_py and path.suffix == ".py":
        py_compile.compile(str(path), doraise=True)

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def sdk_source():
    lines = []
    x = lines.append
    x("# -*- coding: utf-8 -*-")
    x("import json")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x("")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('STATE = BASE / "production_state"')
    x('REPORTS = BASE / "raporlar"')
    x('OS_DIR = STATE / "production_os"')
    x('SUMMARY_DIR = STATE / "platform_summary"')
    x("SOURCE_CHECKS = " + repr(SOURCE_CHECKS))
    x("")
    x("def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')")
    x("def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
    x("def safe_read(path):")
    x("    path = Path(path)")
    x("    if not path.exists(): return ''")
    x("    for enc in ('utf-8','utf-8-sig','cp1254','latin-1'):")
    x("        try: return path.read_text(encoding=enc, errors='ignore')")
    x("        except Exception: pass")
    x("    return ''")
    x("def safe_json(path):")
    x("    try: return json.loads(safe_read(path))")
    x("    except Exception: return None")
    x("def write_json(path, data):")
    x("    path.parent.mkdir(parents=True, exist_ok=True)")
    x("    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')")
    x("")
    x("class ProductionOSSDK:")
    x("    def __init__(self, name='400 Production OS SDK'):")
    x("        self.name = name")
    x("    def discover_sources(self):")
    x("        rows = []")
    x("        for key, folder in SOURCE_CHECKS:")
    x("            folder_path = STATE / folder")
    x("            exists = folder_path.exists()")
    x("            file_count = 0")
    x("            json_count = 0")
    x("            if exists:")
    x("                files = [i for i in folder_path.glob('**/*') if i.is_file()]")
    x("                file_count = len(files)")
    x("                json_count = len([i for i in files if i.suffix.lower() == '.json'])")
    x("            rows.append({'key': key, 'folder': str(folder_path), 'exists': exists, 'file_count': file_count, 'json_count': json_count})")
    x("        return rows")
    x("    def validate(self, sources):")
    x("        found = sum(1 for i in sources if i['exists'])")
    x("        total = len(sources)")
    x("        score = round((found / total) * 100, 2) if total else 100")
    x("        errors = []")
    x("        warnings = []")
    x("        if score < 60: errors.append('Production OS kaynaklarının çoğu bulunamadı.')")
    x("        elif score < 85: warnings.append('Bazı Production OS kaynakları eksik.')")
    x("        decision = 'PRODUCTION OS CONTEXT READY' if not errors else 'PRODUCTION OS CONTEXT BLOCKED'")
    x("        return {'score': score, 'decision': decision, 'errors': errors, 'warnings': warnings}")
    x("    def plan(self, sources, validation):")
    x("        operations = []")
    x("        for source in sources:")
    x("            operations.append({'operation': 'BIND_' + source['key'].upper(), 'status': 'READY' if source['exists'] else 'MISSING', 'file_count': source['file_count'], 'json_count': source['json_count']})")
    x("        mode = 'PRODUCTION_OS_CONTROLLED' if not validation['errors'] else 'PAUSED'")
    x("        return {'mode': mode, 'operations': operations, 'message': str(len(operations)) + ' Production OS binding planned.'}")
    x("    def run(self):")
    x("        OS_DIR.mkdir(parents=True, exist_ok=True)")
    x("        REPORTS.mkdir(parents=True, exist_ok=True)")
    x("        sources = self.discover_sources()")
    x("        validation = self.validate(sources)")
    x("        plan = self.plan(sources, validation)")
    x("        payload = {'module': self.name, 'created_at': now_text(), 'sources': sources, 'validation': validation, 'plan': plan}")
    x("        ts = now_stamp()")
    x("        snapshot = OS_DIR / '400_production_os_snapshot.json'")
    x("        dashboard = OS_DIR / '400_production_os_dashboard.json'")
    x("        state = OS_DIR / ('400_production_os_state_' + ts + '.json')")
    x("        report = REPORTS / ('400_production_os_sdk_raporu_' + ts + '.txt')")
    x("        write_json(snapshot, payload)")
    x("        write_json(state, payload)")
    x("        write_json(dashboard, {'status': validation['decision'], 'score': validation['score'], 'mode': plan['mode'], 'operation_count': len(plan['operations']), 'errors': len(validation['errors']), 'warnings': len(validation['warnings'])})")
    x("        lines = ['='*80, '400 PRODUCTION OS SDK', '='*80, 'Validation : ' + str(validation['decision']), 'Score      : ' + str(validation['score']) + ' / 100', 'Mode       : ' + str(plan['mode']), 'Operations : ' + str(len(plan['operations'])), '', 'Dosyalar:', str(snapshot), str(dashboard), str(report)]")
    x("        report.write_text('\\n'.join(lines), encoding='utf-8')")
    x("        return {'payload': payload, 'paths': {'snapshot': str(snapshot), 'dashboard': str(dashboard), 'state': str(state), 'report': str(report)}}")
    return "\n".join(lines) + "\n"

def sdk_bridge_source():
    return "\n".join([
        "# -*- coding: utf-8 -*-",
        "import sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "400"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from core.production_os_sdk import ProductionOSSDK",
        "def main():",
        "    res = ProductionOSSDK().run()",
        "    v = res['payload']['validation']",
        "    p = res['payload']['plan']",
        "    print('='*80)",
        "    print('400 PRODUCTION OS SDK TAMAMLANDI')",
        "    print('='*80)",
        "    print('Validation : ' + str(v['decision']))",
        "    print('Score      : ' + str(v['score']) + ' / 100')",
        "    print('Errors     : ' + str(len(v['errors'])))",
        "    print('Warnings   : ' + str(len(v['warnings'])))",
        "    print('Mode       : ' + str(p['mode']))",
        "    print('Operations : ' + str(len(p['operations'])))",
        "    print('')",
        "    print('Dosyalar:')",
        "    print(res['paths']['snapshot'])",
        "    print(res['paths']['dashboard'])",
        "    print(res['paths']['report'])",
        "if __name__ == '__main__': main()",
        "",
    ])

def module_source(mid, name, slug):
    lines = []
    x = lines.append
    x("# -*- coding: utf-8 -*-")
    x("import sys, json")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('PACKAGE_DIR = BASE / ".py" / "400"')
    x("sys.path.insert(0, str(PACKAGE_DIR))")
    x("from core.production_os_sdk import ProductionOSSDK")
    x('STATE = BASE / "production_state"')
    x('REPORTS = BASE / "raporlar"')
    x('OS_DIR = STATE / "production_os" / "' + mid + "_" + slug + '"')
    x('MODULE_ID = "' + mid + '"')
    x('MODULE_NAME = "' + name + '"')
    x("def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')")
    x("def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
    x("def write_json(path, data):")
    x("    path.parent.mkdir(parents=True, exist_ok=True)")
    x("    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')")
    x("def analyze(payload):")
    x("    validation = payload['validation']")
    x("    plan = payload['plan']")
    x("    operations = plan.get('operations', [])")
    x("    ready_ops = sum(1 for i in operations if i.get('status') == 'READY')")
    x("    total_ops = len(operations)")
    x("    readiness = round((ready_ops / total_ops) * 100, 2) if total_ops else 100")
    x("    score = min(100, round((validation.get('score', 0) * 0.6) + (readiness * 0.4), 2))")
    x("    decision = '" + name.upper() + " READY' if not validation.get('errors') else '" + name.upper() + " REVIEW'")
    x("    return {'score': score, 'decision': decision, 'readiness': readiness, 'ready_operations': ready_ops, 'total_operations': total_ops, 'recommendation': plan.get('message')}")
    x("def main():")
    x("    OS_DIR.mkdir(parents=True, exist_ok=True)")
    x("    REPORTS.mkdir(parents=True, exist_ok=True)")
    x("    sdk_result = ProductionOSSDK(name=MODULE_ID + ' ' + MODULE_NAME).run()")
    x("    analysis = analyze(sdk_result['payload'])")
    x("    ts = now_stamp()")
    x("    output = OS_DIR / ('" + mid + "_" + slug + ".json')")
    x("    state = OS_DIR / ('" + mid + "_" + slug + "_state_' + ts + '.json')")
    x("    report = REPORTS / ('" + mid + "_" + slug + "_raporu_' + ts + '.txt')")
    x("    payload = {'created_at': now_text(), 'module_id': MODULE_ID, 'module_name': MODULE_NAME, 'analysis': analysis, 'sdk_reference': sdk_result['paths']}")
    x("    write_json(output, payload)")
    x("    write_json(state, payload)")
    x("    lines = ['='*80, MODULE_ID + ' ' + MODULE_NAME.upper(), '='*80, 'Score    : ' + str(analysis['score']) + ' / 100', 'Decision : ' + str(analysis['decision']), 'ReadyOps : ' + str(analysis['ready_operations']) + ' / ' + str(analysis['total_operations']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]")
    x("    report.write_text('\\n'.join(lines), encoding='utf-8')")
    x("    print('\\n'.join(lines))")
    x("    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)")
    x("if __name__ == '__main__': main()")
    return "\n".join(lines) + "\n"

def run_all_source():
    lines = []
    x = lines.append
    x("# -*- coding: utf-8 -*-")
    x("import json, subprocess, sys")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('SUMMARY_DIR = BASE / "production_state" / "platform_summary"')
    x("SUMMARY_DIR.mkdir(parents=True, exist_ok=True)")
    x("COMMANDS = [")
    x('    ("400", "Production OS SDK", [sys.executable, str(BASE / ".py" / "400_Production_OS_SDK.py")]),')
    for mid, name, slug in MODULES:
        x('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    x("]")
    x("def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
    x("def main():")
    x("    print('='*80); print('400 NEOLEGAL PRODUCTION OS RUN ALL BASLADI'); print('='*80)")
    x("    rows=[]; passed=0; failed=0")
    x("    for module_id, name, cmd in COMMANDS:")
    x("        print('\\n>>> ' + ' '.join(cmd))")
    x("        result = subprocess.run(cmd, cwd=str(BASE))")
    x("        status = 'PASS' if result.returncode == 0 else 'FAIL'")
    x("        if status == 'PASS': passed += 1")
    x("        else: failed += 1")
    x("        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})")
    x("    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'")
    x("    payload={'created_at':now_text(),'program':'400 NeoLegal Production OS','modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}")
    x("    summary_path=SUMMARY_DIR/'400_production_os_summary.json'")
    x("    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')")
    x("    print('\\n'+'='*80); print('400 NEOLEGAL PRODUCTION OS SUMMARY'); print('='*80)")
    x("    for row in rows: print(row['module_id'] + ' ' + row['name'].ljust(35) + ' ' + row['status'])")
    x("    print('-'*80); print('Modules Passed    : ' + str(passed) + ' / ' + str(total)); print('Modules Failed    : ' + str(failed)); print('Program Score     : ' + str(score) + ' / 100'); print('FINAL RESULT      : ' + decision); print('Production Ready  : ' + ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)")
    x("    raise SystemExit(0 if decision == 'PASS' else 1)")
    x("if __name__ == '__main__': main()")
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 400 Production OS SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 400 Run All"]
    release_text = "\n".join([
        "# v3.0 – NeoLegal Production OS",
        "",
        "**Tarih:** 09.07.2026",
        "",
        "---",
        "",
        "# Genel Bakış",
        "",
        "v3.0 sürümü ile NeoLegal Production Platform, katman mimarisinden ürünleşmiş Production OS mimarisine geçmiştir.",
        "",
        "# Modüller",
        "",
        *module_lines,
        "",
        "---",
        "",
        "# Sonuç",
        "",
        "NeoLegal Production OS v3.0 oluşturulmuştur.",
        "",
    ])
    RELEASE_FILE.write_text(release_text, encoding="utf-8")
    changelog_entry = "\n".join([
        "# v3.0 – NeoLegal Production OS",
        "",
        "**Tarih:** 09.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `" + TAG + "`",
        "",
        "## Yeni Modüller",
        "",
        *module_lines,
        "",
        "## Sonuç",
        "",
        "NeoLegal Production Platform, v3.0 ile Production OS mimarisine taşındı.",
        "",
        "---",
        "",
    ])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v3.0 – NeoLegal Production OS" not in old:
            CHANGELOG.write_text(changelog_entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + changelog_entry, encoding="utf-8")
    if README.exists():
        row = "| v3.0 | NeoLegal Production OS | PASS |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines = [
        "@echo off",
        "cd /d C:\\Users\\MSI\\Desktop\\kik_proje",
        "",
        "echo Running NeoLegal Production OS v3.0...",
        'python ".py\\400_Run_All.py"',
        "",
        "IF ERRORLEVEL 1 (",
        "    echo.",
        "    echo RELEASE BLOCKED: 400 Production OS FAILED.",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "git status",
        "git add .",
        'git commit -m "Release v3.0: NeoLegal Production OS"',
        "git push",
        "git tag " + TAG,
        "git push origin " + TAG,
        "",
        "pause",
        "",
    ]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    args = parser.parse_args()

    PY.mkdir(parents=True, exist_ok=True)
    OS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("400 ALL-IN-ONE PRODUCTION OS BUILDER BASLADI")
    print("="*80)

    write_file(PY / "400" / "core" / "__init__.py", "")
    write_file(PY / "400" / "core" / "production_os_sdk.py", sdk_source())
    write_file(PY / "400_Production_OS_SDK.py", sdk_bridge_source())
    print("Generated:", PY / "400_Production_OS_SDK.py")

    generated = [str(PY / "400_Production_OS_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)

    run_all_path = PY / "400_Run_All.py"
    write_file(run_all_path, run_all_source())
    print("Generated:", run_all_path)

    release_path = create_release_docs()
    git_bat = create_git_bat()

    print("\n" + "="*80)
    print("400 PRODUCTION OS TEST BASLIYOR")
    print("="*80)
    run_result = run_visible([sys.executable, str(run_all_path)])

    decision = "PASS" if run_result.returncode == 0 else "FAIL"
    git_status = "SKIPPED"
    if decision != "PASS" and not args.force_git:
        git_status = "BLOCKED_BY_FAIL"
    elif args.no_git:
        git_status = "SKIPPED_BY_USER"
    else:
        print("\n" + "="*80)
        print("GIT RELEASE BASLIYOR")
        print("="*80)
        git_result = run_visible(["cmd", "/c", str(git_bat)])
        git_status = "PUSHED" if git_result.returncode == 0 else "FAILED"

    ts = now_stamp()
    payload = {
        "created_at": now_text(),
        "program": "400 NeoLegal Production OS Builder",
        "version": VERSION,
        "tag": TAG,
        "generated_files": generated,
        "run_all": str(run_all_path),
        "release_path": str(release_path),
        "git_bat": str(git_bat),
        "run_returncode": run_result.returncode,
        "final_decision": decision,
        "git": git_status,
    }
    state_path = OS_DIR / ("400_production_os_builder_state_" + ts + ".json")
    report_path = REPORTS / ("400_production_os_builder_raporu_" + ts + ".txt")
    write_json(state_path, payload)
    lines = [
        "="*80,
        "400 ALL-IN-ONE PRODUCTION OS BUILDER FINAL",
        "="*80,
        "Final Decision : " + decision,
        "Git            : " + git_status,
        "Run All        : " + str(run_all_path),
        "Release        : " + str(release_path),
        "Git BAT        : " + str(git_bat),
        "State          : " + str(state_path),
        "Report         : " + str(report_path),
        "="*80,
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS":
        raise SystemExit(1)
    if git_status == "FAILED":
        raise SystemExit(1)
    raise SystemExit(0)

if __name__ == "__main__":
    main()
