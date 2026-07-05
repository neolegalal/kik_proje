# -*- coding: utf-8 -*-
import os
import sys
import glob
import json
import shutil
import subprocess
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
BATCH_DIR = os.path.join(BASE_DIR, "batch_planlari")
URETIM_INPUT_DIR = os.path.join(BASE_DIR, "uretim_input")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

os.makedirs(URETIM_INPUT_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

PYTHON_EXE = sys.executable

SCRIPT_158 = os.path.join(PY_DIR, "158_128_Production_JSONL_Runner.py")
SCRIPT_159V3 = os.path.join(PY_DIR, "159_v3_Production_Output_Final_Validator.py")
SCRIPT_160V3 = os.path.join(PY_DIR, "160_v3_Production_DB_Importer.py")
SCRIPT_146V4 = os.path.join(PY_DIR, "146_v4_Aktif_Kart_Final_Kalite_Raporu.py")
SCRIPT_151 = os.path.join(PY_DIR, "151_Aktif_Kart_RAG_Web_Export_Motoru.py")


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_batch_file(batch_no):
    pattern = os.path.join(BATCH_DIR, f"152_batch_*_{batch_no:04d}.jsonl")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def read_jsonl(path):
    rows = []
    errors = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                errors.append({"line_no": line_no, "error": str(e), "raw": line[:300]})
    return rows, errors


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def prepare_input(batch_file, batch_no, run_tag):
    rows, errors = read_jsonl(batch_file)
    if errors:
        raise RuntimeError(f"Batch JSONL hatası var: {len(errors)}")

    converted = []
    bad = []

    for i, r in enumerate(rows, 1):
        karar_no = str(r.get("karar_no", "")).strip()
        dosya_yolu = str(r.get("dosya_yolu", "")).strip()
        dosya_adi = str(r.get("dosya_adi") or os.path.basename(dosya_yolu)).strip()

        if not karar_no or not dosya_yolu or not os.path.exists(dosya_yolu):
            bad.append({"sira": i, "karar_no": karar_no, "dosya_yolu": dosya_yolu, "row": r})
            continue

        converted.append({
            "sira": len(converted) + 1,
            "karar_no": karar_no,
            "pdf_yolu": dosya_yolu,
            "dosya_yolu": dosya_yolu,
            "dosya_adi": dosya_adi,
            "batch_no": batch_no,
            "pilot_sira": i,
            "kaynak": "162_BATCH_PRODUCTION_RUNNER",
            "durum": "136E_HAZIR"
        })

    input_path = os.path.join(
        URETIM_INPUT_DIR,
        f"155C1_136E_pilot_input_BATCH_{batch_no:04d}_{run_tag}.jsonl"
    )
    bad_path = os.path.join(
        URETIM_INPUT_DIR,
        f"162_batch_{batch_no:04d}_input_hatalar_{run_tag}.jsonl"
    )

    write_jsonl(input_path, converted)
    write_jsonl(bad_path, bad)

    if bad:
        raise RuntimeError(f"Batch input içinde sorunlu kayıt var: {len(bad)} | {bad_path}")

    return input_path, bad_path, len(converted)


def run_step(name, cmd, run_tag, timeout=None):
    stdout_path = os.path.join(LOG_DIR, f"162_{run_tag}_{name}_stdout.txt")
    stderr_path = os.path.join(LOG_DIR, f"162_{run_tag}_{name}_stderr.txt")

    started = datetime.now()

    with open(stdout_path, "w", encoding="utf-8") as out, open(stderr_path, "w", encoding="utf-8") as err:
        p = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            stdout=out,
            stderr=err,
            text=True,
            timeout=timeout,
        )

    finished = datetime.now()

    return {
        "step": name,
        "cmd": cmd,
        "returncode": p.returncode,
        "ok": p.returncode == 0,
        "started": started.strftime("%Y-%m-%d %H:%M:%S"),
        "finished": finished.strftime("%Y-%m-%d %H:%M:%S"),
        "seconds": round((finished - started).total_seconds(), 2),
        "stdout": stdout_path,
        "stderr": stderr_path,
    }


