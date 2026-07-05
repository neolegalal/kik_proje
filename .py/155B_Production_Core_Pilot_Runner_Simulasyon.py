# -*- coding: utf-8 -*-
"""
155B - PRODUCTION CORE PILOT RUNNER SİMÜLASYON

Amaç:
- En güncel 154 pilot JSONL dosyasını okur.
- 500 kaydı sırayla simüle eder.
- Her kayıt için dosya/karar no/uzantı kontrolü yapar.
- Production progress state üretir.
- DB'ye yazmaz.
- OpenAI çağrısı yapmaz.

Kullanım:
  python ".py\\155B_Production_Core_Pilot_Runner_Simulasyon.py"

İsteğe bağlı limit:
  python ".py\\155B_Production_Core_Pilot_Runner_Simulasyon.py" 25
"""

import os
import sys
import glob
import json
import time
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PILOT_DIR = os.path.join(BASE_DIR, "pilot_uretim")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")

PILOT_PATTERN = os.path.join(PILOT_DIR, "154_pilot_batch_*.jsonl")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


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
                return None
            return n
        except Exception:
            raise ValueError("Limit sayı olmalıdır. Örnek: python ... 25")
    return None


def validate_item(r):
    risks = []

    if "_json_error" in r:
        risks.append("JSON_HATASI")
        return risks

    karar_no = str(r.get("karar_no", "")).strip()
    dosya_yolu = str(r.get("dosya_yolu", "")).strip()
    uzanti = str(r.get("uzanti", "")).strip().lower()

    if not karar_no:
        risks.append("KARAR_NO_YOK")

    if not dosya_yolu:
        risks.append("DOSYA_YOLU_YOK")
    elif not os.path.exists(dosya_yolu):
        risks.append("DOSYA_BULUNAMADI")

    if uzanti not in [".pdf", ".txt"]:
        risks.append("UZANTI_DESTEKLENMIYOR")

    try:
        if dosya_yolu and os.path.exists(dosya_yolu):
            size = os.path.getsize(dosya_yolu)
            if size <= 0:
                risks.append("DOSYA_BOYUT_SIFIR")
    except Exception:
        risks.append("DOSYA_BOYUT_OKUNAMADI")

    return risks


def main():
    print("=" * 80)
    print("155B - PRODUCTION CORE PILOT RUNNER SİMÜLASYON")
    print("=" * 80)

    run_tag = tag()
    limit = get_limit()

    pilot_path = latest_file(PILOT_PATTERN)
    if not pilot_path:
        raise FileNotFoundError("154 pilot JSONL dosyası bulunamadı.")

    all_rows = read_jsonl(pilot_path)
    if not all_rows:
        raise RuntimeError("Pilot JSONL boş görünüyor.")

    if limit:
        rows = all_rows[:limit]
    else:
        rows = all_rows

    log_path = os.path.join(LOG_DIR, f"155B_pilot_runner_simulasyon_log_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"155B_pilot_runner_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"155B_pilot_runner_simulasyon_raporu_{run_tag}.txt")

    start_time = time.time()

    processed = 0
    success = 0
    failed = 0
    risk_counts = {}
    log_rows = []

    for idx, r in enumerate(rows, start=1):
        risks = validate_item(r)
        status = "SIM_OK" if not risks else "SIM_RISK"

        if risks:
            failed += 1
            for risk in risks:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1
        else:
            success += 1

        processed += 1

        log_item = {
            "run_id": run_tag,
            "timestamp": now(),
            "pilot_index": idx,
            "batch_no": r.get("batch_no"),
            "pilot_sira": r.get("pilot_sira"),
            "karar_no": r.get("karar_no"),
            "dosya_adi": r.get("dosya_adi"),
            "dosya_yolu": r.get("dosya_yolu"),
            "status": status,
            "risks": risks,
            "mode": "SIMULATION",
            "openai_called": False,
            "db_written": False,
        }
        log_rows.append(log_item)

        if idx % 50 == 0 or idx == len(rows):
            print(f"Simülasyon ilerleme: {idx}/{len(rows)} | OK: {success} | Risk: {failed}")

    elapsed = round(time.time() - start_time, 2)

    write_jsonl(log_path, log_rows)

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "mode": "SIMULATION",
        "pilot_path": pilot_path,
        "total_pilot_rows": len(all_rows),
        "selected_rows": len(rows),
        "processed": processed,
        "success": success,
        "failed": failed,
        "risk_counts": risk_counts,
        "elapsed_seconds": elapsed,
        "openai_called": False,
        "db_written": False,
        "production_ready_for_real_runner": failed == 0 and processed > 0,
        "next_step": "155C_Production_Core_Pilot_Runner_Gercek.py" if failed == 0 else "RISKLERI_GIDER",
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("155B - PRODUCTION CORE PILOT RUNNER SİMÜLASYON RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                    : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Pilot JSONL               : {pilot_path}\n")
        f.write(f"Toplam pilot kayıt        : {len(all_rows)}\n")
        f.write(f"Seçilen kayıt             : {len(rows)}\n")
        f.write(f"İşlenen                   : {processed}\n")
        f.write(f"Başarılı simülasyon       : {success}\n")
        f.write(f"Riskli simülasyon         : {failed}\n")
        f.write(f"Süre saniye               : {elapsed}\n")
        f.write(f"OpenAI çağrısı            : HAYIR\n")
        f.write(f"DB yaz                    : HAYIR\n")
        f.write(f"Gerçek runner hazır       : {'EVET' if state['production_ready_for_real_runner'] else 'HAYIR'}\n\n")

        f.write("RİSK DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if risk_counts:
            for k, v in sorted(risk_counts.items()):
                f.write(f"{k}: {v}\n")
        else:
            f.write("Risk yok.\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Log JSONL                 : {log_path}\n")
        f.write(f"State JSON                : {state_path}\n")
        f.write(f"Rapor                     : {rapor_path}\n")

        if failed:
            f.write("\nRİSKLİ KAYITLAR İLK 50\n")
            f.write("-" * 80 + "\n")
            for item in [x for x in log_rows if x["status"] == "SIM_RISK"][:50]:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("\nPİLOT RUNNER SİMÜLASYON TAMAMLANDI")
    print("-" * 80)
    print(f"Pilot JSONL         : {pilot_path}")
    print(f"İşlenen             : {processed}")
    print(f"Başarılı            : {success}")
    print(f"Riskli              : {failed}")
    print(f"Gerçek runner hazır : {'EVET' if state['production_ready_for_real_runner'] else 'HAYIR'}")

    print("\nDosyalar:")
    print(log_path)
    print(state_path)
    print(rapor_path)

    print("\nNOT: OpenAI çağrısı yapılmadı. DB'ye yazılmadı.")


if __name__ == "__main__":
    main()