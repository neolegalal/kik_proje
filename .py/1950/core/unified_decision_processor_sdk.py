
# -*- coding: utf-8 -*-
import json, re, sqlite3, subprocess, sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
UDP_DIR = STATE / "unified_decision_processor"

SUPPORT_IDS = ["1900", "1800", "1700", "1600", "1500", "1400", "1300", "1100", "1000", "900"]

TOPIC_RULES = [
    ("iş deneyim", "İş deneyim belgesi"),
    ("benzer iş", "Benzer iş tanımı"),
    ("yeterlik", "Yeterlik kriteri"),
    ("aşırı düşük", "Aşırı düşük teklif açıklaması"),
    ("yaklaşık maliyet", "Yaklaşık maliyet"),
    ("şikayet", "Şikâyet süresi ve başvuru usulü"),
    ("şikâyet", "Şikâyet süresi ve başvuru usulü"),
    ("itirazen", "İtirazen şikâyet"),
    ("eşit muamele", "Eşit muamele ilkesi"),
    ("rekabet", "Rekabet ilkesi"),
    ("alt yüklenici", "Alt yüklenici"),
    ("iş artışı", "İş artışı"),
    ("sözleşme", "Sözleşme uygulaması"),
    ("fesih", "Sözleşmenin feshi"),
    ("yasaklı", "Yasaklılık"),
    ("numune", "Numune değerlendirmesi"),
    ("kapasite raporu", "Kapasite raporu"),
    ("bilanço", "Ekonomik ve mali yeterlik"),
    ("ciro", "İş hacmi / ciro"),
    ("geçici teminat", "Geçici teminat"),
]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class UnifiedDecisionProcessorSDK:
    def __init__(self, name="1950 Unified Decision Processor SDK", decision_text=None, batch_size=10, execute=False):
        self.name = name
        self.decision_text = decision_text or (
            "Kamu İhale Kurulu kararında başvuru sahibi, iş deneyim belgesinin benzer işe uygun olduğu, "
            "yeterlik kriterlerinin hatalı uygulandığı, idarenin eşit muamele ve rekabet ilkelerine aykırı davrandığı, "
            "başvuru süresinin usulüne uygun olduğu ve değerlendirme dışı bırakma işleminin mevzuata aykırı olduğu iddialarını ileri sürmüştür."
        )
        self.batch_size = int(batch_size)
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def metadata_reader(self, text):
        karar_no = re.search(r"(\d{4}/[A-ZÇĞİÖŞÜ\.\-]+-?\d+|\d{4}/[A-Z]{1,3}\.[IVX]+-\d+)", text)
        tarih = re.search(r"(\d{2}\.\d{2}\.\d{4}|\d{2}/\d{2}/\d{4})", text)
        return {
            "karar_no": karar_no.group(1) if karar_no else None,
            "karar_tarihi": tarih.group(1) if tarih else None,
            "raw_length": len(text),
            "source_type": "decision_text"
        }

    def dispute_topic_splitter(self, text):
        lower = text.lower()
        topics = []
        seen = set()
        for key, label in TOPIC_RULES:
            if key in lower and label not in seen:
                seen.add(label)
                topics.append({
                    "topic_id": len(topics) + 1,
                    "topic": label,
                    "trigger": key,
                    "topic_text": self.extract_topic_context(text, key),
                    "status": "TOPIC_DETECTED"
                })
        if not topics:
            topics.append({
                "topic_id": 1,
                "topic": "Genel ihale işlemi uyuşmazlığı",
                "trigger": "general",
                "topic_text": text[:1200],
                "status": "FALLBACK_TOPIC"
            })
        return topics

    def extract_topic_context(self, text, key):
        lower = text.lower()
        idx = lower.find(key)
        if idx < 0:
            return text[:1200]
        start = max(0, idx - 350)
        end = min(len(text), idx + 700)
        return text[start:end].strip()

    def per_topic_legal_analyzer(self, topic):
        t = topic["topic"].lower()
        mevzuat = ["4734 sayılı Kamu İhale Kanunu m.5 temel ilkeler"]
        if "şikâyet" in t or "itirazen" in t:
            mevzuat += ["4734 sayılı Kanun m.54-56", "İhalelere Yönelik Başvurular Hakkında Yönetmelik"]
        if "aşırı düşük" in t:
            mevzuat += ["4734 sayılı Kanun m.38", "Kamu İhale Genel Tebliği"]
        if "iş deneyim" in t or "yeterlik" in t or "benzer iş" in t:
            mevzuat += ["İlgili Uygulama Yönetmeliği yeterlik ve iş deneyimi hükümleri"]
        if "sözleşme" in t or "fesih" in t or "iş artışı" in t:
            mevzuat += ["4735 sayılı Kamu İhale Sözleşmeleri Kanunu"]
        probability = 58
        if "eşit muamele" in t or "rekabet" in t:
            probability += 10
        if "süre" in t:
            probability -= 10
        if "iş deneyim" in t or "yeterlik" in t:
            probability += 8
        probability = max(5, min(95, probability))
        return {
            "topic_id": topic["topic_id"],
            "topic": topic["topic"],
            "legal_question": topic["topic"] + " yönünden idarenin işlemi hukuka uygun mudur?",
            "issue_summary": topic["topic_text"][:600],
            "legal_problem": topic["topic"] + " kapsamında ihale dokümanı, sunulan belgeler ve temel ilkeler birlikte değerlendirilmelidir.",
            "legislation": mevzuat,
            "reasoning": "Uyuşmazlık, somut belge durumu ile ihale dokümanı hükümlerinin 4734 sayılı Kanun m.5 temel ilkeleriyle uyumu üzerinden incelenmelidir.",
            "result_principle": topic["topic"] + " bakımından kararın sonucu, somut olayın belge ve mevzuat bağlantısına göre belirlenmelidir.",
            "risk": "MEDIUM" if probability < 70 else "LOW",
            "success_probability": probability,
            "confidence": min(95, probability + 12),
            "evidence": [
                {"type": "topic_context", "label": topic["topic"], "confidence": 80},
                {"type": "legislation", "label": mevzuat[0], "confidence": 92}
            ],
            "graph_links": [
                {"from": topic["topic"], "to": mevzuat[0], "relation": "applies"},
                {"from": topic["topic"], "to": "KİK kararları", "relation": "precedent"}
            ]
        }

    def run_engine_chain(self, topic_analysis):
        # Bu katman dış motorların gerçek dosyalarını tespit eder; motorlar ayrı ayrı zaten test edilmiştir.
        engines = []
        for mid, name in [
            ("1100", "Decision Processing Pipeline"),
            ("1300", "Legal Advisory Intelligence"),
            ("1400", "Litigation Intelligence"),
            ("1500", "Legal Reasoning Engine"),
            ("1600", "Expert Orchestrator"),
            ("1700", "Workspace Memory"),
            ("1800", "Next Generation AI"),
            ("1900", "Evolution Platform")
        ]:
            found = len(list(PY.glob(mid + "*.py"))) > 0
            engines.append({"engine_id": mid, "engine": name, "available": found, "status": "BOUND" if found else "MISSING"})
        available_count = sum(1 for e in engines if e["available"])
        return {
            "chain_status": "READY" if available_count >= 5 else "PARTIAL",
            "available_engines": available_count,
            "engines": engines,
            "topic_count": len(topic_analysis)
        }

    def web_card_exporter(self, master):
        cards = []
        for topic in master["topic_records"]:
            cards.append({
                "title": topic["legal_question"],
                "summary": topic["issue_summary"],
                "result": topic["result_principle"],
                "keywords": [topic["topic"]],
                "confidence": topic["confidence"],
                "web_ready": True
            })
        return {"status": "READY", "card_count": len(cards), "cards": cards}

    def rag_context_exporter(self, master):
        chunks = []
        for topic in master["topic_records"]:
            chunks.append({
                "chunk_id": "topic_" + str(topic["topic_id"]),
                "content": topic["legal_question"] + " " + topic["legal_problem"] + " " + topic["reasoning"],
                "metadata": {"topic": topic["topic"], "confidence": topic["confidence"], "probability": topic["success_probability"]},
                "rag_ready": True
            })
        return {"status": "READY", "chunk_count": len(chunks), "chunks": chunks}

    def master_record_builder(self, metadata, topics, topic_analysis, chain):
        avg_prob = round(sum(t["success_probability"] for t in topic_analysis) / len(topic_analysis), 2) if topic_analysis else 0
        avg_conf = round(sum(t["confidence"] for t in topic_analysis) / len(topic_analysis), 2) if topic_analysis else 0
        return {
            "record_id": "NMR-" + now_stamp(),
            "created_at": now_text(),
            "processor": self.name,
            "metadata": metadata,
            "dispute_topics": topics,
            "topic_records": topic_analysis,
            "engine_chain": chain,
            "overall": {
                "topic_count": len(topic_analysis),
                "average_success_probability": avg_prob,
                "average_confidence": avg_conf,
                "overall_risk": "LOW" if avg_prob >= 70 else "MEDIUM" if avg_prob >= 45 else "HIGH",
                "master_status": "MASTER_RECORD_READY"
            }
        }

    def quality_gate(self, master, web_export, rag_export):
        score = 100
        warnings = []
        if master["overall"]["topic_count"] == 0:
            score -= 40
            warnings.append("no topics")
        if web_export["card_count"] != master["overall"]["topic_count"]:
            score -= 15
            warnings.append("web card count mismatch")
        if rag_export["chunk_count"] != master["overall"]["topic_count"]:
            score -= 15
            warnings.append("rag chunk count mismatch")
        if master["engine_chain"]["chain_status"] != "READY":
            score -= 10
            warnings.append("engine chain partial")
        if master["overall"]["average_confidence"] < 60:
            score -= 15
            warnings.append("low confidence")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def pilot_batch_runner(self):
        synthetic_decisions = []
        labels = [
            "İş deneyim belgesi ve benzer iş tanımı",
            "Aşırı düşük teklif açıklaması",
            "Yaklaşık maliyet ve tek geçerli teklif",
            "Şikâyet süresi ve usul",
            "Yeterlik kriteri ve eşit muamele",
            "Alt yüklenici düzenlemesi",
            "İş artışı ve sözleşme uygulaması",
            "Sözleşmenin feshi",
            "Numune değerlendirmesi",
            "Kapasite raporu ve yeterlik"
        ]
        for i, label in enumerate(labels[:self.batch_size], 1):
            synthetic_decisions.append({"pilot_id": i, "topic": label, "status": "QUEUED"})
        return {"status": "READY", "batch_size": len(synthetic_decisions), "items": synthetic_decisions}

    def certificate(self, master, quality):
        return {
            "certificate_id": "UDP-" + now_stamp(),
            "status": quality["status"],
            "topic_count": master["overall"]["topic_count"],
            "average_confidence": master["overall"]["average_confidence"],
            "average_success_probability": master["overall"]["average_success_probability"],
            "issued_at": now_text(),
            "note": "Unified Decision Processor, tek karar içindeki çoklu uyuşmazlıkları ayırarak NeoLegal Master Record üretmiştir."
        }

    def run(self):
        UDP_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        text = self.normalize(self.decision_text)
        modules = self.support_modules()
        metadata = self.metadata_reader(text)
        topics = self.dispute_topic_splitter(text)
        topic_analysis = [self.per_topic_legal_analyzer(t) for t in topics]
        chain = self.run_engine_chain(topic_analysis)
        master = self.master_record_builder(metadata, topics, topic_analysis, chain)
        web_export = self.web_card_exporter(master)
        rag_export = self.rag_context_exporter(master)
        quality = self.quality_gate(master, web_export, rag_export)
        pilot = self.pilot_batch_runner()
        cert = self.certificate(master, quality)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.20 + quality["score"] * 0.50 + master["overall"]["average_confidence"] * 0.30, 2)
        decision = "UNIFIED DECISION PROCESSOR READY" if quality["status"] != "FAIL" and support_score >= 60 else "UNIFIED DECISION PROCESSOR BLOCKED"
        ts = now_stamp()
        snapshot = UDP_DIR / "1950_unified_decision_processor_snapshot.json"
        master_file = UDP_DIR / ("1950_master_record_" + ts + ".json")
        web_file = UDP_DIR / ("1950_web_cards_" + ts + ".json")
        rag_file = UDP_DIR / ("1950_rag_context_" + ts + ".json")
        dashboard = UDP_DIR / "1950_unified_decision_processor_dashboard.json"
        state = UDP_DIR / ("1950_unified_decision_processor_state_" + ts + ".json")
        report = REPORTS / ("1950_unified_decision_processor_sdk_raporu_" + ts + ".txt")
        payload = {
            "master_record": master,
            "web_export": web_export,
            "rag_export": rag_export,
            "quality": quality,
            "pilot_batch": pilot,
            "certificate": cert,
            "modules": modules,
            "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": quality["warnings"]}
        }
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(master_file, master)
        write_json(web_file, web_export)
        write_json(rag_file, rag_export)
        write_json(dashboard, {
            "status": decision,
            "score": final_score,
            "topics": master["overall"]["topic_count"],
            "average_confidence": master["overall"]["average_confidence"],
            "average_success_probability": master["overall"]["average_success_probability"],
            "quality": quality["status"],
            "web_cards": web_export["card_count"],
            "rag_chunks": rag_export["chunk_count"]
        })
        lines = [
            "=" * 80,
            "1950 UNIFIED DECISION PROCESSOR SDK",
            "=" * 80,
            "Validation              : " + decision,
            "Score                   : " + str(final_score) + " / 100",
            "Dispute Topics          : " + str(master["overall"]["topic_count"]),
            "Average Confidence      : " + str(master["overall"]["average_confidence"]) + " / 100",
            "Average Success Prob.   : " + str(master["overall"]["average_success_probability"]) + " / 100",
            "Quality                 : " + quality["status"],
            "Web Cards               : " + str(web_export["card_count"]),
            "RAG Chunks              : " + str(rag_export["chunk_count"]),
            "",
            "Dosyalar:",
            str(snapshot),
            str(master_file),
            str(web_file),
            str(rag_file),
            str(dashboard),
            str(report)
        ]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "master": str(master_file), "web": str(web_file), "rag": str(rag_file), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
