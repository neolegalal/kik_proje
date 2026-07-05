import sqlite3
import re


DB = "kik.db"


def baslik():

    print("=" * 70)
    print("KAMU IHALE KARAR AI - HUKUKİ BAĞLAM ANALİZ MOTORU")
    print("=" * 70)



def kelime_cikar(metin):

    metin = metin.lower()

    kelimeler = re.findall(
        r"[a-zçğıöşü0-9]+",
        metin
    )

    return kelimeler



def hukuki_konu_analiz(soru):


    kelimeler = kelime_cikar(soru)


    konu_haritasi = {


        "teklif": [
            "teklif",
            "şirket",
            "ortak",
            "aynı kişi",
            "birden fazla"
        ],


        "birden fazla teklif verme yasağı": [

            "aynı",
            "kişi",
            "şirket",
            "iki",
            "birden fazla",
            "teklif"
        ],


        "aşırı düşük teklif": [

            "aşırı",
            "düşük",
            "fiyat",
            "açıklama"
        ],


        "teminat": [

            "teminat",
            "geçici",
            "kesin"

        ]

    }


    skorlar={}


    for konu,anahtarlar in konu_haritasi.items():

        skor=0


        for a in anahtarlar:

            if a in soru.lower():

                skor+=1


        skorlar[konu]=skor



    en_iyi=max(
        skorlar,
        key=skorlar.get
    )


    return en_iyi





def karar_ara(soru):


    conn = sqlite3.connect(DB)

    cursor = conn.cursor()



    konu = hukuki_konu_analiz(soru)



    arama = "%" + konu.lower() + "%"



    cursor.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    guven


    FROM hukuki_kartlar


    WHERE

    lower(baslik) LIKE ?

    OR lower(hukuki_soru) LIKE ?

    OR lower(emsal_ilke) LIKE ?


    LIMIT 5


    """,

    (

    arama,
    arama,
    arama

    ))



    sonuc = cursor.fetchall()


    conn.close()



    return sonuc





def baglam_analiz(soru, kararlar):


    print("\n")
    print("="*70)
    print("HUKUKİ BAĞLAM ANALİZİ")
    print("="*70)



    print("\nSorulan konu:")

    print(soru)



    if not kararlar:

        print("\nUygun emsal karar bulunamadı.")

        return



    print("\n")
    print("EN UYGUN EMSAL KARARLAR")
    print("-"*70)



    for i,k in enumerate(kararlar,1):


        print(f"""

{i}. EMSAL KARAR

Karar:
{k[0]}


Hukuki Konu:
{k[1]}


Hukuki Sorun:
{k[2]}


Kurul Yaklaşımı:
{k[3]}


Sonuç:
{k[4]}


Emsal İlke:
{k[5]}


Güven:
{k[6]}


----------------------------------------

""")



    print("="*70)

    print("UZMAN HUKUKİ DEĞERLENDİRME")

    print("="*70)



    print("""
Uyuşmazlık bakımından değerlendirme yapılırken;

- istekliler arasındaki hukuki ilişki,
- teklif verme davranışı,
- ihale mevzuatındaki yasak fiil hükümleri,
- Kamu İhale Kurulu'nun önceki kararları

birlikte dikkate alınmalıdır.


Bu analiz, emsal karar verileri üzerinden
hukuki bağlam çıkarımı yapmaktadır.
""")



    print("="*70)





def main():


    baslik()


    while True:


        soru=input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru.lower()=="q":

            break



        kararlar = karar_ara(soru)


        baglam_analiz(
            soru,
            kararlar
        )





if __name__=="__main__":

    main()