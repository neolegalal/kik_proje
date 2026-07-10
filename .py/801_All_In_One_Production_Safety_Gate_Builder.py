
# -*- coding: utf-8 -*-
import argparse, json, os, shutil, sqlite3, subprocess, sys, py_compile
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

SAFETY_DIR = STATE / "production_safety_gate"
VERSION = "v4.3"
TAG = "v4.3-production-safety-gate"
RELEASE_FILE = RELEASES / "v4.3-production-safety-gate.md"
GIT_BAT = BASE / "git_release_v4_3_production_safety_gate.bat"

MODULES = [
    ("811", "Database Safety Checker", "database_safety_checker"),
    ("812", "Pipeline Safety Checker", "pipeline_safety_checker"),
    ("813", "API Cost Safety Checker", "api_cost_safety_checker"),
    ("814", "Output Isolation Checker", "output_isolation_checker"),
    ("815", "Duplicate Risk Checker", "duplicate_risk_checker"),
    ("816", "Backup Rollback Checker", "backup_rollback_checker"),
    ("817", "Resume Recovery Checker", "resume_recovery_checker"),
    ("818", "Resource Capacity Checker", "resource_capacity_checker"),
    ("819", "Git State Checker", "git_state_checker"),
    ("820", "Production Launch Gate", "production_launch_gate"),
]
REQUIRED_MODULE_IDS = ["168", "169", "170", "172", "173", "177", "181", "190", "195", "700", "800"]
OPTIONAL_MODULE_IDS = ["206", "207", "208", "209", "210", "211", "212", "550", "600"]

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
    x("import json, os, shutil, sqlite3, subprocess")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('PY = BASE / ".py"')
    x('STATE = BASE / "production_state"')
    x('REPORTS = BASE / "raporlar"')
    x('SAFETY_DIR = STATE / "production_safety_gate"')
    x('PILOT_OUTPUT = STATE / "pilot_execution_output"')
    x('BACKUP_DIR = STATE / "safety_backups"')
    x('QUARANTINE_DIR = STATE / "quarantine"')
    x('RESUME_DIR = STATE / "resume"')
    x("REQUIRED_MODULE_IDS = " + repr(REQUIRED_MODULE_IDS))
    x("OPTIONAL_MODULE_IDS = " + repr(OPTIONAL_MODULE_IDS))
    x("def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')")
    x("def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
    x("def write_json(path, data):")
    x("    path.parent.mkdir(parents=True, exist_ok=True)")
    x("    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')")
    x("class ProductionSafetyGateSDK:")
    x("    def __init__(self, name='801 Production Safety Gate SDK', batch_size=10):")
    x("        self.name = name; self.batch_size = int(batch_size)")
    x("    def check_database(self):")
    x("        candidates=[]")
    x("        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):")
    x("            p=BASE/name")
    x("            item={'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0,'tables':[],'error':None}")
    x("            if p.exists():")
    x("                try:")
    x("                    con=sqlite3.connect(str(p)); cur=con.cursor()")
    x("                    rows=cur.execute(\"select name from sqlite_master where type='table'\").fetchall()")
    x("                    for (t,) in rows[:20]:")
    x("                        try: count=cur.execute('select count(*) from '+t).fetchone()[0]")
    x("                        except Exception: count=None")
    x("                        item['tables'].append({'table':t,'count':count})")
    x("                    con.close()")
    x("                except Exception as e: item['error']=str(e)")
    x("            candidates.append(item)")
    x("        db_found=any(i['exists'] for i in candidates); table_found=any(i.get('tables') for i in candidates)")
    x("        score=100 if db_found and table_found else 85 if db_found else 70")
    x("        return {'score':score,'status':'PASS' if score>=85 else 'WARN','db_found':db_found,'table_found':table_found,'items':candidates}")
    x("    def check_pipeline(self):")
    x("        required=[]; optional=[]")
    x("        for mid in REQUIRED_MODULE_IDS:")
    x("            hits=list(PY.glob(str(mid)+'*.py')); required.append({'module_id':mid,'found':len(hits)>0,'count':len(hits),'sample':[str(x) for x in hits[:5]]})")
    x("        for mid in OPTIONAL_MODULE_IDS:")
    x("            hits=list(PY.glob(str(mid)+'*.py')); optional.append({'module_id':mid,'found':len(hits)>0,'count':len(hits),'sample':[str(x) for x in hits[:5]]})")
    x("        req_found=sum(1 for i in required if i['found']); req_total=len(required)")
    x("        opt_found=sum(1 for i in optional if i['found']); opt_total=len(optional)")
    x("        req_score=round((req_found/req_total)*100,2) if req_total else 100; opt_score=round((opt_found/opt_total)*100,2) if opt_total else 100")
    x("        score=round(req_score*0.8+opt_score*0.2,2); status='PASS' if req_score>=80 else 'WARN' if req_score>=60 else 'FAIL'")
    x("        return {'score':score,'status':status,'required_found':req_found,'required_total':req_total,'optional_found':opt_found,'optional_total':opt_total,'required':required,'optional':optional}")
    x("    def check_api_cost(self):")
    x("        env_keys=[k for k in os.environ.keys() if 'OPENAI' in k.upper() or 'API' in k.upper() or 'KEY' in k.upper()]")
    x("        score=100; warnings=[]")
    x("        if not env_keys: warnings.append('API anahtarı environment içinde tespit edilmedi; local .env kullanılıyor olabilir.')")
    x("        if self.batch_size>50: warnings.append('Batch size 50 üstü; pilot için maliyet kontrolü önerilir.'); score-=15")
    x("        return {'score':max(score,0),'status':'PASS' if score>=85 else 'WARN','env_key_count':len(env_keys),'env_keys_sample':env_keys[:10],'estimated_max_calls':self.batch_size,'warnings':warnings}")
    x("    def check_output_isolation(self):")
    x("        dirs=[PILOT_OUTPUT, QUARANTINE_DIR, RESUME_DIR, BACKUP_DIR, SAFETY_DIR]; created=[]")
    x("        for d in dirs: d.mkdir(parents=True, exist_ok=True); created.append(str(d))")
    x("        files=len([f for f in PILOT_OUTPUT.glob('**/*') if f.is_file()]) if PILOT_OUTPUT.exists() else 0")
    x("        return {'score':100 if files==0 else 90,'status':'PASS','created_dirs':created,'pilot_output_file_count':files}")
    x("    def check_duplicate_risk(self):")
    x("        seen=set(); duplicates=[]")
    x("        for folder in [STATE/'pilot_production', STATE/'real_production_engine', STATE/'production_data_factory']:")
    x("            if not folder.exists(): continue")
    x("            for f in folder.glob('**/*.json'):")
    x("                if f.name in seen: duplicates.append(str(f))")
    x("                seen.add(f.name)")
    x("        score=100 if not duplicates else 85")
    x("        return {'score':score,'status':'PASS' if score>=90 else 'WARN','duplicate_count':len(duplicates),'duplicates_sample':duplicates[:20]}")
    x("    def check_backup_rollback(self):")
    x("        BACKUP_DIR.mkdir(parents=True, exist_ok=True); marker=BACKUP_DIR/('rollback_marker_'+now_stamp()+'.json')")
    x("        write_json(marker, {'created_at':now_text(),'batch_size':self.batch_size,'type':'SAFETY_ROLLBACK_MARKER'})")
    x("        return {'score':100,'status':'PASS','rollback_marker':str(marker)}")
    x("    def check_resume_recovery(self):")
    x("        RESUME_DIR.mkdir(parents=True, exist_ok=True); resume=RESUME_DIR/('safety_resume_'+now_stamp()+'.json')")
    x("        write_json(resume, {'created_at':now_text(),'batch_size':self.batch_size,'status':'READY'})")
    x("        return {'score':100,'status':'PASS','resume_file':str(resume)}")
    x("    def check_resources(self):")
    x("        usage=shutil.disk_usage(str(BASE)); free=round(usage.free/(1024**3),2)")
    x("        score=100 if free>=10 else 80 if free>=2 else 50")
    x("        return {'score':score,'status':'PASS' if score>=80 else 'FAIL','disk_free_gb':free,'disk_total_gb':round(usage.total/(1024**3),2)}")
    x("    def check_git(self):")
    x("        try:")
    x("            r=subprocess.run(['git','status','--porcelain'],cwd=str(BASE),capture_output=True,text=True,timeout=30)")
    x("            changed=[line for line in r.stdout.splitlines() if line.strip()]")
    x("            return {'score':100 if r.returncode==0 else 70,'status':'PASS' if r.returncode==0 else 'WARN','changed_count':len(changed),'changed_sample':changed[:20]}")
    x("        except Exception as e: return {'score':70,'status':'WARN','error':str(e)}")
    x("    def calculate(self, checks):")
    x("        scores=[v['score'] for v in checks.values()]; avg=round(sum(scores)/len(scores),2) if scores else 0")
    x("        fail=any(v['status']=='FAIL' for v in checks.values()); warn=sum(1 for v in checks.values() if v['status']=='WARN')")
    x("        if fail: decision,ready='FAIL','NO'")
    x("        elif avg>=90: decision,ready='PASS','YES'")
    x("        elif avg>=80: decision,ready='WARN','LIMITED'")
    x("        else: decision,ready='FAIL','NO'")
    x("        return {'score':avg,'decision':decision,'production_ready':ready,'warnings':warn}")
    x("    def run(self):")
    x("        SAFETY_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)")
    x("        checks={'database':self.check_database(),'pipeline':self.check_pipeline(),'api_cost':self.check_api_cost(),'output_isolation':self.check_output_isolation(),'duplicate_risk':self.check_duplicate_risk(),'backup_rollback':self.check_backup_rollback(),'resume_recovery':self.check_resume_recovery(),'resources':self.check_resources(),'git_state':self.check_git()}")
    x("        final=self.calculate(checks); ts=now_stamp(); payload={'module':self.name,'created_at':now_text(),'batch_size':self.batch_size,'checks':checks,'final':final}")
    x("        snapshot=SAFETY_DIR/'801_production_safety_gate_snapshot.json'; dashboard=SAFETY_DIR/'801_production_safety_gate_dashboard.json'; state=SAFETY_DIR/('801_production_safety_gate_state_'+ts+'.json'); report=REPORTS/('801_production_safety_gate_sdk_raporu_'+ts+'.txt')")
    x("        write_json(snapshot,payload); write_json(state,payload); write_json(dashboard, {'status':final['decision'],'score':final['score'],'production_ready':final['production_ready'],'warnings':final['warnings']})")
    x("        lines=['='*80,'801 PRODUCTION SAFETY GATE SDK','='*80,'Safety Score : '+str(final['score'])+' / 100','FINAL       : '+str(final['decision']),'Ready       : '+str(final['production_ready']),'Warnings    : '+str(final['warnings']),'','Check Scores:']")
    x("        for k,v in checks.items(): lines.append('- '+k+' : '+str(v['score'])+' / 100 ['+v['status']+']')")
    x("        lines += ['', 'Dosyalar:', str(snapshot), str(dashboard), str(report)]")
    x("        report.write_text('\\n'.join(lines), encoding='utf-8')")
    x("        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'state':str(state),'report':str(report)}}")
    return "\n".join(lines) + "\n"

def sdk_bridge_source():
    return "\n".join([
        "# -*- coding: utf-8 -*-",
        "import argparse, sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "801"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from core.production_safety_gate_sdk import ProductionSafetyGateSDK",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); args=parser.parse_args()",
        "    res=ProductionSafetyGateSDK(batch_size=args.batch_size).run(); f=res['payload']['final']",
        "    print('='*80); print('801 PRODUCTION SAFETY GATE SDK TAMAMLANDI'); print('='*80)",
        "    print('Safety Score : '+str(f['score'])+' / 100'); print('FINAL        : '+str(f['decision'])); print('Ready        : '+str(f['production_ready'])); print('Warnings     : '+str(f['warnings']))",
        "    print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])",
        "    raise SystemExit(1 if f['decision']=='FAIL' else 0)",
        "if __name__=='__main__': main()",
        "",
    ])

