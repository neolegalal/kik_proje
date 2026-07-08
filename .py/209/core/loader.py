# -*- coding: utf-8 -*-
from .config import AUTOMATION_SNAPSHOT, AUTOMATION_DASHBOARD
from .utils import safe_json

class AutonomousLoader:
    def load_automation_snapshot(self):
        return safe_json(AUTOMATION_SNAPSHOT) or {}

    def load_automation_dashboard(self):
        return safe_json(AUTOMATION_DASHBOARD) or {}

    def load_all(self):
        return {
            "automation_snapshot": self.load_automation_snapshot(),
            "automation_dashboard": self.load_automation_dashboard(),
        }
