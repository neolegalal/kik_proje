import sqlite3



print("=" * 70)
print("KAMU IHALE KARAR AI - GERCEK BENZERLIK SKORLAMA MOTORU")
print("=" * 70)



soru = input("\nHukuki sorunuzu yaziniz: ").strip().lower()



conn = sqlite3.connect(
    r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
)


c = conn.cursor()



kelimeler = [
    x
    for x in soru.replace("?", "").split()
]





rows = c.execute("""

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


    baslik = str(r[1] or "").lower()

    ozet = str(r[2] or "").lower()

    sonuc = str(r[3] or "").lower()

    kategori = str(r[4] or "").lower()

    anahtar = str(r[5] or "").lower()

    mevzuat = str(r[6] or "").lower()



    puan=0



    toplam_agirlik=0




    for kelime in kelimeler:


        toplam_agirlik += 1



        if kelime in baslik:

            puan += 5



        elif kelime in anahtar:

            puan += 4



        elif kelime in mevzuat:

            puan += 4



        elif kelime in ozet:

            puan += 2



        elif kelime in sonuc:

            puan += 1





    # kategori desteği


    if "aşırı düşük" in soru:

        if "aşırı düşük" in kategori:

            puan += 5





    if toplam_agirlik == 0:

        continue





    maksimum = (

        toplam_agirlik * 5

    ) + 5





    yuzde = int(

        (puan / maksimum) * 100

    )



    if yuzde > 100:

        yuzde=100




    if puan > 0:


        sonuclar.append(

            (
                yuzde,
                r

            )

        )






sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)







# karar tekilleştirme


tekil={}



for skor,r in sonuclar:


    if r[0] not in tekil:


        tekil[r[0]]=(skor,r)





sonuclar=list(tekil.values())



sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)







print("\n")

print("="*70)

print("GERCEK EMSAL KARAR ANALIZI")

print("="*70)





print("\nSORU")

print("-"*50)

print(soru)






print("\nEN BENZER KARARLAR")

print("-"*50)






for skor,r in sonuclar[:3]:


    print()


    print(
        r[0]
    )


    print(
        "Benzerlik Skoru:",
        "%"+str(skor)
    )



    print()


    print(
        "Konu:"
    )


    print(
        r[1]
    )



    print()


    print(
        "Tespit:"
    )


    print(
        r[2]
    )



    print()


    print(
        "Sonuc:"
    )


    print(
        r[3]
    )


    print("-"*60)






print("\nUZMAN DEGERLENDIRME")

print("-"*50)



print("""
Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


uyuşmazlıklarda;


- teklif açıklamalarının içeriği,

- maliyet unsurlarının açıklanması,

- dayanak belgelerin yeterliliği,

- mevzuata uygunluk


esas alınmaktadır.


Benzer kararlar doğrultusunda,
açıklamanın yeterli ve doğrulanabilir
olmaması halinde teklifin uygun
bulunmaması mümkündür.
""")






print("="*70)

print("AI GERCEK BENZERLIK TAMAMLANDI")

print("="*70)




conn.close()