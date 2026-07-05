# -*- coding: utf-8 -*-
"""
186 - BATCH STRESS TEST

Amaç:
- Kontrollü büyütme testi yapar.
- 181 v4 Final Master Controller'ı farklı limitlerle çalıştırır.
- Her denemeden sonra 182 v2 Drift ve 184 v2 Dashboard üretir.
- Sonuçları tek stres testi raporunda toplar.
- API kullanımı 181 zincirindeki modüllerden kaynaklanır.
- DB'ye 181/169 adımı yazdığı için gerçek üretim testidir.

Kullanım:
  python ".py\\186_Batch_Stress_Test.py"

Varsayılan senaryo:
  25, 50

Özel limitler:
  python ".py\\186_Batch_Stress_Test.py" 25 50 100

Sadece hızlı test:
  python ".py\\186_Batch_Stress_Test.py" 10

Not:
- Büyük limitlere geçmeden önce 10/25/50 ile dene.
- 181 v4 içinde 185 otomatik entegre değildir; 177 FAIL olursa batch durur ve raporlanır.
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

STATE_DIR = os.path.join(BASE_DIR, "production_state")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

SCRIPT_181 = os.path.join(PY_DIR, "181_v4_Final_Master_Production_Controller.py")
SCRIPT_182 = os.path.join(PY_DIR, "182_v2_Production_Drift_Analiz_Motoru.py")
SCRIPT_184 = os.path.join(PY_DIR, "184_v2_Production_Dashboard.py")

os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
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
        shell=False
    )

    elapsed = round(time.time() - start, 2)
    append_text(log_path, proc.stdout or "")
    if proc.stderr:
        append_text(log_path, "\nSTDERR:\n" + proc.stderr)
    append_text(log_path, f"\nCOMMAND END: {now()} | returncode={proc.returncode} | elapsed={elapsed}\n")

    return {
        "returncode": proc.returncode,
        "elapsed_seconds": elapsed,
        "stdout_tail": (proc.stdout or "")[-3000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def latest_state(prefix):
    return read_json(latest_file(os.path.join(STATE_DIR, f"{prefix}*.json")))


def parse_limits():
    limits = []
    for a in sys.argv[1:]:
        try:
            n = int(a)
            if n > 0:
                limits.append(n)
        except Exception:
            pass

    if not limits:
        limits = [25, 50]

    # Güvenlik: yanlışlıkla çok büyük başlatmayı önle
    clean = []
    for n in limits:
        if n > 500:
            print(f"UYARI: {n} çok büyük. Önce en fazla 500 ile stres testi önerilir. Bu limit atlandı.")
            continue
        clean.append(n)

    return clean or [25]


def get_181_summary():
    s = latest_state("181_v4_final_master_controller_state_")
    if not s:
        return {}
    steps = s.get("steps", [])
    step_map = {x.get("step"): x for x in steps if isinstance(x, dict)}
    return {
        "ready": bool(s.get("final_ready_for_large_production")),
        "output_168": s.get("output_168"),
        "optimized_output": s.get("optimized_output"),
        "recommendation": s.get("recommendation"),
        "steps": step_map,
        "state": s,
    }


def get_182_summary():
    s = latest_state("182_v2_production_drift_state_")
    if not s:
        return {}
    return {
        "final_decision": s.get("final_decision"),
        "final_drift_score": s.get("final_drift_score"),
        "new_model_cards": s.get("new_model_cards"),
        "legacy_cards": s.get("legacy_cards"),
        "ready_for_183": s.get("ready_for_183"),
        "state": s,
    }


def get_184_summary():
    s = latest_state("184_v2_production_dashboard_state_")
    if not s:
        return {}
    return {
        "overall_ready": s.get("overall_ready"),
        "active_export_cards": s.get("active_export_cards"),
        "sampling_ready": s.get("sampling_ready"),
        "warnings": s.get("warnings", []),
        "html_path": s.get("html_path"),
        "txt_path": s.get("txt_path"),
        "state": s,
    }


def main():
    print("=" * 80)
    print("186 - BATCH STRESS TEST")
    print("=" * 80)

    run_tag = tag()
    limits = parse_limits()

    for p in [SCRIPT_181, SCRIPT_182, SCRIPT_184]:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Script bulunamadı: {p}")

    log_path = os.path.join(LOG_DIR, f"186_batch_stress_test_log_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"186_batch_stress_test_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"186_batch_stress_test_raporu_{run_tag}.txt")

    print(f"\nSenaryo limitleri: {limits}")
    print("-" * 80)

    results = []
    overall_pass = True

    for idx, limit in enumerate(limits, start=1):
        print(f"\n[{idx}/{len(limits)}] Stress senaryosu başlıyor: limit={limit}")
        scenario_start = time.time()

        scenario = {
            "limit": limit,
            "started_at": now(),
            "181": {},
            "182": {},
            "184": {},
            "ok": False,
            "elapsed_seconds": None,
        }

        # 181
        print(f"181 v4 çalışıyor | limit={limit}")
        res181 = run_cmd(["python", SCRIPT_181, str(limit)], log_path)
        scenario["181_command"] = res181
        summary181 = get_181_summary()
        scenario["181"] = summary181

        ready181 = bool(summary181.get("ready"))
        print(f"181 sonucu: {'OK' if ready181 else 'FAIL'} | {summary181.get('recommendation')}")

        if not ready181:
            overall_pass = False
            scenario["ok"] = False
            scenario["elapsed_seconds"] = round(time.time() - scenario_start, 2)
            results.append(scenario)
            print("Bu senaryo 181'de durdu. Sonraki limite geçilmeyecek.")
            break

        # 182
        print("182 v2 drift analizi çalışıyor")
        res182 = run_cmd(["python", SCRIPT_182], log_path)
        scenario["182_command"] = res182
        summary182 = get_182_summary()
        scenario["182"] = summary182

        drift_ok = summary182.get("final_decision") in {"PASS", "WARNING"}
        print(f"182 sonucu: {'OK' if drift_ok else 'FAIL'} | drift={summary182.get('final_decision')} score={summary182.get('final_drift_score')}")

        if not drift_ok:
            overall_pass = False

        # 184
        print("184 v2 dashboard çalışıyor")
        res184 = run_cmd(["python", SCRIPT_184], log_path)
        scenario["184_command"] = res184
        summary184 = get_184_summary()
        scenario["184"] = summary184

        dash_ok = bool(summary184.get("overall_ready"))
        print(f"184 sonucu: {'OK' if dash_ok else 'WARNING'} | dashboard={summary184.get('html_path')}")

        # Senaryo sonucu
        scenario_ok = ready181 and drift_ok
        scenario["ok"] = scenario_ok
        scenario["elapsed_seconds"] = round(time.time() - scenario_start, 2)
        results.append(scenario)

        if not scenario_ok:
            overall_pass = False
            print("Senaryo uyarı/başarısız bitti. Sonraki limite geçilmeyecek.")
            break

        print(f"Senaryo tamamlandı: limit={limit} | süre={scenario['elapsed_seconds']} sn")

    # Final state
    state = {
        "run_id": run_tag,
        "created_at": now(),
        "limits": limits,
        "scenario_count": len(results),
        "overall_pass": overall_pass,
        "results": results,
        "log_path": log_path,
        "rapor_path": rapor_path,
        "ready_for_187": overall_pass,
        "next_step": "187_Production_Monitor.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("186 - BATCH STRESS TEST RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Limitler                      : {limits}\n")
        f.write(f"Genel sonuç                   : {'PASS' if overall_pass else 'FAIL'}\n")
        f.write(f"187'ye geçilebilir mi          : {'EVET' if overall_pass else 'HAYIR'}\n\n")

        f.write("SENARYOLAR\n")
        f.write("-" * 80 + "\n")
        for r in results:
            s181 = r.get("181", {})
            s182 = r.get("182", {})
            s184 = r.get("184", {})

            f.write(f"\nLimit                         : {r.get('limit')}\n")
            f.write(f"Sonuç                         : {'PASS' if r.get('ok') else 'FAIL'}\n")
            f.write(f"Süre                          : {r.get('elapsed_seconds')} sn\n")
            f.write(f"181 ready                     : {s181.get('ready')}\n")
            f.write(f"181 output                    : {s181.get('optimized_output') or s181.get('output_168')}\n")
            f.write(f"182 drift                     : {s182.get('final_decision')} ({s182.get('final_drift_score')}/100)\n")
            f.write(f"Yeni model kart               : {s182.get('new_model_cards')}\n")
            f.write(f"Aktif export kart             : {s184.get('active_export_cards')}\n")
            f.write(f"Dashboard                     : {s184.get('html_path')}\n")

            steps = s181.get("steps", {})
            if steps:
                f.write("181 adımları:\n")
                for step, obj in steps.items():
                    f.write(f"  - {step:<6} | {'OK' if obj.get('ok') else 'FAIL'} | {obj.get('detail')}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Log                           : {log_path}\n")
        f.write(f"State                         : {state_path}\n")
        f.write(f"Rapor                         : {rapor_path}\n")

    print("\n186 BATCH STRESS TEST TAMAMLANDI")
    print("-" * 80)
    print(f"Çalışan senaryo               : {len(results)}")
    print(f"Genel sonuç                   : {'PASS' if overall_pass else 'FAIL'}")
    print(f"187'ye geçilebilir mi          : {'EVET' if overall_pass else 'HAYIR'}")

    print("\nDosyalar:")
    print(log_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
