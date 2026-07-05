# -*- coding: utf-8 -*-
"""
108_Karar_AI_Toplu_Kart_Denetim_Motoru.py

Amaç:
- KİK Karar AI projesinde üretilen kartları toplu denetler.
- Eksik, zayıf, mükerrer ve bağlantısız kartları tespit eder.
- Web sitesi ve AI danışman için hazır kayıt durumunu raporlar.
"""

import sqlite3
import csv
from pathlib import Path
from datetime import datetime


DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"
RAPOR_DIR.mkdir(exist_ok=True)

TARIH = datetime.now().strftime("%Y%m%d_%H%M%S")

CSV_EKSIK_HUKUKI_KART = RAPOR_DIR / f"108_eksik_hukuki_kartlar_{TARIH}.csv"
CSV_ZAYIF_HUKUKI_KART = RAPOR_DIR / f"108_zayif_hukuki_kartlar_{TARIH}.csv"
CSV_MUKERRER_HUKUKI_KART = RAPOR_DIR / f"108_mukerrer_hukuki_kartlar_{TARIH}.csv"
TXT_RAPOR = RAPOR_DIR / f"108_toplu_kart_denetim_raporu_{TARIH}.txt"


def baglan():
    return sqlite3.connect(DB_PATH)


def say(cur, tablo):
    try:
        return cur.execute(f"SELECT COUNT(*) FROM {tablo}").fetchone()[0]
    except Exception:
        return 0


def bos_mu(deger):
    return deger is None or str(deger).strip() == ""


def zayif_metin(deger, min_uzunluk=40):
    if bos_mu(deger):
        return True
    return len(str(deger).strip()) < min_uzunluk


