import sqlite3



print("=" * 70)
print("KAMU IHALE KARAR AI - KARAR GEREKCE ANALIZ MOTORU")
print("=" * 70)



soru = input("\nHukuki sorunuzu yaziniz: ").strip().lower()



conn = sqlite3.connect(
    r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
)


c = conn.cursor()



kelimeler = soru.replace("?", "").split()





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


    karar_no=r[0]

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




    puan=0



    nedenler=[]





    for kelime in kelimeler:


        if kelime in baslik:

            puan+=5

            nedenler.append(
                kelime+" (başlık)"
            )


        elif kelime in anahtar:

            puan+=4

            nedenler.append(
                kelime+" (anahtar)"
            )



        elif kelime in mevzuat:

            puan+=4

            nedenler.append(
                kelime+" (mevzuat)"
            )


        elif kelime in ozet:

            puan+=2

            nedenler.append(
                kelime+" (tespit)"
            )



        elif kelime in sonuc:

            puan+=1





    if "aşırı düşük" in soru:


        if "aşırı düşük" in kategori:

            puan+=5

            nedenler.append(
                "Aşırı düşük teklif kategorisi"
            )





    if puan>0:


        sonuclar.append(

            (
                puan,
                r,
                list(set(nedenler))

            )

        )







sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)






# karar tekrarlarını kaldır


tekil={}



for puan,r,neden in sonuclar:


    if r[0] not in tekil:


        tekil[r[0]]=(puan,r,neden)





sonuclar=list(tekil.values())






print("\n")

print("="*70)

print("KARAR GEREKCE ANALIZI")

print("="*70)




print("\nSORU")

print("-"*50)

print(soru)






for puan,r,nedenler in sonuclar[:3]:


    skor=min(
        100,
        puan*10
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




    print("\nBENZERLIK NEDENLERİ")

    print("-"*30)


    for n in nedenler:

        print(
            "✓",
            n
        )





    print("\nKARAR TESPİTİ")

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

print("UZMAN DEĞERLENDİRME")

print("="*70)



print("""
Kamu İhale Kurulu kararlarının birlikte
değerlendirilmesi sonucunda;


uyuşmazlıklarda;


- teklif açıklamasının içeriği,
- maliyet unsurlarının açıklanması,
- belge yeterliliği,
- mevzuata uygunluk


hususları esas alınmaktadır.


Benzer kararlar doğrultusunda,
açıklamanın somut ve belgeli şekilde
ortaya konulamaması halinde teklif
açıklaması uygun kabul edilmeyebilir.
""")





print("="*70)

print("AI KARAR GEREKCE ANALIZ TAMAMLANDI")

print("="*70)



conn.close()