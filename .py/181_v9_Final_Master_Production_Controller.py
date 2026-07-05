# -*- coding: utf-8 -*-
"""
181 v9 - FINAL MASTER PRODUCTION CONTROLLER / FULL SELF-HEALING

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
    "188": os.path.join(PY_DIR, "188_Production_Auto_Cleaner.py"),
    "191": os.path.join(PY_DIR, "191_v2_AI_Kalite_Fail_Cleaner.py"),
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
    "185": os.path.join(PY_DIR, "185_Hukuki_Dogruluk_Duzeltme_Karantina_Motoru.py"),
    "185v2": os.path.join(PY_DIR, "185_v2_Hukuki_Dogruluk_Karantina_Motoru.py"),
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
        "skip_185": False,
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
        elif a == "--skip-185":
            flags["skip_185"] = True
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


def latest_log_path(prefix):
    return latest_file(os.path.join(LOG_DIR, f"{prefix}*.jsonl"))


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

    # v4:
    # 171 hâlâ sert kalite filtresidir.
    # Ancak 10+ kararlık kontrollü üretimde tekil ve düşük oranlı "soft block"
    # üretimi durdurmasın. Örn: KONU_OZETI_COK_KISA ama kart puanı yüksekse.
    #
    # Sert blok mantığı:
    # - block = 0 ise doğrudan OK.
    # - block oranı <= %5 ve ortalama kalite >= 95 ise WARNING gibi kabul edilir.
    # - Daha fazla block varsa üretim durur.
    soft_block_limit = max(1, int(total * 0.05)) if total else 0
    soft_block_tolerated = block > 0 and block <= soft_block_limit and avg >= 95

    ok = (
        (block == 0 and (ready or avg >= 85 or total > 0))
        or soft_block_tolerated
    )

    detail = f"ready={ready} block={block} avg={avg} total={total}"
    if soft_block_tolerated:
        detail += " | SOFT_BLOCK_TOLERATED_NON_BLOCKING"

    return ok, detail



def step_ok_188():
    s = latest_state("188_auto_cleaner_state_")
    if not s:
        return False, "188 state yok"
    final_ok = bool(s.get("final_ok"))
    out = s.get("clean_output_path")
    cleaner_used = bool(s.get("cleaner_used"))
    ok = final_ok and out and os.path.exists(out)
    return ok, f"final_ok={final_ok} cleaner_used={cleaner_used} clean_output={out}"


def get_172_status():
    s = latest_state("172_ai_kalite_hakemi_state_")
    if not s:
        return {
            "exists": False,
            "ok": False,
            "detail": "172 state yok",
            "fail": 999,
            "error": 999,
            "avg": 0,
            "ready": False,
            "state": {},
        }

    fail = as_int(s.get("fail_count", 0))
    err = as_int(s.get("error_count", 0))
    avg = as_float(s.get("average_score", 0))
    ready = bool(s.get("ready_for_173", False))

    ok = (ready or avg >= 85) and fail == 0 and err == 0
    detail = f"ready={ready} fail={fail} error={err} avg={avg}"

    return {
        "exists": True,
        "ok": ok,
        "detail": detail,
        "fail": fail,
        "error": err,
        "avg": avg,
        "ready": ready,
        "state": s,
    }


def step_ok_172():
    st = get_172_status()
    return st["ok"], st["detail"]



def step_ok_191():
    s = latest_state("191_v2_ai_fail_cleaner_state_")
    if not s:
        return False, "191 v2 state yok"
    out = s.get("output_path")
    removed = as_int(s.get("removed_cards", 0))
    detected = as_int(s.get("fail_cards_detected", 0))
    ready = bool(s.get("ready_for_172_recheck", False))
    ok = out and os.path.exists(out) and detected > 0 and removed == detected and ready
    return ok, f"ready={ready} detected={detected} removed={removed} output={out}"


def run_172_with_ai_cleaning(current_output, log_path, steps):
    """
    172 çalıştırır. FAIL varsa 191 v2 ile temizler, 172'yi tekrar çalıştırır.
    Returns: (ok, clean_output, summary)
    """
    summary = {
        "initial_output": current_output,
        "final_output": current_output,
        "used_191": False,
        "final_status": None,
        "attempts": [],
    }

    print("\n[3] 172 AI kalite")
    res172 = run_cmd(["python", SCRIPTS["172"], current_output], log_path)
    ok172 = record_step(steps, "172", res172, step_ok_172)

    st172 = get_172_status()
    detail_path_172 = latest_log_path("172_ai_kalite_hakemi_detay_")
    summary["attempts"].append({
        "stage": "initial_172",
        "ok": st172["ok"],
        "detail": st172["detail"],
        "detail_path": detail_path_172,
        "output": current_output,
    })

    if ok172:
        summary["final_status"] = "PASS_INITIAL"
        return True, current_output, summary

    if st172.get("fail", 0) <= 0:
        summary["final_status"] = "FAILED_172_NON_FAIL_REASON"
        return False, current_output, summary

    if not detail_path_172 or not os.path.exists(detail_path_172):
        summary["final_status"] = "FAILED_172_DETAIL_NOT_FOUND"
        return False, current_output, summary

    print("\n[3A] 191 v2 AI kalite fail temizliği")
    res191 = run_cmd(["python", SCRIPTS["191"], current_output, detail_path_172], log_path)
    ok191 = record_step(steps, "191", res191, step_ok_191)
    summary["used_191"] = True

    s191 = latest_state("191_v2_ai_fail_cleaner_state_") or {}
    cleaned_output = s191.get("output_path")
    if not ok191 or not cleaned_output or not os.path.exists(cleaned_output):
        summary["final_status"] = "FAILED_191"
        return False, current_output, summary

    print("\n[3B] 172 tekrar kontrol - 191 sonrası")
    res172b = run_cmd(["python", SCRIPTS["172"], cleaned_output], log_path)
    ok172b = record_step(steps, "172_RECHECK_191", res172b, step_ok_172)

    st172b = get_172_status()
    detail_path_172b = latest_log_path("172_ai_kalite_hakemi_detay_")
    summary["attempts"].append({
        "stage": "after_191_172",
        "ok": st172b["ok"],
        "detail": st172b["detail"],
        "detail_path": detail_path_172b,
        "output": cleaned_output,
    })

    if ok172b:
        summary["final_output"] = cleaned_output
        summary["final_status"] = "PASS_AFTER_191"
        return True, cleaned_output, summary

    summary["final_output"] = cleaned_output
    summary["final_status"] = "FAILED_AFTER_191"
    return False, cleaned_output, summary


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
    decision_count = as_int(s.get("decision_count", 0) or s.get("total_decisions", 0) or s.get("karar_sayisi", 0))
    ready = bool(s.get("ready_for_177", False))

    # v8: düşük oranlı regenerate sinyali üretimi durdurmasın.
    # Sert durdurma: avg < 90 veya regenerate oranı %5'i aşarsa.
    # Non-blocking: avg >= 95 ve regenerate oranı <= %5.
    regen_rate = (regen / decision_count) if decision_count else 0
    soft_regen = regen > 0 and avg >= 95 and regen_rate <= 0.05

    ok = (ready or avg >= 90) and (regen == 0 or soft_regen)

    detail = f"ready={ready} avg_priority={avg} regenerate={regen} regen_rate={round(regen_rate * 100, 2)}%"
    if soft_regen:
        detail += " | ONCELIK_UYARISI_NON_BLOCKING"

    return ok, detail


def get_177_status():
    s = latest_state("177_hukuki_dogruluk_state_")
    if not s:
        return {
            "ok": False,
            "detail": "177 state yok",
            "fail": 999,
            "fail_cards": 999,
            "halluc": 999,
            "overgen": 999,
            "avg": 0,
            "ready": False,
            "state": None,
        }

    fail = as_int(s.get("fail_count", 0))
    fail_cards = as_int(s.get("fail_cards", 0))
    halluc = as_int(s.get("high_hallucination_cards", 0))
    overgen = as_int(s.get("high_overgeneralization_cards", 0))
    avg = as_float(s.get("avg_legal_accuracy_score", 0))
    ready = bool(s.get("ready_for_178", False))
    ok = (ready or avg >= 85) and fail == 0 and fail_cards == 0 and halluc == 0 and overgen == 0
    detail = f"ready={ready} avg={avg} fail={fail} fail_cards={fail_cards} halluc={halluc} overgen={overgen}"

    return {
        "ok": ok,
        "detail": detail,
        "fail": fail,
        "fail_cards": fail_cards,
        "halluc": halluc,
        "overgen": overgen,
        "avg": avg,
        "ready": ready,
        "state": s,
    }


def step_ok_177():
    st = get_177_status()
    return st["ok"], st["detail"]


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
    decision_count = as_int(s.get("decision_count", 0))
    ready = bool(s.get("ready_for_181", False))

    # v5:
    # 180 karar karmaşıklığı / optimal kart sayısı sinyalidir.
    # 175 kapsam ve 176 önceliklendirme geçtiyse, düşük oranlı "too_few"
    # batch'i durdurmaz; üretim sonrası review/sampling uyarısı olarak izlenir.
    #
    # Sert durdurma:
    # - error varsa
    # - fail varsa
    # - too_few oranı %10'u aşarsa
    #
    # Non-blocking:
    # - avg düşükse
    # - ready=False ise
    # - too_few oranı düşükse
    too_few_rate = (too_few / decision_count) if decision_count else 0
    too_few_soft = too_few > 0 and too_few_rate <= 0.10

    ok = err == 0 and fail == 0 and (too_few == 0 or too_few_soft)

    detail = (
        f"ready={ready} avg={avg} too_few={too_few} "
        f"too_few_rate={round(too_few_rate * 100, 2)}% fail={fail} error={err}"
    )

    if ok and (avg < 70 or not ready or too_few_soft):
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


def step_ok_185(prefix):
    s = latest_state(prefix)
    if not s:
        return False, f"{prefix} state yok"
    out = s.get("output_path") or s.get("clean_output_path")
    ok = bool(out and os.path.exists(out))
    detail = (
        f"output={out} corrected={s.get('corrected_cards')} "
        f"quarantined={s.get('quarantined_cards')} kept={s.get('kept_cards')}"
    )
    return ok, detail


def run_177_self_healing(current_output, log_path, steps, flags):
    healing = {
        "initial_output": current_output,
        "final_output": current_output,
        "used_185": False,
        "used_185v2": False,
        "final_status": None,
        "attempts": [],
    }

    print("\n[6] 177 hukuki doğruluk")
    res = run_cmd(["python", SCRIPTS["177"], current_output], log_path)
    ok177 = record_step(steps, "177", res, step_ok_177)
    st = get_177_status()
    detail177 = latest_log_path("177_hukuki_dogruluk_detay_")
    healing["attempts"].append({"stage": "initial_177", "ok": st["ok"], "detail": st["detail"], "detail_path": detail177})

    if ok177:
        healing["final_status"] = "PASS_INITIAL"
        return True, current_output, healing

    if flags.get("skip_185"):
        healing["final_status"] = "FAILED_SELF_HEALING_SKIPPED"
        return False, current_output, healing

    if not detail177 or not os.path.exists(detail177):
        healing["final_status"] = "FAILED_177_DETAIL_NOT_FOUND"
        return False, current_output, healing

    print("\n[6A] 185 otomatik düzeltme")
    res185 = run_cmd(["python", SCRIPTS["185"], current_output, detail177], log_path)
    ok185 = record_step(steps, "185", res185, lambda: step_ok_185("185_dogruluk_duzeltme_state_"))
    healing["used_185"] = True
    s185 = latest_state("185_dogruluk_duzeltme_state_") or {}
    corrected_output = s185.get("output_path")
    if not ok185 or not corrected_output or not os.path.exists(corrected_output):
        healing["final_status"] = "FAILED_185"
        return False, current_output, healing

    print("\n[6B] 177 tekrar kontrol - 185 sonrası")
    res177b = run_cmd(["python", SCRIPTS["177"], corrected_output], log_path)
    ok177b = record_step(steps, "177_RECHECK_185", res177b, step_ok_177)
    stb = get_177_status()
    detail177b = latest_log_path("177_hukuki_dogruluk_detay_")
    healing["attempts"].append({"stage": "after_185_177", "ok": stb["ok"], "detail": stb["detail"], "detail_path": detail177b, "output": corrected_output})

    if ok177b:
        healing["final_output"] = corrected_output
        healing["final_status"] = "PASS_AFTER_185"
        return True, corrected_output, healing

    if not detail177b or not os.path.exists(detail177b):
        healing["final_status"] = "FAILED_177_RECHECK_DETAIL_NOT_FOUND"
        return False, corrected_output, healing

    print("\n[6C] 185 v2 otomatik karantina")
    res185v2 = run_cmd(["python", SCRIPTS["185v2"], corrected_output, detail177b], log_path)
    ok185v2 = record_step(steps, "185v2", res185v2, lambda: step_ok_185("185_v2_karantina_state_"))
    healing["used_185v2"] = True
    s185v2 = latest_state("185_v2_karantina_state_") or {}
    clean_output = s185v2.get("clean_output_path")
    if not ok185v2 or not clean_output or not os.path.exists(clean_output):
        healing["final_status"] = "FAILED_185V2"
        return False, corrected_output, healing

    print("\n[6D] 177 son kontrol - karantina sonrası")
    res177c = run_cmd(["python", SCRIPTS["177"], clean_output], log_path)
    ok177c = record_step(steps, "177_FINAL_RECHECK", res177c, step_ok_177)
    stc = get_177_status()
    detail177c = latest_log_path("177_hukuki_dogruluk_detay_")
    healing["attempts"].append({"stage": "after_185v2_177", "ok": stc["ok"], "detail": stc["detail"], "detail_path": detail177c, "output": clean_output})

    if ok177c:
        healing["final_output"] = clean_output
        healing["final_status"] = "PASS_AFTER_185V2"
        return True, clean_output, healing

    healing["final_output"] = clean_output
    healing["final_status"] = "FAILED_AFTER_185V2"
    return False, clean_output, healing


def main():
    print("=" * 80)
    print("181 v9 - FINAL MASTER PRODUCTION CONTROLLER / FULL SELF-HEALING")
    print("=" * 80)

    run_tag = tag()
    limit, flags = parse_args()

    log_path = os.path.join(LOG_DIR, f"181_v9_final_master_controller_log_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"181_v9_final_master_controller_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"181_v9_final_master_controller_raporu_{run_tag}.txt")

    required = ["168", "171", "188", "169", "170"]
    if not flags["skip_172"]:
        required.append("172")
        required.append("191")
    if not flags["skip_175"]:
        required.append("175")
    if not flags["skip_176"]:
        required.append("176")
    if not flags["skip_177"]:
        required.append("177")
        if not flags.get("skip_185"):
            required.extend(["185", "185v2"])
    if not flags["skip_178"]:
        required.extend(["178", "179"])
    if not flags["skip_180"]:
        required.append("180")
    if not flags["skip_173"]:
        required.append("173")

    missing = [k for k in required if not os.path.exists(SCRIPTS[k])]

    print(f"\nLimit          : {limit}")
    print(f"Dry run        : {'EVET' if flags['dry_run'] else 'HAYIR'}")
    print(f"Self-healing   : {'KAPALI' if flags.get('skip_185') else 'AÇIK'}")
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

    current_output = output_168
    healing_summary = None

    if overall_ok:
        print("\n[2] 188 production auto cleaner")
        res = run_cmd(["python", SCRIPTS["188"], current_output], log_path)
        overall_ok = record_step(steps, "188", res, step_ok_188) and overall_ok

        s188 = latest_state("188_auto_cleaner_state_") or {}
        clean_output = s188.get("clean_output_path")
        if overall_ok and clean_output and os.path.exists(clean_output):
            current_output = clean_output
            print(f"188 clean output: {current_output}")

    ai_cleaning_summary = None
    if overall_ok and not flags["skip_172"]:
        ok_ai, ai_cleaned_output, ai_cleaning_summary = run_172_with_ai_cleaning(current_output, log_path, steps)
        overall_ok = ok_ai and overall_ok
        current_output = ai_cleaned_output
    elif flags["skip_172"]:
        record_step(steps, "172", {}, skipped=True)

    if overall_ok and not flags["skip_175"]:
        print("\n[4] 175 v2 kapsam")
        res = run_cmd(["python", SCRIPTS["175"], current_output], log_path)
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
        ok_heal, healed_output, healing_summary = run_177_self_healing(current_output, log_path, steps, flags)
        overall_ok = ok_heal and overall_ok
        current_output = healed_output
    elif flags["skip_177"]:
        record_step(steps, "177", {}, skipped=True)

    optimized_output = current_output

    if overall_ok and not flags["skip_178"]:
        print("\n[7] 178 kart birleştirme")
        res = run_cmd(["python", SCRIPTS["178"], current_output], log_path)
        overall_ok = record_step(steps, "178", res, step_ok_178) and overall_ok

        if overall_ok:
            print("\n[8] 179 kart optimizasyon")
            before_179 = time.time()
            res = run_cmd(["python", SCRIPTS["179"], current_output], log_path)
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
        "healed_output": current_output,
        "optimized_output": optimized_output,
        "healing_summary": healing_summary,
        "ai_cleaning_summary": ai_cleaning_summary,
        "final_ready_for_large_production": final_ready,
        "overall_ok": overall_ok,
        "steps": steps,
        "log_path": log_path,
        "rapor_path": rapor_path,
        "recommendation": "Büyük üretime kontrollü şekilde geçilebilir." if final_ready else "Başarısız adım rapordan incelenmeli.",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("181 v9 - FINAL MASTER PRODUCTION CONTROLLER / FULL SELF-HEALING RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Limit                         : {limit}\n")
        f.write(f"168 output                    : {output_168}\n")
        f.write(f"Healed/Clean output           : {current_output}\n")
        f.write(f"Optimize output               : {optimized_output}\n")
        f.write(f"Self-healing                  : {'AÇIK' if not flags.get('skip_185') else 'KAPALI'}\n")
        f.write("Auto-cleaner                  : AÇIK\n")
        f.write(f"Final büyük üretime hazır mı  : {'EVET' if final_ready else 'HAYIR'}\n")
        f.write(f"Öneri                         : {state['recommendation']}\n\n")

        if ai_cleaning_summary:
            f.write("172 AI CLEANING OZETI\n")
            f.write("-" * 80 + "\n")
            f.write(f"Durum                         : {ai_cleaning_summary.get('final_status')}\n")
            f.write(f"191 kullanıldı mı              : {'EVET' if ai_cleaning_summary.get('used_191') else 'HAYIR'}\n")
            f.write(f"Final output                  : {ai_cleaning_summary.get('final_output')}\n")
            for a in ai_cleaning_summary.get("attempts", []):
                f.write(f"  - {a.get('stage')} | ok={a.get('ok')} | {a.get('detail')} | {a.get('detail_path')}\n")
            f.write("\n")

        if healing_summary:
            f.write("177 SELF-HEALING OZETI\n")
            f.write("-" * 80 + "\n")
            f.write(f"Durum                         : {healing_summary.get('final_status')}\n")
            f.write(f"185 kullanıldı mı              : {'EVET' if healing_summary.get('used_185') else 'HAYIR'}\n")
            f.write(f"185 v2 kullanıldı mı           : {'EVET' if healing_summary.get('used_185v2') else 'HAYIR'}\n")
            f.write(f"Final output                  : {healing_summary.get('final_output')}\n")
            for a in healing_summary.get("attempts", []):
                f.write(f"  - {a.get('stage')} | ok={a.get('ok')} | {a.get('detail')} | {a.get('detail_path')}\n")
            f.write("\n")

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

    print("\n181 v9 FINAL MASTER CONTROLLER TAMAMLANDI")
    print("-" * 80)
    print(f"Final büyük üretime hazır mı  : {'EVET' if final_ready else 'HAYIR'}")
    print(f"168 output                    : {output_168}")
    print(f"Healed/Clean output           : {current_output}")
    print(f"Optimize output               : {optimized_output}")
    if ai_cleaning_summary:
        print(f"172 AI cleaning durumu        : {ai_cleaning_summary.get('final_status')}")
        print(f"191 kullanıldı mı              : {'EVET' if ai_cleaning_summary.get('used_191') else 'HAYIR'}")
    if healing_summary:
        print(f"177 Self-healing durumu       : {healing_summary.get('final_status')}")
        print(f"185 kullanıldı mı              : {'EVET' if healing_summary.get('used_185') else 'HAYIR'}")
        print(f"185 v2 kullanıldı mı           : {'EVET' if healing_summary.get('used_185v2') else 'HAYIR'}")
    print(f"Öneri                         : {state['recommendation']}")

    print("\nDosyalar:")
    print(log_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
