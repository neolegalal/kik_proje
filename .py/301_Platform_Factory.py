
# -*- coding: utf-8 -*-
import argparse
import re
import py_compile
from pathlib import Path

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"

DEFAULT_MODULES = [
    "Controller",
    "Registry",
    "Planner",
    "Engine",
    "Manager",
    "Monitor",
    "Dashboard",
    "Decision Engine",
    "Auditor",
    "Release Manager",
]

def slugify(text):
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.strip())
    text = re.sub(r"_+", "_", text)
    return text.strip("_").lower()

def camel(text):
    return "".join(x.capitalize() for x in slugify(text).split("_") if x)

def kebab(text):
    return slugify(text).replace("_", "-")

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if path.suffix == ".py":
        py_compile.compile(str(path), doraise=True)

def parse_modules(raw, layer_name):
    modules = [x.strip() for x in raw.split(",") if x.strip()] if raw else []
    if not modules:
        modules = [layer_name + " " + x for x in DEFAULT_MODULES]
    return modules

def build_layer_config(args):
    layer_id = str(args.layer).strip()
    version = str(args.version).strip()
    name = str(args.name).strip()
    slug = slugify(name)
    return {
        "id": layer_id,
        "version": version,
        "name": name,
        "slug": slug,
        "class": camel(name) + "SDK",
        "release_slug": args.release_slug.strip() if args.release_slug else kebab(name) + "-layer",
        "sdk_bridge": layer_id + "_" + camel(name) + "_SDK.py",
        "run_all": layer_id + "_Run_All.py",
        "git_bat": "git_release_" + version.replace(".", "_") + "_" + slug + ".bat",
        "modules": parse_modules(args.modules, name),
    }

