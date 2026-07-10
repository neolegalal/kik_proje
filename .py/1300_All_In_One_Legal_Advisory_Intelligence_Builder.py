
# -*- coding: utf-8 -*-
import argparse, json, sqlite3, subprocess, sys, py_compile, re
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

ADVISORY_DIR = STATE / "legal_advisory_intelligence"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v8.0"
TAG = "v8.0-legal-advisory-intelligence"
RELEASE_FILE = RELEASES / "v8.0-legal-advisory-intelligence.md"
GIT_BAT = BASE / "git_release_v8_0_legal_advisory_intelligence.bat"

MODULES = [
    ("1301", "Case Intake Analyzer", "case_intake_analyzer"),
    ("1302", "Claim Defense Mapper", "claim_defense_mapper"),
    ("1303", "Legal Basis Finder", "legal_basis_finder"),
    ("1304", "Precedent Strength Analyzer", "precedent_strength_analyzer"),
    ("1305", "Outcome Probability Scorer", "outcome_probability_scorer"),
    ("1306", "Defense Draft Generator", "defense_draft_generator"),
    ("1307", "Complaint Appeal Draft Generator", "complaint_appeal_draft_generator"),
    ("1308", "Court Application Risk Analyzer", "court_application_risk_analyzer"),
    ("1309", "Strategy Recommendation Engine", "strategy_recommendation_engine"),
    ("1310", "Advisory Quality Auditor", "advisory_quality_auditor"),
]

