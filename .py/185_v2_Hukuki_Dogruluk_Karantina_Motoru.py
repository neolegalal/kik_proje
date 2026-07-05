# -*- coding: utf-8 -*-
"""
185 v2 - HUKUKI DOGRULUK KARANTINA MOTORU

v2 farkı:
- Eğer bir kart 185 ile daha önce düzeltilmiş olmasına rağmen 177'de hâlâ FAIL / HIGH risk alıyorsa,
  yeniden düzeltmeye çalışmaz; doğrudan karantinaya alır.
- Böylece riskli kart üretime girmez.
- DB'ye yazmaz.
- Temiz JSONL üretir.

Kullanım:
  python ".py\\185_v2_Hukuki_Dogruluk_Karantina_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\185_corrected_production_output_20260630_225422.jsonl" "C:\\Users\\MSI\\Desktop\\kik_proje\\production_logs\\177_hukuki_dogruluk_detay_20260630_225715.jsonl"

Sonra:
  python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\185_v2_clean_production_output_YYYYMMDD_HHMMSS.jsonl"
"""

import os
import re
import sys
import glob
import json
from datetime import datetime


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

INPUT_OUTPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "*production_output_*.jsonl")
INPUT_177_PATTERN = os.path.join(LOG_DIR, "177_hukuki_dogruluk_detay_*.jsonl")

os.makedirs(URETIM_OUTPUT_DIR, exist_ok=True)
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


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                rows.append({"_json_error": str(e), "_line_no": line_no, "_raw": line[:300]})
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def load_177_reviews(path):
    rows = read_jsonl(path)
    reviews = {}

    for row in rows:
        if row.get("status") != "OK":
            continue

        karar_no = str(row.get("karar_no", "")).strip()
        review = row.get("review", {})
        if not karar_no or not isinstance(review, dict):
            continue

        card_reviews = review.get("card_reviews", [])
        if isinstance(card_reviews, list):
            reviews[karar_no] = card_reviews

    return reviews


def should_quarantine(card_review):
    decision = str(card_review.get("decision", "")).upper()
    halluc = str(card_review.get("hallucination_risk", "")).upper()
    overgen = str(card_review.get("overgeneralization_risk", "")).upper()

    if decision == "FAIL":
        return True
    if halluc == "HIGH":
        return True
    if overgen == "HIGH":
        return True
    return False


