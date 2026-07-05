import sqlite3
import json
import datetime
from openai import OpenAI


DB = "kik.db"


with open("api_key.txt","r",encoding="utf-8") as f:
    API_KEY = f.read().strip()


client = OpenAI(
    api_key=API_KEY
)


conn = sqlite3.connect(DB)
cursor = conn.cursor()



print("="*70)
print("KAMU IHALE KARAR AI - TOPLU OZETLEME MOTORU")
print("="*70)



TEST_LIMIT = 5



cursor.execute("""
SELECT

id,
karar_no,
tam_metin,
ilgili_mevzuat

FROM kararlar

WHERE tam_metin IS NOT NULL

LIMIT ?

""",(TEST_LIMIT,))


kararlar = cursor.fetchall()



if not kararlar:

    print("Analiz edilecek karar bulunamadı.")
    exit()



for karar in kararlar:


    karar_id = karar[0]
    karar_no = karar[1]
    metin = karar[2]
    mevzuat = karar[3]



    print("\n")
    print("-"*70)
    print("Analiz edilen karar:", karar_no)



    prompt = f"""

Sen Kamu İhale Hukuku uzmanısın.

Aşağıdaki Kamu İhale Kurulu kararını analiz et.


KARAR:

{metin[:12000]}



Aşağıdaki alanları JSON olarak üret:



{{
"soru_basligi":"",
"kisa_ozet":"",
"hukuki_sorun":"",
"gerekce":"",
"sonuc":"",
"emsal_ilke":"",
"mevzuat":"",
"anahtar_kelimeler":""
}}



Kurallar:

- Soru başlığı uzman araması için hazırlanmalı.
- Özet kısa ve anlaşılır olmalı.
- Hukuki sorun tek cümle olmalı.
- Gerekçe Kurul değerlendirmesini açıklamalı.
- Sonuç net yazılmalı.
- Emsal ilke gelecekte kullanılabilecek hukuk prensibi olmalı.

"""



    try:



        response = client.chat.completions.create(


            model="gpt-5-mini",


            messages=[

                {
                "role":"system",
                "content":
                "Kamu ihale karar analiz uzmanısın."
                },


                {
                "role":"user",
                "content":prompt
                }

            ]

        )



        text = response.choices[0].message.content



        temiz = (
            text
            .replace("```json","")
            .replace("```","")
            .strip()
        )



        data=json.loads(temiz)



        cursor.execute("""


        INSERT INTO ai_karar_kartlari


        (

        karar_id,
        karar_no,

        soru_basligi,
        kisa_ozet,

        hukuki_sorun,

        gerekce,
        sonuc,

        emsal_ilke,

        mevzuat,

        anahtar_kelimeler,

        olusturma_tarihi

        )


        VALUES

        (?,?,?,?,?,?,?,?,?,?,?)



        """,


        (

        karar_id,
        karar_no,

        data.get("soru_basligi"),
        data.get("kisa_ozet"),

        data.get("hukuki_sorun"),

        data.get("gerekce"),
        data.get("sonuc"),

        data.get("emsal_ilke"),

        data.get("mevzuat"),

        data.get("anahtar_kelimeler"),

        datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        ))



        conn.commit()



        print("✓ AI KARAR KARTI KAYDEDİLDİ")

        print(
            data.get("soru_basligi")
        )



    except Exception as e:


        print("HATA:")
        print(e)



conn.close()



print("\n")
print("="*70)
print("AI KARAR OZETLEME TAMAMLANDI")
print("="*70)