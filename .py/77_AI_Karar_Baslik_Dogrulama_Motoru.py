import sqlite3
import json
from datetime import datetime
from openai import OpenAI
import os


DB="kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - KARAR BASLIK DUZELTME MOTORU")
print("="*70)



client=OpenAI(
    api_key="OPENAI_API_KEY"
)



conn=sqlite3.connect(DB)

cursor=conn.cursor()



# yanlış veya boş başlıkları al

cursor.execute("""
SELECT

id,
karar_no,
tam_metin,
ai_soru_basligi

FROM kararlar

WHERE ai_uzman_notu='OPENAI YENI FORMAT TAMAMLANDI'

""")


kayitlar=cursor.fetchall()



print()

print("Kontrol edilecek:")
print(len(kayitlar))




for id, karar_no, metin, eski_baslik in kayitlar:


    print("-"*60)

    print("Kontrol:")

    print(karar_no)



    if not metin:
        continue



    metin=metin[:12000]



    prompt=f"""

Sen kamu ihale hukuku uzmanısın.


Aşağıdaki KİK kararını incele.


Karar No:
{karar_no}


Mevcut soru başlığı:

{eski_baslik}



Karar:

{metin}



Görev:

Kararın gerçek uyuşmazlığını tespit et.


Uzmanların arama yapacağı şekilde TEK bir soru başlığı oluştur.


Örnek:

Yanlış:
"Teknik belgelerin değerlendirilmesi yapılabilir mi?"


Doğru:
"Aynı kişinin ortak olduğu iki şirket aynı ihaleye teklif verebilir mi?"


JSON üret:


{{
"soru_basligi":"",
"ana_konu":"",
"arama_kelime":"",
"neden":"",
}}


Kurallar:

- Mevzuat dili değil uzman arama dili kullan.
- Soru şeklinde yaz.
- Gerçek uyuşmazlığı yaz.
- Genel başlık yazma.



"""



    try:


        cevap=client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[

            {
            "role":"system",
            "content":"Kamu ihale karar analiz uzmanısın."
            },

            {
            "role":"user",
            "content":prompt
            }

            ],


            temperature=0.1

        )



        text=cevap.choices[0].message.content



        data=json.loads(text)



        cursor.execute("""

        UPDATE kararlar

        SET

        ai_soru_basligi=?,
        ai_anahtar_kelimeler=?,
        ai_uzman_notu=?


        WHERE id=?


        """,

        (

        data.get("soru_basligi"),

        data.get("arama_kelime"),

        "BASLIK DUZELTME TAMAMLANDI",

        id

        ))



        print("Düzeltildi:",data.get("soru_basligi"))



    except Exception as e:


        print("HATA")

        print(e)





conn.commit()


print()

print("="*70)

print("BASLIK DUZELTME TAMAMLANDI")

print("="*70)



conn.close()