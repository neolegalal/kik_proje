# -*- coding: utf-8 -*-
from .config import BASE_DIR, STATE_DIR, REPORT_DIR, INTELLIGENCE_SDK_DIR
from .utils import ensure_dirs, now_text, disk_free_gb
from .loader import IntelligenceDataLoader
from .normalizer import IntelligenceNormalizer
from .scoring import IntelligenceScoring
from .risk import IntelligenceRisk
from .recommendation import IntelligenceRecommendation
from .summary import IntelligenceSummary
from .exporter import IntelligenceExporter

class IntelligenceEngine:
    def __init__(self, engine_name="Generic Intelligence Engine"):
        ensure_dirs(STATE_DIR, REPORT_DIR, INTELLIGENCE_SDK_DIR)
        self.engine_name = engine_name
        self.loader = IntelligenceDataLoader()
        self.normalizer = IntelligenceNormalizer()
        self.scoring = IntelligenceScoring()
        self.risk = IntelligenceRisk()
        self.recommendation = IntelligenceRecommendation()
        self.summary = IntelligenceSummary()
        self.exporter = IntelligenceExporter()

    def run(self):
        raw = self.loader.load_all()
        normalized = self.normalizer.normalize(raw)
        score = self.scoring.global_score(normalized)
        risk_level = self.risk.level(score)
        reasons = self.risk.reasons(normalized)
        recommendation = self.recommendation.recommend(normalized, score, risk_level)
        executive_summary = self.summary.build(normalized, score, risk_level, recommendation)

        decision = "INTELLIGENCE SDK READY" if score >= 90 else ("INTELLIGENCE SDK REVIEW" if score >= 70 else "INTELLIGENCE SDK RISK")

        payload = {
            "module": "205.0 Intelligence SDK",
            "engine_name": self.engine_name,
            "created_at": now_text(),
            "disk_free_gb": disk_free_gb(BASE_DIR),
            "normalized": normalized,
            "result": {
                "score": score,
                "risk_level": risk_level,
                "risk_reasons": reasons,
                "decision": decision,
                "recommendation": recommendation,
                "executive_summary": executive_summary,
            }
        }

        paths = self.exporter.export(payload, name_prefix="205_0_intelligence_sdk")
        return {"payload": payload, "paths": paths}