def check_scripts():
    missing = []
    for p in [SCRIPT_158, SCRIPT_159V3, SCRIPT_160V3, SCRIPT_146V4, SCRIPT_151]:
        if not os.path.exists(p):
            missing.append(p)
    return missing


def main():
    print("=" * 80)
    print("162 - BATCH PRODUCTION RUNNER")
    print("=" * 80)

    if len(sys.argv) < 2:
        raise SystemExit('Kullanım: python ".py\\162_Batch_Production_Runner.py" 2')

    batch_no = int(sys.argv[1])
    run_tag = tag()

    missing = check_scripts()
    if missing:
        raise FileNotFoundError("Eksik script:\n" + "\n".join(missing))

    batch_file = find_batch_file(batch_no)
    if not batch_file:
        raise FileNotFoundError(f"Batch dosyası bulunamadı: {batch_no:04d}")

    print(f"Batch no     : {batch_no}")
    print(f"Batch dosyası: {batch_file}")

    input_path, bad_path, input_count = prepare_input(batch_file, batch_no, run_tag)

    print(f"Input hazır  : {input_count}")
    print(f"Input dosyası: {input_path}")

    steps = []

    # 158 en güncel 155C1_136E_pilot_input_*.jsonl dosyasını okuyordu.
    # Bu nedenle batch input dosyasını aynı isim deseniyle ürettik.
    steps_to_run = [
        ("158_openai_uretim", [PYTHON_EXE, SCRIPT_158, str(input_count)]),
        ("159v3_validator", [PYTHON_EXE, SCRIPT_159V3]),
        ("160v3_db_import", [PYTHON_EXE, SCRIPT_160V3]),
        ("146v4_final_quality", [PYTHON_EXE, SCRIPT_146V4]),
        ("151_export", [PYTHON_EXE, SCRIPT_151]),
    ]

    failed = False

    for name, cmd in steps_to_run:
        print(f"\nÇalışıyor: {name}")
        result = run_step(name, cmd, run_tag)
        steps.append(result)

        print(f"Durum: {'OK' if result['ok'] else 'HATA'} | Süre: {result['seconds']} sn")

        if not result["ok"]:
            failed = True
            break

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "batch_no": batch_no,
        "batch_file": batch_file,
        "input_path": input_path,
        "bad_path": bad_path,
        "input_count": input_count,
        "steps": steps,
        "success": not failed,
        "next_batch": batch_no + 1 if not failed else batch_no,
    }

    state_path = os.path.join(STATE_DIR, f"162_batch_production_runner_state_batch_{batch_no:04d}_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"162_batch_production_runner_raporu_batch_{batch_no:04d}_{run_tag}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("162 - BATCH PRODUCTION RUNNER RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih        : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Batch no     : {batch_no}\n")
        f.write(f"Batch dosyası: {batch_file}\n")
        f.write(f"Input dosyası: {input_path}\n")
        f.write(f"Input kayıt  : {input_count}\n")
        f.write(f"Başarı       : {'EVET' if not failed else 'HAYIR'}\n\n")

        f.write("ADIMLAR\n")
        f.write("-" * 80 + "\n")
        for s in steps:
            f.write(
                f"{s['step']} | {'OK' if s['ok'] else 'HATA'} | "
                f"return={s['returncode']} | süre={s['seconds']} sn\n"
            )
            f.write(f"  stdout: {s['stdout']}\n")
            f.write(f"  stderr: {s['stderr']}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON   : {state_path}\n")
        f.write(f"Rapor        : {rapor_path}\n")

    print("\n162 BATCH RUNNER TAMAMLANDI")
    print("-" * 80)
    print(f"Batch no : {batch_no}")
    print(f"Başarı   : {'EVET' if not failed else 'HAYIR'}")
    print(f"Sonraki  : {batch_no + 1 if not failed else batch_no}")
    print("\nDosyalar:")
    print(rapor_path)
    print(state_path)


if __name__ == "__main__":
    main()