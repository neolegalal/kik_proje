# -*- coding: utf-8 -*-
"""
196B v1 - Dynamic Certification Runner
NeoLegal Production Platform v2.0

Amaç:
- 196A statik sertifikasyondan sonra dinamik test sürecini başlatmak.
- Mevcut production modüllerini doğrudan bozucu şekilde çalıştırmadan önce
  komut, dosya, DB, rapor ve state hazırlığını kontrol etmek.
- 20 batch dynamic certification için güvenli bir "pre-flight + command plan" üretmek.

Not:
Bu v1 sürümü varsayılan olarak gerçek production çalıştırmaz.
Önce çalıştırılabilir komut planı, risk analizi ve dynamic certification raporu üretir.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje
python ".py\196B_v1_Dynamic_Certification_Runner.py"

Gerçek çalıştırma modu sonraki v2 sürümünde kontrollü olarak eklenecektir.
"""

import os
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
REPORT_DIR = BASE_DIR / "raporlar"
STATE_DIR = BASE_DIR / "production_state"
NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

DYNAMIC_BATCH_SIZE = 20

CORE_REQUIRED = {
    "181": "Production Controller",
    "192": "Resume Engine",
    "193": "Smart Resume Validation",
    "194": "Production Guardian",
    "195": "Runtime Monitor",
    "196": "Static Certification",
}

PIPELINE_REQUIRED = [
    "168", "188", "172", "175", "176", "177", "185",
    "178", "179", "180", "169", "170", "173",
    "182", "183", "184", "190"
]

LIKELY_ENTRYPOINTS = [
    "181",
    "168",
]


def ensure_dirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def find_files(prefix):
    files = []
    for folder in [PY_DIR, REPORT_DIR, STATE_DIR]:
        if folder.exists():
            files.extend(folder.glob(f"{prefix}*"))
            files.extend(folder.glob(f"*{prefix}*"))
    files = list(set(files))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def find_script(prefix):
    if not PY_DIR.exists():
        return None

    candidates = []
    candidates.extend(PY_DIR.glob(f"{prefix}*.py"))
    candidates.extend(PY_DIR.glob(f"*{prefix}*.py"))
    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if not candidates:
        return None

    # Kendini seçmesin
    filtered = [p for p in candidates if "196B" not in p.name]
    return filtered[0] if filtered else candidates[0]


