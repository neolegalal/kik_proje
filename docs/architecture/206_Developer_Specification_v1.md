# 206 Developer Specification
## NeoLegal Production Platform

**Version:** 1.0  
**Date:** 08.07.2026

# Purpose

This document defines the developer contract for every module in the 206 Scheduler Subsystem.
It specifies responsibilities, public methods, inputs, outputs and implementation rules to keep all 206.x modules consistent.

# Global Coding Rules

- One responsibility per module.
- Composition over duplication.
- JSON as the interchange format.
- Structured logging only.
- Every public method should be documented.
- All outputs must be deterministic.
- All modules must support audit and reporting.

# Shared Interfaces

Every module should expose:

```python
run()
status()
export()
```

Additional methods are module-specific.

---
# 206.0 Scheduler SDK

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Scheduler SDK component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `load_config()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `load_context()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `validate_context()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export_state()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export_report()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `read_intelligence()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `read_metrics()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.1 Scheduler Engine

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Scheduler Engine component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `initialize()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `load_context()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `build_execution_plan()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `allocate_workers()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `execute()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `publish_events()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `refresh_metrics()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `shutdown()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.2 Job Planner

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Job Planner component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `discover_jobs()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `group_jobs()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `estimate_cost()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `order_jobs()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `split_batches()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export_plan()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.3 Priority Queue

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Priority Queue component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `load()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `calculate_priority()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `reorder()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `waiting()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `running()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `retry()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.4 Dependency Resolver

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Dependency Resolver component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `build_graph()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `detect_cycles()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `resolve()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `validate()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export_graph()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.5 Retry Scheduler

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Retry Scheduler component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `retry_now()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `retry_later()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `backoff()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `max_retry()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `escalate()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.6 Cron Manager

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Cron Manager component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `register()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `unregister()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `next_run()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `run_due()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `history()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.7 Batch Planner

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Batch Planner component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `calculate()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `worker_fit()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `queue_fit()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `intelligence_fit()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `recommend()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.8 Scheduler Dashboard

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Scheduler Dashboard component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `build()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `timeline()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `summary()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `alerts()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# 206.9 Scheduler Decision Engine

## Purpose
Defines the responsibilities, public interfaces and lifecycle of the Scheduler Decision Engine component.

## Primary Responsibilities
- Execute only its own responsibility.
- Expose a stable API to other 206 modules.
- Emit structured logs and metrics.
- Write scheduler state when applicable.

## Public Methods

### `read_intelligence()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `evaluate()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `recommend()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `approve()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `deny()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `recovery()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

### `export()`
**Purpose:** Core operation.

**Inputs**
- Scheduler context
- Module configuration
- Runtime state (when required)

**Outputs**
- Structured Python object / JSON-serializable result

**Errors**
- Raises domain-specific exceptions or returns structured error state.

## Inputs
- Scheduler context
- Queue state
- Worker state
- Intelligence outputs (205.x)
- Metrics snapshot (204)

## Outputs
- JSON state
- Report
- Event (if applicable)
- Logger entry

## Success Criteria
- Deterministic execution
- No side effects outside module responsibility
- Full auditability

---

# Cross-Module Contracts

| Producer | Consumer | Contract |
|---|---|---|
|206.2|206.3|Execution Plan|
|206.3|206.7|Prioritized Queue|
|206.4|206.1|Dependency Graph|
|206.7|206.9|Batch Recommendation|
|205.x|206.9|Intelligence Snapshot|

# Testing Requirements

- Unit tests for each public method.
- Integration tests across 206.1–206.9.
- Deterministic replay tests.
- Recovery scenario tests.
- Performance benchmarks for scheduling.

# Coding Standards

- Type hints recommended.
- JSON schema validation for exported state.
- No hidden global state.
- Centralized configuration.
- Exceptions must include actionable messages.

# Conclusion

This specification is the implementation contract for all 206.x modules. Any new scheduler functionality should conform to these interfaces unless the architecture document is revised.
