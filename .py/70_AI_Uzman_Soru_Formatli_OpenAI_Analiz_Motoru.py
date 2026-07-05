import sqlite3
import json
from datetime import datetime
from openai import OpenAI
import os


DB="kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - UZMAN SORU FORMAT ANALIZ MOTORU")
print("="*70)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


conn=sqlite3.connect(DB)
cursor=conn.cursor()


cursor.execute("""
SELECT
id,
karar_no,
tam_metin

FROM kararlar

""")

kayitlar=cursor.fetchall()


print()
print("Analiz edilecek:")
print(len(kayitlar))
print()



for id,karar_no,metin in kayitlar:


    print("-"*60)
    print("Dönüştürülüyor:")
    print(karar_no)



    if not metin:
        continue


    metin=metin[:15000]


    prompt=f"""

Sen Türkiye Kamu İhale Hukuku alanında uzman danışmansın.

Aşağıdaki KİK kararını analiz et.


Karar No:
{karar_no}


Metin:

{metin}



ÇIKTI FORMATI:


{{
"soru_basligi":"",
"kisa_ozet":"",
"sonuc":"",
"emsal_ilke":"",
"anahtar_kelimeler":"",
"uzman_notu":""
}}



ÖNEMLİ KURALLAR:


1- Soru başlığı resmi karar adı olmayacak.

Yanlış:
"İstanbul Büyükşehir Belediyesi ihalesine ilişkin başvuru"

Doğru:
"İhale sözleşmesi imzalandıktan sonra şikayet başvurusu yapılabilir mi?"


2- Uzman bir kişinin arama yapacağı soru oluştur.


3- "hangi durumda",
"zorunlu mudur",
"mümkün müdür",
"verilebilir mi",
"geçerli sayılır mı"

gibi hukuk arama dili kullan.


4- Kısa özet:
Uyuşmazlık + iddia + Kurul değerlendirmesi.


5- Sonuç:
KİK ne karar verdi açık yaz.


6- Emsal ilke:
Genel uygulanabilir hukuk kuralı yaz.



"""


    try:


        cevap=client.chat.completions.create(

            model="gpt-4.1-mini",

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



        text=cevap.choices[0].message.content


        text=text.replace("```json","")
        text=text.replace("```","")


        data=json.loads(text)



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
        json.dumps(
        data.get("anahtar_kelimeler"),
        ensure_ascii=False
        ),

        "OPENAI YENI FORMAT TAMAMLANDI",

        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        id

        ))



        print("Tamamlandı:",karar_no)



    except Exception as e:

        print("HATA:")
        print(e)



conn.commit()


print()
print("="*70)
print("UZMAN SORU FORMAT ANALIZ TAMAMLANDI")
print("="*70)


conn.close()