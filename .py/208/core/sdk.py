# -*- coding: utf-8 -*-
from .loader import AutomationLoader
from .context import AutomationContextBuilder
from .validator import AutomationValidator
from .planner import AutomationPlanner
from .exporter import AutomationExporter
from .utils import now_text

class AutomationSDK:
    def __init__(self, name="208.0 Automation SDK"):
        self.name = name
        self.loader = AutomationLoader()
        self.context_builder = AutomationContextBuilder()
        self.validator = AutomationValidator()
        self.planner = AutomationPlanner()
        self.exporter = AutomationExporter()

    def run(self):
        raw = self.loader.load_all()
        context = self.context_builder.build(raw)
        validation = self.validator.validate(context)
        plan = self.planner.plan(context, validation)
        payload = {"module": self.name, "created_at": now_text(), "context": context, "validation": validation, "plan": plan}
        paths = self.exporter.export(payload)
        return {"payload": payload, "paths": paths}
