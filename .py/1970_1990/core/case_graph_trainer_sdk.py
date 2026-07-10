
# -*- coding: utf-8 -*-
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
CGT_DIR = STATE / "case_graph_trainer"
UDP_DIR = STATE / "unified_decision_processor"
SUPPORT_IDS = ["1950", "1900", "1800", "1700", "1600", "1500", "1400", "1300", "1100"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class CaseGraphTrainerSDK:
    def __init__(self, name="1970-1990 Case Graph Trainer SDK", master_record_path=None, case_text=None, execute=False):
        self.name = name
        self.master_record_path = Path(master_record_path) if master_record_path else None
        self.case_text = case_text or "İş deneyim belgesi, benzer iş, yeterlik kriteri, şikâyet süresi, eşit muamele ve rekabet ilkeleri birlikte değerlendirilmiştir."
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits)})
        return rows

    def load_master_record(self):
        if self.master_record_path and self.master_record_path.exists():
            try:
                return json.loads(self.master_record_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        latest = sorted(UDP_DIR.glob("1950_master_record_*.json"), reverse=True)
        if latest:
            try:
                return json.loads(latest[0].read_text(encoding="utf-8"))
            except Exception:
                pass
        topics = []
        for i, topic in enumerate(["İş deneyim belgesi", "Benzer iş tanımı", "Yeterlik kriteri", "Şikâyet süresi", "Eşit muamele ilkesi", "Rekabet ilkesi"], 1):
            topics.append({
                "topic_id": i,
                "topic": topic,
                "legal_question": topic + " yönünden idarenin işlemi hukuka uygun mudur?",
                "issue_summary": self.case_text,
                "legal_problem": topic + " bakımından uyuşmazlık değerlendirilmelidir.",
                "legislation": ["4734 sayılı Kamu İhale Kanunu m.5 temel ilkeler"],
                "success_probability": 60 + i,
                "confidence": 75 + i,
                "risk": "MEDIUM",
                "evidence": [{"type": "synthetic", "label": topic, "confidence": 80}],
                "graph_links": [{"from": topic, "to": "4734 m.5", "relation": "applies"}]
            })
        return {
            "record_id": "NMR-SYNTHETIC-" + now_stamp(),
            "created_at": now_text(),
            "metadata": {"source_type": "synthetic"},
            "topic_records": topics,
            "overall": {"topic_count": len(topics), "average_success_probability": 63, "average_confidence": 78, "overall_risk": "MEDIUM"}
        }

    def case_intelligence(self, master):
        topics = master.get("topic_records", [])
        scored = []
        for t in topics:
            base = 50
            topic = t.get("topic", "")
            if "İş deneyim" in topic or "Yeterlik" in topic:
                base += 20
            if "Şikâyet" in topic or "süre" in topic.lower():
                base += 15
            if "Eşit muamele" in topic or "Rekabet" in topic:
                base += 12
            base += min(10, int(t.get("confidence", 70)) - 70) if t.get("confidence", 70) > 70 else 0
            scored.append({**t, "priority_score": min(100, base), "role": "UNCLASSIFIED"})
        scored = sorted(scored, key=lambda x: x["priority_score"], reverse=True)
        for i, t in enumerate(scored):
            t["role"] = "MAIN_ISSUE" if i == 0 else "IMPORTANT_SUB_ISSUE" if i <= 2 else "SUB_ISSUE"
            t["result_impact"] = "HIGH" if i == 0 else "MEDIUM" if i <= 2 else "LOW"
        return {
            "status": "READY",
            "main_issue": scored[0] if scored else None,
            "prioritized_topics": scored,
            "topic_count": len(scored),
            "case_structure": "multi_issue" if len(scored) > 1 else "single_issue"
        }

    def graph_builder(self, master, intelligence):
        nodes = []
        edges = []
        seen = set()
        def add_node(ntype, label):
            key = ntype + "::" + label
            if key not in seen:
                seen.add(key)
                nodes.append({"id": len(nodes) + 1, "type": ntype, "label": label})
        add_node("case", master.get("record_id", "case"))
        for t in intelligence["prioritized_topics"]:
            topic = t.get("topic", "Konu")
            add_node("issue", topic)
            edges.append({"from": master.get("record_id", "case"), "to": topic, "relation": t.get("role", "related")})
            for leg in t.get("legislation", []):
                add_node("legislation", leg)
                edges.append({"from": topic, "to": leg, "relation": "applies"})
            for gl in t.get("graph_links", []):
                add_node("concept", gl.get("to", "concept"))
                edges.append({"from": gl.get("from", topic), "to": gl.get("to", "concept"), "relation": gl.get("relation", "related")})
        return {
            "status": "READY",
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "graph_type": "legal_case_knowledge_graph"
        }

    def dataset_factory(self, master, intelligence, graph):
        instruction = []
        rag = []
        fine_tuning = []
        evals = []
        for t in intelligence["prioritized_topics"]:
            question = t.get("legal_question", t.get("topic", "Hukuki soru"))
            answer = t.get("legal_problem", "") + " " + t.get("issue_summary", "")
            instruction.append({"instruction": "Kamu ihale uyuşmazlığını analiz et.", "input": question, "output": answer, "priority": t.get("priority_score")})
            rag.append({"chunk_id": "issue_" + str(t.get("topic_id")), "content": question + " " + answer, "metadata": {"topic": t.get("topic"), "role": t.get("role"), "confidence": t.get("confidence")}})
            fine_tuning.append({"messages": [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]})
            evals.append({"question": question, "expected_topic": t.get("topic"), "expected_role": t.get("role")})
        return {
            "status": "READY",
            "instruction_dataset": instruction,
            "rag_dataset": rag,
            "fine_tuning_dataset": fine_tuning,
            "evaluation_dataset": evals,
            "counts": {
                "instruction": len(instruction),
                "rag": len(rag),
                "fine_tuning": len(fine_tuning),
                "evaluation": len(evals)
            }
        }

    def audit(self, intelligence, graph, dataset):
        score = 100
        warnings = []
        if intelligence["topic_count"] == 0:
            score -= 40; warnings.append("no topic")
        if graph["node_count"] == 0 or graph["edge_count"] == 0:
            score -= 25; warnings.append("empty graph")
        if dataset["counts"]["rag"] == 0:
            score -= 20; warnings.append("empty rag dataset")
        if not intelligence.get("main_issue"):
            score -= 15; warnings.append("main issue missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def certificate(self, audit, dataset, graph):
        return {
            "certificate_id": "CGT-" + now_stamp(),
            "status": audit["status"],
            "dataset_counts": dataset["counts"],
            "graph_nodes": graph["node_count"],
            "graph_edges": graph["edge_count"],
            "issued_at": now_text(),
            "note": "1970-1990 katmanı; Master Record'u case intelligence, graph ve AI dataset çıktılarına dönüştürmüştür."
        }

    def run(self):
        CGT_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        master = self.load_master_record()
        intelligence = self.case_intelligence(master)
        graph = self.graph_builder(master, intelligence)
        dataset = self.dataset_factory(master, intelligence, graph)
        audit = self.audit(intelligence, graph, dataset)
        cert = self.certificate(audit, dataset, graph)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.20 + audit["score"] * 0.45 + min(100, graph["node_count"] * 5) * 0.15 + min(100, dataset["counts"]["rag"] * 10) * 0.20, 2)
        decision = "CASE GRAPH TRAINER READY" if audit["status"] != "FAIL" and support_score >= 60 else "CASE GRAPH TRAINER BLOCKED"
        ts = now_stamp()
        snapshot = CGT_DIR / "1970_1990_case_graph_trainer_snapshot.json"
        intelligence_file = CGT_DIR / ("1970_case_intelligence_" + ts + ".json")
        graph_file = CGT_DIR / ("1980_legal_graph_" + ts + ".json")
        dataset_file = CGT_DIR / ("1990_ai_datasets_" + ts + ".json")
        dashboard = CGT_DIR / "1970_1990_case_graph_trainer_dashboard.json"
        state = CGT_DIR / ("1970_1990_case_graph_trainer_state_" + ts + ".json")
        report = REPORTS / ("1970_1990_case_graph_trainer_sdk_raporu_" + ts + ".txt")
        payload = {
            "master_record": master,
            "case_intelligence": intelligence,
            "legal_graph": graph,
            "ai_datasets": dataset,
            "audit": audit,
            "certificate": cert,
            "modules": modules,
            "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": audit["warnings"]}
        }
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(intelligence_file, intelligence)
        write_json(graph_file, graph)
        write_json(dataset_file, dataset)
        write_json(dashboard, {
            "status": decision,
            "score": final_score,
            "main_issue": intelligence["main_issue"]["topic"] if intelligence.get("main_issue") else None,
            "topics": intelligence["topic_count"],
            "graph_nodes": graph["node_count"],
            "graph_edges": graph["edge_count"],
            "rag_chunks": dataset["counts"]["rag"],
            "audit": audit["status"]
        })
        lines = [
            "=" * 80,
            "1970-1990 CASE GRAPH TRAINER SDK",
            "=" * 80,
            "Validation       : " + decision,
            "Score            : " + str(final_score) + " / 100",
            "Main Issue       : " + str(intelligence["main_issue"]["topic"] if intelligence.get("main_issue") else None),
            "Topics           : " + str(intelligence["topic_count"]),
            "Graph Nodes      : " + str(graph["node_count"]),
            "Graph Edges      : " + str(graph["edge_count"]),
            "RAG Chunks       : " + str(dataset["counts"]["rag"]),
            "Instruction Rows : " + str(dataset["counts"]["instruction"]),
            "FineTune Rows    : " + str(dataset["counts"]["fine_tuning"]),
            "Audit            : " + audit["status"],
            "",
            "Dosyalar:",
            str(snapshot),
            str(intelligence_file),
            str(graph_file),
            str(dataset_file),
            str(dashboard),
            str(report)
        ]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "intelligence": str(intelligence_file), "graph": str(graph_file), "dataset": str(dataset_file), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
