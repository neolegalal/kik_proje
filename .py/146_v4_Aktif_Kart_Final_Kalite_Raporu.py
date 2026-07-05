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

VALID_GUVEN = {"Yüksek", "Orta", "Düşük"}

VALID_SONUC_NORMALIZED = {
    "KABUL",
    "RET",
    "DUZELTICI_ISLEM",
    "IPTAL",
    "KARAR_VERILMESINE_YER_OLMADIGI",
    "DIGER",
    "KISMEN_KABUL",
    "KISMEN_RET",
    "INCELEME_DISI",
    "GOREV_YONUNDEN_RET",
    "SURE_YONUNDEN_RET",
    "ESASTAN_RET",
    "USULDEN_RET",
    "BASVURUNUN_REDDI",
    "BASVURU_REDDI",
    "IDDIA_YERINDE",
    "IDDIA_YERINDE_DEGIL",
    "KARAR",
    "DEGERLENDIRME",
}

COLUMN_ALIASES = {
    "id": ["id", "kart_id"],
    "karar_no": ["karar_no", "karar", "kurul_karar_no"],
    "baslik": ["baslik", "başlık", "kart_baslik", "hukuki_baslik", "soru_basligi"],
    "hukuki_soru": ["hukuki_soru", "soru", "karar_sorusu", "hukuki_soru_basligi", "soru_basligi"],
    "sonuc_tipi": ["sonuc_tipi", "sonuç_tipi", "karar_sonucu", "sonuc_kodu", "tip"],
    "sonuc": ["sonuc", "sonuç", "karar_sonucu_metni", "sonuc_ozeti", "sonuç_özeti"],
    "emsal_ilke": ["emsal_ilke", "ilke", "emsal", "hukuki_ilke", "karar_ilkesi"],
    "anahtar": ["anahtar", "anahtar_kelimeler", "etiketler", "keywords"],
    "mevzuat": ["mevzuat", "yasal_dayanak", "dayanak", "ilgili_mevzuat"],
    "guven": ["guven", "güven", "guven_seviyesi", "güven_seviyesi"],
    "aktif": ["aktif", "is_active"],
    "kalite_etiketi": ["kalite_etiketi", "quality_level", "quality_label"],
    "kalite_notu": ["kalite_notu", "quality_note"],
    "kaynak_yontem": ["kaynak_yontem", "kaynak_yöntem", "source_method"],
    "created_at": ["created_at", "olusturma_tarihi", "created"],
}


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def n(x):
    return re.sub(r"\s+", " ", str(x or "").strip().lower())


def blank(x):
    return not str(x or "").strip()


def tr_upper_ascii(x):
    s = str(x or "").strip()
    tr_map = str.maketrans({
        "ı": "i", "İ": "i", "ğ": "g", "Ğ": "g",
        "ü": "u", "Ü": "u", "ş": "s", "Ş": "s",
        "ö": "o", "Ö": "o", "ç": "c", "Ç": "c",
    })
    s = s.translate(tr_map)
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def normalize_sonuc_tipi(x):
    raw = str(x or "").strip()
    u = tr_upper_ascii(raw)

    mapping = {
        "DÜZELTİCİ İŞLEM": "DUZELTICI_ISLEM",
        "DUZELTICI_ISLEM": "DUZELTICI_ISLEM",
        "DÜZELTICI ISLEM": "DUZELTICI_ISLEM",
        "DÜZELTİCİ": "DUZELTICI_ISLEM",
        "DUZELTICI": "DUZELTICI_ISLEM",
        "KARAR VERİLMESİNE YER OLMADIĞI": "KARAR_VERILMESINE_YER_OLMADIGI",
        "KARAR VERILMESINE YER OLMADIGI": "KARAR_VERILMESINE_YER_OLMADIGI",
        "KARAR_VERILMESINE_YER_OLMADIGI": "KARAR_VERILMESINE_YER_OLMADIGI",
        "DİĞER": "DIGER",
        "DIGER": "DIGER",
        "RET": "RET",
        "RED": "RET",
        "REDDI": "RET",
        "REDDİ": "RET",
        "KABUL": "KABUL",
        "İPTAL": "IPTAL",
        "IPTAL": "IPTAL",
    }

    if raw in mapping:
        return mapping[raw]

    if u in mapping:
        return mapping[u]

    if "DUZELTICI" in u:
        return "DUZELTICI_ISLEM"
    if "YER_OLMAD" in u:
        return "KARAR_VERILMESINE_YER_OLMADIGI"
    if "KISMEN" in u and "KABUL" in u:
        return "KISMEN_KABUL"
    if "KISMEN" in u and ("RET" in u or "RED" in u):
        return "KISMEN_RET"
    if "GOREV" in u and ("RET" in u or "RED" in u):
        return "GOREV_YONUNDEN_RET"
    if "SURE" in u and ("RET" in u or "RED" in u):
        return "SURE_YONUNDEN_RET"
    if "BASVURU" in u and ("RET" in u or "RED" in u):
        return "BASVURU_REDDI"
    if "YERINDE_DEGIL" in u:
        return "IDDIA_YERINDE_DEGIL"
    if "YERINDE" in u:
        return "IDDIA_YERINDE"

    return u


