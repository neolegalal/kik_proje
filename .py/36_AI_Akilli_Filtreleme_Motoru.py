import sqlite3



print("=" * 70)
print("KAMU IHALE KARAR AI - AKILLI FILTRELEME MOTORU")
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


    puan = 0



    baslik = str(r[1] or "").lower()

    ozet = str(r[2] or "").lower()

    sonuc = str(r[3] or "").lower()

    kategori = str(r[4] or "").lower()

    anahtar = str(r[5] or "").lower()

    mevzuat = str(r[6] or "").lower()



    metin = " ".join([

        baslik,
        ozet,
        sonuc,
        kategori,
        anahtar,
        mevzuat

    ])




    # Genel kelime eşleşmesi

    for kelime in kelimeler:

        if kelime in metin:

            puan += 1





    # Başlık ağırlığı

    for kelime in kelimeler:

        if kelime in baslik:

            puan += 5





    # Kategori ağırlığı

    if "aşırı düşük" in kategori:

        if "aşırı" in soru:

            puan += 10





    # Anahtar kelime ağırlığı

    if "45.1.13" in soru:

        if "45.1.13" in mevzuat:

            puan += 10




    if "38" in soru:

        if "38" in mevzuat:

            puan += 10





    if puan > 0:

        sonuclar.append(
            (puan,r)
        )





sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)





print("\n")

print("="*70)

print("AKILLI HUKUKI ANALIZ")

print("="*70)





if not sonuclar:


    print("\nBenzer karar bulunamadi.")

    conn.close()

    exit()





print("\nSORU")

print("-"*50)

print(soru)




print("\nILGILI KARARLAR")

print("-"*50)





gosterilen=0





for puan,r in sonuclar[:5]:


    print()

    print(
        f"{r[0]}   | Ilgililik Puani: {puan}"
    )


    print(
        "Baslik:",
        r[1]
    )


    print(
        "\nTespit:"
    )


    print(
        r[2]
    )


    print(
        "\nSonuc:"
    )


    print(
        r[3]
    )


    print("-"*50)



    gosterilen += 1






print("\nUZMAN SONUC")

print("-"*50)


print("""
Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


uyuşmazlıklarda özellikle;


- teklif açıklamalarının mevzuata uygunluğu,

- belgelerin yeterliliği,

- maliyet unsurlarının açıklanabilirliği,

- ihale dokümanına uygunluk


kriterlerinin esas alındığı görülmektedir.


Açıklamaların yeterli dayanaklarla
desteklenmemesi halinde teklifin
uygun bulunmaması sonucu ortaya çıkabilir.
""")






print("\n")

print("="*70)

print("AI AKILLI FILTRELEME TAMAMLANDI")

print("="*70)



conn.close()