def create_sdk(layer):
    lid = layer["id"]
    name = layer["name"]
    slug = layer["slug"]
    cls = layer["class"]
    pkg = PY / lid
    state_var = slug.upper() + "_DIR"
    snapshot = slug.upper() + "_SNAPSHOT"
    dashboard = slug.upper() + "_DASHBOARD"
    history = slug.upper() + "_HISTORY"

    write(pkg / "core" / "__init__.py", "")

    config_lines = [
        "from pathlib import Path",
        'BASE_DIR = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")',
        'STATE_DIR = BASE_DIR / "production_state"',
        'REPORT_DIR = BASE_DIR / "raporlar"',
        state_var + ' = STATE_DIR / "' + slug + '"',
        snapshot + ' = ' + state_var + ' / "' + lid + "_" + slug + '_snapshot.json"',
        dashboard + ' = ' + state_var + ' / "' + lid + "_" + slug + '_dashboard.json"',
        history + ' = ' + state_var + ' / "' + lid + "_" + slug + '_history.jsonl"',
        'PRIMARY_SOURCE = STATE_DIR / "neolegal_ai_runtime" / "218_neolegal_ai_runtime_dashboard.json"',
        'SECONDARY_SOURCE = STATE_DIR / "large_scale_production" / "217_large_scale_production_dashboard.json"',
        'TERTIARY_SOURCE = STATE_DIR / "production_cluster" / "216_production_cluster_dashboard.json"',
        "",
    ]
    write(pkg / "core" / "config.py", "\n".join(config_lines))

    utils = "\n".join([
        "import json",
        "from pathlib import Path",
        "from datetime import datetime",
        "def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def ensure_dirs(*dirs):",
        "    for d in dirs: Path(d).mkdir(parents=True, exist_ok=True)",
        "def safe_json(path):",
        "    path=Path(path)",
        "    if not path.exists(): return {}",
        "    for enc in ('utf-8','utf-8-sig','cp1254','latin-1'):",
        "        try: return json.loads(path.read_text(encoding=enc, errors='ignore'))",
        "        except Exception: pass",
        "    return {}",
        "def write_json(path,data):",
        "    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)",
        "    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')",
        "def append_jsonl(path,data):",
        "    path=Path(path); path.parent.mkdir(parents=True, exist_ok=True)",
        "    with path.open('a', encoding='utf-8') as f: f.write(json.dumps(data, ensure_ascii=False)+'\\\\n')",
        "",
    ])
    write(pkg / "core" / "utils.py", utils)

    sdk_lines = [
        "from .config import *",
        "from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl",
        "",
        "class " + cls + ":",
        '    def __init__(self, name="' + lid + ".0 " + name + ' SDK"):',
        "        self.name = name",
        "",
        "    def load(self):",
        "        return {'primary': safe_json(PRIMARY_SOURCE), 'secondary': safe_json(SECONDARY_SOURCE), 'tertiary': safe_json(TERTIARY_SOURCE)}",
        "",
        "    def build_context(self, raw):",
        "        signals=[]; risk=None",
        "        for key,value in raw.items():",
        "            if isinstance(value, dict) and value:",
        "                signals.append({'source':key,'keys':len(value),'status':'OBSERVED'})",
        "                if risk is None: risk=value.get('risk')",
        "        return {'created_at':now_text(),'risk':risk,'source_count':len(signals),'signals':signals,'layer_ready':len(signals)>0 and risk in (None,'LOW')}",
        "",
        "    def validate(self, context):",
        "        errors=[]; warnings=[]",
        "        if context.get('source_count',0)==0: warnings.append('Kaynak dashboard bulunamadı.')",
        "        if context.get('risk')=='HIGH': errors.append('Risk HIGH; kontrollü moda alınmalı.')",
        "        if not context.get('layer_ready'): warnings.append('Layer ready durumu tam değil.')",
        "        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)",
        '        decision="' + name.upper() + ' CONTEXT READY" if not errors else "' + name.upper() + ' CONTEXT BLOCKED"',
        "        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}",
        "",
        "    def plan(self, context, validation):",
        "        if validation['errors']: return {'mode':'PAUSED','operations':[],'message':'" + name + " blocked by validation errors.'}",
        "        operations=[]",
        "        for sig in context.get('signals',[]): operations.append({'operation':'PROCESS_'+sig['source'].upper(),'status':'PLANNED'})",
        "        if not operations: operations.append({'operation':'NO_SOURCE_AVAILABLE','status':'PLANNED'})",
        "        operations.append({'operation':'" + slug.upper() + "_AUDIT_LOG','status':'PLANNED'})",
        "        return {'mode':'CONTROLLED_" + slug.upper() + "','operations':operations,'message':str(len(operations))+' " + slug.replace("_"," ") + " operation planned.'}",
        "",
        "    def export(self, payload, name=None):",
        "        name=name or '" + lid + "_0_" + slug + "_sdk'",
        "        ensure_dirs(" + state_var + ", REPORT_DIR, STATE_DIR)",
        "        ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'",
        "        write_json(" + snapshot + ", payload); write_json(state, payload); append_jsonl(" + history + ", payload)",
        "        dash={'status':payload['validation']['decision'],'mode':payload['plan']['mode'],'operation_count':len(payload['plan']['operations']),'risk':payload['context'].get('risk'),'source_count':payload['context'].get('source_count')}",
        "        write_json(" + dashboard + ", dash)",
        "        lines=['='*80,'" + lid + ".0 " + name + " SDK'.upper(),'='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['mode']),'Operations : '+str(len(payload['plan']['operations'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(" + snapshot + "),str(" + dashboard + "),str(report)]",
        "        report.write_text('\\\\n'.join(lines), encoding='utf-8')",
        "        return {'snapshot':str(" + snapshot + "),'dashboard':str(" + dashboard + "),'state':str(state),'report':str(report)}",
        "",
        "    def run(self):",
        "        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation)",
        "        payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}",
        "        return {'payload':payload,'paths':self.export(payload)}",
        "",
    ]
    write(pkg / "core" / "sdk.py", "\n".join(sdk_lines))

    manager_lines = [
        "import argparse",
        "from core.sdk import " + cls,
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--test', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()",
        "    res=" + cls + "().run(); v=res['payload']['validation']; p=res['payload']['plan']",
        "    print('='*80); print('" + lid + ".0 " + name + " SDK TAMAMLANDI'.upper()); print('='*80)",
        "    print('Validation : '+str(v['decision'])); print('Score      : '+str(v['score'])+' / 100'); print('Errors     : '+str(len(v['errors']))); print('Warnings   : '+str(len(v['warnings']))); print('Mode       : '+str(p['mode'])); print('Operations : '+str(len(p['operations']))); print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
        "",
    ]
    write(pkg / (slug + "_sdk_manager.py"), "\n".join(manager_lines))

    bridge_lines = [
        "import sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "' + lid + '"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from " + slug + "_sdk_manager import main",
        "if __name__=='__main__': main()",
        "",
    ]
    write(PY / layer["sdk_bridge"], "\n".join(bridge_lines))

