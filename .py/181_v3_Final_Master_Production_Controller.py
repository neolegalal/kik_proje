# -*- coding: utf-8 -*-
"""
181 v3 - FINAL MASTER PRODUCTION CONTROLLER

v3 farkı:
- 180 v2 karmaşıklık analizi artık BLOCK değil, planlama uyarısıdır.
- 180 sonucunda error=0, fail=0, too_few=0 ise OK kabul edilir.
- Planlama puanı düşükse rapora WARNING olarak yazılır ama büyük üretimi durdurmaz.
- 173 v2 yine non-blocking final acceptance olarak raporlanır.
"""

import os
import sys
import glob
import json
import time
import subprocess
from datetime import datetime


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")

URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)

SCRIPTS = {
    "168": os.path.join(PY_DIR, "168_v2_Production_Format_Revizyonu_Runner.py"),
    "171": os.path.join(PY_DIR, "171_v2_Mini_Uretim_Kalite_Kontrol_Motoru.py"),
    "172": os.path.join(PY_DIR, "172_AI_Kalite_Hakemi.py"),
    "175": os.path.join(PY_DIR, "175_v2_AI_Hukuki_Mesele_Kapsam_Analiz_Motoru.py"),
    "176": os.path.join(PY_DIR, "176_Hukuki_Mesele_Onceliklendirme_Motoru.py"),
    "177": os.path.join(PY_DIR, "177_Hukuki_Dogruluk_Hakemi.py"),
    "178": os.path.join(PY_DIR, "178_Akilli_Kart_Birlestirme_Hakemi.py"),
    "179": os.path.join(PY_DIR, "179_Kart_Optimizasyon_Motoru.py"),
    "180": os.path.join(PY_DIR, "180_v2_Karar_Karmasiklik_Analiz_Motoru.py"),
    "169": os.path.join(PY_DIR, "169_Production_DB_Importer_Revizyonu.py"),
    "170": os.path.join(PY_DIR, "170_RAG_Web_Export_Motoru_Revizyonu.py"),
    "173": os.path.join(PY_DIR, "173_v2_Master_Acceptance_Test.py"),
}


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


def get_any(d, keys, default=None):
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d:
            return d.get(k)
    return default


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


def parse_args():
    limit = 5
    flags = {
        "skip_172": False,
        "skip_175": False,
        "skip_176": False,
        "skip_177": False,
        "skip_178": False,
        "skip_180": False,
        "skip_173": False,
        "dry_run": False,
    }

    for a in sys.argv[1:]:
        if a == "--skip-172":
            flags["skip_172"] = True
        elif a == "--skip-175":
            flags["skip_175"] = True
        elif a == "--skip-176":
            flags["skip_176"] = True
        elif a == "--skip-177":
            flags["skip_177"] = True
        elif a == "--skip-178":
            flags["skip_178"] = True
        elif a == "--skip-180":
            flags["skip_180"] = True
        elif a == "--skip-173":
            flags["skip_173"] = True
        elif a == "--dry-run":
            flags["dry_run"] = True
        else:
            try:
                limit = int(a)
            except Exception:
                pass

    if flags["skip_175"]:
        flags["skip_176"] = True

    return max(1, limit), flags


def run_cmd(cmd, log_path):
    start = time.time()
    append_text(log_path, "\n" + "=" * 80 + "\n")
    append_text(log_path, f"COMMAND START: {now()}\n")
    append_text(log_path, " ".join(cmd) + "\n")
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

    elapsed = round(time.time() - start, 2)
    append_text(log_path, proc.stdout or "")
    if proc.stderr:
        append_text(log_path, "\nSTDERR:\n" + proc.stderr)
    append_text(log_path, f"\nCOMMAND END: {now()} | returncode={proc.returncode} | elapsed={elapsed}\n")

    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout or "",
        "stderr": proc.stderr or "",
        "elapsed_seconds": elapsed,
    }


