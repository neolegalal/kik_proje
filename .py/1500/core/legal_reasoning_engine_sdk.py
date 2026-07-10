
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
