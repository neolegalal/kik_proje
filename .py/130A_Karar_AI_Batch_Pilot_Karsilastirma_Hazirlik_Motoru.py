# -*- coding: utf-8 -*-

import os
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

MODEL = "gpt-4.1-mini"
PILOT_LIMIT = 20

os.makedirs(RAPOR_DIR, exist_ok=True)


def get_columns(cur, table):
    return [r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]


def build_prompt(karar_no, tam_metin):
    return f"""
Sen Kamu İhale Kurulu kararlarını analiz eden uzman bir kamu ihale hukuku asistanısın.

Aşağıdaki KİK karar metnini incele.

Görevin:
1. Karardaki her bağımsız iddiayı ayrı ayrı tespit et.
2. Her iddia için hukuki kart üret.
3. Her kartta şu alanları doldur:
   - iddia_no
   - baslik
   - hukuki_soru
   - iddia_ozeti
   - kurul_degerlendirmesi
   - sonuc
   - emsal_ilke
   - anahtar_kelime
   - mevzuat
   - guven

Sonuç tipi ayrıca çıkar:
- RET
- KABUL
- DÜZELTİCİ İŞLEM
- İPTAL
- KARAR VERİLMESİNE YER OLMADIĞI
- BELİRSİZ

Sadece geçerli JSON döndür.

JSON ŞEMASI:
{{
  "karar_no": "{karar_no}",
  "kartlar": [
    {{
      "iddia_no": 1,
      "baslik": "",
      "hukuki_soru": "",
      "iddia_ozeti": "",
      "kurul_degerlendirmesi": "",
      "sonuc": "",
      "sonuc_tipi": "",
      "emsal_ilke": "",
      "anahtar_kelime": "",
      "mevzuat": "",
      "guven": ""
    }}
  ]
}}

KARAR METNİ:
{tam_metin[:45000]}
""".strip()


def main():
    print("=" * 80)
    print("130A - BATCH PİLOT KARŞILAŞTIRMA HAZIRLIK MOTORU")
    print("=" * 80)

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    karar_cols = get_columns(cur, "kararlar")

    if "tam_metin" not in karar_cols:
        print("HATA: kararlar tablosunda tam_metin sütunu bulunamadı.")
        print("Mevcut sütunlar:")
        for c in karar_cols:
            print("-", c)
        return

    rows = cur.execute("""
        SELECT karar_no, tam_metin
        FROM kararlar
        WHERE tam_metin IS NOT NULL
          AND LENGTH(tam_metin) > 1000
          AND karar_no LIKE '2026/%'
        ORDER BY karar_no
        LIMIT ?
    """, (PILOT_LIMIT,)).fetchall()

    if not rows:
        print("2026 karar bulunamadı. Alternatif olarak tüm kararlardan seçiliyor.")
        rows = cur.execute("""
            SELECT karar_no, tam_metin
            FROM kararlar
            WHERE tam_metin IS NOT NULL
              AND LENGTH(tam_metin) > 1000
            ORDER BY karar_no
            LIMIT ?
        """, (PILOT_LIMIT,)).fetchall()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = os.path.join(RAPOR_DIR, f"130A_batch_pilot_karsilastirma_{ts}.jsonl")
    map_path = os.path.join(RAPOR_DIR, f"130A_batch_pilot_karsilastirma_map_{ts}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"130A_batch_pilot_karsilastirma_rapor_{ts}.txt")

    mapping = {}
    hazir = 0

    with open(jsonl_path, "w", encoding="utf-8") as jf:
        for row in rows:
            karar_no = row["karar_no"]
            tam_metin = row["tam_metin"]

            custom_id = f"pilot_{hazir+1}_{karar_no.replace('/', '_').replace('.', '_').replace('-', '_')}"

            body = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Sen Kamu İhale Kurulu kararlarını analiz eden uzman bir hukuk asistanısın. Sadece geçerli JSON döndür."
                    },
                    {
                        "role": "user",
                        "content": build_prompt(karar_no, tam_metin)
                    }
                ],
                "temperature": 0,
                "response_format": {"type": "json_object"}
            }

            line = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": body
            }

            jf.write(json.dumps(line, ensure_ascii=False) + "\n")

            mapping[custom_id] = {
                "karar_no": karar_no,
                "metin_uzunlugu": len(tam_metin)
            }

            hazir += 1

    with open(map_path, "w", encoding="utf-8") as mf:
        json.dump(mapping, mf, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as rf:
        rf.write("130A - BATCH PİLOT KARŞILAŞTIRMA HAZIRLIK RAPORU\n")
        rf.write("=" * 80 + "\n")
        rf.write(f"Tarih        : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        rf.write(f"Model        : {MODEL}\n")
        rf.write(f"Pilot karar  : {hazir}\n")
        rf.write(f"JSONL        : {jsonl_path}\n")
        rf.write(f"MAP          : {map_path}\n\n")

        for k, v in mapping.items():
            rf.write(f"{k} | {v['karar_no']} | metin: {v['metin_uzunlugu']}\n")

    con.close()

    print("\nHAZIRLIK TAMAMLANDI")
    print("-" * 80)
    print(f"Pilot karar sayısı : {hazir}")
    print(f"JSONL              : {jsonl_path}")
    print(f"MAP                : {map_path}")
    print(f"Rapor              : {rapor_path}")
    print("\nNOT: Bu kod API çağrısı yapmadı, para harcamadı.")


if __name__ == "__main__":
    main()