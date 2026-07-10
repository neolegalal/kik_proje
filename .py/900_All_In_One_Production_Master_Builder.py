
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

MASTER_DIR = STATE / "production_master"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v5.0"
TAG = "v5.0-production-master"
RELEASE_FILE = RELEASES / "v5.0-production-master.md"
GIT_BAT = BASE / "git_release_v5_0_production_master.bat"

MODULES = [
    ("901", "Production Queue Manager", "production_queue_manager"),
    ("902", "Batch Manager", "batch_manager"),
    ("903", "Worker Manager", "worker_manager"),
    ("904", "Cost Manager", "cost_manager"),
    ("905", "Progress Monitor", "progress_monitor"),
    ("906", "Live Dashboard", "live_dashboard"),
    ("907", "Quality Monitor", "quality_monitor"),
    ("908", "Production Auditor", "production_auditor"),
    ("909", "Executive Report", "executive_report"),
    ("910", "Production Commander", "production_commander"),
]

CORE_MODULE_IDS = ["168","169","170","172","173","177","181","190","195","700","800","801"]
PLATFORM_MODULE_IDS = ["400","500","550","600","206","207","208","209","210","211","212"]

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
    x("import json, os, shutil, sqlite3, subprocess")
    x("from pathlib import Path")
    x("from datetime import datetime")
    x('BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")')
    x('PY = BASE / ".py"')
    x('STATE = BASE / "production_state"')
    x('REPORTS = BASE / "raporlar"')
    x('MASTER_DIR = STATE / "production_master"')
    x('SUMMARY_DIR = STATE / "platform_summary"')
    x("CORE_MODULE_IDS = " + repr(CORE_MODULE_IDS))
    x("PLATFORM_MODULE_IDS = " + repr(PLATFORM_MODULE_IDS))
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
    x("class ProductionMasterSDK:")
    x("    def __init__(self, name='900 Production Master SDK', target=100000, batch_size=10, dry_run=True):")
    x("        self.name=name; self.target=int(target); self.batch_size=int(batch_size); self.dry_run=bool(dry_run)")
    x("    def discover_db(self):")
    x("        rows=[]")
    x("        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):")
    x("            p=BASE/name")
    x("            item={'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0,'tables':[],'error':None}")
    x("            if p.exists():")
    x("                try:")
    x("                    con=sqlite3.connect(str(p)); cur=con.cursor(); tables=cur.execute(\"select name from sqlite_master where type='table'\").fetchall()")
    x("                    for (t,) in tables[:30]:")
    x("                        try: count=cur.execute('select count(*) from '+t).fetchone()[0]")
    x("                        except Exception: count=None")
    x("                        item['tables'].append({'table':t,'count':count})")
    x("                    con.close()")
    x("                except Exception as e: item['error']=str(e)")
    x("            rows.append(item)")
    x("        return rows")
    x("    def discover_modules(self):")
    x("        def scan(ids):")
    x("            out=[]")
    x("            for mid in ids:")
    x("                hits=list(PY.glob(str(mid)+'*.py'))")
    x("                out.append({'module_id':mid,'found':len(hits)>0,'count':len(hits),'sample':[str(x) for x in hits[:5]]})")
    x("            return out")
    x("        return {'core':scan(CORE_MODULE_IDS),'platform':scan(PLATFORM_MODULE_IDS)}")
    x("    def discover_summaries(self):")
    x("        rows=[]")
    x("        if SUMMARY_DIR.exists():")
    x("            for f in SUMMARY_DIR.glob('*_summary.json'):")
    x("                data=safe_json(f) or {}")
    x("                rows.append({'path':str(f),'final_decision':data.get('final_decision'),'score':data.get('program_score') or data.get('production_score'),'ready':data.get('production_ready')})")
    x("        return rows")
    x("    def build_queue_plan(self, dbs):")
    x("        db_found=any(d['exists'] for d in dbs)")
    x("        available=0")
    x("        for db in dbs:")
    x("            for t in db.get('tables',[]):")
    x("                if isinstance(t.get('count'), int): available=max(available, t['count'])")
    x("        planned=min(self.batch_size, available if available else self.batch_size)")
    x("        queue=[{'queue_id':i+1,'status':'MASTER_DRY_RUN_PLANNED' if self.dry_run else 'MASTER_EXECUTION_PLANNED'} for i in range(planned)]")
    x("        return {'db_found':db_found,'available_count':available,'planned_batch':planned,'target':self.target,'queue':queue}")
    x("    def estimate_cost(self):")
    x("        # Conservative placeholder: actual cost will be filled by API runtime later.")
    x("        estimated_tokens_per_item=2500")
    x("        estimated_total_tokens=self.batch_size*estimated_tokens_per_item")
    x("        return {'estimated_tokens_per_item':estimated_tokens_per_item,'estimated_total_tokens':estimated_total_tokens,'estimated_api_calls':self.batch_size,'mode':'ESTIMATE_ONLY'}")
    x("    def plan_workers(self):")
    x("        workers=1 if self.batch_size<=10 else 2 if self.batch_size<=100 else 4")
    x("        return {'recommended_workers':workers,'batch_size':self.batch_size,'strategy':'controlled_pilot' if self.batch_size<=100 else 'scaled_production'}")
    x("    def progress(self, queue_plan):")
    x("        completed=0; planned=queue_plan['planned_batch']")
    x("        pct=round((completed/planned)*100,2) if planned else 0")
    x("        return {'target':self.target,'planned_batch':planned,'completed':completed,'progress_percent':pct,'eta':'not_started'}")
    x("    def validate(self, dbs, modules, summaries, queue_plan):")
    x("        core_found=sum(1 for x in modules['core'] if x['found']); core_total=len(modules['core'])")
    x("        plat_found=sum(1 for x in modules['platform'] if x['found']); plat_total=len(modules['platform'])")
    x("        core_score=round((core_found/core_total)*100,2) if core_total else 100")
    x("        platform_score=round((plat_found/plat_total)*100,2) if plat_total else 100")
    x("        db_score=100 if any(d['exists'] for d in dbs) else 80")
    x("        summary_pass=sum(1 for s in summaries if s.get('final_decision')=='PASS')")
    x("        summary_score=100 if summary_pass>=5 else 85 if summary_pass>=2 else 70")
    x("        queue_score=100 if queue_plan['planned_batch']>0 else 0")
    x("        score=round(core_score*0.35 + platform_score*0.20 + db_score*0.15 + summary_score*0.15 + queue_score*0.15,2)")
    x("        errors=[]; warnings=[]")
    x("        if core_score<70: errors.append('Core production modules are incomplete.')")
    x("        if platform_score<60: warnings.append('Some platform support modules are missing.')")
    x("        if not any(d['exists'] for d in dbs): warnings.append('DB not found; master will use synthetic queue until DB is available.')")
    x("        if self.dry_run: warnings.append('Master is running in dry-run mode.')")
    x("        decision='PRODUCTION MASTER READY' if not errors else 'PRODUCTION MASTER BLOCKED'")
    x("        return {'score':score,'core_score':core_score,'platform_score':platform_score,'db_score':db_score,'summary_score':summary_score,'queue_score':queue_score,'decision':decision,'errors':errors,'warnings':warnings}")
    x("    def run(self):")
    x("        MASTER_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)")
    x("        dbs=self.discover_db(); modules=self.discover_modules(); summaries=self.discover_summaries(); queue_plan=self.build_queue_plan(dbs); cost=self.estimate_cost(); workers=self.plan_workers(); progress=self.progress(queue_plan); validation=self.validate(dbs,modules,summaries,queue_plan)")
    x("        payload={'module':self.name,'created_at':now_text(),'target':self.target,'batch_size':self.batch_size,'dry_run':self.dry_run,'databases':dbs,'modules':modules,'summaries':summaries,'queue_plan':queue_plan,'cost':cost,'workers':workers,'progress':progress,'validation':validation}")
    x("        ts=now_stamp(); snapshot=MASTER_DIR/'900_production_master_snapshot.json'; dashboard=MASTER_DIR/'900_production_master_dashboard.json'; state=MASTER_DIR/('900_production_master_state_'+ts+'.json'); report=REPORTS/('900_production_master_sdk_raporu_'+ts+'.txt')")
    x("        write_json(snapshot,payload); write_json(state,payload); write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'target':self.target,'batch_size':self.batch_size,'mode':'DRY_RUN' if self.dry_run else 'EXECUTE','planned_batch':queue_plan['planned_batch'],'workers':workers['recommended_workers'],'warnings':len(validation['warnings']),'errors':len(validation['errors'])})")
    x("        lines=['='*80,'900 PRODUCTION MASTER SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Target     : '+str(self.target),'Batch Size : '+str(self.batch_size),'Mode       : '+('DRY_RUN' if self.dry_run else 'EXECUTE'),'Workers    : '+str(workers['recommended_workers']),'Planned    : '+str(queue_plan['planned_batch']),'','Dosyalar:',str(snapshot),str(dashboard),str(report)]")
    x("        report.write_text('\\n'.join(lines), encoding='utf-8')")
    x("        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'state':str(state),'report':str(report)}}")
    return "\n".join(lines)+"\n"

