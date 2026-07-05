import sqlite3
import os
from datetime import datetime
from collections import Counter, defaultdict

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
os.makedirs(RAPOR_DIR, exist_ok=True)

def now_tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def norm(v):
    return (v or "").strip()

def has_col(cur, table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def risk_sonuc_tipi_sonuc(sonuc_tipi, sonuc):
    st = norm(sonuc_tipi).upper()
    s = norm(sonuc).lower()

    kabul_kelimeleri = [
        "yerindedir", "mevzuata aykırıdır", "hukuka aykırıdır",
        "uygun bulunmamıştır", "yeniden yapılması gerekir",
        "düzeltici işlem"
    ]
    ret_kelimeleri = [
        "yerinde değildir", "reddedilmiştir", "reddine karar",
        "uygun bulunmuştur", "mevzuata uygundur", "hukuka uygundur"
    ]

    if st == "RET" and any(k in s for k in kabul_kelimeleri):
        return True
    if st in ("KABUL", "DÜZELTİCİ İŞLEM", "İPTAL") and any(k in s for k in ret_kelimeleri):
        return True
    return False

def main():
    print("=" * 80)
    print("146 - AKTİF KART SON KALİTE RAPORU")
    print("=" * 80)

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    aktif_var = has_col(cur, "hukuki_kartlar", "aktif")
    kalite_etiketi_var = has_col(cur, "hukuki_kartlar", "kalite_etiketi")

    total = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]

    if aktif_var:
        aktif = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif,1)=1").fetchone()[0]
        pasif = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif,1)=0").fetchone()[0]
        rows = cur.execute("SELECT * FROM hukuki_kartlar WHERE COALESCE(aktif,1)=1").fetchall()
    else:
        aktif = total
        pasif = 0
        rows = cur.execute("SELECT * FROM hukuki_kartlar").fetchall()

    riskler = []
    guven_counter = Counter()
    karar_baslik_map = defaultdict(list)

    bos_sonuc = 0
    bos_soru = 0
    bos_emsal = 0
    sonuc_celiski = 0
    aktif_mukerrer = 0

    for r in rows:
        kart_id = r["id"] if "id" in r.keys() else None
        karar_no = norm(r["karar_no"]) if "karar_no" in r.keys() else ""
        baslik = norm(r["baslik"]) if "baslik" in r.keys() else ""
        soru = norm(r["hukuki_soru"]) if "hukuki_soru" in r.keys() else ""
        sonuc_tipi = norm(r["sonuc_tipi"]) if "sonuc_tipi" in r.keys() else ""
        sonuc = norm(r["sonuc"]) if "sonuc" in r.keys() else ""
        emsal = norm(r["emsal_ilke"]) if "emsal_ilke" in r.keys() else ""
        guven = norm(r["guven"]) if "guven" in r.keys() else "BELİRSİZ"

        guven_counter[guven or "BELİRSİZ"] += 1

        if not sonuc:
            bos_sonuc += 1
            riskler.append((karar_no, kart_id, "BOŞ SONUÇ", baslik))

        if not soru:
            bos_soru += 1
            riskler.append((karar_no, kart_id, "BOŞ HUKUKİ SORU", baslik))

        if not emsal:
            bos_emsal += 1
            riskler.append((karar_no, kart_id, "BOŞ EMSAL İLKE", baslik))

        if risk_sonuc_tipi_sonuc(sonuc_tipi, sonuc):
            sonuc_celiski += 1
            riskler.append((karar_no, kart_id, "SONUÇ TİPİ / SONUÇ ÇELİŞKİSİ", baslik))

        karar_baslik_map[(karar_no, baslik.lower())].append((kart_id, baslik))

    for (karar_no, baslik_key), items in karar_baslik_map.items():
        if baslik_key and len(items) > 1:
            aktif_mukerrer += len(items)
            for kart_id, baslik in items:
                riskler.append((karar_no, kart_id, "AKTİF MÜKERRER BAŞLIK", baslik))

    risk_sayisi = (
        bos_sonuc
        + bos_soru
        + bos_emsal
        + sonuc_celiski
        + aktif_mukerrer
    )

    if aktif == 0:
        kalite_puani = 0
    else:
        kalite_puani = max(0, round(100 - (risk_sayisi / aktif * 100), 2))

    sertifika = risk_sayisi == 0

    ts = now_tag()
    rapor_path = os.path.join(RAPOR_DIR, f"146_aktif_kart_son_kalite_raporu_{ts}.txt")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("146 - AKTİF KART SON KALİTE RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"Aktif kolonu       : {'VAR' if aktif_var else 'YOK'}\n")
        f.write(f"Kalite etiketi     : {'VAR' if kalite_etiketi_var else 'YOK'}\n\n")

        f.write("TOPLAM KART\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam Kart        : {total}\n")
        f.write(f"Aktif Kart         : {aktif}\n")
        f.write(f"Pasif Kart         : {pasif}\n\n")

        f.write("KALİTE\n")
        f.write("-" * 80 + "\n")
        f.write(f"Sonuç Tipi Çelişkisi : {sonuc_celiski}\n")
        f.write(f"Mükerrer Aktif Kart  : {aktif_mukerrer}\n")
        f.write(f"Boş Emsal            : {bos_emsal}\n")
        f.write(f"Boş Sonuç            : {bos_sonuc}\n")
        f.write(f"Boş Hukuki Soru      : {bos_soru}\n\n")

        f.write("GÜVEN DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        for k, v in guven_counter.most_common():
            f.write(f"{k:<15}: {v}\n")
        f.write("\n")

        f.write("KALİTE PUANI\n")
        f.write("-" * 80 + "\n")
        f.write(f"{kalite_puani} / 100\n\n")

        f.write("SERTİFİKA\n")
        f.write("-" * 80 + "\n")
        if sertifika:
            f.write("✓ WEB yayınına uygun\n")
            f.write("✓ RAG indeksine uygun\n")
            f.write("✓ AI danışman motoruna uygun\n")
            f.write("✓ Arama motoruna uygun\n")
            f.write("✓ Eğitim veri seti olarak uygun\n\n")
            f.write("SONUÇ\n")
            f.write("AKTİF VERİ TABANI KALİTE TESTLERİNİ BAŞARIYLA GEÇMİŞTİR.\n")
        else:
            f.write("✗ Sertifika verilmedi.\n")
            f.write("Aktif kartlarda giderilmesi gereken kalite riski bulunmaktadır.\n\n")
            f.write("RİSK DETAYLARI\n")
            f.write("-" * 80 + "\n")
            for karar_no, kart_id, risk, baslik in riskler:
                f.write(f"[{risk}] karar={karar_no} kart_id={kart_id} | {baslik}\n")

    print()
    print("AKTİF KART KALİTE RAPORU OLUŞTURULDU")
    print("-" * 80)
    print(f"Toplam kart    : {total}")
    print(f"Aktif kart     : {aktif}")
    print(f"Pasif kart     : {pasif}")
    print(f"Risk sayısı    : {risk_sayisi}")
    print(f"Kalite puanı   : {kalite_puani} / 100")
    print(f"Sertifika      : {'GEÇTİ' if sertifika else 'KALDI'}")
    print()
    print("Dosya:")
    print(rapor_path)

    con.close()

if __name__ == "__main__":
    main()