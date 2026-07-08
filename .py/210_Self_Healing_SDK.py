# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "210"
sys.path.insert(0, str(PACKAGE_DIR))
from self_healing_sdk_manager import main
if __name__ == "__main__":
    main()
