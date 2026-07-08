# -*- coding: utf-8 -*-
class AutonomousPlanner:
    def plan(self, context, validation):
        if validation["errors"]:
            return {
                "operation_mode": "PAUSED",
                "operations": [],
                "message": "Autonomous operations blocked by validation errors.",
            }

        operations = []

        if context.get("can_operate_autonomously"):
            operations.append({"operation": "AUTO_APPROVE_CONTROLLED_AUTOMATION", "status": "PLANNED"})
        else:
            operations.append({"operation": "REQUIRE_CONTROLLED_REVIEW", "status": "PLANNED"})

        operations.append({"operation": "GOVERNANCE_LOG", "status": "PLANNED"})
        operations.append({"operation": "OPERATIONS_FEEDBACK", "status": "PLANNED"})

        return {
            "operation_mode": "CONTROLLED_AUTONOMY",
            "operations": operations,
            "message": f"{len(operations)} autonomous operation planned.",
        }
