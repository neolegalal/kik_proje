# 206 Scheduler Subsystem v2.3
## Technical Design Specification

**Platform:** NeoLegal Production Platform  
**Document Version:** 2.3  
**Status:** ACTIVE  
**Date:** 08.07.2026  
**Layer:** Scheduler / Orchestration  
**Depends On:** 199, 200, 201, 202, 203, 204, 205, 191–198  

---

# 1. Purpose

The 206 Scheduler Subsystem is the adaptive orchestration layer of the NeoLegal Production Platform.

Its purpose is to plan, prioritize, execute, monitor, retry and optimize production jobs by using:

- Production state
- Queue state
- Worker capacity
- Metrics outputs
- Intelligence Layer outputs
- Recovery state
- Event and log signals

The subsystem is not a simple cron runner. It is designed as an enterprise-grade orchestration engine that can make safe scheduling decisions based on current platform intelligence.

---

# 2. Architectural Position

```text
                         NeoLegal OS

 ┌────────────────────────────────────────────────────────────┐
 │                    Applications / Dashboard                │
 └──────────────────────────────┬─────────────────────────────┘
                                │
 ┌──────────────────────────────▼─────────────────────────────┐
 │                         AI Layer                           │
 └──────────────────────────────┬─────────────────────────────┘
                                │
 ┌──────────────────────────────▼─────────────────────────────┐
 │                    Intelligence Layer 205                  │
 │ Production • Queue • Worker • DB • Event • Logger • AI Sum │
 └──────────────────────────────┬─────────────────────────────┘
                                │
 ┌──────────────────────────────▼─────────────────────────────┐
 │                 Scheduler Subsystem 206                    │
 │ SDK • Engine • Planner • Queue • Retry • Batch • Decision  │
 └──────────────────────────────┬─────────────────────────────┘
                                │
 ┌──────────────────────────────▼─────────────────────────────┐
 │                  Production Platform 168–198               │
 │ Production • QA • Recovery • Queue • Worker • Import       │
 └──────────────────────────────┬─────────────────────────────┘
                                │
 ┌──────────────────────────────▼─────────────────────────────┐
 │                       Database / Export                    │
 └────────────────────────────────────────────────────────────┘
```

---

# 3. Core Design Principles

## 3.1 Deterministic Execution

Every scheduler decision must be reproducible from the same inputs.

## 3.2 Safety First

No job should execute when the platform is in an unsafe state.

## 3.3 Intelligence Driven

Scheduler decisions must consume the Intelligence Layer whenever possible.

## 3.4 Recoverability

Every scheduling cycle must be recoverable after interruption.

## 3.5 Auditability

Every decision must be logged and explainable.

## 3.6 Extensibility

New scheduler strategies must be pluggable.

## 3.7 Separation of Concerns

Planning, priority, dependency, retry, batch sizing and decision-making must remain separate components.

---

# 4. Component Map

```text
206 Scheduler Subsystem
│
├── 206.0 Scheduler SDK
│   ├── context.py
│   ├── contracts.py
│   ├── loader.py
│   ├── validator.py
│   ├── exporter.py
│   └── utils.py
│
├── 206.1 Scheduler Engine
│   ├── lifecycle controller
│   ├── execution coordinator
│   └── scheduler state writer
│
├── 206.2 Job Planner
│   ├── plan builder
│   ├── execution order
│   └── workload distribution
│
├── 206.3 Priority Queue
│   ├── priority scoring
│   ├── dynamic reprioritization
│   └── waiting/running/retry queue views
│
├── 206.4 Dependency Resolver
│   ├── dependency graph
│   ├── cycle detection
│   └── execution blocks
│
├── 206.5 Retry Scheduler
│   ├── retry policy
│   ├── retry limits
│   ├── delay strategy
│   └── escalation
│
├── 206.6 Cron Manager
│   ├── periodic jobs
│   ├── health jobs
│   └── documentation jobs
│
├── 206.7 Batch Planner
│   ├── batch sizing
│   ├── worker fit
│   └── production capacity
│
├── 206.8 Scheduler Dashboard
│   ├── dashboard JSON
│   ├── timeline
│   └── operational summary
│
└── 206.9 Scheduler Decision Engine
    ├── intelligence reader
    ├── decision rules
    ├── safety gate
    └── recommendation output
```

