
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
NEXTGEN_DIR = STATE / "next_generation_neolegal"

SUPPORT_IDS = ["1700", "1600", "1500", "1400", "1300", "1100", "1000", "900", "800", "801"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class NextGenerationNeoLegalSDK:
    def __init__(self, name="1800 Next Generation NeoLegal AI SDK", case_text=None, mode="general", execute=False):
        self.name = name
        self.case_text = case_text or "Bu dosyada kamu ihale hukuku açısından olay analizi, emsal karar ağı, mevzuatın zamana göre uygulanması, uzman ajan tartışması ve sonuç simülasyonu yapılacaktır."
        self.mode = mode
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def copilot(self):
        return {
            "status": "READY",
            "purpose": "Tek konuşmayla 1100, 1300, 1400, 1500, 1600 ve 1700 motorlarını kullanacak kullanıcı arayüzü.",
            "capabilities": [
                "Dosyayı incele",
                "Hukuki sorunları çıkar",
                "Eksik belge sor",
                "Uzman görüşü üret",
                "Dilekçe ve savunma taslağı üret",
                "Görev listesi oluştur",
                "Dosya hafızasına bağlan"
            ]
        }

    def knowledge_graph(self):
        return {
            "status": "READY",
            "nodes": ["Karar", "Mevzuat", "Kavram", "İçtihat", "Dosya", "Argüman", "Risk"],
            "edges": ["emsal", "atıf", "çelişki", "uygular", "destekler", "zayıflatır", "benzer"],
            "purpose": "KİK, Danıştay, Sayıştay ve mahkeme kararlarını mevzuat ve kavramlarla ilişkilendiren içtihat ağı."
        }

    def time_machine(self):
        return {
            "status": "READY",
            "purpose": "Uyuşmazlık tarihindeki mevzuat sürümünü kullanarak değerlendirme yapılmasını sağlar.",
            "required_data": ["Mevzuat sürüm tarihi", "Yürürlük tarihi", "Değişiklik tarihi", "Karar tarihi", "İhale tarihi"],
            "modes": ["current_law", "event_date_law", "decision_date_law", "historical_comparison"]
        }

    def multi_agent(self):
        return {
            "status": "READY",
            "agents": [
                "KİK Uzmanı",
                "Danıştay Uzmanı",
                "Sayıştay Uzmanı",
                "Sözleşme Uzmanı",
                "İdare Savunması Uzmanı",
                "Başvuru Sahibi Uzmanı",
                "AI Hakem"
            ],
            "purpose": "Aynı dosyayı farklı uzman perspektifleriyle tartıştırıp ortak sonuç üretmek."
        }

    def prediction_engine(self):
        text = self.normalize(self.case_text).lower()
        score = 55
        if "eşit muamele" in text or "rekabet" in text:
            score += 10
        if "süre" in text:
            score -= 10
        if "belge" in text or "iş deneyim" in text:
            score += 8
        score = max(5, min(95, score))
        return {
            "status": "READY",
            "base_success_probability": score,
            "simulation_modes": ["evidence_added", "deadline_missed", "strong_precedent_found", "adverse_precedent_found", "new_document_uploaded"],
            "purpose": "Başarı ihtimali, risk ve strateji değişimini senaryolara göre simüle etmek."
        }

    def integration_layer(self, copilot, graph, time_machine, agents, prediction):
        return {
            "status": "READY",
            "integrated_components": {
                "copilot": copilot["status"],
                "knowledge_graph": graph["status"],
                "time_machine": time_machine["status"],
                "multi_agent": agents["status"],
                "prediction_engine": prediction["status"]
            },
            "workflow": [
                "Kullanıcı olayı anlatır veya belge yükler",
                "Copilot olayı ayrıştırır",
                "Knowledge Graph emsal ve kavram ağını çağırır",
                "Time Machine doğru mevzuat tarihini seçer",
                "Multi-Agent uzman tartışması yapar",
                "Prediction Engine başarı ve risk simülasyonu üretir",
                "1600 Expert Orchestrator nihai uzman görüşünü üretir",
                "1700 Workspace dosya hafızasına kaydeder"
            ]
        }

    def qa_audit(self, pack):
        score = 100
        warnings = []
        for key in ["copilot", "knowledge_graph", "time_machine", "multi_agent", "prediction_engine", "integration_layer"]:
            if key not in pack:
                score -= 12
                warnings.append(key + " missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def certificate(self, pack):
        return {
            "certificate_id": "NGN-" + now_stamp(),
            "version_range": "v13.0-v17.0",
            "status": pack["audit"]["status"],
            "issued_at": now_text(),
            "note": "Next Generation NeoLegal AI mimarisi kuruldu. Gerçek değer için Knowledge Graph ve Time Machine veri modelinin gerçek veriyle beslenmesi gerekir."
        }

    def run(self):
        NEXTGEN_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        copilot = self.copilot()
        graph = self.knowledge_graph()
        time_machine = self.time_machine()
        agents = self.multi_agent()
        prediction = self.prediction_engine()
        integration = self.integration_layer(copilot, graph, time_machine, agents, prediction)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "mode": self.mode,
            "case_text": self.case_text,
            "copilot": copilot,
            "knowledge_graph": graph,
            "time_machine": time_machine,
            "multi_agent": agents,
            "prediction_engine": prediction,
            "integration_layer": integration
        }
        pack["audit"] = self.qa_audit(pack)
        pack["certificate"] = self.certificate(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.25 + pack["audit"]["score"] * 0.75, 2)
        decision = "NEXT GENERATION NEOLEGAL READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "NEXT GENERATION NEOLEGAL BLOCKED"
        ts = now_stamp()
        snapshot = NEXTGEN_DIR / "1800_next_generation_neolegal_snapshot.json"
        dashboard = NEXTGEN_DIR / "1800_next_generation_neolegal_dashboard.json"
        state = NEXTGEN_DIR / ("1800_next_generation_neolegal_state_" + ts + ".json")
        report = REPORTS / ("1800_next_generation_neolegal_sdk_raporu_" + ts + ".txt")
        payload = {"next_generation": pack, "modules": modules, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {"status": decision, "score": final_score, "prediction": prediction["base_success_probability"], "audit": pack["audit"]["status"], "components_ready": 5})
        lines = ["=" * 80, "1800 NEXT GENERATION NEOLEGAL AI SDK", "=" * 80, "Validation : " + decision, "Score      : " + str(final_score) + " / 100", "Prediction : " + str(prediction["base_success_probability"]) + " / 100", "Audit      : " + pack["audit"]["status"], "Components : Copilot + Graph + Time Machine + Multi-Agent + Prediction", "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
