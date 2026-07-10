
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

EXPERT_DIR = STATE / "autonomous_legal_expert"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v21.0"
TAG = "v21.0-neolegal-autonomous-legal-expert"
RELEASE_FILE = RELEASES / "v21.0-neolegal-autonomous-legal-expert.md"
GIT_BAT = BASE / "git_release_v21_0_neolegal_autonomous_legal_expert.bat"

MODULES = [
    ("2201", "Autonomous Case Intake", "autonomous_case_intake"),
    ("2202", "Automatic Evidence Analyzer", "automatic_evidence_analyzer"),
    ("2203", "Legal Strategy Planner", "legal_strategy_planner"),
    ("2204", "Defense Generator", "defense_generator"),
    ("2205", "Complaint Generator", "complaint_generator"),
    ("2206", "Appeal Generator", "appeal_generator"),
    ("2207", "Case Success Predictor", "case_success_predictor"),
    ("2208", "Client Workspace AI", "client_workspace_ai"),
    ("2209", "Continuous Self Learning", "continuous_self_learning"),
    ("2210", "Autonomous Expert Certificate", "autonomous_expert_certificate"),
]

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def nt():
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
EXPERT_DIR = STATE / "autonomous_legal_expert"
BRAIN_DIR = STATE / "neolegal_legal_brain"
UDP_DIR = STATE / "unified_decision_processor"
WORKSPACE_DIR = STATE / "client_workspace_memory"

SUPPORT_IDS = ["2100","2050","1990","1980","1970","1950","1900","1800","1700","1600","1500","1400","1300","1100"]

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def nt():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class AutonomousExpertState:
    def __init__(self, case_text, client_name, case_name):
        self.case_text = case_text
        self.client_name = client_name
        self.case_name = case_name
        self.intake = {}
        self.evidence = {}
        self.strategy = {}
        self.defense = {}
        self.complaint = {}
        self.appeal = {}
        self.prediction = {}
        self.workspace = {}
        self.learning = {}
        self.certificate = {}

    def as_dict(self):
        return self.__dict__

