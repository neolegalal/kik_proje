# -*- coding: utf-8 -*-

import sqlite3
import re
from datetime import datetime

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"


def temizle(metin):
    if metin is None:
        return ""
    metin = str(metin)
    metin = re.sub(r"\s+", " ", metin)
    return metin.strip()


def kisalt(metin, limit=500):
    metin = temizle(metin)
    return metin[:limit].rstrip() + "..." if len(metin) > limit else metin


def konu_bul(metin):
    m = temizle(metin).lower()

    sozluk = {
        "iş deneyim belgesi": ["iş deneyim", "iş bitirme", "iş durum"],
        "benzer iş": ["benzer iş"],
        "iş ortaklığı": ["iş ortaklığı", "ortak girişim", "pilot ortak", "özel ortak"],
        "yasaklama": ["yasaklama", "ihalelere katılmaktan yasaklama"],
        "yaklaşık maliyet": ["yaklaşık maliyet"],
        "sınır değer": ["sınır değer"],
        "kesin teminat": ["kesin teminat"],
        "geçici teminat": ["geçici teminat"],
        "aşırı düşük teklif": ["aşırı düşük"],
        "yeterlik kriteri": ["yeterlik", "yeterlilik"],
        "teknik şartname": ["teknik şartname"],
        "idari şartname": ["idari şartname"],
        "fiyat dışı unsur": ["fiyat dışı"],
    }

    bulunan = []

    for konu, kelimeler in sozluk.items():
        if any(k in m for k in kelimeler):
            bulunan.append(konu)

    return bulunan


def soru_basligi_uret(konular, ihale_konusu):
    if konular:
        return f"{konular[0].capitalize()} konusunda Kurul değerlendirmesi nedir?"
    if ihale_konusu:
        return f"{kisalt(ihale_konusu, 120)} ihalesinde uyuşmazlık konusu nedir?"
    return "Kamu İhale Kurulu kararında uyuşmazlık konusu nedir?"


def ozet_uret(tam_metin, limit=700):
    metin = temizle(tam_metin)
    if not metin:
        return "Karar metni bulunamadığından özet üretilemedi."
    return kisalt(metin, limit)


def sonuc_ozeti_uret(karar_sonucu, tam_metin):
    karar_sonucu = temizle(karar_sonucu)
    if karar_sonucu:
        return karar_sonucu

    m = temizle(tam_metin).lower()

    if "iptal" in m:
        return "Kararda ihale süreci bakımından iptal sonucu doğuran bir değerlendirme bulunmaktadır."
    if "redd" in m or "yerinde bulunmamıştır" in m:
        return "Başvuru sahibinin iddiası yerinde görülmemiştir."
    if "yerinde bulunmuştur" in m or "düzeltici işlem" in m:
        return "Başvuru sahibinin iddiası yerinde görülmüş veya düzeltici işlem belirlenmiştir."

    return "Karar sonucu otomatik olarak net tespit edilememiştir."


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    rows = cur.execute("""
        SELECT
            id,
            karar_no,
            ihale_konusu,
            karar_sonucu,
            ilgili_mevzuat,
            tam_metin,
            karar_soru_basligi,
            karar_ozeti,
            karar_sonuc_ozeti,
            anahtar_kelimeler
        FROM kararlar
        WHERE
            karar_soru_basligi IS NULL OR TRIM(karar_soru_basligi) = ''
            OR karar_ozeti IS NULL OR TRIM(karar_ozeti) = ''
            OR karar_sonuc_ozeti IS NULL OR TRIM(karar_sonuc_ozeti) = ''
            OR anahtar_kelimeler IS NULL OR TRIM(anahtar_kelimeler) = ''
    """).fetchall()

    print("=" * 80)
    print("115 - KİK KARAR AI BOŞ KARAR ÖZET ALANLARI DOLDURMA MOTORU")
    print("=" * 80)
    print(f"İşlenecek karar sayısı: {len(rows)}")

    guncellenen = 0

    for row in rows:
        (
            karar_id,
            karar_no,
            ihale_konusu,
            karar_sonucu,
            ilgili_mevzuat,
            tam_metin,
            mevcut_soru,
            mevcut_ozet,
            mevcut_sonuc,
            mevcut_anahtar,
        ) = row

        kaynak_metin = " ".join([
            temizle(ihale_konusu),
            temizle(karar_sonucu),
            temizle(ilgili_mevzuat),
            temizle(tam_metin),
        ])

        konular = konu_bul(kaynak_metin)

        yeni_soru = mevcut_soru if temizle(mevcut_soru) else soru_basligi_uret(konular, ihale_konusu)
        yeni_ozet = mevcut_ozet if temizle(mevcut_ozet) else ozet_uret(tam_metin)
        yeni_sonuc = mevcut_sonuc if temizle(mevcut_sonuc) else sonuc_ozeti_uret(karar_sonucu, tam_metin)
        yeni_anahtar = mevcut_anahtar if temizle(mevcut_anahtar) else ", ".join(konular) if konular else "kamu ihale hukuku"

        cur.execute("""
            UPDATE kararlar
            SET
                karar_soru_basligi = ?,
                karar_ozeti = ?,
                karar_sonuc_ozeti = ?,
                anahtar_kelimeler = ?,
                islenme_tarihi = ?
            WHERE id = ?
        """, (
            yeni_soru,
            yeni_ozet,
            yeni_sonuc,
            yeni_anahtar,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            karar_id,
        ))

        guncellenen += 1

        print(f"Güncellendi: {karar_no} | {yeni_anahtar}")

    con.commit()
    con.close()

    print("\nİşlem tamamlandı.")
    print(f"Güncellenen karar sayısı: {guncellenen}")


if __name__ == "__main__":
    main()