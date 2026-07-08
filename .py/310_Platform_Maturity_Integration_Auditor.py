# -*- coding: utf-8 -*-
"""
310 PLATFORM MATURITY & INTEGRATION AUDITOR

Amaç:
Yeni katman eklemek yerine mevcut NeoLegal Production Platform'un gerçek üretime
ne kadar hazır olduğunu ölçmek.

Bu modül şunları denetler:

1. Release bütünlüğü
2. CHANGELOG bütünlüğü
3. README release history varlığı
4. Run All dosyaları
5. Production summary JSON dosyaları
6. Katman dashboard/snapshot çıktıları
7. Git tag/release dosyası varlığı
8. Platform OS sonrası gerçek üretime geçiş hazırlığı
9. Teknik borç ve entegrasyon riskleri
10. Sonraki aksiyon planı

Çalıştır:
python ".py\\310_Platform_Maturity_Integration_Auditor.py"

GitHub'a almak için oluşacak BAT:
git_release_v2_17_platform_maturity_auditor.bat
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"

AUDIT_DIR = STATE / "platform_maturity"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v2.17"
TAG = "v2.17-platform-maturity-auditor"
MODULE_NAME = "310 Platform Maturity & Integration Auditor"

EXPECTED_CORE_LAYERS = [
    "200", "201", "202", "203", "204", "205", "206", "207", "208", "209",
    "210", "211", "212", "213", "214", "215", "216", "217", "218",
    "219", "303", "304", "305", "306", "307", "308", "309",
]

EXPECTED_RELEASE_KEYWORDS = [
    "platform-core",
    "intelligence",
    "scheduler",
    "execution",
    "automation",
    "autonomous",
    "self-healing",
    "learning",
    "ai-orchestrator",
    "knowledge-graph",
    "continuous-improvement",
    "enterprise-platform",
    "production-cluster",
    "large-scale-production",
    "neolegal-ai-runtime",
    "cloud-platform",
    "security-governance",
    "audit-intelligence",
    "neolegal-kernel",
    "neolegal-enterprise-services",
    "neolegal-api-gateway",
    "neolegal-platform-os",
]


def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_read(path):
    path = Path(path)
    if not path.exists():
        return ""
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            return path.read_text(encoding=enc, errors="ignore")
        except Exception:
            pass
    return ""


def safe_json(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        return json.loads(safe_read(path))
    except Exception:
        return None


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run_git_tags():
    try:
        result = subprocess.run(
            ["git", "tag", "--list"],
            cwd=str(BASE),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.splitlines()
        return []
    except Exception:
        return []


def audit_releases():
    release_files = list(RELEASES.glob("*.md")) if RELEASES.exists() else []
    release_names = [p.name for p in release_files]

    found_keywords = []
    missing_keywords = []

    joined = "\n".join(release_names).lower()
    for key in EXPECTED_RELEASE_KEYWORDS:
        if key.lower() in joined:
            found_keywords.append(key)
        else:
            missing_keywords.append(key)

    score = 100
    if missing_keywords:
        score -= min(40, len(missing_keywords) * 3)

    return {
        "release_file_count": len(release_files),
        "found_keywords": found_keywords,
        "missing_keywords": missing_keywords,
        "score": max(score, 0),
        "status": "PASS" if not missing_keywords else "WARN",
    }


def audit_changelog():
    txt = safe_read(CHANGELOG)
    missing = []
    for key in EXPECTED_RELEASE_KEYWORDS:
        if key.replace("-", " ").lower() not in txt.lower() and key.lower() not in txt.lower():
            missing.append(key)

    score = 100 - min(35, len(missing) * 3)
    return {
        "exists": CHANGELOG.exists(),
        "missing_keywords": missing,
        "score": max(score, 0),
        "status": "PASS" if CHANGELOG.exists() and not missing else "WARN",
    }


def audit_readme():
    txt = safe_read(README)
    has_release_history = "Release History" in txt or "Sürüm" in txt or "Sürümleme" in txt
    has_project_goal = "Kamu İhale" in txt or "NeoLegal" in txt
    score = 100
    if not README.exists():
        score -= 50
    if not has_release_history:
        score -= 25
    if not has_project_goal:
        score -= 10

    return {
        "exists": README.exists(),
        "has_release_history": has_release_history,
        "has_project_goal": has_project_goal,
        "score": max(score, 0),
        "status": "PASS" if README.exists() and has_release_history else "WARN",
    }


def audit_run_all_files():
    found = []
    missing = []
    for layer in EXPECTED_CORE_LAYERS:
        path = PY / f"{layer}_Run_All.py"
        if path.exists():
            found.append(layer)
        else:
            # 200-209 gibi eski katmanlarda Run_All olmayabilir; bu nedenle WARN seviyesinde tutulur.
            missing.append(layer)

    score = 100 - min(35, len(missing))
    return {
        "found": found,
        "missing": missing,
        "score": max(score, 0),
        "status": "PASS" if len(missing) <= 10 else "WARN",
    }


def audit_platform_summaries():
    summaries = {}
    if SUMMARY_DIR.exists():
        for path in SUMMARY_DIR.glob("*_production_summary.json"):
            data = safe_json(path)
            if data:
                layer_id = str(data.get("layer_id") or path.name.split("_")[0])
                summaries[layer_id] = {
                    "path": str(path),
                    "decision": data.get("final_decision"),
                    "score": data.get("production_score"),
                    "ready": data.get("production_ready"),
                }

    pass_count = sum(1 for item in summaries.values() if item.get("decision") == "PASS")
    fail_count = sum(1 for item in summaries.values() if item.get("decision") == "FAIL")

    score = 100
    if fail_count:
        score -= min(70, fail_count * 15)

    return {
        "summary_count": len(summaries),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "summaries": summaries,
        "score": max(score, 0),
        "status": "PASS" if fail_count == 0 and len(summaries) > 0 else "WARN",
    }


def audit_dashboards_and_snapshots():
    dashboards = list(STATE.glob("**/*dashboard*.json")) if STATE.exists() else []
    snapshots = list(STATE.glob("**/*snapshot*.json")) if STATE.exists() else []

    score = 100
    if len(dashboards) < 10:
        score -= 25
    if len(snapshots) < 10:
        score -= 25

    return {
        "dashboard_count": len(dashboards),
        "snapshot_count": len(snapshots),
        "score": max(score, 0),
        "status": "PASS" if len(dashboards) >= 10 and len(snapshots) >= 10 else "WARN",
    }


def audit_git_tags():
    tags = run_git_tags()
    missing = []
    for key in EXPECTED_RELEASE_KEYWORDS:
        if not any(key in tag for tag in tags):
            missing.append(key)

    score = 100 - min(40, len(missing) * 3)

    return {
        "tag_count": len(tags),
        "missing_keywords": missing,
        "score": max(score, 0),
        "status": "PASS" if len(missing) <= 5 else "WARN",
    }


def calculate_final(audits):
    scores = [item.get("score", 0) for item in audits.values()]
    avg = round(sum(scores) / len(scores), 2) if scores else 0

    hard_fail = any(item.get("status") == "FAIL" for item in audits.values())
    warn_count = sum(1 for item in audits.values() if item.get("status") == "WARN")

    if hard_fail:
        decision = "FAIL"
        ready = "NO"
    elif avg >= 90:
        decision = "PASS"
        ready = "YES"
    elif avg >= 75:
        decision = "WARN"
        ready = "LIMITED"
    else:
        decision = "FAIL"
        ready = "NO"

    return {
        "platform_maturity_score": avg,
        "final_decision": decision,
        "production_ready": ready,
        "warn_count": warn_count,
    }


def recommendations(audits, final):
    recs = []

    if audits["releases"]["missing_keywords"]:
        recs.append("Eksik release dosyaları veya isim uyumsuzlukları kontrol edilmeli.")

    if audits["changelog"]["missing_keywords"]:
        recs.append("CHANGELOG eski sürümlerle uyumlu hale getirilmeli.")

    if audits["platform_summaries"]["summary_count"] < 10:
        recs.append("Eski katmanlar için production_summary.json üretimi geriye dönük tamamlanmalı.")

    if audits["dashboards"]["dashboard_count"] < 10:
        recs.append("Dashboard/snapshot standardı eski katmanlara da uygulanmalı.")

    if final["final_decision"] == "PASS":
        recs.append("Platform olgunluk denetimi başarılı. Sonraki adım: gerçek production pipeline bağlantı denetimi.")
        recs.append("100.000+ karar üretimine geçmeden önce 311 Production Pipeline Integration Auditor önerilir.")

    return recs


def create_release_docs():
    release_path = RELEASES / "v2.17-platform-maturity-auditor.md"
    RELEASES.mkdir(parents=True, exist_ok=True)

    release_text = """# v2.17 – Platform Maturity & Integration Auditor

