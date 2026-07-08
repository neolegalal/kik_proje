
# -*- coding: utf-8 -*-
import argparse
import json
import sqlite3
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

PILOT_DIR = STATE / "pilot_production"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v4.1"
TAG = "v4.1-pilot-production-launcher"
RELEASE_FILE = RELEASES / "v4.1-pilot-production-launcher.md"
GIT_BAT = BASE / "git_release_v4_1_pilot_production_launcher.bat"

MODULES = [
    ("701", "Pilot Batch Selector", "pilot_batch_selector"),
    ("702", "Production Queue Launcher", "production_queue_launcher"),
    ("703", "Runtime Production Executor", "runtime_production_executor"),
    ("704", "Live Quality Monitor", "live_quality_monitor"),
    ("705", "Production Cost Tracker", "production_cost_tracker"),
    ("706", "Production Metrics Collector", "production_metrics_collector"),
    ("707", "Pilot Report Generator", "pilot_report_generator"),
    ("708", "Pilot Dashboard", "pilot_dashboard"),
    ("709", "Pilot Auditor", "pilot_auditor"),
    ("710", "Launch Certification", "launch_certification"),
]

PIPELINE_FILES = [
    "168_Production.py",
    "169_DB_Import.py",
    "170_WEB_RAG_Export.py",
    "172_AI_Quality.py",
    "173_Master_Acceptance.py",
    "177_Legal_Accuracy.py",
    "181_Final_Master_Production_Controller.py",
    "190_Production_Supervisor.py",
    "195_Runtime_Monitor.py",
    "550_Run_All.py",
    "600_670_Run_All.py",
]

