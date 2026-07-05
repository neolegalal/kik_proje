import sqlite3
from openai import OpenAI
import os


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - AKILLI KARAR ARAMA MOTORU")
print("="*70)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)



conn = sqlite3.connect(DB)
cursor = conn.cursor()



print()
soru = input("Uzman sorusu: ")
print()



# önce veritabanından analiz edilmiş kararları al

cursor.execute("""

SELECT

karar_no,
ai_soru_basligi,
ai_kisa_ozet,
ai_sonuc,
ai_emsal_ilke,
ai_arama_kelime_danisman

FROM kararlar

WHERE ai_soru_basligi IS NOT NULL


""")


kararlar = cursor.fetchall()



print("Karar sayısı:")
print(len(kararlar))
print()



veri = ""


for k in kararlar:

    veri += f"""

Karar No:
{k[0]}

Soru:
{k[1]}

Özet:
{k[2]}

Sonuç:
{k[3]}

Emsal İlke:
{k[4]}

Anahtar:
{k[5]}


----------------------

"""




prompt = f"""

Sen kamu ihale hukuku uzmanısın.

Aşağıdaki kullanıcı sorusuna,
verilen Kamu İhale Kurulu kararları içinden
en ilgili olanları bul.


Kullanıcı sorusu:

{soru}



Kararlar:

{veri}



Şu formatta cevap ver:


1- En ilgili kararlar

Karar No:
Konu:
Neden ilgili:


2- Hukuki değerlendirme


3- Uygulanacak emsal ilke


4- Uzman için kısa sonuç



"""


try:


    cevap = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

        {
        "role":"system",
        "content":
        "Kamu ihale hukuku danışmanısın."
        },

        {
        "role":"user",
        "content":prompt
        }

        ],

        temperature=0.2

    )


    sonuc = cevap.choices[0].message.content


    print("="*70)
    print("AI KARAR ANALİZİ")
    print("="*70)

    print()

    print(sonuc)



except Exception as e:

    print("HATA:")
    print(e)



conn.close()