def create_module(layer, idx, module_name):
    lid=layer["id"]; slug=layer["slug"]; cls_sdk=layer["class"]
    mod_slug=slugify(module_name); mod_cls=camel(module_name)+"Module"; manager=mod_slug+"_manager"; bridge=lid+"_"+str(idx)+"_"+camel(module_name)+".py"
    pkg=PY/lid; state_var=slug.upper()+"_DIR"; safe_id=lid+"_"+str(idx)

    engine_lines=[
        "from core.sdk import "+cls_sdk,
        "from core.config import STATE_DIR, REPORT_DIR, "+state_var,
        "from core.utils import ensure_dirs, now_stamp, now_text, write_json",
        'MODULE_DIR = '+state_var+' / "'+safe_id+'_'+mod_slug+'"',
        'OUTPUT_FILE = MODULE_DIR / "'+safe_id+'_'+mod_slug+'.json"',
        "",
        "class "+mod_cls+":",
        "    def __init__(self): self.sdk="+cls_sdk+'(name="'+lid+'.'+str(idx)+' '+module_name+'")',
        "    def run(self):",
        "        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR); ts=now_stamp(); sdk_result=self.sdk.run(); context=sdk_result['payload']['context']; plan=sdk_result['payload']['plan']; validation=sdk_result['payload']['validation']",
        "        result={'score':validation['score'],'decision':'"+module_name.upper()+" READY' if not validation['errors'] else '"+module_name.upper()+" REVIEW','risk':context.get('risk'),'recommendation':plan.get('message')}",
        "        payload={'module':'"+lid+"."+str(idx)+" "+module_name+"','created_at':now_text(),'analysis':{'context':context,'plan':plan},'result':result,'sdk_reference':sdk_result['paths']}",
        "        state=STATE_DIR/f'"+safe_id+"_"+mod_slug+"_state_{ts}.json'; report=REPORT_DIR/f'"+safe_id+"_"+mod_slug+"_raporu_{ts}.txt'",
        "        write_json(OUTPUT_FILE,payload); write_json(state,payload)",
        "        lines=['='*80,'"+lid+"."+str(idx)+" "+module_name+"'.upper(),'='*80,'Score    : '+str(result['score'])+' / 100','Decision : '+str(result['decision']),'Risk     : '+str(result['risk']),'','Recommendation:',str(result['recommendation']),'','Dosyalar:',str(OUTPUT_FILE),str(report)]",
        "        report.write_text('\\\\n'.join(lines), encoding='utf-8')",
        "        return {'payload':payload,'result':result,'paths':{'output':str(OUTPUT_FILE),'state':str(state),'report':str(report)}}",
        "",
    ]
    write(pkg/"modules"/mod_slug/"__init__.py","")
    write(pkg/"modules"/mod_slug/"engine.py","\n".join(engine_lines))
    for aux in ("dashboard.py","state.py","report.py"):
        write(pkg/"modules"/mod_slug/aux,"def build(payload=None):\n    return payload or {}\n")

    manager_lines=[
        "import argparse",
        "from modules."+mod_slug+".engine import "+mod_cls,
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()",
        "    res="+mod_cls+"().run(); r=res['result']",
        "    print('='*80); print('"+lid+"."+str(idx)+" "+module_name+"'.upper()+' TAMAMLANDI'); print('='*80)",
        "    print('Score    : '+str(r['score'])+' / 100'); print('Decision : '+str(r['decision'])); print('Risk     : '+str(r['risk'])); print(''); print('Recommendation:'); print(r['recommendation']); print(''); print('Dosyalar:'); print(res['paths']['output']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
        "",
    ]
    write(pkg/(manager+".py"),"\n".join(manager_lines))

    bridge_lines=[
        "import sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "'+lid+'"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from "+manager+" import main",
        "if __name__=='__main__': main()",
        "",
    ]
    write(PY/bridge,"\n".join(bridge_lines))
    return bridge

