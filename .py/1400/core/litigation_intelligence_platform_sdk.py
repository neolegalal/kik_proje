
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
