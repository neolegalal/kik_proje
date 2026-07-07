# -*- coding: utf-8 -*-
r"""
199 v1 - Service Registry
NeoLegal Production Platform v2.0

Amaç:
- Platformdaki core, pipeline, certification, recovery ve orchestration servislerini keşfetmek.
- Her servis için script yolu, bulunma durumu, son değişiklik tarihi ve kategori üretmek.
- Merkezi servis kayıt dosyası oluşturmak.
- Bu sürüm production çalıştırmaz; yalnızca platform servis envanteri çıkarır.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\199_v1_Service_Registry.py"
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
REGISTRY_DIR = STATE_DIR / "service_registry"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

SERVICES = {
    "core": {
        "181": "Production Controller",
        "192": "Resume Engine",
        "193": "Smart Resume Validation",
        "194": "Production Guardian",
        "195": "Runtime Monitor",
    },
    "certification": {
        "196": "Production Certification Suite",
        "196B": "Dynamic Certification",
    },
    "recovery": {
        "197": "Recovery Manager",
    },
    "orchestration": {
        "198": "Distributed Processing / Queue / Worker",
        "199": "Production Manager",
    },
    "pipeline": {
        "168": "Production",
        "188": "Auto Cleaner",
        "172": "AI Quality",
        "175": "Coverage",
        "176": "Priority",
        "177": "Legal Accuracy",
        "185": "Self Healing",
        "178": "Merge",
        "179": "Optimize",
        "180": "Complexity",
        "169": "DB Import",
        "170": "Export",
        "173": "Acceptance",
        "182": "Drift",
        "183": "Sampling",
        "184": "Dashboard",
        "190": "Supervisor",
    }
}


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def find_scripts(prefix: str):
    if not PY_DIR.exists():
        return []

    candidates = []
    candidates.extend(PY_DIR.glob(f"{prefix}*.py"))
    candidates.extend(PY_DIR.glob(f"*{prefix}*.py"))
    candidates = list(set(candidates))

    # 199 v1 kendi dosyasını 199 için sayabilir; bu normal.
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates


def file_info(path: Path):
    try:
        return {
            "path": str(path),
            "name": path.name,
            "size_kb": round(path.stat().st_size / 1024, 2),
            "modified_at": datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception as e:
        return {
            "path": str(path),
            "name": path.name,
            "error": str(e),
        }


def build_registry():
    registry = {
        "module": "199 v1 Service Registry",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "py_dir": str(PY_DIR),
        "disk_free_gb": disk_free_gb(),
        "categories": {},
        "flat_services": {},
    }

    for category, service_map in SERVICES.items():
        registry["categories"][category] = {}

        for prefix, label in service_map.items():
            scripts = find_scripts(prefix)
            primary = scripts[0] if scripts else None

            item = {
                "prefix": prefix,
                "label": label,
                "category": category,
                "status": "FOUND" if primary else "MISSING",
                "primary_script": file_info(primary) if primary else None,
                "script_count": len(scripts),
                "all_scripts": [file_info(p) for p in scripts[:20]],
            }

            registry["categories"][category][prefix] = item
            registry["flat_services"][prefix] = item

    return registry


def evaluate(registry):
    score = 100
    errors = []
    warnings = []

    # Core eksikse ağır ceza
    for prefix, item in registry["categories"].get("core", {}).items():
        if item["status"] != "FOUND":
            score -= 10
            errors.append(f"Core service missing: {prefix} {item['label']}")

    # Pipeline eksikse daha hafif ceza
    for prefix, item in registry["categories"].get("pipeline", {}).items():
        if item["status"] != "FOUND":
            score -= 3
            warnings.append(f"Pipeline service missing: {prefix} {item['label']}")

    for cat in ["certification", "recovery", "orchestration"]:
        for prefix, item in registry["categories"].get(cat, {}).items():
            if item["status"] != "FOUND":
                score -= 5
                warnings.append(f"{cat} service missing: {prefix} {item['label']}")

    if registry["disk_free_gb"] < 50:
        score -= 20
        errors.append("Disk alanı 50 GB altında.")

    score = max(0, min(100, score))

    if errors:
        decision = "REGISTRY NOT READY"
    elif score >= 95:
        decision = "REGISTRY READY"
    elif score >= 85:
        decision = "REGISTRY LOW REVIEW"
    else:
        decision = "REGISTRY REVIEW"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
    }


def write_outputs(registry, result):
    registry_path = REGISTRY_DIR / "199_service_registry.json"
    json_path = STATE_DIR / f"199_v1_service_registry_state_{NOW}.json"
    txt_path = REPORT_DIR / f"199_v1_service_registry_raporu_{NOW}.txt"

    payload = {
        "registry": registry,
        "result": result,
    }

    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("199 v1 SERVICE REGISTRY")
    lines.append("=" * 80)
    lines.append(f"Tarih          : {registry['created_at']}")
    lines.append(f"Score          : {result['score']} / 100")
    lines.append(f"Decision       : {result['decision']}")
    lines.append(f"Disk Free      : {registry['disk_free_gb']} GB")
    lines.append("")

    for category, services in registry["categories"].items():
        lines.append("-" * 80)
        lines.append(category.upper())
        lines.append("-" * 80)
        for prefix, item in services.items():
            primary = item["primary_script"]["name"] if item["primary_script"] else "-"
            lines.append(
                f"{prefix:<5} {item['label']:<38} : {item['status']:<8} "
                f"| scripts={item['script_count']:<3} | primary={primary}"
            )
        lines.append("")

    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)
    if result["errors"]:
        for e in result["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)
    if result["warnings"]:
        for w in result["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines.append("")
    lines.append("NOT:")
    lines.append("199 v1 production çalıştırmaz. Merkezi service registry üretir.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(registry_path))
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return registry_path, json_path, txt_path


def main():
    ensure_dirs()
    registry = build_registry()
    result = evaluate(registry)
    registry_path, json_path, txt_path = write_outputs(registry, result)

    found = sum(1 for item in registry["flat_services"].values() if item["status"] == "FOUND")
    total = len(registry["flat_services"])

    print("=" * 80)
    print("199 v1 SERVICE REGISTRY TAMAMLANDI")
    print("=" * 80)
    print(f"Score       : {result['score']} / 100")
    print(f"Decision    : {result['decision']}")
    print(f"Found       : {found} / {total}")
    print(f"Errors      : {len(result['errors'])}")
    print(f"Warnings    : {len(result['warnings'])}")
    print(f"Disk Free   : {registry['disk_free_gb']} GB")
    print("")
    print("Dosyalar:")
    print(registry_path)
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
