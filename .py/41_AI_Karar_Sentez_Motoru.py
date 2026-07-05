import sqlite3
import re


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - KARAR SENTEZ MOTORU")
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



def benzerlik(soru, metin):

    soru_kelime = set(
        temizle(soru).split()
    )

    metin_kelime = set(
        temizle(metin).split()
    )


    if not soru_kelime:
        return 0


    ortak = len(
        soru_kelime.intersection(metin_kelime)
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



    kararlar = cursor.fetchall()



    analiz=[]



    for k in kararlar:


        metin = " ".join([

            str(k[1]),
            str(k[2]),
            str(k[3]),
            str(k[4]),
            str(k[5]),
            str(k[6])

        ])



        skor = benzerlik(
            soru,
            metin
        )


        if skor > 0:

            analiz.append(
                (
                    skor,
                    k
                )
            )



    analiz.sort(
        reverse=True,
        key=lambda x:x[0]
    )



    print("\n")
    print("="*70)
    print("KARAR SENTEZ ANALIZI")
    print("="*70)



    if len(analiz)==0:


        print("\nBenzer karar bulunamadı.")



    else:


        print("\nEMSAL KARARLAR")
        print("-"*70)



        for skor,k in analiz[:5]:


            print("\nKarar No:")
            print(k[0])


            print("\nBenzerlik Skoru:")
            print("%", skor*10)


            print("\nSoru Başlığı:")
            print(k[1])


            print("\nKarar Özeti:")
            print(k[2])


            print("\nKarar Sonucu:")
            print(k[3])


            print("\nKategori:")
            print(k[4])


            print("\nMevzuat:")
            print(k[6])


            print("-"*70)






    print("\n")
    print("="*70)
    print("UZMAN HUKUKİ SENTEZ")
    print("="*70)



    print("""


Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


aşırı düşük teklif açıklamalarında;


- açıklama yöntemleri,

- analiz girdileri,

- maliyet unsurlarının dayanakları,

- fiyat teklifleri,

- belgelerin yeterliliği,

- mevzuata uygunluk


hususları incelenmektedir.



İstekliler tarafından sunulan açıklamalar;


- somut belgelerle desteklenmeli,

- maliyet avantajını ortaya koymalı,

- gerçekçi ve doğrulanabilir olmalı,

- Kamu İhale Genel Tebliği hükümlerine uygun hazırlanmalıdır.



Açıklamanın;


- belge ile desteklenmemesi,

- analizlerin uygun olmaması,

- maliyet unsurlarının açıklanamaması,

- mevzuata aykırı yöntem kullanılması


halinde;


aşırı düşük teklif açıklaması uygun
bulunmayarak teklif değerlendirme
dışı bırakılabilir.



""")



    print("="*70)
    print("AI KARAR SENTEZ TAMAMLANDI")
    print("="*70)



except Exception as e:


    print("\nVERITABANI HATASI")
    print(e)



finally:


    try:
        conn.close()

    except:
        pass