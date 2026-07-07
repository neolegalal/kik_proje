# -*- coding: utf-8 -*-
import argparse
from config import (
    DOCS_DIR, RELEASES_DIR, ARCHITECTURE_DIR, DECISIONS_DIR, RUNBOOKS_DIR,
    BACKUP_DIR, CHANGELOG_FILE, DEVELOPMENT_REPORT_FILE, RELEASE_V14_FILE
)
from utils import ensure_dirs, read_text, write_text, write_json, backup_file, file_status, now_stamp, now_text
from templates import CHANGELOG, RELEASE_V14, DEVELOPMENT_REPORT

def audit():
    ensure_dirs(DOCS_DIR, RELEASES_DIR, ARCHITECTURE_DIR, DECISIONS_DIR, RUNBOOKS_DIR, BACKUP_DIR)
    files = {
        "CHANGELOG": file_status(CHANGELOG_FILE),
        "DEVELOPMENT_REPORT": file_status(DEVELOPMENT_REPORT_FILE),
        "RELEASE_V14": file_status(RELEASE_V14_FILE),
    }

    problems = []
    for name, info in files.items():
        if not info["exists"]:
            problems.append(f"{name} yok.")
        elif info["size"] == 0:
            problems.append(f"{name} boş.")

    release_text = read_text(RELEASE_V14_FILE)
    if release_text.startswith("# CHANGELOG"):
        problems.append("RELEASE_V14 dosyasında CHANGELOG içeriği var; düzeltilmeli.")

    changelog_text = read_text(CHANGELOG_FILE)
    if "\\#" in changelog_text or "\\*" in changelog_text:
        problems.append("CHANGELOG içinde kaçış karakterleri var.")

    result = {
        "score": 100 - min(60, len(problems) * 10),
        "decision": "DOCS AUDIT CLEAN" if not problems else "DOCS AUDIT REVIEW",
        "problems": problems,
    }
    return {"files": files, "result": result}

def write_v14():
    ensure_dirs(DOCS_DIR, RELEASES_DIR, ARCHITECTURE_DIR, DECISIONS_DIR, RUNBOOKS_DIR, BACKUP_DIR)
    backups = {}
    for label, path in {
        "CHANGELOG": CHANGELOG_FILE,
        "RELEASE_V14": RELEASE_V14_FILE,
        "DEVELOPMENT_REPORT": DEVELOPMENT_REPORT_FILE,
    }.items():
        backups[label] = backup_file(path, BACKUP_DIR)

    write_text(CHANGELOG_FILE, CHANGELOG)
    write_text(RELEASE_V14_FILE, RELEASE_V14)
    write_text(DEVELOPMENT_REPORT_FILE, DEVELOPMENT_REPORT)

    return {
        "written": {
            "CHANGELOG": str(CHANGELOG_FILE),
            "RELEASE_V14": str(RELEASE_V14_FILE),
            "DEVELOPMENT_REPORT": str(DEVELOPMENT_REPORT_FILE),
        },
        "backups": backups,
    }

def write_report(action, data):
    ts = now_stamp()
    report = DOCS_DIR / f"DOCUMENTATION_MANAGER_REPORT_{ts}.md"
    content = [
        "# 206 Documentation Manager Report",
        "",
        f"**Tarih:** {now_text()}",
        f"**Action:** {action}",
        "",
        "## Sonuç",
        "",
        "```json",
        __import__("json").dumps(data, ensure_ascii=False, indent=2),
        "```",
    ]
    write_text(report, "\n".join(content))
    return str(report)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--write-v14", action="store_true")
    args = parser.parse_args()

    if args.write_v14:
        write_data = write_v14()
        audit_data = audit()
        data = {"write": write_data, "audit": audit_data}
        report = write_report("write-v14", data)
        print("="*80)
        print("206 DOCUMENTATION MANAGER TAMAMLANDI")
        print("="*80)
        print("Action   : write-v14")
        print(f"Decision : {audit_data['result']['decision']} ({audit_data['result']['score']}/100)")
        print(f"Problems : {len(audit_data['result']['problems'])}")
        print("")
        print("Yazılan dosyalar:")
        for p in write_data["written"].values():
            print(p)
        print("")
        print("Backup klasörü:")
        print(BACKUP_DIR)
        print("")
        print("Rapor:")
        print(report)
        return

    audit_data = audit()
    report = write_report("audit", audit_data)
    print("="*80)
    print("206 DOCUMENTATION MANAGER AUDIT TAMAMLANDI")
    print("="*80)
    print(f"Decision : {audit_data['result']['decision']} ({audit_data['result']['score']}/100)")
    print(f"Problems : {len(audit_data['result']['problems'])}")
    for p in audit_data["result"]["problems"]:
        print("-", p)
    print("")
    print("Rapor:")
    print(report)

if __name__ == "__main__":
    main()
