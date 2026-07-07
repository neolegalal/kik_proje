# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "205"
sys.path.insert(0, str(PACKAGE_DIR))
from logger_intelligence_manager import main
if __name__ == "__main__":
    main()
