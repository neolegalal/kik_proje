# -*- coding: utf-8 -*-
class AutomationPlanner:
    def plan(self, context, validation):
        if validation["errors"]:
            return {
                "automation_mode": "PAUSED",
                "triggers": [],
                "message": "Automation blocked by validation errors.",
            }

        triggers = []
        if context.get("assignment_count", 0) > 0:
            triggers.append({
                "trigger_type": "EXECUTION_PLAN_TRIGGER",
                "mode": context.get("execution_mode"),
                "assignment_count": context.get("assignment_count"),
                "status": "PLANNED",
            })

        triggers.append({"trigger_type": "METRICS_REFRESH", "status": "PLANNED"})
        triggers.append({"trigger_type": "INTELLIGENCE_REFRESH", "status": "PLANNED"})
        triggers.append({"trigger_type": "SCHEDULER_FEEDBACK", "status": "PLANNED"})

        return {
            "automation_mode": "CONTROLLED",
            "triggers": triggers,
            "message": f"{len(triggers)} automation trigger planned.",
        }
