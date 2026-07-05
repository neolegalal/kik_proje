import sqlite3
import re
from difflib import SequenceMatcher

DB = "kik.db"


def temizle(metin):
    if not metin:
        return ""

    metin = metin.lower()

    degisim = {
        "ı":"i",
        "ğ":"g",
        "ü":"u",
        "ş":"s",
        "ö":"o",
        "ç":"c"
    }

    for a,b in degisim.items():
        metin = metin.replace(a,b)

    metin = re.sub(r'[^a-z0-9 ]',' ',metin)

    return metin



def benzerlik(a,b):

    a = temizle(a)
    b = temizle(b)

    return SequenceMatcher(None,a,b).ratio()



def kelime_eslesme(soru,metin):

    soru = temizle(soru)
    metin = temizle(metin)

    kelimeler = soru.split()

    puan=0

    for k in kelimeler:

        if k in metin:
            puan +=1


    return puan



def ara(soru):

    con = sqlite3.connect(DB)

    cur = con.cursor()


    cur.execute("""
    SELECT 
    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke

    FROM hukuki_kartlar

    """)


    kartlar = cur.fetchall()


    sonuc=[]


    for k in kartlar:


        karar,baslik,hukuki,kurul,sonuc_text,ilke = k


        toplam=0


        # başlık ağırlıklı
        toplam += kelime_eslesme(
            soru,
            baslik
        ) * 5


        # soru
        toplam += kelime_eslesme(
            soru,
            hukuki
        ) * 3


        # kurul
        toplam += kelime_eslesme(
            soru,
            kurul
        )


        # benzerlik
        toplam += benzerlik(
            soru,
            baslik
        ) * 10



        if toplam>0:

            sonuc.append(
                (
                toplam,
                karar,
                baslik,
                hukuki,
                kurul,
                sonuc_text,
                ilke
                )
            )


    con.close()



    sonuc.sort(
        reverse=True,
        key=lambda x:x[0]
    )


    return sonuc[:5]




def main():

    print("="*70)
    print("KAMU IHALE KARAR AI - GELISTIRILMIS ARAMA")
    print("="*70)



    while True:


        soru=input(
            "\nHukuki soru (çıkış:q): "
        )


        if soru=="q":
            break



        print("\nSONUÇLAR\n")


        cevap=ara(soru)



        if not cevap:

            print(
            "Emsal karar bulunamadı."
            )

            continue



        for i,c in enumerate(cevap,1):

            print("-"*70)

            print(
            "SONUÇ:",
            i
            )


            print(
            "Karar:",
            c[1]
            )


            print(
            "Konu:",
            c[2]
            )


            print(
            "\nSoru:"
            )

            print(c[3])


            print(
            "\nKurul değerlendirmesi:"
            )

            print(c[4])


            print(
            "\nSonuç:"
            )

            print(c[5])


            print(
            "\nEmsal ilke:"
            )

            print(c[6])



if __name__=="__main__":
    main()