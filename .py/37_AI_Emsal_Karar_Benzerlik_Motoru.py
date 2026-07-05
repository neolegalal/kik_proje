import sqlite3



print("=" * 70)
print("KAMU IHALE KARAR AI - EMSAL KARAR BENZERLIK MOTORU")
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


    puan=0


    baslik=str(r[1] or "").lower()
    ozet=str(r[2] or "").lower()
    sonuc=str(r[3] or "").lower()
    kategori=str(r[4] or "").lower()
    anahtar=str(r[5] or "").lower()
    mevzuat=str(r[6] or "").lower()



    metin=" ".join([

        baslik,
        ozet,
        sonuc,
        kategori,
        anahtar,
        mevzuat

    ])




    for kelime in kelimeler:

        if kelime in metin:

            puan += 1




    # Başlık önemli

    for kelime in kelimeler:

        if kelime in baslik:

            puan += 5





    # kategori avantajı

    if "aşırı düşük" in soru:

        if "aşırı düşük" in kategori:

            puan += 10





    if puan > 0:

        sonuclar.append(
            (puan,r)
        )





sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)







# KARAR NUMARASI TEKILLESTIRME


tekil={}



for puan,r in sonuclar:


    karar=r[0]


    if karar not in tekil:

        tekil[karar]=(puan,r)




sonuclar=list(tekil.values())



sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)







print("\n")

print("="*70)

print("EMSAL KARAR ANALIZI")

print("="*70)





print("\nSORU")

print("-"*50)

print(soru)







print("\nEMSAL KARARLAR")

print("-"*50)







for puan,r in sonuclar[:3]:


    yuzde=min(

        100,

        puan*7

    )



    print()

    print(
        r[0]
    )



    print(
        "Benzerlik:",
        "%"+str(yuzde)
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
        "Sonuç:"
    )


    print(
        r[3]
    )


    print("-"*60)








print("\nUZMAN SONUÇ")

print("-"*50)



print("""

Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


aşırı düşük teklif açıklamalarında
istekliler tarafından;


- açıklama yapılan unsurların,

- maliyet bileşenlerinin,

- analizlerin,

- dayanak belgelerin


mevzuata uygun ve doğrulanabilir
şekilde ortaya konulması gerektiği
anlaşılmaktadır.



Açıklamaların yeterli bulunmaması
veya belgelerle desteklenmemesi halinde
teklif açıklaması uygun kabul edilmeyebilir.


""")





print("="*70)

print("AI EMSAL KARAR ANALIZ TAMAMLANDI")

print("="*70)



conn.close()