def csv_yaz(dosya, basliklar, satirlar):
    with open(dosya, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(basliklar)
        writer.writerows(satirlar)


def main():
    con = baglan()
    cur = con.cursor()

    print("\n" + "=" * 80)
    print("108 - KİK KARAR AI TOPLU KART DENETİM MOTORU")
    print("=" * 80)

    toplam_karar = say(cur, "kararlar")
    toplam_iddia = say(cur, "karar_iddialari")
    toplam_hukuki_kart = say(cur, "hukuki_kartlar")
    toplam_ai_kart = say(cur, "ai_karar_kartlari")
    toplam_ai_hazirlik = say(cur, "ai_hazirlik")
    toplam_embedding = say(cur, "karar_embedding")

    print(f"Toplam karar              : {toplam_karar}")
    print(f"Toplam iddia              : {toplam_iddia}")
    print(f"Hukuki kart               : {toplam_hukuki_kart}")
    print(f"AI karar kartı            : {toplam_ai_kart}")
    print(f"AI hazırlık kaydı         : {toplam_ai_hazirlik}")
    print(f"Embedding kaydı           : {toplam_embedding}")

    # 1. Eksik hukuki kartlar
    eksik_hukuki_kartlar = cur.execute("""
        SELECT 
            i.karar_no,
            i.iddia_no,
            i.konu,
            i.uzman_soru,
            i.iddia_ozeti,
            i.sonuc
        FROM karar_iddialari i
        LEFT JOIN hukuki_kartlar h
            ON h.karar_no = i.karar_no
           AND h.iddia_no = i.iddia_no
        WHERE h.id IS NULL
        ORDER BY i.karar_no, i.iddia_no
    """).fetchall()

    # 2. Zayıf hukuki kartlar
    tum_hukuki_kartlar = cur.execute("""
        SELECT
            id,
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            kurul_degerlendirmesi,
            sonuc,
            emsal_ilke,
            anahtar_kelime,
            mevzuat,
            guven
        FROM hukuki_kartlar
        ORDER BY karar_no, iddia_no
    """).fetchall()

    zayif_kartlar = []

    for row in tum_hukuki_kartlar:
        (
            kart_id,
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            kurul_degerlendirmesi,
            sonuc,
            emsal_ilke,
            anahtar_kelime,
            mevzuat,
            guven,
        ) = row

        sorunlar = []

        if zayif_metin(baslik, 15):
            sorunlar.append("başlık boş/zayıf")
        if zayif_metin(hukuki_soru, 25):
            sorunlar.append("hukuki soru boş/zayıf")
        if zayif_metin(kurul_degerlendirmesi, 80):
            sorunlar.append("kurul değerlendirmesi boş/zayıf")
        if zayif_metin(sonuc, 30):
            sorunlar.append("sonuç boş/zayıf")
        if zayif_metin(emsal_ilke, 30):
            sorunlar.append("emsal ilke boş/zayıf")
        if zayif_metin(anahtar_kelime, 10):
            sorunlar.append("anahtar kelime boş/zayıf")
        if bos_mu(mevzuat):
            sorunlar.append("mevzuat boş")
        if bos_mu(guven):
            sorunlar.append("güven boş")

        if sorunlar:
            zayif_kartlar.append([
                kart_id,
                karar_no,
                iddia_no,
                "; ".join(sorunlar),
                baslik,
                hukuki_soru,
                sonuc,
                emsal_ilke,
                anahtar_kelime,
                mevzuat,
                guven,
            ])

    # 3. Mükerrer hukuki kartlar
    mukerrer_hukuki_kartlar = cur.execute("""
        SELECT
            karar_no,
            iddia_no,
            COUNT(*) AS adet
        FROM hukuki_kartlar
        GROUP BY karar_no, iddia_no
        HAVING COUNT(*) > 1
        ORDER BY adet DESC, karar_no, iddia_no
    """).fetchall()

    # 4. Karar bazında kart durumu
    kartli_karar_sayisi = cur.execute("""
        SELECT COUNT(DISTINCT karar_no) FROM hukuki_kartlar
    """).fetchone()[0]

    ai_kartli_karar_sayisi = cur.execute("""
        SELECT COUNT(DISTINCT karar_no) FROM ai_karar_kartlari
    """).fetchone()[0]

    iddiali_karar_sayisi = cur.execute("""
        SELECT COUNT(DISTINCT karar_no) FROM karar_iddialari
    """).fetchone()[0]

    tum_iddialar_kartli_mi = cur.execute("""
        SELECT COUNT(*)
        FROM karar_iddialari i
        WHERE NOT EXISTS (
            SELECT 1
            FROM hukuki_kartlar h
            WHERE h.karar_no = i.karar_no
              AND h.iddia_no = i.iddia_no
        )
    """).fetchone()[0]

    # 5. Web ve AI danışman hazır kayıt ölçümü
    web_hazir_kart = cur.execute("""
        SELECT COUNT(*)
        FROM hukuki_kartlar
        WHERE 
            baslik IS NOT NULL AND TRIM(baslik) <> ''
            AND hukuki_soru IS NOT NULL AND TRIM(hukuki_soru) <> ''
            AND kurul_degerlendirmesi IS NOT NULL AND TRIM(kurul_degerlendirmesi) <> ''
            AND sonuc IS NOT NULL AND TRIM(sonuc) <> ''
            AND emsal_ilke IS NOT NULL AND TRIM(emsal_ilke) <> ''
            AND anahtar_kelime IS NOT NULL AND TRIM(anahtar_kelime) <> ''
    """).fetchone()[0]

    ai_danisman_hazir_kart = cur.execute("""
        SELECT COUNT(*)
        FROM ai_karar_kartlari
        WHERE
            soru_basligi IS NOT NULL AND TRIM(soru_basligi) <> ''
            AND kisa_ozet IS NOT NULL AND TRIM(kisa_ozet) <> ''
            AND hukuki_sorun IS NOT NULL AND TRIM(hukuki_sorun) <> ''
            AND sonuc IS NOT NULL AND TRIM(sonuc) <> ''
            AND emsal_ilke IS NOT NULL AND TRIM(emsal_ilke) <> ''
            AND anahtar_kelimeler IS NOT NULL AND TRIM(anahtar_kelimeler) <> ''
    """).fetchone()[0]

    # CSV çıktıları
    csv_yaz(
        CSV_EKSIK_HUKUKI_KART,
        ["karar_no", "iddia_no", "konu", "uzman_soru", "iddia_ozeti", "sonuc"],
        eksik_hukuki_kartlar,
    )

    csv_yaz(
        CSV_ZAYIF_HUKUKI_KART,
        [
            "kart_id",
            "karar_no",
            "iddia_no",
            "sorunlar",
            "baslik",
            "hukuki_soru",
            "sonuc",
            "emsal_ilke",
            "anahtar_kelime",
            "mevzuat",
            "guven",
        ],
        zayif_kartlar,
    )

    csv_yaz(
        CSV_MUKERRER_HUKUKI_KART,
        ["karar_no", "iddia_no", "mukerrer_adet"],
        mukerrer_hukuki_kartlar,
    )

    rapor = f"""
KİK KARAR AI TOPLU KART DENETİM RAPORU
Tarih: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}

GENEL SAYILAR
----------------------------------------
Toplam karar                  : {toplam_karar}
Toplam iddia                  : {toplam_iddia}
Hukuki kart                   : {toplam_hukuki_kart}
AI karar kartı                : {toplam_ai_kart}
AI hazırlık kaydı             : {toplam_ai_hazirlik}
Embedding kaydı               : {toplam_embedding}

KARAR BAZLI DURUM
----------------------------------------
İddia içeren karar sayısı      : {iddiali_karar_sayisi}
Hukuki kartlı karar sayısı     : {kartli_karar_sayisi}
AI kartlı karar sayısı         : {ai_kartli_karar_sayisi}

DENETİM SONUÇLARI
----------------------------------------
Eksik hukuki kart sayısı       : {len(eksik_hukuki_kartlar)}
Zayıf hukuki kart sayısı       : {len(zayif_kartlar)}
Mükerrer kart grubu sayısı     : {len(mukerrer_hukuki_kartlar)}
Kartı olmayan iddia sayısı     : {tum_iddialar_kartli_mi}

HAZIRLIK DURUMU
----------------------------------------
Web sitesi için hazır kart     : {web_hazir_kart}
AI danışman için hazır kart    : {ai_danisman_hazir_kart}

RAPOR DOSYALARI
----------------------------------------
Eksik kart CSV                 : {CSV_EKSIK_HUKUKI_KART}
Zayıf kart CSV                 : {CSV_ZAYIF_HUKUKI_KART}
Mükerrer kart CSV              : {CSV_MUKERRER_HUKUKI_KART}
TXT rapor                      : {TXT_RAPOR}

YORUM
----------------------------------------
Bu rapor, 100 bin karar ölçeğine geçmeden önce mevcut test veritabanındaki
kart üretim kalitesini denetlemek için hazırlanmıştır.

Eksik hukuki kart sayısı yüksekse, sıradaki adım:
109_Karar_AI_Eksik_Kart_Uretim_Motoru.py

Zayıf kart sayısı yüksekse, sıradaki adım:
109_Karar_AI_Zayif_Kart_Guclendirme_Motoru.py

Mükerrer kart varsa, sıradaki adım:
109_Karar_AI_Mukerrer_Kart_Temizleme_Motoru.py
"""

    with open(TXT_RAPOR, "w", encoding="utf-8") as f:
        f.write(rapor.strip())

    print("\n" + "-" * 80)
    print("DENETİM SONUÇLARI")
    print("-" * 80)
    print(f"Eksik hukuki kart sayısı   : {len(eksik_hukuki_kartlar)}")
    print(f"Zayıf hukuki kart sayısı   : {len(zayif_kartlar)}")
    print(f"Mükerrer kart grubu        : {len(mukerrer_hukuki_kartlar)}")
    print(f"Web hazır kart             : {web_hazir_kart}")
    print(f"AI danışman hazır kart     : {ai_danisman_hazir_kart}")

    print("\nRaporlar oluşturuldu:")
    print(CSV_EKSIK_HUKUKI_KART)
    print(CSV_ZAYIF_HUKUKI_KART)
    print(CSV_MUKERRER_HUKUKI_KART)
    print(TXT_RAPOR)

    con.close()

    print("\nİşlem tamamlandı.")


if __name__ == "__main__":
    main()