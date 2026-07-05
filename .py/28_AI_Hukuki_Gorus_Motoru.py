import sqlite3


print("=" * 70)
print("KAMU IHALE KARAR SISTEMI - AI HUKUKI GORUS MOTORU")
print("=" * 70)



soru = input("\nHukuki sorunuzu yaziniz: ").strip().lower()



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
kk.anahtar_kelimeler,
kk.etiketler

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
        str(r[5] or ""),
        str(r[6] or "")
    ]).lower()



    puan=0



    for kelime in kelimeler:

        if len(kelime)>=4 and kelime in metin:

            puan+=1



    kategori=str(r[4]).lower()



    # AŞIRI DÜŞÜK ÖZEL FİLTRE

    if "a08" in kategori:

        if (
            "aşırı düşük" in soru
            or "asiri dusuk" in soru
        ):

            puan += 10



    else:


        if (
            "aşırı düşük" in soru
            or "asiri dusuk" in soru
        ):

            puan -= 5




    kritik=[
        "redded",
        "uygun bulunmadı",
        "uygun bulunmadi",
        "mevzuata aykırı",
        "mevzuata aykiri",
        "yetersiz",
        "değerlendirme dışı",
        "degerlendirme disi"
    ]



    for ifade in kritik:

        if ifade in metin:

            puan +=2




    if puan>=3:

        sonuclar.append((puan,r))




sonuclar.sort(
    key=lambda x:x[0],
    reverse=True
)




print("\n")
print("="*70)
print("AI HUKUKI GORUS")
print("="*70)



if not sonuclar:

    print("Ilgili karar bulunamadi.")
    conn.close()
    exit()




kararlar=[]
sonuclar_metni=[]



for puan,r in sonuclar[:5]:


    if r[0] not in kararlar:

        kararlar.append(r[0])



    if r[3] and r[3] not in sonuclar_metni:

        sonuclar_metni.append(r[3])




print("\nSORU")
print("-"*50)
print(soru)



print("\nHUKUKI DEGERLENDIRME")
print("-"*50)



print("""
Kamu Ihale Kurulu kararlarinda uyuşmazlik;

- teklif aciklamalarinin yeterliligi,
- analiz ve belgelerin mevzuata uygunlugu,
- maliyet unsurlarinin aciklanmasi

yonlerinden incelenmektedir.
""")



for x in sonuclar_metni:

    print("- "+x)




print("\nDAYANAK KARARLAR")
print("-"*50)



for k in kararlar:

    print("-",k)



print("\n")
print("="*70)

print("AI HUKUKI GORUS TAMAMLANDI")

print("="*70)



conn.close()