# -*- coding: utf-8 -*-

import json
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
DB_PATH = BASE_DIR / ".py" / "kik.db"
RAPOR_DIR = BASE_DIR / "raporlar"

BATCH_JSONL = RAPOR_DIR / "133A_batch_sonuc_20260621_184819.jsonl"


def parse_batch_results():
    data = {}

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

        parsed = json.loads(content)
        karar_no = parsed.get("karar_no")
        kartlar = parsed.get("kartlar", [])

        if karar_no:
            data[karar_no] = kartlar

    return data


def fmt_kart(kart, kaynak="DB"):
    if kaynak == "DB":
        return f"""
İddia No      : {kart.get('iddia_no', '')}
Başlık        : {kart.get('baslik', '')}
Hukuki Soru   : {kart.get('hukuki_soru', '')}
Sonuç Tipi    : {kart.get('sonuc_tipi', '')}
Sonuç         : {kart.get('sonuc', '')}
Emsal İlke    : {kart.get('emsal_ilke', '')}
Anahtar       : {kart.get('anahtar_kelime', '')}
Güven         : {kart.get('guven', '')}
Konu Doğrulama: {kart.get('konu_dogrulama', '')}
Şüpheli       : {kart.get('supheli_kart', '')}
""".strip()

    return f"""
İddia No      : {kart.get('iddia_no', '')}
Başlık        : {kart.get('baslik', '')}
Hukuki Soru   : {kart.get('hukuki_soru', '')}
Sonuç Tipi    : {kart.get('sonuc_tipi', '')}
Sonuç         : {kart.get('sonuc', '')}
Emsal İlke    : {kart.get('emsal_ilke', '')}
Anahtar       : {kart.get('anahtar_kelime', '')}
Mevzuat       : {kart.get('mevzuat', '')}
Güven         : {kart.get('guven', '')}
""".strip()


def main():
    print("=" * 80)
    print("136A - BATCH İNSAN GÖZÜ KARŞILAŞTIRMA RAPORU")
    print("=" * 80)

    if not BATCH_JSONL.exists():
        print("Batch sonuç dosyası bulunamadı:")
        print(BATCH_JSONL)
        return

    batch_data = parse_batch_results()

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapor_path = RAPOR_DIR / f"136A_batch_insan_gozu_karsilastirma_{ts}.txt"

    toplam_karar = 0
    toplam_db_kart = 0
    toplam_batch_kart = 0

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("136A - BATCH İNSAN GÖZÜ KARŞILAŞTIRMA RAPORU\n")
        f.write("=" * 100 + "\n")
        f.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Batch JSONL: {BATCH_JSONL}\n\n")

        for karar_no, batch_kartlar in batch_data.items():
            db_rows = cur.execute("""
                SELECT
                    iddia_no,
                    baslik,
                    hukuki_soru,
                    sonuc,
                    emsal_ilke,
                    anahtar_kelime,
                    guven,
                    sonuc_tipi,
                    konu_dogrulama,
                    supheli_kart
                FROM hukuki_kartlar
                WHERE karar_no=?
                ORDER BY iddia_no
            """, (karar_no,)).fetchall()

            db_kartlar = [dict(r) for r in db_rows]

            toplam_karar += 1
            toplam_db_kart += len(db_kartlar)
            toplam_batch_kart += len(batch_kartlar)

            f.write("\n" + "=" * 100 + "\n")
            f.write(f"KARAR NO: {karar_no}\n")
            f.write(f"1. YÖNTEM DB KART SAYISI    : {len(db_kartlar)}\n")
            f.write(f"2. YÖNTEM BATCH KART SAYISI : {len(batch_kartlar)}\n")
            f.write("=" * 100 + "\n\n")

            f.write("### 1. YÖNTEM / STANDART API / DB KARTLARI\n")
            f.write("-" * 100 + "\n")

            if not db_kartlar:
                f.write("DB kartı bulunamadı.\n")
            else:
                for i, kart in enumerate(db_kartlar, 1):
                    f.write(f"\n[DB KART {i}]\n")
                    f.write(fmt_kart(kart, "DB"))
                    f.write("\n")

            f.write("\n\n### 2. YÖNTEM / BATCH API KARTLARI\n")
            f.write("-" * 100 + "\n")

            if not batch_kartlar:
                f.write("Batch kartı bulunamadı.\n")
            else:
                for i, kart in enumerate(batch_kartlar, 1):
                    f.write(f"\n[BATCH KART {i}]\n")
                    f.write(fmt_kart(kart, "BATCH"))
                    f.write("\n")

            f.write("\n\n### İNSAN DEĞERLENDİRME NOTU\n")
            f.write("-" * 100 + "\n")
            f.write("Bu karar için kontrol edilecekler:\n")
            f.write("1) Batch fazla kart üretmişse bunlar gerçekten ayrı iddia mı?\n")
            f.write("2) DB kartlarından eksik olan var mı?\n")
            f.write("3) Hukuki soru daha doğru/hukuki mi?\n")
            f.write("4) Sonuç tipi doğru mu?\n")
            f.write("5) Emsal ilke karar metnini doğru temsil ediyor mu?\n")
            f.write("\n")

        f.write("\n" + "=" * 100 + "\n")
        f.write("GENEL ÖZET\n")
        f.write("=" * 100 + "\n")
        f.write(f"Karar sayısı           : {toplam_karar}\n")
        f.write(f"DB toplam kart         : {toplam_db_kart}\n")
        f.write(f"Batch toplam kart      : {toplam_batch_kart}\n")
        if toplam_karar:
            f.write(f"DB ortalama kart/karar : {round(toplam_db_kart / toplam_karar, 2)}\n")
            f.write(f"Batch ortalama kart    : {round(toplam_batch_kart / toplam_karar, 2)}\n")

    con.close()

    print("\nRAPOR OLUŞTURULDU")
    print("-" * 80)
    print(f"Karar sayısı      : {toplam_karar}")
    print(f"DB kart sayısı    : {toplam_db_kart}")
    print(f"Batch kart sayısı : {toplam_batch_kart}")
    print("\nRapor:")
    print(rapor_path)


if __name__ == "__main__":
    main()