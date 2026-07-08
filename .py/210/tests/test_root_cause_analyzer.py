# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.root_cause_analyzer.engine import RootCauseAnalyzerModule

if __name__ == "__main__":
    res = RootCauseAnalyzerModule().run()
    assert "result" in res
    assert "paths" in res
    print("TEST PASS: root_cause_analyzer")
