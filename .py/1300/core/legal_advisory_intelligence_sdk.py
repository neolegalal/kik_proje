
# -*- coding: utf-8 -*-
import json, sqlite3, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
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
        return re.sub(r"\s+", " ", text or "").strip()

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
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
