import sqlite3
import os
import json
import time
from datetime import datetime
from openai import OpenAI


print("="*70)
print("KAMU IHALE KARAR AI - 100 BIN BATCH URETIM MOTORU")
print("="*70)


# =========================
# API
# =========================

with open("api_key.txt","r",encoding="utf-8") as f:
    api_key=f.read().strip()


client = OpenAI(api_key=api_key)


MODEL = "gpt-5-mini"


# =========================
# DATABASE
# =========================

db = sqlite3.connect("kik.db")
cursor = db.cursor()



# =========================
# KARARLARI AL
# =========================


cursor.execute("""
SELECT 
id,
karar_no,
karar_soru_basligi,
karar_ozeti,
karar_sonuc_ozeti,
ilgili_mevzuat,
anahtar_kelimeler,
tam_metin

FROM kararlar
""")


kararlar = cursor.fetchall()


print()
print("Toplam karar:",len(kararlar))
print()



yeni=0
hata=0



# =========================
# LOOP
# =========================


for karar in kararlar:


    karar_id = karar[0]
    karar_no = karar[1]


    # mevcut kontrol

    cursor.execute("""
    SELECT id 
    FROM ai_karar_kartlari
    WHERE karar_id=?
    """,(karar_id,))


    var = cursor.fetchone()


    if var:

        print("VAR:",karar_no)
        continue



    print("-"*70)
    print("AI işleniyor:",karar_no)



    prompt=f"""

Sen kamu ihale hukuku uzmanısın.

Aşağıdaki KİK kararını analiz et.

Çıktıyı JSON formatında ver.


Alanlar:

soru_basligi

kisa_ozet

hukuki_sorun

gerekce

sonuc

emsal_ilke

mevzuat

anahtar_kelimeler

kategori

alt_kategori

arama_etiketleri

emsal_degeri

ai_soru

ai_cevap


KARAR:

Karar No:
{karar_no}


Konu:
{karar[2]}


Özet:
{karar[3]}


Sonuç:
{karar[4]}


Mevzuat:
{karar[5]}


Metin:
{karar[7]}


"""



    try:


        cevap = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                "role":"system",
                "content":"Kamu ihale hukuku uzmanısın."
                },
                {
                "role":"user",
                "content":prompt
                }
            ]

        )


        text = cevap.choices[0].message.content



        data=json.loads(text)



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
        kategori,
        alt_kategori,
        arama_etiketleri,
        emsal_degeri,
        ai_soru,
        ai_cevap,
        olusturma_tarihi
        )

        VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

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

        data.get("kategori"),
        data.get("alt_kategori"),

        data.get("arama_etiketleri"),
        data.get("emsal_degeri"),

        data.get("ai_soru"),
        data.get("ai_cevap"),

        datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ))



        db.commit()


        yeni+=1


        print("✓ AI KARTI ÜRETİLDİ:",karar_no)



        time.sleep(1)



    except Exception as e:


        hata+=1

        print("HATA:",karar_no)
        print(e)





print()
print("="*70)
print("AI ÜRETİM TAMAMLANDI")
print()
print("Toplam karar:",len(kararlar))
print("Yeni AI kartı:",yeni)
print("Hata:",hata)
print("="*70)


db.close()