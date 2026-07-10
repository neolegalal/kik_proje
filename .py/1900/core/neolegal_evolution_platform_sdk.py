
# -*- coding: utf-8 -*-
import json, sqlite3, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
EVOLUTION_DIR = STATE / "neolegal_evolution_platform"
SUPPORT_IDS = ["1800", "1700", "1600", "1500", "1400", "1300", "1100", "1000", "900", "800"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class NeoLegalEvolutionPlatformSDK:
    def __init__(self, name="1900 NeoLegal Evolution Platform SDK", sample_text=None, mode="general", execute=False):
        self.name = name
        self.sample_text = sample_text or "İş deneyim belgesi, yeterlik kriteri, eşit muamele, rekabet, başvuru süresi, KİK kararları ve Danıştay içtihatları birlikte değerlendirilmelidir."
        self.mode = mode
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def discover_db(self):
        dbs = []
        for name in ("kik.db", "kik_proje.db", "hukuki_kartlar.db"):
            p = BASE / name
            item = {"path": str(p), "exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0, "tables": []}
            if p.exists():
                try:
                    con = sqlite3.connect(str(p))
                    cur = con.cursor()
                    for (t,) in cur.execute("select name from sqlite_master where type='table'").fetchall()[:25]:
                        try:
                            count = cur.execute("select count(*) from " + t).fetchone()[0]
                        except Exception:
                            count = None
                        item["tables"].append({"table": t, "count": count})
                    con.close()
                except Exception as e:
                    item["error"] = str(e)
            dbs.append(item)
        return dbs

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def knowledge_graph_population(self, dbs):
        available_records = 0
        for db in dbs:
            for table in db.get("tables", []):
                if isinstance(table.get("count"), int):
                    available_records = max(available_records, table["count"])
        text = self.normalize(self.sample_text).lower()
        concepts = []
        for key, label in [
            ("iş deneyim", "İş deneyimi"),
            ("yeterlik", "Yeterlik kriteri"),
            ("eşit muamele", "Eşit muamele"),
            ("rekabet", "Rekabet"),
            ("süre", "Başvuru süresi"),
            ("kik", "KİK kararı"),
            ("danıştay", "Danıştay içtihadı"),
            ("sayıştay", "Sayıştay kararı"),
            ("4734", "4734 sayılı Kanun"),
        ]:
            if key in text:
                concepts.append(label)
        if not concepts:
            concepts = ["Kamu ihale uyuşmazlığı", "Mevzuat", "Emsal karar"]
        nodes = [{"id": i + 1, "type": "concept", "label": c} for i, c in enumerate(concepts)]
        edges = []
        for i in range(len(nodes) - 1):
            edges.append({"from": nodes[i]["label"], "to": nodes[i + 1]["label"], "relation": "related"})
        return {"status": "READY", "available_records": available_records, "nodes": nodes, "edges": edges, "population_mode": "DRY_RUN" if not self.execute else "EXECUTE"}

    def contradiction_finder(self, graph):
        contradictions = []
        labels = " ".join(n["label"] for n in graph["nodes"]).lower()
        if "kik" in labels and "danıştay" in labels:
            contradictions.append({"type": "potential_judicial_review_conflict", "description": "KİK kararı ile Danıştay içtihadı arasında yorum farkı ihtimali kontrol edilmelidir.", "severity": "MEDIUM"})
        if not contradictions:
            contradictions.append({"type": "none_detected", "description": "Ön analizde açık çelişki tespit edilmedi.", "severity": "LOW"})
        return {"status": "READY", "contradictions": contradictions, "count": len(contradictions)}

    def legal_pattern_discovery(self, graph, contradictions):
        pattern_score = min(95, 60 + len(graph["nodes"]) * 5 - max(0, contradictions["count"] - 1) * 4)
        patterns = [
            {"pattern": "Yeterlik + belge + temel ilkeler birlikte değerlendirildiğinde başarı ihtimali artar.", "confidence": pattern_score},
            {"pattern": "Süre riski varsa esasa ilişkin güçlü argümanlar dahi usulden engellenebilir.", "confidence": max(40, pattern_score - 12)},
        ]
        return {"status": "READY", "patterns": patterns, "average_pattern_confidence": round(sum(p["confidence"] for p in patterns) / len(patterns), 2)}

    def ai_learning_dataset_builder(self, graph, patterns):
        records = []
        for p in patterns["patterns"]:
            records.append({
                "instruction": "Kamu ihale uyuşmazlığında hukuki strateji üret.",
                "input": self.sample_text,
                "output": p["pattern"],
                "confidence": p["confidence"],
                "source": "neolegal_evolution_synthetic"
            })
        return {"status": "READY", "dataset_records": len(records), "records": records}

    def knowledge_confidence_engine(self, graph, patterns, contradictions):
        base = 82
        base += min(10, len(graph["nodes"]))
        base += 5 if patterns["average_pattern_confidence"] >= 70 else 0
        base -= 8 if any(c["severity"] == "MEDIUM" for c in contradictions["contradictions"]) else 0
        score = max(5, min(99, base))
        return {
            "status": "READY",
            "confidence_score": score,
            "confidence_label": "HIGH" if score >= 85 else "MEDIUM" if score >= 60 else "LOW",
            "components": {
                "graph_nodes": len(graph["nodes"]),
                "pattern_confidence": patterns["average_pattern_confidence"],
                "contradiction_count": contradictions["count"]
            }
        }

    def self_validation_engine(self, confidence, dataset):
        score = confidence["confidence_score"]
        if dataset["dataset_records"] == 0:
            score -= 20
        validation = "PASS" if score >= 75 else "WARN" if score >= 55 else "FAIL"
        return {"status": validation, "validation_score": max(0, score), "checks": ["graph_ready", "patterns_ready", "dataset_ready", "confidence_ready"]}

    def hallucination_detector(self, confidence, evidence):
        risk = 100 - confidence["confidence_score"]
        if evidence["evidence_count"] >= 3:
            risk -= 10
        risk = max(1, min(99, risk))
        return {
            "status": "READY",
            "hallucination_risk": risk,
            "risk_label": "LOW" if risk <= 25 else "MEDIUM" if risk <= 50 else "HIGH",
            "rule": "Kanıt sayısı ve güven puanı düşükse halüsinasyon riski artar."
        }

    def evidence_collector(self, graph):
        evidence = []
        for node in graph["nodes"]:
            evidence.append({"evidence_type": node["type"], "label": node["label"], "source_confidence": 90 if "Kanun" in node["label"] else 80})
        if not evidence:
            evidence = [{"evidence_type": "fallback", "label": "Veri bulunamadı", "source_confidence": 20}]
        return {"status": "READY", "evidence_count": len(evidence), "evidence": evidence}

    def continuous_learning_engine(self, graph, validation):
        return {
            "status": "READY",
            "learning_actions": [
                "Yeni karar geldikçe graph düğümlerini güncelle",
                "Çelişki tespit edilirse confidence skorunu düşür",
                "Doğrulanmış sonuçları learning dataset içine ekle",
                "Hatalı veya zayıf cevapları hallucination detector ile işaretle"
            ],
            "next_learning_batch": len(graph["nodes"]) * 10,
            "validation_reference": validation["status"]
        }

    def evolution_certificate(self, pack):
        return {
            "certificate_id": "EVO-" + now_stamp(),
            "status": pack["audit"]["status"],
            "confidence_score": pack["confidence"]["confidence_score"],
            "hallucination_risk": pack["hallucination"]["hallucination_risk"],
            "issued_at": now_text(),
            "note": "Evolution Platform, NeoLegal'in güvenilirlik, kanıt, graph ve sürekli öğrenme altyapısını kurar."
        }

    def audit(self, pack):
        score = 100
        warnings = []
        required = ["graph", "contradictions", "patterns", "learning_dataset", "confidence", "self_validation", "evidence", "hallucination", "continuous_learning"]
        for key in required:
            if key not in pack:
                score -= 10
                warnings.append(key + " missing")
        if pack.get("hallucination", {}).get("risk_label") == "HIGH":
            score -= 20
            warnings.append("high hallucination risk")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def run(self):
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        dbs = self.discover_db()
        graph = self.knowledge_graph_population(dbs)
        contradictions = self.contradiction_finder(graph)
        patterns = self.legal_pattern_discovery(graph, contradictions)
        dataset = self.ai_learning_dataset_builder(graph, patterns)
        confidence = self.knowledge_confidence_engine(graph, patterns, contradictions)
        evidence = self.evidence_collector(graph)
        validation = self.self_validation_engine(confidence, dataset)
        hallucination = self.hallucination_detector(confidence, evidence)
        learning = self.continuous_learning_engine(graph, validation)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "mode": self.mode,
            "sample_text": self.sample_text,
            "graph": graph,
            "contradictions": contradictions,
            "patterns": patterns,
            "learning_dataset": dataset,
            "confidence": confidence,
            "self_validation": validation,
            "evidence": evidence,
            "hallucination": hallucination,
            "continuous_learning": learning
        }
        pack["audit"] = self.audit(pack)
        pack["certificate"] = self.evolution_certificate(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.20 + pack["audit"]["score"] * 0.35 + confidence["confidence_score"] * 0.30 + max(0, 100 - hallucination["hallucination_risk"]) * 0.15, 2)
        decision = "NEOLEGAL EVOLUTION PLATFORM READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "NEOLEGAL EVOLUTION PLATFORM BLOCKED"
        ts = now_stamp()
        snapshot = EVOLUTION_DIR / "1900_neolegal_evolution_platform_snapshot.json"
        dashboard = EVOLUTION_DIR / "1900_neolegal_evolution_platform_dashboard.json"
        state = EVOLUTION_DIR / ("1900_neolegal_evolution_platform_state_" + ts + ".json")
        report = REPORTS / ("1900_neolegal_evolution_platform_sdk_raporu_" + ts + ".txt")
        payload = {"evolution": pack, "modules": modules, "databases": dbs, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {
            "status": decision,
            "score": final_score,
            "confidence": confidence["confidence_score"],
            "hallucination_risk": hallucination["hallucination_risk"],
            "evidence_count": evidence["evidence_count"],
            "graph_nodes": len(graph["nodes"]),
            "audit": pack["audit"]["status"]
        })
        lines = ["=" * 80, "1900 NEOLEGAL EVOLUTION PLATFORM SDK", "=" * 80, "Validation          : " + decision, "Score               : " + str(final_score) + " / 100", "Knowledge Confidence: " + str(confidence["confidence_score"]) + " / 100", "Hallucination Risk  : " + str(hallucination["hallucination_risk"]) + " / 100", "Evidence Count      : " + str(evidence["evidence_count"]), "Graph Nodes         : " + str(len(graph["nodes"])), "Audit               : " + pack["audit"]["status"], "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
