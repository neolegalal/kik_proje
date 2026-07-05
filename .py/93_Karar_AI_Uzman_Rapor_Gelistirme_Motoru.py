import sqlite3
import datetime
import re


DB = "kik.db"


def temizle(metin):
    if not metin:
        return ""

    return re.sub(
        r"\s+",
        " ",
        metin.strip()
    )


def baglanti():

    return sqlite3.connect(DB)


def ara(soru):

    conn = baglanti()
    cursor = conn.cursor()


    kelimeler = soru.lower().split()

    sorgu = """
    SELECT
    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    mevzuat,
    guven
    FROM hukuki_kartlar
    WHERE
    hukuki_soru LIKE ?
    OR baslik LIKE ?
    OR anahtar_kelime LIKE ?
    OR emsal_ilke LIKE ?
    """


    param = f"%{soru}%"


    cursor.execute(
        sorgu,
        (
            param,
            param,
            param,
            param
        )
    )


    sonuc = cursor.fetchall()


    if not sonuc:

        for kelime in kelimeler:

            cursor.execute(
            """
            SELECT
            karar_no,
            baslik,
            hukuki_soru,
            kurul_degerlendirmesi,
            sonuc,
            emsal_ilke,
            mevzuat,
            guven
            FROM hukuki_kartlar
            WHERE
            hukuki_soru LIKE ?
            OR baslik LIKE ?
            OR anahtar_kelime LIKE ?
            """,
            (
            f"%{kelime}%",
            f"%{kelime}%",
            f"%{kelime}%"
            )
            )


            sonuc += cursor.fetchall()



    conn.close()


    return sonuc



def guven_hesapla(metin):

    uzunluk = len(metin)


    if uzunluk > 150:
        return "Çok yüksek"

    elif uzunluk > 80:
        return "Yüksek"

    else:
        return "Orta"



def rapor_uret(soru):


    sonuclar = ara(soru)


    print("\n")
    print("="*70)
    print("KAMU IHALE KARAR AI - UZMAN RAPOR GELISTIRME")
    print("="*70)


    print("\nSORULAN KONU:")
    print(soru)



    if not sonuclar:

        print("\nEmsal karar bulunamadı.")
        return



    gorulen = set()


    raporlar = []



    for veri in sonuclar:


        karar_no = veri[0]


        if karar_no in gorulen:
            continue


        gorulen.add(karar_no)


        raporlar.append(veri)



    print("\n")
    print("EMSAL KARAR ANALİZİ")
    print("-"*70)



    for i, karar in enumerate(raporlar[:5],1):


        karar_no = karar[0]
        konu = temizle(karar[1])
        soru2 = temizle(karar[2])
        kurul = temizle(karar[3])
        sonuc = temizle(karar[4])
        ilke = temizle(karar[5])
        mevzuat = temizle(karar[6])


        güven = guven_hesapla(
            kurul + ilke
        )



        print("\n")
        print(f"{i}. EMSAL KARAR")
        print("-"*40)


        print("Karar No:")
        print(karar_no)


        print("\nHukuki Konu:")
        print(konu)


        print("\nHukuki Sorun:")
        print(soru2)



        print("\nKİK Yaklaşımı:")
        print(kurul)


        print("\nSonuç:")
        print(sonuc)


        print("\nEmsal İlke:")
        print(ilke)



        if mevzuat:

            print("\nMevzuat:")
            print(mevzuat)



        print("\nBenzerlik Güveni:")
        print(güven)



        print("-"*70)




    print("\n")
    print("="*70)

    print("GENEL HUKUKİ DEĞERLENDİRME")

    print("="*70)



    print(
    """

Kamu İhale Kurulu kararları birlikte değerlendirildiğinde;

Sorulan konu bakımından önceki kararlar,
aynı hukuki nitelikteki uyuşmazlıklarda
emsal yaklaşım oluşturmaktadır.

Değerlendirme yapılırken;

- isteklilerin işlem ve davranışları,
- ihale dokümanı hükümleri,
- ilgili mevzuat düzenlemeleri,
- Kurul'un önceki kararları

birlikte dikkate alınmalıdır.

Bu rapor emsal karar destekli yapay zeka değerlendirmesidir.

"""
    )



    print("="*70)



if __name__ == "__main__":


    while True:

        soru=input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru.lower()=="q":
            break


        rapor_uret(soru)