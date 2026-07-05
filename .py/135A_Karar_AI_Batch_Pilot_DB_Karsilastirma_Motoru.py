# -*- coding: utf-8 -*-

import json
import sqlite3
import csv
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
DB_PATH = BASE_DIR / ".py" / "kik.db"
RAPOR_DIR = BASE_DIR / "raporlar"

BATCH_JSONL = RAPOR_DIR / "133A_batch_sonuc_20260621_184819.jsonl"


def sim(a, b):
    a = (a or "").strip().lower()
    b = (b or "").strip().lower()
    if not a and not b:
        return 100
    if not a or not b:
        return 0
    return round(SequenceMatcher(None, a, b).ratio() * 100, 1)


def parse_batch():
    results = {}

    for line in BATCH_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        obj = json.loads(line)
        content = (
            obj.get("response", {})
            .get("body", {})
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        data = json.loads(content)
        karar_no = data.get("karar_no")
        kartlar = data.get("kartlar", [])

        if karar_no:
            results[karar_no] = kartlar

    return results


def main():
    print("=" * 80)
    print("135A - BATCH PİLOT DB KARŞILAŞTIRMA MOTORU")
    print("=" * 80)

    if not BATCH_JSONL.exists():
        print("Batch sonuç dosyası bulunamadı:")
        print(BATCH_JSONL)
        return

    batch_data = parse_batch()

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    rows_out = []
    toplam_karar = 0
    toplam_db_kart = 0
    toplam_batch_kart = 0
    skorlar = []

    for karar_no, batch_kartlar in batch_data.items():
        db_kartlar = cur.execute("""
            SELECT
                iddia_no,
                baslik,
                hukuki_soru,
                sonuc,
                emsal_ilke,
                anahtar_kelime,
                sonuc_tipi,
                konu_dogrulama,
                supheli_kart
            FROM hukuki_kartlar
            WHERE karar_no=?
            ORDER BY iddia_no
        """, (karar_no,)).fetchall()

        toplam_karar += 1
        toplam_db_kart += len(db_kartlar)
        toplam_batch_kart += len(batch_kartlar)

        max_len = max(len(db_kartlar), len(batch_kartlar))

        for i in range(max_len):
            db = dict(db_kartlar[i]) if i < len(db_kartlar) else {}
            bt = batch_kartlar[i] if i < len(batch_kartlar) else {}

            soru_skor = sim(db.get("hukuki_soru"), bt.get("hukuki_soru"))
            sonuc_skor = sim(db.get("sonuc"), bt.get("sonuc"))
            ilke_skor = sim(db.get("emsal_ilke"), bt.get("emsal_ilke"))
            anahtar_skor = sim(db.get("anahtar_kelime"), bt.get("anahtar_kelime"))

            ort = round((soru_skor + sonuc_skor + ilke_skor + anahtar_skor) / 4, 1)
            skorlar.append(ort)

            rows_out.append({
                "karar_no": karar_no,
                "sira": i + 1,
                "db_iddia_no": db.get("iddia_no", ""),
                "batch_iddia_no": bt.get("iddia_no", ""),
                "db_sonuc_tipi": db.get("sonuc_tipi", ""),
                "batch_sonuc_tipi": bt.get("sonuc_tipi", ""),
                "db_konu_dogrulama": db.get("konu_dogrulama", ""),
                "db_supheli": db.get("supheli_kart", ""),
                "soru_skor": soru_skor,
                "sonuc_skor": sonuc_skor,
                "ilke_skor": ilke_skor,
                "anahtar_skor": anahtar_skor,
                "ortalama_skor": ort,
                "db_hukuki_soru": db.get("hukuki_soru", ""),
                "batch_hukuki_soru": bt.get("hukuki_soru", ""),
                "db_sonuc": db.get("sonuc", ""),
                "batch_sonuc": bt.get("sonuc", ""),
                "db_ilke": db.get("emsal_ilke", ""),
                "batch_ilke": bt.get("emsal_ilke", ""),
                "db_anahtar": db.get("anahtar_kelime", ""),
                "batch_anahtar": bt.get("anahtar_kelime", ""),
            })

    con.close()

    genel_skor = round(sum(skorlar) / len(skorlar), 1) if skorlar else 0

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = RAPOR_DIR / f"135A_batch_db_karsilastirma_{ts}.csv"
    txt_path = RAPOR_DIR / f"135A_batch_db_karsilastirma_ozet_{ts}.txt"

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        writer.writeheader()
        writer.writerows(rows_out)

    dusukler = [r for r in rows_out if r["ortalama_skor"] < 70]
    yuksekler = [r for r in rows_out if r["ortalama_skor"] >= 85]

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("135A - BATCH PİLOT DB KARŞILAŞTIRMA ÖZETİ\n")
        f.write("=" * 80 + "\n")
        f.write(f"Tarih                 : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Karar sayısı           : {toplam_karar}\n")
        f.write(f"DB kart sayısı         : {toplam_db_kart}\n")
        f.write(f"Batch kart sayısı      : {toplam_batch_kart}\n")
        f.write(f"Genel benzerlik skoru  : {genel_skor}\n")
        f.write(f"Skor >= 85             : {len(yuksekler)}\n")
        f.write(f"Skor < 70              : {len(dusukler)}\n")
        f.write("\n")
        f.write(f"CSV rapor              : {csv_path}\n")

        f.write("\nDÜŞÜK SKORLU İLK 20 KAYIT\n")
        f.write("-" * 80 + "\n")
        for r in dusukler[:20]:
            f.write(
                f"{r['karar_no']} | sıra {r['sira']} | skor {r['ortalama_skor']} | "
                f"DB: {r['db_hukuki_soru']} | BATCH: {r['batch_hukuki_soru']}\n"
            )

    print("\nKARŞILAŞTIRMA ÖZETİ")
    print("-" * 80)
    print(f"Karar sayısı          : {toplam_karar}")
    print(f"DB kart sayısı        : {toplam_db_kart}")
    print(f"Batch kart sayısı     : {toplam_batch_kart}")
    print(f"Genel benzerlik skoru : {genel_skor}")
    print(f"Skor >= 85            : {len(yuksekler)}")
    print(f"Skor < 70             : {len(dusukler)}")

    print("\nRaporlar:")
    print(csv_path)
    print(txt_path)


if __name__ == "__main__":
    main()