def newest_output(pattern, since_ts=None):
    files = glob.glob(pattern)
    if since_ts is not None:
        newer = [p for p in files if os.path.getmtime(p) >= since_ts]
        if newer:
            return max(newer, key=os.path.getmtime)
    return max(files, key=os.path.getmtime) if files else None


def latest_state(prefix):
    return read_json(latest_file(os.path.join(STATE_DIR, f"{prefix}*.json")))


def step_ok_168():
    s = latest_state("168_production_runner_state_")
    if not s:
        return False, "168 state yok"
    ok_count = as_int(get_any(s, ["ok_count", "successful", "basarili"], 0))
    err = as_int(get_any(s, ["error_count", "err_count", "hatali"], 0))
    cards = as_int(get_any(s, ["total_cards", "toplam_kart"], 0))
    ready = bool(get_any(s, ["ready_for_next_step", "ready_for_159"], False))
    ok = (ready or ok_count > 0) and ok_count > 0 and err == 0 and cards > 0
    return ok, f"ready={ready} ok={ok_count} error={err} cards={cards}"


def step_ok_171():
    s = latest_state("171_v2_mini_kalite_state_")
    if not s:
        return False, "171 state yok"
    block = as_int(get_any(s, ["block_cards", "block_count"], 0))
    avg = as_float(get_any(s, ["avg_score", "average_score", "ortalama_puan"], 0))
    total = as_int(get_any(s, ["total_cards", "toplam_kart", "cards_checked"], 0))
    ready = bool(get_any(s, ["can_go_169", "ready_for_169", "ready_for_next_step", "ready_for_import"], False))
    ok = block == 0 and (ready or avg >= 85 or total > 0)
    return ok, f"ready={ready} block={block} avg={avg} total={total}"


def step_ok_172():
    s = latest_state("172_ai_kalite_hakemi_state_")
    if not s:
        return False, "172 state yok"
    fail = as_int(s.get("fail_count", 0))
    err = as_int(s.get("error_count", 0))
    avg = as_float(s.get("average_score", 0))
    ready = bool(s.get("ready_for_173", False))
    ok = (ready or avg >= 85) and fail == 0 and err == 0
    return ok, f"ready={ready} fail={fail} error={err} avg={avg}"


def step_ok_175():
    s = latest_state("175_v2_ai_kapsam_state_")
    if not s:
        return False, "175 v2 state yok"
    err = as_int(s.get("error_count", 0))
    avg = as_float(s.get("avg_coverage_score", 0))
    fail = as_int(s.get("fail_count", 0))
    ready = bool(s.get("ready_for_176", False))
    ok = (ready or avg >= 80) and err == 0 and fail == 0
    return ok, f"ready={ready} avg_coverage={avg} fail={fail} error={err}"


def step_ok_176():
    s = latest_state("176_onceliklendirme_state_")
    if not s:
        return False, "176 state yok"
    regen = as_int(s.get("needs_regenerate_count", 0))
    avg = as_float(s.get("avg_priority_coverage", 0))
    ready = bool(s.get("ready_for_177", False))
    ok = (ready or avg >= 90) and regen == 0
    return ok, f"ready={ready} avg_priority={avg} regenerate={regen}"


def step_ok_177():
    s = latest_state("177_hukuki_dogruluk_state_")
    if not s:
        return False, "177 state yok"
    fail = as_int(s.get("fail_count", 0))
    fail_cards = as_int(s.get("fail_cards", 0))
    halluc = as_int(s.get("high_hallucination_cards", 0))
    overgen = as_int(s.get("high_overgeneralization_cards", 0))
    avg = as_float(s.get("avg_legal_accuracy_score", 0))
    ready = bool(s.get("ready_for_178", False))
    ok = (ready or avg >= 85) and fail == 0 and fail_cards == 0 and halluc == 0 and overgen == 0
    return ok, f"ready={ready} avg={avg} fail={fail} fail_cards={fail_cards} halluc={halluc} overgen={overgen}"


