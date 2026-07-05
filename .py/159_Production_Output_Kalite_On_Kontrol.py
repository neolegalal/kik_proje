# -*- coding: utf-8 -*-
"""
159 - PRODUCTION OUTPUT KALİTE ÖN KONTROL

Amaç:
- 158_128_Production_JSONL_Runner çıktısını kontrol eder.
- DB'ye yazmadan önce kart kalitesini doğrular.
- Riskli kartları işaretler.
- DB'ye yazmaz.
"""

import os
import re
import glob
import json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "158_128_production_output_*.jsonl")

VALID_SONUC_TIPLERI = {
    "KABUL",
    "RET",
    "DÜZELTİCİ İŞLEM",
    "İPTAL",
    "KARAR VERİLMESİNE YER OLMADIĞI",
    "DİĞER",
}

VALID_GUVEN = {"Yüksek", "Orta", "Düşük"}

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def read_jsonl(path):
    rows = []
    errors = []

    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                errors.append({
                    "line_no": line_no,
                    "error": str(e),
                    "raw": line[:500],
                })

    return rows, errors


def is_blank(x):
    return not str(x or "").strip()


def norm(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def sonuc_celiski_var(sonuc_tipi, sonuc):
    st = norm(sonuc_tipi)
    s = norm(sonuc)

    kabul_kelimeleri = [
        "yerindedir",
        "yerinde görülmüştür",
        "uygun bulunmamıştır",
        "mevzuata aykırıdır",
        "iptali gerekmektedir",
        "düzeltici işlem",
    ]

    ret_kelimeleri = [
        "yerinde değildir",
        "yerinde görülmemiştir",
        "reddedilmiştir",
        "reddine",
        "mevzuata uygundur",
        "uygun bulunmuştur",
    ]

    if st == "ret":
        for k in kabul_kelimeleri:
            if k in s and "yerinde değildir" not in s and "yerinde görülmemiştir" not in s:
                return True

    if st in ["kabul", "düzeltici işlem", "iptal"]:
        for k in ret_kelimeleri:
            if k in s and "uygun bulunmamıştır" not in s:
                return True

    return False


def validate_card(row, card, card_index):
    risks = []

    karar_no = row.get("karar_no", "")
    baslik = card.get("baslik", "")
    hukuki_soru = card.get("hukuki_soru", "")
    sonuc_tipi = card.get("sonuc_tipi", "")
    sonuc = card.get("sonuc", "")
    emsal_ilke = card.get("emsal_ilke", "")
    anahtar = card.get("anahtar", "")
    mevzuat = card.get("mevzuat", "")
    guven = card.get("guven", "")

    if is_blank(baslik):
        risks.append("BOS_BASLIK")
    if is_blank(hukuki_soru):
        risks.append("BOS_HUKUKI_SORU")
    if is_blank(sonuc):
        risks.append("BOS_SONUC")
    if is_blank(emsal_ilke):
        risks.append("BOS_EMSAL_ILKE")
    if is_blank(anahtar):
        risks.append("BOS_ANAHTAR")
    if is_blank(mevzuat):
        risks.append("BOS_MEVZUAT")
    if is_blank(sonuc_tipi):
        risks.append("BOS_SONUC_TIPI")
    elif str(sonuc_tipi).strip() not in VALID_SONUC_TIPLERI:
        risks.append("SONUC_TIPI_GECERSIZ")

    if is_blank(guven):
        risks.append("BOS_GUVEN")
    elif str(guven).strip() not in VALID_GUVEN:
        risks.append("GUVEN_GECERSIZ")

    if sonuc_tipi and sonuc and sonuc_celiski_var(sonuc_tipi, sonuc):
        risks.append("SONUC_TIPI_SONUC_CELISKI")

    if len(str(baslik).strip()) < 8:
        risks.append("BASLIK_COK_KISA")

    if len(str(hukuki_soru).strip()) < 15:
        risks.append("HUKUKI_SORU_COK_KISA")

    if len(str(emsal_ilke).strip()) < 20:
        risks.append("EMSAL_ILKE_COK_KISA")

    return {
        "karar_no": karar_no,
        "card_index": card_index,
        "baslik": baslik,
        "sonuc_tipi": sonuc_tipi,
        "guven": guven,
        "riskler": risks,
        "db_ready": len(risks) == 0,
        "card": card,
    }


def main():
    print("=" * 80)
    print("159 - PRODUCTION OUTPUT KALİTE ÖN KONTROL")
    print("=" * 80)

    t = tag()

    input_path = latest_file(INPUT_PATTERN)
    if not input_path:
        raise FileNotFoundError("158 output JSONL bulunamadı.")

    rows, json_errors = read_jsonl(input_path)

    total_cards = 0
    ready_cards = 0
    risk_cards = 0
    karar_no_yok = 0
    kart_listesi_yok = 0
    karar_mukerrer = 0

    risk_counts = {}
    card_results = []
    ready_rows = []
    risk_rows = []

    seen_karar = set()

    for row_index, row in enumerate(rows, start=1):
        karar_no = str(row.get("karar_no", "")).strip()

        if not karar_no:
            karar_no_yok += 1

        if karar_no:
            k = karar_no.upper()
            if k in seen_karar:
                karar_mukerrer += 1
            seen_karar.add(k)

        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            kart_listesi_yok += 1
            kartlar = []

        title_seen = set()
        soru_seen = set()
        emsal_seen = set()

        for idx, card in enumerate(kartlar, start=1):
            total_cards += 1

            result = validate_card(row, card, idx)

            b = norm(card.get("baslik"))
            s = norm(card.get("hukuki_soru"))
            e = norm(card.get("emsal_ilke"))

            if b and b in title_seen:
                result["riskler"].append("MUKERRER_BASLIK")
            title_seen.add(b)

            if s and s in soru_seen:
                result["riskler"].append("MUKERRER_HUKUKI_SORU")
            soru_seen.add(s)

            if e and e in emsal_seen:
                result["riskler"].append("MUKERRER_EMSAL_ILKE")
            emsal_seen.add(e)

            result["db_ready"] = len(result["riskler"]) == 0

            for risk in result["riskler"]:
                risk_counts[risk] = risk_counts.get(risk, 0) + 1

            if result["db_ready"]:
                ready_cards += 1
                ready_rows.append(result)
            else:
                risk_cards += 1
                risk_rows.append(result)

            card_results.append(result)

    production_ready = (
        len(json_errors) == 0
        and karar_no_yok == 0
        and kart_listesi_yok == 0
        and karar_mukerrer == 0
        and total_cards > 0
        and risk_cards == 0
    )

    ready_jsonl = os.path.join(URETIM_OUTPUT_DIR, f"159_db_ready_cards_{t}.jsonl")
    risk_jsonl = os.path.join(URETIM_OUTPUT_DIR, f"159_riskli_cards_{t}.jsonl")
    state_path = os.path.join(STATE_DIR, f"159_production_output_kalite_state_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"159_production_output_kalite_on_kontrol_raporu_{t}.txt")

    with open(ready_jsonl, "w", encoding="utf-8") as f:
        for r in ready_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(risk_jsonl, "w", encoding="utf-8") as f:
        for r in risk_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_path": input_path,
        "karar_sayisi": len(rows),
        "json_error_count": len(json_errors),
        "total_cards": total_cards,
        "ready_cards": ready_cards,
        "risk_cards": risk_cards,
        "karar_no_yok": karar_no_yok,
        "kart_listesi_yok": kart_listesi_yok,
        "karar_mukerrer": karar_mukerrer,
        "risk_counts": risk_counts,
        "production_ready": production_ready,
        "ready_jsonl": ready_jsonl,
        "risk_jsonl": risk_jsonl,
        "next_step": "160_Production_DB_Importer.py" if production_ready else "RISKLERI_DUZELT",
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    kalite_puani = 0
    if total_cards:
        kalite_puani = round((ready_cards / total_cards) * 100, 2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("159 - PRODUCTION OUTPUT KALİTE ÖN KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                 : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input JSONL            : {input_path}\n\n")

        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı           : {len(rows)}\n")
        f.write(f"JSON hatası            : {len(json_errors)}\n")
        f.write(f"Karar no yok           : {karar_no_yok}\n")
        f.write(f"Mükerrer karar         : {karar_mukerrer}\n")
        f.write(f"Kart listesi yok       : {kart_listesi_yok}\n")
        f.write(f"Toplam kart            : {total_cards}\n")
        f.write(f"DB ready kart          : {ready_cards}\n")
        f.write(f"Riskli kart            : {risk_cards}\n")
        f.write(f"Kalite puanı           : {kalite_puani} / 100\n")
        f.write(f"Production Ready       : {'EVET' if production_ready else 'HAYIR'}\n\n")

        f.write("RİSK DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if risk_counts:
            for k, v in sorted(risk_counts.items()):
                f.write(f"{k:30}: {v}\n")
        else:
            f.write("Risk yok.\n")

        if risk_rows:
            f.write("\nRİSKLİ KARTLAR İLK 100\n")
            f.write("-" * 80 + "\n")
            for r in risk_rows[:100]:
                f.write(
                    f"[RISK] karar={r['karar_no']} kart={r['card_index']} "
                    f"risk={','.join(r['riskler'])} | {r['baslik']}\n"
                )

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"DB Ready JSONL         : {ready_jsonl}\n")
        f.write(f"Riskli JSONL           : {risk_jsonl}\n")
        f.write(f"State JSON             : {state_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\n159 KALİTE ÖN KONTROL TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı      : {len(rows)}")
    print(f"JSON hatası       : {len(json_errors)}")
    print(f"Toplam kart       : {total_cards}")
    print(f"DB ready kart     : {ready_cards}")
    print(f"Riskli kart       : {risk_cards}")
    print(f"Kalite puanı      : {kalite_puani} / 100")
    print(f"Production Ready  : {'EVET' if production_ready else 'HAYIR'}")

    print("\nDosyalar:")
    print(ready_jsonl)
    print(risk_jsonl)
    print(state_path)
    print(rapor_path)

    print("\nNOT: DB'ye yazılmadı.")


if __name__ == "__main__":
    main()