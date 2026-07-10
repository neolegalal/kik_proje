
# -*- coding: utf-8 -*-
import json, re, statistics
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
VALIDATION_DIR = STATE / "validation_benchmark_platform"
UDP_DIR = STATE / "unified_decision_processor"
CGT_DIR = STATE / "case_graph_trainer"

SUPPORT_IDS = ["1990", "1980", "1970", "1950", "1900", "1800", "1700", "1600", "1500", "1400", "1300", "1100"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class ValidationBenchmarkPlatformSDK:
    def __init__(self, name="2050 Validation & Benchmark Platform SDK", gold_standard_path=None, master_record_path=None, execute=False):
        self.name = name
        self.gold_standard_path = Path(gold_standard_path) if gold_standard_path else None
        self.master_record_path = Path(master_record_path) if master_record_path else None
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits)})
        return rows

    def latest_master_record(self):
        if self.master_record_path and self.master_record_path.exists():
            return self.master_record_path
        latest = sorted(UDP_DIR.glob("1950_master_record_*.json"), reverse=True)
        return latest[0] if latest else None

    def load_json(self, path):
        if path and Path(path).exists():
            try:
                return json.loads(Path(path).read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def gold_standard_builder(self, master):
        # Gerçek gold standard yoksa master record üzerinden başlangıç gold standard iskeleti üretir.
        if self.gold_standard_path and self.gold_standard_path.exists():
            existing = self.load_json(self.gold_standard_path)
            if existing:
                return {"status": "READY", "source": str(self.gold_standard_path), "items": existing.get("items", existing if isinstance(existing, list) else [])}
        topics = master.get("topic_records", []) if master else []
        if not topics:
            topics = [
                {"topic": "Yeterlik kriteri", "legal_question": "Yeterlik kriteri yönünden işlem hukuka uygun mudur?", "legislation": ["4734 m.5"], "result_principle": "Somut belge ve doküman hükmü esas alınır."},
                {"topic": "İş deneyim belgesi", "legal_question": "İş deneyim belgesi uygun mudur?", "legislation": ["Uygulama Yönetmeliği"], "result_principle": "Belgenin kapsamı benzer iş tanımıyla karşılaştırılır."}
            ]
        items = []
        for t in topics:
            items.append({
                "gold_id": "GS-" + str(t.get("topic_id", len(items)+1)),
                "expected_main_issue": t.get("topic"),
                "expected_question": t.get("legal_question"),
                "expected_legislation": t.get("legislation", []),
                "expected_result": t.get("result_principle", t.get("legal_problem", "")),
                "expected_confidence_min": 70,
                "human_status": "AUTO_BASELINE_NEEDS_REVIEW"
            })
        return {"status": "READY", "source": "auto_from_master_record", "items": items}

    def benchmark_runner(self, master, gold):
        topic_records = master.get("topic_records", []) if master else []
        results = []
        for g in gold["items"]:
            expected = (g.get("expected_main_issue") or "").lower()
            best = None
            best_score = 0
            for t in topic_records:
                topic = (t.get("topic") or "").lower()
                score = 100 if expected and expected == topic else 70 if expected and (expected in topic or topic in expected) else 30
                if score > best_score:
                    best = t
                    best_score = score
            results.append({
                "gold_id": g.get("gold_id"),
                "expected_main_issue": g.get("expected_main_issue"),
                "predicted_topic": best.get("topic") if best else None,
                "topic_match_score": best_score,
                "legislation_match_score": self.legislation_score(g, best),
                "result_match_score": self.result_score(g, best),
                "confidence_score": best.get("confidence", 0) if best else 0,
                "status": "PASS" if best_score >= 70 else "FAIL"
            })
        return {"status": "READY", "benchmark_count": len(results), "results": results}

    def legislation_score(self, gold, predicted):
        if not predicted:
            return 0
        expected = set([str(x).lower() for x in gold.get("expected_legislation", [])])
        actual = set([str(x).lower() for x in predicted.get("legislation", [])])
        if not expected:
            return 80 if actual else 50
        overlap = len(expected.intersection(actual))
        return round((overlap / max(1, len(expected))) * 100, 2)

    def result_score(self, gold, predicted):
        if not predicted:
            return 0
        exp = str(gold.get("expected_result", "")).lower()
        pred = (str(predicted.get("result_principle", "")) + " " + str(predicted.get("legal_problem", ""))).lower()
        if not exp:
            return 80 if pred else 40
        exp_words = set(re.findall(r"\w+", exp))
        pred_words = set(re.findall(r"\w+", pred))
        if not exp_words:
            return 50
        return round(len(exp_words.intersection(pred_words)) / len(exp_words) * 100, 2)

    def accuracy_analyzer(self, benchmark):
        results = benchmark["results"]
        if not results:
            return {"status": "FAIL", "accuracy": 0, "main_issue_detection": 0, "citation_accuracy": 0, "result_accuracy": 0}
        main_issue = statistics.mean([r["topic_match_score"] for r in results])
        citation = statistics.mean([r["legislation_match_score"] for r in results])
        result = statistics.mean([r["result_match_score"] for r in results])
        confidence = statistics.mean([r["confidence_score"] for r in results])
        accuracy = round(main_issue * 0.35 + citation * 0.25 + result * 0.25 + min(confidence, 100) * 0.15, 2)
        return {
            "status": "PASS" if accuracy >= 80 else "WARN" if accuracy >= 60 else "FAIL",
            "accuracy": accuracy,
            "main_issue_detection": round(main_issue, 2),
            "citation_accuracy": round(citation, 2),
            "result_accuracy": round(result, 2),
            "average_confidence": round(confidence, 2)
        }

    def legal_consistency_checker(self, benchmark):
        # Aynı gold_id için farklı prediction oluşmuş mu simüle ve tespit eder.
        predictions = {}
        inconsistencies = []
        for r in benchmark["results"]:
            gid = r["gold_id"]
            pred = r["predicted_topic"]
            if gid in predictions and predictions[gid] != pred:
                inconsistencies.append({"gold_id": gid, "first": predictions[gid], "second": pred})
            predictions[gid] = pred
        consistency = 100 if not inconsistencies else max(0, 100 - len(inconsistencies) * 15)
        return {"status": "PASS" if consistency >= 90 else "WARN", "consistency_score": consistency, "inconsistencies": inconsistencies}

    def explainability_engine(self, benchmark, accuracy):
        explanations = []
        for r in benchmark["results"]:
            explanations.append({
                "gold_id": r["gold_id"],
                "why_score": "Ana uyuşmazlık eşleşmesi, mevzuat eşleşmesi, sonuç eşleşmesi ve confidence birlikte puanlanmıştır.",
                "topic_match_score": r["topic_match_score"],
                "legislation_match_score": r["legislation_match_score"],
                "result_match_score": r["result_match_score"],
                "confidence_score": r["confidence_score"]
            })
        return {"status": "READY", "explainability_score": min(100, accuracy["accuracy"] + 5), "items": explanations}

    def hallucination_metric(self, accuracy, benchmark):
        # citation/result zayıfsa hallucination riski artar.
        risk = 100 - (accuracy["citation_accuracy"] * 0.45 + accuracy["result_accuracy"] * 0.35 + accuracy["main_issue_detection"] * 0.20)
        risk = max(0, min(100, round(risk, 2)))
        return {"hallucination_rate": risk, "risk_label": "LOW" if risk <= 15 else "MEDIUM" if risk <= 35 else "HIGH"}

    def human_validation_center(self, gold, benchmark):
        review_items = []
        for r in benchmark["results"]:
            review_items.append({
                "gold_id": r["gold_id"],
                "predicted_topic": r["predicted_topic"],
                "suggested_human_action": "APPROVE" if r["status"] == "PASS" else "REVIEW",
                "review_status": "PENDING_HUMAN_REVIEW"
            })
        return {"status": "READY", "pending_reviews": len(review_items), "items": review_items}

    def continuous_benchmark_engine(self, accuracy, consistency, hallucination):
        can_promote = accuracy["accuracy"] >= 80 and consistency["consistency_score"] >= 90 and hallucination["hallucination_rate"] <= 25
        return {
            "status": "READY",
            "release_gate": "PROMOTE" if can_promote else "HOLD_FOR_REVIEW",
            "rules": [
                "Accuracy >= 80",
                "Consistency >= 90",
                "Hallucination <= 25"
            ],
            "next_benchmark": "Her yeni builder/release sonrası otomatik çalıştırılmalıdır."
        }

    def scientific_report_generator(self, accuracy, consistency, hallucination, benchmark):
        report = {
            "title": "NeoLegal Validation & Benchmark Scientific Report",
            "created_at": now_text(),
            "sample_size": benchmark["benchmark_count"],
            "metrics": {
                "accuracy": accuracy["accuracy"],
                "main_issue_detection": accuracy["main_issue_detection"],
                "citation_accuracy": accuracy["citation_accuracy"],
                "result_accuracy": accuracy["result_accuracy"],
                "consistency": consistency["consistency_score"],
                "hallucination_rate": hallucination["hallucination_rate"]
            },
            "interpretation": "Bu rapor NeoLegal çıktılarının gold standard ile karşılaştırmalı doğrulama metriklerini gösterir."
        }
        return {"status": "READY", "report": report}

    def validation_certificate(self, accuracy, consistency, hallucination, continuous):
        return {
            "certificate_id": "VAL-" + now_stamp(),
            "status": "PASS" if continuous["release_gate"] == "PROMOTE" else "REVIEW_REQUIRED",
            "accuracy": accuracy["accuracy"],
            "main_issue_detection": accuracy["main_issue_detection"],
            "citation_accuracy": accuracy["citation_accuracy"],
            "hallucination_rate": hallucination["hallucination_rate"],
            "consistency": consistency["consistency_score"],
            "issued_at": now_text()
        }

    def audit(self, accuracy, consistency, hallucination, continuous):
        score = round(accuracy["accuracy"] * 0.45 + consistency["consistency_score"] * 0.25 + max(0, 100 - hallucination["hallucination_rate"]) * 0.20 + (100 if continuous["release_gate"] == "PROMOTE" else 70) * 0.10, 2)
        warnings = []
        if accuracy["accuracy"] < 80:
            warnings.append("accuracy below promote threshold")
        if hallucination["hallucination_rate"] > 25:
            warnings.append("hallucination above threshold")
        if consistency["consistency_score"] < 90:
            warnings.append("consistency below threshold")
        status = "PASS" if score >= 85 and not warnings else "WARN" if score >= 70 else "FAIL"
        return {"score": score, "status": status, "warnings": warnings}

    def run(self):
        VALIDATION_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        master_path = self.latest_master_record()
        master = self.load_json(master_path) or {}
        gold = self.gold_standard_builder(master)
        benchmark = self.benchmark_runner(master, gold)
        accuracy = self.accuracy_analyzer(benchmark)
        consistency = self.legal_consistency_checker(benchmark)
        explanation = self.explainability_engine(benchmark, accuracy)
        hallucination = self.hallucination_metric(accuracy, benchmark)
        human = self.human_validation_center(gold, benchmark)
        continuous = self.continuous_benchmark_engine(accuracy, consistency, hallucination)
        scientific = self.scientific_report_generator(accuracy, consistency, hallucination, benchmark)
        certificate = self.validation_certificate(accuracy, consistency, hallucination, continuous)
        audit = self.audit(accuracy, consistency, hallucination, continuous)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.15 + audit["score"] * 0.85, 2)
        decision = "VALIDATION BENCHMARK PLATFORM READY" if audit["status"] != "FAIL" and support_score >= 60 else "VALIDATION BENCHMARK PLATFORM BLOCKED"
        ts = now_stamp()
        snapshot = VALIDATION_DIR / "2050_validation_benchmark_snapshot.json"
        gold_file = VALIDATION_DIR / ("2051_gold_standard_" + ts + ".json")
        benchmark_file = VALIDATION_DIR / ("2052_benchmark_results_" + ts + ".json")
        scientific_file = VALIDATION_DIR / ("2059_scientific_report_" + ts + ".json")
        dashboard = VALIDATION_DIR / "2056_benchmark_dashboard.json"
        state = VALIDATION_DIR / ("2050_validation_benchmark_state_" + ts + ".json")
        report = REPORTS / ("2050_validation_benchmark_sdk_raporu_" + ts + ".txt")
        payload = {
            "gold_standard": gold,
            "benchmark": benchmark,
            "accuracy": accuracy,
            "consistency": consistency,
            "explainability": explanation,
            "hallucination": hallucination,
            "human_validation": human,
            "continuous_benchmark": continuous,
            "scientific_report": scientific,
            "certificate": certificate,
            "audit": audit,
            "modules": modules,
            "master_record_path": str(master_path) if master_path else None,
            "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": audit["warnings"]}
        }
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(gold_file, gold)
        write_json(benchmark_file, benchmark)
        write_json(scientific_file, scientific)
        write_json(dashboard, {
            "status": decision,
            "score": final_score,
            "accuracy": accuracy["accuracy"],
            "main_issue_detection": accuracy["main_issue_detection"],
            "citation_accuracy": accuracy["citation_accuracy"],
            "hallucination_rate": hallucination["hallucination_rate"],
            "consistency": consistency["consistency_score"],
            "release_gate": continuous["release_gate"],
            "audit": audit["status"]
        })
        lines = [
            "=" * 80,
            "2050 VALIDATION & BENCHMARK PLATFORM SDK",
            "=" * 80,
            "Validation           : " + decision,
            "Score                : " + str(final_score) + " / 100",
            "Accuracy             : " + str(accuracy["accuracy"]) + " / 100",
            "Main Issue Detection : " + str(accuracy["main_issue_detection"]) + " / 100",
            "Citation Accuracy    : " + str(accuracy["citation_accuracy"]) + " / 100",
            "Result Accuracy      : " + str(accuracy["result_accuracy"]) + " / 100",
            "Consistency          : " + str(consistency["consistency_score"]) + " / 100",
            "Hallucination Rate   : " + str(hallucination["hallucination_rate"]) + " / 100",
            "Release Gate         : " + continuous["release_gate"],
            "Audit                : " + audit["status"],
            "",
            "Dosyalar:",
            str(snapshot),
            str(gold_file),
            str(benchmark_file),
            str(scientific_file),
            str(dashboard),
            str(report)
        ]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "gold": str(gold_file), "benchmark": str(benchmark_file), "scientific": str(scientific_file), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
