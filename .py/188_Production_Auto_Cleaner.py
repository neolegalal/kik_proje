# -*- coding: utf-8 -*-
"""
188 - PRODUCTION AUTO CLEANER

171 yapısal kalite kontrolünü otomatik çalıştırır.
BLOCK varsa 187 Soft Block Cleaner'ı çalıştırır.
Temiz output üzerinde 171'i tekrar çalıştırır.
DB'ye yazmaz.

Kullanım:
  python ".py\\188_Production_Auto_Cleaner.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_x.jsonl"
"""

import os
import sys
import json
import glob
import time
import subprocess
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

SCRIPT_171 = os.path.join(PY_DIR, "171_v2_Mini_Uretim_Kalite_Kontrol_Motoru.py")
SCRIPT_187 = os.path.join(PY_DIR, "187_171_Soft_Block_Cleaner.py")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def read_json(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_text(path, text):
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)


def as_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def as_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def run_cmd(cmd, log_path):
    start = time.time()
    append_text(log_path, "\n" + "=" * 90 + "\n")
    append_text(log_path, f"COMMAND START: {now()}\n")
    append_text(log_path, " ".join(cmd) + "\n")
    append_text(log_path, "-" * 90 + "\n")

    proc = subprocess.run(
        cmd,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )

    elapsed = round(time.time() - start, 2)
    append_text(log_path, proc.stdout or "")
    if proc.stderr:
        append_text(log_path, "\nSTDERR:\n" + proc.stderr)
    append_text(log_path, f"\nCOMMAND END: {now()} | returncode={proc.returncode} | elapsed={elapsed}\n")

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "elapsed_seconds": elapsed,
    }


def latest_state(prefix):
    return read_json(latest_file(os.path.join(STATE_DIR, f"{prefix}*.json")))


def latest_log(prefix):
    return latest_file(os.path.join(LOG_DIR, f"{prefix}*.jsonl"))


def get_171_summary():
    s = latest_state("171_v2_mini_kalite_state_") or {}
    total = as_int(s.get("total_cards") or s.get("toplam_kart") or 0)
    ready = as_int(s.get("ready_cards") or s.get("ready_count") or 0)
    warning = as_int(s.get("warning_cards") or s.get("warning_count") or 0)
    block = as_int(s.get("block_cards") or s.get("block_count") or 0)
    avg = as_float(s.get("avg_score") or s.get("average_score") or 0)
    can_go = bool(s.get("ready_for_169") or s.get("can_go_169") or s.get("ready_for_next_step"))
    detail = latest_log("171_v2_mini_kalite_detay_")
    return {
        "total": total,
        "ready": ready,
        "warning": warning,
        "block": block,
        "avg": avg,
        "can_go_169": can_go,
        "detail_path": detail,
        "state": s,
    }


def get_187_summary():
    s = latest_state("187_soft_block_cleaner_state_") or {}
    out = s.get("output_path")
    return {
        "output_path": out,
        "removed_cards": as_int(s.get("removed_cards", 0)),
        "hard_block_count": as_int(s.get("hard_block_count", 0)),
        "ready_for_171_recheck": bool(s.get("ready_for_171_recheck")),
        "state": s,
    }


