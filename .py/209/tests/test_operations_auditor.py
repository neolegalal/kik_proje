# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.operations_auditor.engine import OperationsAuditorModule

def test_run():
    res = OperationsAuditorModule().run()
    assert "result" in res
    assert "paths" in res
    assert res["result"]["score"] is not None

if __name__ == "__main__":
    test_run()
    print("TEST PASS: operations_auditor")