def discover_db():
    candidates = []
    for p in BASE_DIR.rglob("*.db"):
        if "kik" in p.name.lower():
            candidates.append(p)

    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    if not candidates:
        return {
            "status": "FAIL",
            "path": None,
            "cards": 0,
            "message": "KİK DB bulunamadı."
        }

    db_path = candidates[0]

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        tables = [x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

        selected = None
        for name in ["hukuki_kartlar", "kararlar", "kik_kararlari", "cards", "legal_cards"]:
            if name in tables:
                selected = name
                break

        if not selected and tables:
            selected = tables[0]

        if not selected:
            conn.close()
            return {
                "status": "FAIL",
                "path": str(db_path),
                "cards": 0,
                "message": "DB var ancak tablo yok."
            }

        count = cur.execute(f"SELECT COUNT(*) FROM {selected}").fetchone()[0]
        conn.close()

        return {
            "status": "PASS" if count > 0 else "WARNING",
            "path": str(db_path),
            "table": selected,
            "cards": count,
            "message": f"DB bulundu. Tablo={selected}, kayıt={count}"
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "path": str(db_path),
            "cards": 0,
            "message": f"DB okunamadı: {e}"
        }


def module_inventory():
    core = {}
    for prefix, name in CORE_REQUIRED.items():
        script = find_script(prefix)
        files = find_files(prefix)
        core[prefix] = {
            "name": name,
            "script": str(script) if script else None,
            "files_found": len(files),
            "status": "PASS" if script else "FAIL"
        }

    pipeline = {}
    for prefix in PIPELINE_REQUIRED:
        script = find_script(prefix)
        files = find_files(prefix)
        pipeline[prefix] = {
            "script": str(script) if script else None,
            "files_found": len(files),
            "status": "PASS" if script else "FAIL"
        }

    return core, pipeline


def build_command_plan(core, pipeline):
    commands = []

    # Önce guardian
    if core.get("194", {}).get("script"):
        commands.append({
            "step": "guardian_preflight",
            "description": "Production Guardian ile ortam kontrolü",
            "command": f'python "{core["194"]["script"]}"',
            "required": True
        })

    # Sonra static certification
    latest_196 = core.get("196", {}).get("script")
    if latest_196:
        commands.append({
            "step": "static_certification",
            "description": "196 statik sertifikasyon kontrolü",
            "command": f'python "{latest_196}"',
            "required": True
        })

    # Production controller varsa 20 batch için ana aday.
    if core.get("181", {}).get("script"):
        commands.append({
            "step": "dynamic_20_batch_candidate",
            "description": "20 batch dynamic production aday komutu. v1 çalıştırmaz, yalnızca planlar.",
            "command": f'python "{core["181"]["script"]}" --batch={DYNAMIC_BATCH_SIZE}',
            "required": True
        })
    elif pipeline.get("168", {}).get("script"):
        commands.append({
            "step": "dynamic_20_batch_fallback",
            "description": "181 yoksa 168 production fallback aday komutu. v1 çalıştırmaz, yalnızca planlar.",
            "command": f'python "{pipeline["168"]["script"]}" --batch={DYNAMIC_BATCH_SIZE}',
            "required": True
        })

    # Runtime monitor
    if core.get("195", {}).get("script"):
        commands.append({
            "step": "runtime_monitor",
            "description": "Runtime Monitor ile sonuç kontrolü",
            "command": f'python "{core["195"]["script"]}"',
            "required": True
        })

    # Supervisor
    if pipeline.get("190", {}).get("script"):
        commands.append({
            "step": "production_supervisor",
            "description": "Production Supervisor ile nihai sağlık kontrolü",
            "command": f'python "{pipeline["190"]["script"]}"',
            "required": True
        })

    return commands


def evaluate(core, pipeline, db, disk_gb, command_plan):
    score = 100
    errors = []
    warnings = []

    if disk_gb < 50:
        score -= 20
        errors.append("Disk alanı 50 GB altında.")

    if db["status"] == "FAIL":
        score -= 25
        errors.append("DB bulunamadı veya okunamadı.")
    elif db["status"] == "WARNING":
        score -= 5
        warnings.append("DB uyarı verdi.")

    for k, v in core.items():
        if v["status"] != "PASS":
            score -= 6
            errors.append(f"Core script eksik: {k} {v['name']}")

    missing_pipeline = []
    for k, v in pipeline.items():
        if v["status"] != "PASS":
            missing_pipeline.append(k)

    if missing_pipeline:
        penalty = min(20, len(missing_pipeline) * 2)
        score -= penalty
        warnings.append(f"Eksik pipeline scriptleri: {', '.join(missing_pipeline)}")

    if not command_plan:
        score -= 20
        errors.append("Dynamic certification için komut planı oluşturulamadı.")

    # v1 gerçek production çalıştırmadığı için en yüksek karar CONDITIONAL olur.
    score = max(0, min(100, score))

    if errors:
        decision = "NOT READY FOR DYNAMIC RUN"
    elif score >= 80:
        decision = "READY FOR 196B v2 CONTROLLED RUN"
    else:
        decision = "CONDITIONAL - REVIEW REQUIRED"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings
    }