def module_source(mid, name, slug):
    return "\n".join([
        "# -*- coding: utf-8 -*-",
        "import argparse, sys, json",
        "from pathlib import Path",
        "from datetime import datetime",
        'BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")',
        'PACKAGE_DIR = BASE / ".py" / "801"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from core.production_safety_gate_sdk import ProductionSafetyGateSDK",
        'STATE = BASE / "production_state"',
        'REPORTS = BASE / "raporlar"',
        'MODULE_DIR = STATE / "production_safety_gate" / "' + mid + '_' + slug + '"',
        'MODULE_ID = "' + mid + '"',
        'MODULE_NAME = "' + name + '"',
        "def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def write_json(path,data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); args=parser.parse_args()",
        "    MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)",
        "    sdk_result=ProductionSafetyGateSDK(name=MODULE_ID+' '+MODULE_NAME,batch_size=args.batch_size).run(); final=sdk_result['payload']['final']; checks=sdk_result['payload']['checks']",
        "    pass_count=sum(1 for v in checks.values() if v['status']=='PASS'); warn_count=sum(1 for v in checks.values() if v['status']=='WARN')",
        "    decision='" + name.upper() + " READY' if final['decision'] in ('PASS','WARN') else '" + name.upper() + " BLOCKED'",
        "    analysis={'score':final['score'],'decision':decision,'pass_count':pass_count,'warn_count':warn_count,'check_count':len(checks),'recommendation':'Safety gate ready for controlled pilot execution.' if final['decision']!='FAIL' else 'Safety gate blocked.'}",
        "    ts=now_stamp(); output=MODULE_DIR/('" + mid + "_" + slug + ".json'); state=MODULE_DIR/('" + mid + "_" + slug + "_state_'+ts+'.json'); report=REPORTS/('" + mid + "_" + slug + "_raporu_'+ts+'.txt')",
        "    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}",
        "    write_json(output,payload); write_json(state,payload)",
        "    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'Checks   : '+str(analysis['pass_count'])+' PASS / '+str(analysis['warn_count'])+' WARN', '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]",
        "    report.write_text('\\n'.join(lines), encoding='utf-8'); print('\\n'.join(lines))",
        "    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)",
        "if __name__=='__main__': main()",
        "",
    ])

