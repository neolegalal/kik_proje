import sqlite3
import json
from datetime import datetime
from openai import OpenAI
import os


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - OPENAI HUKUK ANALIZ MOTORU")
print("="*70)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


conn = sqlite3.connect(DB)
cursor = conn.cursor()



cursor.execute("""
SELECT 
id,
karar_no,
tam_metin

FROM kararlar

WHERE ai_uzman_notu != 'OPENAI ANALIZ TAMAMLANDI'

OR ai_uzman_notu IS NULL

""")


kayitlar = cursor.fetchall()



print()
print("Analiz edilecek:")
print(len(kayitlar))
print()



for id, karar_no, metin in kayitlar:


    print("-"*60)
    print("Analiz:")
    print(karar_no)



    if not metin:
        continue



    # çok uzun metni sınırla

    metin = metin[:12000]



    prompt = f"""

Sen kamu ihale hukuku uzmanısın.

Aşağıdaki Kamu İhale Kurulu kararını analiz et.

Karar No:
{karar_no}


Karar Metni:

{metin}



Şu formatta JSON üret:


{{
"soru_basligi":"",
"kisa_ozet":"",
"sonuc":"",
"emsal_ilke":"",
"anahtar_kelimeler":"",
"uzman_notu":""
}}


Kurallar:

- Hukuki uzman dili kullan.
- Danışmanlıkta kullanılabilecek netlikte yaz.
- Kararın gerçek uyuşmazlığını tespit et.
- Sonucu açık yaz.
- Emsal ilkeyi belirt.


"""



    try:


        cevap = client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[
                {
                "role":"system",
                "content":
                "Kamu ihale hukuku analiz uzmanısın."
                },

                {
                "role":"user",
                "content":prompt
                }
            ],

            temperature=0.1
        )



        text = cevap.choices[0].message.content



        data = json.loads(text)



        cursor.execute("""

        UPDATE kararlar

        SET

        ai_soru_basligi=?,
        ai_kisa_ozet=?,
        ai_sonuc=?,
        ai_emsal_ilke=?,
        ai_anahtar_kelimeler=?,
        ai_uzman_notu=?,
        ai_analiz_tarihi=?


        WHERE id=?


        """,
        (

        data.get("soru_basligi"),
        data.get("kisa_ozet"),
        data.get("sonuc"),
        data.get("emsal_ilke"),
        json.dumps(data.get("anahtar_kelimeler"), ensure_ascii=False),
        "OPENAI ANALIZ TAMAMLANDI",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        id

        ))



        print("Tamamlandı:", karar_no)



    except Exception as e:

        print("HATA:")
        print(e)



conn.commit()



print()
print("="*70)
print("OPENAI ANALIZ TAMAMLANDI")
print()
print("İşlenen:")
print(len(kayitlar))
print("="*70)



conn.close()