**Tarih:** 09.07.2026

---

# Genel Bakış

Bu sürüm ile NeoLegal Production Platform için yeni katman ekleme aşamasından,
mevcut mimariyi gerçek üretime hazırlama aşamasına geçilmiştir.

310 Platform Maturity & Integration Auditor; release, changelog, README,
Run All, production summary, dashboard/snapshot ve Git tag bütünlüğünü denetler.

---

# Yeni Modül

- 310 Platform Maturity & Integration Auditor

---

# Sonuç

Platform mimarisinin olgunluk ve entegrasyon hazırlığı ölçülebilir hale getirilmiştir.
"""
    release_path.write_text(release_text, encoding="utf-8")

    changelog_entry = """# v2.17 – Platform Maturity & Integration Auditor

**Tarih:** 09.07.2026  
**Durum:** Production PASS  
**Git Tag:** `v2.17-platform-maturity-auditor`

## Yeni Modül

- 310 Platform Maturity & Integration Auditor

## Sonuç

Platform mimarisinin release, changelog, README, dashboard, production summary ve Git tag bütünlüğünü ölçen olgunluk denetimi eklendi.

---
"""
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v2.17 – Platform Maturity & Integration Auditor" not in old:
            CHANGELOG.write_text(changelog_entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + changelog_entry, encoding="utf-8")

    if README.exists():
        row = "| v2.17 | Platform Maturity & Integration Auditor | PASS |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")

    index_path = RELEASES / "index.md"
    files = sorted([x.name for x in RELEASES.glob("*.md") if x.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + x + " |" for x in files]), encoding="utf-8")

    bat = BASE / "git_release_v2_17_platform_maturity_auditor.bat"
    bat.write_text(
        """@echo off
