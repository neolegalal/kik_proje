# -*- coding: utf-8 -*-
from config import BASE_DIR, STATE_DIR, REPORT_DIR, CONFIG_DIR, PLATFORM_CONFIG_FILE, MIN_DISK_GB
from utils import now_stamp, now_text, ensure_dirs, disk_free_gb, safe_json, write_json

DEFAULT_CONFIG = {
    "platform": {
        "name": "NeoLegal Production Platform",
        "version": "2.0",
        "environment": "local",
        "default_entrypoint": "200_Platform",
    },
    "paths": {
        "base_dir": str(BASE_DIR),
        "state_dir": str(STATE_DIR),
        "report_dir": str(REPORT_DIR),
        "config_dir": str(CONFIG_DIR),
    },
    "runtime": {
        "min_disk_gb": MIN_DISK_GB,
        "default_timeout_seconds": 3600,
        "safe_mode_default": True,
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
        "require_no_failed_jobs": True,
    },
}

def load_or_create(force=False):
    ensure_dirs(STATE_DIR, REPORT_DIR, CONFIG_DIR)
    if PLATFORM_CONFIG_FILE.exists() and not force:
        data = safe_json(PLATFORM_CONFIG_FILE)
        if data:
            return data, False
    config = dict(DEFAULT_CONFIG)
    config["created_at"] = now_text()
    config["updated_at"] = now_text()
    write_json(PLATFORM_CONFIG_FILE, config)
    return config, True

def validate(config):
    errors = []
    warnings = []
    if not config:
        errors.append("Config yok veya okunamadı.")
    else:
        for section in ["platform", "paths", "runtime", "modes", "quality_gates"]:
            if section not in config:
                errors.append(f"Eksik bölüm: {section}")
        if config.get("modes", {}).get("production") is True:
            warnings.append("Production modu varsayılan açık. Güvenlik için kapalı olmalı.")
    score = 100 - min(60, len(errors) * 15) - min(30, len(warnings) * 3)
    score = max(0, score)
    decision = "CONFIG INVALID" if errors else ("CONFIG REVIEW" if warnings else "CONFIG READY")
    return {"score": score, "decision": decision, "errors": errors, "warnings": warnings}

def run(force=False):
    ts = now_stamp()
    config, created = load_or_create(force=force)
    result = validate(config)
    state = STATE_DIR / f"200_pkg_config_state_{ts}.json"
    report = REPORT_DIR / f"200_pkg_config_raporu_{ts}.txt"
    payload = {"module": "200 Package Config Manager", "created_at": now_text(), "config_created": created, "config_file": str(PLATFORM_CONFIG_FILE), "config": config, "result": result}
    write_json(state, payload)
    report.write_text("\n".join([
        "="*80,
        "200 PACKAGE - CONFIG MANAGER",
        "="*80,
        f"Score    : {result['score']} / 100",
        f"Decision : {result['decision']}",
        f"Created  : {created}",
        f"Config   : {PLATFORM_CONFIG_FILE}",
        "",
        "Dosyalar:",
        str(PLATFORM_CONFIG_FILE),
        str(state),
        str(report),
    ]), encoding="utf-8")
    return {"config": config, "result": result, "paths": {"config": str(PLATFORM_CONFIG_FILE), "state": str(state), "report": str(report)}}