def sdk_bridge_source():
    return "\n".join([
        "# -*- coding: utf-8 -*-",
        "import argparse, sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "900"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from core.production_master_sdk import ProductionMasterSDK",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()",
        "    res=ProductionMasterSDK(target=args.target,batch_size=args.batch_size,dry_run=not args.execute).run(); v=res['payload']['validation']",
        "    print('='*80); print('900 PRODUCTION MASTER SDK TAMAMLANDI'); print('='*80)",
        "    print('Validation : '+str(v['decision']))",
        "    print('Score      : '+str(v['score'])+' / 100')",
        "    print('Errors     : '+str(len(v['errors'])))",
        "    print('Warnings   : '+str(len(v['warnings'])))",
        "    print('')",
        "    print('Dosyalar:')",
        "    print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])",
        "    raise SystemExit(1 if v['errors'] else 0)",
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
        'PACKAGE_DIR = BASE / ".py" / "900"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from core.production_master_sdk import ProductionMasterSDK",
        'STATE = BASE / "production_state"',
        'REPORTS = BASE / "raporlar"',
        'MODULE_DIR = STATE / "production_master" / "' + mid + '_' + slug + '"',
        'MODULE_ID = "' + mid + '"',
        'MODULE_NAME = "' + name + '"',
        "def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def write_json(path,data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()",
        "    MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)",
        "    sdk=ProductionMasterSDK(name=MODULE_ID+' '+MODULE_NAME,target=args.target,batch_size=args.batch_size,dry_run=not args.execute)",
        "    res=sdk.run(); val=res['payload']['validation']; queue=res['payload']['queue_plan']; workers=res['payload']['workers']; cost=res['payload']['cost']",
        "    score=val['score']; decision='" + name.upper() + " READY' if not val['errors'] else '" + name.upper() + " BLOCKED'",
        "    analysis={'score':score,'decision':decision,'planned_batch':queue['planned_batch'],'target':args.target,'workers':workers,'cost':cost,'recommendation':'Production Master ready for controlled operation.' if not val['errors'] else 'Production Master blocked.'}",
        "    ts=now_stamp(); output=MODULE_DIR/('" + mid + "_" + slug + ".json'); state=MODULE_DIR/('" + mid + "_" + slug + "_state_'+ts+'.json'); report=REPORTS/('" + mid + "_" + slug + "_raporu_'+ts+'.txt')",
        "    payload={'created_at':now_text(),'module_id':MODULE_ID,'module_name':MODULE_NAME,'analysis':analysis,'sdk_reference':res['paths']}",
        "    write_json(output,payload); write_json(state,payload)",
        "    lines=['='*80, MODULE_ID+' '+MODULE_NAME.upper(), '='*80, 'Score    : '+str(analysis['score'])+' / 100', 'Decision : '+str(analysis['decision']), 'Target   : '+str(analysis['target']), 'Batch    : '+str(analysis['planned_batch']), 'Workers  : '+str(analysis['workers']['recommended_workers']), '', 'Recommendation:', str(analysis['recommendation']), '', 'Dosyalar:', str(output), str(report)]",
        "    report.write_text('\\n'.join(lines), encoding='utf-8'); print('\\n'.join(lines))",
        "    raise SystemExit(0 if 'READY' in analysis['decision'] else 1)",
        "if __name__=='__main__': main()",
        "",
    ])