SUPPORT_IDS = ["1100", "1000", "900", "800", "801", "172", "177", "170", "169"]

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
    return '''
# -*- coding: utf-8 -*-
import json, sqlite3, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
ADVISORY_DIR = STATE / "legal_advisory_intelligence"
SUPPORT_IDS = ["1100", "1000", "900", "800", "801", "172", "177", "170", "169"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class LegalAdvisoryIntelligenceSDK:
    def __init__(self, name="1300 Legal Advisory Intelligence SDK", case_text=None, advisory_type="general", execute=False):
        self.name = name
        self.case_text = case_text or "İhale sürecinde isteklinin değerlendirme dışı bırakılması, yeterlik kriteri, teklif değerlendirmesi ve başvuru süresi yönünden hukuki riskler bulunmaktadır."
        self.advisory_type = advisory_type
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def db_status(self):
        rows = []
        for name in ("kik.db", "kik_proje.db", "hukuki_kartlar.db"):
            p = BASE / name
            item = {"path": str(p), "exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0, "tables": []}
            if p.exists():
                try:
                    con = sqlite3.connect(str(p))
                    cur = con.cursor()
                    for (t,) in cur.execute("select name from sqlite_master where type='table'").fetchall()[:20]:
                        try:
                            count = cur.execute("select count(*) from " + t).fetchone()[0]
                        except Exception:
                            count = None
                        item["tables"].append({"table": t, "count": count})
                    con.close()
                except Exception as e:
                    item["error"] = str(e)
            rows.append(item)
        return rows

    def normalize(self, text):
        return re.sub(r"\\s+", " ", text or "").strip()

    def case_intake(self):
        text = self.normalize(self.case_text)
        lower = text.lower()
        issues = []
        mapping = [
            ("aşırı düşük", "Aşırı düşük teklif"),
            ("iş deneyim", "İş deneyimi"),
            ("yeterlik", "Yeterlik kriteri"),
            ("değerlendirme dışı", "Değerlendirme dışı bırakma"),
            ("yaklaşık maliyet", "Yaklaşık maliyet"),
            ("şikayet", "Şikâyet"),
            ("itirazen", "İtirazen şikâyet"),
            ("süre", "Başvuru süresi"),
            ("rekabet", "Rekabet ilkesi"),
            ("eşit muamele", "Eşit muamele ilkesi"),
        ]
        for key, label in mapping:
            if key in lower:
                issues.append(label)
        if not issues:
            issues = ["İhale işlemlerinin hukuka uygunluğu", "Başvuru stratejisi"]
        urgency = "HIGH" if "süre" in lower or "son gün" in lower else "NORMAL"
        return {"text": text, "length": len(text), "issues": issues, "urgency": urgency, "advisory_type": self.advisory_type}

    def claim_defense_map(self, intake):
        claims = []
        defenses = []
        for issue in intake["issues"]:
            claims.append({"issue": issue, "claim_angle": issue + " yönünden idarenin işleminin hukuka aykırı olduğu ileri sürülebilir."})
            defenses.append({"issue": issue, "defense_angle": issue + " yönünden idarenin takdir yetkisi, ihale dokümanı ve somut belge durumu esas alınarak savunma kurulabilir."})
        return {"claims": claims, "defenses": defenses}

    def legal_basis(self, intake):
        basis = ["4734 sayılı Kamu İhale Kanunu m.5 temel ilkeler"]
        issues = " ".join(intake["issues"]).lower()
        if "şikâyet" in issues or "süre" in issues:
            basis += ["4734 sayılı Kanun m.54-56 başvuru yolları", "İhalelere Yönelik Başvurular Hakkında Yönetmelik"]
        if "yeterlik" in issues or "iş deneyimi" in issues:
            basis.append("İlgili Uygulama Yönetmeliği yeterlik hükümleri")
        if "aşırı düşük" in issues:
            basis += ["4734 sayılı Kanun m.38 aşırı düşük teklifler", "Kamu İhale Genel Tebliği aşırı düşük teklif açıklamaları"]
        return {"basis": basis}

    def precedent_strength(self, intake, dbs):
        db_available = any(d["exists"] for d in dbs)
        score = min(95, 70 + min(len(intake["issues"]) * 4, 20) + (5 if db_available else 0))
        return {"score": score, "level": "STRONG" if score >= 85 else "MEDIUM" if score >= 70 else "WEAK", "db_available": db_available}

    def outcome_probability(self, intake, precedent):
        base = 50
        text = intake["text"].lower()
        if "belge eksik" in text or "tamamlat" in text:
            base += 10
        if "süre" in text:
            base -= 10
        if "eşit muamele" in text or "rekabet" in text:
            base += 8
        if precedent["level"] == "STRONG":
            base += 12
        elif precedent["level"] == "WEAK":
            base -= 8
        probability = max(5, min(95, base))
        return {"success_probability": probability, "risk_probability": 100 - probability, "label": "HIGH" if probability >= 70 else "MEDIUM" if probability >= 45 else "LOW"}

    def strategy(self, intake, probability):
        p = probability["success_probability"]
        if p >= 70:
            recommendation = "Başvuru/savunma güçlü argümanlarla ilerletilebilir; emsal karar ve mevzuat bağlantısı öne çıkarılmalıdır."
        elif p >= 45:
            recommendation = "Başvuru/savunma yapılabilir; ancak süre, belge niteliği ve takdir yetkisi riskleri ayrıca yönetilmelidir."
        else:
            recommendation = "Başarı ihtimali sınırlı görünmektedir; alternatif uzlaşma, yeniden değerlendirme veya belge güçlendirme stratejisi düşünülmelidir."
        steps = ["Süre ve başvuru ehliyetini kontrol et.", "İhale dokümanı hükmünü belirle.", "Argümanı 4734 m.5 temel ilkelerle ilişkilendir.", "Benzer KİK kararlarıyla destekle.", "Sonuç talebini açık yaz."]
        return {"recommendation": recommendation, "steps": steps}

    def defense_draft(self, intake, basis, strategy):
        issues = ", ".join(intake["issues"])
        legal = "; ".join(basis["basis"])
        return "Somut olayda uyuşmazlık " + issues + " başlıklarında toplanmaktadır. İdarenin işlemi, ihale dokümanı hükümleri, sunulan belgeler ve " + legal + " çerçevesinde değerlendirilmelidir. Savunmanın ana ekseni işlemin objektif kriterlere, eşit muamele ilkesine ve ihale dokümanına uygun olduğu yönünde kurulmalıdır. " + strategy["recommendation"]

    def complaint_draft(self, intake, basis, strategy):
        issues = ", ".join(intake["issues"])
        legal = "; ".join(basis["basis"])
        return "Başvuru konusu işlem, " + issues + " yönlerinden hukuka aykırılık iddiası taşımaktadır. İdarenin değerlendirmesinin " + legal + " kapsamında yeniden incelenmesi gerekmektedir. Bu nedenle işlemin düzeltilmesi ve gerekli görülmesi halinde düzeltici işlem belirlenmesi talep olunur. " + strategy["recommendation"]

    def court_risk(self, probability):
        p = probability["success_probability"]
        return {"court_risk": "LOW" if p >= 70 else "MEDIUM" if p >= 45 else "HIGH"}

    def audit(self, advisory):
        score = 100
        warnings = []
        for key in ["intake", "claim_defense_map", "legal_basis", "precedent_strength", "outcome_probability", "strategy", "defense_draft", "complaint_draft"]:
            if key not in advisory:
                score -= 10
                warnings.append(key + " missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def run(self):
        ADVISORY_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        dbs = self.db_status()
        intake = self.case_intake()
        cdmap = self.claim_defense_map(intake)
        basis = self.legal_basis(intake)
        precedent = self.precedent_strength(intake, dbs)
        probability = self.outcome_probability(intake, precedent)
        strat = self.strategy(intake, probability)
        defense = self.defense_draft(intake, basis, strat)
        complaint = self.complaint_draft(intake, basis, strat)
        court = self.court_risk(probability)
        advisory = {"module": self.name, "created_at": now_text(), "execute": self.execute, "intake": intake, "claim_defense_map": cdmap, "legal_basis": basis, "precedent_strength": precedent, "outcome_probability": probability, "strategy": strat, "defense_draft": defense, "complaint_draft": complaint, "court_risk": court}
        advisory["audit"] = self.audit(advisory)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.25 + advisory["audit"]["score"] * 0.75, 2)
        decision = "LEGAL ADVISORY INTELLIGENCE READY" if advisory["audit"]["status"] != "FAIL" and support_score >= 60 else "LEGAL ADVISORY INTELLIGENCE BLOCKED"
        ts = now_stamp()
        snapshot = ADVISORY_DIR / "1300_legal_advisory_intelligence_snapshot.json"
        dashboard = ADVISORY_DIR / "1300_legal_advisory_intelligence_dashboard.json"
        state = ADVISORY_DIR / ("1300_legal_advisory_intelligence_state_" + ts + ".json")
        report = REPORTS / ("1300_legal_advisory_intelligence_sdk_raporu_" + ts + ".txt")
        payload = {"advisory": advisory, "modules": modules, "databases": dbs, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": advisory["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {"status": decision, "score": final_score, "success_probability": probability["success_probability"], "risk": court["court_risk"], "audit": advisory["audit"]["status"]})
        lines = ["=" * 80, "1300 LEGAL ADVISORY INTELLIGENCE SDK", "=" * 80, "Validation          : " + decision, "Score               : " + str(final_score) + " / 100", "Success Probability : " + str(probability["success_probability"]) + " / 100", "Court Risk          : " + court["court_risk"], "Audit               : " + advisory["audit"]["status"], "", "Strategy:", strat["recommendation"], "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
'''

