# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime
import re

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"

HEDEF_KONULAR = [
    "iş deneyim belgesi",
    "benzer iş",
    "iş ortaklığı",
    "yasaklama",
    "yaklaşık maliyet",
    "sınır değer",
    "alt yüklenici",
    "bilanço",
    "ciro",
    "kesin teminat",
]


def temizle(metin):
    if metin is None:
        return ""
    metin = str(metin)
    metin = re.sub(r"\s+", " ", metin)
    return metin.strip()


def var_mi(cur, karar_no, konu):
    row = cur.execute("""
        SELECT id FROM hukuki_kartlar
        WHERE karar_no = ?
          AND LOWER(IFNULL(anahtar_kelime,'')) LIKE ?
        LIMIT 1
    """, (karar_no, f"%{konu.lower()}%")).fetchone()
    return row is not None


def yeni_iddia_no(cur, karar_no):
    row = cur.execute("""
        SELECT MAX(iddia_no) FROM hukuki_kartlar
        WHERE karar_no = ?
    """, (karar_no,)).fetchone()

    if row and row[0]:
        return int(row[0]) + 1
    return 1


def baslik_uret(konu):
    return f"{konu.capitalize()} konusunda Kurul değerlendirmesi"


def hukuki_soru_uret(konu):
    sorular = {
        "iş deneyim belgesi": "İş deneyim belgesinin yeterlik kriteri olarak sunulması ve değerlendirilmesi hukuken nasıl yapılmalıdır?",
        "benzer iş": "Benzer iş tanımına uygunluk değerlendirmesi hangi esaslara göre yapılmalıdır?",
        "iş ortaklığı": "İş ortaklığı veya ortak girişim yapısının ihaleye katılım bakımından hukuki etkisi nedir?",
        "yasaklama": "İhalelere katılmaktan yasaklama yaptırımı hangi hallerde gündeme gelir?",
        "yaklaşık maliyet": "Yaklaşık maliyetin belirlenmesi ve değerlendirmeye etkisi nasıl ele alınmalıdır?",
        "sınır değer": "Sınır değer ve aşırı düşük teklif ilişkisi hangi esaslara göre değerlendirilmelidir?",
        "alt yüklenici": "Alt yüklenici çalıştırılmasına ilişkin düzenlemeler ihalede nasıl değerlendirilmelidir?",
        "bilanço": "Bilanço ve mali yeterlik kriterleri hangi esaslara göre değerlendirilmelidir?",
        "ciro": "Ciro veya iş hacmine ilişkin yeterlik kriterleri nasıl değerlendirilmelidir?",
        "kesin teminat": "Kesin teminatın sunulması ve gelir kaydedilmesi hangi hukuki esaslara tabidir?",
    }
    return sorular.get(konu, f"{konu} konusu hukuken nasıl değerlendirilmelidir?")


def sonuc_uret(karar_sonuc_ozeti, karar_sonucu):
    return temizle(karar_sonuc_ozeti) or temizle(karar_sonucu) or "Karar sonucu otomatik olarak özetlenmiştir."


def emsal_ilke_uret(konu):
    ilkeler = {
        "iş deneyim belgesi": "İş deneyim belgeleri, ihale dokümanında öngörülen yeterlik kriterleri ve benzer iş tanımı çerçevesinde değerlendirilmelidir.",
        "benzer iş": "Benzer iş değerlendirmesinde ihale dokümanında yapılan tanım esas alınır; isteklinin sunduğu işin bu tanıma uygunluğu somut olarak incelenmelidir.",
        "iş ortaklığı": "İş ortaklığı ve ortak girişimlerde ortakların yeterlikleri ve teklif ilişkileri ihale mevzuatındaki sınırlamalar çerçevesinde değerlendirilmelidir.",
        "yasaklama": "Yasaklama yaptırımı ancak mevzuatta öngörülen fiil ve şartların somut olayda gerçekleşmesi halinde uygulanabilir.",
        "yaklaşık maliyet": "Yaklaşık maliyet, tekliflerin değerlendirilmesinde tek başına eleme nedeni olmayıp somut ihale şartlarıyla birlikte değerlendirilmelidir.",
        "sınır değer": "Sınır değer hesabı ve aşırı düşük teklif değerlendirmesi mevzuatta belirlenen usul ve kriterlere uygun yapılmalıdır.",
        "alt yüklenici": "Alt yükleniciye ilişkin düzenlemeler ihale dokümanı, sözleşme hükümleri ve ilgili mevzuat birlikte dikkate alınarak değerlendirilmelidir.",
        "bilanço": "Bilanço oranları ve mali yeterlik belgeleri ihale dokümanında belirtilen kriterlere uygunluk bakımından incelenmelidir.",
        "ciro": "Ciro ve iş hacmi belgeleri, isteklinin ekonomik ve mali yeterliğini tevsik eden belgeler olarak değerlendirilmelidir.",
        "kesin teminat": "Kesin teminatın sunulması, iadesi veya gelir kaydedilmesi sözleşme ve ihale mevzuatındaki şartlara bağlıdır.",
    }
    return ilkeler.get(konu, f"{konu} konusunda Kurulun somut olay değerlendirmesi esas alınmalıdır.")


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    print("=" * 80)
    print("116 - KARAR TABLOSUNDAN HUKUKİ KART ÜRETİM MOTORU")
    print("=" * 80)

    rows = cur.execute("""
        SELECT
            karar_no,
            karar_soru_basligi,
            karar_ozeti,
            karar_sonuc_ozeti,
            karar_sonucu,
            anahtar_kelimeler,
            ilgili_mevzuat
        FROM kararlar
        WHERE anahtar_kelimeler IS NOT NULL
          AND TRIM(anahtar_kelimeler) <> ''
    """).fetchall()

    uretilen = 0
    atlanan = 0

    for row in rows:
        (
            karar_no,
            karar_soru_basligi,
            karar_ozeti,
            karar_sonuc_ozeti,
            karar_sonucu,
            anahtar_kelimeler,
            ilgili_mevzuat,
        ) = row

        anahtar_norm = temizle(anahtar_kelimeler).lower()

        for konu in HEDEF_KONULAR:
            if konu not in anahtar_norm:
                continue

            if var_mi(cur, karar_no, konu):
                atlanan += 1
                continue

            iddia_no = yeni_iddia_no(cur, karar_no)

            baslik = baslik_uret(konu)
            hukuki_soru = hukuki_soru_uret(konu)
            kurul_degerlendirmesi = temizle(karar_ozeti) or temizle(karar_soru_basligi)
            sonuc = sonuc_uret(karar_sonuc_ozeti, karar_sonucu)
            emsal_ilke = emsal_ilke_uret(konu)

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
                kurul_degerlendirmesi,
                sonuc,
                emsal_ilke,
                konu,
                datetime.now().strftime("%Y-%m-%d"),
                temizle(karar_ozeti),
                temizle(ilgili_mevzuat),
                "Orta",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))

            uretilen += 1
            print(f"Üretildi: {karar_no} | {konu}")

    con.commit()

    toplam = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]
    con.close()

    print("\nİşlem tamamlandı.")
    print(f"Üretilen kart : {uretilen}")
    print(f"Atlanan kart  : {atlanan}")
    print(f"Toplam kart   : {toplam}")


if __name__ == "__main__":
    main()