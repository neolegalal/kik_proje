# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.safe_run_gate.engine import SafeRunGateModule

def test_run():
    res = SafeRunGateModule().run()
    assert "result" in res
    assert "paths" in res
    assert res["result"]["score"] is not None

if __name__ == "__main__":
    test_run()
    print("TEST PASS: safe_run_gate")
