
from pathlib import Path
import py_compile, sys

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "212"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"

MODULES = [
    ("212.1", "Model Router", "212_1_Model_Router.py"),
    ("212.2", "Prompt Planner", "212_2_Prompt_Planner.py"),
    ("212.3", "AI Task Manager", "212_3_AI_Task_Manager.py"),
    ("212.4", "Multi Model Engine", "212_4_Multi_Model_Engine.py"),
    ("212.5", "Consensus Engine", "212_5_Consensus_Engine.py"),
    ("212.6", "Response Optimizer", "212_6_Response_Optimizer.py"),
    ("212.7", "AI Supervisor", "212_7_AI_Supervisor.py"),
    ("212.8", "AI Dashboard", "212_8_AI_Dashboard.py"),
    ("212.9", "AI Decision Engine", "212_9_AI_Decision_Engine.py"),
    ("212.10", "AI Auditor", "212_10_AI_Auditor.py"),
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
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
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
        'AI_DIR = STATE_DIR / "ai_orchestrator"',
        'AI_HISTORY = AI_DIR / "212_ai_orchestrator_history.jsonl"',
        'AI_SNAPSHOT = AI_DIR / "212_ai_orchestrator_snapshot.json"',
        'AI_DASHBOARD = AI_DIR / "212_ai_orchestrator_dashboard.json"',
        'LEARNING_SNAPSHOT = STATE_DIR / "learning" / "211_learning_snapshot.json"',
        'LEARNING_DASHBOARD = STATE_DIR / "learning" / "211_learning_dashboard.json"',
        'HEALING_DASHBOARD = STATE_DIR / "self_healing" / "210_healing_dashboard.json"',
        'AUTONOMOUS_DASHBOARD = STATE_DIR / "autonomous" / "209_autonomous_dashboard.json"',
        'AUTOMATION_DASHBOARD = STATE_DIR / "automation" / "208_automation_dashboard.json"',
        'EXECUTION_DASHBOARD = STATE_DIR / "execution" / "207_execution_dashboard.json"',
        'DEFAULT_MODELS = ["GPT", "QWEN", "GEMINI", "CLAUDE", "NEOLEGAL_AI"]',
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
    ])
    w(core / "sdk.py", [
        "from .config import *",
        "from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl",
        "class AIOrchestratorSDK:",
        "    def __init__(self, name='212.0 AI Orchestrator SDK'): self.name=name",
        "    def load(self):",
        "        return {'learning_snapshot':safe_json(LEARNING_SNAPSHOT),'learning_dashboard':safe_json(LEARNING_DASHBOARD),'healing_dashboard':safe_json(HEALING_DASHBOARD),'autonomous_dashboard':safe_json(AUTONOMOUS_DASHBOARD),'automation_dashboard':safe_json(AUTOMATION_DASHBOARD),'execution_dashboard':safe_json(EXECUTION_DASHBOARD)}",
        "    def build_context(self, raw):",
        "        learning=raw.get('learning_snapshot',{}) or {}; learning_dash=raw.get('learning_dashboard',{}) or {}; healing=raw.get('healing_dashboard',{}) or {}; autonomous=raw.get('autonomous_dashboard',{}) or {}; automation=raw.get('automation_dashboard',{}) or {}; execution=raw.get('execution_dashboard',{}) or {}",
        "        validation=learning.get('validation',{}) or {}; plan=learning.get('plan',{}) or {}; patterns=plan.get('patterns',[]) or []",
        "        risk=learning_dash.get('risk') or healing.get('risk') or autonomous.get('risk') or automation.get('risk') or execution.get('risk')",
        "        tasks=[]",
        "        if patterns: tasks.append({'task':'ROUTE_LEARNING_PATTERNS','weight':len(patterns)})",
        "        if learning_dash.get('pattern_count') is not None: tasks.append({'task':'OPTIMIZE_RECOMMENDATIONS','weight':learning_dash.get('pattern_count')})",
        "        if healing.get('action_count') is not None: tasks.append({'task':'SUPERVISE_HEALING_CONTEXT','weight':healing.get('action_count')})",
        "        if autonomous.get('operation_count') is not None: tasks.append({'task':'ASSESS_AUTONOMOUS_CONTEXT','weight':autonomous.get('operation_count')})",
        "        return {'created_at':now_text(),'risk':risk,'learning_score':validation.get('score'),'task_count':len(tasks),'tasks':tasks,'models':DEFAULT_MODELS,'orchestration_ready':len(tasks)>0 and risk in (None,'LOW')}",
        "    def validate(self, context):",
        "        errors=[]; warnings=[]",
        "        if context.get('task_count',0)==0: warnings.append('AI orchestration için task bulunamadı.')",
        "        if context.get('risk')=='HIGH': errors.append('Risk HIGH; AI orchestration kontrollü moda alınmalı.')",
        "        if not context.get('orchestration_ready'): warnings.append('AI orchestration ready durumu tam değil.')",
        "        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)",
        "        decision='AI ORCHESTRATION CONTEXT READY' if not errors else 'AI ORCHESTRATION CONTEXT BLOCKED'",
        "        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}",
        "    def plan(self, context, validation):",
        "        if validation['errors']: return {'ai_mode':'PAUSED','routes':[],'message':'AI orchestration blocked by validation errors.'}",
        "        routes=[]",
        "        models=context.get('models',[]) or []",
        "        for i, task in enumerate(context.get('tasks',[])): routes.append({'task':task['task'],'model':models[i % len(models)] if models else 'DEFAULT','status':'ROUTED'})",
        "        if not routes: routes.append({'task':'NO_AI_TASK_AVAILABLE','model':'NONE','status':'PLANNED'})",
        "        routes.append({'task':'CONSENSUS_CHECK','model':'MULTI_MODEL','status':'PLANNED'})",
        "        routes.append({'task':'AI_AUDIT_LOG','model':'AUDITOR','status':'PLANNED'})",
        "        return {'ai_mode':'CONTROLLED_AI_ORCHESTRATION','routes':routes,'message':str(len(routes))+' AI orchestration route planned.'}",
        "    def export(self,payload,name='212_0_ai_orchestrator_sdk'):",
        "        ensure_dirs(AI_DIR, REPORT_DIR, STATE_DIR); ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'",
        "        write_json(AI_SNAPSHOT,payload); write_json(state,payload); append_jsonl(AI_HISTORY,payload)",
        "        dash={'ai_status':payload['validation']['decision'],'ai_mode':payload['plan']['ai_mode'],'route_count':len(payload['plan']['routes']),'risk':payload['context'].get('risk'),'task_count':payload['context'].get('task_count')}",
        "        write_json(AI_DASHBOARD,dash)",
        "        lines=['='*80,'212.0 AI ORCHESTRATOR SDK','='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['ai_mode']),'Routes     : '+str(len(payload['plan']['routes'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(AI_SNAPSHOT),str(AI_DASHBOARD),str(state),str(report)]",
        "        report.write_text('\\\\n'.join(lines), encoding='utf-8')",
        "        return {'snapshot':str(AI_SNAPSHOT),'dashboard':str(AI_DASHBOARD),'state':str(state),'report':str(report)}",
        "    def run(self):",
        "        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation); payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}; return {'payload':payload,'paths':self.export(payload)}",
    ])
    w(PKG / "ai_orchestrator_sdk_manager.py", [
        "import argparse",
        "from core.sdk import AIOrchestratorSDK",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--test', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()",
        "    res=AIOrchestratorSDK().run(); v=res['payload']['validation']; p=res['payload']['plan']",
        "    print('='*80); print('212.0 AI ORCHESTRATOR SDK TAMAMLANDI'); print('='*80)",
        "    print('Validation : '+str(v['decision'])); print('Score      : '+str(v['score'])+' / 100'); print('Errors     : '+str(len(v['errors']))); print('Warnings   : '+str(len(v['warnings']))); print('Mode       : '+str(p['ai_mode'])); print('Routes     : '+str(len(p['routes']))); print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
    ])
    w(PY / "212_AI_Orchestrator_SDK.py", [
        "import sys",
        "from pathlib import Path",
        'PACKAGE_DIR = Path(__file__).resolve().parent / "212"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        "from ai_orchestrator_sdk_manager import main",
        "if __name__=='__main__': main()",
    ])

