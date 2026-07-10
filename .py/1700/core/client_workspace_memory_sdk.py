
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