def main():
    print("=" * 80)
    print("188 - PRODUCTION AUTO CLEANER")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2 and os.path.exists(sys.argv[1]):
        input_output = sys.argv[1]
    else:
        input_output = latest_file(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"))

    if not input_output or not os.path.exists(input_output):
        raise FileNotFoundError("Input production output bulunamadı.")

    for p in [SCRIPT_171, SCRIPT_187]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Script bulunamadı: {p}")

    log_path = os.path.join(LOG_DIR, f"188_auto_cleaner_log_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"188_auto_cleaner_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"188_production_auto_cleaner_raporu_{run_tag}.txt")

    print(f"\nInput output : {input_output}")
    print("-" * 80)

    steps = []
    current_output = input_output
    cleaner_used = False

    print("\n[1] 171 ilk yapısal kalite kontrol")
    res171a = run_cmd(["python", SCRIPT_171, current_output], log_path)
    s171a = get_171_summary()
    ok_171a = res171a["returncode"] == 0 and s171a["block"] == 0
    steps.append({"step": "171_INITIAL", "ok": ok_171a, **s171a, "elapsed_seconds": res171a["elapsed_seconds"]})
    print(f"171 ilk sonuç: block={s171a['block']} warning={s171a['warning']} avg={s171a['avg']}")

    if s171a["block"] > 0:
        if not s171a["detail_path"] or not os.path.exists(s171a["detail_path"]):
            final_ok = False
            reason = "171 detay dosyası bulunamadı."
        else:
            print("\n[2] 187 soft block cleaner çalışıyor")
            cleaner_used = True
            res187 = run_cmd(["python", SCRIPT_187, current_output, s171a["detail_path"]], log_path)
            s187 = get_187_summary()
            ok187 = (
                res187["returncode"] == 0
                and s187["hard_block_count"] == 0
                and s187["output_path"]
                and os.path.exists(s187["output_path"])
            )
            steps.append({"step": "187_CLEANER", "ok": ok187, **s187, "elapsed_seconds": res187["elapsed_seconds"]})
            print(f"187 sonuç: ok={ok187} removed={s187['removed_cards']} hard={s187['hard_block_count']} output={s187['output_path']}")

            if not ok187:
                final_ok = False
                reason = "187 soft block cleaner başarısız."
            else:
                current_output = s187["output_path"]
                print("\n[3] 171 tekrar kontrol - temiz output")
                res171b = run_cmd(["python", SCRIPT_171, current_output], log_path)
                s171b = get_171_summary()
                ok_171b = res171b["returncode"] == 0 and s171b["block"] == 0
                steps.append({"step": "171_RECHECK", "ok": ok_171b, **s171b, "elapsed_seconds": res171b["elapsed_seconds"]})
                print(f"171 tekrar sonuç: ok={ok_171b} block={s171b['block']} warning={s171b['warning']} avg={s171b['avg']}")
                final_ok = ok_171b
                reason = "Temizlendi ve 171 tekrar geçti." if ok_171b else "187 sonrası 171 hâlâ BLOCK verdi."
    else:
        final_ok = ok_171a
        reason = "171 ilk kontrolde BLOCK yok."

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_output": input_output,
        "clean_output_path": current_output,
        "cleaner_used": cleaner_used,
        "steps": steps,
        "final_ok": final_ok,
        "ready_for_177": final_ok,
        "reason": reason,
        "log_path": log_path,
        "rapor_path": rapor_path,
        "recommended_177_command": f'python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "{current_output}"',
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("188 - PRODUCTION AUTO CLEANER RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input output                  : {input_output}\n")
        f.write(f"Clean output                  : {current_output}\n")
        f.write(f"Cleaner kullanıldı mı          : {'EVET' if cleaner_used else 'HAYIR'}\n")
        f.write(f"Final sonuç                   : {'PASS' if final_ok else 'FAIL'}\n")
        f.write(f"177'ye geçilebilir mi          : {'EVET' if final_ok else 'HAYIR'}\n")
        f.write(f"Neden                         : {reason}\n\n")
        f.write("ADIMLAR\n")
        f.write("-" * 80 + "\n")
        for st in steps:
            f.write(f"{st.get('step'):<20} | {'OK' if st.get('ok') else 'FAIL'} | block={st.get('block')} warning={st.get('warning')} avg={st.get('avg')} removed={st.get('removed_cards')} hard={st.get('hard_block_count')}\n")
        f.write("\nÖNERILEN KOMUT\n")
        f.write("-" * 80 + "\n")
        f.write(state["recommended_177_command"] + "\n")
        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Log                           : {log_path}\n")
        f.write(f"State                         : {state_path}\n")
        f.write(f"Rapor                         : {rapor_path}\n")

    print("\n188 AUTO CLEANER TAMAMLANDI")
    print("-" * 80)
    print(f"Cleaner kullanıldı mı          : {'EVET' if cleaner_used else 'HAYIR'}")
    print(f"Final sonuç                   : {'PASS' if final_ok else 'FAIL'}")
    print(f"Clean output                  : {current_output}")
    print(f"177'ye geçilebilir mi          : {'EVET' if final_ok else 'HAYIR'}")
    print("\nÖnerilen komut:")
    print(state["recommended_177_command"])
    print("\nDosyalar:")
    print(log_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
