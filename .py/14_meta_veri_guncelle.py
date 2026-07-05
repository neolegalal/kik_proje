import sqlite3
import re

DB = "kik.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - META VERİ GÜNCELLEME MOTORU")
print("="*70)


kararlar = cursor.execute("""
SELECT id, tam_metin, karar_no, karar_tarihi, idare_adi, ihale_kayit_no
FROM kararlar
""").fetchall()


for k in kararlar:

    id = k[0]
    metin = k[1] or ""

    print("Analiz:", k[2])


    # İL
    il = ""

    iller = [
        "İstanbul","Ankara","İzmir","Erzurum",
        "Bursa","Konya","Antalya","Adana",
        "Kocaeli","Trabzon","Samsun"
    ]

    for x in iller:
        if x.lower() in metin.lower():
            il=x
            break


    # İDARE TÜRÜ
    idare_turu=""

    if "Belediye" in metin:
        idare_turu="Belediye"

    elif "Bakanlığı" in metin:
        idare_turu="Bakanlık"

    elif "Genel Müdürlüğü" in metin:
        idare_turu="Genel Müdürlük"

    elif "Üniversitesi" in metin:
        idare_turu="Üniversite"



    # SEKTÖR

    sektor=""

    if "inşaat" in metin.lower() or "yapım işi" in metin.lower():
        sektor="İnşaat"

    elif "altyapı" in metin.lower():
        sektor="Altyapı"

    elif "temizlik" in metin.lower():
        sektor="Hizmet"

    elif "mal alımı" in metin.lower():
        sektor="Mal"



    # BAŞVURU TÜRÜ

    basvuru=""

    if "itirazen şikayet" in metin.lower():
        basvuru="İtirazen Şikayet"

    elif "şikayet başvurusu" in metin.lower():
        basvuru="Şikayet"



    # BAŞVURAN TİPİ

    basvuran=""

    if "iş ortaklığı" in metin.lower():
        basvuran="İş Ortaklığı"

    elif "limited" in metin.lower():
        basvuran="Şirket"



    # UYUŞMAZLIK AŞAMASI

    asama=""

    if "ihalenin iptali" in metin.lower():
        asama="İhale İptali"

    elif "teklif değerlendirme" in metin.lower():
        asama="Teklif Değerlendirme"



    # HAKLILIK

    haklilik=""

    if "iddiasının yerinde olduğu" in metin.lower():
        haklilik="Başvuru Haklı"

    elif "iddiasının yerinde olmadığı" in metin.lower():
        haklilik="Başvuru Haksız"



    cursor.execute("""
    UPDATE kararlar SET

    il=?,
    idare_turu=?,
    sektor=?,
    basvuru_turu=?,
    basvuran_tipi=?,
    uyusmazlik_asamasi=?,
    haklilik_durumu=?

    WHERE id=?

    """,
    (
    il,
    idare_turu,
    sektor,
    basvuru,
    basvuran,
    asama,
    haklilik,
    id
    ))



conn.commit()


print()
print("="*70)
print(" META VERİ GÜNCELLEME TAMAMLANDI")
print("="*70)


conn.close()