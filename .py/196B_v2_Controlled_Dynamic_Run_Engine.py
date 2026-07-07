# -*- coding: utf-8 -*-
r"""
196B v2 - Controlled Dynamic Run Engine
NeoLegal Production Platform v2.0

Amaç:
- 196B v1 komut planından sonra kontrollü dinamik test yapmak.
- Production Controller veya fallback production scriptini tespit etmek.
- 20 batch aday komutunu kurmak.
- Varsayılan olarak DRY RUN çalışır; gerçek production çalıştırmak için --execute gerekir.
- Timeout, stdout/stderr yakalama, rapor/state üretimi sağlar.

Kullanım:
cd /d C:\Users\MSI\Desktop\kik_proje

Ön kontrol:
python ".py\196B_v2_Controlled_Dynamic_Run_Engine.py"

Gerçek kontrollü test:
python ".py\196B_v2_Controlled_Dynamic_Run_Engine.py" --execute --batch=20

Daha kısa test:
python ".py\196B_v2_Controlled_Dynamic_Run_Engine.py" --execute --batch=5
"""

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
REPORT_DIR = BASE_DIR / "raporlar"
STATE_DIR = BASE_DIR / "production_state"

NOW = datetime.now().strftime("%Y%m%d_%H%M%S")

DEFAULT_BATCH = 20
DEFAULT_TIMEOUT_SECONDS = 60 * 60  # 1 saat


def ensure_dirs():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def safe_read(path: Path, limit_chars=12000):
    for enc in ("utf-8", "utf-8-sig", "cp1254", "latin-1"):
        try:
            text = path.read_text(encoding=enc, errors="ignore")
            return text[:limit_chars]
        except Exception:
            pass
    return ""


def disk_free_gb():
    usage = shutil.disk_usage(str(BASE_DIR))
    return round(usage.free / (1024 ** 3), 2)


