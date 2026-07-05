# -*- coding: utf-8 -*-
"""
163 - MASTER PRODUCTION CONTROLLER v2

Amaç:
- Büyük üretim için tek komutlu kontrollü batch zinciri çalıştırır.
- Yeni kalite mimarisine göre çalışır:
  168 v2  -> üretim
  171 v2  -> kural tabanlı kalite kontrol
  172     -> AI kalite hakemi, opsiyonel / mini örneklem
  169     -> DB import
  170     -> Web/RAG export
  173 v2  -> master acceptance

Kullanım:
  python ".py\\163_Master_Production_Controller.py" 10

Örnek:
  python ".py\\163_Master_Production_Controller.py" 5
  python ".py\\163_Master_Production_Controller.py" 20
  python ".py\\163_Master_Production_Controller.py" 50 --skip-ai-judge

Not:
- API maliyeti oluşur.
- 172 AI kalite hakemi varsayılan olarak sadece küçük/orta testlerde önerilir.
- Büyük seri üretimde --skip-ai-judge kullanılabilir; 171 v2 yine çalışır.
"""

import os
import sys
import json
import glob
import time
import shutil
import subprocess
from datetime import datetime


# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")

STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")

SCRIPT_168 = os.path.join(PY_DIR, "168_v2_Production_Format_Revizyonu_Runner.py")
SCRIPT_171 = os.path.join(PY_DIR, "171_v2_Mini_Uretim_Kalite_Kontrol_Motoru.py")
SCRIPT_172 = os.path.join(PY_DIR, "172_AI_Kalite_Hakemi.py")
SCRIPT_169 = os.path.join(PY_DIR, "169_Production_DB_Importer_Revizyonu.py")
SCRIPT_170 = os.path.join(PY_DIR, "170_RAG_Web_Export_Motoru_Revizyonu.py")
SCRIPT_173 = os.path.join(PY_DIR, "173_v2_Master_Acceptance_Test.py")

os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


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


def get_limit_and_flags():
    limit = 5
    skip_ai_judge = False
    stop_after_production = False
    dry_run = False

    args = sys.argv[1:]
    for a in args:
        if a == "--skip-ai-judge":
            skip_ai_judge = True
        elif a == "--stop-after-production":
            stop_after_production = True
        elif a == "--dry-run":
            dry_run = True
        else:
            try:
                limit = int(a)
            except Exception:
                pass

    if limit <= 0:
        limit = 5

    return limit, skip_ai_judge, stop_after_production, dry_run


def check_script(path):
    return os.path.exists(path)


def run_cmd(cmd, log_path):
    started = time.time()

    append_text(log_path, "\n" + "=" * 80 + "\n")
    append_text(log_path, f"COMMAND START: {now()}\n")
    append_text(log_path, " ".join([str(x) for x in cmd]) + "\n")
    append_text(log_path, "-" * 80 + "\n")

    proc = subprocess.run(
        cmd,
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        shell=False
    )

    elapsed = round(time.time() - started, 2)

    append_text(log_path, proc.stdout or "")
    if proc.stderr:
        append_text(log_path, "\nSTDERR:\n")
        append_text(log_path, proc.stderr)
    append_text(log_path, f"\nCOMMAND END: {now()} | returncode={proc.returncode} | elapsed={elapsed}\n")

    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "elapsed_seconds": elapsed,
    }


