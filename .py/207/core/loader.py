# -*- coding: utf-8 -*-
from .config import SCHEDULER_SNAPSHOT, SCHEDULER_DASHBOARD, QUEUE_FILE, WORKER_FILE
from .utils import safe_json

class ExecutionLoader:
    def load_scheduler_snapshot(self):
        return safe_json(SCHEDULER_SNAPSHOT) or {}

    def load_scheduler_dashboard(self):
        return safe_json(SCHEDULER_DASHBOARD) or {}

    def load_queue(self):
        return safe_json(QUEUE_FILE) or {}

    def load_workers(self):
        return safe_json(WORKER_FILE) or {}

    def load_all(self):
        return {
            "scheduler_snapshot": self.load_scheduler_snapshot(),
            "scheduler_dashboard": self.load_scheduler_dashboard(),
            "queue": self.load_queue(),
            "workers": self.load_workers(),
        }