def step_ok_178():
    s = latest_state("178_birlestirme_hakemi_state_")
    if not s:
        return False, "178 state yok"
    err = as_int(s.get("error_count", 0))
    ready = bool(s.get("ready_for_179", False))
    ok = (ready or err == 0) and err == 0
    return ok, f"ready={ready} merge={s.get('merge_recommended_count')} reduction={s.get('reduction_rate')} error={err}"


def step_ok_179():
    s = latest_state("179_kart_optimizasyon_state_")
    if not s:
        return False, "179 state yok"
    err = as_int(s.get("error_count", 0))
    out = s.get("output_jsonl")
    ready = bool(s.get("ready_for_180", False))
    ok = (ready or out) and err == 0 and out and os.path.exists(out)
    return ok, f"ready={ready} output={out} reduction={s.get('reduction_rate')} error={err}"


def step_ok_180():
    s = latest_state("180_v2_karmasiklik_state_")
    if not s:
        return False, "180 v2 state yok"

    err = as_int(s.get("error_count", 0))
    too_few = as_int(s.get("too_few_count", 0))
    fail = as_int(s.get("fail_count", 0))
    avg = as_float(s.get("avg_planning_score", 0))
    ready = bool(s.get("ready_for_181", False))

    # v3: 180 planlama sinyalidir. Eksik kart, fail veya hata yoksa OK.
    ok = err == 0 and fail == 0 and too_few == 0
    warning = avg < 70 or not ready
    detail = f"ready={ready} avg={avg} too_few={too_few} fail={fail} error={err}"
    if ok and warning:
        detail += " | PLANLAMA_UYARISI_NON_BLOCKING"
    return ok, detail


def step_ok_169():
    s = latest_state("169_db_importer_state_")
    if not s:
        return False, "169 state yok"
    err = as_int(get_any(s, ["error_count", "hata"], 0))
    ready = bool(get_any(s, ["ready_for_next_step", "ready_for_170"], False))
    ok = (ready or err == 0) and err == 0
    return ok, f"ready={ready} error={err} inserted={get_any(s, ['inserted', 'inserted_cards', 'db_inserted_cards'])}"


def step_ok_170():
    s = latest_state("170_export_state_")
    if not s:
        return False, "170 state yok"
    exported = as_int(s.get("active_rows_exported", 0))
    web = s.get("web_jsonl")
    rag = s.get("rag_jsonl")
    ok = exported > 0 and web and os.path.exists(web) and rag and os.path.exists(rag)
    return ok, f"exported={exported} web={web} rag={rag}"


def step_ok_173():
    s = latest_state("173_v2_master_acceptance_state_")
    if not s:
        return False, "173 v2 state yok"
    ok = bool(s.get("master_ready_for_large_production"))
    return ok, f"ready={s.get('master_ready_for_large_production')} score={s.get('score')} blocks={s.get('block_count')}"


def record_step(steps, code, result, ok_func=None, skipped=False, non_blocking=False):
    if skipped:
        item = {"step": code, "ok": True, "skipped": True, "detail": "Atlandı"}
        steps.append(item)
        print(f"{code} sonucu: OK | Atlandı")
        return True

    if result["returncode"] != 0:
        detail = "Komut hata döndürdü"
        item = {
            "step": code,
            "ok": False,
            "returncode": result["returncode"],
            "detail": detail,
            "stderr_tail": result.get("stderr", "")[-1200:],
            "non_blocking": non_blocking,
        }
        steps.append(item)
        print(f"{code} sonucu: FAIL | {detail}")
        return False

    if ok_func:
        ok, detail = ok_func()
    else:
        ok, detail = True, "Komut tamamlandı"

    item = {
        "step": code,
        "ok": bool(ok),
        "returncode": result["returncode"],
        "detail": detail,
        "elapsed_seconds": result.get("elapsed_seconds"),
        "non_blocking": non_blocking,
    }
    steps.append(item)
    print(f"{code} sonucu: {'OK' if ok else 'FAIL'} | {detail}")
    return bool(ok)


