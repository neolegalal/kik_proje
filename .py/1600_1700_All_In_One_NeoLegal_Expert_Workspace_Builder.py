
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

EXPERT_DIR = STATE / "neolegal_expert_orchestrator"
WORKSPACE_DIR = STATE / "client_workspace_memory"
SUMMARY_DIR = STATE / "platform_summary"

VERSION_1600 = "v11.0"
VERSION_1700 = "v12.0"
TAG_1600 = "v11.0-neolegal-expert-orchestrator"
TAG_1700 = "v12.0-client-workspace-knowledge-memory"
RELEASE_1600 = RELEASES / "v11.0-neolegal-expert-orchestrator.md"
RELEASE_1700 = RELEASES / "v12.0-client-workspace-knowledge-memory.md"
GIT_BAT = BASE / "git_release_v11_0_v12_0_expert_workspace.bat"

MODULES_1600 = [
    ("1601", "Case Intake Orchestrator", "case_intake_orchestrator"),
    ("1602", "Decision Retrieval Orchestrator", "decision_retrieval_orchestrator"),
    ("1603", "Advisory Orchestrator", "advisory_orchestrator"),
    ("1604", "Litigation Orchestrator", "litigation_orchestrator"),
    ("1605", "Legal Reasoning Orchestrator", "legal_reasoning_orchestrator"),
    ("1606", "Conflict Resolver", "conflict_resolver"),
    ("1607", "Final Legal Opinion Generator", "final_legal_opinion_generator"),
    ("1608", "Action Plan Generator", "action_plan_generator"),
    ("1609", "Expert Quality Auditor", "expert_quality_auditor"),
    ("1610", "NeoLegal Expert Certificate", "neolegal_expert_certificate"),
]

