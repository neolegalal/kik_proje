# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_DIR))
from modules.healing_auditor.engine import HealingAuditorModule

if __name__ == "__main__":
    res = HealingAuditorModule().run()
    assert "result" in res
    assert "paths" in res
    print("TEST PASS: healing_auditor")
