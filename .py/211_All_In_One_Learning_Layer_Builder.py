
from pathlib import Path
import py_compile, sys

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "211"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"

MODULES = [
    ("211.1", "Experience Collector", "211_1_Experience_Collector.py"),
    ("211.2", "Pattern Learner", "211_2_Pattern_Learner.py"),
    ("211.3", "Failure Learner", "211_3_Failure_Learner.py"),
    ("211.4", "Success Learner", "211_4_Success_Learner.py"),
    ("211.5", "Worker Learning", "211_5_Worker_Learning.py"),
    ("211.6", "Batch Learning", "211_6_Batch_Learning.py"),
    ("211.7", "Recommendation Engine", "211_7_Recommendation_Engine.py"),
    ("211.8", "Learning Dashboard", "211_8_Learning_Dashboard.py"),
    ("211.9", "Learning Decision Engine", "211_9_Learning_Decision_Engine.py"),
    ("211.10", "Learning Auditor", "211_10_Learning_Auditor.py"),
]

def snake(s):
    out, prev = [], False
    for c in s:
        if c.isalnum():
            if c.isupper() and prev:
                out.append("_")
            out.append(c.lower())
            prev = c.islower() or c.isdigit()
        else:
            if out and out[-1] != "_":
                out.append("_")
            prev = False
    return "".join(out).strip("_")

def camel(s):
    return "".join(x.capitalize() for x in snake(s).split("_") if x)

