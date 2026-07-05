import sqlite3
import json
import os
from datetime import datetime
from openai import OpenAI


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - IDDIA SEGMENTASYON MOTORU")
print("="*70)



# OPENAI BAGLANTI

api_key = os.getenv("OPENAI_API_KEY")


if not api_key:
    print("HATA: OPENAI_API_KEY bulunamadı.")
    print("CMD:")
    print('setx OPENAI_API_KEY "API_KEYINIZ"')
    exit()


client = OpenAI(
    api_key=api_key
)



# DATABASE

conn = sqlite3.connect(DB)

cursor = conn.cursor()



# tablo oluştur

cursor.execute("""

CREATE TABLE IF NOT EXISTS karar_iddialari (

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_id INTEGER,

karar_no TEXT,

iddia_no INTEGER,

konu TEXT,

uzman_soru TEXT,

iddia_ozeti TEXT,

kurul_cevabi TEXT,

sonuc TEXT,

emsal_ilke TEXT,

guven TEXT,

olusturma_tarihi TEXT

)

""")


conn.commit()


print("Tablo hazır: karar_iddialari")



# karar kolonlarını kontrol et


kolonlar = cursor.execute(
"PRAGMA table_info(kararlar)"
).fetchall()


print()

print("Mevcut kolonlar:")

for k in kolonlar:
    print(k[1])



# kararları al


kararlar = cursor.execute("""


SELECT

id,

karar_no,

kart_kisa_ozet,

karar_sonucu,

emsal_degeri


FROM kararlar


""").fetchall()



print()

print("Analiz edilecek karar:")

print(len(kararlar))



# eski üretimleri temizle

cursor.execute(
"DELETE FROM karar_iddialari"
)

conn.commit()





def iddia_analizi(karar):


    karar_no = karar[1]

    ozet = karar[2] or ""

    sonuc = karar[3] or ""

    emsal = karar[4] or ""



    prompt = f"""

Sen kamu ihale hukuku uzmanısın.

Aşağıdaki Kamu İhale Kurulu kararını incele.

Bu karar içerisinde birden fazla şikayet konusu olabilir.

Her farklı hukuki iddiayı ayrı kart oluştur.

Örneğin:

- aşırı düşük teklif
- geçici teminat
- fiyat dışı unsur
- yeterlik belgesi
- ortaklık
- süre
- başvuru

gibi konuları ayrı değerlendir.


Her kart için JSON üret.


Alanlar:


konu

uzman_soru

iddia_ozeti

kurul_cevabi

sonuc

emsal_ilke



Karar No:

{karar_no}



Özet:

{ozet}



Sonuç:

{sonuc}



Emsal:

{emsal}



Sadece JSON döndür.



Format:

[
{{
"konu":"",
"uzman_soru":"",
"iddia_ozeti":"",
"kurul_cevabi":"",
"sonuc":"",
"emsal_ilke":""
}}
]

"""


    try:


        cevap = client.chat.completions.create(

            model="gpt-4o-mini",


            messages=[

                {
                    "role":"system",
                    "content":
                    "Kamu ihale hukuku karar analiz uzmanısın."
                },


                {
                    "role":"user",
                    "content":prompt
                }

            ],


            temperature=0.1

        )



        metin = cevap.choices[0].message.content


        metin = metin.replace("```json","")
        metin = metin.replace("```","")


        return json.loads(metin)



    except Exception as e:


        print()

        print("AI hata:")

        print(e)


        return []







toplam = 0



for karar in kararlar:


    print("-"*60)

    print("Analiz:")

    print(karar[1])


    sonuc = iddia_analizi(karar)



    sira = 1



    for kart in sonuc:


        cursor.execute("""


        INSERT INTO karar_iddialari

        (

        karar_id,

        karar_no,

        iddia_no,

        konu,

        uzman_soru,

        iddia_ozeti,

        kurul_cevabi,

        sonuc,

        emsal_ilke,

        guven,

        olusturma_tarihi

        )


        VALUES (?,?,?,?,?,?,?,?,?,?,?)


        """,


        (

        karar[0],

        karar[1],

        sira,

        kart.get("konu"),

        kart.get("uzman_soru"),

        kart.get("iddia_ozeti"),

        kart.get("kurul_cevabi"),

        kart.get("sonuc"),

        kart.get("emsal_ilke"),

        "Yüksek",

        datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
        )

        ))



        sira += 1

        toplam += 1





    conn.commit()



    print(
        "Üretilen iddia:",
        len(sonuc)
    )





print()

print("="*70)

print("IDDIA AYRISTIRMA TAMAMLANDI")

print("="*70)


print("Karar:")

print(len(kararlar))


print("Üretilen hukuki kart:")

print(toplam)


print("="*70)



conn.close()