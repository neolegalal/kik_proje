# -*- coding: utf-8 -*-
r"""
200 v2 - Configuration Manager
NeoLegal Production Platform v2.0

Amaç:
- Platform ayarlarını tek merkezde toplamak.
- config dosyası oluşturmak / okumak / doğrulamak.
- 200 Platform Core'un sonraki sürümlerinde kullanılacak merkezi yapılandırma tabanını kurmak.
- Production çalıştırmaz.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Varsayılan config oluştur / doğrula:
python ".py\200_v2_Configuration_Manager.py" --init

Config durumunu göster:
python ".py\200_v2_Configuration_Manager.py" --status

Config doğrula:
python ".py\200_v2_Configuration_Manager.py" --validate
"""

import argparse
import json
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
STATE_DIR = BASE_DIR / "production_state"
REPORT_DIR = BASE_DIR / "raporlar"
CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "neolegal_platform_config.json"

NOW = datetime.now().strftime("%Y%m%d_%H%M%S")


DEFAULT_CONFIG = {
    "platform": {
        "name": "NeoLegal Production Platform",
        "version": "2.0",
        "environment": "local",
        "default_entrypoint": "200_Platform_Core",
    },
    "paths": {
        "base_dir": str(BASE_DIR),
        "py_dir": str(PY_DIR),
        "state_dir": str(STATE_DIR),
        "report_dir": str(REPORT_DIR),
        "config_dir": str(CONFIG_DIR),
    },
    "runtime": {
        "min_disk_gb": 50,
        "default_timeout_seconds": 3600,
        "safe_mode_default": True,
        "production_execute_requires_flag": True,
    },
    "queue": {
        "default_worker": "worker-1",
        "default_worker_pool": ["worker-1", "worker-2", "worker-3"],
        "max_attempts": 3,
        "default_batch_size": 10,
    },
    "modes": {
        "status": True,
        "health": True,
        "registry": True,
        "plan": True,
        "execute": False,
        "production": False,
        "maintenance": True,
    },
    "quality_gates": {
        "require_registry_ready": True,
        "require_platform_ready": True,
        "require_recovery_clean": True,
        "require_no_active_worker_running": True,
        "require_no_failed_jobs": True,
    },
    "github": {
        "release_policy": "develop -> validation -> tag -> merge -> main -> production",
        "last_confirmed_tag": "v1.3-dynamic-certification-recovery-pass",
    },
    "notes": [
        "200 v2 Configuration Manager tarafından oluşturuldu.",
        "Bu dosya production çalıştırmaz; yalnızca merkezi ayarları yönetir."
    ]
}


def ensure_dirs():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def read_config():
    if not CONFIG_FILE.exists():
        return None
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_config(config):
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def init_config(force=False):
    existing = read_config()
    if existing and not force:
        return existing, False

    config = dict(DEFAULT_CONFIG)
    config["created_at"] = now_text()
    config["updated_at"] = now_text()
    write_config(config)
    return config, True


def validate_config(config):
    errors = []
    warnings = []

    if not config:
        errors.append("Config dosyası yok veya okunamadı.")
        return {
            "score": 0,
            "decision": "CONFIG INVALID",
            "errors": errors,
            "warnings": warnings,
        }

    required_sections = ["platform", "paths", "runtime", "queue", "modes", "quality_gates"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Eksik config bölümü: {section}")

    paths = config.get("paths", {})
    for key in ["base_dir", "py_dir", "state_dir", "report_dir"]:
        p = paths.get(key)
        if not p:
            errors.append(f"paths.{key} eksik.")
        elif not Path(p).exists():
            warnings.append(f"paths.{key} mevcut değil: {p}")

    runtime = config.get("runtime", {})
    if runtime.get("min_disk_gb", 0) < 10:
        warnings.append("min_disk_gb çok düşük görünüyor.")

    if runtime.get("default_timeout_seconds", 0) < 300:
        warnings.append("default_timeout_seconds düşük görünüyor.")

    worker_pool = config.get("queue", {}).get("default_worker_pool", [])
    if not worker_pool:
        warnings.append("Worker pool boş.")

    modes = config.get("modes", {})
    if modes.get("production") is True:
        warnings.append("production modu varsayılan açık görünüyor. Güvenlik için kapalı olmalı.")

    score = 100
    score -= min(60, len(errors) * 15)
    score -= min(30, len(warnings) * 3)
    score = max(0, score)

    if errors:
        decision = "CONFIG INVALID"
    elif warnings:
        decision = "CONFIG REVIEW"
    else:
        decision = "CONFIG READY"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
    }


