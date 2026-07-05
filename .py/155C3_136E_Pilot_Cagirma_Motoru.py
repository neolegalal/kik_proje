# -*- coding: utf-8 -*-
"""
155C3 - 136E PİLOT ÇAĞIRMA MOTORU

Güvenli amaç:
- En güncel 155C1 136E input dosyasını bulur.
- İlk 5 kayıttan mini pilot input üretir.
- 136E motorunun dışarıdan input/limit almayı destekleyip desteklemediğini kontrol eder.
- Destek varsa 136E'yi 5 kayıtla çağırır.
- Destek yoksa 136E'yi çalıştırmaz; adaptasyon gerektiğini raporlar.
- DB'ye yazmaz.
"""

import os
import sys
import glob
import json
import subprocess
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
URETIM_INPUT_DIR = os.path.join(BASE_DIR, "uretim_input")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

SCRIPT_136E = os.path.join(PY_DIR, "136E_Batch_Guvenli_Sadeleme_Motoru.py")
INPUT_PATTERN = os.path.join(URETIM_INPUT_DIR, "155C1_136E_pilot_input_*.jsonl")

DEFAULT_LIMIT = 5
CALL_TIMEOUT_SECONDS = 60 * 30

os.makedirs(URETIM_INPUT_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def read_jsonl(path):
    rows = []
    if not path or not os.path.exists(path):
        return rows

    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                rows.append({
                    "_json_error": str(e),
                    "_line_no": line_no,
                    "_raw": line[:500],
                })
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def get_limit():
    if len(sys.argv) >= 2:
        try:
            n = int(sys.argv[1])
            if n <= 0:
                return DEFAULT_LIMIT
            return n
        except Exception:
            return DEFAULT_LIMIT
    return DEFAULT_LIMIT


def inspect_136e_support():
    """
    136E'nin parametreli/çevresel değişkenli çalışmaya hazır olup olmadığını kontrol eder.
    Bu güvenlik için gerekli: destek yoksa körlemesine çalıştırmıyoruz.
    """
    result = {
        "script_exists": os.path.exists(SCRIPT_136E),
        "supports_sys_argv": False,
        "supports_env_input": False,
        "supports_limit": False,
        "safe_to_call": False,
        "signals": [],
    }

    if not result["script_exists"]:
        return result

    try:
        with open(SCRIPT_136E, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
    except Exception as e:
        result["signals"].append(f"OKUNAMADI: {e}")
        return result

    if "sys.argv" in code:
        result["supports_sys_argv"] = True
        result["signals"].append("sys.argv bulundu")

    env_markers = [
        "KIK_136E_INPUT_JSONL",
        "KIK_INPUT_JSONL",
        "INPUT_JSONL",
        "PILOT_INPUT",
    ]
    for m in env_markers:
        if m in code:
            result["supports_env_input"] = True
            result["signals"].append(f"env/input marker bulundu: {m}")

    limit_markers = [
        "KIK_136E_LIMIT",
        "LIMIT",
        "limit",
        "--limit",
    ]
    for m in limit_markers:
        if m in code:
            result["supports_limit"] = True
            result["signals"].append(f"limit marker bulundu: {m}")

    # En güvenli koşul: hem dış input hem limit desteği görülmeli.
    result["safe_to_call"] = (
        result["script_exists"]
        and (result["supports_sys_argv"] or result["supports_env_input"])
        and result["supports_limit"]
    )

    return result


def main():
    print("=" * 80)
    print("155C3 - 136E PİLOT ÇAĞIRMA MOTORU")
    print("=" * 80)

    run_tag = tag()
    limit = get_limit()

    input_path = latest_file(INPUT_PATTERN)
    if not input_path:
        raise FileNotFoundError("155C1 136E pilot input JSONL bulunamadı.")

    rows = read_jsonl(input_path)
    clean_rows = [r for r in rows if "_json_error" not in r]

    mini_rows = clean_rows[:limit]

    mini_input_path = os.path.join(
        URETIM_INPUT_DIR,
        f"155C3_136E_mini_pilot_input_{limit}_{run_tag}.jsonl"
    )
    write_jsonl(mini_input_path, mini_rows)

    support = inspect_136e_support()

    stdout_path = os.path.join(LOG_DIR, f"155C3_136E_stdout_{run_tag}.txt")
    stderr_path = os.path.join(LOG_DIR, f"155C3_136E_stderr_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"155C3_136E_pilot_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"155C3_136E_pilot_cagirma_raporu_{run_tag}.txt")

    command = [
        sys.executable,
        SCRIPT_136E,
        mini_input_path,
        str(limit),
    ]

    called = False
    returncode = None
    call_status = "CAGRILMADI"
    error_message = ""

    if support["safe_to_call"]:
        called = True
        env = os.environ.copy()
        env["KIK_136E_INPUT_JSONL"] = mini_input_path
        env["KIK_136E_LIMIT"] = str(limit)
        env["KIK_136E_MODE"] = "PILOT"
        env["KIK_136E_DB_WRITE"] = "FALSE"

        try:
            with open(stdout_path, "w", encoding="utf-8") as out, open(stderr_path, "w", encoding="utf-8") as err:
                p = subprocess.run(
                    command,
                    cwd=BASE_DIR,
                    env=env,
                    stdout=out,
                    stderr=err,
                    text=True,
                    timeout=CALL_TIMEOUT_SECONDS,
                )
                returncode = p.returncode
                call_status = "OK" if p.returncode == 0 else "HATA"
        except subprocess.TimeoutExpired:
            call_status = "TIMEOUT"
            error_message = f"136E çağrısı timeout oldu: {CALL_TIMEOUT_SECONDS} saniye"
        except Exception as e:
            call_status = "HATA"
            error_message = str(e)
    else:
        error_message = (
            "136E güvenli dış input/limit desteği kesin tespit edilemediği için çağrılmadı. "
            "Önce 136E'ye parametre/env input desteği eklenmeli."
        )

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "mini_input_path": mini_input_path,
        "limit": limit,
        "script_136E": SCRIPT_136E,
        "support": support,
        "command": command,
        "called": called,
        "returncode": returncode,
        "call_status": call_status,
        "error_message": error_message,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "db_written": False,
        "next_step": "136E_ADAPTASYON_GEREKLI" if not support["safe_to_call"] else "136E_CIKTI_KONTROL",
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("155C3 - 136E PİLOT ÇAĞIRMA RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                 : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input JSONL            : {input_path}\n")
        f.write(f"Mini input             : {mini_input_path}\n")
        f.write(f"Limit                  : {limit}\n")
        f.write(f"136E script             : {SCRIPT_136E}\n")
        f.write(f"136E var                : {'EVET' if support['script_exists'] else 'HAYIR'}\n")
        f.write(f"sys.argv desteği        : {'EVET' if support['supports_sys_argv'] else 'HAYIR'}\n")
        f.write(f"env input desteği       : {'EVET' if support['supports_env_input'] else 'HAYIR'}\n")
        f.write(f"limit desteği           : {'EVET' if support['supports_limit'] else 'HAYIR'}\n")
        f.write(f"Güvenli çağrı           : {'EVET' if support['safe_to_call'] else 'HAYIR'}\n")
        f.write(f"136E çağrıldı           : {'EVET' if called else 'HAYIR'}\n")
        f.write(f"Çağrı durumu            : {call_status}\n")
        f.write(f"Return code             : {returncode}\n")
        f.write(f"DB yaz                  : HAYIR\n")
        f.write(f"Hata mesajı             : {error_message}\n\n")

        f.write("DESTEK SİNYALLERİ\n")
        f.write("-" * 80 + "\n")
        if support["signals"]:
            for s in support["signals"]:
                f.write(f"- {s}\n")
        else:
            f.write("Destek sinyali bulunamadı.\n")

        f.write("\nKOMUT\n")
        f.write("-" * 80 + "\n")
        f.write(" ".join(command) + "\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"STDOUT                 : {stdout_path}\n")
        f.write(f"STDERR                 : {stderr_path}\n")
        f.write(f"STATE                  : {state_path}\n")
        f.write(f"RAPOR                  : {rapor_path}\n")

    print("\n136E PİLOT ÇAĞIRMA KONTROLÜ TAMAMLANDI")
    print("-" * 80)
    print(f"Mini input       : {mini_input_path}")
    print(f"Limit            : {limit}")
    print(f"136E var          : {'EVET' if support['script_exists'] else 'HAYIR'}")
    print(f"Güvenli çağrı     : {'EVET' if support['safe_to_call'] else 'HAYIR'}")
    print(f"136E çağrıldı     : {'EVET' if called else 'HAYIR'}")
    print(f"Çağrı durumu      : {call_status}")
    print(f"Return code       : {returncode}")
    print(f"Hata              : {error_message}")

    print("\nDosyalar:")
    print(rapor_path)
    print(state_path)
    print(stdout_path)
    print(stderr_path)

    print("\nNOT: DB'ye yazılmadı.")


if __name__ == "__main__":
    main()