def table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def resolve_columns(cols):
    lower_map = {c.lower(): c for c in cols}
    resolved = {}

    for logical, aliases in COLUMN_ALIASES.items():
        found = None
        for a in aliases:
            if a.lower() in lower_map:
                found = lower_map[a.lower()]
                break
        resolved[logical] = found

    return resolved


def get_value(row_dict, resolved, logical, default=""):
    real_col = resolved.get(logical)
    if not real_col:
        return default
    return row_dict.get(real_col, default)


def contains_any(text, words):
    text = n(text)
    return any(w in text for w in words)


def semantic_warning(sonuc_tipi_raw, sonuc):
    st = normalize_sonuc_tipi(sonuc_tipi_raw)
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

    if st in {"RET", "BASVURU_REDDI", "ESASTAN_RET", "USULDEN_RET", "GOREV_YONUNDEN_RET", "SURE_YONUNDEN_RET"}:
        return contains_any(s, kabul_like)

    if st in {"KABUL", "DUZELTICI_ISLEM", "IPTAL", "KISMEN_KABUL"}:
        return contains_any(s, ret_like)

    return False


def validate_card(card):
    block = []
    warning = []

    sonuc_norm = normalize_sonuc_tipi(card["sonuc_tipi"])

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
        warning.append("BOS_SONUC_TIPI")
    elif sonuc_norm not in VALID_SONUC_NORMALIZED:
        warning.append("SONUC_TIPI_TANIMSIZ_WARNING")

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

    return level, block, warning, sonuc_norm


