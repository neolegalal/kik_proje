import sqlite3


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - AI HUKUKİ SORU CEVAP MOTORU")
print("="*70)


soru = input("\nHukuki sorunuzu yazınız: ")


conn = sqlite3.connect(
r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
)

c = conn.cursor()



# kelimeleri ayır
kelimeler = [
x.lower()
for x in soru.replace("?","").split()
]


sonuclar = []


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



for r in rows:


    metin = " ".join(
    [
    str(r[1]),
    str(r[2]),
    str(r[3]),
    str(r[4]),
    str(r[5])
    ]
    ).lower()



    puan = 0


    for kelime in kelimeler:

        if kelime in metin:
            puan += 1



    if puan > 0:

        sonuclar.append(
        (
        puan,
        r
        )
        )



# yüksek eşleşme üstte

sonuclar.sort(
reverse=True,
key=lambda x:x[0]
)



print("\n")
print("="*70)
print(" AI HUKUKİ CEVAP")
print("="*70)



if not sonuclar:


    print("İlgili karar bulunamadı.")



else:


    print(
    "İlgili karar sayısı:",
    len(sonuclar)
    )


    for puan,r in sonuclar[:5]:


        print("\n")
        print("-"*60)

        print("Karar:",r[0])

        print("\nUyuşmazlık:")
        print(r[1])

        print("\nÖzet:")
        print(r[2])

        print("\nSonuç:")
        print(r[3])

        print("\nKategori:")
        print(r[4])

        print("\nMevzuat:")
        print(r[6])



print("\n")
print("="*70)
print(" AI SORU CEVAP TAMAMLANDI")
print("="*70)


conn.close()