"""
ADIM 1: Sifirdan veritabani kurulumu + PDF tam metinlerini yukle
22 sutunlu temiz tablo olusturur, tam metni doldurur.
Diger alanlar sonraki scriptlerle doldurulacak.

Kullanim: python 1_kurulum.py
PDF'ler:  ./pdfs/ klasorunde
Cikti:    ./kik.db
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    print("pdfplumber yok. Kur: pip install pdfplumber")
    exit(1)

PDF_KLASORU = "./pdfs"
DB_DOSYASI  = "./kik.db"
TOPLU_COMMIT = 100
LOG_ARALIGI  = 500


def db_olustur(baglanti):
    """22 sutunlu temiz tablo"""
    baglanti.execute("""
        CREATE TABLE IF NOT EXISTS kararlar (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            dosya_adi         TEXT UNIQUE,

            -- REGEX ALANLARI (1-15)
            karar_no          TEXT,
            karar_tarihi      TEXT,
            karar_yili        INTEGER,
            toplanti_no       TEXT,
            gundem_no         TEXT,
            basvuru_sahibi    TEXT,
            idare_adi         TEXT,
            ihale_kayit_no    TEXT,
            ihale_konusu      TEXT,
            ihale_turu        TEXT,
            ihale_usulu       TEXT,
            ihale_ili         TEXT,
            karar_sonucu      TEXT,
            oylama            TEXT,
            ilgili_mevzuat    TEXT,

            -- YAPAY ZEKA ALANLARI (16-20)
            karar_soru_basligi TEXT,
            karar_ozeti        TEXT,
            karar_sonuc_ozeti  TEXT,
            ana_kategori       TEXT,
            anahtar_kelimeler  TEXT,

            -- DIGER (21-22)
            tam_metin          TEXT,
            emsal_degeri       TEXT,

            -- Sistem
            islenme_tarihi     TEXT
        )
    """)
    baglanti.commit()


def pdf_metin_oku(pdf_yolu):
    metin = ""
    with pdfplumber.open(pdf_yolu) as pdf:
        for sayfa in pdf.pages:
            t = sayfa.extract_text()
            if t:
                metin += t + "\n"
    return metin.strip()


def islenmis_dosyalar(baglanti):
    return {row[0] for row in baglanti.execute("SELECT dosya_adi FROM kararlar")}


def main():
    pdf_klasoru = Path(PDF_KLASORU)
    if not pdf_klasoru.exists():
        print(f"HATA: '{PDF_KLASORU}' klasoru yok.")
        return

    pdf_listesi = sorted(pdf_klasoru.glob("*.pdf"))
    toplam = len(pdf_listesi)
    print(f"Bulunan PDF: {toplam}")
    if toplam == 0:
        print("PDF yok!")
        return

    baglanti = sqlite3.connect(DB_DOSYASI)
    baglanti.execute("PRAGMA journal_mode=WAL")
    db_olustur(baglanti)

    islenmis = islenmis_dosyalar(baglanti)
    print(f"Zaten islenmis: {len(islenmis)} | Kalan: {toplam - len(islenmis)}\n")

    basarili = hatali = atlanan = commit_sayac = 0
    baslangic = datetime.now()

    for i, pdf_yolu in enumerate(pdf_listesi, 1):
        dosya_adi = pdf_yolu.name
        if dosya_adi in islenmis:
            atlanan += 1
            continue
        try:
            tam_metin = pdf_metin_oku(pdf_yolu)
            if not tam_metin or len(tam_metin) < 50:
                tam_metin = "[BOS VEYA OKUNAMADI]"
                hatali += 1
            else:
                basarili += 1
            baglanti.execute(
                "INSERT OR REPLACE INTO kararlar (dosya_adi, tam_metin, islenme_tarihi) VALUES (?,?,?)",
                (dosya_adi, tam_metin, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            commit_sayac += 1
        except Exception as e:
            hatali += 1
            print(f"  HATA {dosya_adi}: {e}")

        if commit_sayac >= TOPLU_COMMIT:
            baglanti.commit()
            commit_sayac = 0
        if i % LOG_ARALIGI == 0 or i == toplam:
            gecen = (datetime.now() - baslangic).total_seconds()
            hiz = (basarili + hatali) / gecen if gecen > 0 else 0
            kalan = (toplam - i) / hiz if hiz > 0 else 0
            print(f"[{i}/{toplam}] Basarili:{basarili} Hatali:{hatali} "
                  f"Hiz:{hiz:.1f}/sn Kalan:~{kalan/60:.0f}dk")

    baglanti.commit()

    print("\n=== TAMAMLANDI ===")
    print(f"Basarili: {basarili} | Hatali: {hatali} | Atlanan: {atlanan}")

    # En uzun metin kontrolu
    print("\nEn uzun 3 metin:")
    for row in baglanti.execute(
        "SELECT dosya_adi, LENGTH(tam_metin) FROM kararlar ORDER BY LENGTH(tam_metin) DESC LIMIT 3"
    ):
        print(f"  {row[1]:>8d} karakter - {row[0][-40:]}")

    sayi = baglanti.execute("SELECT COUNT(*) FROM kararlar").fetchone()[0]
    print(f"\nToplam {sayi} karar veritabaninda. Sonraki adim: regex alanlari.")
    baglanti.close()


if __name__ == "__main__":
    main()
