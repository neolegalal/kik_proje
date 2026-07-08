# -*- coding: utf-8 -*-
"""
302 ULTIMATE PLATFORM FACTORY - AUTO RELEASE EDITION

Bu sürüm 301 Platform Factory'yi kullanır ve tüm akışı otomatikleştirir:

1. Yeni layer/version/name belirler.
2. 301 Platform Factory ile katmanı üretir.
3. Run All testini otomatik çalıştırır.
4. FINAL DECISION PASS ise Git Release BAT dosyasını otomatik çalıştırır.
5. Git commit, push, tag ve tag push işlemleri otomatik yapılır.
6. Factory raporu üretir.

Örnek:
python ".py\\302_Ultimate_Platform_Factory_Auto_Release.py" --name "Security Governance"

Elle layer/version vermek istersen:
python ".py\\302_Ultimate_Platform_Factory_Auto_Release.py" --layer 304 --version v2.11 --name "Audit Intelligence"

Sadece üretip test etmek, Git'e göndermemek için:
python ".py\\302_Ultimate_Platform_Factory_Auto_Release.py" --name "Audit Intelligence" --no-git
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
FACTORY_STATE = STATE / "platform_factory"

FACTORY_301 = PY / "301_Platform_Factory.py"

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def slugify(text):
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.strip())
    text = re.sub(r"_+", "_", text)
    return text.strip("_").lower()

def kebab(text):
    return slugify(text).replace("_", "-")

def parse_version(version):
    m = re.match(r"v(\d+)\.(\d+)$", version.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))

def format_version(major, minor):
    return f"v{major}.{minor}"

def existing_layer_numbers():
    nums = set()
    for path in PY.glob("*_Run_All.py"):
        m = re.match(r"(\d+)_Run_All\.py$", path.name)
        if m:
            try:
                nums.add(int(m.group(1)))
            except Exception:
                pass
    for path in PY.glob("*_*.py"):
        m = re.match(r"(\d+)_", path.name)
        if m:
            try:
                nums.add(int(m.group(1)))
            except Exception:
                pass
    return sorted(nums)

def suggest_next_layer():
    nums = [n for n in existing_layer_numbers() if n >= 200]
    if not nums:
        return 220
    return max(nums) + 1

def existing_versions():
    versions = []
    if RELEASES.exists():
        for path in RELEASES.glob("v*-*.md"):
            m = re.match(r"(v\d+\.\d+)-", path.name)
            if m:
                parsed = parse_version(m.group(1))
                if parsed:
                    versions.append(parsed)
    if CHANGELOG.exists():
        txt = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"# (v\d+\.\d+) ", txt):
            parsed = parse_version(m.group(1))
            if parsed:
                versions.append(parsed)
    return versions

def suggest_next_version():
    versions = existing_versions()
    if not versions:
        return "v2.10"
    major, minor = max(versions)
    return format_version(major, minor + 1)

def smart_modules(layer_name):
    clean = layer_name.replace("Layer", "").strip()
    return [
        clean + " Controller",
        clean + " Registry",
        clean + " Policy Engine",
        clean + " Planner",
        clean + " Execution Engine",
        clean + " Monitor",
        clean + " Dashboard",
        clean + " Decision Engine",
        clean + " Auditor",
        clean + " Release Manager",
    ]

def check_conflicts(layer_id, version, name, release_slug):
    conflicts = []
    slug = slugify(name)
    class_part = "".join(x.capitalize() for x in slug.split("_") if x)
    paths = [
        PY / f"{layer_id}_Run_All.py",
        PY / f"{layer_id}_{class_part}_SDK.py",
        BASE / f"git_release_{version.replace('.', '_')}_{slug}.bat",
        RELEASES / f"{version}-{release_slug}.md",
    ]
    for path in paths:
        if path.exists():
            conflicts.append(str(path))
    return conflicts

def run_cmd(cmd, cwd=BASE):
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, shell=False)
    return {
        "cmd": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

def run_cmd_visible(cmd, cwd=BASE):
    return subprocess.run(cmd, cwd=str(cwd), shell=False)

def write_report(payload):
    FACTORY_STATE.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    ts = now_stamp()
    state_path = FACTORY_STATE / f"302_auto_release_factory_state_{ts}.json"
    report_path = REPORTS / f"302_auto_release_factory_raporu_{ts}.txt"

    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "=" * 80,
        "302 ULTIMATE PLATFORM FACTORY - AUTO RELEASE RAPORU",
        "=" * 80,
        "Created At       : " + str(payload.get("created_at")),
        "Layer            : " + str(payload.get("layer_id")),
        "Version          : " + str(payload.get("version")),
        "Name             : " + str(payload.get("name")),
        "Release Slug     : " + str(payload.get("release_slug")),
        "Modules          : " + str(len(payload.get("modules", []))),
        "Factory Decision : " + str(payload.get("factory_decision")),
        "Run Decision     : " + str(payload.get("run_decision")),
        "Git Decision     : " + str(payload.get("git_decision")),
        "Final Decision   : " + str(payload.get("final_decision")),
        "",
        "Run All Command:",
        str(payload.get("run_all_command")),
        "",
        "Git BAT:",
        str(payload.get("git_bat")),
        "",
        "State:",
        str(state_path),
        "Report:",
        str(report_path),
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return state_path, report_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", default="", help="Boş bırakılırsa otomatik önerilir.")
    parser.add_argument("--version", default="", help="Boş bırakılırsa otomatik önerilir.")
    parser.add_argument("--name", required=True, help='Örn: "Security Governance"')
    parser.add_argument("--modules", default="", help="Virgülle ayrılmış modül listesi. Boşsa akıllı varsayılan liste üretilir.")
    parser.add_argument("--release-slug", default="", help="Boşsa otomatik üretilir.")
    parser.add_argument("--force", action="store_true", help="Çakışma varsa yine de üret.")
    parser.add_argument("--no-git", action="store_true", help="PASS olsa bile Git release yapma.")
    parser.add_argument("--dry-run", action="store_true", help="Sadece planı göster; üretim/test/git yok.")
    args = parser.parse_args()

    if not FACTORY_301.exists():
        print("=" * 80)
        print("302 AUTO RELEASE BLOCKED")
        print("=" * 80)
        print("301 Platform Factory bulunamadı:")
        print(FACTORY_301)
        sys.exit(1)

    layer_id = args.layer.strip() or str(suggest_next_layer())
    version = args.version.strip() or suggest_next_version()
    name = args.name.strip()
    release_slug = args.release_slug.strip() or kebab(name) + "-layer"
    modules = [x.strip() for x in args.modules.split(",") if x.strip()] if args.modules else smart_modules(name)

    run_all = f"{layer_id}_Run_All.py"
    git_bat = BASE / f"git_release_{version.replace('.', '_')}_{slugify(name)}.bat"

    conflicts = check_conflicts(layer_id, version, name, release_slug)
    if conflicts and not args.force:
        payload = {
            "created_at": now_text(),
            "layer_id": layer_id,
            "version": version,
            "name": name,
            "release_slug": release_slug,
            "modules": modules,
            "factory_decision": "BLOCKED_BY_CONFLICT",
            "run_decision": "NOT_RUN",
            "git_decision": "NOT_RUN",
            "final_decision": "BLOCKED",
            "conflicts": conflicts,
            "run_all_command": f'python ".py\\{run_all}"',
            "git_bat": str(git_bat),
        }
        state_path, report_path = write_report(payload)
        print("=" * 80)
        print("302 AUTO RELEASE BLOCKED")
        print("=" * 80)
        print("Çakışan dosyalar bulundu. Devam etmek için --force kullan.")
        for item in conflicts:
            print("- " + item)
        print("")
        print("Report:")
        print(report_path)
        sys.exit(1)

    payload = {
        "created_at": now_text(),
        "layer_id": layer_id,
        "version": version,
        "name": name,
        "release_slug": release_slug,
        "modules": modules,
        "factory_decision": None,
        "run_decision": None,
        "git_decision": None,
        "final_decision": None,
        "conflicts": conflicts,
        "run_all_command": f'python ".py\\{run_all}"',
        "git_bat": str(git_bat),
    }

    print("=" * 80)
    print("302 ULTIMATE PLATFORM FACTORY - AUTO RELEASE")
    print("=" * 80)
    print("Layer       :", layer_id)
    print("Version     :", version)
    print("Name        :", name)
    print("Modules     :", len(modules))
    print("Git Auto    :", "NO" if args.no_git else "YES")
    print("Dry Run     :", "YES" if args.dry_run else "NO")
    print("=" * 80)

    if args.dry_run:
        payload["factory_decision"] = "DRY_RUN"
        payload["run_decision"] = "DRY_RUN"
        payload["git_decision"] = "DRY_RUN"
        payload["final_decision"] = "DRY_RUN"
        state_path, report_path = write_report(payload)
        print("DRY RUN tamamlandı.")
        print(report_path)
        sys.exit(0)

    factory_cmd = [
        sys.executable,
        str(FACTORY_301),
        "--layer", str(layer_id),
        "--version", str(version),
        "--name", str(name),
        "--modules", ",".join(modules),
        "--release-slug", release_slug,
    ]

    print("\n[1/3] Layer üretimi başlıyor...")
    factory_result = run_cmd(factory_cmd)
    payload["factory_301"] = factory_result

    if factory_result["stdout"]:
        print(factory_result["stdout"])
    if factory_result["stderr"]:
        print(factory_result["stderr"])

    if factory_result["returncode"] != 0:
        payload["factory_decision"] = "FAILED"
        payload["run_decision"] = "NOT_RUN"
        payload["git_decision"] = "NOT_RUN"
        payload["final_decision"] = "FAILED"
        state_path, report_path = write_report(payload)
        print("Factory FAILED.")
        print(report_path)
        sys.exit(1)

    payload["factory_decision"] = "READY"

    print("\n[2/3] Run All testi başlıyor...")
    run_result = run_cmd_visible([sys.executable, str(PY / run_all)], cwd=BASE)
    payload["run_returncode"] = run_result.returncode

    if run_result.returncode != 0:
        payload["run_decision"] = "FAIL"
        payload["git_decision"] = "NOT_RUN"
        payload["final_decision"] = "FAIL"
        state_path, report_path = write_report(payload)
        print("=" * 80)
        print("FINAL DECISION: FAIL")
        print("Git release yapılmadı.")
        print("Report:", report_path)
        print("=" * 80)
        sys.exit(1)

    payload["run_decision"] = "PASS"

    if args.no_git:
        payload["git_decision"] = "SKIPPED_BY_USER"
        payload["final_decision"] = "PASS_NO_GIT"
        state_path, report_path = write_report(payload)
        print("=" * 80)
        print("FINAL DECISION: PASS")
        print("Git release kullanıcı isteğiyle atlandı.")
        print("Report:", report_path)
        print("=" * 80)
        sys.exit(0)

    print("\n[3/3] Git release başlıyor...")
    if not git_bat.exists():
        payload["git_decision"] = "BAT_NOT_FOUND"
        payload["final_decision"] = "PASS_BUT_GIT_FAILED"
        state_path, report_path = write_report(payload)
        print("=" * 80)
        print("FINAL DECISION: PASS BUT GIT FAILED")
        print("Git BAT bulunamadı:")
        print(git_bat)
        print("Report:", report_path)
        print("=" * 80)
        sys.exit(1)

    git_result = run_cmd_visible(["cmd", "/c", str(git_bat)], cwd=BASE)
    payload["git_returncode"] = git_result.returncode

    if git_result.returncode != 0:
        payload["git_decision"] = "FAILED"
        payload["final_decision"] = "PASS_BUT_GIT_FAILED"
        state_path, report_path = write_report(payload)
        print("=" * 80)
        print("FINAL DECISION: PASS BUT GIT FAILED")
        print("Report:", report_path)
        print("=" * 80)
        sys.exit(1)

    payload["git_decision"] = "PUSHED"
    payload["final_decision"] = "PASS_AND_PUSHED"
    state_path, report_path = write_report(payload)

    print("=" * 80)
    print("FINAL DECISION: PASS AND PUSHED")
    print("=" * 80)
    print("Layer      :", layer_id, name)
    print("Version    :", version)
    print("GitHub     : PUSHED")
    print("Tag        :", version + "-" + release_slug)
    print("Report     :", report_path)
    print("=" * 80)
    sys.exit(0)


if __name__ == "__main__":
    main()
