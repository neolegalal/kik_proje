import sqlite3
import re


DB = "kik.db"


def normalize(metin):

    if not metin:
        return ""

    metin = metin.lower()

    degisim = {
        "ı":"i",
        "ş":"s",
        "ğ":"g",
        "ü":"u",
        "ö":"o",
        "ç":"c"
    }

    for a,b in degisim.items():
        metin = metin.replace(a,b)

    return metin



def kelime_eslesme(soru, metin):

    soru = normalize(soru)
    metin = normalize(metin)

    kelimeler = soru.split()

    skor = 0

    for k in kelimeler:

        if len(k) > 2 and k in metin:
            skor += 1

    return skor



def mevzuat_analiz(soru):

    soru = normalize(soru)

    sonuc = []


    if (
        "iki sirket" in soru
        or "ayni kisi" in soru
        or "birden fazla teklif" in soru
        or "iki sirketle teklif" in soru
    ):

        sonuc.append({

            "kanun":
            "4734 sayılı Kamu İhale Kanunu",

            "madde":
            "Madde 17/d",

            "konu":
            "Yasak fiil ve davranışlar - Birden fazla teklif verme yasağı",

            "aciklama":
            "İhalelerde istekliler tarafından birden fazla teklif verilmesi yasaktır."

        })


    return sonuc




def ilgili_kararlari_getir(soru):

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    veriler = cursor.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    guven


    FROM hukuki_kartlar

    """).fetchall()


    conn.close()



    analiz = []



    for v in veriler:


        metin = " ".join([

            str(v[1]),
            str(v[2]),
            str(v[3]),
            str(v[5])

        ])


        skor = kelime_eslesme(
            soru,
            metin
        )


        if skor >= 2:

            analiz.append({

                "karar_no":v[0],
                "konu":v[1],
                "soru":v[2],
                "yaklasim":v[3],
                "sonuc":v[4],
                "ilke":v[5],
                "skor":skor

            })



    analiz.sort(
        key=lambda x:x["skor"],
        reverse=True
    )



    return analiz[:5]




def guven_hesapla(skor):

    if skor >= 5:
        return "Çok yüksek"

    elif skor >=3:
        return "Yüksek"

    else:
        return "Orta"





def calistir(soru):


    print("\n")
    print("="*70)
    print("KAMU IHALE KARAR AI - MEVZUAT BAGLANTI MOTORU v2")
    print("="*70)



    print("\nSORULAN KONU:")
    print(soru)



    print("\n")
    print("İLGİLİ MEVZUAT")
    print("-"*70)



    mevzuatlar = mevzuat_analiz(soru)



    for m in mevzuatlar:


        print("\nKanun:")
        print(m["kanun"])


        print("\nMadde:")
        print(m["madde"])


        print("\nKonu:")
        print(m["konu"])


        print("\nAçıklama:")
        print(m["aciklama"])


        print("-"*70)





    print("\n")
    print("EN UYGUN EMSAL KARARLAR")
    print("-"*70)



    kararlar = ilgili_kararlari_getir(soru)



    if not kararlar:

        print(
        "Uygun emsal karar bulunamadı."
        )


    for i,k in enumerate(kararlar,1):


        print("\n")
        print(
        f"{i}. EMSAL KARAR"
        )


        print("\nKarar:")
        print(k["karar_no"])



        print("\nHukuki Konu:")
        print(k["konu"])



        print("\nHukuki Sorun:")
        print(k["soru"])



        print("\nKurul Yaklaşımı:")
        print(k["yaklasim"])



        print("\nSonuç:")
        print(k["sonuc"])



        print("\nEmsal İlke:")
        print(k["ilke"])



        print("\nBenzerlik Güveni:")
        print(
            guven_hesapla(k["skor"])
        )


        print("-"*70)





    print("\n")
    print("="*70)
    print("HUKUKİ BAĞLANTI SONUCU")
    print("="*70)



    print("""

Mevzuat hükümleri ile Kamu İhale Kurulu kararları
birlikte değerlendirilmiştir.

Benzer uyuşmazlıklarda;

- teklif verme davranışı,
- istekliler arasındaki ilişki,
- yasak fiil ve davranış hükümleri,
- Kurul uygulaması

birlikte dikkate alınmalıdır.

Bu çıktı emsal karar + mevzuat bağlantılı
yapay zeka hukuki analizidir.

""")





def main():


    while True:


        soru = input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru.lower()=="q":
            break


        calistir(soru)





if __name__=="__main__":

    main()