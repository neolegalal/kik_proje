# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.self_healing_decision_engine.engine import SelfHealingDecisionEngineModule

if __name__ == "__main__":
    res = SelfHealingDecisionEngineModule().run()
    assert "result" in res
    assert "paths" in res
    print("TEST PASS: self_healing_decision_engine")
