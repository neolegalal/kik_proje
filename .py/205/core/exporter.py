# -*- coding: utf-8 -*-
from .utils import write_json, now_stamp, now_text
from .config import STATE_DIR, REPORT_DIR, INTELLIGENCE_SDK_DIR, SDK_TEST_OUTPUT

class IntelligenceExporter:
    def export(self, payload, name_prefix="205_0_sdk"):
        ts = now_stamp()
        state = STATE_DIR / f"{name_prefix}_state_{ts}.json"
        report = REPORT_DIR / f"{name_prefix}_raporu_{ts}.txt"
        output = INTELLIGENCE_SDK_DIR / f"{name_prefix}_output.json"

        write_json(output, payload)
        write_json(state, payload)

        result = payload.get("result", {})
        lines = [
            "="*80,
            "205.0 INTELLIGENCE SDK",
            "="*80,
            f"Time      : {now_text()}",
            f"Score     : {result.get('score')}",
            f"Risk      : {result.get('risk_level')}",
            f"Decision  : {result.get('decision')}",
            "",
            "SUMMARY",
            "-"*80,
            result.get("executive_summary", ""),
            "",
            "RECOMMENDATION",
            "-"*80,
            result.get("recommendation", ""),
            "",
            "Dosyalar:",
            str(output),
            str(state),
            str(report),
        ]
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"output": str(output), "state": str(state), "report": str(report)}
