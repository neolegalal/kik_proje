# -*- coding: utf-8 -*-
from .loader import SchedulerLoader
from .context import SchedulerContextBuilder
from .validator import SchedulerValidator
from .decision import SchedulerDecisionHelper
from .exporter import SchedulerExporter
from .utils import now_text

class SchedulerSDK:
    def __init__(self, name="206.0 Scheduler SDK"):
        self.name = name
        self.loader = SchedulerLoader()
        self.context_builder = SchedulerContextBuilder()
        self.validator = SchedulerValidator()
        self.decision_helper = SchedulerDecisionHelper()
        self.exporter = SchedulerExporter()

    def run(self):
        raw = self.loader.load_all()
        context = self.context_builder.build(raw)
        validation = self.validator.validate(context)
        decision = self.decision_helper.decide(context, validation)
        payload = {"module": self.name, "created_at": now_text(), "context": context, "validation": validation, "decision": decision}
        paths = self.exporter.export(payload)
        return {"payload": payload, "paths": paths}
