import sqlite3


print("=" * 70)
print("KAMU IHALE KARAR AI - HUKUKI AGIRLIKLI BENZERLIK MOTORU")
print("=" * 70)



soru = input("\nHukuki sorunuzu yaziniz: ").strip().lower()



conn = sqlite3.connect(
    r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
)


c = conn.cursor()



# genel kelimeler düşük ağırlık
agirliklar = {


    "mevzuata":5,
    "aykırı":5,
    "belge":5,
    "belgeler":5,
    "analiz":5,
    "analizlerin":5,
    "maliyet":5,
    "maliyet unsuru":6,
    "açıklama":4,
    "açıklaması":4,
    "reddedilmesi":6,
    "değerlendirme dışı":6,
    "uygun":3,
    "45.1.13":8,
    "tebliğ":5,
    "birim fiyat":6,
    "iş kalemi":5,


    "aşırı":1,
    "düşük":1,
    "teklif":1

}







rows=c.execute("""

SELECT

karar_no,
soru,
ozet,
sonuc,
kategori,
anahtar,
mevzuat

FROM ai_hazirlik

""").fetchall()






sonuclar=[]





for r in rows:



    alanlar=[

        str(r[1] or "").lower(),
        str(r[2] or "").lower(),
        str(r[3] or "").lower(),
        str(r[4] or "").lower(),
        str(r[5] or "").lower(),
        str(r[6] or "").lower()

    ]


    metin=" ".join(alanlar)



    puan=0

    nedenler=[]





    for kelime,agirlik in agirliklar.items():



        if kelime in soru:



            if kelime in metin:


                puan += agirlik


                nedenler.append(

                    kelime + 
                    " (+" +
                    str(agirlik)+
                    ")"

                )





    if puan>0:


        sonuclar.append(

            (
                puan,
                r,
                nedenler

            )

        )







sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)







print("\n")

print("="*70)

print("HUKUKI EMSAL BENZERLIK ANALIZI")

print("="*70)




print("\nSORU")

print("-"*50)

print(soru)






print("\nKARARLAR")

print("-"*50)





for puan,r,nedenler in sonuclar[:3]:


    skor=min(

        100,

        puan*4

    )



    print("\n")

    print("="*60)



    print(
        r[0]
    )


    print(

        "Benzerlik:",

        "%"+str(skor)

    )



    print("\nKONU")

    print("-"*30)

    print(
        r[1]
    )



    print("\nHUKUKI BENZERLIK NEDENLERI")

    print("-"*30)



    for n in set(nedenler):

        print(
            "✓",
            n
        )




    print("\nKARAR OZETI")

    print("-"*30)

    print(
        r[2]
    )



    print("\nKARAR SONUCU")

    print("-"*30)

    print(
        r[3]
    )






print("\n")

print("="*70)

print("UZMAN SONUC")

print("="*70)



print("""

Kamu İhale Kurulu kararları
değerlendirildiğinde;


benzer uyuşmazlıklarda;


- açıklama yöntemleri,
- maliyet unsurları,
- belge yeterliliği,
- mevzuata uygunluk


kriterlerinin esas alındığı görülmektedir.


Benzerlik değerlendirmesinde
yalnızca konu değil,
hukuki gerekçe ve sonuçlar
birlikte dikkate alınmıştır.

""")




print("="*70)

print("AI HUKUKI AGIRLIKLI BENZERLIK TAMAMLANDI")

print("="*70)



conn.close()