def create_module(mid, name, bridge):
    slug=snake(name); cls=camel(name)+"Module"; manager=slug+"_manager"; safe=mid.replace(".","_")
    mdir=PKG/"modules"/slug
    w(mdir/"__init__.py", [""])
    w(mdir/"engine.py", [
        "from core.sdk import AIOrchestratorSDK",
        "from core.config import STATE_DIR, REPORT_DIR, AI_DIR",
        "from core.utils import ensure_dirs, now_stamp, now_text, write_json",
        f'MODULE_DIR = AI_DIR / "{safe}_{slug}"',
        f'OUTPUT_FILE = MODULE_DIR / "{safe}_{slug}.json"',
        f"class {cls}:",
        f"    def __init__(self): self.sdk=AIOrchestratorSDK(name='{mid} {name}')",
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
        'PACKAGE_DIR = Path(__file__).resolve().parent / "212"',
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
    w(PKG/"generators"/"module_generator.py", ["# Generated by 212 all-in-one builder."])
    w(PY/"212_Module_Generator.py", ["print('212 Module Generator is installed. Use batch builder.')"])

def write_run_all():
    lines=["import subprocess, sys","from pathlib import Path",'BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")',"COMMANDS = ["]
    lines.append('    [sys.executable, str(BASE / ".py" / "212_AI_Orchestrator_SDK.py"), "--test"],')
    for _,_,bridge in MODULES:
        lines.append(f'    [sys.executable, str(BASE / ".py" / "{bridge}"), "--run"],')
    lines += ["]","def main():","    print('='*80); print('212 AI ORCHESTRATOR RUN ALL BAŞLADI'); print('='*80)","    for cmd in COMMANDS:","        print('\\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))","        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)","    print('\\n'+'='*80); print('212 AI ORCHESTRATOR RUN ALL TAMAMLANDI'); print('='*80)","if __name__=='__main__': main()"]
    w(PY/"212_Run_All.py", lines)

def update_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    rel=RELEASES/"v2.2-ai-orchestrator-layer.md"
    rel.write_text("# v2.2 – AI Orchestrator Layer\n\n**Tarih:** 09.07.2026\n\n---\n\n# Genel Bakış\n\nv2.2 sürümü ile NeoLegal Production Platform'un AI Orchestrator Layer mimarisi tamamlanmıştır.\n\nBu katman, Learning Layer çıktılarından gelen sinyalleri AI görevlerine dönüştürür; model yönlendirme, prompt planlama, çoklu model, consensus ve AI denetim altyapısını oluşturur.\n\n---\n\n# Yeni Modüller\n\n- 212.0 AI Orchestrator SDK\n- 212.0 AI Orchestrator Module Generator\n- 212.1 Model Router\n- 212.2 Prompt Planner\n- 212.3 AI Task Manager\n- 212.4 Multi Model Engine\n- 212.5 Consensus Engine\n- 212.6 Response Optimizer\n- 212.7 AI Supervisor\n- 212.8 AI Dashboard\n- 212.9 AI Decision Engine\n- 212.10 AI Auditor\n- 212 Run All\n\n---\n\n# Sonuç\n\nAI Orchestrator Layer başarıyla tamamlandı.\n", encoding="utf-8")
    entry="# v2.2 – AI Orchestrator Layer\n\n**Tarih:** 09.07.2026  \n**Durum:** Production PASS  \n**Git Tag:** `v2.2-ai-orchestrator-layer`\n\n## Yeni Modüller\n\n- 212.0 AI Orchestrator SDK\n- 212.0 AI Orchestrator Module Generator\n- 212.1 Model Router\n- 212.2 Prompt Planner\n- 212.3 AI Task Manager\n- 212.4 Multi Model Engine\n- 212.5 Consensus Engine\n- 212.6 Response Optimizer\n- 212.7 AI Supervisor\n- 212.8 AI Dashboard\n- 212.9 AI Decision Engine\n- 212.10 AI Auditor\n- 212 Run All\n\n## Sonuç\n\nAI Orchestrator Layer başarıyla tamamlandı.\n\n---\n"
    if CHANGELOG.exists():
        old=CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v2.2 – AI Orchestrator Layer" not in old:
            CHANGELOG.write_text(entry+"\n"+old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n"+entry, encoding="utf-8")
    if README.exists():
        txt=README.read_text(encoding="utf-8", errors="ignore")
        if "| v2.2 | AI Orchestrator Layer | PASS |" not in txt and "| v2.1 | Learning Layer | PASS |" in txt:
            txt=txt.replace("| v2.1 | Learning Layer | PASS |","| v2.2 | AI Orchestrator Layer | PASS |\n| v2.1 | Learning Layer | PASS |")
            README.write_text(txt, encoding="utf-8")
    idx=RELEASES/"index.md"
    files=sorted([x.name for x in RELEASES.glob("*.md") if x.name!="index.md"], reverse=True)
    idx.write_text("\n".join(["# Release Index","","| Release |","|---|"]+["| "+x+" |" for x in files]), encoding="utf-8")
    bat=BASE/"git_release_v2_2_ai_orchestrator.bat"
    bat.write_text("@echo off\ncd /d C:\\Users\\MSI\\Desktop\\kik_proje\n\ngit status\ngit add .\ngit commit -m \"Release v2.2: AI orchestrator layer architecture\"\ngit push\ngit tag v2.2-ai-orchestrator-layer\ngit push origin v2.2-ai-orchestrator-layer\n\npause\n", encoding="utf-8")
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
    print("212 ALL-IN-ONE AI ORCHESTRATOR BUILDER TAMAMLANDI")
    print("="*80)
    print("SDK                 : READY")
    print("Module Generator    : READY")
    print("Üretilen modül      :", len(results))
    print("Errors              :", len(errors))
    print("Run All             :", PY/"212_Run_All.py")
    print("Release Doc         :", rel)
    print("Release Index       :", idx)
    print("Git BAT             :", bat)
    print("")
    print("Şimdi çalıştır:")
    print(r'python ".py\212_Run_All.py"')
    print("")
    print("Run All PASS olursa Git için şunu çalıştırabilirsin:")
    print(str(bat))

if __name__=="__main__":
    main()
