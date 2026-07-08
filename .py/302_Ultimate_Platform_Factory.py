# -*- coding: utf-8 -*-
"""
302 ULTIMATE PLATFORM FACTORY

301 Platform Factory'nin bir üst sürümüdür.

Amaç:
Yeni katman üretimini daha akıllı hale getirmek.

Özellikler:
- Sonraki layer numarasını otomatik önerir.
- Sonraki version numarasını otomatik önerir.
- İsim / dosya çakışması kontrolü yapar.
- Modül listesi verilmezse layer adına göre akıllı varsayılan 10 modül üretir.
- 301 Platform Factory'yi kullanarak katmanı üretir.
- Üretim sonrası Run All komutunu gösterir.
- Git BAT dosyasını gösterir.
- Factory report üretir.

Örnek:
python ".py\\302_Ultimate_Platform_Factory.py" --name "Security Governance"

Otomatik olarak şunu hesaplar:
--layer 220
--version v3.0

İstersen elle de verebilirsin:
python ".py\\302_Ultimate_Platform_Factory.py" --layer 220 --version v3.0 --name "Security Governance"
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
README = BASE / "README.md"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
FACTORY_STATE = STATE / "platform_factory"
FACTORY_REPORTS = REPORTS

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


def camel(text):
    return "".join(x.capitalize() for x in slugify(text).split("_") if x)


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
            nums.add(int(m.group(1)))
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
            name = path.name
            m = re.match(r"(v\d+\.\d+)-", name)
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
        return "v3.0"
    major, minor = max(versions)
    return format_version(major, minor + 1)


def smart_modules(layer_name):
    base = layer_name.strip()
    clean = base.replace("Layer", "").strip()
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
    class_part = camel(name)

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


def run_301(layer_id, version, name, modules, release_slug, dry_run=False):
    cmd = [
        sys.executable,
        str(FACTORY_301),
        "--layer",
        str(layer_id),
        "--version",
        str(version),
        "--name",
        str(name),
        "--modules",
        ",".join(modules),
        "--release-slug",
        release_slug,
    ]

    if dry_run:
        return {"returncode": 0, "cmd": cmd, "stdout": "DRY RUN", "stderr": ""}

    result = subprocess.run(cmd, cwd=str(BASE), capture_output=True, text=True)
    return {
        "returncode": result.returncode,
        "cmd": cmd,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def write_factory_report(payload):
    FACTORY_STATE.mkdir(parents=True, exist_ok=True)
    FACTORY_REPORTS.mkdir(parents=True, exist_ok=True)

    ts = now_stamp()
    state_path = FACTORY_STATE / f"302_ultimate_factory_state_{ts}.json"
    report_path = FACTORY_REPORTS / f"302_ultimate_factory_raporu_{ts}.txt"

    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "=" * 80,
        "302 ULTIMATE PLATFORM FACTORY RAPORU",
        "=" * 80,
        "Created At     : " + str(payload.get("created_at")),
        "Layer          : " + str(payload.get("layer_id")),
        "Version        : " + str(payload.get("version")),
        "Name           : " + str(payload.get("name")),
        "Release Slug   : " + str(payload.get("release_slug")),
        "Modules        : " + str(len(payload.get("modules", []))),
        "Decision       : " + str(payload.get("decision")),
        "Conflicts      : " + str(len(payload.get("conflicts", []))),
        "",
        "Modules:",
    ]
    for item in payload.get("modules", []):
        lines.append("- " + item)

    lines += [
        "",
        "Run All:",
        str(payload.get("run_all_command")),
        "",
        "Git BAT:",
        str(payload.get("git_bat")),
        "",
        "301 Return Code:",
        str(payload.get("factory_301", {}).get("returncode")),
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
    parser.add_argument("--dry-run", action="store_true", help="Üretmeden sadece planı göster.")
    args = parser.parse_args()

    if not FACTORY_301.exists():
        print("=" * 80)
        print("302 ULTIMATE PLATFORM FACTORY BLOCKED")
        print("=" * 80)
        print("301 Platform Factory bulunamadı:")
        print(FACTORY_301)
        sys.exit(1)

    layer_id = args.layer.strip() or str(suggest_next_layer())
    version = args.version.strip() or suggest_next_version()
    name = args.name.strip()
    release_slug = args.release_slug.strip() or kebab(name) + "-layer"

    modules = [x.strip() for x in args.modules.split(",") if x.strip()] if args.modules else smart_modules(name)

    conflicts = check_conflicts(layer_id, version, name, release_slug)
    if conflicts and not args.force:
        payload = {
            "created_at": now_text(),
            "layer_id": layer_id,
            "version": version,
            "name": name,
            "release_slug": release_slug,
            "modules": modules,
            "decision": "BLOCKED_BY_CONFLICT",
            "conflicts": conflicts,
            "run_all_command": f'python ".py\\{layer_id}_Run_All.py"',
            "git_bat": str(BASE / f"git_release_{version.replace('.', '_')}_{slugify(name)}.bat"),
            "factory_301": {"returncode": None},
        }
        state_path, report_path = write_factory_report(payload)

        print("=" * 80)
        print("302 ULTIMATE PLATFORM FACTORY BLOCKED")
        print("=" * 80)
        print("Çakışan dosyalar bulundu. Devam etmek için --force kullan.")
        for item in conflicts:
            print("- " + item)
        print("")
        print("Report:")
        print(report_path)
        sys.exit(1)

    factory_result = run_301(layer_id, version, name, modules, release_slug, dry_run=args.dry_run)
    decision = "READY" if factory_result["returncode"] == 0 else "FAILED"

    payload = {
        "created_at": now_text(),
        "layer_id": layer_id,
        "version": version,
        "name": name,
        "release_slug": release_slug,
        "modules": modules,
        "decision": decision,
        "conflicts": conflicts,
        "run_all_command": f'python ".py\\{layer_id}_Run_All.py"',
        "git_bat": str(BASE / f"git_release_{version.replace('.', '_')}_{slugify(name)}.bat"),
        "factory_301": factory_result,
    }
    state_path, report_path = write_factory_report(payload)

    print("=" * 80)
    print("302 ULTIMATE PLATFORM FACTORY TAMAMLANDI")
    print("=" * 80)
    print("Decision      :", decision)
    print("Layer         :", layer_id)
    print("Version       :", version)
    print("Name          :", name)
    print("Release Slug  :", release_slug)
    print("Modules       :", len(modules))
    print("Dry Run       :", "YES" if args.dry_run else "NO")
    print("")
    print("Run All:")
    print(payload["run_all_command"])
    print("")
    print("Git BAT:")
    print(payload["git_bat"])
    print("")
    print("Report:")
    print(report_path)

    if factory_result["stdout"]:
        print("")
        print("301 Output:")
        print(factory_result["stdout"])

    if factory_result["stderr"]:
        print("")
        print("301 Errors:")
        print(factory_result["stderr"])

    sys.exit(0 if decision == "READY" else 1)


if __name__ == "__main__":
    main()