def find_latest_168_output_before_after(before_time):
    files = glob.glob(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"))
    files = [f for f in files if os.path.getmtime(f) >= before_time]
    if not files:
        return latest_file(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"))
    return max(files, key=os.path.getmtime)


def state_ok_168():
    s = read_json(latest_file(os.path.join(STATE_DIR, "168_production_runner_state_*.json")))
    if not s:
        return False, "168 state yok"
    ok = bool(s.get("ready_for_next_step")) and int(s.get("ok_count", 0)) > 0 and int(s.get("error_count", 0)) == 0
    return ok, f"ok={s.get('ok_count')} error={s.get('error_count')} cards={s.get('total_cards')}"


def state_ok_171():
    s = read_json(latest_file(os.path.join(STATE_DIR, "171_v2_mini_kalite_state_*.json")))
    if not s:
        return False, "171 state yok"

    # 171 v2 alanları farklı olabilir; esnek oku
    ready = bool(s.get("can_go_169", s.get("ready_for_169", s.get("ready_for_next_step", False))))
    block = int(s.get("block_cards", s.get("block_count", 0)) or 0)
    score = float(s.get("avg_score", s.get("average_score", 0)) or 0)

    ok = ready or (block == 0 and score >= 90)
    return ok, f"ready={ready} block={block} score={score}"


def state_ok_172():
    s = read_json(latest_file(os.path.join(STATE_DIR, "172_ai_kalite_hakemi_state_*.json")))
    if not s:
        return False, "172 state yok"
    ok = bool(s.get("ready_for_173")) and int(s.get("fail_count", 0)) == 0
    return ok, f"ready_for_173={s.get('ready_for_173')} fail={s.get('fail_count')} avg={s.get('average_score')}"


def state_ok_169():
    s = read_json(latest_file(os.path.join(STATE_DIR, "169_db_importer_state_*.json")))
    if not s:
        return False, "169 state yok"
    ready = bool(s.get("ready_for_next_step", s.get("ready_for_170", False)))
    err = int(s.get("error_count", s.get("hata", 0)) or 0)
    ok = ready and err == 0
    return ok, f"ready={ready} error={err}"


def state_ok_170():
    s = read_json(latest_file(os.path.join(STATE_DIR, "170_export_state_*.json")))
    if not s:
        return False, "170 state yok"
    exported = int(s.get("active_rows_exported", 0) or 0)
    web = s.get("web_jsonl")
    rag = s.get("rag_jsonl")
    ok = exported > 0 and web and os.path.exists(web) and rag and os.path.exists(rag)
    return ok, f"exported={exported} web={web} rag={rag}"


def state_ok_173():
    s = read_json(latest_file(os.path.join(STATE_DIR, "173_v2_master_acceptance_state_*.json")))
    if not s:
        return False, "173 state yok"
    ok = bool(s.get("master_ready_for_large_production"))
    return ok, f"ready={s.get('master_ready_for_large_production')} score={s.get('score')} blocks={s.get('block_count')}"


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("163 - MASTER PRODUCTION CONTROLLER v2")
    print("=" * 80)

    run_tag = tag()
    limit, skip_ai_judge, stop_after_production, dry_run = get_limit_and_flags()

    log_path = os.path.join(LOG_DIR, f"163_master_controller_log_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"163_master_controller_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"163_master_controller_raporu_{run_tag}.txt")

    required_scripts = [
        SCRIPT_168, SCRIPT_171, SCRIPT_169, SCRIPT_170, SCRIPT_173
    ]
    if not skip_ai_judge:
        required_scripts.append(SCRIPT_172)

    missing_scripts = [p for p in required_scripts if not check_script(p)]

    print(f"\nLimit          : {limit}")
    print(f"AI hakem       : {'KAPALI' if skip_ai_judge else 'AÇIK'}")
    print(f"Dry run        : {'EVET' if dry_run else 'HAYIR'}")
    print("-" * 80)

    if missing_scripts:
        print("\nEksik scriptler:")
        for p in missing_scripts:
            print(p)
        raise FileNotFoundError("Eksik script var. Önce dosyaları .py klasörüne koy.")

    if dry_run:
        print("\nDRY RUN: Komutlar çalıştırılmadı.")
        commands = [
            ["python", SCRIPT_168, str(limit)],
            ["python", SCRIPT_171],
            ["python", SCRIPT_172, "<168_output_jsonl>"] if not skip_ai_judge else None,
            ["python", SCRIPT_169, "<168_output_jsonl>"],
            ["python", SCRIPT_170],
            ["python", SCRIPT_173],
        ]
        commands = [c for c in commands if c]
        for c in commands:
            print(" ".join(c))
        return

    steps = []
    overall_ok = True
    before_168_time = time.time()

    # -------------------------------------------------------------------------
    # 168 üretim
    # -------------------------------------------------------------------------
    print("\n[1/6] 168 v2 üretim çalışıyor...")
    res = run_cmd(["python", SCRIPT_168, str(limit)], log_path)
    ok, detail = state_ok_168()
    steps.append({"step": "168", "returncode": res["returncode"], "ok": ok and res["returncode"] == 0, "detail": detail})
    print(f"168 sonucu: {'OK' if steps[-1]['ok'] else 'FAIL'} | {detail}")

    if not steps[-1]["ok"]:
        overall_ok = False

    output_168 = find_latest_168_output_before_after(before_168_time)
    if not output_168 or not os.path.exists(output_168):
        overall_ok = False
        steps.append({"step": "168_OUTPUT", "ok": False, "detail": "168 output bulunamadı"})
        print("168 output bulunamadı.")

    if stop_after_production or not overall_ok:
        print("\nİşlem üretim sonrası veya hata nedeniyle durdu.")
    else:
        # ---------------------------------------------------------------------
        # 171 kalite
        # ---------------------------------------------------------------------
        print("\n[2/6] 171 v2 kural tabanlı kalite kontrol çalışıyor...")
        res = run_cmd(["python", SCRIPT_171, output_168], log_path)
        ok, detail = state_ok_171()
        steps.append({"step": "171", "returncode": res["returncode"], "ok": ok and res["returncode"] == 0, "detail": detail})
        print(f"171 sonucu: {'OK' if steps[-1]['ok'] else 'FAIL'} | {detail}")

        if not steps[-1]["ok"]:
            overall_ok = False

        # ---------------------------------------------------------------------
        # 172 AI hakem
        # ---------------------------------------------------------------------
        if overall_ok and not skip_ai_judge:
            print("\n[3/6] 172 AI kalite hakemi çalışıyor...")
            res = run_cmd(["python", SCRIPT_172, output_168], log_path)
            ok, detail = state_ok_172()
            steps.append({"step": "172", "returncode": res["returncode"], "ok": ok and res["returncode"] == 0, "detail": detail})
            print(f"172 sonucu: {'OK' if steps[-1]['ok'] else 'FAIL'} | {detail}")

            if not steps[-1]["ok"]:
                overall_ok = False
        elif skip_ai_judge:
            steps.append({"step": "172", "ok": True, "detail": "AI hakem atlandı (--skip-ai-judge)"})
            print("\n[3/6] 172 AI kalite hakemi atlandı.")

        # ---------------------------------------------------------------------
        # 169 DB import
        # ---------------------------------------------------------------------
        if overall_ok:
            print("\n[4/6] 169 DB import çalışıyor...")
            res = run_cmd(["python", SCRIPT_169, output_168], log_path)
            ok, detail = state_ok_169()
            steps.append({"step": "169", "returncode": res["returncode"], "ok": ok and res["returncode"] == 0, "detail": detail})
            print(f"169 sonucu: {'OK' if steps[-1]['ok'] else 'FAIL'} | {detail}")

            if not steps[-1]["ok"]:
                overall_ok = False

        # ---------------------------------------------------------------------
        # 170 export
        # ---------------------------------------------------------------------
        if overall_ok:
            print("\n[5/6] 170 export çalışıyor...")
            res = run_cmd(["python", SCRIPT_170], log_path)
            ok, detail = state_ok_170()
            steps.append({"step": "170", "returncode": res["returncode"], "ok": ok and res["returncode"] == 0, "detail": detail})
            print(f"170 sonucu: {'OK' if steps[-1]['ok'] else 'FAIL'} | {detail}")

            if not steps[-1]["ok"]:
                overall_ok = False

        # ---------------------------------------------------------------------
        # 173 master acceptance
        # ---------------------------------------------------------------------
        if overall_ok:
            print("\n[6/6] 173 v2 master acceptance çalışıyor...")
            res = run_cmd(["python", SCRIPT_173], log_path)
            ok, detail = state_ok_173()
            steps.append({"step": "173", "returncode": res["returncode"], "ok": ok and res["returncode"] == 0, "detail": detail})
            print(f"173 sonucu: {'OK' if steps[-1]['ok'] else 'FAIL'} | {detail}")

            if not steps[-1]["ok"]:
                overall_ok = False

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "limit": limit,
        "skip_ai_judge": skip_ai_judge,
        "stop_after_production": stop_after_production,
        "output_168": output_168,
        "overall_ok": overall_ok,
        "steps": steps,
        "log_path": log_path,
        "rapor_path": rapor_path,
        "next_recommendation": "Batch limit artırılarak kontrollü üretime devam edilebilir." if overall_ok else "Hatalı adım rapordan incelenmeli.",
    }

    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("163 - MASTER PRODUCTION CONTROLLER v2 RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                 : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Limit                 : {limit}\n")
        f.write(f"AI hakem              : {'KAPALI' if skip_ai_judge else 'AÇIK'}\n")
        f.write(f"168 output            : {output_168}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Master zincir başarılı : {'EVET' if overall_ok else 'HAYIR'}\n")
        f.write(f"Öneri                  : {state['next_recommendation']}\n\n")

        f.write("ADIMLAR\n")
        f.write("-" * 80 + "\n")
        for st in steps:
            f.write(f"{st.get('step'):<10} | {'OK' if st.get('ok') else 'FAIL'} | {st.get('detail')}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Log                    : {log_path}\n")
        f.write(f"State                  : {state_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\n163 MASTER CONTROLLER TAMAMLANDI")
    print("-" * 80)
    print(f"Master zincir başarılı : {'EVET' if overall_ok else 'HAYIR'}")
    print(f"168 output             : {output_168}")
    print(f"Öneri                  : {state['next_recommendation']}")

    print("\nDosyalar:")
    print(log_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