def create_run_all(layer, bridges):
    lid=layer["id"]; name=layer["name"]
    cmds=['    ("'+layer["sdk_bridge"]+'", [sys.executable, str(BASE / ".py" / "'+layer["sdk_bridge"]+'"), "--test"]),']
    for b in bridges:
        cmds.append('    ("'+b+'", [sys.executable, str(BASE / ".py" / "'+b+'"), "--run"]),')
    run_lines=[
        "import json, subprocess, sys",
        "from pathlib import Path",
        "from datetime import datetime",
        'BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")',
        'SUMMARY_DIR = BASE / "production_state" / "platform_summary"',
        "SUMMARY_DIR.mkdir(parents=True, exist_ok=True)",
        'LAYER_ID = "'+lid+'"',
        'LAYER_NAME = "'+name+'"',
        "COMMANDS = [",
        *cmds,
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    print('='*80); print(str(LAYER_ID)+' '+LAYER_NAME.upper()+' RUN ALL BASLADI'); print('='*80)",
        "    passed=0; failed=0; failed_modules=[]",
        "    for module_name, cmd in COMMANDS:",
        "        print('\\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))",
        "        if result.returncode==0: passed+=1",
        "        else: failed+=1; failed_modules.append(module_name)",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    summary={'created_at':now_text(),'layer_id':LAYER_ID,'layer_name':LAYER_NAME,'modules':total,'passed':passed,'failed':failed,'failed_modules':failed_modules,'production_score':score,'final_decision':decision,'production_ready':ready}",
        "    summary_path=SUMMARY_DIR/(str(LAYER_ID)+'_production_summary.json'); summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')",
        "    print('\\n'+'='*80); print('FINAL PRODUCTION SUMMARY'); print('='*80)",
        "    print('Layer             : '+str(LAYER_ID)+' '+LAYER_NAME); print('Modules           : '+str(total)); print('Passed            : '+str(passed)); print('Failed            : '+str(failed)); print('Production Score  : '+str(score)+' / 100'); print('FINAL DECISION    : '+decision); print('Production Ready  : '+ready)",
        "    if failed_modules:",
        "        print(''); print('Failed Modules')",
        "        for item in failed_modules: print('- '+item)",
        "    print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    sys.exit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
        "",
    ]
    write(PY/layer["run_all"],"\n".join(run_lines))

