# -*- coding: utf-8 -*-
from .config import EXECUTION_SNAPSHOT, EXECUTION_DASHBOARD, SCHEDULER_DASHBOARD
from .utils import safe_json

class AutomationLoader:
    def load_execution_snapshot(self):
        return safe_json(EXECUTION_SNAPSHOT) or {}

    def load_execution_dashboard(self):
        return safe_json(EXECUTION_DASHBOARD) or {}

    def load_scheduler_dashboard(self):
        return safe_json(SCHEDULER_DASHBOARD) or {}

    def load_all(self):
        return {
            "execution_snapshot": self.load_execution_snapshot(),
            "execution_dashboard": self.load_execution_dashboard(),
            "scheduler_dashboard": self.load_scheduler_dashboard(),
        }
