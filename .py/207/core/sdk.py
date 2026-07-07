# -*- coding: utf-8 -*-
from .loader import ExecutionLoader
from .context import ExecutionContextBuilder
from .validator import ExecutionValidator
from .planner import ExecutionPlanner
from .exporter import ExecutionExporter
from .utils import now_text

class ExecutionSDK:
    def __init__(self, name="207.0 Execution SDK"):
        self.name = name
        self.loader = ExecutionLoader()
        self.context_builder = ExecutionContextBuilder()
        self.validator = ExecutionValidator()
        self.planner = ExecutionPlanner()
        self.exporter = ExecutionExporter()

    def run(self):
        raw = self.loader.load_all()
        context = self.context_builder.build(raw)
        validation = self.validator.validate(context)
        plan = self.planner.plan(context, validation)
        payload = {
            "module": self.name,
            "created_at": now_text(),
            "context": context,
            "validation": validation,
            "plan": plan,
        }
        paths = self.exporter.export(payload)
        return {"payload": payload, "paths": paths}