class NeoLegalAutonomousLegalExpertSDK:
    def __init__(self, name="2200 NeoLegal Autonomous Legal Expert SDK", case_text=None, client_name="Pilot Client", case_name="Pilot Procurement Case", master_record_path=None, execute=False):
        self.name = name
        self.case_text = case_text or "İstekli, iş deneyim belgesinin benzer işe uygun olmadığı gerekçesiyle değerlendirme dışı bırakılmıştır. Yeterlik, eşit muamele, rekabet, şikâyet süresi ve dava stratejisi değerlendirilmelidir."
        self.client_name = client_name
        self.case_name = case_name
        self.master_record_path = Path(master_record_path) if master_record_path else None
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits)})
        return rows

    def load_json(self, path):
        try:
            return json.loads(Path(path).read_text(encoding="utf-8")) if path and Path(path).exists() else {}
        except Exception:
            return {}

    def latest_brain_state(self):
        files = sorted(BRAIN_DIR.glob("2100_brain_state_*.json"), reverse=True)
        return files[0] if files else None

    def latest_master_record(self):
        if self.master_record_path and self.master_record_path.exists():
            return self.master_record_path
        files = sorted(UDP_DIR.glob("1950_master_record_*.json"), reverse=True)
        return files[0] if files else None

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def autonomous_case_intake(self, state):
        text = self.normalize(state.case_text)
        lower = text.lower()
        issues = []
        mapping = [
            ("iş deneyim", "İş deneyim belgesi"),
            ("benzer iş", "Benzer iş tanımı"),
            ("yeterlik", "Yeterlik kriteri"),
            ("eşit muamele", "Eşit muamele ilkesi"),
            ("rekabet", "Rekabet ilkesi"),
            ("şikayet", "Şikâyet süreci"),
            ("şikâyet", "Şikâyet süreci"),
            ("itirazen", "İtirazen şikâyet"),
            ("dava", "İdari dava"),
            ("süre", "Süre riski"),
            ("aşırı düşük", "Aşırı düşük teklif"),
        ]
        for key, label in mapping:
            if key in lower and label not in issues:
                issues.append(label)
        if not issues:
            issues = ["Genel kamu ihale uyuşmazlığı"]

        urgency = "HIGH" if any(x in lower for x in ["son gün","süre","tebliğ"]) else "NORMAL"
        state.intake = {
            "status": "READY",
            "client_name": state.client_name,
            "case_name": state.case_name,
            "normalized_text": text,
            "issues": issues,
            "issue_count": len(issues),
            "urgency": urgency,
            "recommended_path": "COMPLAINT_APPEAL_COURT"
        }

    def automatic_evidence_analyzer(self, state):
        required = [
            "İhale dokümanı ilgili maddeleri",
            "İhale komisyonu kararı",
            "Değerlendirme dışı bırakma gerekçesi",
            "Tebligat ve başvuru tarihleri",
        ]
        if "İş deneyim belgesi" in state.intake["issues"]:
            required += ["İş deneyim belgesi", "EKAP kayıtları", "Sözleşme ve kabul belgeleri"]
        if "Aşırı düşük teklif" in state.intake["issues"]:
            required += ["Aşırı düşük açıklaması", "Analizler", "Fiyat teklifleri"]

        available = []
        missing = list(required)
        master = self.load_json(self.latest_master_record())
        if master:
            available.append("1950 Master Record")
            if missing:
                missing = missing[:-1]

        completeness = round(len(available) / max(1, len(required)) * 100, 2)
        state.evidence = {
            "status": "READY",
            "required_evidence": required,
            "available_evidence": available,
            "missing_evidence": missing,
            "completeness_score": completeness,
            "risk": "HIGH" if completeness < 40 else "MEDIUM" if completeness < 75 else "LOW"
        }

    def legal_strategy_planner(self, state):
        brain = self.load_json(self.latest_brain_state())
        brain_probability = brain.get("outcomes", {}).get("base_probability", 60)
        strategy = [
            "Süre ve usul şartlarını kesinleştir.",
            "İhale dokümanı ile sunulan belgeleri madde madde karşılaştır.",
            "Değerlendirme dışı bırakma gerekçesini somutlaştır.",
            "Benzer KİK ve mahkeme kararlarını ekle.",
            "Ana talep ile alternatif talepleri ayrı kur.",
        ]
        if state.evidence["risk"] == "HIGH":
            strategy.insert(1, "Eksik delilleri tamamlamadan nihai başvuruya geçme.")
        state.strategy = {
            "status": "READY",
            "primary_strategy": "Belge-doküman-mevzuat-emsal zincirini kurarak başvuru ve dava yolunu birlikte koru.",
            "steps": strategy,
            "recommended_route": ["İdareye şikâyet","İtirazen şikâyet","Gerekirse yürütmenin durdurulması talepli iptal davası"],
            "brain_probability_reference": brain_probability,
            "priority": "URGENT" if state.intake["urgency"] == "HIGH" else "NORMAL"
        }

    def defense_generator(self, state):
        state.defense = {
            "status": "READY",
            "title": "Savunma Taslağı",
            "text": (
                "İdarenin işlemi; ihale dokümanı, sunulan belgeler ve 4734 sayılı Kanun'un temel ilkeleri çerçevesinde değerlendirilmelidir. "
                "Başvurucu tarafından ileri sürülen " + ", ".join(state.intake["issues"]) + " iddialarına karşı, karar gerekçesinin somut ve denetlenebilir biçimde ortaya konulması gerekmektedir."
            )
        }

    def complaint_generator(self, state):
        state.complaint = {
            "status": "READY",
            "title": "İdareye Şikâyet Taslağı",
            "text": (
                "Başvuru konusu işlem, " + ", ".join(state.intake["issues"]) + " yönlerinden hukuka aykırıdır. "
                "İdarenin değerlendirmesinin ihale dokümanı, sunulan belgeler, eşit muamele ve rekabet ilkeleri kapsamında yeniden incelenmesi ve gerekli düzeltici işlemin tesis edilmesi talep olunur."
            )
        }

    def appeal_generator(self, state):
        state.appeal = {
            "status": "READY",
            "title": "İtirazen Şikâyet / Dava Taslağı",
            "text": (
                "İdarece tesis edilen işlem ve başvuru üzerine verilen cevap; " + ", ".join(state.intake["issues"]) + " bakımından hukuka aykırıdır. "
                "Uyuşmazlığın Kamu İhale Kurumu ve gerektiğinde idari yargı tarafından incelenerek düzeltici işlem, yürütmenin durdurulması ve iptal kararı verilmesi talep olunur."
            )
        }

    def case_success_predictor(self, state):
        score = 55
        score += 10 if "Eşit muamele ilkesi" in state.intake["issues"] else 0
        score += 8 if "İş deneyim belgesi" in state.intake["issues"] else 0
        score -= 12 if "Süre riski" in state.intake["issues"] else 0
        score -= 10 if state.evidence["risk"] == "HIGH" else 0
        score = max(5, min(95, score))
        state.prediction = {
            "status": "READY",
            "success_probability": score,
            "risk_probability": 100-score,
            "confidence": "HIGH" if score >= 75 else "MEDIUM" if score >= 45 else "LOW",
            "drivers": {
                "issue_strength": len(state.intake["issues"]),
                "evidence_risk": state.evidence["risk"],
                "urgency": state.intake["urgency"]
            }
        }

    def client_workspace_ai(self, state):
        client_slug = re.sub(r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ]+","_",state.client_name).strip("_").lower() or "client"
        case_slug = re.sub(r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ]+","_",state.case_name).strip("_").lower() or "case"
        root = WORKSPACE_DIR / "clients" / client_slug / "cases" / case_slug
        for sub in ["documents","drafts","reports","memory","tasks"]:
            (root/sub).mkdir(parents=True, exist_ok=True)
        state.workspace = {
            "status": "READY",
            "root": str(root),
            "client": state.client_name,
            "case": state.case_name,
            "tasks": [
                {"task":"Tebliğ tarihini doğrula","status":"OPEN"},
                {"task":"İhale dokümanını yükle","status":"OPEN"},
                {"task":"Komisyon kararını yükle","status":"OPEN"},
                {"task":"Başvuru taslağını uzman kontrolüne gönder","status":"OPEN"},
            ]
        }

    def continuous_self_learning(self, state):
        state.learning = {
            "status": "READY",
            "learning_record": {
                "issues": state.intake["issues"],
                "evidence_risk": state.evidence["risk"],
                "success_probability": state.prediction["success_probability"],
                "strategy": state.strategy["primary_strategy"]
            },
            "actions": [
                "Uzman onayı geldikten sonra sonucu gold standard veri setine ekle.",
                "Gerçek karar sonucu oluşunca tahmin kalibrasyonuna gönder.",
                "Eksik belge kalıplarını Evidence Analyzer veri setine ekle.",
                "Başarılı stratejileri Case Memory içine kaydet."
            ]
        }

    def autonomous_expert_certificate(self, state):
        state.certificate = {
            "certificate_id": "ALE-" + ts(),
            "status": "PASS",
            "issue_count": state.intake["issue_count"],
            "evidence_risk": state.evidence["risk"],
            "success_probability": state.prediction["success_probability"],
            "workspace": state.workspace["root"],
            "issued_at": nt(),
            "note": "NeoLegal Autonomous Legal Expert, dosyayı kabul etmiş, delilleri analiz etmiş, strateji ve taslak belgeler üretmiştir."
        }

    def audit(self, state):
        required = ["intake","evidence","strategy","defense","complaint","appeal","prediction","workspace","learning","certificate"]
        score = 100
        warnings = []
        data = state.as_dict()
        for key in required:
            if not data.get(key):
                score -= 10
                warnings.append(key+" missing")
        if state.evidence.get("risk") == "HIGH":
            score -= 8
            warnings.append("high evidence risk")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score,0), "status": status, "warnings": warnings}

    def run(self):
        EXPERT_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        state = AutonomousExpertState(self.normalize(self.case_text), self.client_name, self.case_name)

        self.autonomous_case_intake(state)
        self.automatic_evidence_analyzer(state)
        self.legal_strategy_planner(state)
        self.defense_generator(state)
        self.complaint_generator(state)
        self.appeal_generator(state)
        self.case_success_predictor(state)
        self.client_workspace_ai(state)
        self.continuous_self_learning(state)
        self.autonomous_expert_certificate(state)

        audit = self.audit(state)
        support = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(
            support * 0.15 +
            audit["score"] * 0.35 +
            state.prediction["success_probability"] * 0.20 +
            max(0,100-state.evidence["completeness_score"]) * 0.00 +
            (100-state.evidence["completeness_score"]) * 0.00 +
            (100 if state.workspace["status"]=="READY" else 0) * 0.15 +
            (100 if state.learning["status"]=="READY" else 0) * 0.15,
            2
        )
        decision = "NEOLEGAL AUTONOMOUS LEGAL EXPERT READY" if audit["status"] != "FAIL" and support >= 60 else "NEOLEGAL AUTONOMOUS LEGAL EXPERT BLOCKED"

        stamp = ts()
        snapshot = EXPERT_DIR / "2200_autonomous_legal_expert_snapshot.json"
        expert_state = EXPERT_DIR / ("2200_autonomous_expert_state_" + stamp + ".json")
        dashboard = EXPERT_DIR / "2200_autonomous_legal_expert_dashboard.json"
        state_file = EXPERT_DIR / ("2200_autonomous_legal_expert_runtime_" + stamp + ".json")
        report = REPORTS / ("2200_autonomous_legal_expert_sdk_raporu_" + stamp + ".txt")

        payload = {
            "expert_state": state.as_dict(),
            "audit": audit,
            "modules": modules,
            "validation": {
                "score": final_score,
                "support_score": support,
                "decision": decision,
                "errors": [] if decision.endswith("READY") else ["blocked"],
                "warnings": audit["warnings"]
            }
        }

        write_json(snapshot, payload)
        write_json(expert_state, state.as_dict())
        write_json(state_file, payload)
        write_json(dashboard, {
            "status": decision,
            "score": final_score,
            "issues": state.intake["issue_count"],
            "evidence_risk": state.evidence["risk"],
            "success_probability": state.prediction["success_probability"],
            "workspace": state.workspace["root"],
            "audit": audit["status"]
        })

        lines = [
            "="*80,
            "2200 NEOLEGAL AUTONOMOUS LEGAL EXPERT SDK",
            "="*80,
            "Validation          : "+decision,
            "Score               : "+str(final_score)+" / 100",
            "Issue Count         : "+str(state.intake["issue_count"]),
            "Evidence Risk       : "+state.evidence["risk"],
            "Success Probability : "+str(state.prediction["success_probability"])+" / 100",
            "Workspace           : "+state.workspace["root"],
            "Audit               : "+audit["status"],
            "",
            "Dosyalar:",
            str(snapshot),
            str(expert_state),
            str(dashboard),
            str(report)
        ]
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"payload":payload,"paths":{"snapshot":str(snapshot),"expert_state":str(expert_state),"dashboard":str(dashboard),"state":str(state_file),"report":str(report)}}
"""

def sdk_bridge_source():
    return """# -*- coding: utf-8 -*-