def main():
    print("=" * 80)
    print("185 v2 - HUKUKI DOGRULUK KARANTINA MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_output = sys.argv[1]
    else:
        input_output = latest_file(INPUT_OUTPUT_PATTERN)

    if len(sys.argv) >= 3:
        input_177 = sys.argv[2]
    else:
        input_177 = latest_file(INPUT_177_PATTERN)

    if not input_output or not os.path.exists(input_output):
        raise FileNotFoundError("Production output JSONL bulunamadı.")
    if not input_177 or not os.path.exists(input_177):
        raise FileNotFoundError("177 hukuki doğruluk detay dosyası bulunamadı.")

    print(f"\nInput output : {input_output}")
    print(f"Input 177    : {input_177}")
    print("-" * 80)

    rows = read_jsonl(input_output)
    reviews = load_177_reviews(input_177)

    clean_output_path = os.path.join(URETIM_OUTPUT_DIR, f"185_v2_clean_production_output_{run_tag}.jsonl")
    quarantine_path = os.path.join(LOG_DIR, f"185_v2_quarantine_cards_{run_tag}.jsonl")
    detail_path = os.path.join(LOG_DIR, f"185_v2_karantina_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"185_v2_karantina_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"185_v2_hukuki_dogruluk_karantina_raporu_{run_tag}.txt")

    output_rows = []

    total_cards = 0
    kept_cards = 0
    quarantined_cards = 0
    affected_decisions = set()

    for row in rows:
        if row.get("status") != "OK":
            output_rows.append(row)
            continue

        karar_no = str(row.get("karar_no") or row.get("orijinal_karar_no") or "").strip()
        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            kartlar = []

        total_cards += len(kartlar)

        card_reviews = reviews.get(karar_no, [])
        review_by_index = {}
        for cr in card_reviews:
            try:
                review_by_index[int(cr.get("card_index"))] = cr
            except Exception:
                pass

        new_kartlar = []

        for idx, card in enumerate(kartlar, start=1):
            cr = review_by_index.get(idx)

            if cr and should_quarantine(cr):
                quarantined_cards += 1
                affected_decisions.add(karar_no)

                append_jsonl(quarantine_path, {
                    "karar_no": karar_no,
                    "card_index": idx,
                    "action": "QUARANTINED_AFTER_RECHECK",
                    "card": card,
                    "review": cr,
                    "reason": "177 recheck still returned FAIL or HIGH risk.",
                })

                append_jsonl(detail_path, {
                    "karar_no": karar_no,
                    "card_index": idx,
                    "action": "QUARANTINED",
                    "title": card.get("baslik"),
                    "decision": cr.get("decision"),
                    "hallucination_risk": cr.get("hallucination_risk"),
                    "overgeneralization_risk": cr.get("overgeneralization_risk"),
                    "issues": cr.get("issues", []),
                })
                continue

            kept_cards += 1
            new_kartlar.append(card)

        new_row = dict(row)
        new_row["kartlar"] = new_kartlar
        new_row["kart_sayisi"] = len(new_kartlar)
        new_row["hukuki_dogruluk_karantina"] = {
            "source": "185_v2_Hukuki_Dogruluk_Karantina_Motoru",
            "created_at": now(),
            "original_card_count": len(kartlar),
            "new_card_count": len(new_kartlar),
            "quarantined_count": len(kartlar) - len(new_kartlar),
        }

        output_rows.append(new_row)

    write_jsonl(clean_output_path, output_rows)

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_output": input_output,
        "input_177": input_177,
        "clean_output_path": clean_output_path,
        "total_cards": total_cards,
        "kept_cards": kept_cards,
        "quarantined_cards": quarantined_cards,
        "affected_decisions": sorted(affected_decisions),
        "affected_decision_count": len(affected_decisions),
        "quarantine_path": quarantine_path,
        "detail_path": detail_path,
        "rapor_path": rapor_path,
        "ready_for_177_recheck": True,
        "ready_for_178": True,
        "recommended_recheck_command": f'python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "{clean_output_path}"',
        "recommended_next_command": f'python ".py\\178_Akilli_Kart_Birlestirme_Hakemi.py" "{clean_output_path}"',
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("185 v2 - HUKUKI DOGRULUK KARANTINA MOTORU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input output                  : {input_output}\n")
        f.write(f"Input 177                     : {input_177}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kart                    : {total_cards}\n")
        f.write(f"Korunan kart                   : {kept_cards}\n")
        f.write(f"Karantina kart                 : {quarantined_cards}\n")
        f.write(f"Etkilenen karar                : {len(affected_decisions)}\n")
        f.write(f"177 tekrar kontrol hazır mı    : EVET\n")
        f.write(f"178'e geçilebilir mi           : EVET\n\n")

        f.write("ETKILENEN KARARLAR\n")
        f.write("-" * 80 + "\n")
        for k in sorted(affected_decisions):
            f.write(f"- {k}\n")

        f.write("\nÖNERILEN KOMUTLAR\n")
        f.write("-" * 80 + "\n")
        f.write(state["recommended_recheck_command"] + "\n")
        f.write(state["recommended_next_command"] + "\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Clean output                   : {clean_output_path}\n")
        f.write(f"Quarantine JSONL               : {quarantine_path}\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n185 v2 KARANTINA TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart                    : {total_cards}")
    print(f"Korunan kart                   : {kept_cards}")
    print(f"Karantina kart                 : {quarantined_cards}")
    print(f"Etkilenen karar                : {len(affected_decisions)}")
    print(f"177 tekrar kontrol hazır mı    : EVET")
    print(f"178'e geçilebilir mi           : EVET")

    print("\nClean output:")
    print(clean_output_path)

    print("\nÖnerilen komut:")
    print(state["recommended_recheck_command"])

    print("\nDosyalar:")
    print(quarantine_path)
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
