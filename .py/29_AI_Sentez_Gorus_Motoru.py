import sqlite3


print("=" * 70)
print("KAMU IHALE KARAR SISTEMI - AI HUKUKI SENTEZ MOTORU")
print("=" * 70)



soru = input("\nHukuki sorunuzu yaziniz: ").strip()



conn = sqlite3.connect(
    r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
)

c = conn.cursor()



kelimeler = [
    x.lower()
    for x in soru.replace("?", " ").replace(",", " ").split()
]




rows = c.execute("""
SELECT

k.karar_no,

kk.soru_basligi,
kk.karar_ozeti,
kk.karar_sonucu,
kk.ana_kategori,
kk.anahtar_kelimeler


FROM karar_konulari kk


JOIN kararlar k

ON kk.karar_id = k.id

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


        if len(kelime)>3 and kelime in metin:

            puan += 1




    if "aşırı düşük" in soru.lower():

        if "a08" in str(r[4]).lower():

            puan += 10



    if puan >= 3:

        sonuclar.append(
            (puan,r)
        )




sonuclar.sort(
    key=lambda x:x[0],
    reverse=True
)





print("\n")
print("="*70)
print("AI HUKUKI GORUS")
print("="*70)




if not sonuclar:


    print("İlgili karar bulunamadı.")

    conn.close()

    exit()




secili=[]



for puan,r in sonuclar[:5]:


    if r not in secili:

        secili.append(r)





print("\nSORU")
print("-"*50)

print(soru)



print("\nHUKUKI DEGERLENDIRME")
print("-"*50)




if "aşırı düşük" in soru.lower():



    print("""
Aşırı düşük teklif açıklamalarına ilişkin
Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


4734 sayılı Kanun'un 38'inci maddesi
kapsamında istekliler tarafından sunulan
açıklamaların;


- açıklama istenilen iş kalemleri,
- analiz girdileri,
- maliyet bileşenleri,
- dayanak belgeler


yönünden mevzuata uygun ve yeterli şekilde
ortaya konulması gerektiği anlaşılmaktadır.



Kurul incelemelerinde;

açıklamaların yeterli belgeyle desteklenmemesi,
sunulan analizlerin ihale dokümanına uygun olmaması
veya maliyet unsurlarının gerçekçi şekilde
açıklanamaması durumlarında teklif
açıklamalarının uygun bulunmadığı görülmektedir.


""")



else:


    print("""
Kamu İhale Kurulu kararları birlikte
değerlendirildiğinde;


uyuşmazlıkların;

- mevzuata uygunluk,
- belge yeterliliği,
- ihale dokümanı hükümleri,
- teklif değerlendirme esasları


çerçevesinde incelendiği görülmektedir.


""")






print("KARARLARDAN ELDE EDİLEN TESPİTLER")
print("-"*50)



eklenen=[]



for r in secili:


    if r[3] and r[3] not in eklenen:


        eklenen.append(r[3])




for x in eklenen[:5]:


    print("- "+x)





print("\nSONUÇ")
print("-"*50)


print("""
Sonuç olarak;

istekliler tarafından yapılan açıklamaların
ihale mevzuatında belirlenen şartları taşıması
zorunludur.

Açıklamaların yeterli görülmemesi,
belgelendirme şartlarının sağlanmaması veya
mevzuata aykırı hususlar bulunması halinde
teklifin değerlendirme dışı bırakılması
sonucu ortaya çıkabilmektedir.


""")





print("\nDAYANAK KARARLAR")
print("-"*50)



gosterilen=[]



for r in secili:


    if r[0] not in gosterilen:


        gosterilen.append(r[0])


for k in gosterilen:


    print("-",k)




print("\n")
print("="*70)

print("AI HUKUKI SENTEZ TAMAMLANDI")

print("="*70)



conn.close()