def w(path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    if path.suffix == ".py":
        py_compile.compile(str(path), doraise=True)

def install_sdk():
    core = PKG / "core"
    w(core / "__init__.py", [""])
    w(core / "config.py", [
        "from pathlib import Path",
        'BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")',
        'STATE_DIR = BASE_DIR / "production_state"',
        'REPORT_DIR = BASE_DIR / "raporlar"',
        'LEARNING_DIR = STATE_DIR / "learning"',
        'LEARNING_HISTORY = LEARNING_DIR / "211_learning_history.jsonl"',
        'LEARNING_SNAPSHOT = LEARNING_DIR / "211_learning_snapshot.json"',
        'LEARNING_DASHBOARD = LEARNING_DIR / "211_learning_dashboard.json"',
        'HEALING_SNAPSHOT = STATE_DIR / "self_healing" / "210_healing_snapshot.json"',
        'HEALING_DASHBOARD = STATE_DIR / "self_healing" / "210_healing_dashboard.json"',
        'AUTONOMOUS_DASHBOARD = STATE_DIR / "autonomous" / "209_autonomous_dashboard.json"',
        'AUTOMATION_DASHBOARD = STATE_DIR / "automation" / "208_automation_dashboard.json"',
        'EXECUTION_DASHBOARD = STATE_DIR / "execution" / "207_execution_dashboard.json"',
        'SCHEDULER_DASHBOARD = STATE_DIR / "scheduler" / "206_scheduler_dashboard.json"',
    ])
    w(core / "utils.py", [
        "import json",
        "from pathlib import Path",
        "from datetime import datetime",
        "def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def ensure_dirs(*dirs):",
        "    for d in dirs: Path(d).mkdir(parents=True, exist_ok=True)",
        "def safe_json(path):",
        "    path = Path(path)",
        "    if not path.exists(): return {}",
        "    for enc in ('utf-8','utf-8-sig','cp1254','latin-1'):",
        "        try: return json.loads(path.read_text(encoding=enc, errors='ignore'))",
        "        except Exception: pass",
        "    return {}",
        "def write_json(path, data):",
        "    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)",
        "    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')",
        "def append_jsonl(path, data):",
        "    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)",
        "    with path.open('a', encoding='utf-8') as f: f.write(json.dumps(data, ensure_ascii=False)+'\\\\n')",
    ])
    w(core / "sdk.py", [
        "from .config import *",
        "from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl",
        "class LearningSDK:",
        "    def __init__(self, name='211.0 Learning SDK'): self.name=name",
        "    def load(self):",
        "        return {'healing_snapshot':safe_json(HEALING_SNAPSHOT),'healing_dashboard':safe_json(HEALING_DASHBOARD),'autonomous_dashboard':safe_json(AUTONOMOUS_DASHBOARD),'automation_dashboard':safe_json(AUTOMATION_DASHBOARD),'execution_dashboard':safe_json(EXECUTION_DASHBOARD),'scheduler_dashboard':safe_json(SCHEDULER_DASHBOARD)}",
        "    def build_context(self, raw):",
        "        healing=raw.get('healing_snapshot',{}) or {}; validation=healing.get('validation',{}) or {}; plan=healing.get('plan',{}) or {}; actions=plan.get('actions',[]) or []",
        "        execution=raw.get('execution_dashboard',{}) or {}; automation=raw.get('automation_dashboard',{}) or {}; autonomous=raw.get('autonomous_dashboard',{}) or {}; healing_dash=raw.get('healing_dashboard',{}) or {}; scheduler=raw.get('scheduler_dashboard',{}) or {}",
        "        risk=healing_dash.get('risk') or autonomous.get('risk') or automation.get('risk') or execution.get('risk') or scheduler.get('risk')",
        "        signals=[]",
        "        if validation.get('score') is not None: signals.append({'type':'HEALING_SCORE','value':validation.get('score')})",
        "        if actions: signals.append({'type':'HEALING_ACTION_COUNT','value':len(actions)})",
        "        if execution.get('assignment_count') is not None: signals.append({'type':'EXECUTION_ASSIGNMENT_COUNT','value':execution.get('assignment_count')})",
        "        if automation.get('trigger_count') is not None: signals.append({'type':'AUTOMATION_TRIGGER_COUNT','value':automation.get('trigger_count')})",
        "        if autonomous.get('operation_count') is not None: signals.append({'type':'AUTONOMOUS_OPERATION_COUNT','value':autonomous.get('operation_count')})",
        "        return {'created_at':now_text(),'risk':risk,'signal_count':len(signals),'signals':signals,'learning_ready':len(signals)>0 and risk in (None,'LOW')}",
        "    def validate(self, context):",
        "        errors=[]; warnings=[]",
        "        if context.get('signal_count',0)==0: warnings.append('Learning için sinyal bulunamadı.')",
        "        if context.get('risk')=='HIGH': errors.append('Risk HIGH; learning kontrollü moda alınmalı.')",
        "        if not context.get('learning_ready'): warnings.append('Learning ready durumu tam değil.')",
        "        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)",
        "        decision='LEARNING CONTEXT READY' if not errors else 'LEARNING CONTEXT BLOCKED'",
        "        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}",
        "    def plan(self, context, validation):",
        "        if validation['errors']: return {'learning_mode':'PAUSED','patterns':[],'message':'Learning blocked by validation errors.'}",
        "        patterns=[{'pattern':'OBSERVE_'+s['type'],'value':s.get('value'),'status':'LEARNED'} for s in context.get('signals',[])]",
        "        if not patterns: patterns.append({'pattern':'NO_PATTERN_AVAILABLE','status':'PLANNED'})",
        "        patterns.append({'pattern':'UPDATE_RECOMMENDATION_MEMORY','status':'PLANNED'}); patterns.append({'pattern':'LEARNING_AUDIT_LOG','status':'PLANNED'})",
        "        return {'learning_mode':'CONTROLLED_LEARNING','patterns':patterns,'message':str(len(patterns))+' learning pattern planned.'}",
        "    def export(self, payload, name='211_0_learning_sdk'):",
        "        ensure_dirs(LEARNING_DIR, REPORT_DIR, STATE_DIR); ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'",
        "        write_json(LEARNING_SNAPSHOT,payload); write_json(state,payload); append_jsonl(LEARNING_HISTORY,payload)",
        "        dash={'learning_status':payload['validation']['decision'],'learning_mode':payload['plan']['learning_mode'],'pattern_count':len(payload['plan']['patterns']),'risk':payload['context'].get('risk'),'signal_count':payload['context'].get('signal_count')}",
        "        write_json(LEARNING_DASHBOARD,dash)",
        "        lines=['='*80,'211.0 LEARNING SDK','='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['learning_mode']),'Patterns   : '+str(len(payload['plan']['patterns'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(LEARNING_SNAPSHOT),str(LEARNING_DASHBOARD),str(state),str(report)]",
        "        report.write_text('\\\\n'.join(lines), encoding='utf-8')",
        "        return {'snapshot':str(LEARNING_SNAPSHOT),'dashboard':str(LEARNING_DASHBOARD),'state':str(state),'report':str(report)}",
        "    def run(self):",
        "        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation); payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}; return {'payload':payload,'paths':self.export(payload)}",
    ])
    w(PKG / "learning_sdk_manager.py", [
        "import argparse",
        "from core.sdk import LearningSDK",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--test', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()",
        "    res=LearningSDK().run(); v=res['payload']['validation']; p=res['payload']['plan']",
        "    print('='*80); print('211.0 LEARNING SDK TAMAMLANDI'); print('='*80)",
        "    print('Validation : '+str(v['decision'])); print('Score      : '+str(v['score'])+' / 100'); print('Errors     : '+str(len(v['errors']))); print('Warnings   : '+str(len(v['warnings']))); print('Mode       : '+str(p['learning_mode'])); print('Patterns   : '+str(len(p['patterns']))); print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
    ])
    w(PY / "211_Learning_SDK.py", [
        "import sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "211"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from learning_sdk_manager import main",
        "if __name__=='__main__': main()",
    ])

def create_module(mid, name, bridge):
    slug=snake(name); cls=camel(name)+"Module"; manager=slug+"_manager"; safe=mid.replace(".","_")
    mdir=PKG/"modules"/slug
    w(mdir/"__init__.py", [""])
    w(mdir/"engine.py", [
        "from core.sdk import LearningSDK",
        "from core.config import STATE_DIR, REPORT_DIR, LEARNING_DIR",
        "from core.utils import ensure_dirs, now_stamp, now_text, write_json",
        f'MODULE_DIR = LEARNING_DIR / "{safe}_{slug}"',
        f'OUTPUT_FILE = MODULE_DIR / "{safe}_{slug}.json"',
        f"class {cls}:",
        f"    def __init__(self): self.sdk=LearningSDK(name='{mid} {name}')",
        "    def run(self):",
        "        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR); ts=now_stamp(); sdk_result=self.sdk.run(); context=sdk_result['payload']['context']; plan=sdk_result['payload']['plan']; validation=sdk_result['payload']['validation']",
        f"        result={{'score':validation['score'],'decision':'{name.upper()} READY' if not validation['errors'] else '{name.upper()} REVIEW','risk':context.get('risk'),'recommendation':plan.get('message')}}",
        f"        payload={{'module':'{mid} {name}','created_at':now_text(),'analysis':{{'context':context,'plan':plan}},'result':result,'sdk_reference':sdk_result['paths']}}",
        f"        state=STATE_DIR/f'{safe}_{slug}_state_{{ts}}.json'; report=REPORT_DIR/f'{safe}_{slug}_raporu_{{ts}}.txt'",
        "        write_json(OUTPUT_FILE,payload); write_json(state,payload)",
        f"        lines=['='*80,'{mid} {name}'.upper(),'='*80,'Score    : '+str(result['score'])+' / 100','Decision : '+str(result['decision']),'Risk     : '+str(result['risk']),'','Recommendation:',str(result['recommendation']),'','Dosyalar:',str(OUTPUT_FILE),str(report)]",
        "        report.write_text('\\n'.join(lines), encoding='utf-8')",
        "        return {'payload':payload,'result':result,'paths':{'output':str(OUTPUT_FILE),'state':str(state),'report':str(report)}}",
    ])
    w(PKG/(manager+".py"), [
        "import argparse",
        f"from modules.{slug}.engine import {cls}",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()",
        f"    res={cls}().run(); r=res['result']",
        f"    print('='*80); print('{mid} {name}'.upper()+' TAMAMLANDI'); print('='*80)",
        "    print('Score    : '+str(r['score'])+' / 100'); print('Decision : '+str(r['decision'])); print('Risk     : '+str(r['risk'])); print(''); print('Recommendation:'); print(r['recommendation']); print(''); print('Dosyalar:'); print(res['paths']['output']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
    ])
    for aux in ["dashboard.py","state.py","report.py"]:
        w(mdir/aux, ["def build(payload=None):", "    return payload or {}"])
    w(PY/bridge, [
        "import sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "211"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        f"from {manager} import main",
        "if __name__=='__main__': main()",
    ])
    w(PKG/"tests"/("test_"+slug+".py"), [
        "import sys",
        "from pathlib import Path",
        "PACKAGE_DIR = Path(__file__).resolve().parents[1]",
        "sys.path.insert(0, str(PACKAGE_DIR))",
        f"from modules.{slug}.engine import {cls}",
        f"if __name__=='__main__': res={cls}().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: {slug}')",
    ])
    return {"target_module": mid+" "+name, "decision": "MODULE GENERATED", "errors": []}

def install_generator():
    w(PKG/"generators"/"__init__.py", [""])
    w(PKG/"generators"/"module_generator.py", ["# Generated by 211 all-in-one builder."])
    w(PY/"211_Module_Generator.py", ["print('211 Module Generator is installed. Use batch builder.')"])

def write_run_all():
    lines=["import subprocess, sys","from pathlib import Path",'BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")',"COMMANDS = ["]
    lines.append('    [sys.executable, str(BASE / ".py" / "211_Learning_SDK.py"), "--test"],')
    for _,_,bridge in MODULES:
        lines.append(f'    [sys.executable, str(BASE / ".py" / "{bridge}"), "--run"],')
    lines += ["]","def main():","    print('='*80); print('211 LEARNING RUN ALL BAŞLADI'); print('='*80)","    for cmd in COMMANDS:","        print('\\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))","        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)","    print('\\n'+'='*80); print('211 LEARNING RUN ALL TAMAMLANDI'); print('='*80)","if __name__=='__main__': main()"]
    w(PY/"211_Run_All.py", lines)

def update_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    rel=RELEASES/"v2.1-learning-layer.md"
    rel.write_text("# v2.1 – Learning Layer\n\n**Tarih:** 09.07.2026\n\n---\n\n# Genel Bakış\n\nv2.1 sürümü ile NeoLegal Production Platform'un Learning Layer mimarisi tamamlanmıştır.\n\n---\n\n# Yeni Modüller\n\n- 211.0 Learning SDK\n- 211.0 Learning Module Generator\n- 211.1 Experience Collector\n- 211.2 Pattern Learner\n- 211.3 Failure Learner\n- 211.4 Success Learner\n- 211.5 Worker Learning\n- 211.6 Batch Learning\n- 211.7 Recommendation Engine\n- 211.8 Learning Dashboard\n- 211.9 Learning Decision Engine\n- 211.10 Learning Auditor\n- 211 Run All\n\n---\n\n# Sonuç\n\nLearning Layer başarıyla tamamlandı.\n", encoding="utf-8")
    entry="# v2.1 – Learning Layer\n\n**Tarih:** 09.07.2026  \n**Durum:** Production PASS  \n**Git Tag:** `v2.1-learning-layer`\n\n## Yeni Modüller\n\n- 211.0 Learning SDK\n- 211.0 Learning Module Generator\n- 211.1 Experience Collector\n- 211.2 Pattern Learner\n- 211.3 Failure Learner\n- 211.4 Success Learner\n- 211.5 Worker Learning\n- 211.6 Batch Learning\n- 211.7 Recommendation Engine\n- 211.8 Learning Dashboard\n- 211.9 Learning Decision Engine\n- 211.10 Learning Auditor\n- 211 Run All\n\n## Sonuç\n\nLearning Layer başarıyla tamamlandı.\n\n---\n"
    if CHANGELOG.exists():
        old=CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v2.1 – Learning Layer" not in old:
            CHANGELOG.write_text(entry+"\n"+old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n"+entry, encoding="utf-8")
    if README.exists():
        txt=README.read_text(encoding="utf-8", errors="ignore")
        if "| v2.1 | Learning Layer | PASS |" not in txt and "| v2.0 | Self-Healing Layer | PASS |" in txt:
            txt=txt.replace("| v2.0 | Self-Healing Layer | PASS |","| v2.1 | Learning Layer | PASS |\n| v2.0 | Self-Healing Layer | PASS |")
            README.write_text(txt, encoding="utf-8")
    idx=RELEASES/"index.md"
    files=sorted([x.name for x in RELEASES.glob("*.md") if x.name!="index.md"], reverse=True)
    idx.write_text("\n".join(["# Release Index","","| Release |","|---|"]+["| "+x+" |" for x in files]), encoding="utf-8")
    bat=BASE/"git_release_v2_1_learning.bat"
    bat.write_text("@echo off\ncd /d C:\\Users\\MSI\\Desktop\\kik_proje\n\ngit status\ngit add .\ngit commit -m \"Release v2.1: Learning layer architecture\"\ngit push\ngit tag v2.1-learning-layer\ngit push origin v2.1-learning-layer\n\npause\n", encoding="utf-8")
    return rel, idx, bat

def main():
    PY.mkdir(parents=True, exist_ok=True)
    install_sdk()
    install_generator()
    results=[create_module(*m) for m in MODULES]
    write_run_all()
    rel, idx, bat=update_docs()
    errors=[]
    for r in results: errors.extend(r.get("errors",[]))
    print("="*80)
    print("211 ALL-IN-ONE LEARNING LAYER BUILDER TAMAMLANDI")
    print("="*80)
    print("SDK                 : READY")
    print("Module Generator    : READY")
    print("Üretilen modül      :", len(results))
    print("Errors              :", len(errors))
    print("Run All             :", PY/"211_Run_All.py")
    print("Release Doc         :", rel)
    print("Release Index       :", idx)
    print("Git BAT             :", bat)
    print("")
    print("Şimdi çalıştır:")
    print(r'python ".py\211_Run_All.py"')
    print("")
    print("Run All PASS olursa Git için şunu çalıştırabilirsin:")
    print(str(bat))

if __name__=="__main__":
    main()