def write_report(action, config, created):
    validation = validate_config(config)

    payload = {
        "module": "200 v2 Configuration Manager",
        "created_at": now_text(),
        "action": action,
        "config_file": str(CONFIG_FILE),
        "config_created_now": created,
        "disk_free_gb": disk_free_gb(),
        "config": config,
        "validation": validation,
    }

    json_path = STATE_DIR / f"200_v2_configuration_manager_state_{NOW}.json"
    txt_path = REPORT_DIR / f"200_v2_configuration_manager_raporu_{NOW}.txt"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("200 v2 CONFIGURATION MANAGER")
    lines.append("=" * 80)
    lines.append(f"Tarih             : {payload['created_at']}")
    lines.append(f"Action            : {action}")
    lines.append(f"Score             : {validation['score']} / 100")
    lines.append(f"Decision          : {validation['decision']}")
    lines.append(f"Config File       : {CONFIG_FILE}")
    lines.append(f"Created Now       : {created}")
    lines.append(f"Disk Free         : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("CONFIG SUMMARY")
    lines.append("-" * 80)
    if config:
        lines.append(f"Platform          : {config.get('platform', {}).get('name')}")
        lines.append(f"Version           : {config.get('platform', {}).get('version')}")
        lines.append(f"Environment       : {config.get('platform', {}).get('environment')}")
        lines.append(f"Default Worker    : {config.get('queue', {}).get('default_worker')}")
        lines.append(f"Worker Pool       : {config.get('queue', {}).get('default_worker_pool')}")
        lines.append(f"Safe Mode         : {config.get('runtime', {}).get('safe_mode_default')}")
        lines.append(f"Production Default: {config.get('modes', {}).get('production')}")
    else:
        lines.append("Config okunamadı.")
    lines.append("")
    lines.append("-" * 80)
    lines.append("ERRORS")
    lines.append("-" * 80)
    if validation["errors"]:
        for e in validation["errors"]:
            lines.append(f"- {e}")
    else:
        lines.append("Errors: 0")
    lines.append("")
    lines.append("-" * 80)
    lines.append("WARNINGS")
    lines.append("-" * 80)
    if validation["warnings"]:
        for w in validation["warnings"]:
            lines.append(f"- {w}")
    else:
        lines.append("Warnings: 0")
    lines.append("")
    lines.append("NOT:")
    lines.append("200 v2 production çalıştırmaz. Merkezi yapılandırma dosyası oluşturur/doğrular.")
    lines.append("")
    lines.append("Dosyalar:")
    lines.append(str(CONFIG_FILE))
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    return payload, json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--validate", action="store_true")
    return parser.parse_args()


def main():
    ensure_dirs()
    args = parse_args()

    created = False
    action = "status"

    if args.init:
        action = "init"
        config, created = init_config(force=args.force)
    else:
        config = read_config()
        if not config:
            config, created = init_config(force=False)
            action = "auto-init"
        elif args.validate:
            action = "validate"
        elif args.status:
            action = "status"

    payload, json_path, txt_path = write_report(action, config, created)
    validation = payload["validation"]

    print("=" * 80)
    print("200 v2 CONFIGURATION MANAGER TAMAMLANDI")
    print("=" * 80)
    print(f"Action    : {action}")
    print(f"Score     : {validation['score']} / 100")
    print(f"Decision  : {validation['decision']}")
    print(f"Errors    : {len(validation['errors'])}")
    print(f"Warnings  : {len(validation['warnings'])}")
    print(f"Config    : {CONFIG_FILE}")
    print("")
    print("Dosyalar:")
    print(CONFIG_FILE)
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
