# -*- coding: utf-8 -*-
from config_intelligence import TARGET_DB_COUNT

INTELLIGENCE_INPUT_SCHEMA = {
    "required_sources": [
        "204_metrics_snapshot.json",
        "204_metrics_history.jsonl",
        "204_dashboard_metrics.json",
        "205_metrics_trends.json",
    ],
    "metrics_fields": {
        "system": ["disk_free_gb", "db_count", "db_status"],
        "queue": ["total", "waiting", "running", "finished", "failed", "completion_rate"],
        "workers": ["total", "idle", "running", "jobs_completed", "jobs_failed"],
        "events": ["total", "invalid", "by_type", "by_severity"],
        "logs": ["total", "invalid", "by_source", "by_level"],
        "trends": ["db_delta", "event_delta", "log_delta", "queue_finished_delta"],
    }
}

INTELLIGENCE_OUTPUT_SCHEMA = {
    "production_analytics": {
        "production_velocity": "float",
        "db_current_count": "int",
        "target_db_count": "int",
        "remaining_to_target": "int",
    },
    "queue_intelligence": {
        "completion_rate": "float",
        "backlog": "int",
        "failed_jobs": "int",
        "queue_risk": "LOW|MEDIUM|HIGH",
    },
    "worker_intelligence": {
        "worker_count": "int",
        "idle_workers": "int",
        "running_workers": "int",
        "worker_health": "LOW|MEDIUM|HIGH",
    },
    "event_intelligence": {
        "event_total": "int",
        "error_events": "int",
        "warning_events": "int",
        "event_health": "LOW|MEDIUM|HIGH",
    },
    "logger_intelligence": {
        "log_total": "int",
        "error_logs": "int",
        "warning_logs": "int",
        "logger_health": "LOW|MEDIUM|HIGH",
    },
    "forecast": {
        "target": TARGET_DB_COUNT,
        "remaining": "int",
        "estimated_days_to_target": "float|null",
        "forecast_confidence": "LOW|MEDIUM|HIGH",
    },
    "stability": {
        "platform_stability_index": "0-100",
        "risk_level": "LOW|MEDIUM|HIGH",
        "risk_reasons": "list",
    },
    "executive_summary": {
        "summary_text": "str",
        "recommended_next_action": "str",
    }
}

ENGINE_CONTRACTS = [
    {
        "engine_id": "205.1",
        "name": "Production Analytics",
        "inputs": ["db_count", "db_delta", "metrics_history"],
        "outputs": ["production_velocity", "remaining_to_target"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.2",
        "name": "Queue Intelligence",
        "inputs": ["queue_total", "queue_finished", "queue_failed", "completion_rate"],
        "outputs": ["backlog", "queue_risk"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.3",
        "name": "Worker Intelligence",
        "inputs": ["workers_total", "workers_idle", "workers_running", "jobs_completed", "jobs_failed"],
        "outputs": ["worker_health", "worker_performance_index"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.4",
        "name": "DB Growth Analytics",
        "inputs": ["db_count", "db_delta", "target_db_count"],
        "outputs": ["remaining_to_target", "estimated_days_to_target"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.5",
        "name": "Event Intelligence",
        "inputs": ["event_total", "event_invalid", "event_severity"],
        "outputs": ["event_health", "event_risk"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.6",
        "name": "Logger Intelligence",
        "inputs": ["log_total", "log_invalid", "log_level"],
        "outputs": ["logger_health", "logger_risk"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.7",
        "name": "Stability Index",
        "inputs": ["all_engine_outputs"],
        "outputs": ["platform_stability_index", "risk_level"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.8",
        "name": "Health Trend",
        "inputs": ["metrics_score_series", "decision_series"],
        "outputs": ["health_direction", "average_health_score"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.9",
        "name": "Forecast Engine",
        "inputs": ["production_velocity", "db_delta", "remaining_to_target"],
        "outputs": ["estimated_days_to_target", "forecast_confidence"],
        "status": "CONTRACT_DEFINED"
    },
    {
        "engine_id": "205.10",
        "name": "AI Executive Summary",
        "inputs": ["all_engine_outputs"],
        "outputs": ["summary_text", "recommended_next_action"],
        "status": "CONTRACT_DEFINED"
    },
]
