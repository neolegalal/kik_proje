import sqlite3


print("=" * 70)
print("KAMU IHALE KARAR AI - UZMAN GORUS MOTORU")
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


    metin=" ".join([


        str(r[1] or ""),
        str(r[2] or ""),
        str(r[3] or ""),
        str(r[4] or ""),
        str(r[5] or "")


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

print("UZMAN HUKUKI GORUS")

print("="*70)




if not sonuclar:


    print("Benzer karar bulunamadi.")

    conn.close()

    exit()




secili=sonuclar[:5]




print("""

HUKUKI KONU
--------------------------------------------------

Uyuşmazlık, istekliler tarafından sunulan teklif
açıklamalarının ihale mevzuatına uygun olup olmadığı
ve açıklamanın yeterli dayanaklarla desteklenip
desteklenmediği hususları kapsamında değerlendirilmiştir.



HUKUKI DEGERLENDIRME
--------------------------------------------------

Kamu İhale Kurulu kararları birlikte değerlendirildiğinde;


- açıklama istenilen unsurların açık ve anlaşılır olması,

- kullanılan maliyet bileşenlerinin dayanaklarının bulunması,

- analizlerin ihale dokümanı ve mevzuata uygun hazırlanması,

- sunulan belgelerin açıklamayı doğrular nitelikte olması


gerektiği görülmektedir.



KURUL YAKLASIMI
--------------------------------------------------

Kurul incelemelerinde;

sadece düşük fiyat verilmesi değil,
bu düşük fiyatın nasıl oluşturulduğu ve
belgelendirilip belgelendirilmediği önem taşımaktadır.



Açıklamalar;


- mevzuata aykırı,
- eksik,
- gerçekçi olmayan,
- belge ile desteklenmeyen


hususlar içeriyorsa uygun kabul edilmemektedir.



SONUC
--------------------------------------------------

Sonuç olarak;

aşırı düşük teklif açıklamalarının kabul edilebilmesi için
isteklinin maliyet avantajını somut belgelerle ortaya koyması
gerekmektedir.


Açıklamanın yeterli görülmemesi halinde teklifin
değerlendirme dışı bırakılması mümkündür.



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

print("AI UZMAN GORUS TAMAMLANDI")

print("="*70)



conn.close()