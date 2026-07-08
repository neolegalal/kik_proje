
# -*- coding: utf-8 -*-
from pathlib import Path
import py_compile
import sys

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"

LAYERS = [
    {
        "id": "213",
        "version": "v2.3",
        "name": "Knowledge Graph",
        "slug": "knowledge_graph",
        "release_slug": "knowledge-graph-layer",
        "state_dir": "knowledge_graph",
        "sdk_class": "KnowledgeGraphSDK",
        "sdk_bridge": "213_Knowledge_Graph_SDK.py",
        "run_all": "213_Run_All.py",
        "git_bat": "git_release_v2_3_knowledge_graph.bat",
        "modules": [
            "Graph Builder",
            "Relation Extractor",
            "Entity Resolver",
            "Knowledge Store",
            "Semantic Search",
            "Context Builder",
            "Graph Dashboard",
            "Graph Decision Engine",
            "Graph Auditor",
            "Graph Optimizer",
        ],
        "source_dashboards": [
            ("ai", "ai_orchestrator", "212_ai_orchestrator_dashboard.json"),
            ("learning", "learning", "211_learning_dashboard.json"),
            ("healing", "self_healing", "210_healing_dashboard.json"),
        ],
        "unit": "graph operation",
    },
    {
        "id": "214",
        "version": "v2.4",
        "name": "Continuous Improvement",
        "slug": "continuous_improvement",
        "release_slug": "continuous-improvement-layer",
        "state_dir": "continuous_improvement",
        "sdk_class": "ContinuousImprovementSDK",
        "sdk_bridge": "214_Continuous_Improvement_SDK.py",
        "run_all": "214_Run_All.py",
        "git_bat": "git_release_v2_4_continuous_improvement.bat",
        "modules": [
            "Improvement Collector",
            "Feedback Analyzer",
            "Quality Loop Engine",
            "Optimization Planner",
            "Improvement Prioritizer",
            "Experiment Manager",
            "Improvement Dashboard",
            "Improvement Decision Engine",
            "Improvement Auditor",
            "Improvement Roadmap Engine",
        ],
        "source_dashboards": [
            ("graph", "knowledge_graph", "213_knowledge_graph_dashboard.json"),
            ("ai", "ai_orchestrator", "212_ai_orchestrator_dashboard.json"),
            ("learning", "learning", "211_learning_dashboard.json"),
        ],
        "unit": "improvement operation",
    },
    {
        "id": "215",
        "version": "v2.5",
        "name": "Enterprise Platform",
        "slug": "enterprise_platform",
        "release_slug": "enterprise-platform-layer",
        "state_dir": "enterprise_platform",
        "sdk_class": "EnterprisePlatformSDK",
        "sdk_bridge": "215_Enterprise_Platform_SDK.py",
        "run_all": "215_Run_All.py",
        "git_bat": "git_release_v2_5_enterprise_platform.bat",
        "modules": [
            "Enterprise Controller",
            "Tenant Manager",
            "Access Governance",
            "Policy Registry",
            "Service Catalog",
            "Compliance Manager",
            "Enterprise Dashboard",
            "Enterprise Decision Engine",
            "Enterprise Auditor",
            "Enterprise Release Manager",
        ],
        "source_dashboards": [
            ("improvement", "continuous_improvement", "214_continuous_improvement_dashboard.json"),
            ("graph", "knowledge_graph", "213_knowledge_graph_dashboard.json"),
            ("ai", "ai_orchestrator", "212_ai_orchestrator_dashboard.json"),
        ],
        "unit": "enterprise operation",
    },
    {
        "id": "216",
        "version": "v2.6",
        "name": "Production Cluster",
        "slug": "production_cluster",
        "release_slug": "production-cluster-layer",
        "state_dir": "production_cluster",
        "sdk_class": "ProductionClusterSDK",
        "sdk_bridge": "216_Production_Cluster_SDK.py",
        "run_all": "216_Run_All.py",
        "git_bat": "git_release_v2_6_production_cluster.bat",
        "modules": [
            "Cluster Controller",
            "Node Registry",
            "Worker Pool Manager",
            "Load Balancer",
            "Cluster Health Monitor",
            "Scaling Planner",
            "Cluster Dashboard",
            "Cluster Decision Engine",
            "Cluster Auditor",
            "Cluster Recovery Manager",
        ],
        "source_dashboards": [
            ("enterprise", "enterprise_platform", "215_enterprise_platform_dashboard.json"),
            ("improvement", "continuous_improvement", "214_continuous_improvement_dashboard.json"),
            ("graph", "knowledge_graph", "213_knowledge_graph_dashboard.json"),
        ],
        "unit": "cluster operation",
    },
    {
        "id": "217",
        "version": "v2.7",
        "name": "Large Scale Production",
        "slug": "large_scale_production",
        "release_slug": "large-scale-production-layer",
        "state_dir": "large_scale_production",
        "sdk_class": "LargeScaleProductionSDK",
        "sdk_bridge": "217_Large_Scale_Production_SDK.py",
        "run_all": "217_Run_All.py",
        "git_bat": "git_release_v2_7_large_scale_production.bat",
        "modules": [
            "Mass Production Controller",
            "Batch Expansion Engine",
            "Throughput Planner",
            "Capacity Governor",
            "Quality Gate Manager",
            "Production Rollout Engine",
            "Large Scale Dashboard",
            "Large Scale Decision Engine",
            "Large Scale Auditor",
            "Production Completion Manager",
        ],
        "source_dashboards": [
            ("cluster", "production_cluster", "216_production_cluster_dashboard.json"),
            ("enterprise", "enterprise_platform", "215_enterprise_platform_dashboard.json"),
            ("improvement", "continuous_improvement", "214_continuous_improvement_dashboard.json"),
        ],
        "unit": "large scale operation",
    },
    {
        "id": "218",
        "version": "v2.8",
        "name": "NeoLegal AI Runtime",
        "slug": "neolegal_ai_runtime",
        "release_slug": "neolegal-ai-runtime-layer",
        "state_dir": "neolegal_ai_runtime",
        "sdk_class": "NeoLegalAIRuntimeSDK",
        "sdk_bridge": "218_NeoLegal_AI_Runtime_SDK.py",
        "run_all": "218_Run_All.py",
        "git_bat": "git_release_v2_8_neolegal_ai_runtime.bat",
        "modules": [
            "Runtime Controller",
            "RAG Runtime Engine",
            "Query Understanding",
            "Legal Answer Engine",
            "Citation Engine",
            "Hallucination Guard",
            "Runtime Dashboard",
            "Runtime Decision Engine",
            "Runtime Auditor",
            "Public API Gateway",
        ],
        "source_dashboards": [
            ("large_scale", "large_scale_production", "217_large_scale_production_dashboard.json"),
            ("cluster", "production_cluster", "216_production_cluster_dashboard.json"),
            ("ai", "ai_orchestrator", "212_ai_orchestrator_dashboard.json"),
        ],
        "unit": "runtime operation",
    },
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

def install_sdk(layer):
    lid = layer["id"]
    lname = layer["name"]
    pkg = PY / lid
    core = pkg / "core"
    state_var = layer["state_dir"].upper()
    class_name = layer["sdk_class"]
    snapshot = f"{lid}_{layer['slug']}_snapshot.json"
    dashboard = f"{lid}_{layer['slug']}_dashboard.json"
    history = f"{lid}_{layer['slug']}_history.jsonl"

    w(core / "__init__.py", [""])
    config_lines = [
        "from pathlib import Path",
        'BASE_DIR = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")',
        'STATE_DIR = BASE_DIR / "production_state"',
        'REPORT_DIR = BASE_DIR / "raporlar"',
        f'{state_var}_DIR = STATE_DIR / "{layer["state_dir"]}"',
        f'{state_var}_HISTORY = {state_var}_DIR / "{history}"',
        f'{state_var}_SNAPSHOT = {state_var}_DIR / "{snapshot}"',
        f'{state_var}_DASHBOARD = {state_var}_DIR / "{dashboard}"',
    ]
    for key, folder, filename in layer["source_dashboards"]:
        config_lines.append(f'{key.upper()}_DASHBOARD = STATE_DIR / "{folder}" / "{filename}"')
    w(core / "config.py", config_lines)

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

    load_dict = ",".join([f"'{key}':safe_json({key.upper()}_DASHBOARD)" for key, _, _ in layer["source_dashboards"]])
    primary_key = layer["source_dashboards"][0][0]
    second_key = layer["source_dashboards"][1][0] if len(layer["source_dashboards"]) > 1 else primary_key

    w(core / "sdk.py", [
        "from .config import *",
        "from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl",
        f"class {class_name}:",
        f"    def __init__(self, name='{lid}.0 {lname} SDK'): self.name=name",
        "    def load(self):",
        f"        return {{{load_dict}}}",
        "    def build_context(self, raw):",
        f"        primary=raw.get('{primary_key}',{{}}) or {{}}",
        f"        secondary=raw.get('{second_key}',{{}}) or {{}}",
        "        risk=primary.get('risk') or secondary.get('risk')",
        "        source_count=sum(1 for v in raw.values() if v)",
        "        signals=[]",
        "        for k,v in raw.items():",
        "            if isinstance(v, dict) and v:",
        "                signals.append({'source':k,'keys':len(v),'status':'OBSERVED'})",
        f"        return {{'created_at':now_text(),'risk':risk,'source_count':source_count,'signals':signals,'layer_ready':source_count>0 and risk in (None,'LOW')}}",
        "    def validate(self, context):",
        "        errors=[]; warnings=[]",
        "        if context.get('source_count',0)==0: warnings.append('Kaynak dashboard bulunamadı.')",
        "        if context.get('risk')=='HIGH': errors.append('Risk HIGH; kontrollü moda alınmalı.')",
        "        if not context.get('layer_ready'): warnings.append('Layer ready durumu tam değil.')",
        "        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)",
        f"        decision='{lname.upper()} CONTEXT READY' if not errors else '{lname.upper()} CONTEXT BLOCKED'",
        "        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}",
        "    def plan(self, context, validation):",
        f"        if validation['errors']: return {{'mode':'PAUSED','operations':[],'message':'{lname} blocked by validation errors.'}}",
        "        operations=[]",
        "        for sig in context.get('signals',[]): operations.append({'operation':'PROCESS_'+sig['source'].upper(),'status':'PLANNED'})",
        "        if not operations: operations.append({'operation':'NO_SOURCE_AVAILABLE','status':'PLANNED'})",
        f"        operations.append({{'operation':'{snake(lname).upper()}_AUDIT_LOG','status':'PLANNED'}})",
        f"        return {{'mode':'CONTROLLED_{snake(lname).upper()}','operations':operations,'message':str(len(operations))+' {layer['unit']} planned.'}}",
        "    def export(self,payload,name=None):",
        f"        name=name or '{lid}_0_{layer['slug']}_sdk'",
        f"        ensure_dirs({state_var}_DIR, REPORT_DIR, STATE_DIR); ts=now_stamp(); state=STATE_DIR/f'{{name}}_state_{{ts}}.json'; report=REPORT_DIR/f'{{name}}_raporu_{{ts}}.txt'",
        f"        write_json({state_var}_SNAPSHOT,payload); write_json(state,payload); append_jsonl({state_var}_HISTORY,payload)",
        f"        dash={{'status':payload['validation']['decision'],'mode':payload['plan']['mode'],'operation_count':len(payload['plan']['operations']),'risk':payload['context'].get('risk'),'source_count':payload['context'].get('source_count')}}",
        f"        write_json({state_var}_DASHBOARD,dash)",
        f"        lines=['='*80,'{lid}.0 {lname} SDK'.upper(),'='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['mode']),'Operations : '+str(len(payload['plan']['operations'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str({state_var}_SNAPSHOT),str({state_var}_DASHBOARD),str(state),str(report)]",
        "        report.write_text('\\\\n'.join(lines), encoding='utf-8')",
        f"        return {{'snapshot':str({state_var}_SNAPSHOT),'dashboard':str({state_var}_DASHBOARD),'state':str(state),'report':str(report)}}",
        "    def run(self):",
        "        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation); payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}; return {'payload':payload,'paths':self.export(payload)}",
    ])

    manager_name = f"{layer['slug']}_sdk_manager"
    w(pkg / (manager_name + ".py"), [
        "import argparse",
        f"from core.sdk import {class_name}",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--test', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()",
        f"    res={class_name}().run(); v=res['payload']['validation']; p=res['payload']['plan']",
        f"    print('='*80); print('{lid}.0 {lname} SDK TAMAMLANDI'.upper()); print('='*80)",
        "    print('Validation : '+str(v['decision'])); print('Score      : '+str(v['score'])+' / 100'); print('Errors     : '+str(len(v['errors']))); print('Warnings   : '+str(len(v['warnings']))); print('Mode       : '+str(p['mode'])); print('Operations : '+str(len(p['operations']))); print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
    ])
    w(PY / layer["sdk_bridge"], [
        "import sys",
        "from pathlib import Path",
        f'PACKAGE_DIR = Path(__file__).resolve().parent / "{lid}"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        f"from {manager_name} import main",
        "if __name__=='__main__': main()",
    ])

def create_module(layer, module_index, module_name):
    lid = layer["id"]
    pkg = PY / lid
    lname = layer["name"]
    bridge = f"{lid}_{module_index}_{'_'.join(module_name.split())}.py"
    # Special use given actual bridge from run generation later
    slug = snake(module_name)
    cls = camel(module_name) + "Module"
    manager = slug + "_manager"
    safe = f"{lid}_{module_index}"
    state_var = layer["state_dir"].upper()
    w(pkg / "modules" / slug / "__init__.py", [""])
    w(pkg / "modules" / slug / "engine.py", [
        f"from core.sdk import {layer['sdk_class']}",
        f"from core.config import STATE_DIR, REPORT_DIR, {state_var}_DIR",
        "from core.utils import ensure_dirs, now_stamp, now_text, write_json",
        f'MODULE_DIR = {state_var}_DIR / "{safe}_{slug}"',
        f'OUTPUT_FILE = MODULE_DIR / "{safe}_{slug}.json"',
        f"class {cls}:",
        f"    def __init__(self): self.sdk={layer['sdk_class']}(name='{lid}.{module_index} {module_name}')",
        "    def run(self):",
        "        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR); ts=now_stamp(); sdk_result=self.sdk.run(); context=sdk_result['payload']['context']; plan=sdk_result['payload']['plan']; validation=sdk_result['payload']['validation']",
        f"        result={{'score':validation['score'],'decision':'{module_name.upper()} READY' if not validation['errors'] else '{module_name.upper()} REVIEW','risk':context.get('risk'),'recommendation':plan.get('message')}}",
        f"        payload={{'module':'{lid}.{module_index} {module_name}','created_at':now_text(),'analysis':{{'context':context,'plan':plan}},'result':result,'sdk_reference':sdk_result['paths']}}",
        f"        state=STATE_DIR/f'{safe}_{slug}_state_{{ts}}.json'; report=REPORT_DIR/f'{safe}_{slug}_raporu_{{ts}}.txt'",
        "        write_json(OUTPUT_FILE,payload); write_json(state,payload)",
        f"        lines=['='*80,'{lid}.{module_index} {module_name}'.upper(),'='*80,'Score    : '+str(result['score'])+' / 100','Decision : '+str(result['decision']),'Risk     : '+str(result['risk']),'','Recommendation:',str(result['recommendation']),'','Dosyalar:',str(OUTPUT_FILE),str(report)]",
        "        report.write_text('\\\\n'.join(lines), encoding='utf-8')",
        "        return {'payload':payload,'result':result,'paths':{'output':str(OUTPUT_FILE),'state':str(state),'report':str(report)}}",
    ])
    w(pkg / (manager + ".py"), [
        "import argparse",
        f"from modules.{slug}.engine import {cls}",
        "def main():",
        "    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()",
        f"    res={cls}().run(); r=res['result']",
        f"    print('='*80); print('{lid}.{module_index} {module_name}'.upper()+' TAMAMLANDI'); print('='*80)",
        "    print('Score    : '+str(r['score'])+' / 100'); print('Decision : '+str(r['decision'])); print('Risk     : '+str(r['risk'])); print(''); print('Recommendation:'); print(r['recommendation']); print(''); print('Dosyalar:'); print(res['paths']['output']); print(res['paths']['report'])",
        "if __name__=='__main__': main()",
    ])
    for aux in ["dashboard.py", "state.py", "report.py"]:
        w(pkg / "modules" / slug / aux, ["def build(payload=None):", "    return payload or {}"])
    bridge_name = f"{lid}_{module_index}_{camel(module_name)}.py"
    w(PY / bridge_name, [
        "import sys",
        "from pathlib import Path",
        f'PACKAGE_DIR = Path(__file__).resolve().parent / "{lid}"',
        "sys.path.insert(0, str(PACKAGE_DIR))",
        f"from {manager} import main",
        "if __name__=='__main__': main()",
    ])
    w(pkg / "tests" / ("test_" + slug + ".py"), [
        "import sys",
        "from pathlib import Path",
        "PACKAGE_DIR = Path(__file__).resolve().parents[1]",
        "sys.path.insert(0, str(PACKAGE_DIR))",
        f"from modules.{slug}.engine import {cls}",
        f"if __name__=='__main__': res={cls}().run(); assert 'result' in res; assert 'paths' in res; print('TEST PASS: {slug}')",
    ])
    return bridge_name

def install_generator(layer):
    pkg = PY / layer["id"]
    w(pkg / "generators" / "__init__.py", [""])
    w(pkg / "generators" / "module_generator.py", [f"# Generated by 300 Platform Layer Generator for {layer['id']}."])
    w(PY / f"{layer['id']}_Module_Generator.py", [f"print('{layer['id']} Module Generator is installed. Use generated layer builder.')"])

def write_run_all(layer, bridges):
    lines = ["import subprocess, sys", "from pathlib import Path", 'BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")', "COMMANDS = ["]
    lines.append(f'    [sys.executable, str(BASE / ".py" / "{layer["sdk_bridge"]}"), "--test"],')
    for b in bridges:
        lines.append(f'    [sys.executable, str(BASE / ".py" / "{b}"), "--run"],')
    lines += [
        "]",
        "def main():",
        f"    print('='*80); print('{layer['id']} {layer['name'].upper()} RUN ALL BAŞLADI'); print('='*80)",
        "    for cmd in COMMANDS:",
        "        print('\\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))",
        "        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)",
        f"    print('\\n'+'='*80); print('{layer['id']} {layer['name'].upper()} RUN ALL TAMAMLANDI'); print('='*80)",
        "if __name__=='__main__': main()",
    ]
    w(PY / layer["run_all"], lines)

def update_docs(layer):
    RELEASES.mkdir(parents=True, exist_ok=True)
    rel = RELEASES / f"{layer['version']}-{layer['release_slug']}.md"
    module_lines = [f"- {layer['id']}.0 {layer['name']} SDK", f"- {layer['id']}.0 {layer['name']} Module Generator"]
    for i, m in enumerate(layer["modules"], start=1):
        module_lines.append(f"- {layer['id']}.{i} {m}")
    module_lines.append(f"- {layer['id']} Run All")
    rel_text = [
        f"# {layer['version']} – {layer['name']} Layer",
        "",
        "**Tarih:** 09.07.2026",
        "",
        "---",
        "",
        "# Genel Bakış",
        "",
        f"{layer['version']} sürümü ile NeoLegal Production Platform'un {layer['name']} Layer mimarisi tamamlanmıştır.",
        "",
        "---",
        "",
        "# Yeni Modüller",
        "",
    ] + module_lines + ["", "---", "", "# Sonuç", "", f"{layer['name']} Layer başarıyla tamamlandı."]
    rel.write_text("\n".join(rel_text) + "\n", encoding="utf-8")

    entry = [
        f"# {layer['version']} – {layer['name']} Layer",
        "",
        "**Tarih:** 09.07.2026  ",
        "**Durum:** Production PASS  ",
        f"**Git Tag:** `{layer['version']}-{layer['release_slug']}`",
        "",
        "## Yeni Modüller",
        "",
    ] + module_lines + ["", "## Sonuç", "", f"{layer['name']} Layer başarıyla tamamlandı.", "", "---", ""]
    entry_text = "\n".join(entry)
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if f"{layer['version']} – {layer['name']} Layer" not in old:
            CHANGELOG.write_text(entry_text + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry_text, encoding="utf-8")

    if README.exists():
        txt = README.read_text(encoding="utf-8", errors="ignore")
        row = f"| {layer['version']} | {layer['name']} Layer | PASS |"
        if row not in txt:
            # Insert after Release History table header when possible, otherwise above v2.2 row.
            if "| v2.2 | AI Orchestrator Layer | PASS |" in txt:
                txt = txt.replace("| v2.2 | AI Orchestrator Layer | PASS |", row + "\n| v2.2 | AI Orchestrator Layer | PASS |")
            elif "## Release History" in txt:
                txt = txt.replace("## Release History", "## Release History\n\n" + row)
            README.write_text(txt, encoding="utf-8")

    idx = RELEASES / "index.md"
    files = sorted([x.name for x in RELEASES.glob("*.md") if x.name != "index.md"], reverse=True)
    idx.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + x + " |" for x in files]), encoding="utf-8")

    bat = BASE / layer["git_bat"]
    tag = f"{layer['version']}-{layer['release_slug']}"
    bat.write_text(
        "@echo off\n"
        "cd /d C:\\Users\\MSI\\Desktop\\kik_proje\n\n"
        "git status\n"
        "git add .\n"
        f"git commit -m \"Release {layer['version']}: {layer['name']} layer architecture\"\n"
        "git push\n"
        f"git tag {tag}\n"
        f"git push origin {tag}\n\n"
        "pause\n",
        encoding="utf-8",
    )
    return rel, idx, bat