---

# 5. Module Responsibilities

## 206.0 Scheduler SDK

Provides shared infrastructure for all 206.x modules.

Responsibilities:

- Load scheduler configuration
- Load queue state
- Load worker state
- Load 205 Intelligence outputs
- Validate scheduler context
- Export scheduler state
- Export reports
- Provide common JSON schema helpers

---

## 206.1 Scheduler Engine

Main lifecycle controller.

Responsibilities:

- Start scheduling cycle
- Load scheduler context
- Request job plan
- Request dependency resolution
- Request priority sorting
- Request batch decision
- Execute worker assignment
- Publish event
- Write scheduler state
- Trigger metrics refresh

---

## 206.2 Job Planner

Builds an execution plan.

Responsibilities:

- Select waiting jobs
- Group compatible jobs
- Define execution order
- Estimate execution load
- Produce execution plan JSON

---

## 206.3 Priority Queue

Assigns and updates priorities.

Priority levels:

```text
CRITICAL
HIGH
NORMAL
LOW
```

Priority is affected by:

- failed retry count
- job age
- production importance
- dependency position
- recovery status
- Intelligence Layer risk

---

## 206.4 Dependency Resolver

Prevents invalid execution order.

Responsibilities:

- Build dependency graph
- Detect circular dependencies
- Resolve blocking jobs
- Create execution blocks
- Mark unsafe dependency chains

---

## 206.5 Retry Scheduler

Handles failed and retry jobs.

Retry strategies:

```text
IMMEDIATE_RETRY
DELAYED_RETRY
EXPONENTIAL_BACKOFF
MANUAL_REVIEW
ESCALATE_TO_RECOVERY
```

---

## 206.6 Cron Manager

Manages periodic platform tasks.

Examples:

- 204 metrics snapshot
- 205 intelligence run all
- documentation audit
- recovery audit
- backup verification
- queue health audit
- worker health audit

---

## 206.7 Batch Planner

Calculates safe batch size.

Inputs:

- worker count
- idle worker count
- queue risk
- platform stability
- DB growth status
- forecast confidence
- logger/event risk

Outputs:

- recommended batch size
- maximum safe batch size
- minimum safe batch size
- execution mode

---

## 206.8 Scheduler Dashboard

Generates dashboard-ready operational state.

Outputs:

- current scheduler status
- current plan
- active batch
- retry jobs
- dependency warnings
- decision summary
- timeline
- worker allocation

---

## 206.9 Scheduler Decision Engine

The adaptive decision layer.

Consumes all relevant 205 outputs:

- 205.1 Production Analytics
- 205.2 Queue Intelligence
- 205.3 Worker Intelligence
- 205.4 DB Growth Analytics
- 205.5 Event Intelligence
- 205.6 Logger Intelligence
- 205.7 Platform Stability Index
- 205.8 Health Trend Engine
- 205.9 Forecast Engine
- 205.10 Executive AI Summary

Decision outputs:

```text
ALLOW_PRODUCTION
ALLOW_SMALL_BATCH
PAUSE_PRODUCTION
RETRY_FAILED_JOBS
REQUEST_RECOVERY
WAIT_FOR_WORKERS
REFRESH_METRICS
RUN_INTELLIGENCE
```

---

# 6. Scheduler Data Flow

```text
Production Request
        │
        ▼
206.1 Scheduler Engine
        │
        ▼
206.2 Job Planner
        │
        ▼
206.4 Dependency Resolver
        │
        ▼
206.3 Priority Queue
        │
        ▼
206.9 Decision Engine
        │
        ▼
206.7 Batch Planner
        │
        ▼
Worker Assignment
        │
        ▼
Production Controller 181
        │
        ▼
Event Bus 201
        │
        ▼
Logger 203
        │
        ▼
Metrics 204
        │
        ▼
Intelligence 205
        │
        ▼
Scheduler Feedback
```

---

# 7. Sequence Diagram – Normal Execution

