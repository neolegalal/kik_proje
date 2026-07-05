import sqlite3
import re


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - SORU KARAR ESLESME MOTORU")
print("="*70)



conn = sqlite3.connect(DB)
cursor = conn.cursor()



# Kullanıcı sorusu al

soru = input("\nHukuki sorunuzu yazınız: ")



def temizle(metin):

    metin = metin.lower()

    metin = re.sub(
        r"[^a-zA-ZçğıöşüÇĞİÖŞÜ0-9 ]",
        " ",
        metin
    )

    return set(metin.split())



soru_kelime = temizle(soru)



print("\nSoru kelimeleri:")
print(soru_kelime)



# karar kartlarını al

cursor.execute("""
SELECT

karar_no,
soru_basligi,
kisa_ozet,
hukuki_sorun,
gerekce,
sonuc,
emsal_ilke,
kategori

FROM ai_karar_kartlari

""")


kararlar = cursor.fetchall()



sonuclar=[]



for karar in kararlar:


    metin = " ".join([
        str(x) for x in karar
        if x
    ])


    karar_kelime = temizle(metin)


    ortak = soru_kelime.intersection(
        karar_kelime
    )


    if len(soru_kelime)>0:

        skor = int(
            len(ortak)
            /
            len(soru_kelime)
            *
            100
        )

    else:

        skor=0



    if skor>0:


        sonuclar.append(
            (
            skor,
            karar
            )
        )



# sırala

sonuclar.sort(
    key=lambda x:x[0],
    reverse=True
)



print()
print("="*70)
print("EMSAL KARAR ANALİZİ")
print("="*70)



if not sonuclar:

    print("Benzer karar bulunamadı.")


else:


    for skor, karar in sonuclar[:5]:


        print()
        print("-"*70)

        print("Karar No:")
        print(karar[0])

        print()

        print("Benzerlik:")
        print("%",skor)

        print()

        print("Konu:")
        print(karar[1])

        print()

        print("Kategori:")
        print(karar[7])



# log tablosu

cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_eslesme_log
(
id INTEGER PRIMARY KEY AUTOINCREMENT,
soru TEXT,
sonuc_sayisi INTEGER
)

""")


cursor.execute("""
INSERT INTO ai_eslesme_log
(soru,sonuc_sayisi)

VALUES (?,?)

""",
(
soru,
len(sonuclar)
))



conn.commit()
conn.close()



print()
print("✓ Eşleşme tamamlandı")