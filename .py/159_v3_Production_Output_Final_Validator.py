# -*- coding: utf-8 -*-
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

VALID_SONUC = {
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


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def n(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def is_blank(x):
    return not str(x or "").strip()


def contains_any(text, words):
    text = n(text)
    return any(w in text for w in words)


def semantic_warning(sonuc_tipi, sonuc):
    """
    V3 mantığı:
    Sonuç tipi / sonuç uyumsuzluğu artık BLOCK değildir.
    Çünkü üretim kartlarında sonuc_tipi çoğu zaman nihai karar yönünü,
    sonuc ise idari işlem/mevzuat değerlendirmesini açıklayabilir.
    Bu nedenle bu durum yalnızca WARNING olarak işaretlenir.
    """
    st = str(sonuc_tipi or "").strip().upper()
    s = n(sonuc)

    if not st or not s:
        return False

    kabul_like = [
        "iddiası yerindedir",
        "iddia yerindedir",
        "yerinde görülmüştür",
        "başvurunun kabul",
        "düzeltici işlem",
        "ihalenin iptaline",
        "mevzuata aykırıdır",
        "uygun bulunmamıştır",
        "hukuka aykırıdır",
    ]

    ret_like = [
        "iddiası yerinde değildir",
        "iddia yerinde değildir",
        "yerinde görülmemiştir",
        "başvurunun reddine",
        "itirazen şikayet başvurusunun reddine",
        "reddedilmiştir",
        "mevzuata uygundur",
        "uygun bulunmuştur",
        "aykırılık bulunmamıştır",
    ]

    if st == "RET" and contains_any(s, kabul_like):
        return True

    if st in ["KABUL", "DÜZELTİCİ İŞLEM", "İPTAL"] and contains_any(s, ret_like):
        return True

    return False


def validate_card(row, card, card_index):
    block = []
    warning = []

    karar_no = row.get("karar_no", "")

    baslik = card.get("baslik", "")
    hukuki_soru = card.get("hukuki_soru", "")
    sonuc_tipi = card.get("sonuc_tipi", "")
    sonuc = card.get("sonuc", "")
    emsal_ilke = card.get("emsal_ilke", "")
    anahtar = card.get("anahtar", "")
    mevzuat = card.get("mevzuat", "")
    guven = card.get("guven", "")

    # BLOCK: DB'ye girmemesi gereken gerçek yapısal eksikler
    if is_blank(karar_no):
        block.append("BOS_KARAR_NO")

    if is_blank(baslik):
        block.append("BOS_BASLIK")

    if is_blank(hukuki_soru):
        block.append("BOS_HUKUKI_SORU")

    if is_blank(sonuc):
        block.append("BOS_SONUC")

    if is_blank(emsal_ilke):
        block.append("BOS_EMSAL_ILKE")

    if is_blank(sonuc_tipi):
        block.append("BOS_SONUC_TIPI")
    elif str(sonuc_tipi).strip().upper() not in VALID_SONUC:
        block.append("SONUC_TIPI_GECERSIZ")

    # WARNING: Kalite uyarısı ama DB'ye girebilir
    if is_blank(anahtar):
        warning.append("BOS_ANAHTAR")

    if is_blank(mevzuat):
        warning.append("BOS_MEVZUAT")

    if is_blank(guven):
        warning.append("BOS_GUVEN")
    elif str(guven).strip() not in VALID_GUVEN:
        warning.append("GUVEN_FORMAT")

    if len(str(baslik).strip()) < 8:
        warning.append("BASLIK_KISA")

    if len(str(hukuki_soru).strip()) < 15:
        warning.append("HUKUKI_SORU_KISA")

    if len(str(emsal_ilke).strip()) < 20:
        warning.append("EMSAL_ILKE_KISA")

    if semantic_warning(sonuc_tipi, sonuc):
        warning.append("SONUC_TIPI_SONUC_UYUM_UYARISI")

    if block:
        level = "BLOCK"
        db_ready = False
    elif warning:
        level = "WARNING"
        db_ready = True
    else:
        level = "READY"
        db_ready = True

    return {
        "karar_no": karar_no,
        "card_index": card_index,
        "baslik": baslik,
        "sonuc_tipi": sonuc_tipi,
        "guven": guven,
        "block_riskleri": block,
        "uyarilar": warning,
        "quality_level": level,
        "db_ready": db_ready,
        "card": card,
    }


def main():
    print("=" * 80)
    print("159 v3 - PRODUCTION OUTPUT FINAL VALIDATOR")
    print("=" * 80)

    t = tag()

    input_path = latest_file(INPUT_PATTERN)
    if not input_path:
        raise FileNotFoundError("158 output JSONL bulunamadı.")

    rows, json_errors = read_jsonl(input_path)

    ready = []
    warning = []
    block = []
    all_results = []

    block_counts = {}
    warning_counts = {}

    karar_no_yok = 0
    kart_listesi_yok = 0
    karar_mukerrer = 0
    total_cards = 0

    seen_karar = set()

    for row in rows:
        karar_no = str(row.get("karar_no", "")).strip()

        if not karar_no:
            karar_no_yok += 1
        else:
            key = karar_no.upper()
            if key in seen_karar:
                karar_mukerrer += 1
            seen_karar.add(key)

        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            kart_listesi_yok += 1
            continue

        seen_baslik = set()
        seen_soru = set()

        for idx, card in enumerate(kartlar, start=1):
            total_cards += 1
            result = validate_card(row, card, idx)

            b = n(card.get("baslik"))
            s = n(card.get("hukuki_soru"))

            if b and b in seen_baslik:
                result["uyarilar"].append("MUKERRER_BASLIK_WARNING")
            seen_baslik.add(b)

            if s and s in seen_soru:
                result["uyarilar"].append("MUKERRER_SORU_WARNING")
            seen_soru.add(s)

            if result["block_riskleri"]:
                result["quality_level"] = "BLOCK"
                result["db_ready"] = False
            elif result["uyarilar"]:
                result["quality_level"] = "WARNING"
                result["db_ready"] = True
            else:
                result["quality_level"] = "READY"
                result["db_ready"] = True

            for r in result["block_riskleri"]:
                block_counts[r] = block_counts.get(r, 0) + 1

            for w in result["uyarilar"]:
                warning_counts[w] = warning_counts.get(w, 0) + 1

            all_results.append(result)

            if result["quality_level"] == "BLOCK":
                block.append(result)
            elif result["quality_level"] == "WARNING":
                warning.append(result)
            else:
                ready.append(result)

    db_ready_rows = ready + warning

    production_ready = (
        len(json_errors) == 0
        and karar_no_yok == 0
        and kart_listesi_yok == 0
        and total_cards > 0
        and len(block) == 0
    )

    kalite = round((len(db_ready_rows) / total_cards) * 100, 2) if total_cards else 0

    ready_path = os.path.join(URETIM_OUTPUT_DIR, f"159_v3_db_ready_cards_{t}.jsonl")
    warning_path = os.path.join(URETIM_OUTPUT_DIR, f"159_v3_warning_cards_{t}.jsonl")
    block_path = os.path.join(URETIM_OUTPUT_DIR, f"159_v3_block_cards_{t}.jsonl")
    all_path = os.path.join(URETIM_OUTPUT_DIR, f"159_v3_all_validated_cards_{t}.jsonl")
    state_path = os.path.join(STATE_DIR, f"159_v3_validator_state_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"159_v3_production_output_final_validator_raporu_{t}.txt")

    write_jsonl(ready_path, db_ready_rows)
    write_jsonl(warning_path, warning)
    write_jsonl(block_path, block)
    write_jsonl(all_path, all_results)

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_path": input_path,
        "karar_sayisi": len(rows),
        "json_errors": len(json_errors),
        "karar_no_yok": karar_no_yok,
        "kart_listesi_yok": kart_listesi_yok,
        "karar_mukerrer": karar_mukerrer,
        "total_cards": total_cards,
        "ready": len(ready),
        "warning": len(warning),
        "block": len(block),
        "db_ready": len(db_ready_rows),
        "quality_score": kalite,
        "production_ready": production_ready,
        "block_counts": block_counts,
        "warning_counts": warning_counts,
        "ready_jsonl": ready_path,
        "warning_jsonl": warning_path,
        "block_jsonl": block_path,
        "all_jsonl": all_path,
        "next_step": "160_v3_Production_DB_Importer.py" if production_ready else "BLOCK_KARTLARI_INCELE",
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("159 v3 - PRODUCTION OUTPUT FINAL VALIDATOR RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input JSONL         : {input_path}\n\n")

        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı        : {len(rows)}\n")
        f.write(f"JSON hatası         : {len(json_errors)}\n")
        f.write(f"Karar no yok        : {karar_no_yok}\n")
        f.write(f"Mükerrer karar      : {karar_mukerrer}\n")
        f.write(f"Kart listesi yok    : {kart_listesi_yok}\n")
        f.write(f"Toplam kart         : {total_cards}\n")
        f.write(f"READY               : {len(ready)}\n")
        f.write(f"WARNING             : {len(warning)}\n")
        f.write(f"BLOCK               : {len(block)}\n")
        f.write(f"DB Ready            : {len(db_ready_rows)}\n")
        f.write(f"Kalite puanı        : {kalite} / 100\n")
        f.write(f"Production Ready    : {'EVET' if production_ready else 'HAYIR'}\n\n")

        f.write("BLOCK RİSK DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if block_counts:
            for k, v in sorted(block_counts.items()):
                f.write(f"{k:35}: {v}\n")
        else:
            f.write("BLOCK risk yok.\n")

        f.write("\nWARNING DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if warning_counts:
            for k, v in sorted(warning_counts.items()):
                f.write(f"{k:35}: {v}\n")
        else:
            f.write("Warning yok.\n")

        if block:
            f.write("\nBLOCK KARTLAR İLK 100\n")
            f.write("-" * 80 + "\n")
            for r in block[:100]:
                f.write(
                    f"[BLOCK] karar={r['karar_no']} kart={r['card_index']} "
                    f"risk={','.join(r['block_riskleri'])} | {r['baslik']}\n"
                )

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"DB Ready JSONL      : {ready_path}\n")
        f.write(f"Warning JSONL       : {warning_path}\n")
        f.write(f"Block JSONL         : {block_path}\n")
        f.write(f"All Validated JSONL : {all_path}\n")
        f.write(f"State JSON          : {state_path}\n")
        f.write(f"Rapor               : {rapor_path}\n")

    print("\n159 v3 FINAL VALIDATOR TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı     : {len(rows)}")
    print(f"Toplam kart      : {total_cards}")
    print(f"READY            : {len(ready)}")
    print(f"WARNING          : {len(warning)}")
    print(f"BLOCK            : {len(block)}")
    print(f"DB Ready         : {len(db_ready_rows)}")
    print(f"Kalite puanı     : {kalite} / 100")
    print(f"Production Ready : {'EVET' if production_ready else 'HAYIR'}")

    print("\nDosyalar:")
    print(ready_path)
    print(warning_path)
    print(block_path)
    print(all_path)
    print(state_path)
    print(rapor_path)

    print("\nNOT: DB'ye yazılmadı.")


if __name__ == "__main__":
    main()