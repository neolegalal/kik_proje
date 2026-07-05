# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
DB_PATH = BASE_DIR / ".py" / "kik.db"
RAPOR_DIR = BASE_DIR / "raporlar"
RAPOR_DIR.mkdir(exist_ok=True)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
rapor = RAPOR_DIR / f"138_batch_db_son_kalite_kontrol_{ts}.txt"

con = sqlite3.connect(DB_PATH)
cur = con.cursor()

rows = cur.execute("""
SELECT
    karar_no,
    iddia_no,
    baslik,
    hukuki_soru,
    sonuc_tipi,
    sonuc,
    emsal_ilke,
    anahtar_kelime,
    mevzuat,
    guven,
    kaynak_yontem
FROM hukuki_kartlar
WHERE kaynak_yontem = 'BATCH_136E'
ORDER BY karar_no, iddia_no
""").fetchall()

kararlar = {}
for r in rows:
    kararlar.setdefault(r[0], []).append(r)

with open(rapor, "w", encoding="utf-8") as f:
    f.write("138 - BATCH DB SON KALİTE KONTROL RAPORU\n")
    f.write("=" * 100 + "\n")
    f.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
    f.write(f"DB: {DB_PATH}\n\n")
    f.write("GENEL ÖZET\n")
    f.write("-" * 100 + "\n")
    f.write(f"Karar sayısı : {len(kararlar)}\n")
    f.write(f"Kart sayısı  : {len(rows)}\n\n")

    for karar_no, kartlar in kararlar.items():
        f.write("=" * 100 + "\n")
        f.write(f"KARAR NO: {karar_no} | Kart sayısı: {len(kartlar)}\n")
        f.write("=" * 100 + "\n\n")

        for r in kartlar:
            (
                karar_no, iddia_no, baslik, hukuki_soru, sonuc_tipi,
                sonuc, emsal_ilke, anahtar, mevzuat, guven, kaynak
            ) = r

            f.write(f"[KART {iddia_no}]\n")
            f.write(f"Başlık      : {baslik}\n")
            f.write(f"Hukuki Soru : {hukuki_soru}\n")
            f.write(f"Sonuç Tipi  : {sonuc_tipi}\n")
            f.write(f"Sonuç       : {sonuc}\n")
            f.write(f"Emsal İlke  : {emsal_ilke}\n")
            f.write(f"Anahtar     : {anahtar}\n")
            f.write(f"Mevzuat     : {mevzuat}\n")
            f.write(f"Güven       : {guven}\n")
            f.write(f"Kaynak      : {kaynak}\n\n")

print("=" * 80)
print("138 - BATCH DB SON KALİTE KONTROL RAPORU")
print("=" * 80)
print(f"Karar sayısı : {len(kararlar)}")
print(f"Kart sayısı  : {len(rows)}")
print(f"Rapor        : {rapor}")

con.close()