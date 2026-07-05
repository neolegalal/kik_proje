# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
DB_YAZ = True

DUZELTMELER = {
    422: "KABUL",
    424: "KABUL",
    567: "KABUL",
    568: "KABUL",
    569: "KABUL",
    1102: "RET",
    1591: "RET",
    1668: "KABUL",
    1786: "KABUL",
    1827: "RET",
}

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def main():
    print("=" * 80)
    print("149 - FINAL KALİTE SERTİFİKA TEMİZLİK MOTORU")
    print("=" * 80)

    t = tag()
    rapor_path = os.path.join(RAPOR_DIR, f"149_final_kalite_sertifika_temizlik_raporu_{t}.txt")
    yedek_tablo = f"hukuki_kartlar_yedek_149_{t}"

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute(f"CREATE TABLE {yedek_tablo} AS SELECT * FROM hukuki_kartlar")

    uygulanan = 0
    bulunamayan = 0
    detaylar = []

    for kart_id, yeni_tip in DUZELTMELER.items():
        cur.execute("""
            SELECT id, karar_no, baslik, sonuc_tipi, sonuc
            FROM hukuki_kartlar
            WHERE id=? AND COALESCE(aktif,1)=1
        """, (kart_id,))
        row = cur.fetchone()

        if not row:
            bulunamayan += 1
            detaylar.append(f"[BULUNAMADI] kart_id={kart_id}")
            continue

        _, karar_no, baslik, eski_tip, sonuc = row

        cur.execute("""
            UPDATE hukuki_kartlar
            SET sonuc_tipi=?,
                kalite_etiketi=NULL,
                kalite_notu=NULL
            WHERE id=? AND COALESCE(aktif,1)=1
        """, (yeni_tip, kart_id))

        uygulanan += cur.rowcount
        detaylar.append(
            f"[DUZELTILDI] karar={karar_no} kart_id={kart_id} "
            f"sonuc_tipi: {eski_tip} -> {yeni_tip} | {baslik}"
        )

    if DB_YAZ:
        con.commit()
    else:
        con.rollback()

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar")
    toplam = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif,1)=1")
    aktif = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif,1)=0")
    pasif = cur.fetchone()[0]

    con.close()

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("149 - FINAL KALİTE SERTİFİKA TEMİZLİK RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih          : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB             : {DB_PATH}\n")
        f.write(f"DB yaz         : {DB_YAZ}\n")
        f.write(f"Yedek tablo    : {yedek_tablo}\n")
        f.write(f"Plan kart      : {len(DUZELTMELER)}\n")
        f.write(f"Uygulanan      : {uygulanan}\n")
        f.write(f"Bulunamayan    : {bulunamayan}\n")
        f.write(f"Toplam kart    : {toplam}\n")
        f.write(f"Aktif kart     : {aktif}\n")
        f.write(f"Pasif kart     : {pasif}\n\n")
        f.write("DETAYLAR\n")
        f.write("-" * 80 + "\n")
        for d in detaylar:
            f.write(d + "\n")

    print("\nFINAL TEMİZLİK TAMAMLANDI")
    print("-" * 80)
    print(f"Plan kart   : {len(DUZELTMELER)}")
    print(f"Uygulanan   : {uygulanan}")
    print(f"Bulunamayan : {bulunamayan}")
    print(f"Aktif kart  : {aktif}")
    print(f"Pasif kart  : {pasif}")
    print(f"Yedek tablo : {yedek_tablo}")
    print("\nDosya:")
    print(rapor_path)

if __name__ == "__main__":
    main()