def write_outputs(payload):
    json_path = STATE_DIR / f"196B_v1_dynamic_certification_state_{NOW}.json"
    txt_path = REPORT_DIR / f"196B_v1_dynamic_certification_raporu_{NOW}.txt"
    bat_path = BASE_DIR / f"196B_v1_dynamic_certification_command_plan_{NOW}.bat"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("196B v1 DYNAMIC CERTIFICATION RUNNER")
    lines.append("=" * 80)
    lines.append(f"Tarih                : {payload['created_at']}")
    lines.append(f"Dynamic Batch Size   : {payload['dynamic_batch_size']}")
    lines.append(f"Score                : {payload['result']['score']} / 100")
    lines.append(f"Decision             : {payload['result']['decision']}")
    lines.append(f"Disk Free            : {payload['disk_free_gb']} GB")
    lines.append(f"DB Status            : {payload['db']['status']}")
    lines.append(f"DB Path              : {payload['db'].get('path')}")
    lines.append(f"DB Cards             : {payload['db'].get('cards')}")
    lines.append("")

    lines.append("-" * 80)
    lines.append("CORE SCRIPT INVENTORY")
    lines.append("-" * 80)
    for k, v in payload["core"].items():
        lines.append(f"{k} {v['name']:<30} : {v['status']} | script={v['script']}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("PIPELINE SCRIPT INVENTORY")
    lines.append("-" * 80)
    for k, v in payload["pipeline"].items():
        lines.append(f"{k:<5}: {v['status']} | script={v['script']}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("COMMAND PLAN")
    lines.append("-" * 80)
    for i, cmd in enumerate(payload["command_plan"], start=1):
        lines.append(f"{i}. {cmd['step']}")
        lines.append(f"   {cmd['description']}")
        lines.append(f"   {cmd['command']}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)
    if payload["result"]["errors"]:
        for e in payload["result"]["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)
    if payload["result"]["warnings"]:
        for w in payload["result"]["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")

    lines.append("")
    lines.append("-" * 80)
    lines.append("SONUC")
    lines.append("-" * 80)
    lines.append("Bu v1 sürümü gerçek üretim çalıştırmaz.")
    lines.append("Amaç, 196B v2 kontrollü dinamik test için güvenli komut planı üretmektir.")

    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))
    lines.append(str(bat_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    bat_lines = []
    bat_lines.append("@echo off")
    bat_lines.append("chcp 65001 > nul")
    bat_lines.append(f'cd /d "{BASE_DIR}"')
    bat_lines.append("echo 196B v1 command plan - otomatik calistirma dosyasidir.")
    bat_lines.append("echo Bu dosya v1 tarafindan plan olarak uretilmistir.")
    bat_lines.append("echo Gercek calistirmadan once raporu kontrol edin.")
    bat_lines.append("pause")
    for cmd in payload["command_plan"]:
        bat_lines.append("echo.")
        bat_lines.append(f"echo STEP: {cmd['step']}")
        bat_lines.append(cmd["command"])
        bat_lines.append("if errorlevel 1 goto ERR")
    bat_lines.append("echo.")
    bat_lines.append("echo 196B command plan tamamlandi.")
    bat_lines.append("goto END")
    bat_lines.append(":ERR")
    bat_lines.append("echo HATA: Bir adim basarisiz oldu.")
    bat_lines.append(":END")
    bat_lines.append("pause")

    bat_path.write_text("\n".join(bat_lines), encoding="utf-8")

    return json_path, txt_path, bat_path


def main():
    ensure_dirs()
    disk_gb = disk_free_gb()
    db = discover_db()
    core, pipeline = module_inventory()
    command_plan = build_command_plan(core, pipeline)
    result = evaluate(core, pipeline, db, disk_gb, command_plan)

    payload = {
        "module": "196B v1 Dynamic Certification Runner",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "dynamic_batch_size": DYNAMIC_BATCH_SIZE,
        "disk_free_gb": disk_gb,
        "db": db,
        "core": core,
        "pipeline": pipeline,
        "command_plan": command_plan,
        "result": result
    }

    json_path, txt_path, bat_path = write_outputs(payload)

    print("=" * 80)
    print("196B v1 DYNAMIC CERTIFICATION RUNNER TAMAMLANDI")
    print("=" * 80)
    print(f"Score      : {result['score']} / 100")
    print(f"Decision   : {result['decision']}")
    print(f"Errors     : {len(result['errors'])}")
    print(f"Warnings   : {len(result['warnings'])}")
    print(f"Disk Free  : {disk_gb} GB")
    print(f"DB Status  : {db['status']}")
    print(f"DB Cards   : {db.get('cards')}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)
    print(bat_path)


if __name__ == "__main__":
    main()
