import sqlite3
import re


DB = "kik.db"


def temizle(metin):
    if not metin:
        return ""

    metin = metin.lower()

    turkce = {
        "ı":"i",
        "ğ":"g",
        "ü":"u",
        "ş":"s",
        "ö":"o",
        "ç":"c"
    }

    for k,v in turkce.items():
        metin = metin.replace(k,v)

    return metin


def kelimeler(metin):

    metin = temizle(metin)

    return set(
        re.findall(r"\w+", metin)
    )


def puanla(soru, kart):

    soru_kelime = kelimeler(soru)

    alanlar = [

        kart["baslik"],
        kart["hukuki_soru"],
        kart["iddia_ozeti"],
        kart["anahtar_kelime"],
        kart["emsal_ilke"]

    ]


    toplam = 0


    for alan in alanlar:

        alan_kelime = kelimeler(alan)

        ortak = soru_kelime.intersection(
            alan_kelime
        )

        if alan == kart["baslik"]:
            toplam += len(ortak)*5

        elif alan == kart["anahtar_kelime"]:
            toplam += len(ortak)*4

        elif alan == kart["hukuki_soru"]:
            toplam += len(ortak)*3

        else:
            toplam += len(ortak)


    return toplam



def ara(soru):

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()


    veriler = cursor.execute(
        """
        SELECT *
        FROM hukuki_kartlar
        """
    ).fetchall()


    sonuc=[]


    for kart in veriler:

        puan = puanla(
            soru,
            kart
        )

        if puan>2:

            sonuc.append(
                (
                    puan,
                    kart
                )
            )


    conn.close()


    sonuc.sort(
        key=lambda x:x[0],
        reverse=True
    )


    temiz=[]

    kararlar=set()


    for puan,kart in sonuc:

        if kart["id"] not in kararlar:

            temiz.append(
                (puan,kart)
            )

            kararlar.add(
                kart["id"]
            )


    return temiz[:3]




def cevap(soru):


    print("\n")
    print("="*70)
    print("HUKUKİ DEĞERLENDİRME")
    print("="*70)


    print("\nSorulan konu:")
    print(soru)


    sonuclar=ara(soru)



    if not sonuclar:

        print("\nEmsal karar bulunamadı.")
        return



    print("\nEMSAL KARAR ANALİZİ")
    print("-"*70)



    for puan,kart in sonuclar:


        print("\nKarar:")
        print(
            kart["karar_no"]
        )


        print("\nKonu:")
        print(
            kart["baslik"]
        )


        print("\nKurul yaklaşımı:")
        print(
            kart["kurul_degerlendirmesi"]
        )


        print("\nSonuç:")
        print(
            kart["sonuc"]
        )


        print("-"*70)



    print("\nGENEL HUKUKİ SONUÇ")

    print(
        sonuclar[0][1]["emsal_ilke"]
    )





def main():

    print("="*70)
    print(
    "KAMU IHALE KARAR AI - HUKUKİ FİLTRELEME MOTORU"
    )
    print("="*70)


    while True:


        soru=input(
            "\nHukuki soru (çıkış:q): "
        )


        if soru=="q":
            break


        cevap(soru)



if __name__=="__main__":
    main()