import sqlite3
from datetime import datetime


DB = "kik.db"


def temizle(metin):
    if not metin:
        return ""
    return metin.strip()


def karar_getir(soru):

    conn = sqlite3.connect(DB)
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

    conn.close()


    sonuc=[]


    for v in veriler:

        skor=0

        metin=" ".join([
            str(v[1]),
            str(v[2]),
            str(v[3]),
            str(v[5])
        ]).lower()


        for k in kelimeler:
            if k in metin:
                skor+=10


        if skor>0:

            sonuc.append({

                "karar_no":v[0],
                "konu":v[1],
                "soru":v[2],
                "degerlendirme":v[3],
                "sonuc":v[4],
                "ilke":v[5],
                "guven":v[6],
                "skor":skor

            })


    sonuc.sort(
        key=lambda x:x["skor"],
        reverse=True
    )


    return sonuc[:5]



def gerekce_uret(soru, kararlar):


    print("\n")
    print("="*70)
    print("KAMU IHALE KARAR AI - HUKUKİ GEREKÇE ÇIKARIM MOTORU")
    print("="*70)


    print("\nSORULAN OLAY:")
    print(soru)


    print("\nEMSAL KARARLARDAN ÇIKARILAN GEREKÇELER")
    print("-"*70)


    if not kararlar:

        print("Uygun emsal karar bulunamadı.")
        return



    ilkeler=[]


    for i,k in enumerate(kararlar,1):


        print("\n")
        print(f"{i}. KARAR")
        print("-"*40)

        print("Karar No:")
        print(k["karar_no"])


        print("\nHukuki Konu:")
        print(k["konu"])


        print("\nKurul Gerekçesi:")
        print(
            temizle(k["degerlendirme"])
        )


        print("\nSonuç:")
        print(
            temizle(k["sonuc"])
        )


        print("\nEmsal İlke:")
        print(
            temizle(k["ilke"])
        )


        ilkeler.append(k["ilke"])



    print("\n")
    print("="*70)
    print("HUKUKİ GEREKÇE ANALİZİ")
    print("="*70)



    print("""
Kamu İhale Kurulu kararlarında uyuşmazlık değerlendirilirken;

- isteklilerin işlem ve davranışları,
- teklif verme şekli,
- ihale sürecindeki hukuki durum,
- ilgili mevzuat hükümleri,
- önceki Kurul kararları

birlikte değerlendirilmektedir.

Somut olay bakımından emsal kararların ortak yaklaşımı dikkate
alındığında, benzer uyuşmazlıklarda aynı hukuki değerlendirme
ilkeleri uygulanmaktadır.
""")


    print("\nÇIKARILAN EMSAL PRENSİPLER:")


    for i,x in enumerate(set(ilkeler),1):

        print(
            f"- {x}"
        )


    print("\n")
    print("="*70)



def main():

    while True:


        soru=input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru.lower()=="q":
            break


        kararlar=karar_getir(soru)

        gerekce_uret(
            soru,
            kararlar
        )



if __name__=="__main__":
    main()