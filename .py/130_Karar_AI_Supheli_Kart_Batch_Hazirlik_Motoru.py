# -*- coding: utf-8 -*-

import os
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

MODEL = "gpt-4.1-mini"
PILOT_LIMIT = 20  # İlk Batch pilotu için 20 kart. Sonra 50 yaparız.

os.makedirs(RAPOR_DIR, exist_ok=True)


TEXT_COLUMN_CANDIDATES = [
    "tam_metin", "karar_metni", "metin", "pdf_metin", "ham_metin",
    "icerik", "karar_text", "full_text", "text", "extracted_text"
]


def table_columns(cur, table_name):
    return [r[1] for r in cur.execute(f"PRAGMA table_info({table_name})").fetchall()]


def find_text_source(cur):
    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    sources = []

    for (table,) in tables:
        cols = table_columns(cur, table)

        if "karar_no" not in cols:
            continue

        for col in cols:
            if col.lower() in TEXT_COLUMN_CANDIDATES:
                sources.append((table, col))

    return sources


def get_decision_text(cur, karar_no, sources):
    for table, text_col in sources:
        try:
            row = cur.execute(
                f"SELECT {text_col} FROM {table} WHERE karar_no=? LIMIT 1",
                (karar_no,)
            ).fetchone()

            if row and row[0] and len(str(row[0]).strip()) > 500:
                return str(row[0])
        except Exception:
            pass

    return ""


def build_prompt(card, karar_metni):
    return f"""
Sen kamu ihale hukuku uzmanı gibi davran.

Aşağıdaki HUKUKİ KART ile ORİJİNAL KİK KARAR METNİNİ karşılaştır.

Görevin:
1. Kartın karar metniyle uyumlu olup olmadığını denetle.
2. Kart tamamen hatalıysa doğru kartı yeniden üret.
3. Konu doğru ama sonuç/ilke eksikse düzelt.
4. Sonuç tipini belirle.

SONUÇ TİPİ seçenekleri:
- RET
- KABUL
- DÜZELTİCİ İŞLEM
- İPTAL
- KARAR VERİLMESİNE YER OLMADIĞI
- BELİRSİZ

UYUM DURUMU seçenekleri:
- DUZGUN
- KISMEN_HATALI
- TAMAMEN_HATALI

Sadece geçerli JSON döndür.

JSON ŞEMASI:
{{
  "uyum_durumu": "",
  "duzeltme_gerekli": true,
  "karar_no": "",
  "iddia_no": 0,
  "yeni_baslik": "",
  "yeni_hukuki_soru": "",
  "yeni_sonuc": "",
  "yeni_emsal_ilke": "",
  "yeni_anahtar_kelime": "",
  "sonuc_tipi": "",
  "gerekce": ""
}}

HUKUKİ KART:
Karar No: {card["karar_no"]}
İddia No: {card["iddia_no"]}
Başlık: {card["baslik"]}
Hukuki Soru: {card["hukuki_soru"]}
Sonuç: {card["sonuc"]}
Emsal İlke: {card["emsal_ilke"]}
Anahtar Kelime: {card["anahtar_kelime"]}
Güven: {card["guven"]}
Konu Doğrulama: {card["konu_dogrulama"]}
Şüpheli Kart: {card["supheli_kart"]}

ORİJİNAL KARAR METNİ:
{karar_metni[:45000]}
""".strip()


def main():
    print("=" * 80)
    print("130 - KİK KARAR AI ŞÜPHELİ KART BATCH HAZIRLIK MOTORU")
    print("=" * 80)

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    sources = find_text_source(cur)

    print("\nMetin kaynağı adayları:")
    if sources:
        for t, c in sources:
            print(f"- {t}.{c}")
    else:
        print("UYARI: karar_no + metin içeren tablo/sütun otomatik bulunamadı.")

    rows = cur.execute("""
        SELECT
            id,
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            sonuc,
            emsal_ilke,
            anahtar_kelime,
            guven,
            konu_dogrulama,
            konu_kalite_puani,
            supheli_kart
        FROM hukuki_kartlar
        WHERE supheli_kart='EVET'
        ORDER BY karar_no, iddia_no
        LIMIT ?
    """, (PILOT_LIMIT,)).fetchall()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = os.path.join(RAPOR_DIR, f"130_supheli_kart_batch_pilot_{ts}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"130_supheli_kart_batch_hazirlik_raporu_{ts}.txt")

    hazir = 0
    eksik_metin = 0

    with open(jsonl_path, "w", encoding="utf-8") as jf, open(rapor_path, "w", encoding="utf-8") as rf:
        rf.write("130 - ŞÜPHELİ KART BATCH HAZIRLIK RAPORU\n")
        rf.write("=" * 80 + "\n")
        rf.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        rf.write(f"Pilot limit: {PILOT_LIMIT}\n\n")

        for r in rows:
            card = dict(r)
            karar_no = card["karar_no"]
            karar_metni = get_decision_text(cur, karar_no, sources)

            if not karar_metni:
                eksik_metin += 1
                rf.write(f"EKSİK METİN | Kart ID: {card['id']} | Karar No: {karar_no}\n")
                continue

            prompt = build_prompt(card, karar_metni)

            body = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Sen Kamu İhale Kurulu kararlarını analiz eden uzman bir hukuk asistanısın. Sadece geçerli JSON döndür."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"}
            }

            line = {
                "custom_id": f"kart_{card['id']}_{karar_no.replace('/', '_')}_iddia_{card['iddia_no']}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": body
            }

            jf.write(json.dumps(line, ensure_ascii=False) + "\n")
            hazir += 1
            rf.write(f"HAZIR | Kart ID: {card['id']} | Karar No: {karar_no} | İddia: {card['iddia_no']}\n")

    con.close()

    print("\n" + "-" * 80)
    print("HAZIRLIK ÖZETİ")
    print("-" * 80)
    print(f"Şüpheli kart pilot limiti : {PILOT_LIMIT}")
    print(f"Batch için hazırlanan     : {hazir}")
    print(f"Karar metni bulunamayan   : {eksik_metin}")
    print("\nOluşturulan dosyalar:")
    print(jsonl_path)
    print(rapor_path)

    print("\nNOT:")
    print("Bu kod API çağrısı yapmadı, para harcamadı.")
    print("Sadece Batch API için JSONL hazırladı.")


if __name__ == "__main__":
    main()