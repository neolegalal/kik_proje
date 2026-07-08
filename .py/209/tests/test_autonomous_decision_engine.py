# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.autonomous_decision_engine.engine import AutonomousDecisionEngineModule

def test_run():
    res = AutonomousDecisionEngineModule().run()
    assert "result" in res
    assert "paths" in res
    assert res["result"]["score"] is not None

if __name__ == "__main__":
    test_run()
    print("TEST PASS: autonomous_decision_engine")