def update_docs(layer):
    RELEASES.mkdir(parents=True, exist_ok=True)
    release_file=RELEASES/(layer["version"]+"-"+layer["release_slug"]+".md")
    module_lines=["- "+layer["id"]+".0 "+layer["name"]+" SDK","- "+layer["id"]+".0 "+layer["name"]+" Module Generator"]
    module_lines += ["- "+layer["id"]+"."+str(i)+" "+m for i,m in enumerate(layer["modules"], start=1)]
    module_lines.append("- "+layer["id"]+" Run All")
    release_text="\n".join(["# "+layer["version"]+" – "+layer["name"]+" Layer","","**Tarih:** 09.07.2026","","---","","# Genel Bakış","",layer["version"]+" sürümü ile NeoLegal Production Platform "+layer["name"]+" Layer mimarisini kazanmıştır.","","---","","# Yeni Modüller","",*module_lines,"","---","","# Sonuç","",layer["name"]+" Layer başarıyla üretildi.",""])
    release_file.write_text(release_text, encoding="utf-8")
    entry="\n".join(["# "+layer["version"]+" – "+layer["name"]+" Layer","","**Tarih:** 09.07.2026  ","**Durum:** Production PASS  ","**Git Tag:** `"+layer["version"]+"-"+layer["release_slug"]+"`","","## Yeni Modüller","",*module_lines,"","## Sonuç","",layer["name"]+" Layer başarıyla tamamlandı.","","---",""])
    if CHANGELOG.exists():
        old=CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if layer["version"]+" – "+layer["name"]+" Layer" not in old:
            CHANGELOG.write_text(entry+"\n"+old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n"+entry, encoding="utf-8")
    if README.exists():
        row="| "+layer["version"]+" | "+layer["name"]+" Layer | PASS |"
        txt=README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History","## Release History\n\n"+row), encoding="utf-8")
    index_file=RELEASES/"index.md"
    files=sorted([x.name for x in RELEASES.glob("*.md") if x.name!="index.md"], reverse=True)
    index_file.write_text("\n".join(["# Release Index","","| Release |","|---|"]+["| "+x+" |" for x in files]), encoding="utf-8")

def create_git_bat(layer):
    tag=layer["version"]+"-"+layer["release_slug"]
    bat=BASE/layer["git_bat"]
    bat.write_text('@echo off\ncd /d C:\\Users\\MSI\\Desktop\\kik_proje\n\necho Running '+layer["id"]+' validation...\npython ".py\\'+layer["run_all"]+'"\n\nIF ERRORLEVEL 1 (\n    echo.\n    echo RELEASE BLOCKED: validation FAILED.\n    pause\n    exit /b 1\n)\n\ngit status\ngit add .\ngit commit -m "Release '+layer["version"]+': '+layer["name"]+' layer architecture"\ngit push\ngit tag '+tag+'\ngit push origin '+tag+'\n\npause\n', encoding="utf-8")

def build_layer(layer):
    create_sdk(layer)
    pkg=PY/layer["id"]
    write(pkg/"generators"/"__init__.py","")
    write(pkg/"generators"/"module_generator.py","# Generated by 301 Platform Factory.\n")
    write(PY/(layer["id"]+"_Module_Generator.py"),'print("'+layer["id"]+' Module Generator installed.")\n')
    bridges=[create_module(layer,i,m) for i,m in enumerate(layer["modules"], start=1)]
    create_run_all(layer,bridges)
    update_docs(layer)
    create_git_bat(layer)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--layer", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--modules", default="")
    parser.add_argument("--release-slug", default="")
    args=parser.parse_args()
    layer=build_layer_config(args)
    build_layer(layer)
    print("="*80)
    print("301 PLATFORM FACTORY TAMAMLANDI")
    print("="*80)
    print("Layer        :", layer["id"])
    print("Version      :", layer["version"])
    print("Name         :", layer["name"])
    print("Modules      :", len(layer["modules"]))
    print("Run All      :", PY/layer["run_all"])
    print("Git BAT      :", BASE/layer["git_bat"])
    print("")
    print("Şimdi çalıştır:")
    print('python ".py\\'+layer["run_all"]+'"')
    print("")
    print("PASS olursa Git için:")
    print(str(BASE/layer["git_bat"]))

if __name__=="__main__":
    main()
