import sqlite3


print("=" * 70)
print("KAMU IHALE KARAR AI - HUKUKI ANALIZ MOTORU")
print("=" * 70)


soru = input("\nHukuki sorunuzu yaziniz: ").strip()


conn = sqlite3.connect(
    r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
)


c = conn.cursor()


kelimeler = [
    x.lower()
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



sonuclar = []



for r in rows:


    metin = " ".join([

        str(r[1] or ""),
        str(r[2] or ""),
        str(r[3] or ""),
        str(r[4] or ""),
        str(r[5] or "")

    ]).lower()



    puan = 0


    for kelime in kelimeler:

        if kelime in metin:

            puan += 1



    if puan > 0:

        sonuclar.append(
            (puan,r)
        )




sonuclar.sort(
    reverse=True,
    key=lambda x:x[0]
)




print("\n")
print("=" * 70)
print("HUKUKI ANALIZ")
print("=" * 70)



if not sonuclar:

    print("Benzer karar bulunamadı.")

    conn.close()

    exit()



secili = sonuclar[:5]



print("""

Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde uyuşmazlığın;


- teklif açıklamalarının mevzuata uygunluğu,
- sunulan belgelerin yeterliliği,
- maliyet unsurlarının açıklanabilirliği,
- ihale dokümanı hükümlerine uygunluk


yönlerinden incelendiği görülmektedir.



Benzer kararlarda özellikle;


- açıklamaların yeterli belge ile desteklenmesi,
- analiz girdilerinin doğru açıklanması,
- maliyet bileşenlerinin gerçekçi olması,
- mevzuatta belirtilen usullere uyulması


aranmaktadır.



""")



print("KARARLARDAN ELDE EDİLEN TESPİTLER")
print("-"*70)



gosterilen=[]



for puan,r in secili:


    if r[3] not in gosterilen:


        gosterilen.append(r[3])


        print("\n- " + r[3])




print("\n")


print("="*70)

print("SONUÇ")

print("="*70)



print("""

Sonuç olarak;

istekliler tarafından sunulan açıklamaların
mevzuatta belirtilen şartları sağlaması
gerekmektedir.


Açıklamaların yetersiz olması,
belgelendirme şartlarının karşılanmaması
veya maliyet unsurlarının açıklanamaması
halinde teklif açıklaması uygun bulunmayabilir.


""")



print("DAYANAK KARARLAR")
print("-"*70)



for puan,r in secili:

    print(
        "-",
        r[0]
    )



print("\n")
print("="*70)

print("AI HUKUKI ANALIZ TAMAMLANDI")

print("="*70)



conn.close()