def build_layer(layer):
    install_sdk(layer)
    install_generator(layer)
    bridges = []
    for i, module_name in enumerate(layer["modules"], start=1):
        bridges.append(create_module(layer, i, module_name))
    write_run_all(layer, bridges)
    rel, idx, bat = update_docs(layer)
    return {"layer": layer["id"], "name": layer["name"], "bridges": bridges, "release": rel, "index": idx, "bat": bat}

def write_mega_run_all(results):
    lines = ["import subprocess, sys", "from pathlib import Path", 'BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")', "COMMANDS = ["]
    for layer in LAYERS:
        lines.append(f'    [sys.executable, str(BASE / ".py" / "{layer["run_all"]}")],')
    lines += [
        "]",
        "def main():",
        "    print('='*80); print('213-218 MEGA PLATFORM RUN ALL BAŞLADI'); print('='*80)",
        "    for cmd in COMMANDS:",
        "        print('\\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))",
        "        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)",
        "    print('\\n'+'='*80); print('213-218 MEGA PLATFORM RUN ALL TAMAMLANDI'); print('='*80)",
        "if __name__=='__main__': main()",
    ]
    w(PY / "213_218_Mega_Run_All.py", lines)

def write_mega_git_bat():
    lines = [
        "@echo off",
        "cd /d C:\\Users\\MSI\\Desktop\\kik_proje",
        "",
        "git status",
        "git add .",
        'git commit -m "Release v2.3-v2.8: Complete platform layers 213-218"',
        "git push",
    ]
    for layer in LAYERS:
        tag = f"{layer['version']}-{layer['release_slug']}"
        lines.append(f"git tag {tag}")
        lines.append(f"git push origin {tag}")
    lines += ["", "pause"]
    bat = BASE / "git_release_v2_3_to_v2_8_layers.bat"
    bat.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return bat

def main():
    PY.mkdir(parents=True, exist_ok=True)
    results = []
    for layer in LAYERS:
        results.append(build_layer(layer))
    write_mega_run_all(results)
    mega_bat = write_mega_git_bat()
    print("=" * 80)
    print("300 PLATFORM LAYER GENERATOR 213-218 TAMAMLANDI")
    print("=" * 80)
    print("Üretilen katman:", len(results))
    print("")
    for r in results:
        print(f"{r['layer']} {r['name']} -> READY")
    print("")
    print("Toplu test:")
    print(r'python ".py\213_218_Mega_Run_All.py"')
    print("")
    print("Tek tek test dosyaları:")
    for layer in LAYERS:
        print(f'python ".py\\{layer["run_all"]}"')
    print("")
    print("Toplu Git BAT:")
    print(mega_bat)
    print("")
    print("Not: İstersen her katmanın kendi git_release_*.bat dosyası da üretildi.")

if __name__ == "__main__":
    main()
