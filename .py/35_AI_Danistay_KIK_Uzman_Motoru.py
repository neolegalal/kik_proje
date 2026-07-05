import sqlite3


print("=" * 70)
print("KAMU IHALE KARAR AI - KIK UZMAN ANALIZ MOTORU")
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





sonuclar=[]




for r in rows:


    metin = " ".join([

        str(r[1] or ""),
        str(r[2] or ""),
        str(r[3] or ""),
        str(r[4] or ""),
        str(r[5] or ""),
        str(r[6] or "")

    ]).lower()



    puan=0



    for kelime in kelimeler:

        if kelime in metin:

            puan += 1




    if puan>0:

        sonuclar.append(
            (puan,r)
        )




sonuclar.sort(

    reverse=True,

    key=lambda x:x[0]

)





print("\n")

print("="*70)

print("KIK UZMAN HUKUKI ANALIZ")

print("="*70)



if not sonuclar:


    print("Benzer karar bulunamadi.")

    conn.close()

    exit()



secili = sonuclar[:5]




print("""
HUKUKI KONU
--------------------------------------------------

Uyuşmazlık, ihale sürecinde istekliler tarafından
sunulan açıklama ve belgelerin mevzuata uygunluğu
ile açıklamanın yeterli olup olmadığı hususlarına
ilişkindir.



MEVZUAT VE DEGERLENDIRME
--------------------------------------------------

Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


- teklif açıklamalarının gerçekçi olması,

- açıklama yapılan maliyet unsurlarının
  dayanaklarının bulunması,

- sunulan belgelerin açıklamayı desteklemesi,

- ihale dokümanı ve mevzuat hükümlerine
  uygun hareket edilmesi


gerektiği görülmektedir.




KARARLARDAN ELDE EDİLEN UZMAN TESPİTLERİ
--------------------------------------------------

""")





gosterilen=set()



for puan,r in secili:


    if r[2] not in gosterilen:


        print("- " + r[2])

        print()


        gosterilen.add(r[2])





print("""
SONUÇ
--------------------------------------------------

Kamu İhale Kurulu uygulamasında;


açıklamanın yalnızca sunulmuş olması yeterli olmayıp,
açıklamanın dayanak belgelerle desteklenmesi
ve maliyet unsurlarının açıklanabilir nitelikte olması
aranmaktadır.


Bu şartların sağlanmaması halinde;

- teklif açıklaması uygun bulunmayabilir,

- isteklinin teklifi değerlendirme dışı bırakılabilir.


DAYANAK KARARLAR
--------------------------------------------------

""")




for puan,r in secili:


    print("-", r[0])




print("\n")

print("="*70)

print("AI KIK UZMAN ANALIZ TAMAMLANDI")

print("="*70)



conn.close()