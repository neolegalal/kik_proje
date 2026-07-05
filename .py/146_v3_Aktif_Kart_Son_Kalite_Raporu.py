# -*- coding: utf-8 -*-
import os
import re
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

VALID_SONUC = {
    "KABUL",
    "RET",
    "DÜZELTİCİ İŞLEM",
    "İPTAL",
    "KARAR VERİLMESİNE YER OLMADIĞI",
    "DİĞER",
}

VALID_GUVEN = {"Yüksek", "Orta", "Düşük"}


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def n(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def blank(x):
    return not str(x or "").strip()


def table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def col(row, cols, name, default=""):
    if name in cols:
        return row[cols.index(name)]
    return default


def contains_any(text, words):
    text = n(text)
    return any(w in text for w in words)


def semantic_warning(sonuc_tipi, sonuc):
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


def validate_card(card):
    block = []
    warning = []

    if blank(card["karar_no"]):
        block.append("BOS_KARAR_NO")

    if blank(card["baslik"]):
        block.append("BOS_BASLIK")

    if blank(card["hukuki_soru"]):
        block.append("BOS_HUKUKI_SORU")

    if blank(card["sonuc"]):
        block.append("BOS_SONUC")

    if blank(card["emsal_ilke"]):
        block.append("BOS_EMSAL_ILKE")

    if blank(card["sonuc_tipi"]):
        block.append("BOS_SONUC_TIPI")
    elif str(card["sonuc_tipi"]).strip().upper() not in VALID_SONUC:
        block.append("SONUC_TIPI_GECERSIZ")

    if blank(card["anahtar"]):
        warning.append("BOS_ANAHTAR")

    if blank(card["mevzuat"]):
        warning.append("BOS_MEVZUAT")

    if blank(card["guven"]):
        warning.append("BOS_GUVEN")
    elif str(card["guven"]).strip() not in VALID_GUVEN:
        warning.append("GUVEN_FORMAT")

    if len(str(card["baslik"]).strip()) < 8:
        warning.append("BASLIK_KISA")

    if len(str(card["hukuki_soru"]).strip()) < 15:
        warning.append("HUKUKI_SORU_KISA")

    if len(str(card["emsal_ilke"]).strip()) < 20:
        warning.append("EMSAL_ILKE_KISA")

    if semantic_warning(card["sonuc_tipi"], card["sonuc"]):
        warning.append("SONUC_TIPI_SONUC_UYUM_UYARISI")

    if block:
        level = "BLOCK"
    elif warning:
        level = "WARNING"
    else:
        level = "READY"

    return level, block, warning


def main():
    print("=" * 80)
    print("146 v3 - AKTİF KART SON KALİTE RAPORU")
    print("=" * 80)

    t = tag()

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB bulunamadı: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cols = table_columns(cur, "hukuki_kartlar")

    aktif_var = "aktif" in cols
    kalite_etiketi_var = "kalite_etiketi" in cols

    cur.execute("SELECT * FROM hukuki_kartlar")
    all_rows = cur.fetchall()

    if aktif_var:
        cur.execute("SELECT * FROM hukuki_kartlar WHERE COALESCE(aktif,1)=1")
    else:
        cur.execute("SELECT * FROM hukuki_kartlar")

    active_rows = cur.fetchall()

    if aktif_var:
        cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif,1)=0")
        passive_count = cur.fetchone()[0]
    else:
        passive_count = 0

    ready = []
    warning = []
    block = []

    block_counts = {}
    warning_counts = {}
    guven_counts = {}

    title_seen = {}
    duplicate_active_titles = []

    for row in active_rows:
        card = {
            "id": col(row, cols, "id", ""),
            "karar_no": col(row, cols, "karar_no", ""),
            "baslik": col(row, cols, "baslik", ""),
            "hukuki_soru": col(row, cols, "hukuki_soru", ""),
            "sonuc_tipi": col(row, cols, "sonuc_tipi", ""),
            "sonuc": col(row, cols, "sonuc", ""),
            "emsal_ilke": col(row, cols, "emsal_ilke", ""),
            "anahtar": col(row, cols, "anahtar", ""),
            "mevzuat": col(row, cols, "mevzuat", ""),
            "guven": col(row, cols, "guven", ""),
            "kalite_etiketi": col(row, cols, "kalite_etiketi", ""),
            "kaynak_yontem": col(row, cols, "kaynak_yontem", ""),
        }

        g = str(card["guven"] or "").strip()
        guven_counts[g] = guven_counts.get(g, 0) + 1

        key = (str(card["karar_no"]).strip().upper(), n(card["baslik"]))
        if key[0] and key[1]:
            if key in title_seen:
                duplicate_active_titles.append({
                    "karar_no": card["karar_no"],
                    "id1": title_seen[key],
                    "id2": card["id"],
                    "baslik": card["baslik"],
                })
            else:
                title_seen[key] = card["id"]

        level, block_risks, warnings = validate_card(card)

        result = {
            "id": card["id"],
            "karar_no": card["karar_no"],
            "baslik": card["baslik"],
            "sonuc_tipi": card["sonuc_tipi"],
            "guven": card["guven"],
            "quality_level": level,
            "block_riskleri": block_risks,
            "uyarilar": warnings,
            "kalite_etiketi": card["kalite_etiketi"],
            "kaynak_yontem": card["kaynak_yontem"],
        }

        for r in block_risks:
            block_counts[r] = block_counts.get(r, 0) + 1

        for w in warnings:
            warning_counts[w] = warning_counts.get(w, 0) + 1

        if level == "BLOCK":
            block.append(result)
        elif level == "WARNING":
            warning.append(result)
        else:
            ready.append(result)

    total_active = len(active_rows)
    total_all = len(all_rows)
    db_ready = len(ready) + len(warning)
    quality_score = round((db_ready / total_active) * 100, 2) if total_active else 0

    # v3 sertifika:
    # BLOCK yoksa kalite geçer; WARNING veri yayınını engellemez.
    certificate_pass = len(block) == 0 and total_active > 0

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "db_path": DB_PATH,
        "total_cards": total_all,
        "active_cards": total_active,
        "passive_cards": passive_count,
        "ready": len(ready),
        "warning": len(warning),
        "block": len(block),
        "db_ready": db_ready,
        "quality_score": quality_score,
        "certificate_pass": certificate_pass,
        "aktif_kolonu": aktif_var,
        "kalite_etiketi": kalite_etiketi_var,
        "block_counts": block_counts,
        "warning_counts": warning_counts,
        "guven_counts": guven_counts,
        "duplicate_active_titles": len(duplicate_active_titles),
    }

    state_path = os.path.join(STATE_DIR, f"146_v3_aktif_kart_son_kalite_state_{t}.json")
    block_jsonl = os.path.join(RAPOR_DIR, f"146_v3_block_kartlar_{t}.jsonl")
    warning_jsonl = os.path.join(RAPOR_DIR, f"146_v3_warning_kartlar_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"146_v3_aktif_kart_son_kalite_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(block_jsonl, "w", encoding="utf-8") as f:
        for r in block:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(warning_jsonl, "w", encoding="utf-8") as f:
        for r in warning:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("146 v3 - AKTİF KART SON KALİTE RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"Aktif kolonu       : {'VAR' if aktif_var else 'YOK'}\n")
        f.write(f"Kalite etiketi     : {'VAR' if kalite_etiketi_var else 'YOK'}\n\n")

        f.write("TOPLAM KART\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam Kart        : {total_all}\n")
        f.write(f"Aktif Kart         : {total_active}\n")
        f.write(f"Pasif Kart         : {passive_count}\n\n")

        f.write("KALİTE v3\n")
        f.write("-" * 80 + "\n")
        f.write(f"READY              : {len(ready)}\n")
        f.write(f"WARNING            : {len(warning)}\n")
        f.write(f"BLOCK              : {len(block)}\n")
        f.write(f"DB Ready           : {db_ready}\n")
        f.write(f"Aktif mükerrer başlık uyarısı : {len(duplicate_active_titles)}\n")
        f.write(f"Kalite puanı       : {quality_score} / 100\n\n")

        f.write("GÜVEN DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        for k, v in sorted(guven_counts.items(), key=lambda x: str(x[0])):
            f.write(f"{k or 'BOŞ':15}: {v}\n")

        f.write("\nBLOCK RİSK DAĞILIMI\n")
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
                    f"[BLOCK] id={r['id']} karar={r['karar_no']} "
                    f"risk={','.join(r['block_riskleri'])} | {r['baslik']}\n"
                )

        f.write("\nSERTİFİKA\n")
        f.write("-" * 80 + "\n")
        if certificate_pass:
            f.write("✓ WEB yayınına uygun\n")
            f.write("✓ RAG indeksine uygun\n")
            f.write("✓ AI danışman motoruna uygun\n")
            f.write("✓ Arama motoruna uygun\n")
            f.write("✓ Eğitim veri seti olarak uygun\n")
            f.write("\nSONUÇ\n")
            f.write("AKTİF VERİ TABANI v3 KALİTE TESTLERİNİ BAŞARIYLA GEÇMİŞTİR.\n")
        else:
            f.write("✗ Sertifika verilmedi.\n")
            f.write("Aktif kartlarda BLOCK seviyesinde kalite riski bulunmaktadır.\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON          : {state_path}\n")
        f.write(f"Block JSONL         : {block_jsonl}\n")
        f.write(f"Warning JSONL       : {warning_jsonl}\n")
        f.write(f"Rapor               : {rapor_path}\n")

    con.close()

    print("\n146 v3 AKTİF KART KALİTE RAPORU OLUŞTURULDU")
    print("-" * 80)
    print(f"Toplam kart    : {total_all}")
    print(f"Aktif kart     : {total_active}")
    print(f"Pasif kart     : {passive_count}")
    print(f"READY          : {len(ready)}")
    print(f"WARNING        : {len(warning)}")
    print(f"BLOCK          : {len(block)}")
    print(f"Kalite puanı   : {quality_score} / 100")
    print(f"Sertifika      : {'GEÇTİ' if certificate_pass else 'KALDI'}")
    print("\nDosya:")
    print(rapor_path)


if __name__ == "__main__":
    main()