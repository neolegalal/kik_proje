# -*- coding: utf-8 -*-
"""
148 - AKTİF KART KALİTE RİSK DB UYGULAMA MOTORU

147 planındaki düzeltmeleri DB'ye uygular.
- Önce yedek tablo alır.
- aktif=0 kartları dikkate almaz.
- Boş sonuç / boş emsal / güven format / sonuç tipi çelişkisi düzeltmelerini uygular.
- Mükerrer başlık kartlarını pasifleştirir.
"""

import os
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

DB_YAZ = True

def now_tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def find_latest_plan():
    files = [
        os.path.join(RAPOR_DIR, f)
        for f in os.listdir(RAPOR_DIR)
        if f.startswith("147_aktif_kart_kalite_risk_duzeltme_plani_")
        and f.endswith(".jsonl")
    ]
    if not files:
        raise FileNotFoundError("147 düzeltme planı JSONL bulunamadı.")
    return max(files, key=os.path.getmtime)

def col_exists(cur, table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def ensure_columns(cur):
    if not col_exists(cur, "hukuki_kartlar", "aktif"):
        cur.execute("ALTER TABLE hukuki_kartlar ADD COLUMN aktif INTEGER DEFAULT 1")
    if not col_exists(cur, "hukuki_kartlar", "kalite_etiketi"):
        cur.execute("ALTER TABLE hukuki_kartlar ADD COLUMN kalite_etiketi TEXT")
    if not col_exists(cur, "hukuki_kartlar", "kalite_notu"):
        cur.execute("ALTER TABLE hukuki_kartlar ADD COLUMN kalite_notu TEXT")

def get_columns(cur):
    cur.execute("PRAGMA table_info(hukuki_kartlar)")
    return [r[1] for r in cur.fetchall()]

def get_card(cur, kart_id):
    cur.execute("SELECT * FROM hukuki_kartlar WHERE id=?", (kart_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = get_columns(cur)
    return dict(zip(cols, row))

def normalize_guven(v):
    if not v:
        return "Orta"
    s = str(v).strip().lower()
    if s == "yüksek":
        return "Yüksek"
    if s == "orta":
        return "Orta"
    if s == "düşük":
        return "Düşük"
    return str(v).strip()

def apply_update(cur, kart_id, alan, yeni):
    cur.execute(
        f"UPDATE hukuki_kartlar SET {alan}=? WHERE id=? AND COALESCE(aktif,1)=1",
        (yeni, kart_id)
    )
    return cur.rowcount

def main():
    print("=" * 80)
    print("148 - AKTİF KART KALİTE RİSK DB UYGULAMA MOTORU")
    print("=" * 80)

    tag = now_tag()
    plan_path = find_latest_plan()
    rapor_path = os.path.join(RAPOR_DIR, f"148_aktif_kart_kalite_risk_db_uygulama_raporu_{tag}.txt")

    with open(plan_path, "r", encoding="utf-8") as f:
        plan = [json.loads(line) for line in f if line.strip()]

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    ensure_columns(cur)

    yedek_tablo = f"hukuki_kartlar_yedek_148_{tag}"
    cur.execute(f"CREATE TABLE {yedek_tablo} AS SELECT * FROM hukuki_kartlar")

    uygulanan = 0
    atlanan_pasif = 0
    bulunamayan = 0
    detaylar = []

    for item in plan:
        kart_id = item.get("kart_id") or item.get("id")
        risk_tipi = item.get("risk_tipi") or item.get("risk") or item.get("islem")
        alan = item.get("alan")
        yeni = item.get("yeni")
        notu = item.get("not") or item.get("aciklama") or ""

        if not kart_id:
            bulunamayan += 1
            detaylar.append("[ATLANDI] kart_id yok")
            continue

        card = get_card(cur, kart_id)
        if not card:
            bulunamayan += 1
            detaylar.append(f"[BULUNAMADI] kart_id={kart_id}")
            continue

        if int(card.get("aktif") if card.get("aktif") is not None else 1) == 0:
            atlanan_pasif += 1
            detaylar.append(f"[PASIF_ATLANDI] kart_id={kart_id} | {card.get('baslik','')}")
            continue

        risk_upper = str(risk_tipi or "").upper()

        # 1) Mükerrer başlık pasifleştirme
        if "MUKERRER" in risk_upper:
            cur.execute("""
                UPDATE hukuki_kartlar
                SET aktif=0,
                    kalite_etiketi='AKTIF_MUKERRER_BASLIK',
                    kalite_notu=?
                WHERE id=? AND COALESCE(aktif,1)=1
            """, (notu or "147 kalite planı kapsamında aktif mükerrer başlık pasifleştirildi.", kart_id))
            if cur.rowcount:
                uygulanan += 1
                detaylar.append(f"[PASIFLESTIRILDI] kart_id={kart_id} | {card.get('baslik','')}")
            continue

        # 2) Güven formatı
        if risk_upper == "GUVEN_FORMAT" or alan == "guven":
            eski = card.get("guven")
            yeni_deger = normalize_guven(yeni or eski)
            if eski != yeni_deger:
                uygulanan += apply_update(cur, kart_id, "guven", yeni_deger)
                detaylar.append(f"[GUVEN] kart_id={kart_id} {eski} -> {yeni_deger}")
            continue

        # 3) Boş sonuç
        if risk_upper == "BOS_SONUC" or alan == "sonuc":
            if yeni:
                uygulanan += apply_update(cur, kart_id, "sonuc", yeni)
                detaylar.append(f"[SONUC] kart_id={kart_id} -> {yeni}")
            else:
                detaylar.append(f"[SONUC_ATLANDI] kart_id={kart_id} yeni değer yok")
            continue

        # 4) Boş emsal ilke
        if risk_upper == "BOS_EMSAL_ILKE" or alan == "emsal_ilke":
            if yeni:
                uygulanan += apply_update(cur, kart_id, "emsal_ilke", yeni)
                detaylar.append(f"[EMSAL] kart_id={kart_id} -> {yeni}")
            else:
                detaylar.append(f"[EMSAL_ATLANDI] kart_id={kart_id} yeni değer yok")
            continue

        # 5) Sonuç tipi çelişkisi
        if risk_upper == "SONUC_TIPI_CELISKI" or alan == "sonuc_tipi":
            if yeni:
                eski = card.get("sonuc_tipi")
                uygulanan += apply_update(cur, kart_id, "sonuc_tipi", yeni)
                detaylar.append(f"[SONUC_TIPI] kart_id={kart_id} {eski} -> {yeni}")
            else:
                detaylar.append(f"[SONUC_TIPI_ATLANDI] kart_id={kart_id} yeni değer yok")
            continue

        detaylar.append(f"[TANIMSIZ_ATLANDI] kart_id={kart_id} risk={risk_tipi}")

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
        f.write("148 - AKTİF KART KALİTE RİSK DB UYGULAMA RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih          : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB             : {DB_PATH}\n")
        f.write(f"Plan JSONL     : {plan_path}\n")
        f.write(f"DB yaz         : {DB_YAZ}\n")
        f.write(f"Yedek tablo    : {yedek_tablo}\n")
        f.write(f"Plan kayıt     : {len(plan)}\n")
        f.write(f"Uygulanan      : {uygulanan}\n")
        f.write(f"Pasif atlanan  : {atlanan_pasif}\n")
        f.write(f"Kart bulunamadı: {bulunamayan}\n")
        f.write(f"Toplam kart    : {toplam}\n")
        f.write(f"Aktif kart     : {aktif}\n")
        f.write(f"Pasif kart     : {pasif}\n\n")
        f.write("DETAYLAR\n")
        f.write("-" * 80 + "\n")
        for d in detaylar:
            f.write(d + "\n")

    print("\nDB UYGULAMA TAMAMLANDI")
    print("-" * 80)
    print(f"Plan kayıt     : {len(plan)}")
    print(f"Uygulanan      : {uygulanan}")
    print(f"Pasif atlanan  : {atlanan_pasif}")
    print(f"Kart bulunamadı: {bulunamayan}")
    print(f"Aktif kart     : {aktif}")
    print(f"Pasif kart     : {pasif}")
    print(f"Yedek tablo    : {yedek_tablo}")
    print("\nDosya:")
    print(rapor_path)

if __name__ == "__main__":
    main()