def find_script_by_prefix(prefix: str, exclude_tokens=None):
    exclude_tokens = exclude_tokens or []
    if not PY_DIR.exists():
        return None

    candidates = []
    candidates.extend(PY_DIR.glob(f"{prefix}*.py"))
    candidates.extend(PY_DIR.glob(f"*{prefix}*.py"))
    candidates = list(set(candidates))

    clean = []
    for p in candidates:
        name_upper = p.name.upper()
        if any(token.upper() in name_upper for token in exclude_tokens):
            continue
        clean.append(p)

    clean.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return clean[0] if clean else None


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
            "table": None,
            "cards_before": 0,
            "message": "KİK DB bulunamadı."
        }

    db_path = candidates[0]

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        tables = [x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

        table = None
        for t in ("hukuki_kartlar", "kararlar", "kik_kararlari", "cards", "legal_cards"):
            if t in tables:
                table = t
                break

        if not table and tables:
            table = tables[0]

        if not table:
            conn.close()
            return {
                "status": "FAIL",
                "path": str(db_path),
                "table": None,
                "cards_before": 0,
                "message": "DB var ancak tablo bulunamadı."
            }

        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()

        return {
            "status": "PASS" if count > 0 else "WARNING",
            "path": str(db_path),
            "table": table,
            "cards_before": count,
            "message": f"DB bulundu. Tablo={table}, kayıt={count}"
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "path": str(db_path),
            "table": None,
            "cards_before": 0,
            "message": f"DB okunamadı: {e}"
        }


def db_count(db_info):
    if not db_info.get("path") or not db_info.get("table"):
        return None

    try:
        conn = sqlite3.connect(db_info["path"])
        cur = conn.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM {db_info['table']}").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return None


def latest_file(folder: Path, pattern: str):
    if not folder.exists():
        return None
    files = list(folder.glob(pattern))
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def build_entrypoint():
    # Öncelik 181 Production Controller
    controller = find_script_by_prefix("181", exclude_tokens=["196B"])
    if controller:
        return {
            "mode": "controller",
            "script": str(controller),
            "reason": "181 Production Controller bulundu."
        }

    # Fallback 168 Production
    production = find_script_by_prefix("168", exclude_tokens=["196B"])
    if production:
        return {
            "mode": "fallback_168",
            "script": str(production),
            "reason": "181 bulunamadı; 168 Production fallback seçildi."
        }

    return {
        "mode": "none",
        "script": None,
        "reason": "181 veya 168 production script bulunamadı."
    }


def command_variants(script_path: str, batch: int):
    # Mevcut scriptlerin argüman formatı bilinmediği için en güvenli sırayla adaylar üretilir.
    # v2 yalnızca ilk adayı çalıştırır; başarısız olursa kullanıcı rapora göre yönlendirir.
    return [
        [sys.executable, script_path, f"--batch={batch}"],
        [sys.executable, script_path, str(batch)],
        [sys.executable, script_path],
    ]


def run_command(command, timeout_seconds):
    started = time.time()

    try:
        proc = subprocess.run(
            command,
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=timeout_seconds
        )

        elapsed = round(time.time() - started, 2)

        return {
            "executed": True,
            "timeout": False,
            "returncode": proc.returncode,
            "elapsed_seconds": elapsed,
            "stdout_tail": proc.stdout[-12000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-12000:] if proc.stderr else "",
            "status": "PASS" if proc.returncode == 0 else "FAIL"
        }

    except subprocess.TimeoutExpired as e:
        elapsed = round(time.time() - started, 2)
        return {
            "executed": True,
            "timeout": True,
            "returncode": None,
            "elapsed_seconds": elapsed,
            "stdout_tail": (e.stdout or "")[-12000:] if isinstance(e.stdout, str) else "",
            "stderr_tail": (e.stderr or "")[-12000:] if isinstance(e.stderr, str) else "",
            "status": "TIMEOUT"
        }

    except Exception as e:
        elapsed = round(time.time() - started, 2)
        return {
            "executed": True,
            "timeout": False,
            "returncode": None,
            "elapsed_seconds": elapsed,
            "stdout_tail": "",
            "stderr_tail": str(e),
            "status": "FAIL"
        }


def evaluate(payload):
    score = 100
    errors = []
    warnings = []

    if payload["disk_free_gb"] < 50:
        score -= 20
        errors.append("Disk alanı 50 GB altında.")

    if payload["db"]["status"] == "FAIL":
        score -= 25
        errors.append("DB bulunamadı veya okunamadı.")
    elif payload["db"]["status"] == "WARNING":
        score -= 5
        warnings.append("DB var ancak kayıt sayısı düşük.")

    if not payload["entrypoint"]["script"]:
        score -= 30
        errors.append("Production entrypoint bulunamadı.")

    if not payload["execute"]:
        score -= 10
        warnings.append("DRY RUN: Gerçek dynamic production çalıştırılmadı.")

    run = payload.get("run_result")
    if payload["execute"]:
        if not run:
            score -= 20
            errors.append("Execute istendi ancak run_result oluşmadı.")
        elif run["status"] == "PASS":
            pass
        elif run["status"] == "TIMEOUT":
            score -= 15
            errors.append("Dynamic run timeout oldu.")
        else:
            score -= 20
            errors.append("Dynamic run başarısız oldu.")

        after = payload.get("db_cards_after")
        before = payload["db"].get("cards_before")
        if after is not None and before is not None:
            delta = after - before
            payload["db_cards_delta"] = delta
            if delta < 0:
                score -= 20
                errors.append("DB kayıt sayısı azaldı.")
            elif delta == 0:
                warnings.append("DB kayıt sayısı değişmedi. Bu test sadece kontrol modunda çalışmış olabilir.")
            else:
                warnings.append(f"DB kayıt artışı tespit edildi: +{delta}")
        else:
            warnings.append("Run sonrası DB sayımı yapılamadı.")

    score = max(0, min(100, score))

    if errors:
        decision = "DYNAMIC NOT CERTIFIED"
    elif payload["execute"] and score >= 90:
        decision = "DYNAMIC CERTIFIED"
    elif payload["execute"] and score >= 75:
        decision = "DYNAMIC CONDITIONAL CERTIFIED"
    else:
        decision = "READY FOR CONTROLLED EXECUTE"

    return {
        "score": score,
        "decision": decision,
        "errors": errors,
        "warnings": warnings
    }


def write_report(payload):
    json_path = STATE_DIR / f"196B_v2_controlled_dynamic_state_{NOW}.json"
    txt_path = REPORT_DIR / f"196B_v2_controlled_dynamic_raporu_{NOW}.txt"

    payload["result"] = evaluate(payload)

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("=" * 80)
    lines.append("196B v2 CONTROLLED DYNAMIC RUN ENGINE")
    lines.append("=" * 80)
    lines.append(f"Tarih               : {payload['created_at']}")
    lines.append(f"Execute Mode        : {payload['execute']}")
    lines.append(f"Batch Size          : {payload['batch']}")
    lines.append(f"Timeout Seconds     : {payload['timeout_seconds']}")
    lines.append(f"Score               : {payload['result']['score']} / 100")
    lines.append(f"Decision            : {payload['result']['decision']}")
    lines.append(f"Disk Free           : {payload['disk_free_gb']} GB")
    lines.append("")
    lines.append("-" * 80)
    lines.append("DB")
    lines.append("-" * 80)
    lines.append(f"DB Status           : {payload['db']['status']}")
    lines.append(f"DB Path             : {payload['db'].get('path')}")
    lines.append(f"DB Table            : {payload['db'].get('table')}")
    lines.append(f"DB Cards Before     : {payload['db'].get('cards_before')}")
    lines.append(f"DB Cards After      : {payload.get('db_cards_after')}")
    lines.append(f"DB Cards Delta      : {payload.get('db_cards_delta')}")
    lines.append(f"DB Message          : {payload['db'].get('message')}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("ENTRYPOINT")
    lines.append("-" * 80)
    lines.append(f"Mode                : {payload['entrypoint']['mode']}")
    lines.append(f"Script              : {payload['entrypoint']['script']}")
    lines.append(f"Reason              : {payload['entrypoint']['reason']}")
    lines.append("")
    lines.append("-" * 80)
    lines.append("COMMAND")
    lines.append("-" * 80)
    lines.append(" ".join(payload["selected_command"]) if payload.get("selected_command") else "Komut yok.")
    lines.append("")
    lines.append("-" * 80)
    lines.append("RUN RESULT")
    lines.append("-" * 80)
    rr = payload.get("run_result")
    if rr:
        lines.append(f"Executed            : {rr.get('executed')}")
        lines.append(f"Status              : {rr.get('status')}")
        lines.append(f"Return Code         : {rr.get('returncode')}")
        lines.append(f"Timeout             : {rr.get('timeout')}")
        lines.append(f"Elapsed Seconds     : {rr.get('elapsed_seconds')}")
        lines.append("")
        lines.append("STDOUT TAIL:")
        lines.append(rr.get("stdout_tail") or "")
        lines.append("")
        lines.append("STDERR TAIL:")
        lines.append(rr.get("stderr_tail") or "")
    else:
        lines.append("DRY RUN: komut çalıştırılmadı.")
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
    lines.append("Dosyalar:")
    lines.append(str(json_path))
    lines.append(str(txt_path))

    txt_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, txt_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Gerçek controlled dynamic run çalıştırır.")
    parser.add_argument("--batch", type=int, default=DEFAULT_BATCH, help="Test batch sayısı.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="Saniye cinsinden timeout.")
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_dirs()

    db = discover_db()
    entrypoint = build_entrypoint()

    selected_command = None
    variants = []
    run_result = None
    db_after = None

    if entrypoint["script"]:
        variants = command_variants(entrypoint["script"], args.batch)
        selected_command = variants[0]

    payload = {
        "module": "196B v2 Controlled Dynamic Run Engine",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": str(BASE_DIR),
        "execute": bool(args.execute),
        "batch": args.batch,
        "timeout_seconds": args.timeout,
        "disk_free_gb": disk_free_gb(),
        "db": db,
        "entrypoint": entrypoint,
        "command_variants": variants,
        "selected_command": selected_command,
        "run_result": None,
        "db_cards_after": None,
        "db_cards_delta": None,
    }

    if args.execute and selected_command:
        run_result = run_command(selected_command, args.timeout)
        db_after = db_count(db)
        payload["run_result"] = run_result
        payload["db_cards_after"] = db_after

    json_path, txt_path = write_report(payload)
    result = payload["result"]

    print("=" * 80)
    print("196B v2 CONTROLLED DYNAMIC RUN ENGINE TAMAMLANDI")
    print("=" * 80)
    print(f"Execute Mode    : {payload['execute']}")
    print(f"Batch Size      : {payload['batch']}")
    print(f"Score           : {result['score']} / 100")
    print(f"Decision        : {result['decision']}")
    print(f"Errors          : {len(result['errors'])}")
    print(f"Warnings        : {len(result['warnings'])}")
    print(f"DB Status       : {db['status']}")
    print(f"DB Cards Before : {db.get('cards_before')}")
    print(f"DB Cards After  : {payload.get('db_cards_after')}")
    print(f"Entrypoint      : {entrypoint.get('script')}")
    print("")
    print("Dosyalar:")
    print(json_path)
    print(txt_path)


if __name__ == "__main__":
    main()