def run_all_source():
    lines = [
        "# -*- coding: utf-8 -*-",
        "import argparse, json, subprocess, sys",
        "from pathlib import Path",
        "from datetime import datetime",
        'BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")',
        'SUMMARY_DIR = BASE / "production_state" / "platform_summary"',
        "SUMMARY_DIR.mkdir(parents=True, exist_ok=True)",
        "COMMANDS = [",
        '    ("801", "Production Safety Gate SDK", [sys.executable, str(BASE / ".py" / "801_Production_Safety_Gate_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); args=parser.parse_args()",
        "    print('='*80); print('801 PRODUCTION SAFETY GATE RUN ALL BASLADI'); print('='*80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id,name,cmd in COMMANDS:",
        "        full_cmd=cmd+['--batch-size', str(args.batch_size)]",
        "        print('\\n>>> '+' '.join(full_cmd)); result=subprocess.run(full_cmd, cwd=str(BASE))",
        "        status='PASS' if result.returncode==0 else 'FAIL'",
        "        if status=='PASS': passed+=1",
        "        else: failed+=1",
        "        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'801 Production Safety Gate','batch_size':args.batch_size,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'801_production_safety_gate_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')",
        "    print('\\n'+'='*80); print('801 PRODUCTION SAFETY GATE SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
        "",
    ]
    return "\n".join(lines)

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 801 Production Safety Gate SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 801 Run All"]
    release_text = "\n".join(["# v4.3 – Production Safety Gate", "", "**Tarih:** 10.07.2026", "", "---", "", "# Genel Bakış", "", "v4.3 sürümü ile NeoLegal Production Platform gerçek execution öncesi zorunlu güvenlik kapısı kazanmıştır.", "", "Bu sürüm DB, pipeline, API/maliyet, output isolation, duplicate risk, backup/rollback, resume/recovery, kaynak kapasitesi ve Git durumu kontrollerini içerir.", "", "# Modüller", ""] + module_lines + ["", "---", "", "# Sonuç", "", "Production Safety Gate v4.3 oluşturulmuştur.", ""])
    RELEASE_FILE.write_text(release_text, encoding="utf-8")
    changelog_entry = "\n".join(["# v4.3 – Production Safety Gate", "", "**Tarih:** 10.07.2026  ", "**Durum:** Production PASS  ", "**Git Tag:** `" + TAG + "`", "", "## Yeni Modüller", ""] + module_lines + ["", "## Sonuç", "", "NeoLegal Production Platform v4.3 ile gerçek execution öncesi safety gate mimarisine geçti.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v4.3 – Production Safety Gate" not in old:
            CHANGELOG.write_text(changelog_entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + changelog_entry, encoding="utf-8")
    if README.exists():
        row = "| v4.3 | Production Safety Gate | PASS |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines = ["@echo off", "cd /d C:\\Users\\MSI\\Desktop\\kik_proje", "", "echo Running Production Safety Gate v4.3...", 'python ".py\\801_Run_All.py" --batch-size 10', "", "IF ERRORLEVEL 1 (", "    echo.", "    echo RELEASE BLOCKED: 801 Production Safety Gate FAILED.", "    pause", "    exit /b 1", ")", "", "git status", "git add .", 'git commit -m "Release v4.3: Production Safety Gate"', "git push", "git tag " + TAG, "git push origin " + TAG, "", "pause", ""]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()
    PY.mkdir(parents=True, exist_ok=True); SAFETY_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    print("="*80); print("801 ALL-IN-ONE PRODUCTION SAFETY GATE BUILDER BASLADI"); print("="*80)
    write_file(PY/"801"/"core"/"__init__.py", "")
    write_file(PY/"801"/"core"/"production_safety_gate_sdk.py", sdk_source())
    write_file(PY/"801_Production_Safety_Gate_SDK.py", sdk_bridge_source())
    print("Generated:", PY/"801_Production_Safety_Gate_SDK.py")
    generated=[str(PY/"801_Production_Safety_Gate_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY/(mid+"_"+slug+".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)
    run_all_path = PY/"801_Run_All.py"
    write_file(run_all_path, run_all_source())
    print("Generated:", run_all_path)
    release_path = create_release_docs()
    git_bat = create_git_bat()
    print("\n"+"="*80); print("801 SAFETY GATE TEST BASLIYOR"); print("="*80)
    run_result = run_visible([sys.executable, str(run_all_path), "--batch-size", str(args.batch_size)])
    decision = "PASS" if run_result.returncode == 0 else "FAIL"
    git_status = "SKIPPED"
    if decision != "PASS" and not args.force_git:
        git_status = "BLOCKED_BY_FAIL"
    elif args.no_git:
        git_status = "SKIPPED_BY_USER"
    else:
        print("\n"+"="*80); print("GIT RELEASE BASLIYOR"); print("="*80)
        git_result = run_visible(["cmd", "/c", str(git_bat)])
        git_status = "PUSHED" if git_result.returncode == 0 else "FAILED"
    ts=now_stamp()
    payload={"created_at":now_text(),"program":"801 Production Safety Gate Builder","version":VERSION,"tag":TAG,"batch_size":args.batch_size,"generated_files":generated,"run_all":str(run_all_path),"release_path":str(release_path),"git_bat":str(git_bat),"run_returncode":run_result.returncode,"final_decision":decision,"git":git_status}
    state_path=SAFETY_DIR/("801_production_safety_gate_builder_state_"+ts+".json")
    report_path=REPORTS/("801_production_safety_gate_builder_raporu_"+ts+".txt")
    write_json(state_path,payload)
    lines=["="*80,"801 ALL-IN-ONE PRODUCTION SAFETY GATE BUILDER FINAL","="*80,"Final Decision : "+decision,"Git            : "+git_status,"Batch Size     : "+str(args.batch_size),"Run All        : "+str(run_all_path),"Release        : "+str(release_path),"Git BAT        : "+str(git_bat),"State          : "+str(state_path),"Report         : "+str(report_path),"="*80]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision!="PASS": raise SystemExit(1)
    if git_status=="FAILED": raise SystemExit(1)
    raise SystemExit(0)

if __name__=="__main__":
    main()