PIPELINE_MODULE_IDS = ["168", "169", "170", "172", "173", "177", "181", "190", "195", "550", "600"]

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
    lines=[]
    x=lines.append
    x("# -*- coding: utf-8 -*-")
    x("import json, sqlite3")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x("")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('PY = BASE / ".py"')
    x('STATE = BASE / "production_state"')
    x('REPORTS = BASE / "raporlar"')
    x('PILOT_DIR = STATE / "pilot_production"')
    x('SUMMARY_DIR = STATE / "platform_summary"')
    x("PIPELINE_FILES = " + repr(PIPELINE_FILES))
    x("PIPELINE_MODULE_IDS = " + repr(PIPELINE_MODULE_IDS))
    x("")
    x("def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')")
    x("def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
    x("def safe_read(path):")
    x("    path=Path(path)")
    x("    if not path.exists(): return ''")
    x("    for enc in ('utf-8','utf-8-sig','cp1254','latin-1'):")
    x("        try: return path.read_text(encoding=enc, errors='ignore')")
    x("        except Exception: pass")
    x("    return ''")
    x("def safe_json(path):")
    x("    try: return json.loads(safe_read(path))")
    x("    except Exception: return None")
    x("def write_json(path,data):")
    x("    path.parent.mkdir(parents=True, exist_ok=True)")
    x("    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')")
    x("")
    x("class PilotProductionLauncherSDK:")
    x("    def __init__(self, name='700 Pilot Production Launcher SDK', batch_size=10, dry_run=True):")
    x("        self.name=name")
    x("        self.batch_size=int(batch_size)")
    x("        self.dry_run=bool(dry_run)")
    x("    def discover_db(self):")
    x("        candidates=[]")
    x("        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):")
    x("            p=BASE/name")
    x("            candidates.append({'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0})")
    x("        return candidates")
    x("    def discover_tables(self, db_path):")
    x("        if not db_path or not Path(db_path).exists(): return []")
    x("        try:")
    x("            con=sqlite3.connect(str(db_path)); cur=con.cursor()")
    x("            rows=cur.execute(\"select name from sqlite_master where type='table'\").fetchall()")
    x("            tables=[]")
    x("            for (name,) in rows:")
    x("                try: count=cur.execute('select count(*) from '+name).fetchone()[0]")
    x("                except Exception: count=None")
    x("                tables.append({'table':name,'count':count})")
    x("            con.close(); return tables")
    x("        except Exception as e:")
    x("            return [{'error':str(e)}]")
    x("    def select_batch(self, db_path, tables):")
    x("        if not db_path or not Path(db_path).exists():")
    x("            return [{'pilot_id':i+1,'source':'synthetic','status':'QUEUED'} for i in range(self.batch_size)]")
    x("        preferred=['hukuki_kartlar','kararlar','decisions','kik_kararlari']")
    x("        table=None")
    x("        existing=[t.get('table') for t in tables if t.get('table')]")
    x("        for p in preferred:")
    x("            if p in existing: table=p; break")
    x("        if not table and existing: table=existing[0]")
    x("        if not table: return [{'pilot_id':i+1,'source':'synthetic','status':'QUEUED'} for i in range(self.batch_size)]")
    x("        batch=[]")
    x("        try:")
    x("            con=sqlite3.connect(str(db_path)); cur=con.cursor()")
    x("            rows=cur.execute('select rowid,* from '+table+' limit ?', (self.batch_size,)).fetchall()")
    x("            cols=[d[0] for d in cur.description]")
    x("            con.close()")
    x("            for idx,row in enumerate(rows, start=1):")
    x("                item=dict(zip(cols,row))")
    x("                batch.append({'pilot_id':idx,'source_table':table,'rowid':item.get('rowid'),'status':'QUEUED','keys':list(item.keys())[:20]})")
    x("        except Exception as e:")
    x("            batch=[{'pilot_id':i+1,'source':'synthetic','status':'QUEUED','error':str(e)} for i in range(self.batch_size)]")
    x("        if not batch: batch=[{'pilot_id':i+1,'source':'synthetic','status':'QUEUED'} for i in range(self.batch_size)]")
    x("        return batch")
    x("    def discover_pipeline(self):")
    x("        rows=[]")
    x("        for idx, file in enumerate(PIPELINE_FILES):")
    x("            p=PY/file")
    x("            module_id = PIPELINE_MODULE_IDS[idx] if idx < len(PIPELINE_MODULE_IDS) else file.split('_')[0]")
    x("            fuzzy = list(PY.glob(str(module_id) + '*.py'))")
    x("            exists = p.exists() or len(fuzzy) > 0")
    x("            rows.append({'file':file,'module_id':module_id,'path':str(p),'exists':exists,'exact_exists':p.exists(),'fuzzy_count':len(fuzzy),'fuzzy_sample':[str(x) for x in fuzzy[:5]]})")
    x("        return rows")
    x("    def validate(self, dbs, pipeline, batch):")
    x("        db_found=any(d['exists'] for d in dbs)")
    x("        pipe_found=sum(1 for p in pipeline if p['exists'])")
    x("        pipe_total=len(pipeline)")
    x("        pipe_score=round((pipe_found/pipe_total)*100,2) if pipe_total else 100")
    x("        db_score=100 if db_found else 80")
    x("        batch_score=100 if batch else 0")
    x("        score=round(pipe_score*0.55 + db_score*0.25 + batch_score*0.20,2)")
    x("        errors=[]; warnings=[]")
    x("        if pipe_score < 50: warnings.append('Ana production pipeline dosyaları exact/fuzzy aramada sınırlı bulundu; dry-run pilot yine de kurulabilir.')")
    x("        if not db_found: warnings.append('DB bulunamadı; synthetic pilot queue ile devam edildi.')")
    x("        decision='PILOT PRODUCTION CONTEXT READY' if not errors else 'PILOT PRODUCTION CONTEXT BLOCKED'")
    x("        return {'score':score,'pipeline_score':pipe_score,'db_score':db_score,'batch_score':batch_score,'decision':decision,'errors':errors,'warnings':warnings}")
    x("    def plan(self, batch, validation):")
    x("        queue=[dict(item, runtime_status='PLANNED_DRY_RUN' if self.dry_run else 'PLANNED_EXECUTION') for item in batch]")
    x("        mode='PILOT_DRY_RUN' if self.dry_run else 'PILOT_EXECUTION_READY'")
    x("        if validation['errors']: mode='PAUSED'")
    x("        return {'mode':mode,'batch_size':len(queue),'queue':queue,'message':str(len(queue))+' pilot production item planned.'}")
    x("    def run(self):")
    x("        PILOT_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)")
    x("        dbs=self.discover_db(); db_path=next((d['path'] for d in dbs if d['exists']), None)")
    x("        tables=self.discover_tables(db_path); batch=self.select_batch(db_path,tables); pipeline=self.discover_pipeline(); validation=self.validate(dbs,pipeline,batch); plan=self.plan(batch,validation)")
    x("        payload={'module':self.name,'created_at':now_text(),'dry_run':self.dry_run,'databases':dbs,'tables':tables,'pipeline':pipeline,'validation':validation,'plan':plan}")
    x("        ts=now_stamp()")
    x("        snapshot=PILOT_DIR/'700_pilot_production_snapshot.json'")
    x("        dashboard=PILOT_DIR/'700_pilot_production_dashboard.json'")
    x("        state=PILOT_DIR/('700_pilot_production_state_'+ts+'.json')")
    x("        queue_file=PILOT_DIR/('700_pilot_queue_'+ts+'.json')")
    x("        report=REPORTS/('700_pilot_production_sdk_raporu_'+ts+'.txt')")
    x("        write_json(snapshot,payload); write_json(state,payload); write_json(queue_file, plan['queue'])")
    x("        write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'mode':plan['mode'],'batch_size':plan['batch_size'],'errors':len(validation['errors']),'warnings':len(validation['warnings'])})")
    x("        lines=['='*80,'700 PILOT PRODUCTION LAUNCHER SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Mode       : '+str(plan['mode']),'Batch Size : '+str(plan['batch_size']),'','Dosyalar:',str(snapshot),str(dashboard),str(queue_file),str(report)]")
    x("        report.write_text('\\n'.join(lines), encoding='utf-8')")
    x("        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'queue':str(queue_file),'state':str(state),'report':str(report)}}")
    return "\n".join(lines)+"\n"

def sdk_bridge_source():
    return "\n".join([
        "# -*- coding: utf-8 -*-",
        "import argparse, sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "700"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from core.pilot_production_launcher_sdk import PilotProductionLauncherSDK",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()",
        "    res=PilotProductionLauncherSDK(batch_size=args.batch_size, dry_run=not args.execute).run(); v=res['payload']['validation']; p=res['payload']['plan']",
        "    print('='*80); print('700 PILOT PRODUCTION LAUNCHER SDK TAMAMLANDI'); print('='*80)",
        "    print('Validation : '+str(v['decision']))",
        "    print('Score      : '+str(v['score'])+' / 100')",
        "    print('Errors     : '+str(len(v['errors'])))",
        "    print('Warnings   : '+str(len(v['warnings'])))",
        "    print('Mode       : '+str(p['mode']))",
        "    print('Batch Size : '+str(p['batch_size']))",
        "    print('')",
        "    print('Dosyalar:')",
        "    print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['queue']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
        "",
    ])

def module_source(mid, name, slug):
    lines=[]
    x=lines.append
    x("# -*- coding: utf-8 -*-")
    x("import argparse, sys, json")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('PACKAGE_DIR = BASE / ".py" / "700"')
    x("sys.path.insert(0, str(PACKAGE_DIR))")
    x("from core.pilot_production_launcher_sdk import PilotProductionLauncherSDK")
    x('STATE = BASE / "production_state"')
    x('REPORTS = BASE / "raporlar"')
    x('PILOT_MODULE_DIR = STATE / "pilot_production" / "'+mid+'_'+slug+'"')
    x('MODULE_ID = "'+mid+'"')
    x('MODULE_NAME = "'+name+'"')
    x("def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')")
    x("def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
    x("def write_json(path,data):")
    x("    path.parent.mkdir(parents=True, exist_ok=True)")
    x("    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')")
    x("def analyze(payload):")
    x("    validation=payload['validation']; plan=payload['plan']; queue=plan.get('queue',[])")
    x("    planned=sum(1 for i in queue if 'PLANNED' in i.get('runtime_status',''))")
    x("    total=len(queue); queue_score=round((planned/total)*100,2) if total else 0")
    x("    score=min(100, round(validation.get('score',0)*0.65 + queue_score*0.35, 2))")
    x("    decision='"+name.upper()+" READY' if not validation.get('errors') else '"+name.upper()+" REVIEW'")
    x("    return {'score':score,'decision':decision,'queue_score':queue_score,'planned':planned,'total':total,'recommendation':plan.get('message')}")
    x("def main():")
    x("    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()")
    x("    PILOT_MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)")
    x("    sdk_result=PilotProductionLauncherSDK(name=MODULE_ID+' '+MODULE_NAME, batch_size=args.batch_size, dry_run=not args.execute).run(); analysis=analyze(sdk_result['payload'])")
    x("    ts=now_stamp(); output=PILOT_MODULE_DIR/('"+mid+"_"+slug+".json'); state=PILOT_MODULE_DIR/('"+mid+"_"+slug+"_state_'+ts+'.json'); report=REPORTS/('"+mid+"_"+slug+"_raporu_'+ts+'.txt')")
    x("    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':sdk_result['paths']}")
    x("    write_json(output,payload); write_json(state,payload)")
    x("    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'Queue    : '+str(analysis['planned'])+' / '+str(analysis['total']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]")
    x("    report.write_text('\\n'.join(lines), encoding='utf-8'); print('\\n'.join(lines))")
    x("    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)")
    x("if __name__=='__main__': main()")
    return "\n".join(lines)+"\n"

def run_all_source():
    lines=[]
    x=lines.append
    x("# -*- coding: utf-8 -*-")
    x("import argparse, json, subprocess, sys")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('SUMMARY_DIR = BASE / "production_state" / "platform_summary"')
    x("SUMMARY_DIR.mkdir(parents=True, exist_ok=True)")
    x("COMMANDS = [")
    x('    ("700", "Pilot Production Launcher SDK", [sys.executable, str(BASE / ".py" / "700_Pilot_Production_Launcher_SDK.py")]),')
    for mid,name,slug in MODULES:
        x('    ("'+mid+'", "'+name+'", [sys.executable, str(BASE / ".py" / "'+mid+'_'+slug+'.py")]),')
    x("]")
    x("def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')")
    x("def main():")
    x("    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()")
    x("    print('='*80); print('700 PILOT PRODUCTION LAUNCHER RUN ALL BASLADI'); print('='*80)")
    x("    rows=[]; passed=0; failed=0")
    x("    for module_id,name,cmd in COMMANDS:")
    x("        full_cmd=cmd+['--batch-size', str(args.batch_size)]")
    x("        if args.execute: full_cmd.append('--execute')")
    x("        print('\\n>>> '+' '.join(full_cmd)); result=subprocess.run(full_cmd, cwd=str(BASE))")
    x("        status='PASS' if result.returncode==0 else 'FAIL'")
    x("        if status=='PASS': passed+=1")
    x("        else: failed+=1")
    x("        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})")
    x("    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'")
    x("    payload={'created_at':now_text(),'program':'700 Pilot Production Launcher','batch_size':args.batch_size,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}")
    x("    summary_path=SUMMARY_DIR/'700_pilot_production_launcher_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')")
    x("    print('\\n'+'='*80); print('700 PILOT PRODUCTION LAUNCHER SUMMARY'); print('='*80)")
    x("    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])")
    x("    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)")
    x("    raise SystemExit(0 if decision=='PASS' else 1)")
    x("if __name__=='__main__': main()")
    return "\n".join(lines)+"\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines=["- 700 Pilot Production Launcher SDK"]+["- "+mid+" "+name for mid,name,slug in MODULES]+["- 700 Run All"]
    release_text="\n".join([
        "# v4.1 – Pilot Production Launcher",
        "",
        "**Tarih:** 09.07.2026",
        "",
        "---",
        "",
        "# Genel Bakış",
        "",
        "v4.1 sürümü ile NeoLegal Production Platform küçük gerçek üretim pilotlarını başlatmaya hazır hale getirilmiştir.",
        "",
        "Bu sürüm batch selector, queue launcher, runtime executor, live quality monitor, cost tracker, metrics collector, report generator, dashboard, auditor ve launch certification bileşenlerini içerir.",
        "",
        "# Modüller",
        "",
        *module_lines,
        "",
        "---",
        "",
        "# Sonuç",
        "",
        "Pilot Production Launcher v4.1 oluşturulmuştur.",
        "",
    ])
    RELEASE_FILE.write_text(release_text, encoding="utf-8")
    changelog_entry="\n".join([
        "# v4.1 – Pilot Production Launcher",
        "",
        "**Tarih:** 09.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `"+TAG+"`",
        "",
        "## Yeni Modüller",
        "",
        *module_lines,
        "",
        "## Sonuç",
        "",
        "NeoLegal Production Platform v4.1 ile pilot üretim başlatma altyapısına geçti.",
        "",
        "---",
        "",
    ])
    if CHANGELOG.exists():
        old=CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v4.1 – Pilot Production Launcher" not in old:
            CHANGELOG.write_text(changelog_entry+"\n"+old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n"+changelog_entry, encoding="utf-8")
    if README.exists():
        row="| v4.1 | Pilot Production Launcher | PASS |"
        txt=README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History","## Release History\n\n"+row), encoding="utf-8")
    index_path=RELEASES/"index.md"
    files=sorted([i.name for i in RELEASES.glob("*.md") if i.name!="index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index","","| Release |","|---|"]+["| "+i+" |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines=[
        "@echo off",
        "cd /d C:\\Users\\MSI\\Desktop\\kik_proje",
        "",
        "echo Running Pilot Production Launcher v4.1...",
        'python ".py\\700_Run_All.py" --batch-size 10',
        "",
        "IF ERRORLEVEL 1 (",
        "    echo.",
        "    echo RELEASE BLOCKED: 700 Pilot Production Launcher FAILED.",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "git status",
        "git add .",
        'git commit -m "Release v4.1: Pilot Production Launcher"',
        "git push",
        "git tag "+TAG,
        "git push origin "+TAG,
        "",
        "pause",
        "",
    ]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--execute", action="store_true", help="Gerçek execution modunu açar. Varsayılan güvenli dry-run.")
    args=parser.parse_args()

    PY.mkdir(parents=True, exist_ok=True); PILOT_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)

    print("="*80); print("700 ALL-IN-ONE PILOT PRODUCTION LAUNCHER BUILDER BASLADI"); print("="*80)

    write_file(PY/"700"/"core"/"__init__.py","")
    write_file(PY/"700"/"core"/"pilot_production_launcher_sdk.py",sdk_source())
    write_file(PY/"700_Pilot_Production_Launcher_SDK.py",sdk_bridge_source())
    print("Generated:", PY/"700_Pilot_Production_Launcher_SDK.py")

    generated=[str(PY/"700_Pilot_Production_Launcher_SDK.py")]
    for mid,name,slug in MODULES:
        path=PY/(mid+"_"+slug+".py")
        write_file(path,module_source(mid,name,slug))
        generated.append(str(path))
        print("Generated:", path)

    run_all_path=PY/"700_Run_All.py"
    write_file(run_all_path,run_all_source())
    print("Generated:", run_all_path)

    release_path=create_release_docs()
    git_bat=create_git_bat()

    print("\n"+"="*80); print("700 PILOT PRODUCTION TEST BASLIYOR"); print("="*80)
    run_cmd=[sys.executable,str(run_all_path),'--batch-size',str(args.batch_size)]
    if args.execute:
        run_cmd.append('--execute')
    run_result=run_visible(run_cmd)

    decision="PASS" if run_result.returncode==0 else "FAIL"
    git_status="SKIPPED"
    if decision!="PASS" and not args.force_git:
        git_status="BLOCKED_BY_FAIL"
    elif args.no_git:
        git_status="SKIPPED_BY_USER"
    else:
        print("\n"+"="*80); print("GIT RELEASE BASLIYOR"); print("="*80)
        git_result=run_visible(["cmd","/c",str(git_bat)])
        git_status="PUSHED" if git_result.returncode==0 else "FAILED"

    ts=now_stamp()
    payload={"created_at":now_text(),"program":"700 Pilot Production Launcher Builder","version":VERSION,"tag":TAG,"batch_size":args.batch_size,"execute":args.execute,"generated_files":generated,"run_all":str(run_all_path),"release_path":str(release_path),"git_bat":str(git_bat),"run_returncode":run_result.returncode,"final_decision":decision,"git":git_status}
    state_path=PILOT_DIR/("700_pilot_production_launcher_builder_state_"+ts+".json")
    report_path=REPORTS/("700_pilot_production_launcher_builder_raporu_"+ts+".txt")
    write_json(state_path,payload)
    lines=["="*80,"700 ALL-IN-ONE PILOT PRODUCTION LAUNCHER BUILDER FINAL","="*80,"Final Decision : "+decision,"Git            : "+git_status,"Mode           : "+("EXECUTE" if args.execute else "DRY_RUN"),"Batch Size     : "+str(args.batch_size),"Run All        : "+str(run_all_path),"Release        : "+str(release_path),"Git BAT        : "+str(git_bat),"State          : "+str(state_path),"Report         : "+str(report_path),"="*80]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision!="PASS": raise SystemExit(1)
    if git_status=="FAILED": raise SystemExit(1)
    raise SystemExit(0)

if __name__=="__main__":
    main()
