# -*- coding: utf-8 -*-
"""
185 - HUKUKI DOGRULUK DUZELTME / KARANTINA MOTORU

Amaç:
- 177 Hukuki Doğruluk Hakemi detay JSONL çıktısını okur.
- FAIL kartları veya HIGH hallüsinasyon/aşırı genelleme riski olan kartları tespit eder.
- Mümkünse 177'nin correction_suggestion alanlarıyla kartı düzeltir.
- Düzeltme yeterli değilse kartı karantinaya alır ve üretim JSONL'den çıkarır.
- DB'ye yazmaz.
- 178/179/169 öncesi temizlenmiş output JSONL üretir.

Kullanım:
  python ".py\\185_Hukuki_Dogruluk_Duzeltme_Karantina_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_YYYYMMDD_HHMMSS.jsonl"

Belirli 177 detay dosyasıyla:
  python ".py\\185_Hukuki_Dogruluk_Duzeltme_Karantina_Motoru.py" "C:\\...\\168_production_output_x.jsonl" "C:\\Users\\MSI\\Desktop\\kik_proje\\production_logs\\177_hukuki_dogruluk_detay_YYYYMMDD_HHMMSS.jsonl"

Sonra:
  python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\185_corrected_production_output_YYYYMMDD_HHMMSS.jsonl"
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

INPUT_168_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")
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


def clean_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s:
        return []
    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return [str(x).strip() for x in obj if str(x).strip()]
    except Exception:
        pass
    return [p.strip() for p in re.split(r"[,;]\s*", s) if p.strip()]


def infer_mevzuat_from_issue_text(issue_text, fallback_mevzuat):
    out = []
    text = issue_text or ""

    # Basit ve güvenli mevzuat yakalama.
    patterns = [
        r"4734\s*(?:sayılı\s*Kanun'?un)?\s*m\.?\s*(\d+[\/]?[a-zA-Z]?)",
        r"4734\s*(?:sayılı\s*Kanun'?un)?\s*(\d+)\s*(?:inci|nci|üncü|uncu)?\s*madd",
        r"4735\s*(?:sayılı\s*Kanun'?un)?\s*m\.?\s*(\d+[\/]?[a-zA-Z]?)",
    ]
    for pat in patterns:
        for m in re.findall(pat, text, flags=re.I):
            if "4734" in pat:
                out.append(f"4734 m.{m}")
            elif "4735" in pat:
                out.append(f"4735 m.{m}")

    # 56/b özel yakalama
    if re.search(r"56\s*/\s*b|56\s*\.?\s*madd.*\(b\)|56/b", text, flags=re.I):
        out.append("4734 m.56/b")

    for x in fallback_mevzuat:
        if x:
            out.append(x)

    seen = set()
    uniq = []
    for x in out:
        k = x.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    return uniq


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
        if not isinstance(card_reviews, list):
            continue

        reviews[karar_no] = card_reviews

    return reviews


def should_fix_or_quarantine(card_review):
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


def apply_correction(card, card_review, fallback_mevzuat):
    new_card = dict(card)

    corr = card_review.get("correction_suggestion", {})
    if not isinstance(corr, dict):
        corr = {}

    changed = False

    if corr.get("hukuki_soru"):
        new_card["hukuki_soru"] = str(corr.get("hukuki_soru")).strip()
        changed = True

    if corr.get("sonuc_ozeti"):
        new_card["sonuc_ozeti"] = str(corr.get("sonuc_ozeti")).strip()
        new_card["sonuc"] = new_card["sonuc_ozeti"]
        changed = True

    if corr.get("emsal_ilke"):
        new_card["emsal_ilke"] = str(corr.get("emsal_ilke")).strip()
        changed = True

    # Sonuç tipi düzeltme: Issues içinde iptal deniyorsa KABUL yerine IPTAL.
    issues_text = " ".join([str(x) for x in card_review.get("issues", [])])
    if re.search(r"iptal kararı|ihale.*iptal|karar.*iptal", issues_text, flags=re.I):
        st = str(new_card.get("sonuc_tipi", "")).upper()
        if st in {"KABUL", "RET", "RED", ""}:
            new_card["sonuc_tipi"] = "İPTAL"
            changed = True

    # Mevzuat boşsa issues/fallback'ten güvenli tahmin yap.
    mev = clean_list(new_card.get("mevzuat"))
    if not mev:
        inferred = infer_mevzuat_from_issue_text(issues_text, fallback_mevzuat)
        if inferred:
            new_card["mevzuat"] = inferred
            changed = True

    new_card["hukuki_dogruluk_duzeltme"] = {
        "source": "185_Hukuki_Dogruluk_Duzeltme_Karantina_Motoru",
        "created_at": now(),
        "original_decision": card_review.get("decision"),
        "original_hallucination_risk": card_review.get("hallucination_risk"),
        "original_overgeneralization_risk": card_review.get("overgeneralization_risk"),
        "issues": card_review.get("issues", []),
        "applied_correction": changed,
    }

    return new_card, changed


def main():
    print("=" * 80)
    print("185 - HUKUKI DOGRULUK DUZELTME / KARANTINA MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_168 = sys.argv[1]
    else:
        input_168 = latest_file(INPUT_168_PATTERN)

    if len(sys.argv) >= 3:
        input_177 = sys.argv[2]
    else:
        input_177 = latest_file(INPUT_177_PATTERN)

    if not input_168 or not os.path.exists(input_168):
        raise FileNotFoundError("168 production output bulunamadı.")
    if not input_177 or not os.path.exists(input_177):
        raise FileNotFoundError("177 hukuki doğruluk detay dosyası bulunamadı.")

    print(f"\nInput 168 : {input_168}")
    print(f"Input 177 : {input_177}")
    print("-" * 80)

    rows = read_jsonl(input_168)
    reviews = load_177_reviews(input_177)

    output_path = os.path.join(URETIM_OUTPUT_DIR, f"185_corrected_production_output_{run_tag}.jsonl")
    quarantine_path = os.path.join(LOG_DIR, f"185_quarantine_cards_{run_tag}.jsonl")
    detail_path = os.path.join(LOG_DIR, f"185_dogruluk_duzeltme_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"185_dogruluk_duzeltme_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"185_hukuki_dogruluk_duzeltme_raporu_{run_tag}.txt")

    output_rows = []

    total_cards = 0
    corrected_cards = 0
    quarantined_cards = 0
    affected_decisions = set()
    untouched_decisions = 0

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

        # Aynı karar içindeki güvenli mevzuat fallback'i
        fallback_mevzuat = []
        for c in kartlar:
            fallback_mevzuat.extend(clean_list(c.get("mevzuat")))
        fallback_mevzuat = list(dict.fromkeys(fallback_mevzuat))

        new_kartlar = []
        decision_changed = False

        for idx, card in enumerate(kartlar, start=1):
            cr = review_by_index.get(idx)

            if not cr or not should_fix_or_quarantine(cr):
                new_kartlar.append(card)
                continue

            affected_decisions.add(karar_no)

            fixed_card, changed = apply_correction(card, cr, fallback_mevzuat)

            # Güvenli kabul koşulu:
            # Düzeltme uygulandıysa ve temel alanlar doluysa üretime bırak.
            required_ok = all(str(fixed_card.get(k, "")).strip() for k in ["hukuki_soru", "sonuc_ozeti", "emsal_ilke"])
            mev_ok = len(clean_list(fixed_card.get("mevzuat"))) > 0

            if changed and required_ok and mev_ok:
                corrected_cards += 1
                decision_changed = True
                new_kartlar.append(fixed_card)
                append_jsonl(detail_path, {
                    "karar_no": karar_no,
                    "card_index": idx,
                    "action": "CORRECTED",
                    "title": card.get("baslik"),
                    "issues": cr.get("issues", []),
                    "new_sonuc_tipi": fixed_card.get("sonuc_tipi"),
                    "new_mevzuat": fixed_card.get("mevzuat"),
                })
            else:
                quarantined_cards += 1
                decision_changed = True
                append_jsonl(quarantine_path, {
                    "karar_no": karar_no,
                    "card_index": idx,
                    "action": "QUARANTINED",
                    "card": card,
                    "review": cr,
                    "reason": "Correction insufficient or mevzuat still empty.",
                })
                append_jsonl(detail_path, {
                    "karar_no": karar_no,
                    "card_index": idx,
                    "action": "QUARANTINED",
                    "title": card.get("baslik"),
                    "issues": cr.get("issues", []),
                })

        new_row = dict(row)
        new_row["kartlar"] = new_kartlar
        new_row["kart_sayisi"] = len(new_kartlar)
        new_row["hukuki_dogruluk_duzeltme"] = {
            "source": "185_Hukuki_Dogruluk_Duzeltme_Karantina_Motoru",
            "created_at": now(),
            "changed": decision_changed,
            "original_card_count": len(kartlar),
            "new_card_count": len(new_kartlar),
        }

        if not decision_changed:
            untouched_decisions += 1

        output_rows.append(new_row)

    write_jsonl(output_path, output_rows)

    ready_for_177_recheck = True
    ready_for_178 = quarantined_cards == 0

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_168": input_168,
        "input_177": input_177,
        "output_path": output_path,
        "total_cards": total_cards,
        "corrected_cards": corrected_cards,
        "quarantined_cards": quarantined_cards,
        "affected_decisions": sorted(affected_decisions),
        "affected_decision_count": len(affected_decisions),
        "untouched_decisions": untouched_decisions,
        "quarantine_path": quarantine_path,
        "detail_path": detail_path,
        "rapor_path": rapor_path,
        "ready_for_177_recheck": ready_for_177_recheck,
        "ready_for_178": ready_for_178,
        "recommended_recheck_command": f'python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "{output_path}"',
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("185 - HUKUKI DOGRULUK DUZELTME / KARANTINA MOTORU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input 168                     : {input_168}\n")
        f.write(f"Input 177                     : {input_177}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kart                    : {total_cards}\n")
        f.write(f"Düzeltilen kart                : {corrected_cards}\n")
        f.write(f"Karantina kart                 : {quarantined_cards}\n")
        f.write(f"Etkilenen karar                : {len(affected_decisions)}\n")
        f.write(f"177 tekrar kontrol hazır mı    : EVET\n")
        f.write(f"178'e doğrudan geçilebilir mi  : {'EVET' if ready_for_178 else 'HAYIR'}\n\n")

        f.write("ETKILENEN KARARLAR\n")
        f.write("-" * 80 + "\n")
        for k in sorted(affected_decisions):
            f.write(f"- {k}\n")

        f.write("\nÖNERILEN KOMUT\n")
        f.write("-" * 80 + "\n")
        f.write(state["recommended_recheck_command"] + "\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Corrected output               : {output_path}\n")
        f.write(f"Quarantine JSONL               : {quarantine_path}\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n185 DUZELTME / KARANTINA TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart                    : {total_cards}")
    print(f"Düzeltilen kart                : {corrected_cards}")
    print(f"Karantina kart                 : {quarantined_cards}")
    print(f"Etkilenen karar                : {len(affected_decisions)}")
    print(f"177 tekrar kontrol hazır mı    : EVET")
    print(f"178'e doğrudan geçilebilir mi  : {'EVET' if ready_for_178 else 'HAYIR'}")

    print("\nCorrected output:")
    print(output_path)

    print("\nÖnerilen komut:")
    print(state["recommended_recheck_command"])

    print("\nDosyalar:")
    print(quarantine_path)
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
