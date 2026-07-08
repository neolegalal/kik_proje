# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "210"
sys.path.insert(0, str(PACKAGE_DIR))
from generators.module_generator import create_module

if __name__ == "__main__":
    print("210 Module Generator is installed. Use create_module from batch builder.")
