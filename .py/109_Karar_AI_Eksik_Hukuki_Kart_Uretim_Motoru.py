# -*- coding: utf-8 -*-
"""
109_Karar_AI_Eksik_Hukuki_Kart_Uretim_Motoru.py

Amaç:
- karar_iddialari tablosundaki her iddia için hukuki_kartlar tablosunda kart var mı kontrol eder.
- Eksik kartları kurallı yöntemle üretir.
- AI kullanmaz.
- Hızlı, güvenli ve 100 bin karar ölçeğine uygundur.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import csv


DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"
RAPOR_DIR.mkdir(exist_ok=True)

TARIH = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_CSV = RAPOR_DIR / f"109_uretilen_hukuki_kartlar_{TARIH}.csv"


def temizle(metin):
    if metin is None:
        return ""
    return str(metin).replace("\r", " ").replace("\n", " ").strip()


def kisalt(metin, limit=180):
    metin = temizle(metin)
    if len(metin) <= limit:
        return metin
    return metin[:limit].rstrip() + "..."


def ilk_dolu(*degerler):
    for d in degerler:
        d = temizle(d)
        if d:
            return d
    return ""


def baslik_uret(uzman_soru, konu, iddia_ozeti):
    kaynak = ilk_dolu(uzman_soru, konu, iddia_ozeti)
    kaynak = temizle(kaynak)

    if not kaynak:
        return "Hukuki uyuşmazlık konusu"

    if len(kaynak) > 160:
        kaynak = kaynak[:160].rstrip()

    if not kaynak.endswith("?"):
        return kaynak

    return kaynak


def hukuki_soru_uret(uzman_soru, konu, iddia_ozeti):
    soru = ilk_dolu(uzman_soru, konu, iddia_ozeti)

    if not soru:
        return "Başvuru sahibinin iddiası hukuken yerinde midir?"

    soru = temizle(soru)

    if soru.endswith("?"):
        return soru

    return soru + " hususu hukuken nasıl değerlendirilmelidir?"


def kurul_degerlendirmesi_uret(kurul_degerlendirmesi, kurul_cevabi, iddia_ozeti):
    metin = ilk_dolu(kurul_degerlendirmesi, kurul_cevabi)

    if metin:
        return metin

    if iddia_ozeti:
        return (
            "Kurul değerlendirmesi alanı boş olduğundan, bu kart başvuru iddiası "
            "özetine dayalı olarak oluşturulmuştur. İddia özeti: "
            + kisalt(iddia_ozeti, 600)
        )

    return "Kurul değerlendirmesi metni tespit edilememiştir."


def sonuc_uret(sonuc):
    sonuc = temizle(sonuc)
    if sonuc:
        return sonuc
    return "Karar sonucu alanı tespit edilememiştir."


def emsal_ilke_uret(emsal_ilke, konu, sonuc):
    emsal_ilke = temizle(emsal_ilke)

    if emsal_ilke:
        return emsal_ilke

    konu = temizle(konu)
    sonuc = temizle(sonuc)

    if konu and sonuc:
        return f"{konu} bakımından Kurulun değerlendirmesi ve karar sonucu birlikte dikkate alınmalıdır."

    if konu:
        return f"{konu} konusunda Kurulun somut olay değerlendirmesi esas alınmalıdır."

    return "Emsal ilke alanı otomatik üretim sırasında tespit edilememiştir."


def anahtar_kelime_uret(anahtar_kelime, konu, mevzuat):
    anahtar_kelime = temizle(anahtar_kelime)
    if anahtar_kelime:
        return anahtar_kelime

    kelimeler = []

    konu = temizle(konu).lower()
    mevzuat = temizle(mevzuat)

    sozluk = {
        "iş deneyim": "iş deneyim belgesi",
        "benzer iş": "benzer iş",
        "aşırı düşük": "aşırı düşük teklif",
        "geçici teminat": "geçici teminat",
        "kesin teminat": "kesin teminat",
        "yasak": "yasaklama",
        "ihale dokümanı": "ihale dokümanı",
        "teknik şartname": "teknik şartname",
        "idari şartname": "idari şartname",
        "yaklaşık maliyet": "yaklaşık maliyet",
        "yeterlik": "yeterlik kriteri",
        "bilanço": "bilanço",
        "ciro": "ciro",
        "personel": "personel çalıştırılması",
        "araç": "araç",
        "makine": "makine ekipman",
        "ortak girişim": "ortak girişim",
        "iş ortaklığı": "iş ortaklığı",
        "alt yüklenici": "alt yüklenici",
        "şikayet": "şikayet başvurusu",
        "itirazen şikayet": "itirazen şikayet",
        "süre": "başvuru süresi",
    }

    for aranan, etiket in sozluk.items():
        if aranan in konu and etiket not in kelimeler:
            kelimeler.append(etiket)

    if mevzuat and mevzuat not in kelimeler:
        kelimeler.append(mevzuat)

    if not kelimeler:
        kelimeler.append("kamu ihale hukuku")

    return ", ".join(kelimeler[:8])


def guven_uret(guven, kurul_degerlendirmesi, sonuc, emsal_ilke):
    guven = temizle(guven)
    if guven:
        return guven

    puan = 50

    if temizle(kurul_degerlendirmesi):
        puan += 20
    if temizle(sonuc):
        puan += 15
    if temizle(emsal_ilke):
        puan += 15

    if puan >= 85:
        return "Yüksek"
    if puan >= 65:
        return "Orta"
    return "Düşük"


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    print("\n" + "=" * 80)
    print("109 - KİK KARAR AI EKSİK HUKUKİ KART ÜRETİM MOTORU")
    print("=" * 80)

    toplam_iddia = cur.execute("SELECT COUNT(*) FROM karar_iddialari").fetchone()[0]
    mevcut_kart = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]

    eksik_iddialar = cur.execute("""
        SELECT
            i.karar_no,
            i.iddia_no,
            i.konu,
            i.uzman_soru,
            i.iddia_ozeti,
            i.kurul_cevabi,
            i.kurul_degerlendirmesi,
            i.sonuc,
            i.emsal_ilke,
            i.mevzuat,
            i.anahtar_kelime,
            i.guven
        FROM karar_iddialari i
        LEFT JOIN hukuki_kartlar h
            ON h.karar_no = i.karar_no
           AND h.iddia_no = i.iddia_no
        WHERE h.id IS NULL
        ORDER BY i.karar_no, i.iddia_no
    """).fetchall()

    print(f"Toplam iddia        : {toplam_iddia}")
    print(f"Mevcut hukuki kart  : {mevcut_kart}")
    print(f"Eksik hukuki kart   : {len(eksik_iddialar)}")

    uretilen = 0
    atlanan = 0
    log_satirlari = []

    for row in eksik_iddialar:
        (
            karar_no,
            iddia_no,
            konu,
            uzman_soru,
            iddia_ozeti,
            kurul_cevabi,
            kurul_degerlendirmesi,
            sonuc,
            emsal_ilke,
            mevzuat,
            anahtar_kelime,
            guven,
        ) = row

        karar_no = temizle(karar_no)

        if not karar_no or iddia_no is None:
            atlanan += 1
            log_satirlari.append([
                karar_no,
                iddia_no,
                "ATLANDI",
                "karar_no veya iddia_no eksik",
            ])
            continue

        baslik = baslik_uret(uzman_soru, konu, iddia_ozeti)
        hukuki_soru = hukuki_soru_uret(uzman_soru, konu, iddia_ozeti)
        kurul_degerlendirmesi_yeni = kurul_degerlendirmesi_uret(
            kurul_degerlendirmesi,
            kurul_cevabi,
            iddia_ozeti,
        )
        sonuc_yeni = sonuc_uret(sonuc)
        emsal_ilke_yeni = emsal_ilke_uret(emsal_ilke, konu, sonuc)
        anahtar_kelime_yeni = anahtar_kelime_uret(anahtar_kelime, konu, mevzuat)
        guven_yeni = guven_uret(
            guven,
            kurul_degerlendirmesi_yeni,
            sonuc_yeni,
            emsal_ilke_yeni,
        )

        cur.execute("""
            INSERT INTO hukuki_kartlar (
                karar_no,
                iddia_no,
                baslik,
                hukuki_soru,
                kurul_degerlendirmesi,
                sonuc,
                emsal_ilke,
                anahtar_kelime,
                kart_tarihi,
                iddia_ozeti,
                mevzuat,
                guven,
                olusturma_tarihi
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            kurul_degerlendirmesi_yeni,
            sonuc_yeni,
            emsal_ilke_yeni,
            anahtar_kelime_yeni,
            datetime.now().strftime("%Y-%m-%d"),
            temizle(iddia_ozeti),
            temizle(mevzuat),
            guven_yeni,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))

        uretilen += 1
        log_satirlari.append([
            karar_no,
            iddia_no,
            "ÜRETİLDİ",
            baslik,
        ])

    con.commit()

    sonraki_kart = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]

    with open(LOG_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["karar_no", "iddia_no", "durum", "not"])
        writer.writerows(log_satirlari)

    print("\n" + "-" * 80)
    print("ÜRETİM SONUCU")
    print("-" * 80)
    print(f"Üretilen kart       : {uretilen}")
    print(f"Atlanan kayıt       : {atlanan}")
    print(f"Önceki kart sayısı  : {mevcut_kart}")
    print(f"Sonraki kart sayısı : {sonraki_kart}")
    print(f"Log dosyası         : {LOG_CSV}")

    con.close()

    print("\nİşlem tamamlandı.")


if __name__ == "__main__":
    main()
