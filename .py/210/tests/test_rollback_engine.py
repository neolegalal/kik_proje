# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.rollback_engine.engine import RollbackEngineModule

if __name__ == "__main__":
    res = RollbackEngineModule().run()
    assert "result" in res
    assert "paths" in res
    print("TEST PASS: rollback_engine")