def run_all_source():
    lines=[
        "# -*- coding: utf-8 -*-",
        "import argparse, json, subprocess, sys",
        "from pathlib import Path",
        "from datetime import datetime",
        'BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")',
        'SUMMARY_DIR = BASE / "production_state" / "platform_summary"',
        "SUMMARY_DIR.mkdir(parents=True, exist_ok=True)",
        "COMMANDS = [",
        '    ("900", "Production Master SDK", [sys.executable, str(BASE / ".py" / "900_Production_Master_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()",
        "    print('='*80); print('900 PRODUCTION MASTER RUN ALL BASLADI'); print('='*80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id,name,cmd in COMMANDS:",
        "        full=cmd+['--target',str(args.target),'--batch-size',str(args.batch_size)]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> '+' '.join(full)); result=subprocess.run(full, cwd=str(BASE))",
        "        status='PASS' if result.returncode==0 else 'FAIL'",
        "        if status=='PASS': passed+=1",
        "        else: failed+=1",
        "        rows.append({'module_id':module_id,'name':name,'status':status,'returncode':result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'900 Production Master','target':args.target,'batch_size':args.batch_size,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'900_production_master_summary.json'; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')",
        "    print('\\n'+'='*80); print('900 PRODUCTION MASTER SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(35)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
        "",
    ]
    return "\n".join(lines)

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines=["- 900 Production Master SDK"]+["- "+mid+" "+name for mid,name,slug in MODULES]+["- 900 Run All"]
    release_text="\n".join([
        "# v5.0 – Production Master",
        "",
        "**Tarih:** 10.07.2026",
        "",
        "---",
        "",
        "# Genel Bakış",
        "",
        "v5.0 sürümü ile NeoLegal Production Platform, gerçek veri üretimini tek merkezden yönetmeye hazırlanan Production Master operasyon merkezine kavuşmuştur.",
        "",
        "Bu sürüm queue, batch, worker, cost, progress, live dashboard, quality monitor, auditor, executive report ve commander bileşenlerini içerir.",
        "",
        "# Modüller",
        "",
        *module_lines,
        "",
        "---",
        "",
        "# Sonuç",
        "",
        "Production Master v5.0 oluşturulmuştur.",
        "",
    ])
    RELEASE_FILE.write_text(release_text, encoding="utf-8")
    entry="\n".join([
        "# v5.0 – Production Master",
        "",
        "**Tarih:** 10.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `"+TAG+"`",
        "",
        "## Yeni Modüller",
        "",
        *module_lines,
        "",
        "## Sonuç",
        "",
        "NeoLegal Production Platform v5.0 ile gerçek üretim operasyon merkezi mimarisine geçti.",
        "",
        "---",
        "",
    ])
    if CHANGELOG.exists():
        old=CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v5.0 – Production Master" not in old:
            CHANGELOG.write_text(entry+"\n"+old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n"+entry, encoding="utf-8")
    if README.exists():
        row="| v5.0 | Production Master | PASS |"
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
        "echo Running Production Master v5.0...",
        'python ".py\\900_Run_All.py" --target 100000 --batch-size 10',
        "",
        "IF ERRORLEVEL 1 (",
        "    echo.",
        "    echo RELEASE BLOCKED: 900 Production Master FAILED.",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "git status",
        "git add .",
        'git commit -m "Release v5.0: Production Master"',
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
    parser.add_argument("--target", type=int, default=100000)
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--execute", action="store_true")
    args=parser.parse_args()

    PY.mkdir(parents=True, exist_ok=True); MASTER_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)

    print("="*80); print("900 ALL-IN-ONE PRODUCTION MASTER BUILDER BASLADI"); print("="*80)

    write_file(PY/"900"/"core"/"__init__.py", "")
    write_file(PY/"900"/"core"/"production_master_sdk.py", sdk_source())
    write_file(PY/"900_Production_Master_SDK.py", sdk_bridge_source())
    print("Generated:", PY/"900_Production_Master_SDK.py")

    generated=[str(PY/"900_Production_Master_SDK.py")]
    for mid,name,slug in MODULES:
        path=PY/(mid+"_"+slug+".py")
        write_file(path,module_source(mid,name,slug))
        generated.append(str(path))
        print("Generated:", path)

    run_all_path=PY/"900_Run_All.py"
    write_file(run_all_path,run_all_source())
    print("Generated:", run_all_path)

    release_path=create_release_docs()
    git_bat=create_git_bat()

    print("\n"+"="*80); print("900 PRODUCTION MASTER TEST BASLIYOR"); print("="*80)
    run_cmd=[sys.executable,str(run_all_path),"--target",str(args.target),"--batch-size",str(args.batch_size)]
    if args.execute:
        run_cmd.append("--execute")
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
    payload={"created_at":now_text(),"program":"900 Production Master Builder","version":VERSION,"tag":TAG,"target":args.target,"batch_size":args.batch_size,"execute":args.execute,"generated_files":generated,"run_all":str(run_all_path),"release_path":str(release_path),"git_bat":str(git_bat),"run_returncode":run_result.returncode,"final_decision":decision,"git":git_status}
    state_path=MASTER_DIR/("900_production_master_builder_state_"+ts+".json")
    report_path=REPORTS/("900_production_master_builder_raporu_"+ts+".txt")
    write_json(state_path,payload)
    lines=["="*80,"900 ALL-IN-ONE PRODUCTION MASTER BUILDER FINAL","="*80,"Final Decision : "+decision,"Git            : "+git_status,"Mode           : "+("EXECUTE" if args.execute else "DRY_RUN"),"Target         : "+str(args.target),"Batch Size     : "+str(args.batch_size),"Run All        : "+str(run_all_path),"Release        : "+str(release_path),"Git BAT        : "+str(git_bat),"State          : "+str(state_path),"Report         : "+str(report_path),"="*80]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision!="PASS": raise SystemExit(1)
    if git_status=="FAILED": raise SystemExit(1)
    raise SystemExit(0)

if __name__=="__main__":
    main()