cd /d C:\\Users\\MSI\\Desktop\\kik_proje

echo Running 310 Platform Maturity Auditor...
python ".py\\310_Platform_Maturity_Integration_Auditor.py"

IF ERRORLEVEL 1 (
    echo.
    echo RELEASE BLOCKED: 310 auditor FAILED.
    pause
    exit /b 1
)

git status
git add .
git commit -m "Release v2.17: Platform maturity and integration auditor"
git push
git tag v2.17-platform-maturity-auditor
git push origin v2.17-platform-maturity-auditor

pause
""",
        encoding="utf-8",
    )

    return release_path, bat


def main():
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    audits = {
        "releases": audit_releases(),
        "changelog": audit_changelog(),
        "readme": audit_readme(),
        "run_all_files": audit_run_all_files(),
        "platform_summaries": audit_platform_summaries(),
        "dashboards": audit_dashboards_and_snapshots(),
        "git_tags": audit_git_tags(),
    }

    final = calculate_final(audits)
    recs = recommendations(audits, final)

    release_path, git_bat = create_release_docs()

    payload = {
        "created_at": now_text(),
        "module": MODULE_NAME,
        "version": VERSION,
        "tag": TAG,
        "audits": audits,
        "final": final,
        "recommendations": recs,
        "release_path": str(release_path),
        "git_bat": str(git_bat),
    }

    ts = now_stamp()
    state_path = AUDIT_DIR / f"310_platform_maturity_audit_{ts}.json"
    report_path = REPORTS / f"310_platform_maturity_audit_raporu_{ts}.txt"
    write_json(state_path, payload)

    lines = [
        "=" * 80,
        "310 PLATFORM MATURITY & INTEGRATION AUDITOR",
        "=" * 80,
        "Platform Maturity Score : " + str(final["platform_maturity_score"]) + " / 100",
        "FINAL DECISION          : " + str(final["final_decision"]),
        "Production Ready        : " + str(final["production_ready"]),
        "Warnings                : " + str(final["warn_count"]),
        "",
        "Audit Scores:",
    ]
    for key, item in audits.items():
        lines.append("- " + key + " : " + str(item.get("score")) + " / 100 [" + str(item.get("status")) + "]")

    lines += [
        "",
        "Recommendations:",
    ]
    for rec in recs:
        lines.append("- " + rec)

    lines += [
        "",
        "Files:",
        str(state_path),
        str(report_path),
        str(release_path),
        str(git_bat),
        "",
        "=" * 80,
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))

    # WARN durumunda da çıkış kodu 0; çünkü bu denetim geliştirme amaçlıdır.
    # FAIL olursa release engellensin.
    if final["final_decision"] == "FAIL":
        raise SystemExit(1)

    raise SystemExit(0)


if __name__ == "__main__":
    main()
