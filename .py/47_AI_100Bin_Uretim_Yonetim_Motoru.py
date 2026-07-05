import sqlite3
import json
import time
from datetime import datetime
from openai import OpenAI


DB = "kik.db"

MODEL = "gpt-5-mini"




# ======================================================
# API KEY OKUMA
# ======================================================

with open("api_key.txt", "r", encoding="utf-8") as f:
    API_KEY = f.read().strip()


client = OpenAI(
    api_key=API_KEY
)




print("="*70)
print("KAMU IHALE KARAR AI - 100 BIN URETIM YONETIM MOTORU")
print("="*70)




conn = sqlite3.connect(DB)

cursor = conn.cursor()




# ======================================================
# AI KART VAR MI?
# ======================================================

def ai_kart_var_mi(karar_no):

    cursor.execute("""
    SELECT id
    FROM ai_karar_kartlari
    WHERE karar_no=?
    """,
    (karar_no,))


    return cursor.fetchone()




# ======================================================
# AI ANALIZ
# ======================================================

def ai_uret(karar_metni):


    prompt = f"""

Sen kamu ihale hukuku uzmanısın.

Aşağıdaki Kamu İhale Kurulu kararını analiz et.

Çıktıyı SADECE JSON formatında ver.


Format:

{{
"soru_basligi":"",
"kisa_ozet":"",
"hukuki_sorun":"",
"gerekce":"",
"sonuc":"",
"emsal_ilke":"",
"mevzuat":"",
"anahtar_kelimeler":"",
"kategori":""
}}


Karar metni:

{karar_metni}

"""


    response = client.chat.completions.create(

        model=MODEL,

        messages=[

            {
            "role":"user",
            "content":prompt
            }

        ]

    )


    cevap = response.choices[0].message.content


    return json.loads(cevap)





# ======================================================
# AI KART KAYIT
# ======================================================

def kaydet_ai_karti(karar, veri):


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

    olusturma_tarihi

    )


    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    karar[0],

    karar[1],

    veri.get("soru_basligi"),

    veri.get("kisa_ozet"),

    veri.get("hukuki_sorun"),

    veri.get("gerekce"),

    veri.get("sonuc"),

    veri.get("emsal_ilke"),

    veri.get("mevzuat"),

    veri.get("anahtar_kelimeler"),

    veri.get("kategori"),

    datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ))



    conn.commit()






# ======================================================
# KARARLARI AL
# ======================================================


cursor.execute("""

SELECT

id,

karar_no,

tam_metin

FROM kararlar

ORDER BY id


""")


kararlar = cursor.fetchall()



toplam = len(kararlar)

yeni = 0

hata = 0




print()

print("Toplam karar:", toplam)





# ======================================================
# ÜRETİM DÖNGÜSÜ
# ======================================================


for karar in kararlar:


    karar_id = karar[0]

    karar_no = karar[1]

    metin = karar[2]




    if ai_kart_var_mi(karar_no):

        print(
            "VAR:",
            karar_no
        )

        continue




    print()

    print("-"*70)

    print("Analiz edilen karar:" , karar_no)




    try:


        sonuc = ai_uret(

            metin[:12000]

        )



        kaydet_ai_karti(

            karar,

            sonuc

        )



        yeni += 1



        print(
            "✓ AI KARAR KARTI KAYDEDİLDİ"
        )



        time.sleep(1)





    except Exception as e:


        hata += 1


        print()

        print(
            "HATA:",
            e
        )






print()

print("="*70)

print("AI URETIM TAMAMLANDI")

print()

print("Toplam karar:", toplam)

print("Yeni AI kartı:", yeni)

print("Hata:", hata)

print("="*70)



conn.close()