def main():
    print("=" * 80)
    print("146 v4 - AKTİF KART FINAL KALİTE RAPORU")
    print("=" * 80)

    t = tag()

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB bulunamadı: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cols = table_columns(cur, "hukuki_kartlar")
    resolved = resolve_columns(cols)

    aktif_col = resolved.get("aktif")
    kalite_etiketi_col = resolved.get("kalite_etiketi")

    cur.execute("SELECT * FROM hukuki_kartlar")
    all_rows = cur.fetchall()

    if aktif_col:
        cur.execute(f"SELECT * FROM hukuki_kartlar WHERE COALESCE({aktif_col},1)=1")
    else:
        cur.execute("SELECT * FROM hukuki_kartlar")

    active_rows = cur.fetchall()

    if aktif_col:
        cur.execute(f"SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE({aktif_col},1)=0")
        passive_count = cur.fetchone()[0]
    else:
        passive_count = 0

    ready = []
    warning = []
    block = []

    block_counts = {}
    warning_counts = {}
    guven_counts = {}
    sonuc_counts = {}
    kaynak_counts = {}

    title_seen = {}
    duplicate_active_titles = []

    for row in active_rows:
        row_dict = dict(row)

        card = {
            "id": get_value(row_dict, resolved, "id"),
            "karar_no": get_value(row_dict, resolved, "karar_no"),
            "baslik": get_value(row_dict, resolved, "baslik"),
            "hukuki_soru": get_value(row_dict, resolved, "hukuki_soru"),
            "sonuc_tipi": get_value(row_dict, resolved, "sonuc_tipi"),
            "sonuc": get_value(row_dict, resolved, "sonuc"),
            "emsal_ilke": get_value(row_dict, resolved, "emsal_ilke"),
            "anahtar": get_value(row_dict, resolved, "anahtar"),
            "mevzuat": get_value(row_dict, resolved, "mevzuat"),
            "guven": get_value(row_dict, resolved, "guven"),
            "kalite_etiketi": get_value(row_dict, resolved, "kalite_etiketi"),
            "kalite_notu": get_value(row_dict, resolved, "kalite_notu"),
            "kaynak_yontem": get_value(row_dict, resolved, "kaynak_yontem"),
        }

        sonuc_norm = normalize_sonuc_tipi(card["sonuc_tipi"])

        g = str(card["guven"] or "").strip()
        guven_counts[g or "BOŞ"] = guven_counts.get(g or "BOŞ", 0) + 1
        sonuc_counts[sonuc_norm or "BOŞ"] = sonuc_counts.get(sonuc_norm or "BOŞ", 0) + 1

        kaynak = str(card["kaynak_yontem"] or "").strip()
        kaynak_counts[kaynak or "BOŞ"] = kaynak_counts.get(kaynak or "BOŞ", 0) + 1

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

        level, block_risks, warnings, sonuc_norm = validate_card(card)

        if duplicate_active_titles and key in title_seen:
            pass

        result = {
            "id": card["id"],
            "karar_no": card["karar_no"],
            "baslik": card["baslik"],
            "sonuc_tipi": card["sonuc_tipi"],
            "sonuc_tipi_norm": sonuc_norm,
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
        "columns": cols,
        "resolved_columns": resolved,
        "block_counts": block_counts,
        "warning_counts": warning_counts,
        "guven_counts": guven_counts,
        "sonuc_counts": sonuc_counts,
        "kaynak_counts": kaynak_counts,
        "duplicate_active_titles": len(duplicate_active_titles),
    }

    state_path = os.path.join(STATE_DIR, f"146_v4_aktif_kart_final_kalite_state_{t}.json")
    block_jsonl = os.path.join(RAPOR_DIR, f"146_v4_block_kartlar_{t}.jsonl")
    warning_jsonl = os.path.join(RAPOR_DIR, f"146_v4_warning_kartlar_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"146_v4_aktif_kart_final_kalite_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(block_jsonl, "w", encoding="utf-8") as f:
        for r in block:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(warning_jsonl, "w", encoding="utf-8") as f:
        for r in warning:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("146 v4 - AKTİF KART FINAL KALİTE RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"Aktif kolonu       : {'VAR' if aktif_col else 'YOK'}\n")
        f.write(f"Kalite etiketi     : {'VAR' if kalite_etiketi_col else 'YOK'}\n\n")

        f.write("KOLON EŞLEŞTİRME\n")
        f.write("-" * 80 + "\n")
        for k, v in resolved.items():
            f.write(f"{k:20}: {v or 'YOK'}\n")

        f.write("\nTOPLAM KART\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam Kart        : {total_all}\n")
        f.write(f"Aktif Kart         : {total_active}\n")
        f.write(f"Pasif Kart         : {passive_count}\n\n")

        f.write("KALİTE v4\n")
        f.write("-" * 80 + "\n")
        f.write(f"READY              : {len(ready)}\n")
        f.write(f"WARNING            : {len(warning)}\n")
        f.write(f"BLOCK              : {len(block)}\n")
        f.write(f"DB Ready           : {db_ready}\n")
        f.write(f"Aktif mükerrer başlık uyarısı : {len(duplicate_active_titles)}\n")
        f.write(f"Kalite puanı       : {quality_score} / 100\n\n")

        f.write("KAYNAK DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        for k, v in sorted(kaynak_counts.items(), key=lambda x: (-x[1], str(x[0]))):
            f.write(f"{k:35}: {v}\n")

        f.write("\nSONUÇ TİPİ DAĞILIMI normalize\n")
        f.write("-" * 80 + "\n")
        for k, v in sorted(sonuc_counts.items(), key=lambda x: (-x[1], str(x[0]))):
            f.write(f"{k:35}: {v}\n")

        f.write("\nGÜVEN DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        for k, v in sorted(guven_counts.items(), key=lambda x: str(x[0])):
            f.write(f"{k:15}: {v}\n")

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
            f.write("AKTİF VERİ TABANI v4 FINAL KALİTE TESTLERİNİ BAŞARIYLA GEÇMİŞTİR.\n")
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

    print("\n146 v4 AKTİF KART FINAL KALİTE RAPORU OLUŞTURULDU")
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