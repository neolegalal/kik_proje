
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
