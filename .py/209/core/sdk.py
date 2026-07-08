# -*- coding: utf-8 -*-
from .loader import AutonomousLoader
from .context import AutonomousContextBuilder
from .validator import AutonomousValidator
from .planner import AutonomousPlanner
from .exporter import AutonomousExporter
from .utils import now_text

class AutonomousSDK:
    def __init__(self, name="209.0 Autonomous Operations SDK"):
        self.name = name
        self.loader = AutonomousLoader()
        self.context_builder = AutonomousContextBuilder()
        self.validator = AutonomousValidator()
        self.planner = AutonomousPlanner()
        self.exporter = AutonomousExporter()

    def run(self):
        raw = self.loader.load_all()
        context = self.context_builder.build(raw)
        validation = self.validator.validate(context)
        plan = self.planner.plan(context, validation)
        payload = {"module": self.name, "created_at": now_text(), "context": context, "validation": validation, "plan": plan}
        paths = self.exporter.export(payload)
        return {"payload": payload, "paths": paths}
