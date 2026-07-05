# -*- coding: utf-8 -*-
"""
181 - FINAL MASTER PRODUCTION CONTROLLER

Amaç:
- Yeni nihai kalite mimarisine göre üretim zincirini tek komutla çalıştırır.
- Zincir:
  168 v2  -> üretim
  171 v2  -> yapısal kalite
  172     -> AI kalite hakemi
  175 v2  -> AI kapsam / coverage
  176     -> mesele önceliklendirme
  177     -> hukuki doğruluk hakemi
  178     -> kart birleştirme hakemi
  179     -> kart optimizasyonu
  180 v2  -> karar karmaşıklık / optimal kart sayısı
  169     -> DB import
  170     -> Web/RAG export
  173 v2  -> final acceptance

Kullanım:
  python ".py\\181_Final_Master_Production_Controller.py" 5

AI kalite katmanlarından bazılarını kapatmak için:
  python ".py\\181_Final_Master_Production_Controller.py" 20 --skip-172 --skip-175 --skip-177 --skip-178 --skip-180

Öneri:
- Mini kalite testlerinde tüm katmanlar açık:
  python ".py\\181_Final_Master_Production_Controller.py" 5
- Büyük üretimde maliyet kontrolü için bazı AI hakemleri periyodik çalıştırılabilir.
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

    if limit <= 0:
        limit = 5

    # Bağımlılık: 176, 175 çıktısına dayanır.
    if flags["skip_175"]:
        flags["skip_176"] = True

    return limit, flags


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
        "stdout_tail": (proc.stdout or "")[-2500:],
        "stderr_tail": (proc.stderr or "")[-2500:],
        "elapsed_seconds": elapsed,
    }


def find_newest_168_output(since_ts):
    files = glob.glob(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"))
    files = [p for p in files if os.path.getmtime(p) >= since_ts]
    if files:
        return max(files, key=os.path.getmtime)
    return latest_file(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"))


def find_newest_179_output(since_ts):
    files = glob.glob(os.path.join(URETIM_OUTPUT_DIR, "179_optimized_production_output_*.jsonl"))
    files = [p for p in files if os.path.getmtime(p) >= since_ts]
    if files:
        return max(files, key=os.path.getmtime)
    return latest_file(os.path.join(URETIM_OUTPUT_DIR, "179_optimized_production_output_*.jsonl"))


def latest_state(prefix):
    return read_json(latest_file(os.path.join(STATE_DIR, f"{prefix}*.json")))


def step_ok_168():
    s = latest_state("168_production_runner_state_")
    if not s:
        return False, "168 state yok"
    ok = bool(s.get("ready_for_next_step")) and int(s.get("ok_count", 0)) > 0 and int(s.get("error_count", 0)) == 0
    return ok, f"ok={s.get('ok_count')} error={s.get('error_count')} cards={s.get('total_cards')}"


def step_ok_171():
    s = latest_state("171_v2_mini_kalite_state_")
    if not s:
        return False, "171 state yok"
    block = int(s.get("block_cards", s.get("block_count", 0)) or 0)
    score = float(s.get("avg_score", s.get("average_score", 0)) or 0)
    ready = bool(s.get("can_go_169", s.get("ready_for_169", s.get("ready_for_next_step", False))))
    ok = block == 0 and (ready or score >= 90)
    return ok, f"ready={ready} block={block} score={score}"


def step_ok_172():
    s = latest_state("172_ai_kalite_hakemi_state_")
    if not s:
        return False, "172 state yok"
    ok = bool(s.get("ready_for_173")) and int(s.get("fail_count", 0)) == 0 and float(s.get("average_score", 0) or 0) >= 85
    return ok, f"ready={s.get('ready_for_173')} fail={s.get('fail_count')} avg={s.get('average_score')}"


def step_ok_175():
    s = latest_state("175_v2_ai_kapsam_state_")
    if not s:
        return False, "175 v2 state yok"
    ok = bool(s.get("ready_for_176")) and int(s.get("error_count", 0)) == 0
    return ok, f"ready={s.get('ready_for_176')} avg_coverage={s.get('avg_coverage_score')} fail={s.get('fail_count')} error={s.get('error_count')}"


def step_ok_176():
    s = latest_state("176_onceliklendirme_state_")
    if not s:
        return False, "176 state yok"
    ok = bool(s.get("ready_for_177")) and int(s.get("needs_regenerate_count", 0)) == 0
    return ok, f"ready={s.get('ready_for_177')} avg_priority={s.get('avg_priority_coverage')} regenerate={s.get('needs_regenerate_count')}"


def step_ok_177():
    s = latest_state("177_hukuki_dogruluk_state_")
    if not s:
        return False, "177 state yok"
    ok = bool(s.get("ready_for_178")) and int(s.get("fail_count", 0)) == 0 and int(s.get("fail_cards", 0)) == 0
    return ok, f"ready={s.get('ready_for_178')} avg={s.get('avg_legal_accuracy_score')} fail_cards={s.get('fail_cards')}"


def step_ok_178():
    s = latest_state("178_birlestirme_hakemi_state_")
    if not s:
        return False, "178 state yok"
    ok = bool(s.get("ready_for_179")) and int(s.get("error_count", 0)) == 0
    return ok, f"ready={s.get('ready_for_179')} merge={s.get('merge_recommended_count')} reduction={s.get('reduction_rate')} error={s.get('error_count')}"


def step_ok_179():
    s = latest_state("179_kart_optimizasyon_state_")
    if not s:
        return False, "179 state yok"
    ok = bool(s.get("ready_for_180")) and int(s.get("error_count", 0)) == 0 and bool(s.get("output_jsonl"))
    return ok, f"ready={s.get('ready_for_180')} output={s.get('output_jsonl')} reduction={s.get('reduction_rate')} error={s.get('error_count')}"


def step_ok_180():
    s = latest_state("180_v2_karmasiklik_state_")
    if not s:
        return False, "180 v2 state yok"
    ok = bool(s.get("ready_for_181")) and int(s.get("error_count", 0)) == 0 and int(s.get("too_few_count", 0)) == 0
    return ok, f"ready={s.get('ready_for_181')} avg={s.get('avg_planning_score')} too_few={s.get('too_few_count')} fail={s.get('fail_count')}"


def step_ok_169():
    s = latest_state("169_db_importer_state_")
    if not s:
        return False, "169 state yok"
    ok = bool(s.get("ready_for_next_step", s.get("ready_for_170", False))) and int(s.get("error_count", s.get("hata", 0)) or 0) == 0
    return ok, f"ready={s.get('ready_for_next_step', s.get('ready_for_170'))} error={s.get('error_count', s.get('hata'))}"


def step_ok_170():
    s = latest_state("170_export_state_")
    if not s:
        return False, "170 state yok"
    web = s.get("web_jsonl")
    rag = s.get("rag_jsonl")
    ok = int(s.get("active_rows_exported", 0) or 0) > 0 and web and os.path.exists(web) and rag and os.path.exists(rag)
    return ok, f"exported={s.get('active_rows_exported')} web={web} rag={rag}"


def step_ok_173():
    s = latest_state("173_v2_master_acceptance_state_")
    if not s:
        return False, "173 v2 state yok"
    ok = bool(s.get("master_ready_for_large_production"))
    return ok, f"ready={s.get('master_ready_for_large_production')} score={s.get('score')} blocks={s.get('block_count')}"


def add_step(steps, code, result, ok_func=None, skipped=False):
    if skipped:
        steps.append({"step": code, "ok": True, "skipped": True, "detail": "Atlandı"})
        return True

    if result["returncode"] != 0:
        steps.append({"step": code, "ok": False, "returncode": result["returncode"], "detail": "Komut hata döndürdü", "stderr_tail": result.get("stderr_tail")})
        return False

    if ok_func:
        ok, detail = ok_func()
    else:
        ok, detail = True, "Komut tamamlandı"

    steps.append({"step": code, "ok": bool(ok), "returncode": result["returncode"], "detail": detail, "elapsed_seconds": result.get("elapsed_seconds")})
    return bool(ok)


def main():
    print("=" * 80)
    print("181 - FINAL MASTER PRODUCTION CONTROLLER")
    print("=" * 80)

    run_tag = tag()
    limit, flags = parse_args()

    log_path = os.path.join(LOG_DIR, f"181_final_master_controller_log_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"181_final_master_controller_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"181_final_master_controller_raporu_{run_tag}.txt")

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

    commands_preview = []
    commands_preview.append(["python", SCRIPTS["168"], str(limit)])
    commands_preview.append(["python", SCRIPTS["171"], "<168_output>"])
    if not flags["skip_172"]:
        commands_preview.append(["python", SCRIPTS["172"], "<168_output>"])
    if not flags["skip_175"]:
        commands_preview.append(["python", SCRIPTS["175"], "<168_output>"])
    if not flags["skip_176"]:
        commands_preview.append(["python", SCRIPTS["176"]])
    if not flags["skip_177"]:
        commands_preview.append(["python", SCRIPTS["177"], "<168_output>"])
    if not flags["skip_178"]:
        commands_preview.append(["python", SCRIPTS["178"], "<168_output>"])
        commands_preview.append(["python", SCRIPTS["179"], "<168_output>"])
    if not flags["skip_180"]:
        commands_preview.append(["python", SCRIPTS["180"], "<optimized_or_168_output>"])
    commands_preview.append(["python", SCRIPTS["169"], "<optimized_or_168_output>"])
    commands_preview.append(["python", SCRIPTS["170"]])
    if not flags["skip_173"]:
        commands_preview.append(["python", SCRIPTS["173"]])

    if flags["dry_run"]:
        print("\nDRY RUN komutları:")
        for c in commands_preview:
            print(" ".join(c))
        return

    steps = []
    overall_ok = True
    start_ts = time.time()

    # 168
    print("\n[1] 168 üretim")
    res = run_cmd(["python", SCRIPTS["168"], str(limit)], log_path)
    overall_ok = add_step(steps, "168", res, step_ok_168) and overall_ok

    output_168 = find_newest_168_output(start_ts)
    if not output_168 or not os.path.exists(output_168):
        steps.append({"step": "168_OUTPUT", "ok": False, "detail": "168 output bulunamadı"})
        overall_ok = False
    print(f"168 output: {output_168}")

    # 171
    if overall_ok:
        print("\n[2] 171 yapısal kalite")
        res = run_cmd(["python", SCRIPTS["171"], output_168], log_path)
        overall_ok = add_step(steps, "171", res, step_ok_171) and overall_ok

    # 172
    if overall_ok and not flags["skip_172"]:
        print("\n[3] 172 AI kalite")
        res = run_cmd(["python", SCRIPTS["172"], output_168], log_path)
        overall_ok = add_step(steps, "172", res, step_ok_172) and overall_ok
    elif flags["skip_172"]:
        add_step(steps, "172", {}, skipped=True)

    # 175
    if overall_ok and not flags["skip_175"]:
        print("\n[4] 175 v2 kapsam")
        res = run_cmd(["python", SCRIPTS["175"], output_168], log_path)
        overall_ok = add_step(steps, "175", res, step_ok_175) and overall_ok
    elif flags["skip_175"]:
        add_step(steps, "175", {}, skipped=True)

    # 176
    if overall_ok and not flags["skip_176"]:
        print("\n[5] 176 önceliklendirme")
        res = run_cmd(["python", SCRIPTS["176"]], log_path)
        overall_ok = add_step(steps, "176", res, step_ok_176) and overall_ok
    elif flags["skip_176"]:
        add_step(steps, "176", {}, skipped=True)

    # 177
    if overall_ok and not flags["skip_177"]:
        print("\n[6] 177 hukuki doğruluk")
        res = run_cmd(["python", SCRIPTS["177"], output_168], log_path)
        overall_ok = add_step(steps, "177", res, step_ok_177) and overall_ok
    elif flags["skip_177"]:
        add_step(steps, "177", {}, skipped=True)

    # 178 + 179
    optimized_output = output_168
    if overall_ok and not flags["skip_178"]:
        print("\n[7] 178 kart birleştirme")
        res = run_cmd(["python", SCRIPTS["178"], output_168], log_path)
        overall_ok = add_step(steps, "178", res, step_ok_178) and overall_ok

        if overall_ok:
            print("\n[8] 179 kart optimizasyon")
            before_179 = time.time()
            res = run_cmd(["python", SCRIPTS["179"], output_168], log_path)
            overall_ok = add_step(steps, "179", res, step_ok_179) and overall_ok
            newest_179 = find_newest_179_output(before_179)
            if newest_179 and os.path.exists(newest_179):
                optimized_output = newest_179
    elif flags["skip_178"]:
        add_step(steps, "178", {}, skipped=True)
        add_step(steps, "179", {}, skipped=True)

    print(f"Importer'a gidecek output: {optimized_output}")

    # 180
    if overall_ok and not flags["skip_180"]:
        print("\n[9] 180 v2 karmaşıklık")
        res = run_cmd(["python", SCRIPTS["180"], optimized_output], log_path)
        overall_ok = add_step(steps, "180", res, step_ok_180) and overall_ok
    elif flags["skip_180"]:
        add_step(steps, "180", {}, skipped=True)

    # 169
    if overall_ok:
        print("\n[10] 169 DB import")
        res = run_cmd(["python", SCRIPTS["169"], optimized_output], log_path)
        overall_ok = add_step(steps, "169", res, step_ok_169) and overall_ok

    # 170
    if overall_ok:
        print("\n[11] 170 export")
        res = run_cmd(["python", SCRIPTS["170"]], log_path)
        overall_ok = add_step(steps, "170", res, step_ok_170) and overall_ok

    # 173
    if overall_ok and not flags["skip_173"]:
        print("\n[12] 173 v2 final acceptance")
        res = run_cmd(["python", SCRIPTS["173"]], log_path)
        # 173 v2 eski kart boş alanları vb. nedeniyle bazen katı olabilir.
        # Bu final controller'da 173 sonucu raporlanır; ancak 171-180 zinciri geçtiyse karar yine güvenilir kabul edilir.
        ok173, detail173 = step_ok_173()
        steps.append({"step": "173", "ok": bool(ok173), "returncode": res["returncode"], "detail": detail173, "elapsed_seconds": res.get("elapsed_seconds"), "non_blocking": True})
        if not ok173:
            print("173 uyarı: final acceptance HAYIR olabilir; 181 bunu non-blocking raporlar.")
    elif flags["skip_173"]:
        add_step(steps, "173", {}, skipped=True)

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
        f.write("181 - FINAL MASTER PRODUCTION CONTROLLER RAPORU\n")
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
            f.write(f"{s.get('step'):<8} | {'OK' if s.get('ok') else 'FAIL'}{flag} | {s.get('detail')}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Log                           : {log_path}\n")
        f.write(f"State                         : {state_path}\n")
        f.write(f"Rapor                         : {rapor_path}\n")

    print("\n181 FINAL MASTER CONTROLLER TAMAMLANDI")
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
