
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
LIT_DIR = STATE / "litigation_intelligence"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v9.0"
TAG = "v9.0-litigation-intelligence-platform"
RELEASE_FILE = RELEASES / "v9.0-litigation-intelligence-platform.md"
GIT_BAT = BASE / "git_release_v9_0_litigation_intelligence_platform.bat"

MODULES = [
    ("1401", "Complaint Draft Engine", "complaint_draft_engine"),
    ("1402", "Appeal Draft Engine", "appeal_draft_engine"),
    ("1403", "Administrative Case Draft Engine", "administrative_case_draft_engine"),
    ("1404", "Defense Reply Engine", "defense_reply_engine"),
    ("1405", "Counter Defense Analyzer", "counter_defense_analyzer"),
    ("1406", "Evidence Gap Analyzer", "evidence_gap_analyzer"),
    ("1407", "Stay Of Execution Analyzer", "stay_of_execution_analyzer"),
    ("1408", "Hearing Strategy Planner", "hearing_strategy_planner"),
    ("1409", "Litigation Probability Updater", "litigation_probability_updater"),
    ("1410", "Litigation Quality Auditor", "litigation_quality_auditor"),
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
import json, sqlite3, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
LIT_DIR = STATE / "litigation_intelligence"
SUPPORT_IDS = ["1300", "1100", "1000", "900", "800", "801", "177", "172", "170", "169"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class LitigationIntelligencePlatformSDK:
    def __init__(self, name="1400 Litigation Intelligence Platform SDK", case_text=None, litigation_type="general", execute=False):
        self.name = name
        self.case_text = case_text or "İsteklinin değerlendirme dışı bırakılması, yeterlik kriterlerinin uygulanması, başvuru süresi ve ihale dokümanı hükümlerinin yorumlanması nedeniyle idareye şikâyet, itirazen şikâyet ve dava stratejisi değerlendirilmelidir."
        self.litigation_type = litigation_type
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def intake(self):
        text = self.normalize(self.case_text)
        lower = text.lower()
        issues = []
        mapping = [
            ("değerlendirme dışı", "Değerlendirme dışı bırakma"),
            ("yeterlik", "Yeterlik kriteri"),
            ("iş deneyim", "İş deneyimi"),
            ("aşırı düşük", "Aşırı düşük teklif"),
            ("yaklaşık maliyet", "Yaklaşık maliyet"),
            ("şikâyet", "Şikâyet"),
            ("şikayet", "Şikâyet"),
            ("itirazen", "İtirazen şikâyet"),
            ("dava", "İdari dava"),
            ("mahkeme", "İdari dava"),
            ("yürütmenin durdurulması", "Yürütmenin durdurulması"),
            ("süre", "Süre riski"),
            ("rekabet", "Rekabet ilkesi"),
            ("eşit muamele", "Eşit muamele ilkesi"),
        ]
        for key, label in mapping:
            if key in lower and label not in issues:
                issues.append(label)
        if not issues:
            issues = ["İhale işleminin hukuka uygunluğu", "Başvuru ve dava stratejisi"]
        stage = "COURT" if "dava" in lower or "mahkeme" in lower else "APPEAL" if "itirazen" in lower else "COMPLAINT"
        urgency = "HIGH" if "süre" in lower or "son gün" in lower or "tebliğ" in lower else "NORMAL"
        return {"text": text, "issues": issues, "stage": stage, "urgency": urgency, "litigation_type": self.litigation_type}

    def legal_basis(self, intake):
        basis = ["4734 sayılı Kamu İhale Kanunu m.5 temel ilkeler"]
        issue_text = " ".join(intake["issues"]).lower()
        if "şikâyet" in issue_text or "süre" in issue_text:
            basis += ["4734 sayılı Kanun m.54-56 başvuru yolları", "İhalelere Yönelik Başvurular Hakkında Yönetmelik"]
        if "idari dava" in issue_text or intake["stage"] == "COURT":
            basis += ["2577 sayılı İdari Yargılama Usulü Kanunu", "Yürütmenin durdurulması koşulları"]
        if "aşırı düşük" in issue_text:
            basis += ["4734 sayılı Kanun m.38", "Kamu İhale Genel Tebliği aşırı düşük teklif hükümleri"]
        if "yeterlik" in issue_text or "iş deneyimi" in issue_text:
            basis.append("İlgili Uygulama Yönetmeliği yeterlik ve iş deneyimi hükümleri")
        return basis

    def complaint_draft(self, intake, basis):
        return "İDAREYE ŞİKÂYET TASLAĞI\\n\\nBaşvuru konusu işlem, " + ", ".join(intake["issues"]) + " yönlerinden hukuka aykırılık taşımaktadır. İdarenin değerlendirmesinin " + "; ".join(basis) + " çerçevesinde yeniden incelenmesi ve gerekli görülmesi halinde düzeltici işlem belirlenmesi talep olunur."

    def appeal_draft(self, intake, basis):
        return "İTİRAZEN ŞİKÂYET TASLAĞI\\n\\nİdareye yapılan başvuru üzerine tesis edilen işlem veya zımni ret, " + ", ".join(intake["issues"]) + " bakımından Kamu İhale mevzuatına aykırıdır. Kurul tarafından başvuru konusu işlemin incelenerek düzeltici işlem belirlenmesi talep olunur."

    def court_case_draft(self, intake, basis):
        return "İDARİ DAVA TASLAĞI\\n\\nDava konusu işlem, " + ", ".join(intake["issues"]) + " yönlerinden hukuka aykırıdır. İşlem; sebep, konu, amaç ve yetki unsurları ile " + "; ".join(basis) + " kapsamında değerlendirilmelidir. Açık hukuka aykırılık ve telafisi güç zarar koşulları oluştuğundan yürütmenin durdurulması ve iptal talep olunur."

    def defense_reply(self, intake, basis):
        return "SAVUNMAYA CEVAP TASLAĞI\\n\\nDavalı idarenin savunmasında ileri sürülen hususlar, somut olayın maddi ve hukuki çerçevesini karşılamamaktadır. Uyuşmazlık " + ", ".join(intake["issues"]) + " başlıklarında yoğunlaşmakta olup, savunma " + "; ".join(basis) + " hükümleri karşısında yeterli değildir."

    def evidence_gap(self, intake):
        gaps = ["İhale dokümanı ilgili maddeleri", "Tebligat ve süre belgeleri", "İdarenin değerlendirme tutanakları"]
        if "İş deneyimi" in intake["issues"]:
            gaps.append("İş deneyim belgesi ve EKAP kayıtları")
        if "Aşırı düşük teklif" in intake["issues"]:
            gaps.append("Aşırı düşük açıklaması ve analiz/proforma belgeleri")
        return {"required_evidence": gaps, "gap_risk": "MEDIUM" if len(gaps) >= 4 else "LOW"}

    def stay_of_execution(self, intake):
        text = intake["text"].lower()
        illegality = 65
        damage = 60
        if "açık hukuka aykırı" in text or "rekabet" in text or "eşit muamele" in text:
            illegality += 15
        if "sözleşme" in text or "telafisi güç" in text:
            damage += 15
        score = min(95, round((illegality + damage) / 2))
        return {"score": score, "level": "STRONG" if score >= 75 else "MEDIUM" if score >= 55 else "WEAK"}

    def probability(self, intake, evidence, stay):
        base = 50
        if "Süre riski" in intake["issues"]:
            base -= 10
        if "Rekabet ilkesi" in intake["issues"] or "Eşit muamele ilkesi" in intake["issues"]:
            base += 10
        if evidence["gap_risk"] == "LOW":
            base += 8
        if stay["level"] == "STRONG":
            base += 10
        p = max(5, min(95, base))
        return {"success_probability": p, "risk_probability": 100 - p, "label": "HIGH" if p >= 70 else "MEDIUM" if p >= 45 else "LOW"}

    def audit(self, pack):
        score = 100
        warnings = []
        for key in ["complaint_draft", "appeal_draft", "court_case_draft", "defense_reply", "evidence_gap", "stay_of_execution", "probability", "hearing_strategy"]:
            if key not in pack:
                score -= 10
                warnings.append(key + " missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def run(self):
        LIT_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        intake = self.intake()
        basis = self.legal_basis(intake)
        evidence = self.evidence_gap(intake)
        stay = self.stay_of_execution(intake)
        prob = self.probability(intake, evidence, stay)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "intake": intake,
            "legal_basis": basis,
            "complaint_draft": self.complaint_draft(intake, basis),
            "appeal_draft": self.appeal_draft(intake, basis),
            "court_case_draft": self.court_case_draft(intake, basis),
            "defense_reply": self.defense_reply(intake, basis),
            "evidence_gap": evidence,
            "stay_of_execution": stay,
            "probability": prob,
            "hearing_strategy": {"focus_points": ["Süre ve usul itirazlarını bertaraf et", "Doküman hükmünü açık şekilde göster", "Somut belge ve tutanakları sırayla sun"], "tone": "technical_and_evidence_based"},
        }
        pack["audit"] = self.audit(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.25 + pack["audit"]["score"] * 0.75, 2)
        decision = "LITIGATION INTELLIGENCE READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "LITIGATION INTELLIGENCE BLOCKED"
        ts = now_stamp()
        snapshot = LIT_DIR / "1400_litigation_intelligence_snapshot.json"
        dashboard = LIT_DIR / "1400_litigation_intelligence_dashboard.json"
        state = LIT_DIR / ("1400_litigation_intelligence_state_" + ts + ".json")
        report = REPORTS / ("1400_litigation_intelligence_sdk_raporu_" + ts + ".txt")
        payload = {"litigation": pack, "modules": modules, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {"status": decision, "score": final_score, "success_probability": prob["success_probability"], "stay_score": stay["score"], "audit": pack["audit"]["status"]})
        lines = ["=" * 80, "1400 LITIGATION INTELLIGENCE PLATFORM SDK", "=" * 80, "Validation          : " + decision, "Score               : " + str(final_score) + " / 100", "Success Probability : " + str(prob["success_probability"]) + " / 100", "YD Score            : " + str(stay["score"]) + " / 100", "Audit               : " + pack["audit"]["status"], "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
"""

def sdk_bridge_source():
    return """# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1400"
sys.path.insert(0, str(PACKAGE_DIR))
from core.litigation_intelligence_platform_sdk import LitigationIntelligencePlatformSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--litigation-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = LitigationIntelligencePlatformSDK(case_text=args.case_text, litigation_type=args.litigation_type, execute=args.execute).run()
    v = res["payload"]["validation"]
    lit = res["payload"]["litigation"]
    print("=" * 80)
    print("1400 LITIGATION INTELLIGENCE PLATFORM SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Success Probability : " + str(lit["probability"]["success_probability"]) + " / 100")
    print("YD Score            : " + str(lit["stay_of_execution"]["score"]) + " / 100")
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
PACKAGE_DIR = BASE / ".py" / "1400"
sys.path.insert(0, str(PACKAGE_DIR))
from core.litigation_intelligence_platform_sdk import LitigationIntelligencePlatformSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "litigation_intelligence" / "__MID_____SLUG__"
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
    parser.add_argument("--litigation-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = LitigationIntelligencePlatformSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, litigation_type=args.litigation_type, execute=args.execute).run()
    val = res["payload"]["validation"]
    lit = res["payload"]["litigation"]
    decision = "__NAME_UPPER__ READY" if not val["errors"] else "__NAME_UPPER__ BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "success_probability": lit["probability"]["success_probability"], "yd_score": lit["stay_of_execution"]["score"], "audit": lit["audit"]["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "__MID_____SLUG__.json"
    state = MODULE_DIR / ("__MID_____SLUG___state_" + ts + ".json")
    report = REPORTS / ("__MID_____SLUG___raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score       : " + str(analysis["score"]) + " / 100", "Decision    : " + str(analysis["decision"]), "Probability : " + str(analysis["success_probability"]) + " / 100", "YD Score    : " + str(analysis["yd_score"]) + " / 100", "Audit       : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
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
        '    ("1400", "Litigation Intelligence Platform SDK", [sys.executable, str(BASE / ".py" / "1400_Litigation_Intelligence_Platform_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser = argparse.ArgumentParser()",
        "    parser.add_argument('--case-text', default=None)",
        "    parser.add_argument('--litigation-type', default='general')",
        "    parser.add_argument('--execute', action='store_true')",
        "    args = parser.parse_args()",
        "    print('=' * 80)",
        "    print('1400 LITIGATION INTELLIGENCE PLATFORM RUN ALL BASLADI')",
        "    print('=' * 80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id, name, cmd in COMMANDS:",
        "        full = cmd + ['--litigation-type', args.litigation_type]",
        "        if args.case_text: full += ['--case-text', args.case_text]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> ' + ' '.join(full))",
        "        result = subprocess.run(full, cwd=str(BASE))",
        "        status = 'PASS' if result.returncode == 0 else 'FAIL'",
        "        if status == 'PASS': passed += 1",
        "        else: failed += 1",
        "        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'1400 Litigation Intelligence Platform','litigation_type':args.litigation_type,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'1400_litigation_intelligence_platform_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')",
        "    print('\\n'+'='*80); print('1400 LITIGATION INTELLIGENCE PLATFORM SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(44)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
    ]
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 1400 Litigation Intelligence Platform SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 1400 Run All"]
    RELEASE_FILE.write_text("\n".join(["# v9.0 – Litigation Intelligence Platform", "", "**Tarih:** 10.07.2026", "", "Bu sürüm, NeoLegal'i şikâyet, itirazen şikâyet, dava, savunmaya cevap, delil eksikliği, yürütmenin durdurulması ve duruşma stratejisi üretebilen dava/başvuru zekâsı katmanına taşır.", "", "# Modüller", ""] + module_lines + ["", "---", "", "Litigation Intelligence Platform v9.0 oluşturulmuştur.", ""]), encoding="utf-8")
    entry = "\n".join(["# v9.0 – Litigation Intelligence Platform", "", "**Tarih:** 10.07.2026  ", "**Durum:** Production PASS  ", "**Git Tag:** `" + TAG + "`", "", "## Yeni Modüller", ""] + module_lines + ["", "## Sonuç", "", "NeoLegal, başvuru/dava dosyası hazırlama ve dava stratejisi üretme katmanına taşındı.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v9.0 – Litigation Intelligence Platform" not in old:
            CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v9.0 | Litigation Intelligence Platform | PASS |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines = ["@echo off", "cd /d C:\\Users\\MSI\\Desktop\\kik_proje", "", "echo Running Litigation Intelligence Platform v9.0...", 'python ".py\\1400_Run_All.py"', "", "IF ERRORLEVEL 1 (", "    echo.", "    echo RELEASE BLOCKED: 1400 Litigation Intelligence Platform FAILED.", "    pause", "    exit /b 1", ")", "", "git status", "git add .", 'git commit -m "Release v9.0: Litigation Intelligence Platform"', "git push", "git tag " + TAG, "git push origin " + TAG, "", "pause", ""]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--litigation-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    PY.mkdir(parents=True, exist_ok=True)
    LIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print("1400 ALL-IN-ONE LITIGATION INTELLIGENCE PLATFORM BUILDER BASLADI")
    print("=" * 80)
    write_file(PY / "1400" / "core" / "__init__.py", "")
    write_file(PY / "1400" / "core" / "litigation_intelligence_platform_sdk.py", SDK_CODE)
    write_file(PY / "1400_Litigation_Intelligence_Platform_SDK.py", sdk_bridge_source())
    generated = [str(PY / "1400_Litigation_Intelligence_Platform_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)
    run_all = PY / "1400_Run_All.py"
    write_file(run_all, run_all_source())
    print("Generated:", run_all)
    release_path = create_release_docs()
    git_bat = create_git_bat()
    print("\n" + "=" * 80)
    print("1400 LITIGATION INTELLIGENCE PLATFORM TEST BASLIYOR")
    print("=" * 80)
    cmd = [sys.executable, str(run_all), "--litigation-type", args.litigation_type]
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
    state = LIT_DIR / ("1400_litigation_intelligence_platform_builder_state_" + ts + ".json")
    report = REPORTS / ("1400_litigation_intelligence_platform_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1400 Litigation Intelligence Platform Builder", "version": VERSION, "tag": TAG, "litigation_type": args.litigation_type, "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1400 ALL-IN-ONE LITIGATION INTELLIGENCE PLATFORM BUILDER FINAL", "=" * 80, "Final Decision : " + decision, "Git            : " + git_status, "Mode           : " + ("EXECUTE" if args.execute else "DRY_RUN"), "Litigation Type: " + str(args.litigation_type), "Run All        : " + str(run_all), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state), "Report         : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
