# -*- coding: utf-8 -*-
"""
151 - AKTİF KART RAG / WEB EXPORT MOTORU

Amaç:
- kik.db içindeki aktif=1 hukuki kartları dışa aktarır.
- Web için CSV + JSONL üretir.
- RAG / AI danışman için temiz JSONL üretir.
- Pasif kartları export etmez.
"""

import os
import csv
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
EXPORT_DIR = os.path.join(BASE_DIR, "export")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def clean(v):
    if v is None:
        return ""
    return str(v).strip()


def get_columns(cur):
    cur.execute("PRAGMA table_info(hukuki_kartlar)")
    return [r[1] for r in cur.fetchall()]


def col_exists(cols, name):
    return name in cols


def main():
    print("=" * 80)
    print("151 - AKTİF KART RAG / WEB EXPORT MOTORU")
    print("=" * 80)

    t = tag()

    web_csv = os.path.join(EXPORT_DIR, f"151_web_aktif_kartlar_{t}.csv")
    web_jsonl = os.path.join(EXPORT_DIR, f"151_web_aktif_kartlar_{t}.jsonl")
    rag_jsonl = os.path.join(EXPORT_DIR, f"151_rag_aktif_kartlar_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"151_aktif_kart_rag_web_export_raporu_{t}.txt")

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cols = get_columns(cur)

    aktif_where = "COALESCE(aktif,1)=1" if col_exists(cols, "aktif") else "1=1"

    cur.execute(f"""
        SELECT *
        FROM hukuki_kartlar
        WHERE {aktif_where}
        ORDER BY karar_no, id
    """)

    rows = cur.fetchall()
    con.close()

    export_rows = []

    for r in rows:
        item = {
            "kart_id": r["id"] if "id" in r.keys() else "",
            "karar_no": clean(r["karar_no"]) if "karar_no" in r.keys() else "",
            "baslik": clean(r["baslik"]) if "baslik" in r.keys() else "",
            "hukuki_soru": clean(r["hukuki_soru"]) if "hukuki_soru" in r.keys() else "",
            "sonuc_tipi": clean(r["sonuc_tipi"]) if "sonuc_tipi" in r.keys() else "",
            "sonuc": clean(r["sonuc"]) if "sonuc" in r.keys() else "",
            "emsal_ilke": clean(r["emsal_ilke"]) if "emsal_ilke" in r.keys() else "",
            "anahtar": clean(r["anahtar"]) if "anahtar" in r.keys() else "",
            "mevzuat": clean(r["mevzuat"]) if "mevzuat" in r.keys() else "",
            "guven": clean(r["guven"]) if "guven" in r.keys() else "",
            "kaynak_yontem": clean(r["kaynak_yontem"]) if "kaynak_yontem" in r.keys() else "",
        }

        item["rag_text"] = (
            f"Karar No: {item['karar_no']}\n"
            f"Başlık: {item['baslik']}\n"
            f"Hukuki Soru: {item['hukuki_soru']}\n"
            f"Sonuç Tipi: {item['sonuc_tipi']}\n"
            f"Sonuç: {item['sonuc']}\n"
            f"Emsal İlke: {item['emsal_ilke']}\n"
            f"Mevzuat: {item['mevzuat']}\n"
            f"Anahtar Kelimeler: {item['anahtar']}"
        ).strip()

        export_rows.append(item)

    fieldnames = [
        "kart_id",
        "karar_no",
        "baslik",
        "hukuki_soru",
        "sonuc_tipi",
        "sonuc",
        "emsal_ilke",
        "anahtar",
        "mevzuat",
        "guven",
        "kaynak_yontem",
    ]

    with open(web_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in export_rows:
            writer.writerow({k: item.get(k, "") for k in fieldnames})

    with open(web_jsonl, "w", encoding="utf-8") as f:
        for item in export_rows:
            f.write(json.dumps({k: item.get(k, "") for k in fieldnames}, ensure_ascii=False) + "\n")

    with open(rag_jsonl, "w", encoding="utf-8") as f:
        for item in export_rows:
            rag_item = {
                "id": f"kik_kart_{item['kart_id']}",
                "karar_no": item["karar_no"],
                "title": item["baslik"],
                "text": item["rag_text"],
                "metadata": {
                    "kart_id": item["kart_id"],
                    "karar_no": item["karar_no"],
                    "sonuc_tipi": item["sonuc_tipi"],
                    "guven": item["guven"],
                    "kaynak_yontem": item["kaynak_yontem"],
                    "anahtar": item["anahtar"],
                    "mevzuat": item["mevzuat"],
                }
            }
            f.write(json.dumps(rag_item, ensure_ascii=False) + "\n")

    karar_sayisi = len(set(x["karar_no"] for x in export_rows if x["karar_no"]))

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("151 - AKTİF KART RAG / WEB EXPORT RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih       : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB          : {DB_PATH}\n")
        f.write(f"Aktif kart  : {len(export_rows)}\n")
        f.write(f"Karar sayısı: {karar_sayisi}\n\n")
        f.write("DOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Web CSV     : {web_csv}\n")
        f.write(f"Web JSONL   : {web_jsonl}\n")
        f.write(f"RAG JSONL   : {rag_jsonl}\n")

    print("\nEXPORT TAMAMLANDI")
    print("-" * 80)
    print(f"Aktif kart  : {len(export_rows)}")
    print(f"Karar sayısı: {karar_sayisi}")
    print("\nDosyalar:")
    print(web_csv)
    print(web_jsonl)
    print(rag_jsonl)
    print(rapor_path)


if __name__ == "__main__":
    main()