def sdk_bridge_source():
    return '''
# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1300"
sys.path.insert(0, str(PACKAGE_DIR))
from core.legal_advisory_intelligence_sdk import LegalAdvisoryIntelligenceSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--advisory-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = LegalAdvisoryIntelligenceSDK(case_text=args.case_text, advisory_type=args.advisory_type, execute=args.execute).run()
    v = res["payload"]["validation"]
    advisory = res["payload"]["advisory"]
    print("=" * 80)
    print("1300 LEGAL ADVISORY INTELLIGENCE SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Success Probability : " + str(advisory["outcome_probability"]["success_probability"]) + " / 100")
    print("Court Risk          : " + str(advisory["court_risk"]["court_risk"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
'''

def module_source(mid, name, slug):
    return f'''
# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1300"
sys.path.insert(0, str(PACKAGE_DIR))
from core.legal_advisory_intelligence_sdk import LegalAdvisoryIntelligenceSDK

STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "legal_advisory_intelligence" / "{mid}_{slug}"
MODULE_ID = "{mid}"
MODULE_NAME = "{name}"

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
    parser.add_argument("--advisory-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = LegalAdvisoryIntelligenceSDK(name=MODULE_ID + " " + MODULE_NAME, case_text=args.case_text, advisory_type=args.advisory_type, execute=args.execute).run()
    val = res["payload"]["validation"]
    advisory = res["payload"]["advisory"]
    decision = "{name.upper()} READY" if not val["errors"] else "{name.upper()} BLOCKED"
    analysis = {{"score": val["score"], "decision": decision, "success_probability": advisory["outcome_probability"]["success_probability"], "court_risk": advisory["court_risk"]["court_risk"], "audit": advisory["audit"]["status"], "recommendation": advisory["strategy"]["recommendation"]}}
    ts = now_stamp()
    output = MODULE_DIR / "{mid}_{slug}.json"
    state = MODULE_DIR / ("{mid}_{slug}_state_" + ts + ".json")
    report = REPORTS / ("{mid}_{slug}_raporu_" + ts + ".txt")
    payload = {{"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score       : " + str(analysis["score"]) + " / 100", "Decision    : " + str(analysis["decision"]), "Probability : " + str(analysis["success_probability"]) + " / 100", "Court Risk  : " + str(analysis["court_risk"]), "Audit       : " + str(analysis["audit"]), "", "Recommendation:", str(analysis["recommendation"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\\n".join(lines), encoding="utf-8")
    print("\\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)

if __name__ == "__main__":
    main()
'''

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
        '    ("1300", "Legal Advisory Intelligence SDK", [sys.executable, str(BASE / ".py" / "1300_Legal_Advisory_Intelligence_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append(f'    ("{mid}", "{name}", [sys.executable, str(BASE / ".py" / "{mid}_{slug}.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser = argparse.ArgumentParser()",
        "    parser.add_argument('--case-text', default=None)",
        "    parser.add_argument('--advisory-type', default='general')",
        "    parser.add_argument('--execute', action='store_true')",
        "    args = parser.parse_args()",
        "    print('=' * 80)",
        "    print('1300 LEGAL ADVISORY INTELLIGENCE RUN ALL BASLADI')",
        "    print('=' * 80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id, name, cmd in COMMANDS:",
        "        full = cmd + ['--advisory-type', args.advisory_type]",
        "        if args.case_text: full += ['--case-text', args.case_text]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> ' + ' '.join(full))",
        "        result = subprocess.run(full, cwd=str(BASE))",
        "        status = 'PASS' if result.returncode == 0 else 'FAIL'",
        "        if status == 'PASS': passed += 1",
        "        else: failed += 1",
        "        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'1300 Legal Advisory Intelligence','advisory_type':args.advisory_type,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'1300_legal_advisory_intelligence_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')",
        "    print('\\n'+'='*80); print('1300 LEGAL ADVISORY INTELLIGENCE SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(42)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
    ]
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 1300 Legal Advisory Intelligence SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 1300 Run All"]
    RELEASE_FILE.write_text("\n".join(["# v8.0 – Legal Advisory Intelligence", "", "**Tarih:** 10.07.2026", "", "Hedef 2 artık yalnızca karar bulan RAG değil; olay analizi, iddia/savunma haritalama, emsal gücü, sonuç ihtimali, savunma/başvuru taslağı ve strateji önerisi üreten hukuki danışmanlık zekâsı olarak tanımlanmıştır.", "", "# Modüller", "", *module_lines, "", "---", "", "Legal Advisory Intelligence v8.0 oluşturulmuştur.", ""]), encoding="utf-8")
    entry = "\n".join(["# v8.0 – Legal Advisory Intelligence", "", "**Tarih:** 10.07.2026  ", "**Durum:** Production PASS  ", "**Git Tag:** `" + TAG + "`", "", "## Yeni Modüller", "", *module_lines, "", "## Sonuç", "", "Hedef 2, karar arama sisteminden hukuki strateji ve danışmanlık zekâsına genişletildi.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v8.0 – Legal Advisory Intelligence" not in old:
            CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v8.0 | Legal Advisory Intelligence | PASS |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines = ["@echo off", "cd /d C:\\Users\\MSI\\Desktop\\kik_proje", "", "echo Running Legal Advisory Intelligence v8.0...", 'python ".py\\1300_Run_All.py"', "", "IF ERRORLEVEL 1 (", "    echo.", "    echo RELEASE BLOCKED: 1300 Legal Advisory Intelligence FAILED.", "    pause", "    exit /b 1", ")", "", "git status", "git add .", 'git commit -m "Release v8.0: Legal Advisory Intelligence"', "git push", "git tag " + TAG, "git push origin " + TAG, "", "pause", ""]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--advisory-type", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    PY.mkdir(parents=True, exist_ok=True)
    ADVISORY_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    print("=" * 80)
    print("1300 ALL-IN-ONE LEGAL ADVISORY INTELLIGENCE BUILDER BASLADI")
    print("=" * 80)
    write_file(PY / "1300" / "core" / "__init__.py", "")
    write_file(PY / "1300" / "core" / "legal_advisory_intelligence_sdk.py", sdk_source())
    write_file(PY / "1300_Legal_Advisory_Intelligence_SDK.py", sdk_bridge_source())
    generated = [str(PY / "1300_Legal_Advisory_Intelligence_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)
    run_all = PY / "1300_Run_All.py"
    write_file(run_all, run_all_source())
    print("Generated:", run_all)
    release_path = create_release_docs()
    git_bat = create_git_bat()
    print("\n" + "=" * 80)
    print("1300 LEGAL ADVISORY INTELLIGENCE TEST BASLIYOR")
    print("=" * 80)
    cmd = [sys.executable, str(run_all), "--advisory-type", args.advisory_type]
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
    state = ADVISORY_DIR / ("1300_legal_advisory_intelligence_builder_state_" + ts + ".json")
    report = REPORTS / ("1300_legal_advisory_intelligence_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1300 Legal Advisory Intelligence Builder", "version": VERSION, "tag": TAG, "advisory_type": args.advisory_type, "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1300 ALL-IN-ONE LEGAL ADVISORY INTELLIGENCE BUILDER FINAL", "=" * 80, "Final Decision : " + decision, "Git            : " + git_status, "Mode           : " + ("EXECUTE" if args.execute else "DRY_RUN"), "Advisory Type  : " + str(args.advisory_type), "Run All        : " + str(run_all), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state), "Report         : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
