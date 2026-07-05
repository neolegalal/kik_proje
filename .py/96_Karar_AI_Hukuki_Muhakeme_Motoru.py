import sqlite3


DB = "kik.db"


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
    guven
    FROM hukuki_kartlar
    """

    veriler = cursor.execute(sorgu).fetchall()

    bulunan = []

    for v in veriler:

        metin = " ".join([
            str(v[1]),
            str(v[2]),
            str(v[3]),
            str(v[5])
        ]).lower()


        skor = 0

        for kelime in kelimeler:
            if kelime in metin:
                skor += 10


        if skor > 0:
            bulunan.append((skor,v))


    bulunan.sort(reverse=True,key=lambda x:x[0])

    conn.close()

    return bulunan[:3]



def muhakeme(soru,sonuclar):


    print("\n")
    print("="*70)
    print("KAMU IHALE KARAR AI - HUKUKİ MUHAKEME MOTORU")
    print("="*70)


    print("""
SORULAN OLAY:
""")
    print(soru)



    print("\n")
    print("EMSAL KARARLARDAN HUKUKİ MUHAKEME")
    print("-"*70)



    if not sonuclar:

        print("Uygun emsal karar bulunamadı.")
        return



    for i,(skor,k) in enumerate(sonuclar,1):

        print("\n")
        print(f"{i}. EMSAL KARAR")
        print("-"*40)

        print("Karar No:")
        print(k[0])


        print("\nUyuşmazlık:")
        print(k[1])


        print("\nKurul Yaklaşımı:")
        print(k[3])


        print("\nSonuç:")
        print(k[4])

        print("\nEmsal İlke:")
        print(k[5])

        print("\nBenzerlik:")
        print(
            "yüksek"
            if skor >=20
            else "orta"
        )



    print("\n")
    print("="*70)
    print("HUKUKİ MUHAKEME SONUCU")
    print("="*70)


    print("""
Kamu İhale Kurulu uygulamasında;

- somut olayın özellikleri,
- isteklilerin davranışları,
- teklif verme yöntemi,
- mevzuat hükümleri,
- önceki Kurul kararları

birlikte değerlendirilmektedir.


Benzer uyuşmazlıklarda emsal kararlar,
hukuki değerlendirmede yol gösterici niteliktedir.

Bu değerlendirme emsal karar destekli yapay zeka analizidir.
""")



def main():

    while True:

        soru=input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru=="q":
            break


        sonuclar=ara(soru)

        muhakeme(
            soru,
            sonuclar
        )



if __name__=="__main__":
    main()