def main():
    print("=" * 80)
    print("181 v3 - FINAL MASTER PRODUCTION CONTROLLER")
    print("=" * 80)

    run_tag = tag()
    limit, flags = parse_args()

    log_path = os.path.join(LOG_DIR, f"181_v3_final_master_controller_log_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"181_v3_final_master_controller_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"181_v3_final_master_controller_raporu_{run_tag}.txt")

    required = ["168", "171", "169", "170"]
    if not flags["skip_172"]:
        required.append("172")
    if not flags["skip_175"]:
        required.append("175")
    if not flags["skip_176"]:
        required.append("176")
    if not flags["skip_177"]:
        required.append("177")
    if not flags["skip_178"]:
        required.extend(["178", "179"])
    if not flags["skip_180"]:
        required.append("180")
    if not flags["skip_173"]:
        required.append("173")

    missing = [k for k in required if not os.path.exists(SCRIPTS[k])]

    print(f"\nLimit          : {limit}")
    print(f"Dry run        : {'EVET' if flags['dry_run'] else 'HAYIR'}")
    print(f"Atlananlar     : {[k for k,v in flags.items() if v and k != 'dry_run']}")
    print("-" * 80)

    if missing:
        print("\nEksik scriptler:")
        for k in missing:
            print(f"{k}: {SCRIPTS[k]}")
        raise FileNotFoundError("Eksik script var.")

    if flags["dry_run"]:
        print("DRY RUN aktif.")
        return

    steps = []
    overall_ok = True
    start_ts = time.time()

    print("\n[1] 168 üretim")
    res = run_cmd(["python", SCRIPTS["168"], str(limit)], log_path)
    overall_ok = record_step(steps, "168", res, step_ok_168) and overall_ok

    output_168 = newest_output(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"), start_ts)
    if not output_168 or not os.path.exists(output_168):
        steps.append({"step": "168_OUTPUT", "ok": False, "detail": "168 output bulunamadı"})
        print("168_OUTPUT sonucu: FAIL | 168 output bulunamadı")
        overall_ok = False
    else:
        print(f"168 output: {output_168}")

    if overall_ok:
        print("\n[2] 171 yapısal kalite")
        res = run_cmd(["python", SCRIPTS["171"], output_168], log_path)
        overall_ok = record_step(steps, "171", res, step_ok_171) and overall_ok

    if overall_ok and not flags["skip_172"]:
        print("\n[3] 172 AI kalite")
        res = run_cmd(["python", SCRIPTS["172"], output_168], log_path)
        overall_ok = record_step(steps, "172", res, step_ok_172) and overall_ok
    elif flags["skip_172"]:
        record_step(steps, "172", {}, skipped=True)

    if overall_ok and not flags["skip_175"]:
        print("\n[4] 175 v2 kapsam")
        res = run_cmd(["python", SCRIPTS["175"], output_168], log_path)
        overall_ok = record_step(steps, "175", res, step_ok_175) and overall_ok
    elif flags["skip_175"]:
        record_step(steps, "175", {}, skipped=True)

    if overall_ok and not flags["skip_176"]:
        print("\n[5] 176 önceliklendirme")
        res = run_cmd(["python", SCRIPTS["176"]], log_path)
        overall_ok = record_step(steps, "176", res, step_ok_176) and overall_ok
    elif flags["skip_176"]:
        record_step(steps, "176", {}, skipped=True)

    if overall_ok and not flags["skip_177"]:
        print("\n[6] 177 hukuki doğruluk")
        res = run_cmd(["python", SCRIPTS["177"], output_168], log_path)
        overall_ok = record_step(steps, "177", res, step_ok_177) and overall_ok
    elif flags["skip_177"]:
        record_step(steps, "177", {}, skipped=True)

    optimized_output = output_168

    if overall_ok and not flags["skip_178"]:
        print("\n[7] 178 kart birleştirme")
        res = run_cmd(["python", SCRIPTS["178"], output_168], log_path)
        overall_ok = record_step(steps, "178", res, step_ok_178) and overall_ok

        if overall_ok:
            print("\n[8] 179 kart optimizasyon")
            before_179 = time.time()
            res = run_cmd(["python", SCRIPTS["179"], output_168], log_path)
            overall_ok = record_step(steps, "179", res, step_ok_179) and overall_ok
            newest_179 = newest_output(os.path.join(URETIM_OUTPUT_DIR, "179_optimized_production_output_*.jsonl"), before_179)
            if newest_179 and os.path.exists(newest_179):
                optimized_output = newest_179
    elif flags["skip_178"]:
        record_step(steps, "178", {}, skipped=True)
        record_step(steps, "179", {}, skipped=True)

    print(f"\nImporter'a gidecek output: {optimized_output}")

    if overall_ok and not flags["skip_180"]:
        print("\n[9] 180 v2 karmaşıklık")
        res = run_cmd(["python", SCRIPTS["180"], optimized_output], log_path)
        overall_ok = record_step(steps, "180", res, step_ok_180) and overall_ok
    elif flags["skip_180"]:
        record_step(steps, "180", {}, skipped=True)

    if overall_ok:
        print("\n[10] 169 DB import")
        res = run_cmd(["python", SCRIPTS["169"], optimized_output], log_path)
        overall_ok = record_step(steps, "169", res, step_ok_169) and overall_ok

    if overall_ok:
        print("\n[11] 170 export")
        res = run_cmd(["python", SCRIPTS["170"]], log_path)
        overall_ok = record_step(steps, "170", res, step_ok_170) and overall_ok

    if overall_ok and not flags["skip_173"]:
        print("\n[12] 173 v2 final acceptance")
        res = run_cmd(["python", SCRIPTS["173"]], log_path)
        record_step(steps, "173", res, step_ok_173, non_blocking=True)
    elif flags["skip_173"]:
        record_step(steps, "173", {}, skipped=True)

    hard_steps = [s for s in steps if not s.get("skipped") and not s.get("non_blocking")]
    hard_ok = all(s.get("ok") for s in hard_steps)
    final_ready = hard_ok and overall_ok

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "limit": limit,
        "flags": flags,
        "output_168": output_168,
        "optimized_output": optimized_output,
        "final_ready_for_large_production": final_ready,
        "overall_ok": overall_ok,
        "steps": steps,
        "log_path": log_path,
        "rapor_path": rapor_path,
        "recommendation": "Büyük üretime kontrollü şekilde geçilebilir." if final_ready else "Başarısız adım rapordan incelenmeli.",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("181 v3 - FINAL MASTER PRODUCTION CONTROLLER RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Limit                         : {limit}\n")
        f.write(f"168 output                    : {output_168}\n")
        f.write(f"Optimize output               : {optimized_output}\n")
        f.write(f"Final büyük üretime hazır mı  : {'EVET' if final_ready else 'HAYIR'}\n")
        f.write(f"Öneri                         : {state['recommendation']}\n\n")

        f.write("ADIMLAR\n")
        f.write("-" * 80 + "\n")
        for s in steps:
            flags_txt = []
            if s.get("skipped"):
                flags_txt.append("SKIP")
            if s.get("non_blocking"):
                flags_txt.append("NON-BLOCKING")
            flag = f" ({', '.join(flags_txt)})" if flags_txt else ""
            f.write(f"{s.get('step'):<10} | {'OK' if s.get('ok') else 'FAIL'}{flag} | {s.get('detail')}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Log                           : {log_path}\n")
        f.write(f"State                         : {state_path}\n")
        f.write(f"Rapor                         : {rapor_path}\n")

    print("\n181 v3 FINAL MASTER CONTROLLER TAMAMLANDI")
    print("-" * 80)
    print(f"Final büyük üretime hazır mı  : {'EVET' if final_ready else 'HAYIR'}")
    print(f"168 output                    : {output_168}")
    print(f"Optimize output               : {optimized_output}")
    print(f"Öneri                         : {state['recommendation']}")

    print("\nDosyalar:")
    print(log_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
