# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.policy_engine.engine import PolicyEngineModule

def test_run():
    res = PolicyEngineModule().run()
    assert "result" in res
    assert "paths" in res
    assert res["result"]["score"] is not None

if __name__ == "__main__":
    test_run()
    print("TEST PASS: policy_engine")
