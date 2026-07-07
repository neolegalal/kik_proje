# -*- coding: utf-8 -*-
class ExecutionPlanner:
    def plan(self, context, validation):
        if validation["errors"]:
            return {
                "execution_mode": "PAUSED",
                "assignments": [],
                "message": "Execution blocked by validation errors.",
            }

        selected = context["queue"]["selected_jobs"]
        workers = context["workers"]["available_worker_ids"]

        assignments = []
        if workers and selected > 0:
            for i in range(selected):
                assignments.append({
                    "job_slot": i + 1,
                    "worker_id": workers[i % len(workers)],
                    "status": "PLANNED",
                })

        return {
            "execution_mode": "CONTROLLED",
            "assignments": assignments,
            "message": f"{len(assignments)} job slot planned across {len(workers)} idle workers.",
        }