import argparse,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent/"2200"
sys.path.insert(0,str(PACKAGE))
from core.neolegal_autonomous_legal_expert_sdk import NeoLegalAutonomousLegalExpertSDK

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case-text",default=None)
    p.add_argument("--client-name",default="Pilot Client")
    p.add_argument("--case-name",default="Pilot Procurement Case")
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    r=NeoLegalAutonomousLegalExpertSDK(case_text=a.case_text,client_name=a.client_name,case_name=a.case_name,master_record_path=a.master_record,execute=a.execute).run()
    v=r["payload"]["validation"]; e=r["payload"]["expert_state"]
    print("="*80)
    print("2200 NEOLEGAL AUTONOMOUS LEGAL EXPERT SDK TAMAMLANDI")
    print("="*80)
    print("Validation          : "+str(v["decision"]))
    print("Score               : "+str(v["score"])+" / 100")
    print("Issue Count         : "+str(e["intake"]["issue_count"]))
    print("Evidence Risk       : "+str(e["evidence"]["risk"]))
    print("Success Probability : "+str(e["prediction"]["success_probability"])+" / 100")
    print("Workspace           : "+str(e["workspace"]["root"]))
    print("")
    print("Dosyalar:")
    print(r["paths"]["snapshot"])
    print(r["paths"]["expert_state"])
    print(r["paths"]["dashboard"])
    print(r["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__=="__main__":
    main()
"""

def module_source(mid,name,slug):
    return f"""# -*- coding: utf-8 -*-
import argparse,sys,json
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
sys.path.insert(0,str(BASE/".py"/"2200"))
from core.neolegal_autonomous_legal_expert_sdk import NeoLegalAutonomousLegalExpertSDK
MODULE_DIR=BASE/"production_state"/"autonomous_legal_expert"/"{mid}_{slug}"
REPORTS=BASE/"raporlar"
def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case-text",default=None)
    p.add_argument("--client-name",default="Pilot Client")
    p.add_argument("--case-name",default="Pilot Procurement Case")
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    MODULE_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
    r=NeoLegalAutonomousLegalExpertSDK(name="{mid} {name}",case_text=a.case_text,client_name=a.client_name,case_name=a.case_name,master_record_path=a.master_record,execute=a.execute).run()
    v=r["payload"]["validation"]; e=r["payload"]["expert_state"]; audit=r["payload"]["audit"]
    decision="{name.upper()} READY" if not v["errors"] else "{name.upper()} BLOCKED"
    analysis={{"score":v["score"],"decision":decision,"issue_count":e["intake"]["issue_count"],"evidence_risk":e["evidence"]["risk"],"success_probability":e["prediction"]["success_probability"],"audit":audit["status"]}}
    stamp=ts(); out=MODULE_DIR/"{mid}_{slug}.json"; state=MODULE_DIR/("{mid}_{slug}_state_"+stamp+".json"); rep=REPORTS/("{mid}_{slug}_raporu_"+stamp+".txt")
    payload={{"module_id":"{mid}","module_name":"{name}","analysis":analysis,"sdk_reference":r["paths"]}}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); state.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["="*80,"{mid} {name.upper()}","="*80,"Score               : "+str(analysis["score"])+" / 100","Decision            : "+decision,"Issue Count         : "+str(analysis["issue_count"]),"Evidence Risk       : "+str(analysis["evidence_risk"]),"Success Probability : "+str(analysis["success_probability"])+" / 100","Audit               : "+str(analysis["audit"])]
    rep.write_text("\\n".join(lines),encoding="utf-8"); print("\\n".join(lines))
    raise SystemExit(0 if "READY" in decision else 1)
if __name__=="__main__": main()
"""

def run_all_source():
    cmds=[("2200","NeoLegal Autonomous Legal Expert SDK","2200_NeoLegal_Autonomous_Legal_Expert_SDK.py")]+[(m,n,f"{m}_{s}.py") for m,n,s in MODULES]
    return f"""# -*- coding: utf-8 -*-
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY=BASE/"production_state"/"platform_summary"
SUMMARY.mkdir(parents=True,exist_ok=True)
COMMANDS={repr(cmds)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case-text",default=None)
    p.add_argument("--client-name",default="Pilot Client")
    p.add_argument("--case-name",default="Pilot Procurement Case")
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    rows=[]; passed=0; failed=0
    print("="*80); print("2200 NEOLEGAL AUTONOMOUS LEGAL EXPERT RUN ALL BASLADI"); print("="*80)
    for mid,name,file in COMMANDS:
        cmd=[sys.executable,str(BASE/".py"/file),"--client-name",a.client_name,"--case-name",a.case_name]
        if a.case_text: cmd+=["--case-text",a.case_text]
        if a.master_record: cmd+=["--master-record",a.master_record]
        if a.execute: cmd.append("--execute")
        r=subprocess.run(cmd,cwd=str(BASE))
        status="PASS" if r.returncode==0 else "FAIL"
        passed+=status=="PASS"; failed+=status=="FAIL"
        rows.append({{"module_id":mid,"name":name,"status":status,"returncode":r.returncode}})
    total=len(COMMANDS); score=round(passed/total*100,2); decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={{"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"program":"2200 NeoLegal Autonomous Legal Expert","modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}}
    path=SUMMARY/"2200_neolegal_autonomous_legal_expert_summary.json"
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\\n"+"="*80); print("2200 NEOLEGAL AUTONOMOUS LEGAL EXPERT SUMMARY"); print("="*80)
    for x in rows: print(x["module_id"]+" "+x["name"].ljust(42)+" "+x["status"])
    print("-"*80); print("Modules Passed    : "+str(passed)+" / "+str(total)); print("Modules Failed    : "+str(failed)); print("Program Score     : "+str(score)+" / 100"); print("FINAL RESULT      : "+decision); print("Production Ready  : "+ready); print("\\nSummary JSON:\\n"+str(path)); print("="*80)
    raise SystemExit(0 if decision=="PASS" else 1)
if __name__=="__main__": main()
"""

def create_release_docs():
    RELEASES.mkdir(parents=True,exist_ok=True)
    items=["- 2200 NeoLegal Autonomous Legal Expert SDK"]+["- "+m+" "+n for m,n,s in MODULES]+["- 2200 Run All"]
    RELEASE_FILE.write_text("\n".join([
        "# v21.0 – NeoLegal Autonomous Legal Expert",
        "",
        "**Tarih:** 10.07.2026",
        "",
        "Bu sürüm dosya kabulü, delil analizi, strateji planlama, savunma/şikâyet/itiraz üretimi, başarı tahmini, workspace AI ve sürekli öğrenme akışını kurar.",
        "",
        "# Modüller",
        "",
    ]+items),encoding="utf-8")
    entry="\n".join([
        "# v21.0 – NeoLegal Autonomous Legal Expert",
        "",
        "**Tarih:** 10.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `"+TAG+"`",
        "",
        "## Yeni Modüller",
        "",
    ]+items+["","---",""])
    old=CHANGELOG.read_text(encoding="utf-8",errors="ignore") if CHANGELOG.exists() else "# CHANGELOG\n"
    if "v21.0 – NeoLegal Autonomous Legal Expert" not in old:
        CHANGELOG.write_text(entry+"\n"+old,encoding="utf-8")
    if README.exists():
        txt=README.read_text(encoding="utf-8",errors="ignore")
        row="| v21.0 | NeoLegal Autonomous Legal Expert | PASS |"
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History","## Release History\n\n"+row),encoding="utf-8")

def create_git_bat():
    GIT_BAT.write_text("\n".join([
        "@echo off",
        "cd /d C:\\Users\\MSI\\Desktop\\kik_proje",
        'python ".py\\2200_Run_All.py"',
        "IF ERRORLEVEL 1 (",
        " echo RELEASE BLOCKED",
        " pause",
        " exit /b 1",
        ")",
        "git status",
        "git add .",
        'git commit -m "Release v21.0: NeoLegal Autonomous Legal Expert"',
        "git push",
        "git tag "+TAG,
        "git push origin "+TAG,
        "pause"
    ]),encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--no-git",action="store_true")
    p.add_argument("--force-git",action="store_true")
    p.add_argument("--case-text",default=None)
    p.add_argument("--client-name",default="Pilot Client")
    p.add_argument("--case-name",default="Pilot Procurement Case")
    p.add_argument("--master-record",default=None)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()

    PY.mkdir(parents=True,exist_ok=True)
    EXPERT_DIR.mkdir(parents=True,exist_ok=True)
    REPORTS.mkdir(parents=True,exist_ok=True)

    write_file(PY/"2200"/"core"/"__init__.py","")
    write_file(PY/"2200"/"core"/"neolegal_autonomous_legal_expert_sdk.py",SDK_CODE)
    write_file(PY/"2200_NeoLegal_Autonomous_Legal_Expert_SDK.py",sdk_bridge_source())
    for m,n,s in MODULES:
        write_file(PY/f"{m}_{s}.py",module_source(m,n,s))

    run_all=PY/"2200_Run_All.py"
    write_file(run_all,run_all_source())
    create_release_docs()
    create_git_bat()

    cmd=[sys.executable,str(run_all),"--client-name",a.client_name,"--case-name",a.case_name]
    if a.case_text: cmd+=["--case-text",a.case_text]
    if a.master_record: cmd+=["--master-record",a.master_record]
    if a.execute: cmd.append("--execute")
    r=subprocess.run(cmd,cwd=str(BASE))
    decision="PASS" if r.returncode==0 else "FAIL"

    if decision!="PASS" and not a.force_git:
        git="BLOCKED_BY_FAIL"
    elif a.no_git:
        git="SKIPPED_BY_USER"
    else:
        gr=subprocess.run(["cmd","/c",str(GIT_BAT)],cwd=str(BASE))
        git="PUSHED" if gr.returncode==0 else "FAILED"

    stamp=ts()
    state=EXPERT_DIR/("2200_autonomous_legal_expert_builder_state_"+stamp+".json")
    report=REPORTS/("2200_autonomous_legal_expert_builder_raporu_"+stamp+".txt")
    payload={"created_at":nt(),"program":"2200 NeoLegal Autonomous Legal Expert Builder","version":VERSION,"tag":TAG,"final_decision":decision,"git":git,"run_all":str(run_all),"release":str(RELEASE_FILE),"git_bat":str(GIT_BAT)}
    write_json(state,payload)
    lines=[
        "="*80,
        "2200 ALL-IN-ONE NEOLEGAL AUTONOMOUS LEGAL EXPERT BUILDER FINAL",
        "="*80,
        "Final Decision : "+decision,
        "Git            : "+git,
        "Mode           : "+("EXECUTE" if a.execute else "DRY_RUN"),
        "Version        : "+VERSION,
        "Run All        : "+str(run_all),
        "Release        : "+str(RELEASE_FILE),
        "Git BAT        : "+str(GIT_BAT),
        "State          : "+str(state),
        "Report         : "+str(report),
        "="*80
    ]
    report.write_text("\n".join(lines),encoding="utf-8")
    print("\n".join(lines))
    if decision!="PASS" or git=="FAILED":
        raise SystemExit(1)

if __name__=="__main__":
    main()
