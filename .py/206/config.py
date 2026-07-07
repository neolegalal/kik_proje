# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
DOCS_DIR = BASE_DIR / "docs"
RELEASES_DIR = DOCS_DIR / "releases"
ARCHITECTURE_DIR = DOCS_DIR / "architecture"
DECISIONS_DIR = DOCS_DIR / "decisions"
RUNBOOKS_DIR = DOCS_DIR / "runbooks"
BACKUP_DIR = DOCS_DIR / "_doc_backups"

CHANGELOG_FILE = DOCS_DIR / "CHANGELOG.md"
DEVELOPMENT_REPORT_FILE = DOCS_DIR / "DEVELOPMENT_REPORT.md"
RELEASE_V14_FILE = RELEASES_DIR / "v1.4-platform-core-services.md"
ARCHITECTURE_FILE = ARCHITECTURE_DIR / "Production_Platform_v2.md"

VERSION = "v1.4-platform-core-services"
RELEASE_DATE = "07.07.2026"
