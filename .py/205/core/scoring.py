# -*- coding: utf-8 -*-
from .utils import clamp

class IntelligenceScoring:
    def score_queue(self, queue):
        score = 100
        if queue.get("failed", 0):
            score -= min(30, queue.get("failed", 0) * 10)
        if queue.get("running", 0) > 0:
            score -= 0
        if queue.get("completion_rate", 0) < 50 and queue.get("total", 0) > 0:
            score -= 10
        return int(clamp(score))

    def score_workers(self, workers):
        score = 100
        if workers.get("total", 0) == 0:
            return 0
        if workers.get("jobs_failed", 0):
            score -= min(30, workers.get("jobs_failed", 0) * 10)
        return int(clamp(score))

    def score_events(self, events):
        score = 100
        if events.get("invalid", 0):
            score -= min(30, events.get("invalid", 0) * 10)
        sev = events.get("by_severity") or {}
        score -= min(40, (sev.get("ERROR", 0) + sev.get("CRITICAL", 0)) * 10)
        score -= min(10, sev.get("WARNING", 0) * 2)
        return int(clamp(score))

    def score_logs(self, logs):
        score = 100
        if logs.get("invalid", 0):
            score -= min(30, logs.get("invalid", 0) * 10)
        levels = logs.get("by_level") or {}
        score -= min(40, (levels.get("ERROR", 0) + levels.get("CRITICAL", 0)) * 10)
        score -= min(10, levels.get("WARNING", 0) * 2)
        return int(clamp(score))

    def global_score(self, normalized):
        parts = [
            normalized.get("health", {}).get("score") or 0,
            self.score_queue(normalized.get("queue", {})),
            self.score_workers(normalized.get("workers", {})),
            self.score_events(normalized.get("events", {})),
            self.score_logs(normalized.get("logs", {})),
        ]
        return round(sum(parts) / len(parts), 2) if parts else 0
