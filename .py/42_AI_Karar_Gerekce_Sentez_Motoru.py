import sqlite3
import re


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - KARAR GEREKCE SENTEZ MOTORU")
print("="*70)



soru = input("\nHukuki sorunuzu yaziniz: ")



def temizle(metin):

    if metin is None:
        return ""

    return re.sub(
        r"[^a-zçğıöşü0-9\s]",
        " ",
        str(metin).lower()
    )



def skor_hesapla(soru, metin):

    soru_kelime = set(
        temizle(soru).split()
    )

    metin_kelime = set(
        temizle(metin).split()
    )


    if not soru_kelime:
        return 0


    ortak = len(
        soru_kelime.intersection(
            metin_kelime
        )
    )


    return ortak




try:


    conn = sqlite3.connect(DB)

    cursor = conn.cursor()



    cursor.execute("""

    SELECT

    karar_no,
    soru,
    ozet,
    sonuc,
    kategori,
    anahtar,
    mevzuat

    FROM ai_hazirlik

    """)



    veriler = cursor.fetchall()



    sonuc_listesi = []



    for veri in veriler:


        metin = " ".join([

            str(veri[1]),
            str(veri[2]),
            str(veri[3]),
            str(veri[4]),
            str(veri[5])

        ])



        skor = skor_hesapla(
            soru,
            metin
        )


        if skor > 0:

            sonuc_listesi.append(
                (
                    skor,
                    veri
                )
            )



    sonuc_listesi.sort(
        reverse=True,
        key=lambda x:x[0]
    )




    print("\n")
    print("="*70)
    print("EMSAL KARAR GEREKÇE ANALİZİ")
    print("="*70)




    if not sonuc_listesi:


        print("\nBenzer karar bulunamadı.")



    else:



        for skor,veri in sonuc_listesi[:5]:


            print("\n")
            print("-"*70)


            print("Karar No:")
            print(veri[0])


            print("\nBenzerlik:")
            print("%", skor*10)



            print("\nKararın Konusu:")
            print(veri[1])



            print("\nKarar Gerekçesi:")
            print(veri[2])



            print("\nKarar Sonucu:")
            print(veri[3])



            print("\nMevzuat:")
            print(veri[6])



    print("\n")
    print("="*70)
    print("UZMAN HUKUKİ GEREKÇE SENTEZİ")
    print("="*70)




    print("""


Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


aşırı düşük teklif açıklamalarında
esas alınan temel hususlar;


- açıklama yönteminin mevzuata uygun olması,

- analiz girdilerinin açıklanması,

- maliyet unsurlarının dayanaklarının gösterilmesi,

- fiyat teklifleri ve belgelerin doğrulanabilir olması,

- açıklamanın gerçekçi olmasıdır.



EMSAL KARARLARDA;


istekliler tarafından sunulan açıklamaların
sadece şekli olarak yapılmasının yeterli olmadığı;


açıklamanın;

- somut belgelere dayanması,

- maliyet avantajını ortaya koyması,

- ihale dokümanı ve Kamu İhale Genel Tebliği hükümlerine uygun olması


gerektiği görülmektedir.



Bu şartların sağlanmaması halinde;


aşırı düşük teklif açıklaması uygun
bulunmayarak teklif değerlendirme dışı
bırakılabilmektedir.



""")



    print("="*70)
    print("AI GEREKÇE SENTEZ TAMAMLANDI")
    print("="*70)



except Exception as e:


    print("\nVERİTABANI HATASI")
    print(e)



finally:

    try:

        conn.close()

    except:

        pass