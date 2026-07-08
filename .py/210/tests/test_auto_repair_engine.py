# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.auto_repair_engine.engine import AutoRepairEngineModule

if __name__ == "__main__":
    res = AutoRepairEngineModule().run()
    assert "result" in res
    assert "paths" in res
    print("TEST PASS: auto_repair_engine")
