# 142_Batch_Validator_Duzeltme_DB_Uygulama_Motoru.py

import os, json, sqlite3, shutil
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
DB_PATH = os.path.join(PY_DIR, "kik.db")

SIM_JSONL = r"C:\Users\MSI\Desktop\kik_proje\raporlar\141_batch_duzeltme_simulasyon_ozet_20260628_114648.jsonl"

DB_YAZ = True

ALAN_MAP = {
    "baslik": "baslik",
    "hukuki_soru": "hukuki_soru",
    "sonuc_tipi": "sonuc_tipi",
    "sonuc": "sonuc",
    "emsal_ilke": "emsal_ilke",
    "anahtar": "anahtar_kelimeler",
    "anahtar_kelimeler": "anahtar_kelimeler",
    "mevzuat": "mevzuat",
    "guven": "guven",
    "güven": "guven",
}

def now():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]

def main():
    print("=" * 80)
    print("142 - BATCH VALIDATOR DÜZELTME DB UYGULAMA MOTORU")
    print("=" * 80)

    rows = read_jsonl(SIM_JSONL)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cols = table_columns(cur, "hukuki_kartlar")

    ts = now()
    yedek_tablo = f"hukuki_kartlar_yedek_142_{ts}"

    if DB_YAZ:
        cur.execute(f"CREATE TABLE {yedek_tablo} AS SELECT * FROM hukuki_kartlar")

    uygulanan_kart = 0
    degisiklik_toplam = 0
    kart_bulunamadi = 0
    atlanan_alan = 0
    detaylar = []

    for row in rows:
        kart_id = row.get("kart_id")
        karar_no = row.get("karar_no")
        degisiklikler = row.get("degisiklikler", [])

        if not kart_id:
            kart_bulunamadi += 1
            detaylar.append(f"[BULUNAMADI] karar={karar_no} kart_id yok")
            continue

        cur.execute("SELECT id FROM hukuki_kartlar WHERE id=?", (kart_id,))
        found = cur.fetchone()

        if not found:
            kart_bulunamadi += 1
            detaylar.append(f"[BULUNAMADI] karar={karar_no} kart_id={kart_id}")
            continue

        kart_degisti = False

        for d in degisiklikler:
            alan = str(d.get("alan", "")).strip()
            yeni = d.get("yeni")

            db_alan = ALAN_MAP.get(alan)

            if not db_alan or db_alan not in cols:
                atlanan_alan += 1
                detaylar.append(f"[ATLANDI] karar={karar_no} kart_id={kart_id} alan={alan} DB alanı yok")
                continue

            if DB_YAZ:
                cur.execute(
                    f"UPDATE hukuki_kartlar SET {db_alan}=? WHERE id=?",
                    (yeni, kart_id)
                )

            kart_degisti = True
            degisiklik_toplam += 1
            detaylar.append(
                f"[UYGULANDI] karar={karar_no} kart_id={kart_id} {db_alan}: {d.get('eski')} -> {yeni}"
            )

        if kart_degisti:
            uygulanan_kart += 1

    if DB_YAZ:
        con.commit()

    rapor_path = os.path.join(RAPOR_DIR, f"142_batch_validator_db_duzeltme_raporu_{ts}.txt")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("142 - BATCH VALIDATOR DÜZELTME DB UYGULAMA RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"Simülasyon JSONL   : {SIM_JSONL}\n")
        f.write(f"Plan kayıt         : {len(rows)}\n")
        f.write(f"Uygulanan kart     : {uygulanan_kart}\n")
        f.write(f"Değişiklik toplamı : {degisiklik_toplam}\n")
        f.write(f"Kart bulunamadı    : {kart_bulunamadi}\n")
        f.write(f"Atlanan alan       : {atlanan_alan}\n")
        f.write(f"DB yaz             : {DB_YAZ}\n")
        f.write(f"Yedek tablo        : {yedek_tablo if DB_YAZ else 'YOK'}\n\n")
        f.write("DETAYLAR\n")
        f.write("-" * 80 + "\n")
        for line in detaylar:
            f.write(line + "\n")

    con.close()

    print()
    print("DB DÜZELTME UYGULAMASI TAMAMLANDI")
    print("-" * 80)
    print(f"Plan kayıt          : {len(rows)}")
    print(f"Uygulanan kart      : {uygulanan_kart}")
    print(f"Değişiklik toplamı  : {degisiklik_toplam}")
    print(f"Kart bulunamadı     : {kart_bulunamadi}")
    print(f"Atlanan alan        : {atlanan_alan}")
    print(f"DB yaz              : {DB_YAZ}")
    print(f"Yedek tablo         : {yedek_tablo if DB_YAZ else 'YOK'}")
    print()
    print("Dosya:")
    print(rapor_path)
    print()
    print("DB'ye yazıldı." if DB_YAZ else "DB'ye yazılmadı.")

if __name__ == "__main__":
    main()