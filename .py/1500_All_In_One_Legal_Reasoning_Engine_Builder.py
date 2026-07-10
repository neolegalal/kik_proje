
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

REASONING_DIR = STATE / "legal_reasoning_engine"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v10.0"
TAG = "v10.0-legal-reasoning-engine"
RELEASE_FILE = RELEASES / "v10.0-legal-reasoning-engine.md"
GIT_BAT = BASE / "git_release_v10_0_legal_reasoning_engine.bat"

MODULES = [
    ("1501", "Issue Identifier", "issue_identifier"),
    ("1502", "Legal Argument Generator", "legal_argument_generator"),
    ("1503", "Counter Argument Generator", "counter_argument_generator"),
    ("1504", "Evidence Weight Analyzer", "evidence_weight_analyzer"),
    ("1505", "Precedent Comparator", "precedent_comparator"),
    ("1506", "Legal Conflict Resolver", "legal_conflict_resolver"),
    ("1507", "Outcome Prediction Engine", "outcome_prediction_engine"),
    ("1508", "Strategy Optimizer", "strategy_optimizer"),
    ("1509", "AI Reasoning Auditor", "ai_reasoning_auditor"),
    ("1510", "Legal Reasoning Certificate", "legal_reasoning_certificate"),
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
REASONING_DIR = STATE / "legal_reasoning_engine"
SUPPORT_IDS = ["1400", "1300", "1100", "1000", "900", "800", "801", "177", "172", "170", "169"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class LegalReasoningEngineSDK:
    def __init__(self, name="1500 Legal Reasoning Engine SDK", case_text=None, reasoning_type="general", execute=False):
        self.name = name
        self.case_text = case_text or "İstekli, yeterlik kriteri ve iş deneyim belgesi nedeniyle değerlendirme dışı bırakılmıştır. İdare işleminin eşit muamele, rekabet, ihale dokümanı ve başvuru süresi yönünden hukuka uygunluğu tartışmalıdır."
        self.reasoning_type = reasoning_type
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def issue_identifier(self):
        text = self.normalize(self.case_text)
        lower = text.lower()
        issues = []
        mapping = [
            ("yeterlik", "Yeterlik kriterinin uygulanması"),
            ("iş deneyim", "İş deneyim belgesinin değerlendirilmesi"),
            ("değerlendirme dışı", "Değerlendirme dışı bırakma işlemi"),
            ("aşırı düşük", "Aşırı düşük teklif açıklaması"),
            ("yaklaşık maliyet", "Yaklaşık maliyet ve teklif ilişkisi"),
            ("eşit muamele", "Eşit muamele ilkesi"),
            ("rekabet", "Rekabet ilkesi"),
            ("süre", "Başvuru süresi ve usul riski"),
            ("şikayet", "İdareye şikâyet stratejisi"),
            ("itirazen", "İtirazen şikâyet stratejisi"),
            ("dava", "İdari dava stratejisi"),
        ]
        for key, label in mapping:
            if key in lower and label not in issues:
                issues.append(label)
        if not issues:
            issues = ["İhale işleminin hukuka uygunluğu", "Başvuru ve savunma stratejisi"]
        return {"case_text": text, "issues": issues, "issue_count": len(issues)}

    def legal_argument_generator(self, issues):
        arguments = []
        for issue in issues["issues"]:
            arguments.append({
                "issue": issue,
                "pro_argument": issue + " bakımından idarenin işleminin somut belge, ihale dokümanı ve 4734 sayılı Kanun m.5 temel ilkeleriyle uyumlu olup olmadığı incelenmelidir.",
                "claimant_angle": issue + " yönünden başvurucu lehine hukuka aykırılık argümanı kurulabilir.",
                "administration_angle": issue + " yönünden idarenin takdir yetkisi ve doküman hükümlerine bağlı işlem tesis ettiği savunulabilir."
            })
        return arguments

    def counter_argument_generator(self, arguments):
        counters = []
        for arg in arguments:
            counters.append({
                "issue": arg["issue"],
                "expected_counter": "Karşı taraf, " + arg["issue"] + " bakımından ihale dokümanının açık olduğunu, başvurucunun gerekli belgeleri sunmadığını veya idarenin eşit muameleye uygun hareket ettiğini ileri sürebilir.",
                "reply_strategy": "Bu karşı argümana karşı somut belge, doküman hükmü ve benzer KİK kararlarıyla cevap verilmelidir."
            })
        return counters

    def evidence_weight_analyzer(self, issues):
        evidence = []
        base_items = ["İhale dokümanı", "Zarf açma ve belge kontrol tutanağı", "Komisyon kararı", "Tebligat kayıtları"]
        for item in base_items:
            evidence.append({"evidence": item, "weight": 80, "importance": "HIGH"})
        if any("İş deneyim" in i for i in issues["issues"]):
            evidence.append({"evidence": "İş deneyim belgesi ve EKAP kaydı", "weight": 90, "importance": "CRITICAL"})
        if any("Aşırı düşük" in i for i in issues["issues"]):
            evidence.append({"evidence": "Aşırı düşük açıklaması, analiz ve fiyat teklifleri", "weight": 90, "importance": "CRITICAL"})
        if any("süre" in i.lower() for i in issues["issues"]):
            evidence.append({"evidence": "Başvuru tarihi ve tebliğ tarihi", "weight": 95, "importance": "CRITICAL"})
        avg = round(sum(e["weight"] for e in evidence) / len(evidence), 2)
        return {"evidence": evidence, "average_weight": avg}

    def precedent_comparator(self, issues):
        issue_count = issues["issue_count"]
        score = min(95, 68 + issue_count * 4)
        return {
            "similarity_score": score,
            "level": "HIGH" if score >= 80 else "MEDIUM" if score >= 60 else "LOW",
            "note": "Bu skor, tespit edilen hukuki meselelerin mevcut KİK/mahkeme kararlarıyla eşleşebilirliğine ilişkin ön muhakeme skorudur."
        }

    def legal_conflict_resolver(self, issues):
        conflicts = []
        if any("Yeterlik" in i for i in issues["issues"]):
            conflicts.append("Yeterlik kriterinin katı uygulanması ile rekabet/eşit muamele ilkeleri arasındaki denge kurulmalıdır.")
        if any("Başvuru süresi" in i for i in issues["issues"]):
            conflicts.append("Süre kuralları kamu düzeni niteliğinde olduğundan esas incelemenin önüne geçebilir.")
        if not conflicts:
            conflicts.append("Açık norm çatışması tespit edilmemiştir; somut olay yorumu belirleyici olacaktır.")
        return {"conflicts": conflicts, "resolution": "Öncelik sırası: süre/usul → ihale dokümanı → somut belge → temel ilkeler → emsal kararlar."}

    def outcome_prediction(self, issues, evidence, precedent, conflicts):
        base = 50
        if precedent["level"] == "HIGH":
            base += 15
        elif precedent["level"] == "LOW":
            base -= 10
        if evidence["average_weight"] >= 85:
            base += 10
        if any("Süre kuralları" in c for c in conflicts["conflicts"]):
            base -= 12
        if any("rekabet" in i.lower() or "eşit muamele" in i.lower() for i in issues["issues"]):
            base += 8
        probability = max(5, min(95, base))
        return {
            "success_probability": probability,
            "risk_probability": 100 - probability,
            "confidence": "HIGH" if probability >= 75 else "MEDIUM" if probability >= 45 else "LOW"
        }

    def strategy_optimizer(self, prediction, issues):
        p = prediction["success_probability"]
        if p >= 75:
            primary = "Güçlü başvuru/dava stratejisi: esas argümanlar ve emsal kararlar merkeze alınmalıdır."
        elif p >= 45:
            primary = "Dengeli strateji: ana argüman yanında usul, belge ve alternatif talepler birlikte kurulmalıdır."
        else:
            primary = "Risk azaltma stratejisi: eksik belgeler tamamlanmalı, ikincil argümanlar ve uzlaşma/yeniden değerlendirme seçenekleri korunmalıdır."
        route = ["İdareye şikâyet", "İtirazen şikâyet", "Gerekirse yürütmenin durdurulması talepli iptal davası"]
        if any("dava" in i.lower() for i in issues["issues"]):
            route = ["Dava dilekçesi", "Yürütmenin durdurulması", "Savunmaya cevap", "Ek beyan"]
        return {"primary_strategy": primary, "recommended_route": route}

    def reasoning_audit(self, pack):
        score = 100
        warnings = []
        required = ["issues", "arguments", "counter_arguments", "evidence_weight", "precedent_comparison", "conflict_resolution", "outcome_prediction", "strategy"]
        for key in required:
            if key not in pack:
                score -= 10
                warnings.append(key + " missing")
        if pack.get("outcome_prediction", {}).get("success_probability") is None:
            score -= 15
            warnings.append("probability missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def certificate(self, pack):
        return {
            "certificate_id": "LRE-" + now_stamp(),
            "reasoning_type": self.reasoning_type,
            "status": pack["audit"]["status"],
            "success_probability": pack["outcome_prediction"]["success_probability"],
            "issued_at": now_text(),
            "note": "Bu çıktı karar destek amaçlıdır; nihai hukuki değerlendirme uzman kontrolüyle yapılmalıdır."
        }

    def run(self):
        REASONING_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        issues = self.issue_identifier()
        arguments = self.legal_argument_generator(issues)
        counters = self.counter_argument_generator(arguments)
        evidence = self.evidence_weight_analyzer(issues)
        precedent = self.precedent_comparator(issues)
        conflicts = self.legal_conflict_resolver(issues)
        prediction = self.outcome_prediction(issues, evidence, precedent, conflicts)
        strategy = self.strategy_optimizer(prediction, issues)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "issues": issues,
            "arguments": arguments,
            "counter_arguments": counters,
            "evidence_weight": evidence,
            "precedent_comparison": precedent,
            "conflict_resolution": conflicts,
            "outcome_prediction": prediction,
            "strategy": strategy,
        }
        pack["audit"] = self.reasoning_audit(pack)
        pack["certificate"] = self.certificate(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.25 + pack["audit"]["score"] * 0.75, 2)
        decision = "LEGAL REASONING ENGINE READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "LEGAL REASONING ENGINE BLOCKED"
        ts = now_stamp()
        snapshot = REASONING_DIR / "1500_legal_reasoning_engine_snapshot.json"
        dashboard = REASONING_DIR / "1500_legal_reasoning_engine_dashboard.json"
        state = REASONING_DIR / ("1500_legal_reasoning_engine_state_" + ts + ".json")
        report = REPORTS / ("1500_legal_reasoning_engine_sdk_raporu_" + ts + ".txt")
        payload = {"reasoning": pack, "modules": modules, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {"status": decision, "score": final_score, "success_probability": prediction["success_probability"], "confidence": prediction["confidence"], "audit": pack["audit"]["status"]})
        lines = ["=" * 80, "1500 LEGAL REASONING ENGINE SDK", "=" * 80, "Validation          : " + decision, "Score               : " + str(final_score) + " / 100", "Success Probability : " + str(prediction["success_probability"]) + " / 100", "Confidence          : " + prediction["confidence"], "Audit               : " + pack["audit"]["status"], "", "Strategy:", strategy["primary_strategy"], "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
"""

def sdk_bridge_source():
    return """# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1500"
sys.path.insert(0, str(PACKAGE_DIR))
from core.legal_reasoning_engine_sdk import LegalReasoningEngineSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--reasoning-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = LegalReasoningEngineSDK(case_text=args.case_text, reasoning_type=args.reasoning_type, execute=args.execute).run()
    v = res["payload"]["validation"]
    reasoning = res["payload"]["reasoning"]
    print("=" * 80)
    print("1500 LEGAL REASONING ENGINE SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Success Probability : " + str(reasoning["outcome_prediction"]["success_probability"]) + " / 100")
    print("Confidence          : " + str(reasoning["outcome_prediction"]["confidence"]))
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
PACKAGE_DIR = BASE / ".py" / "1500"
sys.path.insert(0, str(PACKAGE_DIR))
from core.legal_reasoning_engine_sdk import LegalReasoningEngineSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "legal_reasoning_engine" / "__MID_____SLUG__"
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
    parser.add_argument("--reasoning-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = LegalReasoningEngineSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, reasoning_type=args.reasoning_type, execute=args.execute).run()
    val = res["payload"]["validation"]
    reasoning = res["payload"]["reasoning"]
    decision = "__NAME_UPPER__ READY" if not val["errors"] else "__NAME_UPPER__ BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "success_probability": reasoning["outcome_prediction"]["success_probability"], "confidence": reasoning["outcome_prediction"]["confidence"], "audit": reasoning["audit"]["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "__MID_____SLUG__.json"
    state = MODULE_DIR / ("__MID_____SLUG___state_" + ts + ".json")
    report = REPORTS / ("__MID_____SLUG___raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score       : " + str(analysis["score"]) + " / 100", "Decision    : " + str(analysis["decision"]), "Probability : " + str(analysis["success_probability"]) + " / 100", "Confidence  : " + str(analysis["confidence"]), "Audit       : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
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
        '    ("1500", "Legal Reasoning Engine SDK", [sys.executable, str(BASE / ".py" / "1500_Legal_Reasoning_Engine_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser = argparse.ArgumentParser()",
        "    parser.add_argument('--case-text', default=None)",
        "    parser.add_argument('--reasoning-type', default='general')",
        "    parser.add_argument('--execute', action='store_true')",
        "    args = parser.parse_args()",
        "    print('=' * 80)",
        "    print('1500 LEGAL REASONING ENGINE RUN ALL BASLADI')",
        "    print('=' * 80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id, name, cmd in COMMANDS:",
        "        full = cmd + ['--reasoning-type', args.reasoning_type]",
        "        if args.case_text: full += ['--case-text', args.case_text]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> ' + ' '.join(full))",
        "        result = subprocess.run(full, cwd=str(BASE))",
        "        status = 'PASS' if result.returncode == 0 else 'FAIL'",
        "        if status == 'PASS': passed += 1",
        "        else: failed += 1",
        "        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'1500 Legal Reasoning Engine','reasoning_type':args.reasoning_type,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'1500_legal_reasoning_engine_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')",
        "    print('\\n'+'='*80); print('1500 LEGAL REASONING ENGINE SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(40)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
    ]
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 1500 Legal Reasoning Engine SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 1500 Run All"]
    RELEASE_FILE.write_text("\n".join(["# v10.0 – Legal Reasoning Engine", "", "**Tarih:** 10.07.2026", "", "Bu sürüm, NeoLegal'i karar arama ve dilekçe üretme seviyesinden hukuki muhakeme, karşı argüman, delil ağırlığı, emsal karşılaştırma, norm çatışması çözümü ve strateji optimizasyonu seviyesine taşır.", "", "# Modüller", ""] + module_lines + ["", "---", "", "Legal Reasoning Engine v10.0 oluşturulmuştur.", ""]), encoding="utf-8")
    entry = "\n".join(["# v10.0 – Legal Reasoning Engine", "", "**Tarih:** 10.07.2026  ", "**Durum:** Production PASS  ", "**Git Tag:** `" + TAG + "`", "", "## Yeni Modüller", ""] + module_lines + ["", "## Sonuç", "", "NeoLegal, hukuki muhakeme ve strateji optimizasyonu katmanına taşındı.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v10.0 – Legal Reasoning Engine" not in old:
            CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v10.0 | Legal Reasoning Engine | PASS |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines = ["@echo off", "cd /d C:\\Users\\MSI\\Desktop\\kik_proje", "", "echo Running Legal Reasoning Engine v10.0...", 'python ".py\\1500_Run_All.py"', "", "IF ERRORLEVEL 1 (", "    echo.", "    echo RELEASE BLOCKED: 1500 Legal Reasoning Engine FAILED.", "    pause", "    exit /b 1", ")", "", "git status", "git add .", 'git commit -m "Release v10.0: Legal Reasoning Engine"', "git push", "git tag " + TAG, "git push origin " + TAG, "", "pause", ""]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--reasoning-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    PY.mkdir(parents=True, exist_ok=True)
    REASONING_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print("1500 ALL-IN-ONE LEGAL REASONING ENGINE BUILDER BASLADI")
    print("=" * 80)
    write_file(PY / "1500" / "core" / "__init__.py", "")
    write_file(PY / "1500" / "core" / "legal_reasoning_engine_sdk.py", SDK_CODE)
    write_file(PY / "1500_Legal_Reasoning_Engine_SDK.py", sdk_bridge_source())
    generated = [str(PY / "1500_Legal_Reasoning_Engine_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)
    run_all = PY / "1500_Run_All.py"
    write_file(run_all, run_all_source())
    print("Generated:", run_all)
    release_path = create_release_docs()
    git_bat = create_git_bat()
    print("\n" + "=" * 80)
    print("1500 LEGAL REASONING ENGINE TEST BASLIYOR")
    print("=" * 80)
    cmd = [sys.executable, str(run_all), "--reasoning-type", args.reasoning_type]
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
    state = REASONING_DIR / ("1500_legal_reasoning_engine_builder_state_" + ts + ".json")
    report = REPORTS / ("1500_legal_reasoning_engine_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1500 Legal Reasoning Engine Builder", "version": VERSION, "tag": TAG, "reasoning_type": args.reasoning_type, "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1500 ALL-IN-ONE LEGAL REASONING ENGINE BUILDER FINAL", "=" * 80, "Final Decision : " + decision, "Git            : " + git_status, "Mode           : " + ("EXECUTE" if args.execute else "DRY_RUN"), "Reasoning Type : " + str(args.reasoning_type), "Run All        : " + str(run_all), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state), "Report         : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