```text
User / Automation
      │
      ▼
Scheduler Engine
      │
      ├── load context
      │
      ├── read queue
      │
      ├── read workers
      │
      ├── read intelligence
      │
      ▼
Job Planner
      │
      ▼
Dependency Resolver
      │
      ▼
Priority Queue
      │
      ▼
Decision Engine
      │
      ├── checks stability
      │
      ├── checks queue risk
      │
      ├── checks worker capacity
      │
      └── recommends execution mode
      │
      ▼
Batch Planner
      │
      ▼
Worker Manager
      │
      ▼
181 Production Controller
      │
      ▼
Metrics + Intelligence refresh
```

---

# 8. Sequence Diagram – Unsafe Execution

```text
Scheduler Engine
      │
      ▼
Decision Engine
      │
      ├── Platform Stability < 90
      ├── Queue Risk = HIGH
      └── Logger Risk = MEDIUM/HIGH
      │
      ▼
Decision: PAUSE_PRODUCTION
      │
      ▼
Recovery Manager
      │
      ▼
Recovery Audit
      │
      ▼
Metrics Snapshot
      │
      ▼
Intelligence Run All
      │
      ▼
Decision Re-evaluation
```

---

# 9. Scheduler State Machine

```text
IDLE
 │
 ▼
LOAD_CONTEXT
 │
 ▼
PLAN_JOBS
 │
 ▼
RESOLVE_DEPENDENCIES
 │
 ▼
PRIORITIZE
 │
 ▼
DECIDE
 │
 ├── PAUSE
 │       ▼
 │   RECOVERY_CHECK
 │       ▼
 │   WAIT
 │
 └── ALLOW
         ▼
     PLAN_BATCH
         ▼
     ASSIGN_WORKERS
         ▼
     EXECUTE
         ▼
     MONITOR
         ▼
     METRICS_REFRESH
         ▼
     INTELLIGENCE_REFRESH
         ▼
     COMPLETE
```

---

# 10. JSON Schemas

## 10.1 Scheduler Context

```json
{
  "scheduler_id": "SCH-20260708-0001",
  "created_at": "2026-07-08T01:00:00",
  "mode": "AUTO",
  "queue": {
    "waiting": 17,
    "running": 0,
    "failed": 0,
    "retry": 0
  },
  "workers": {
    "total": 3,
    "idle": 3,
    "running": 0
  },
  "intelligence": {
    "platform_stability": 98,
    "queue_risk": "LOW",
    "worker_risk": "LOW",
    "forecast_confidence": "LOW"
  }
}
```

## 10.2 Scheduler Decision

```json
{
  "decision": "ALLOW_SMALL_BATCH",
  "risk": "LOW",
  "recommended_batch_size": 25,
  "reason": "Platform stable but forecast confidence is low.",
  "requires_recovery": false,
  "requires_metrics_refresh_after_run": true
}
```

## 10.3 Execution Plan

```json
{
  "plan_id": "PLAN-20260708-0001",
  "jobs": [
    {
      "job_id": "JOB-000004",
      "priority": "NORMAL",
      "dependencies": [],
      "assigned_worker": "worker-1"
    }
  ],
  "batch_size": 25,
  "execution_mode": "CONTROLLED"
}
```

---

# 11. Decision Table

| Condition | Decision |
|----------|----------|
| Stability >= 95 and Queue Risk LOW | ALLOW_PRODUCTION |
| Stability 90–95 and Forecast LOW | ALLOW_SMALL_BATCH |
| Stability < 90 | PAUSE_PRODUCTION |
| Queue Risk HIGH | RETRY_FAILED_JOBS |
| Worker Idle = 0 | WAIT_FOR_WORKERS |
| Logger Risk HIGH | REQUEST_RECOVERY |
| Event Risk HIGH | REQUEST_RECOVERY |
| Metrics stale | REFRESH_METRICS |
| Intelligence stale | RUN_INTELLIGENCE |

---

# 12. Batch Size Rules

```text
IF Stability >= 95 AND Queue Risk LOW AND Worker Capacity HIGH
    Batch Size = NORMAL_BATCH

IF Stability >= 90 AND Forecast Confidence LOW
    Batch Size = SMALL_BATCH

IF Queue Risk MEDIUM
    Batch Size = SMALL_BATCH

IF Logger/Event Risk HIGH
    Batch Size = 0

IF Recovery Required
    Batch Size = 0
```

