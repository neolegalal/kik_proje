# -*- coding: utf-8 -*-
import os, re, glob, json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "158_128_production_output_*.jsonl")

VALID_SONUC = {"KABUL", "RET", "DÜZELTİCİ İŞLEM", "İPTAL", "KARAR VERİLMESİNE YER OLMADIĞI", "DİĞER"}
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
    rows, errors = [], []
    with open(path, "r", encoding="utf-8") as f:
        for no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                errors.append({"line": no, "error": str(e), "raw": line[:300]})
    return rows, errors


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def n(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def blank(x):
    return not str(x or "").strip()


def contains_any(text, words):
    text = n(text)
    return any(w in text for w in words)


def sonuc_semantic_risk(sonuc_tipi, sonuc):
    st = str(sonuc_tipi or "").strip().upper()
    s = n(sonuc)

    kabul_signals = [
        "iddiası yerindedir",
        "iddia yerindedir",
        "yerinde görülmüştür",
        "başvurunun kabul",
        "düzeltici işlem belirlenmesine",
        "ihalenin iptaline",
        "mevzuata aykırıdır",
        "uygun bulunmamıştır",
    ]

    ret_signals = [
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

    duzeltici_signals = [
        "düzeltici işlem",
        "yeniden değerlendirilmesi",
        "teklifinin değerlendirme dışı bırakılması",
        "işlemlerin mevzuata uygun olarak yeniden gerçekleştirilmesi",
    ]

    iptal_signals = [
        "ihalenin iptaline",
        "iptaline karar verilmiştir",
    ]

    if st == "RET":
        return contains_any(s, kabul_signals) and not contains_any(s, ret_signals)

    if st == "KABUL":
        return contains_any(s, ret_signals) and not contains_any(s, kabul_signals + duzeltici_signals)

    if st == "DÜZELTİCİ İŞLEM":
        return contains_any(s, ret_signals) and not contains_any(s, duzeltici_signals)

    if st == "İPTAL":
        return contains_any(s, ret_signals) and not contains_any(s, iptal_signals)

    return False


def validate_card(row, card, idx):
    risks = []
    warnings = []

    baslik = card.get("baslik", "")
    soru = card.get("hukuki_soru", "")
    sonuc_tipi = card.get("sonuc_tipi", "")
    sonuc = card.get("sonuc", "")
    emsal = card.get("emsal_ilke", "")
    anahtar = card.get("anahtar", "")
    mevzuat = card.get("mevzuat", "")
    guven = card.get("guven", "")

    if blank(baslik): risks.append("BOS_BASLIK")
    if blank(soru): risks.append("BOS_HUKUKI_SORU")
    if blank(sonuc): risks.append("BOS_SONUC")
    if blank(emsal): risks.append("BOS_EMSAL_ILKE")
    if blank(sonuc_tipi): risks.append("BOS_SONUC_TIPI")
    elif str(sonuc_tipi).strip().upper() not in VALID_SONUC:
        risks.append("SONUC_TIPI_GECERSIZ")

    if blank(guven): warnings.append("BOS_GUVEN")
    elif str(guven).strip() not in VALID_GUVEN:
        warnings.append("GUVEN_FORMAT")

    if blank(mevzuat): warnings.append("BOS_MEVZUAT")
    if blank(anahtar): warnings.append("BOS_ANAHTAR")

    if not blank(sonuc_tipi) and not blank(sonuc):
        if sonuc_semantic_risk(sonuc_tipi, sonuc):
            risks.append("GERCEK_SONUC_TIPI_CELISKI")

    if len(str(emsal).strip()) < 15:
        warnings.append("EMSAL_KISA")

    if risks:
        level = "BLOCK"
    elif warnings:
        level = "WARNING"
    else:
        level = "READY"

    return {
        "karar_no": row.get("karar_no", ""),
        "card_index": idx,
        "baslik": baslik,
        "sonuc_tipi": sonuc_tipi,
        "guven": guven,
        "riskler": risks,
        "uyarilar": warnings,
        "quality_level": level,
        "db_ready": level in ["READY", "WARNING"],
        "card": card,
    }


def main():
    print("=" * 80)
    print("159 v2 - PRODUCTION OUTPUT KALİTE VALIDATOR")
    print("=" * 80)

    t = tag()
    input_path = latest_file(INPUT_PATTERN)
    if not input_path:
        raise FileNotFoundError("158 output JSONL bulunamadı.")

    rows, json_errors = read_jsonl(input_path)

    ready, warning, manual, block = [], [], [], []
    risk_counts, warn_counts = {}, {}

    total_cards = 0
    duplicate_title = 0
    duplicate_question = 0

    for row in rows:
        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            continue

        seen_titles = set()
        seen_questions = set()

        for i, card in enumerate(kartlar, 1):
            total_cards += 1
            result = validate_card(row, card, i)

            b = n(card.get("baslik"))
            q = n(card.get("hukuki_soru"))

            if b and b in seen_titles:
                result["uyarilar"].append("MUKERRER_BASLIK_WARNING")
                duplicate_title += 1
            seen_titles.add(b)

            if q and q in seen_questions:
                result["uyarilar"].append("MUKERRER_SORU_WARNING")
                duplicate_question += 1
            seen_questions.add(q)

            if result["riskler"]:
                result["quality_level"] = "BLOCK"
                result["db_ready"] = False
            elif result["uyarilar"]:
                result["quality_level"] = "WARNING"
                result["db_ready"] = True

            for r in result["riskler"]:
                risk_counts[r] = risk_counts.get(r, 0) + 1
            for w in result["uyarilar"]:
                warn_counts[w] = warn_counts.get(w, 0) + 1

            if result["quality_level"] == "READY":
                ready.append(result)
            elif result["quality_level"] == "WARNING":
                warning.append(result)
            elif result["quality_level"] == "MANUAL":
                manual.append(result)
            else:
                block.append(result)

    db_ready = ready + warning
    production_ready = len(json_errors) == 0 and len(block) == 0 and total_cards > 0
    kalite = round((len(db_ready) / total_cards) * 100, 2) if total_cards else 0

    ready_path = os.path.join(URETIM_OUTPUT_DIR, f"159_v2_db_ready_cards_{t}.jsonl")
    warning_path = os.path.join(URETIM_OUTPUT_DIR, f"159_v2_warning_cards_{t}.jsonl")
    block_path = os.path.join(URETIM_OUTPUT_DIR, f"159_v2_block_cards_{t}.jsonl")
    state_path = os.path.join(STATE_DIR, f"159_v2_validator_state_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"159_v2_production_output_kalite_validator_raporu_{t}.txt")

    write_jsonl(ready_path, db_ready)
    write_jsonl(warning_path, warning)
    write_jsonl(block_path, block)

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_path": input_path,
        "karar_sayisi": len(rows),
        "json_errors": len(json_errors),
        "total_cards": total_cards,
        "ready": len(ready),
        "warning": len(warning),
        "manual": len(manual),
        "block": len(block),
        "db_ready": len(db_ready),
        "quality_score": kalite,
        "production_ready": production_ready,
        "ready_jsonl": ready_path,
        "warning_jsonl": warning_path,
        "block_jsonl": block_path,
        "next_step": "160_v2_Production_DB_Importer.py" if production_ready else "BLOCK_KARTLARI_INCELE",
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("159 v2 - PRODUCTION OUTPUT KALİTE VALIDATOR RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input JSONL         : {input_path}\n\n")
        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı        : {len(rows)}\n")
        f.write(f"JSON hatası         : {len(json_errors)}\n")
        f.write(f"Toplam kart         : {total_cards}\n")
        f.write(f"READY               : {len(ready)}\n")
        f.write(f"WARNING             : {len(warning)}\n")
        f.write(f"MANUAL              : {len(manual)}\n")
        f.write(f"BLOCK               : {len(block)}\n")
        f.write(f"DB Ready            : {len(db_ready)}\n")
        f.write(f"Kalite puanı        : {kalite} / 100\n")
        f.write(f"Production Ready    : {'EVET' if production_ready else 'HAYIR'}\n\n")

        f.write("BLOCK RİSK DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if risk_counts:
            for k, v in sorted(risk_counts.items()):
                f.write(f"{k:35}: {v}\n")
        else:
            f.write("BLOCK risk yok.\n")

        f.write("\nWARNING DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if warn_counts:
            for k, v in sorted(warn_counts.items()):
                f.write(f"{k:35}: {v}\n")
        else:
            f.write("Warning yok.\n")

        if block:
            f.write("\nBLOCK KARTLAR İLK 100\n")
            f.write("-" * 80 + "\n")
            for r in block[:100]:
                f.write(f"[BLOCK] karar={r['karar_no']} kart={r['card_index']} risk={','.join(r['riskler'])} | {r['baslik']}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"DB Ready JSONL      : {ready_path}\n")
        f.write(f"Warning JSONL       : {warning_path}\n")
        f.write(f"Block JSONL         : {block_path}\n")
        f.write(f"State JSON          : {state_path}\n")
        f.write(f"Rapor               : {rapor_path}\n")

    print("\n159 v2 VALIDATOR TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı     : {len(rows)}")
    print(f"Toplam kart      : {total_cards}")
    print(f"READY            : {len(ready)}")
    print(f"WARNING          : {len(warning)}")
    print(f"BLOCK            : {len(block)}")
    print(f"DB Ready         : {len(db_ready)}")
    print(f"Kalite puanı     : {kalite} / 100")
    print(f"Production Ready : {'EVET' if production_ready else 'HAYIR'}")
    print("\nDosyalar:")
    print(ready_path)
    print(warning_path)
    print(block_path)
    print(state_path)
    print(rapor_path)
    print("\nNOT: DB'ye yazılmadı.")


if __name__ == "__main__":
    main()