# -*- coding: utf-8 -*-
"""
181 v14 - FINAL MASTER PRODUCTION CONTROLLER / RESUME ORCHESTRATOR

v13 farkı:
- 182 v2 Production Drift sonucunda WARNING bloklayıcı değildir.
- 182 state içindeki ready_for_183=True ise 183'e geçilir.
- final_decision=PASS veya WARNING ise 181 zinciri devam eder.
- final_decision=FAIL / CRITICAL / BLOCK ise üretim durur.
- 182 skorları nested state yapısından da okunur: new_model_analysis/general_analysis.
- 177 self-healing PASS_AFTER_185 / PASS_AFTER_185V2 olduğunda ara 177 FAIL kayıtları final readiness hesabında blok sayılmaz.
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
    "182": os.path.join(PY_DIR, "182_v2_Production_Drift_Analiz_Motoru.py"),
    "183": os.path.join(PY_DIR, "183_Production_Sampling_QA.py"),
    "184": os.path.join(PY_DIR, "184_v4_Production_Dashboard.py"),
    "190": os.path.join(PY_DIR, "190_v2_Production_Supervisor.py"),
    "192": os.path.join(PY_DIR, "192_Resume_Engine.py"),
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
        "skip_182": False,
        "skip_183": False,
        "skip_184": False,
        "skip_190": False,
        "skip_185": False,
        "dry_run": False,
        "resume_run_id": None,
    }

    for a in sys.argv[1:]:
        if a.startswith("--resume="):
            flags["resume_run_id"] = a.split("=", 1)[1].strip()
            continue

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
        elif a == "--skip-182":
            flags["skip_182"] = True
        elif a == "--skip-183":
            flags["skip_183"] = True
        elif a == "--skip-184":
            flags["skip_184"] = True
        elif a == "--skip-190":
            flags["skip_190"] = True
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



def step_ok_182():
    s = latest_state("182_v2_production_drift_state_")
    if not s:
        return False, "182 v2 state yok"

    decision = (
        s.get("final_decision")
        or s.get("decision")
        or ""
    ).upper()

    # 182 v2 state yapısında skorlar çoğunlukla nested alanlarda duruyor.
    # v11 burada yanlış anahtar okuduğu için new_score/pool_score 0.0 görünüyordu.
    new_model = s.get("new_model_analysis") or {}
    general = s.get("general_analysis") or {}

    new_score = as_float(
        s.get("new_model_drift_score",
              new_model.get("drift_score",
                            s.get("drift_score", 0)))
    )

    pool_score = as_float(
        s.get("overall_pool_drift_score",
              s.get("general_drift_score",
                    general.get("drift_score", 0)))
    )

    ready_for_183 = bool(s.get("ready_for_183", False))

    # 182'nin kendi iş kuralı:
    # PASS      -> devam
    # WARNING   -> üretimi durdurmaz; rapora uyarı olarak yazılır
    # ready_for_183=True -> 182 zaten sonraki adıma geçilebilir demiştir
    # FAIL/CRITICAL/BLOCK -> durdur
    blocking_decisions = {"FAIL", "CRITICAL", "BLOCK", "BLOCKED"}
    nonblocking_decisions = {"PASS", "WARNING", "WARN"}

    if decision in blocking_decisions:
        ok = False
    elif ready_for_183:
        ok = True
    elif decision in nonblocking_decisions:
        ok = True
    else:
        # Geriye dönük tolerans: karar alanı yoksa skorlarla karar ver.
        ok = new_score >= 80 or pool_score >= 85

    detail = (
        f"decision={decision} new_score={new_score} pool_score={pool_score} "
        f"ready_for_183={ready_for_183}"
    )

    if ok and decision in {"WARNING", "WARN"}:
        detail += " | DRIFT_WARNING_NON_BLOCKING"

    return ok, detail


def step_ok_183():
    s = latest_state("183_sampling_qa_state_")
    if not s:
        return False, "183 sampling state yok"
    ready_ai = bool(s.get("ready_for_ai_qa", s.get("ai_qa_ready", False)))
    ready_184 = bool(s.get("ready_for_184", False))
    missing = as_int(s.get("missing_production_rows", s.get("production_missing_rows", 0)))
    samples = as_int(s.get("sample_count", s.get("created_sample_count", 0)))
    ok = (ready_ai or ready_184 or samples > 0) and missing == 0
    return ok, f"ready_ai={ready_ai} ready_184={ready_184} samples={samples} missing_rows={missing}"


def step_ok_184():
    s = latest_state("184_v4_production_dashboard_state_")
    if not s:
        return False, "184 v4 dashboard state yok"
    status = str(s.get("general_status") or s.get("genel_durum") or "").upper()
    ready = bool(s.get("ready_for_190", s.get("ready_for_185", False)))
    drift = str(s.get("drift_decision") or s.get("drift") or "").upper()
    # Dashboard bir görünüm katmanıdır; KONTROL GEREKIR üretim blok değildir.
    ok = ready or "PASS" in drift or status in {"ÜRETİME HAZIR", "URETIME HAZIR", "PRODUCTION_READY"}
    return ok, f"status={status} ready={ready} drift={drift}"


def step_ok_190():
    s = latest_state("190_v2_production_supervisor_state_")
    if not s:
        return False, "190 v2 supervisor state yok"
    score = as_float(s.get("production_health_score", s.get("health_score", 0)))
    ready = bool(s.get("ready_for_191", s.get("ready_for_next", False)))
    next_batch = s.get("next_batch_suggestion") or s.get("sonraki_batch_onerisi")
    ok = score >= 90 or ready
    return ok, f"health_score={score} ready={ready} next_batch={next_batch}"


def compute_recovered_steps(ai_cleaning_summary, healing_summary):
    recovered = set()
    if ai_cleaning_summary and ai_cleaning_summary.get("final_status") in {"PASS_AFTER_191"}:
        recovered.add("172")
    if healing_summary and healing_summary.get("final_status") in {"PASS_AFTER_185", "PASS_AFTER_185V2"}:
        recovered.add("177")
    return recovered


def compute_final_ready(steps, overall_ok, recovered_steps):
    hard_steps = []

    def is_recovered_attempt(step_name):
        step_name = str(step_name or "")

        # 172 AI kalite self-healing ile kurtarıldıysa ilk 172 FAIL kaydı
        # final readiness hesabında blok sayılmaz.
        if "172" in recovered_steps and step_name in {"172", "172_RECHECK_191"}:
            return True

        # 177 hukuki doğruluk self-healing / karantina ile kurtarıldıysa
        # ara 177 denemeleri FAIL olarak raporda kalır; ancak final üretim kararını
        # bloklamaz. Final 177_FINAL_RECHECK zaten ayrıca OK olmalıdır.
        if "177" in recovered_steps and step_name in {"177", "177_RECHECK_185"}:
            return True

        return False

    for st in steps:
        if st.get("skipped") or st.get("non_blocking"):
            continue
        if is_recovered_attempt(st.get("step")):
            continue
        hard_steps.append(st)

    return all(st.get("ok") for st in hard_steps) and overall_ok, hard_steps


def write_state_snapshot(state_path, run_tag, limit, flags, output_168, current_output,
                         optimized_output, healing_summary, ai_cleaning_summary,
                         steps, overall_ok, recovered_steps, log_path, rapor_path,
                         final_ready=None, recommendation=None):
    if final_ready is None:
        final_ready, _ = compute_final_ready(steps, overall_ok, recovered_steps)
    if recommendation is None:
        recommendation = "Büyük üretime kontrollü şekilde geçilebilir." if final_ready else "Başarısız adım rapordan incelenmeli."

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
        "recovered_steps": sorted(recovered_steps),
        "steps": steps,
        "log_path": log_path,
        "rapor_path": rapor_path,
        "recommendation": recommendation,
    }
    write_json(state_path, state)
    return state


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




def load_resume_engine():
    """192_Resume_Engine.py dosyasını güvenli şekilde yükler."""
    import importlib.util
    import sys

    resume_path = SCRIPTS.get("192")
    if not resume_path or not os.path.exists(resume_path):
        raise FileNotFoundError(f"192 Resume Engine bulunamadı: {resume_path}")

    module_name = "resume_engine_192"
    spec = importlib.util.spec_from_file_location(module_name, resume_path)
    mod = importlib.util.module_from_spec(spec)

    # Python 3.14 + dataclass için gerekli
    sys.modules[module_name] = mod

    spec.loader.exec_module(mod)
    return mod.ResumeEngine


def resume_step_done(resume, step):
    try:
        return resume.is_step_done(step)
    except Exception:
        return False


def resume_mark_done(resume, step, output_path=None, detail="", elapsed_seconds=None, extra=None):
    try:
        resume.mark_step_done(step, output_path=output_path, detail=detail, elapsed_seconds=elapsed_seconds, extra=extra)
    except TypeError:
        resume.mark_step_done(step, output_path=output_path, detail=detail, elapsed_seconds=elapsed_seconds)
    except Exception:
        pass


def resume_start_step(resume, step, detail=""):
    try:
        resume.start_step(step, detail=detail)
    except Exception:
        pass


def resume_mark_fail(resume, step, error, detail=""):
    try:
        resume.mark_step_fail(step, error=error, detail=detail)
    except Exception:
        pass


def latest_resume_state_for_limit(limit):
    pattern = os.path.join(STATE_DIR, "192_resume_state_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    candidates = []
    for p in files:
        try:
            s = read_json(p)
            if s and int(s.get("batch_limit", -1)) == int(limit) and s.get("status") in {"RUNNING", "INTERRUPTED", "FAILED"}:
                candidates.append(p)
        except Exception:
            pass
    return max(candidates, key=os.path.getmtime) if candidates else None


def print_resume_banner(resume):
    try:
        s = resume.summary()
        print("\n" + "=" * 80)
        print("192 RESUME ENGINE AKTIF")
        print("=" * 80)
        print(f"Run ID          : {s.get('run_id')}")
        print(f"Batch Limit     : {s.get('batch_limit')}")
        print(f"Status          : {s.get('status')}")
        print(f"Last Done Step  : {s.get('last_done_step')}")
        print(f"Done Steps      : {', '.join(s.get('done_steps') or []) if s.get('done_steps') else 'Yok'}")
        print("-" * 80)
    except Exception:
        pass


def main():
    print("=" * 80)
    print("181 v14 - FINAL MASTER PRODUCTION CONTROLLER / RESUME ORCHESTRATOR")
    print("=" * 80)

    limit, flags = parse_args()
    ResumeEngine = load_resume_engine()

    if flags.get("resume_run_id"):
        run_tag = flags["resume_run_id"]
    else:
        run_tag = tag()

    log_path = os.path.join(LOG_DIR, f"181_v14_final_master_controller_log_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"181_v14_final_master_controller_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"181_v14_final_master_controller_raporu_{run_tag}.txt")

    resume = ResumeEngine(project_root=BASE_DIR, run_id=run_tag, batch_limit=limit)
    resume.start_run({
        "controller": "181_v14",
        "limit": limit,
        "flags": flags,
        "started_from": "resume" if flags.get("resume_run_id") else "new_run",
    })
    print_resume_banner(resume)

    required = ["168", "171", "188", "169", "170", "192"]
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
    if not flags["skip_182"]:
        required.append("182")
    if not flags["skip_183"]:
        required.append("183")
    if not flags["skip_184"]:
        required.append("184")
    if not flags["skip_190"]:
        required.append("190")

    missing = [k for k in required if not os.path.exists(SCRIPTS[k])]

    print(f"\nLimit          : {limit}")
    print(f"Dry run        : {'EVET' if flags['dry_run'] else 'HAYIR'}")
    print(f"Self-healing   : {'KAPALI' if flags.get('skip_185') else 'AÇIK'}")
    print(f"Resume run_id  : {run_tag}")
    print(f"Atlananlar     : {[k for k,v in flags.items() if v and k not in {'dry_run', 'resume_run_id'}]}")
    print("-" * 80)

    if missing:
        print("\nEksik scriptler:")
        for k in missing:
            print(f"{k}: {SCRIPTS[k]}")
        resume.fail_run("Eksik script var.")
        raise FileNotFoundError("Eksik script var.")

    if flags["dry_run"]:
        print("DRY RUN aktif.")
        resume.finish_run(final_ready=False, detail="Dry run completed.")
        return

    steps = []
    overall_ok = True
    start_ts = time.time()

    try:
        # [1] 168
        if resume_step_done(resume, "168"):
            output_168 = resume.get_step_output("168")
            detail = resume.get_step_detail("168") or "RESUME: daha önce tamamlandı"
            steps.append({"step": "168", "ok": True, "detail": detail, "resumed": True})
            print(f"\n[1] 168 üretim | RESUME OK | {output_168}")
        else:
            print("\n[1] 168 üretim")
            resume_start_step(resume, "168", "Production generation")
            res = run_cmd(["python", SCRIPTS["168"], str(limit)], log_path)
            ok168 = record_step(steps, "168", res, step_ok_168)
            overall_ok = ok168 and overall_ok
            output_168 = newest_output(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"), start_ts)
            if not output_168 or not os.path.exists(output_168):
                steps.append({"step": "168_OUTPUT", "ok": False, "detail": "168 output bulunamadı"})
                print("168_OUTPUT sonucu: FAIL | 168 output bulunamadı")
                overall_ok = False
                resume_mark_fail(resume, "168", "168 output bulunamadı")
            else:
                print(f"168 output: {output_168}")
                if ok168:
                    resume_mark_done(resume, "168", output_path=output_168, detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))

        current_output = output_168
        healing_summary = None
        ai_cleaning_summary = None

        # [2] 188
        if overall_ok:
            if resume_step_done(resume, "188"):
                out = resume.get_step_output("188")
                if out and os.path.exists(out):
                    current_output = out
                steps.append({"step": "188", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print(f"\n[2] 188 production auto cleaner | RESUME OK | {current_output}")
            else:
                print("\n[2] 188 production auto cleaner")
                resume_start_step(resume, "188", "Production auto cleaner")
                res = run_cmd(["python", SCRIPTS["188"], current_output], log_path)
                ok188 = record_step(steps, "188", res, step_ok_188)
                overall_ok = ok188 and overall_ok
                s188 = latest_state("188_auto_cleaner_state_") or {}
                clean_output = s188.get("clean_output_path")
                if overall_ok and clean_output and os.path.exists(clean_output):
                    current_output = clean_output
                    print(f"188 clean output: {current_output}")
                if ok188:
                    resume_mark_done(resume, "188", output_path=current_output, detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))

        # [3] 172 + 191
        if overall_ok and not flags["skip_172"]:
            if resume_step_done(resume, "172"):
                out = resume.get_step_output("172")
                if out and os.path.exists(out):
                    current_output = out
                steps.append({"step": "172", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print(f"\n[3] 172 AI kalite | RESUME OK | {current_output}")
                ai_cleaning_summary = {
                    "initial_output": current_output,
                    "final_output": current_output,
                    "used_191": False,
                    "final_status": "PASS_RESUMED",
                    "attempts": [],
                }
            else:
                resume_start_step(resume, "172", "AI quality with optional 191 cleaning")
                ok_ai, ai_cleaned_output, ai_cleaning_summary = run_172_with_ai_cleaning(current_output, log_path, steps)
                overall_ok = ok_ai and overall_ok
                current_output = ai_cleaned_output
                if ok_ai:
                    resume_mark_done(resume, "172", output_path=current_output, detail=ai_cleaning_summary.get("final_status"))
                else:
                    resume_mark_fail(resume, "172", ai_cleaning_summary.get("final_status") or "172 failed")
        elif flags["skip_172"]:
            record_step(steps, "172", {}, skipped=True)

        # [4] 175
        if overall_ok and not flags["skip_175"]:
            if resume_step_done(resume, "175"):
                steps.append({"step": "175", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[4] 175 v2 kapsam | RESUME OK")
            else:
                print("\n[4] 175 v2 kapsam")
                resume_start_step(resume, "175", "Coverage analysis")
                res = run_cmd(["python", SCRIPTS["175"], current_output], log_path)
                ok175 = record_step(steps, "175", res, step_ok_175)
                overall_ok = ok175 and overall_ok
                if ok175:
                    resume_mark_done(resume, "175", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_175"]:
            record_step(steps, "175", {}, skipped=True)

        # [5] 176
        if overall_ok and not flags["skip_176"]:
            if resume_step_done(resume, "176"):
                steps.append({"step": "176", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[5] 176 önceliklendirme | RESUME OK")
            else:
                print("\n[5] 176 önceliklendirme")
                resume_start_step(resume, "176", "Priority analysis")
                res = run_cmd(["python", SCRIPTS["176"]], log_path)
                ok176 = record_step(steps, "176", res, step_ok_176)
                overall_ok = ok176 and overall_ok
                if ok176:
                    resume_mark_done(resume, "176", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_176"]:
            record_step(steps, "176", {}, skipped=True)

        # [6] 177 + 185 + 185v2
        if overall_ok and not flags["skip_177"]:
            if resume_step_done(resume, "177"):
                out = resume.get_step_output("177")
                if out and os.path.exists(out):
                    current_output = out
                steps.append({"step": "177", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print(f"\n[6] 177 hukuki doğruluk | RESUME OK | {current_output}")
                healing_summary = {
                    "initial_output": current_output,
                    "final_output": current_output,
                    "used_185": False,
                    "used_185v2": False,
                    "final_status": "PASS_RESUMED",
                    "attempts": [],
                }
            else:
                resume_start_step(resume, "177", "Legal accuracy with self-healing")
                ok_heal, healed_output, healing_summary = run_177_self_healing(current_output, log_path, steps, flags)
                overall_ok = ok_heal and overall_ok
                current_output = healed_output
                if ok_heal:
                    resume_mark_done(resume, "177", output_path=current_output, detail=healing_summary.get("final_status"))
                else:
                    resume_mark_fail(resume, "177", healing_summary.get("final_status") or "177 failed")
        elif flags["skip_177"]:
            record_step(steps, "177", {}, skipped=True)

        optimized_output = current_output

        # [7-8] 178 + 179
        if overall_ok and not flags["skip_178"]:
            if resume_step_done(resume, "178"):
                steps.append({"step": "178", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[7] 178 kart birleştirme | RESUME OK")
            else:
                print("\n[7] 178 kart birleştirme")
                resume_start_step(resume, "178", "Smart merge")
                res = run_cmd(["python", SCRIPTS["178"], current_output], log_path)
                ok178 = record_step(steps, "178", res, step_ok_178)
                overall_ok = ok178 and overall_ok
                if ok178:
                    resume_mark_done(resume, "178", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))

            if overall_ok:
                if resume_step_done(resume, "179"):
                    out = resume.get_step_output("179")
                    if out and os.path.exists(out):
                        optimized_output = out
                    steps.append({"step": "179", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                    print(f"\n[8] 179 kart optimizasyon | RESUME OK | {optimized_output}")
                else:
                    print("\n[8] 179 kart optimizasyon")
                    resume_start_step(resume, "179", "Card optimization")
                    before_179 = time.time()
                    res = run_cmd(["python", SCRIPTS["179"], current_output], log_path)
                    ok179 = record_step(steps, "179", res, step_ok_179)
                    overall_ok = ok179 and overall_ok
                    newest_179 = newest_output(os.path.join(URETIM_OUTPUT_DIR, "179_optimized_production_output_*.jsonl"), before_179)
                    if newest_179 and os.path.exists(newest_179):
                        optimized_output = newest_179
                    if ok179:
                        resume_mark_done(resume, "179", output_path=optimized_output, detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_178"]:
            record_step(steps, "178", {}, skipped=True)
            record_step(steps, "179", {}, skipped=True)

        print(f"\nImporter'a gidecek output: {optimized_output}")

        # [9] 180
        if overall_ok and not flags["skip_180"]:
            if resume_step_done(resume, "180"):
                steps.append({"step": "180", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[9] 180 v2 karmaşıklık | RESUME OK")
            else:
                print("\n[9] 180 v2 karmaşıklık")
                resume_start_step(resume, "180", "Complexity analysis")
                res = run_cmd(["python", SCRIPTS["180"], optimized_output], log_path)
                ok180 = record_step(steps, "180", res, step_ok_180)
                overall_ok = ok180 and overall_ok
                if ok180:
                    resume_mark_done(resume, "180", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_180"]:
            record_step(steps, "180", {}, skipped=True)

        # [10] 169
        if overall_ok:
            if resume_step_done(resume, "169"):
                steps.append({"step": "169", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[10] 169 DB import | RESUME OK")
            else:
                print("\n[10] 169 DB import")
                resume_start_step(resume, "169", "DB import")
                res = run_cmd(["python", SCRIPTS["169"], optimized_output], log_path)
                ok169 = record_step(steps, "169", res, step_ok_169)
                overall_ok = ok169 and overall_ok
                if ok169:
                    resume_mark_done(resume, "169", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))

        # [11] 170
        if overall_ok:
            if resume_step_done(resume, "170"):
                steps.append({"step": "170", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[11] 170 export | RESUME OK")
            else:
                print("\n[11] 170 export")
                resume_start_step(resume, "170", "WEB/RAG export")
                res = run_cmd(["python", SCRIPTS["170"]], log_path)
                ok170 = record_step(steps, "170", res, step_ok_170)
                overall_ok = ok170 and overall_ok
                if ok170:
                    resume_mark_done(resume, "170", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))

        # [12] 173 non-blocking
        if overall_ok and not flags["skip_173"]:
            if resume_step_done(resume, "173"):
                steps.append({"step": "173", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True, "non_blocking": True})
                print("\n[12] 173 v2 final acceptance | RESUME OK")
            else:
                print("\n[12] 173 v2 final acceptance")
                resume_start_step(resume, "173", "Final acceptance")
                res = run_cmd(["python", SCRIPTS["173"]], log_path)
                ok173 = record_step(steps, "173", res, step_ok_173, non_blocking=True)
                if ok173:
                    resume_mark_done(resume, "173", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_173"]:
            record_step(steps, "173", {}, skipped=True)

        recovered_steps = compute_recovered_steps(ai_cleaning_summary, healing_summary)
        final_ready, hard_steps = compute_final_ready(steps, overall_ok, recovered_steps)

        state = write_state_snapshot(
            state_path, run_tag, limit, flags, output_168, current_output,
            optimized_output, healing_summary, ai_cleaning_summary,
            steps, overall_ok, recovered_steps, log_path, rapor_path,
            final_ready=final_ready
        )

        # [13] 182
        if overall_ok and not flags["skip_182"]:
            if resume_step_done(resume, "182"):
                steps.append({"step": "182", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[13] 182 v2 production drift | RESUME OK")
            else:
                print("\n[13] 182 v2 production drift")
                resume_start_step(resume, "182", "Production drift")
                res = run_cmd(["python", SCRIPTS["182"]], log_path)
                ok182 = record_step(steps, "182", res, step_ok_182)
                overall_ok = ok182 and overall_ok
                if ok182:
                    resume_mark_done(resume, "182", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_182"]:
            record_step(steps, "182", {}, skipped=True)

        # [14] 183
        if overall_ok and not flags["skip_183"]:
            if resume_step_done(resume, "183"):
                steps.append({"step": "183", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True})
                print("\n[14] 183 production sampling QA | RESUME OK")
            else:
                print("\n[14] 183 production sampling QA")
                resume_start_step(resume, "183", "Sampling QA")
                res = run_cmd(["python", SCRIPTS["183"]], log_path)
                ok183 = record_step(steps, "183", res, step_ok_183)
                overall_ok = ok183 and overall_ok
                if ok183:
                    resume_mark_done(resume, "183", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_183"]:
            record_step(steps, "183", {}, skipped=True)

        recovered_steps = compute_recovered_steps(ai_cleaning_summary, healing_summary)
        final_ready, hard_steps = compute_final_ready(steps, overall_ok, recovered_steps)
        state = write_state_snapshot(
            state_path, run_tag, limit, flags, output_168, current_output,
            optimized_output, healing_summary, ai_cleaning_summary,
            steps, overall_ok, recovered_steps, log_path, rapor_path,
            final_ready=final_ready
        )

        # [15] 184 non-blocking
        if overall_ok and not flags["skip_184"]:
            if resume_step_done(resume, "184"):
                steps.append({"step": "184", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True, "non_blocking": True})
                print("\n[15] 184 v4 production dashboard | RESUME OK")
            else:
                print("\n[15] 184 v4 production dashboard")
                resume_start_step(resume, "184", "Dashboard")
                res = run_cmd(["python", SCRIPTS["184"]], log_path)
                ok184 = record_step(steps, "184", res, step_ok_184, non_blocking=True)
                if ok184:
                    resume_mark_done(resume, "184", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_184"]:
            record_step(steps, "184", {}, skipped=True)

        recovered_steps = compute_recovered_steps(ai_cleaning_summary, healing_summary)
        final_ready, hard_steps = compute_final_ready(steps, overall_ok, recovered_steps)
        state = write_state_snapshot(
            state_path, run_tag, limit, flags, output_168, current_output,
            optimized_output, healing_summary, ai_cleaning_summary,
            steps, overall_ok, recovered_steps, log_path, rapor_path,
            final_ready=final_ready
        )

        # [16] 190 non-blocking
        if overall_ok and not flags["skip_190"]:
            if resume_step_done(resume, "190"):
                steps.append({"step": "190", "ok": True, "detail": "RESUME: daha önce tamamlandı", "resumed": True, "non_blocking": True})
                print("\n[16] 190 v2 production supervisor | RESUME OK")
            else:
                print("\n[16] 190 v2 production supervisor")
                resume_start_step(resume, "190", "Supervisor")
                res = run_cmd(["python", SCRIPTS["190"]], log_path)
                ok190 = record_step(steps, "190", res, step_ok_190, non_blocking=True)
                if ok190:
                    resume_mark_done(resume, "190", detail=steps[-1].get("detail"), elapsed_seconds=res.get("elapsed_seconds"))
        elif flags["skip_190"]:
            record_step(steps, "190", {}, skipped=True)

        recovered_steps = compute_recovered_steps(ai_cleaning_summary, healing_summary)
        final_ready, hard_steps = compute_final_ready(steps, overall_ok, recovered_steps)
        state = write_state_snapshot(
            state_path, run_tag, limit, flags, output_168, current_output,
            optimized_output, healing_summary, ai_cleaning_summary,
            steps, overall_ok, recovered_steps, log_path, rapor_path,
            final_ready=final_ready
        )

        # Resume final state
        resume.finish_run(final_ready=final_ready, detail=state["recommendation"])

        with open(rapor_path, "w", encoding="utf-8") as f:
            f.write("181 v14 - FINAL MASTER PRODUCTION CONTROLLER / RESUME ORCHESTRATOR RAPORU\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
            f.write(f"Limit                         : {limit}\n")
            f.write(f"Run ID                        : {run_tag}\n")
            f.write(f"Resume Engine                 : AKTIF\n")
            f.write(f"Resume State                  : {resume.state_path}\n")
            f.write(f"168 output                    : {output_168}\n")
            f.write(f"Healed/Clean output           : {current_output}\n")
            f.write(f"Optimize output               : {optimized_output}\n")
            f.write(f"Self-healing                  : {'AÇIK' if not flags.get('skip_185') else 'KAPALI'}\n")
            f.write("Auto-cleaner                  : AÇIK\n")
            f.write(f"Final büyük üretime hazır mı  : {'EVET' if final_ready else 'HAYIR'}\n")
            f.write(f"Kurtarılan adımlar             : {', '.join(sorted(recovered_steps)) if recovered_steps else 'Yok'}\n")
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
                if s.get("resumed"):
                    flags_txt.append("RESUMED")
                flag = f" ({', '.join(flags_txt)})" if flags_txt else ""
                f.write(f"{s.get('step'):<10} | {'OK' if s.get('ok') else 'FAIL'}{flag} | {s.get('detail')}\n")

            f.write("\nDOSYALAR\n")
            f.write("-" * 80 + "\n")
            f.write(f"Log                           : {log_path}\n")
            f.write(f"State                         : {state_path}\n")
            f.write(f"Resume State                  : {resume.state_path}\n")
            f.write(f"Rapor                         : {rapor_path}\n")

        # Ek 192 raporu
        try:
            resume_report = os.path.join(RAPOR_DIR, f"192_resume_engine_181_v14_{run_tag}.txt")
            resume.write_summary_report(resume_report)
        except Exception:
            pass

        print("\n181 v14 FINAL MASTER CONTROLLER TAMAMLANDI")
        print("-" * 80)
        print(f"Final büyük üretime hazır mı  : {'EVET' if final_ready else 'HAYIR'}")
        print(f"Run ID                        : {run_tag}")
        print(f"Resume State                  : {resume.state_path}")
        print(f"168 output                    : {output_168}")
        print(f"Healed/Clean output           : {current_output}")
        print(f"Optimize output               : {optimized_output}")
        print(f"Kurtarılan adımlar             : {', '.join(sorted(recovered_steps)) if recovered_steps else 'Yok'}")
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
        print(resume.state_path)
        print(rapor_path)

    except KeyboardInterrupt:
        resume.interrupt_marker("keyboard_interrupt")
        print("\nKullanıcı tarafından durduruldu. Resume state kaydedildi.")
        raise
    except Exception as exc:
        resume.fail_run(str(exc))
        print("\n181 v14 hata ile durdu. Resume state kaydedildi.")
        raise


if __name__ == "__main__":
    main()