---

# 13. Event Flow

Scheduler publishes events to 201 Event Bus:

```json
{
  "event_type": "SCHEDULER_DECISION",
  "source": "206.9 Scheduler Decision Engine",
  "severity": "INFO",
  "payload": {
    "decision": "ALLOW_SMALL_BATCH",
    "recommended_batch_size": 25
  }
}
```

Important event types:

```text
SCHEDULER_STARTED
SCHEDULER_CONTEXT_LOADED
SCHEDULER_PLAN_CREATED
SCHEDULER_DECISION
SCHEDULER_BATCH_PLANNED
SCHEDULER_WORKER_ASSIGNED
SCHEDULER_PAUSED
SCHEDULER_RECOVERY_REQUESTED
SCHEDULER_COMPLETED
```

---

# 14. Logging Rules

Every scheduler module writes structured logs to 203 Central Logger.

Log levels:

```text
INFO
WARNING
ERROR
CRITICAL
```

Examples:

```json
{
  "source": "206.1 Scheduler Engine",
  "level": "INFO",
  "message": "Scheduler cycle started.",
  "scheduler_id": "SCH-20260708-0001"
}
```

---

# 15. Metrics Outputs

206 writes scheduler metrics into:

```text
production_state/metrics/scheduler/
```

Recommended files:

```text
206_scheduler_snapshot.json
206_scheduler_history.jsonl
206_scheduler_dashboard.json
206_scheduler_decisions.jsonl
```

---

# 16. Dashboard Contract

Dashboard-ready output:

```json
{
  "scheduler_status": "READY",
  "last_decision": "ALLOW_SMALL_BATCH",
  "recommended_batch_size": 25,
  "active_workers": 0,
  "idle_workers": 3,
  "waiting_jobs": 17,
  "risk": "LOW",
  "stability": 98,
  "forecast_confidence": "LOW"
}
```

---

# 17. Failure Scenarios

## 17.1 Queue Failure

Action:

```text
Pause → Retry Scheduler → Recovery Check → Replan
```

## 17.2 Worker Failure

Action:

```text
Mark worker unavailable → Reassign job → Refresh metrics
```

## 17.3 Metrics Failure

Action:

```text
Do not execute large batch → Run 204 snapshot → Re-evaluate
```

## 17.4 Intelligence Failure

Action:

```text
Fallback to conservative scheduling
```

## 17.5 Recovery Failure

Action:

```text
Stop scheduler and require manual review
```

---

# 18. Safety Gates

Scheduler may not execute production if:

- DB is unavailable
- Queue file is corrupt
- Worker file is corrupt
- Recovery state is HIGH
- Platform Stability < 90
- Logger Critical > 0
- Event Critical > 0
- Intelligence output is missing and mode is strict

---

# 19. Configuration

Recommended config:

```json
{
  "scheduler": {
    "mode": "AUTO",
    "default_batch_size": 25,
    "small_batch_size": 10,
    "max_batch_size": 100,
    "strict_intelligence_required": true,
    "auto_recovery_enabled": true,
    "metrics_refresh_after_run": true
  }
}
```

---

# 20. Roadmap

## 206.0

Scheduler SDK

## 206.1

Scheduler Engine

## 206.2

Job Planner

## 206.3

Priority Queue

## 206.4

Dependency Resolver

## 206.5

Retry Scheduler

## 206.6

Cron Manager

## 206.7

Batch Planner

## 206.8

Scheduler Dashboard

## 206.9

Scheduler Decision Engine

---

# 21. Future Extensions

- AI Scheduler
- Self-learning Scheduler
- Distributed Scheduler
- Cloud Scheduler
- Multi-node worker pool
- Real-time web dashboard
- Telegram scheduler alerting
- Human approval workflow

---

# 22. Conclusion

206 Scheduler Subsystem v2.3 defines the adaptive orchestration architecture of the NeoLegal Production Platform.

It connects production, metrics, intelligence, recovery and future AI layers into a single scheduling lifecycle.

This document is the reference architecture for all 206.x modules.