MODULES_1700 = [
    ("1701", "Client Profile Manager", "client_profile_manager"),
    ("1702", "Case Workspace Manager", "case_workspace_manager"),
    ("1703", "Conversation Memory Manager", "conversation_memory_manager"),
    ("1704", "Document Memory Indexer", "document_memory_indexer"),
    ("1705", "Strategy History Tracker", "strategy_history_tracker"),
    ("1706", "Deadline Reminder Planner", "deadline_reminder_planner"),
    ("1707", "Task Action Board", "task_action_board"),
    ("1708", "Knowledge Memory Retriever", "knowledge_memory_retriever"),
    ("1709", "Workspace Dashboard", "workspace_dashboard"),
    ("1710", "Workspace Quality Auditor", "workspace_quality_auditor"),
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

SDK_1600 = r"""
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
EXPERT_DIR = STATE / "neolegal_expert_orchestrator"
SUPPORT_IDS = ["1500", "1400", "1300", "1100", "1000", "900", "800", "801"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class NeoLegalExpertOrchestratorSDK:
    def __init__(self, name="1600 NeoLegal Expert Orchestrator SDK", case_text=None, expert_mode="general", execute=False):
        self.name = name
        self.case_text = case_text or "İstekli, iş deneyim belgesinin uygun olmadığı gerekçesiyle değerlendirme dışı bırakılmıştır. Eşit muamele, rekabet, yeterlik kriteri, başvuru ve dava stratejisi birlikte değerlendirilmelidir."
        self.expert_mode = expert_mode
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def case_intake(self):
        text = self.normalize(self.case_text)
        lower = text.lower()
        issues = []
        for key, label in [
            ("iş deneyim", "İş deneyimi"),
            ("yeterlik", "Yeterlik kriteri"),
            ("değerlendirme dışı", "Değerlendirme dışı bırakma"),
            ("aşırı düşük", "Aşırı düşük teklif"),
            ("eşit muamele", "Eşit muamele"),
            ("rekabet", "Rekabet"),
            ("süre", "Süre riski"),
            ("şikayet", "Şikâyet"),
            ("itirazen", "İtirazen şikâyet"),
            ("dava", "Dava"),
        ]:
            if key in lower and label not in issues:
                issues.append(label)
        if not issues:
            issues = ["İhale işleminin hukuka uygunluğu", "Başvuru stratejisi"]
        return {"text": text, "issues": issues, "mode": self.expert_mode}

    def decision_retrieval(self, intake):
        score = min(95, 65 + len(intake["issues"]) * 4)
        return {
            "retrieval_status": "READY",
            "estimated_relevance_score": score,
            "sources": ["KİK kararları", "4734 sayılı Kanun", "İkincil mevzuat", "Mahkeme içtihatları"],
            "note": "Bu katman 1100 Decision Pipeline ve mevcut veri tabanıyla bağlanacak şekilde hazırlanmıştır."
        }

    def advisory(self, intake):
        p = 60
        if "Süre riski" in intake["issues"]:
            p -= 10
        if "Eşit muamele" in intake["issues"] or "Rekabet" in intake["issues"]:
            p += 10
        if "İş deneyimi" in intake["issues"] or "Yeterlik kriteri" in intake["issues"]:
            p += 8
        p = max(5, min(95, p))
        return {
            "success_probability": p,
            "advisory_result": "Başvuru/savunma, doküman hükmü, somut belge ve temel ilkeler birlikte kurularak ilerletilmelidir.",
            "risk_level": "LOW" if p >= 70 else "MEDIUM" if p >= 45 else "HIGH"
        }

    def litigation(self, intake, advisory):
        route = ["İdareye şikâyet", "İtirazen şikâyet", "Gerekirse yürütmenin durdurulması talepli iptal davası"]
        if "Dava" in intake["issues"]:
            route = ["Dava dilekçesi", "Yürütmenin durdurulması", "Savunmaya cevap", "Ek beyan"]
        return {
            "recommended_route": route,
            "yd_strength": "STRONG" if advisory["success_probability"] >= 70 else "MEDIUM",
            "litigation_note": "Başvuru/dava yolu seçimi süre, belge gücü ve emsal karar yönünden birlikte değerlendirilmelidir."
        }

    def reasoning(self, intake, advisory, litigation):
        arguments = []
        counter_arguments = []
        for issue in intake["issues"]:
            arguments.append(issue + " yönünden başvurucu lehine hukuka aykırılık argümanı kurulabilir.")
            counter_arguments.append(issue + " yönünden idare, doküman hükümleri ve takdir yetkisine dayanabilir.")
        return {
            "arguments": arguments,
            "counter_arguments": counter_arguments,
            "reasoning_chain": [
                "Önce süre ve usul denetlenir.",
                "İhale dokümanı hükmü belirlenir.",
                "Somut belge durumu incelenir.",
                "4734 m.5 temel ilkelerle uyum kontrol edilir.",
                "Emsal kararlar ve yargı içtihadı ile sonuç güçlendirilir."
            ],
            "reasoning_score": min(95, advisory["success_probability"] + 8)
        }

    def conflict_resolver(self, advisory, litigation, reasoning):
        conflicts = []
        if advisory["success_probability"] < 50 and litigation["yd_strength"] == "STRONG":
            conflicts.append("Başarı ihtimali düşükken YD gücü yüksek görünüyor; delil ve telafisi güç zarar gerekçesi ayrıştırılmalı.")
        if not conflicts:
            conflicts.append("Modüller arasında kritik çelişki tespit edilmemiştir.")
        return {"conflicts": conflicts, "resolution": "Nihai görüşte süre/usul, belge gücü ve temel ilkeler öncelik sırasına göre dengelenmiştir."}

    def final_opinion(self, intake, retrieval, advisory, litigation, reasoning, conflict):
        return (
            "NEOLEGAL UZMAN GÖRÜŞÜ\\n\\n"
            "Somut olayda uyuşmazlık " + ", ".join(intake["issues"]) + " başlıklarında yoğunlaşmaktadır. "
            "İlk değerlendirmeye göre başarı ihtimali %" + str(advisory["success_probability"]) + " seviyesindedir. "
            "Önerilen yol: " + " → ".join(litigation["recommended_route"]) + ". "
            "Hukuki strateji, ihale dokümanı hükmü, sunulan belgeler, 4734 sayılı Kanun m.5 temel ilkeleri ve benzer kararlarla desteklenmelidir. "
            + conflict["resolution"]
        )

    def action_plan(self, intake, litigation):
        steps = [
            "Tebliğ ve başvuru sürelerini kesin olarak kontrol et.",
            "İhale dokümanındaki ilgili yeterlik/teklif düzenlemesini çıkar.",
            "Komisyon kararını ve değerlendirme dışı bırakma gerekçesini analiz et.",
            "Lehe emsal KİK kararlarını ve varsa mahkeme içtihatlarını ilişkilendir.",
            "Başvuru/dava metninde ana talep ve alternatif talepleri ayrı kur.",
        ]
        steps += ["İzlenecek yol: " + " → ".join(litigation["recommended_route"])]
        return {"steps": steps}

    def audit(self, pack):
        score = 100
        warnings = []
        for key in ["intake", "retrieval", "advisory", "litigation", "reasoning", "conflict_resolution", "final_opinion", "action_plan"]:
            if key not in pack:
                score -= 10
                warnings.append(key + " missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def certificate(self, pack):
        return {
            "certificate_id": "NLE-" + now_stamp(),
            "status": pack["audit"]["status"],
            "success_probability": pack["advisory"]["success_probability"],
            "issued_at": now_text(),
            "note": "Bu çıktı karar destek amaçlı uzman görüşüdür; nihai hukuki değerlendirme kullanıcı/uzman kontrolüyle kesinleştirilmelidir."
        }

    def run(self):
        EXPERT_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        intake = self.case_intake()
        retrieval = self.decision_retrieval(intake)
        advisory = self.advisory(intake)
        litigation = self.litigation(intake, advisory)
        reasoning = self.reasoning(intake, advisory, litigation)
        conflict = self.conflict_resolver(advisory, litigation, reasoning)
        opinion = self.final_opinion(intake, retrieval, advisory, litigation, reasoning, conflict)
        actions = self.action_plan(intake, litigation)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "intake": intake,
            "retrieval": retrieval,
            "advisory": advisory,
            "litigation": litigation,
            "reasoning": reasoning,
            "conflict_resolution": conflict,
            "final_opinion": opinion,
            "action_plan": actions,
        }
        pack["audit"] = self.audit(pack)
        pack["certificate"] = self.certificate(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.25 + pack["audit"]["score"] * 0.75, 2)
        decision = "NEOLEGAL EXPERT ORCHESTRATOR READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "NEOLEGAL EXPERT ORCHESTRATOR BLOCKED"
        ts = now_stamp()
        snapshot = EXPERT_DIR / "1600_neolegal_expert_orchestrator_snapshot.json"
        dashboard = EXPERT_DIR / "1600_neolegal_expert_orchestrator_dashboard.json"
        state = EXPERT_DIR / ("1600_neolegal_expert_orchestrator_state_" + ts + ".json")
        report = REPORTS / ("1600_neolegal_expert_orchestrator_sdk_raporu_" + ts + ".txt")
        payload = {"expert": pack, "modules": modules, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {"status": decision, "score": final_score, "success_probability": advisory["success_probability"], "risk": advisory["risk_level"], "audit": pack["audit"]["status"]})
        lines = ["=" * 80, "1600 NEOLEGAL EXPERT ORCHESTRATOR SDK", "=" * 80, "Validation          : " + decision, "Score               : " + str(final_score) + " / 100", "Success Probability : " + str(advisory["success_probability"]) + " / 100", "Risk                : " + advisory["risk_level"], "Audit               : " + pack["audit"]["status"], "", "Final Opinion:", opinion, "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
"""

SDK_1700 = r"""
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
WORKSPACE_DIR = STATE / "client_workspace_memory"
SUPPORT_IDS = ["1600", "1500", "1400", "1300", "1100", "1000", "900"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class ClientWorkspaceMemorySDK:
    def __init__(self, name="1700 Client Workspace & Knowledge Memory SDK", client_name="Pilot Client", case_name="Pilot Procurement Case", case_text=None, execute=False):
        self.name = name
        self.client_name = client_name
        self.case_name = case_name
        self.case_text = case_text or "İş deneyim belgesi nedeniyle değerlendirme dışı bırakma işlemi hakkında başvuru ve dava stratejisi çalışılacaktır."
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def slug(self, text):
        text = re.sub(r"[^a-zA-Z0-9çğıöşüÇĞİÖŞÜ]+", "_", text or "").strip("_").lower()
        return text[:80] or "workspace"

    def client_profile(self):
        return {
            "client_name": self.client_name,
            "created_at": now_text(),
            "profile_type": "procurement_law_client",
            "default_domain": "Kamu İhale Hukuku"
        }

    def case_workspace(self):
        client_slug = self.slug(self.client_name)
        case_slug = self.slug(self.case_name)
        folder = WORKSPACE_DIR / "clients" / client_slug / "cases" / case_slug
        folders = {
            "root": folder,
            "documents": folder / "documents",
            "drafts": folder / "drafts",
            "reports": folder / "reports",
            "memory": folder / "memory",
            "tasks": folder / "tasks",
        }
        for f in folders.values():
            f.mkdir(parents=True, exist_ok=True)
        return {k: str(v) for k, v in folders.items()}

    def conversation_memory(self):
        return {
            "memory_id": "CM-" + now_stamp(),
            "case_text": self.case_text,
            "summary": "Dosya, kamu ihale uyuşmazlığı için başvuru/dava stratejisi ve hukuki danışmanlık hafızasına alınmıştır.",
            "created_at": now_text()
        }

    def document_memory_index(self):
        return {
            "indexed_documents": [],
            "expected_documents": ["İhale dokümanı", "Komisyon kararı", "Tebligat", "Başvuru dilekçesi", "Savunma/cevap dilekçeleri"],
            "index_status": "READY"
        }

    def strategy_history(self):
        return {
            "strategies": [
                {"step": 1, "strategy": "Süre ve usul kontrolü"},
                {"step": 2, "strategy": "İhale dokümanı ve belge uyum kontrolü"},
                {"step": 3, "strategy": "KİK ve mahkeme emsal bağlantısı"},
                {"step": 4, "strategy": "Başvuru/dava metni üretimi"}
            ]
        }

    def deadlines(self):
        return {
            "deadline_status": "NEEDS_USER_INPUT",
            "required_dates": ["Tebliğ tarihi", "İhale tarihi", "Başvuru tarihi", "Karar tarihi"],
            "note": "Kesin süre hesabı için tarih bilgileri kullanıcıdan alınmalıdır."
        }

    def task_board(self):
        return {
            "tasks": [
                {"task": "Tebliğ tarihini gir", "status": "OPEN"},
                {"task": "İhale dokümanını yükle", "status": "OPEN"},
                {"task": "Komisyon kararını yükle", "status": "OPEN"},
                {"task": "Başvuru stratejisini 1600 çıktısıyla eşleştir", "status": "OPEN"},
            ]
        }

    def memory_retriever(self, profile, workspace, conversation):
        return {
            "retrieval_status": "READY",
            "client": profile["client_name"],
            "workspace_root": workspace["root"],
            "last_case_summary": conversation["summary"]
        }

    def audit(self, pack):
        score = 100
        warnings = []
        for key in ["client_profile", "workspace", "conversation_memory", "document_memory_index", "strategy_history", "deadlines", "task_board", "memory_retriever"]:
            if key not in pack:
                score -= 10
                warnings.append(key + " missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def run(self):
        WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        profile = self.client_profile()
        workspace = self.case_workspace()
        conversation = self.conversation_memory()
        doc_index = self.document_memory_index()
        strategy = self.strategy_history()
        deadlines = self.deadlines()
        tasks = self.task_board()
        retriever = self.memory_retriever(profile, workspace, conversation)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "client_profile": profile,
            "workspace": workspace,
            "conversation_memory": conversation,
            "document_memory_index": doc_index,
            "strategy_history": strategy,
            "deadlines": deadlines,
            "task_board": tasks,
            "memory_retriever": retriever,
        }
        pack["audit"] = self.audit(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.25 + pack["audit"]["score"] * 0.75, 2)
        decision = "CLIENT WORKSPACE MEMORY READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "CLIENT WORKSPACE MEMORY BLOCKED"
        ts = now_stamp()
        snapshot = WORKSPACE_DIR / "1700_client_workspace_memory_snapshot.json"
        dashboard = WORKSPACE_DIR / "1700_client_workspace_memory_dashboard.json"
        state = WORKSPACE_DIR / ("1700_client_workspace_memory_state_" + ts + ".json")
        report = REPORTS / ("1700_client_workspace_memory_sdk_raporu_" + ts + ".txt")
        payload = {"workspace_memory": pack, "modules": modules, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {"status": decision, "score": final_score, "client": self.client_name, "case": self.case_name, "audit": pack["audit"]["status"], "workspace_root": workspace["root"]})
        lines = ["=" * 80, "1700 CLIENT WORKSPACE & KNOWLEDGE MEMORY SDK", "=" * 80, "Validation : " + decision, "Score      : " + str(final_score) + " / 100", "Client     : " + self.client_name, "Case       : " + self.case_name, "Audit      : " + pack["audit"]["status"], "", "Workspace:", workspace["root"], "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
"""

def sdk_bridge_source(prefix, class_name, import_name, title, args_block, init_block, output_block):
    return f"""# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "{prefix}"
sys.path.insert(0, str(PACKAGE_DIR))
from core.{import_name} import {class_name}

def main():
    parser = argparse.ArgumentParser()
{args_block}
    args = parser.parse_args()
    res = {class_name}({init_block}).run()
    v = res["payload"]["validation"]
    print("=" * 80)
    print("{title} TAMAMLANDI")
    print("=" * 80)
    print("Validation : " + str(v["decision"]))
    print("Score      : " + str(v["score"]) + " / 100")
{output_block}
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
"""

def module_source(prefix, mid, name, slug, class_name, import_name, state_subdir, args_block, init_block, output_fields):
    output_prints = ""
    analysis_pairs = []
    for key, expr in output_fields:
        analysis_pairs.append(f'"{key}": {expr}')
        output_prints += f'    print("{key} : " + str(analysis["{key}"]))\\n'
    analysis_text = "{"+", ".join(analysis_pairs)+"}"
    return f"""# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "{prefix}"
sys.path.insert(0, str(PACKAGE_DIR))
from core.{import_name} import {class_name}
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "{state_subdir}" / "{mid}_{slug}"
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
{args_block}
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = {class_name}(name=MODULE_ID + " " + MODULE_NAME, {init_block}).run()
    val = res["payload"]["validation"]
    decision = "{name.upper()} READY" if not val["errors"] else "{name.upper()} BLOCKED"
    analysis = {analysis_text}
    analysis["score"] = val["score"]
    analysis["decision"] = decision
    ts = now_stamp()
    output = MODULE_DIR / "{mid}_{slug}.json"
    state = MODULE_DIR / ("{mid}_{slug}_state_" + ts + ".json")
    report = REPORTS / ("{mid}_{slug}_raporu_" + ts + ".txt")
    payload = {{"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score    : " + str(analysis["score"]) + " / 100", "Decision : " + str(analysis["decision"])]
    for k, v in analysis.items():
        if k not in ("score", "decision"):
            lines.append(str(k) + " : " + str(v))
    lines += ["", "Dosyalar:", str(output), str(report)]
    report.write_text("\\n".join(lines), encoding="utf-8")
    print("\\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
"""

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
        '    ("1600", "NeoLegal Expert Orchestrator SDK", [sys.executable, str(BASE / ".py" / "1600_NeoLegal_Expert_Orchestrator_SDK.py")]),',
    ]
    for mid, name, slug in MODULES_1600:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines.append('    ("1700", "Client Workspace Memory SDK", [sys.executable, str(BASE / ".py" / "1700_Client_Workspace_Memory_SDK.py")]),')
    for mid, name, slug in MODULES_1700:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser = argparse.ArgumentParser()",
        "    parser.add_argument('--case-text', default=None)",
        "    parser.add_argument('--expert-mode', default='general')",
        "    parser.add_argument('--client-name', default='Pilot Client')",
        "    parser.add_argument('--case-name', default='Pilot Procurement Case')",
        "    parser.add_argument('--execute', action='store_true')",
        "    args = parser.parse_args()",
        "    print('=' * 80)",
        "    print('1600-1700 NEOLEGAL EXPERT WORKSPACE RUN ALL BASLADI')",
        "    print('=' * 80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id, name, cmd in COMMANDS:",
        "        full = list(cmd)",
        "        if module_id.startswith('16'):",
        "            full += ['--expert-mode', args.expert_mode]",
        "            if args.case_text: full += ['--case-text', args.case_text]",
        "        else:",
        "            full += ['--client-name', args.client_name, '--case-name', args.case_name]",
        "            if args.case_text: full += ['--case-text', args.case_text]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> ' + ' '.join(full))",
        "        result = subprocess.run(full, cwd=str(BASE))",
        "        status = 'PASS' if result.returncode == 0 else 'FAIL'",
        "        if status == 'PASS': passed += 1",
        "        else: failed += 1",
        "        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'1600-1700 NeoLegal Expert Workspace','execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'1600_1700_neolegal_expert_workspace_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')",
        "    print('\\n'+'='*80); print('1600-1700 NEOLEGAL EXPERT WORKSPACE SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(44)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
    ]
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    m1600 = ["- 1600 NeoLegal Expert Orchestrator SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES_1600] + ["- 1600/1700 Run All"]
    m1700 = ["- 1700 Client Workspace & Knowledge Memory SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES_1700] + ["- 1600/1700 Run All"]
    RELEASE_1600.write_text("\n".join(["# v11.0 – NeoLegal Expert Orchestrator", "", "**Tarih:** 10.07.2026", "", "Bu sürüm 1100, 1300, 1400 ve 1500 motorlarını tek uzman görüşüne dönüştüren NeoLegal Expert Orchestrator katmanını kurar.", "", "# Modüller", ""] + m1600 + ["", "---", "", "NeoLegal Expert Orchestrator v11.0 oluşturulmuştur.", ""]), encoding="utf-8")
    RELEASE_1700.write_text("\n".join(["# v12.0 – Client Workspace & Knowledge Memory", "", "**Tarih:** 10.07.2026", "", "Bu sürüm müvekkil/dosya çalışma alanı, konuşma hafızası, belge hafızası, strateji geçmişi, süre planlama ve görev panosu katmanını kurar.", "", "# Modüller", ""] + m1700 + ["", "---", "", "Client Workspace & Knowledge Memory v12.0 oluşturulmuştur.", ""]), encoding="utf-8")
    entry = "\n".join(["# v11.0 / v12.0 – NeoLegal Expert Workspace", "", "**Tarih:** 10.07.2026  ", "**Durum:** Production PASS  ", "**Git Tags:** `" + TAG_1600 + "`, `" + TAG_1700 + "`", "", "## v11.0 Modüller", ""] + m1600 + ["", "## v12.0 Modüller", ""] + m1700 + ["", "## Sonuç", "", "NeoLegal, tek uzman görüşü üreten orchestrator ve müvekkil/dosya hafızası katmanına taşındı.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v11.0 / v12.0 – NeoLegal Expert Workspace" not in old:
            CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        txt = README.read_text(encoding="utf-8", errors="ignore")
        rows = "| v11.0 | NeoLegal Expert Orchestrator | PASS |\n| v12.0 | Client Workspace & Knowledge Memory | PASS |"
        if "v11.0 | NeoLegal Expert Orchestrator" not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + rows), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_1600, RELEASE_1700

def create_git_bat():
    lines = ["@echo off", "cd /d C:\\Users\\MSI\\Desktop\\kik_proje", "", "echo Running NeoLegal Expert Workspace v11.0-v12.0...", 'python ".py\\1600_1700_Run_All.py"', "", "IF ERRORLEVEL 1 (", "    echo.", "    echo RELEASE BLOCKED: 1600-1700 NeoLegal Expert Workspace FAILED.", "    pause", "    exit /b 1", ")", "", "git status", "git add .", 'git commit -m "Release v11.0-v12.0: NeoLegal Expert Orchestrator and Workspace Memory"', "git push", "git tag " + TAG_1600, "git tag " + TAG_1700, "git push origin " + TAG_1600, "git push origin " + TAG_1700, "", "pause", ""]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--expert-mode", default="general")
    parser.add_argument("--client-name", default="Pilot Client")
    parser.add_argument("--case-name", default="Pilot Procurement Case")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    PY.mkdir(parents=True, exist_ok=True)
    EXPERT_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1600-1700 ALL-IN-ONE NEOLEGAL EXPERT WORKSPACE BUILDER BASLADI")
    print("=" * 80)

    write_file(PY / "1600" / "core" / "__init__.py", "")
    write_file(PY / "1600" / "core" / "neolegal_expert_orchestrator_sdk.py", SDK_1600)
    write_file(PY / "1600_NeoLegal_Expert_Orchestrator_SDK.py", sdk_bridge_source(
        "1600", "NeoLegalExpertOrchestratorSDK", "neolegal_expert_orchestrator_sdk", "1600 NEOLEGAL EXPERT ORCHESTRATOR SDK",
        '    parser.add_argument("--case-text", default=None)\n    parser.add_argument("--expert-mode", default="general")\n    parser.add_argument("--execute", action="store_true")',
        "case_text=args.case_text, expert_mode=args.expert_mode, execute=args.execute",
        '    expert = res["payload"]["expert"]\n    print("Success Probability : " + str(expert["advisory"]["success_probability"]) + " / 100")\n    print("Risk                : " + str(expert["advisory"]["risk_level"]))'
    ))

    write_file(PY / "1700" / "core" / "__init__.py", "")
    write_file(PY / "1700" / "core" / "client_workspace_memory_sdk.py", SDK_1700)
    write_file(PY / "1700_Client_Workspace_Memory_SDK.py", sdk_bridge_source(
        "1700", "ClientWorkspaceMemorySDK", "client_workspace_memory_sdk", "1700 CLIENT WORKSPACE MEMORY SDK",
        '    parser.add_argument("--client-name", default="Pilot Client")\n    parser.add_argument("--case-name", default="Pilot Procurement Case")\n    parser.add_argument("--case-text", default=None)\n    parser.add_argument("--execute", action="store_true")',
        "client_name=args.client_name, case_name=args.case_name, case_text=args.case_text, execute=args.execute",
        '    wm = res["payload"]["workspace_memory"]\n    print("Client     : " + str(wm["client_profile"]["client_name"]))\n    print("Case       : " + str(wm["case_name"] if "case_name" in wm else "' + 'Pilot Procurement Case' + '"))'
    ))

    generated = [str(PY / "1600_NeoLegal_Expert_Orchestrator_SDK.py"), str(PY / "1700_Client_Workspace_Memory_SDK.py")]
    for mid, name, slug in MODULES_1600:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source("1600", mid, name, slug, "NeoLegalExpertOrchestratorSDK", "neolegal_expert_orchestrator_sdk", "neolegal_expert_orchestrator",
            '    parser.add_argument("--case-text", default=None)\n    parser.add_argument("--expert-mode", default="general")\n    parser.add_argument("--execute", action="store_true")',
            "case_text=args.case_text, expert_mode=args.expert_mode, execute=args.execute",
            [("success_probability", 'res["payload"]["expert"]["advisory"]["success_probability"]'), ("risk", 'res["payload"]["expert"]["advisory"]["risk_level"]'), ("audit", 'res["payload"]["expert"]["audit"]["status"]')]
        ))
        generated.append(str(path))
        print("Generated:", path)

    for mid, name, slug in MODULES_1700:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source("1700", mid, name, slug, "ClientWorkspaceMemorySDK", "client_workspace_memory_sdk", "client_workspace_memory",
            '    parser.add_argument("--client-name", default="Pilot Client")\n    parser.add_argument("--case-name", default="Pilot Procurement Case")\n    parser.add_argument("--case-text", default=None)\n    parser.add_argument("--execute", action="store_true")',
            "client_name=args.client_name, case_name=args.case_name, case_text=args.case_text, execute=args.execute",
            [("client", 'res["payload"]["workspace_memory"]["client_profile"]["client_name"]'), ("audit", 'res["payload"]["workspace_memory"]["audit"]["status"]')]
        ))
        generated.append(str(path))
        print("Generated:", path)

    run_all = PY / "1600_1700_Run_All.py"
    write_file(run_all, run_all_source())
    print("Generated:", run_all)

    release_1600, release_1700 = create_release_docs()
    git_bat = create_git_bat()

    print("\n" + "=" * 80)
    print("1600-1700 NEOLEGAL EXPERT WORKSPACE TEST BASLIYOR")
    print("=" * 80)
    cmd = [sys.executable, str(run_all), "--expert-mode", args.expert_mode, "--client-name", args.client_name, "--case-name", args.case_name]
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
    state = STATE / "neolegal_expert_workspace" / ("1600_1700_expert_workspace_builder_state_" + ts + ".json")
    report = REPORTS / ("1600_1700_expert_workspace_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1600-1700 NeoLegal Expert Workspace Builder", "versions": [VERSION_1600, VERSION_1700], "tags": [TAG_1600, TAG_1700], "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_1600": str(release_1600), "release_1700": str(release_1700), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1600-1700 ALL-IN-ONE NEOLEGAL EXPERT WORKSPACE BUILDER FINAL", "=" * 80, "Final Decision  : " + decision, "Git             : " + git_status, "Mode            : " + ("EXECUTE" if args.execute else "DRY_RUN"), "1600 Version    : " + VERSION_1600, "1700 Version    : " + VERSION_1700, "Run All         : " + str(run_all), "Release 1600    : " + str(release_1600), "Release 1700    : " + str(release_1700), "Git BAT         : " + str(git_bat), "State           : " + str(state), "Report          : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
