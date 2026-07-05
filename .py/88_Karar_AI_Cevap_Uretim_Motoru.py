import sqlite3
import difflib

print("="*70)
print("KAMU IHALE KARAR AI - CEVAP URETIM MOTORU")
print("="*70)


DB = "kik.db"


def benzerlik(a,b):
    return difflib.SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()



def cevap_uret(soru):

    con = sqlite3.connect(DB)
    c = con.cursor()


    kartlar = c.execute("""
    SELECT
    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke

    FROM hukuki_kartlar

    """).fetchall()


    bulunan=[]


    for k in kartlar:

        puan = 0

        puan += benzerlik(
            soru,
            k[2]
        )

        puan += benzerlik(
            soru,
            k[1]
        )


        if soru.lower() in k[1].lower():
            puan += 1


        bulunan.append(
            (
            puan,
            k
            )
        )


    bulunan.sort(
        reverse=True,
        key=lambda x:x[0]
    )


    if not bulunan or bulunan[0][0] < 0.25:

        print("\nEmsal karar bulunamadı.")
        return



    secilen = bulunan[0][1]


    print("\n")
    print("="*70)

    print("HUKUKİ DEĞERLENDİRME")

    print()

    print(
    secilen[2]
    )


    print("\n")

    print("Kurul değerlendirmesi:")

    print(
    secilen[3]
    )


    print("\n")

    print("SONUÇ:")

    print(
    secilen[4]
    )


    print("\n")

    print("EMSAL İLKE:")

    print(
    secilen[5]
    )


    print("\nKaynak Karar:")

    print(
    secilen[0]
    )

    print("="*70)



def main():

    while True:

        soru=input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru=="q":
            break


        cevap_uret(soru)



if __name__=="__main__":
    main()