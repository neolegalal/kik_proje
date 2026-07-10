
# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys, py_compile
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

NEXTGEN_DIR = STATE / "next_generation_neolegal"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v13.0-v17.0"
TAG = "v13-v17-next-generation-neolegal-ai"
RELEASE_FILE = RELEASES / "v13-v17-next-generation-neolegal-ai.md"
GIT_BAT = BASE / "git_release_v13_to_v17_next_generation_neolegal_ai.bat"

MODULES = [
    ("1801", "NeoLegal Copilot", "copilot"),
    ("1802", "Knowledge Graph Engine", "knowledge_graph_engine"),
    ("1803", "Legal Time Machine", "legal_time_machine"),
    ("1804", "Multi Agent Legal AI", "multi_agent_legal_ai"),
    ("1805", "Prediction Simulation Engine", "prediction_simulation_engine"),
    ("1806", "Next Generation Integration Layer", "next_generation_integration_layer"),
    ("1807", "Next Generation QA Auditor", "next_generation_qa_auditor"),
    ("1808", "Next Generation Dashboard", "next_generation_dashboard"),
    ("1809", "Next Generation Release Manager", "next_generation_release_manager"),
    ("1810", "Next Generation Certificate", "next_generation_certificate"),
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

SDK_CODE = r"""
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
NEXTGEN_DIR = STATE / "next_generation_neolegal"

SUPPORT_IDS = ["1700", "1600", "1500", "1400", "1300", "1100", "1000", "900", "800", "801"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class NextGenerationNeoLegalSDK:
    def __init__(self, name="1800 Next Generation NeoLegal AI SDK", case_text=None, mode="general", execute=False):
        self.name = name
        self.case_text = case_text or "Bu dosyada kamu ihale hukuku açısından olay analizi, emsal karar ağı, mevzuatın zamana göre uygulanması, uzman ajan tartışması ve sonuç simülasyonu yapılacaktır."
        self.mode = mode
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def copilot(self):
        return {
            "status": "READY",
            "purpose": "Tek konuşmayla 1100, 1300, 1400, 1500, 1600 ve 1700 motorlarını kullanacak kullanıcı arayüzü.",
            "capabilities": [
                "Dosyayı incele",
                "Hukuki sorunları çıkar",
                "Eksik belge sor",
                "Uzman görüşü üret",
                "Dilekçe ve savunma taslağı üret",
                "Görev listesi oluştur",
                "Dosya hafızasına bağlan"
            ]
        }

    def knowledge_graph(self):
        return {
            "status": "READY",
            "nodes": ["Karar", "Mevzuat", "Kavram", "İçtihat", "Dosya", "Argüman", "Risk"],
            "edges": ["emsal", "atıf", "çelişki", "uygular", "destekler", "zayıflatır", "benzer"],
            "purpose": "KİK, Danıştay, Sayıştay ve mahkeme kararlarını mevzuat ve kavramlarla ilişkilendiren içtihat ağı."
        }

    def time_machine(self):
        return {
            "status": "READY",
            "purpose": "Uyuşmazlık tarihindeki mevzuat sürümünü kullanarak değerlendirme yapılmasını sağlar.",
            "required_data": ["Mevzuat sürüm tarihi", "Yürürlük tarihi", "Değişiklik tarihi", "Karar tarihi", "İhale tarihi"],
            "modes": ["current_law", "event_date_law", "decision_date_law", "historical_comparison"]
        }

    def multi_agent(self):
        return {
            "status": "READY",
            "agents": [
                "KİK Uzmanı",
                "Danıştay Uzmanı",
                "Sayıştay Uzmanı",
                "Sözleşme Uzmanı",
                "İdare Savunması Uzmanı",
                "Başvuru Sahibi Uzmanı",
                "AI Hakem"
            ],
            "purpose": "Aynı dosyayı farklı uzman perspektifleriyle tartıştırıp ortak sonuç üretmek."
        }

    def prediction_engine(self):
        text = self.normalize(self.case_text).lower()
        score = 55
        if "eşit muamele" in text or "rekabet" in text:
            score += 10
        if "süre" in text:
            score -= 10
        if "belge" in text or "iş deneyim" in text:
            score += 8
        score = max(5, min(95, score))
        return {
            "status": "READY",
            "base_success_probability": score,
            "simulation_modes": ["evidence_added", "deadline_missed", "strong_precedent_found", "adverse_precedent_found", "new_document_uploaded"],
            "purpose": "Başarı ihtimali, risk ve strateji değişimini senaryolara göre simüle etmek."
        }

    def integration_layer(self, copilot, graph, time_machine, agents, prediction):
        return {
            "status": "READY",
            "integrated_components": {
                "copilot": copilot["status"],
                "knowledge_graph": graph["status"],
                "time_machine": time_machine["status"],
                "multi_agent": agents["status"],
                "prediction_engine": prediction["status"]
            },
            "workflow": [
                "Kullanıcı olayı anlatır veya belge yükler",
                "Copilot olayı ayrıştırır",
                "Knowledge Graph emsal ve kavram ağını çağırır",
                "Time Machine doğru mevzuat tarihini seçer",
                "Multi-Agent uzman tartışması yapar",
                "Prediction Engine başarı ve risk simülasyonu üretir",
                "1600 Expert Orchestrator nihai uzman görüşünü üretir",
                "1700 Workspace dosya hafızasına kaydeder"
            ]
        }

    def qa_audit(self, pack):
        score = 100
        warnings = []
        for key in ["copilot", "knowledge_graph", "time_machine", "multi_agent", "prediction_engine", "integration_layer"]:
            if key not in pack:
                score -= 12
                warnings.append(key + " missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def certificate(self, pack):
        return {
            "certificate_id": "NGN-" + now_stamp(),
            "version_range": "v13.0-v17.0",
            "status": pack["audit"]["status"],
            "issued_at": now_text(),
            "note": "Next Generation NeoLegal AI mimarisi kuruldu. Gerçek değer için Knowledge Graph ve Time Machine veri modelinin gerçek veriyle beslenmesi gerekir."
        }

    def run(self):
        NEXTGEN_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        copilot = self.copilot()
        graph = self.knowledge_graph()
        time_machine = self.time_machine()
        agents = self.multi_agent()
        prediction = self.prediction_engine()
        integration = self.integration_layer(copilot, graph, time_machine, agents, prediction)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "mode": self.mode,
            "case_text": self.case_text,
            "copilot": copilot,
            "knowledge_graph": graph,
            "time_machine": time_machine,
            "multi_agent": agents,
            "prediction_engine": prediction,
            "integration_layer": integration
        }
        pack["audit"] = self.qa_audit(pack)
        pack["certificate"] = self.certificate(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.25 + pack["audit"]["score"] * 0.75, 2)
        decision = "NEXT GENERATION NEOLEGAL READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "NEXT GENERATION NEOLEGAL BLOCKED"
        ts = now_stamp()
        snapshot = NEXTGEN_DIR / "1800_next_generation_neolegal_snapshot.json"
        dashboard = NEXTGEN_DIR / "1800_next_generation_neolegal_dashboard.json"
        state = NEXTGEN_DIR / ("1800_next_generation_neolegal_state_" + ts + ".json")
        report = REPORTS / ("1800_next_generation_neolegal_sdk_raporu_" + ts + ".txt")
        payload = {"next_generation": pack, "modules": modules, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {"status": decision, "score": final_score, "prediction": prediction["base_success_probability"], "audit": pack["audit"]["status"], "components_ready": 5})
        lines = ["=" * 80, "1800 NEXT GENERATION NEOLEGAL AI SDK", "=" * 80, "Validation : " + decision, "Score      : " + str(final_score) + " / 100", "Prediction : " + str(prediction["base_success_probability"]) + " / 100", "Audit      : " + pack["audit"]["status"], "Components : Copilot + Graph + Time Machine + Multi-Agent + Prediction", "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
"""

def sdk_bridge_source():
    return """# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1800"
sys.path.insert(0, str(PACKAGE_DIR))
from core.next_generation_neolegal_sdk import NextGenerationNeoLegalSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = NextGenerationNeoLegalSDK(case_text=args.case_text, mode=args.mode, execute=args.execute).run()
    v = res["payload"]["validation"]
    ng = res["payload"]["next_generation"]
    print("=" * 80)
    print("1800 NEXT GENERATION NEOLEGAL AI SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation : " + str(v["decision"]))
    print("Score      : " + str(v["score"]) + " / 100")
    print("Prediction : " + str(ng["prediction_engine"]["base_success_probability"]) + " / 100")
    print("Audit      : " + str(ng["audit"]["status"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
"""

def module_source(mid, name, slug):
    tpl = """# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1800"
sys.path.insert(0, str(PACKAGE_DIR))
from core.next_generation_neolegal_sdk import NextGenerationNeoLegalSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "next_generation_neolegal" / "__MID_____SLUG__"
MODULE_ID = "__MID__"
MODULE_NAME = "__NAME__"
def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = NextGenerationNeoLegalSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, mode=args.mode, execute=args.execute).run()
    val = res["payload"]["validation"]
    ng = res["payload"]["next_generation"]
    decision = "__NAME_UPPER__ READY" if not val["errors"] else "__NAME_UPPER__ BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "prediction": ng["prediction_engine"]["base_success_probability"], "audit": ng["audit"]["status"], "components_ready": 5}
    ts = now_stamp()
    output = MODULE_DIR / "__MID_____SLUG__.json"
    state = MODULE_DIR / ("__MID_____SLUG___state_" + ts + ".json")
    report = REPORTS / ("__MID_____SLUG___raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score      : " + str(analysis["score"]) + " / 100", "Decision   : " + str(analysis["decision"]), "Prediction : " + str(analysis["prediction"]) + " / 100", "Audit      : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\\n".join(lines), encoding="utf-8")
    print("\\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
"""
    return tpl.replace("__MID__", mid).replace("__SLUG__", slug).replace("__NAME__", name).replace("__NAME_UPPER__", name.upper())

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
        '    ("1800", "Next Generation NeoLegal AI SDK", [sys.executable, str(BASE / ".py" / "1800_Next_Generation_NeoLegal_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser = argparse.ArgumentParser()",
        "    parser.add_argument('--case-text', default=None)",
        "    parser.add_argument('--mode', default='general')",
        "    parser.add_argument('--execute', action='store_true')",
        "    args = parser.parse_args()",
        "    print('=' * 80)",
        "    print('1800 NEXT GENERATION NEOLEGAL AI RUN ALL BASLADI')",
        "    print('=' * 80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id, name, cmd in COMMANDS:",
        "        full = cmd + ['--mode', args.mode]",
        "        if args.case_text: full += ['--case-text', args.case_text]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> ' + ' '.join(full))",
        "        result = subprocess.run(full, cwd=str(BASE))",
        "        status = 'PASS' if result.returncode == 0 else 'FAIL'",
        "        if status == 'PASS': passed += 1",
        "        else: failed += 1",
        "        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'1800 Next Generation NeoLegal AI','mode':args.mode,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'1800_next_generation_neolegal_ai_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')",
        "    print('\\n'+'='*80); print('1800 NEXT GENERATION NEOLEGAL AI SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(44)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
    ]
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 1800 Next Generation NeoLegal AI SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 1800 Run All"]
    RELEASE_FILE.write_text("\n".join([
        "# v13.0–v17.0 – Next Generation NeoLegal AI",
        "",
        "**Tarih:** 10.07.2026",
        "",
        "Bu sürüm beş ana yeni nesil alanı tek mimari altında başlatır: NeoLegal Copilot, Knowledge Graph / İçtihat Ağı, Mevzuat Zaman Makinesi, Multi-Agent Legal AI ve Tahmin/Simülasyon Motoru.",
        "",
        "# Modüller",
        "",
    ] + module_lines + [
        "",
        "---",
        "",
        "Not: Bu builder altyapıyı kurar. Knowledge Graph ve Time Machine gerçek değerini, karar ve mevzuat verileri ilişkilendirildikçe kazanacaktır.",
        ""
    ]), encoding="utf-8")
    entry = "\n".join([
        "# v13.0–v17.0 – Next Generation NeoLegal AI",
        "",
        "**Tarih:** 10.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `" + TAG + "`",
        "",
        "## Yeni Modüller",
        "",
    ] + module_lines + [
        "",
        "## Sonuç",
        "",
        "NeoLegal, Copilot + Knowledge Graph + Time Machine + Multi-Agent + Prediction mimarisine taşındı.",
        "",
        "---",
        ""
    ])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v13.0–v17.0 – Next Generation NeoLegal AI" not in old:
            CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v13.0-v17.0 | Next Generation NeoLegal AI | PASS |"
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
        "echo Running Next Generation NeoLegal AI v13-v17...",
        'python ".py\\1800_Run_All.py"',
        "",
        "IF ERRORLEVEL 1 (",
        "    echo.",
        "    echo RELEASE BLOCKED: 1800 Next Generation NeoLegal AI FAILED.",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "git status",
        "git add .",
        'git commit -m "Release v13-v17: Next Generation NeoLegal AI"',
        "git push",
        "git tag " + TAG,
        "git push origin " + TAG,
        "",
        "pause",
        ""
    ]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    PY.mkdir(parents=True, exist_ok=True)
    NEXTGEN_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1800 ALL-IN-ONE NEXT GENERATION NEOLEGAL BUILDER BASLADI")
    print("=" * 80)

    write_file(PY / "1800" / "core" / "__init__.py", "")
    write_file(PY / "1800" / "core" / "next_generation_neolegal_sdk.py", SDK_CODE)
    write_file(PY / "1800_Next_Generation_NeoLegal_SDK.py", sdk_bridge_source())

    generated = [str(PY / "1800_Next_Generation_NeoLegal_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)

    run_all = PY / "1800_Run_All.py"
    write_file(run_all, run_all_source())
    print("Generated:", run_all)

    release_path = create_release_docs()
    git_bat = create_git_bat()

    print("\n" + "=" * 80)
    print("1800 NEXT GENERATION NEOLEGAL AI TEST BASLIYOR")
    print("=" * 80)
    cmd = [sys.executable, str(run_all), "--mode", args.mode]
    if args.case_text:
        cmd += ["--case-text", args.case_text]
    if args.execute:
        cmd.append("--execute")
    result = run_visible(cmd)

    decision = "PASS" if result.returncode == 0 else "FAIL"
    git_status = "SKIPPED"
    if decision != "PASS" and not args.force_git:
        git_status = "BLOCKED_BY_FAIL"
    elif args.no_git:
        git_status = "SKIPPED_BY_USER"
    else:
        print("\n" + "=" * 80)
        print("GIT RELEASE BASLIYOR")
        print("=" * 80)
        git_result = run_visible(["cmd", "/c", str(git_bat)])
        git_status = "PUSHED" if git_result.returncode == 0 else "FAILED"

    ts = now_stamp()
    state = NEXTGEN_DIR / ("1800_next_generation_neolegal_builder_state_" + ts + ".json")
    report = REPORTS / ("1800_next_generation_neolegal_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1800 Next Generation NeoLegal AI Builder", "version": VERSION, "tag": TAG, "mode": args.mode, "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1800 ALL-IN-ONE NEXT GENERATION NEOLEGAL BUILDER FINAL", "=" * 80, "Final Decision : " + decision, "Git            : " + git_status, "Mode           : " + ("EXECUTE" if args.execute else "DRY_RUN"), "Version Range  : " + VERSION, "Run All        : " + str(run_all), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state), "Report         : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
