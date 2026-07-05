import sqlite3
import json
import os
from datetime import datetime
from openai import OpenAI


print("="*70)
print("KAMU IHALE KARAR AI - GERCEK IDDIA AYRISTIRMA MOTORU")
print("="*70)


# OPENAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


# DATABASE
conn = sqlite3.connect("kik.db")
cursor = conn.cursor()


# TABLO
cursor.execute("""
CREATE TABLE IF NOT EXISTS karar_iddialari (

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_no TEXT,

iddia_no INTEGER,

konu TEXT,

uzman_soru TEXT,

kurul_degerlendirmesi TEXT,

sonuc TEXT,

emsal_ilke TEXT,

kaynak TEXT,

tarih TEXT

)
""")

conn.commit()


print("Tablo hazır")


# TEST KARARI
karar_no = "2006/UM.Z-3138"


karar = cursor.execute("""

SELECT 
karar_no,
tam_metin

FROM kararlar

WHERE karar_no=?

""",(karar_no,)).fetchone()


if not karar:

    print("Karar bulunamadı")
    exit()


print()
print("Analiz:")
print(karar[0])


metin = karar[1]


# uzunluk kontrol
metin = metin[:30000]


prompt = f"""

Sen Kamu İhale Hukuku uzmanısın.

Aşağıdaki Kamu İhale Kurulu kararını incele.

Kararda geçen GERÇEK hukuki uyuşmazlıkları çıkar.

Genel ihale konuları üretme.

Sadece:
- başvuru sahibinin iddiaları
- Kurulun cevap verdiği hukuki meseleler

çıkarılacaktır.

Her iddia için:

konu

uzman_soru

kurul_degerlendirmesi

sonuc

emsal_ilke


JSON formatında döndür.


Format:

{{
"iddialar":[

{{
"konu":"",
"uzman_soru":"",
"kurul_degerlendirmesi":"",
"sonuc":"",
"emsal_ilke":""
}}

]

}}


Karar metni:

{metin}

"""


try:


    cevap = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ],

        temperature=0

    )


    sonuc = cevap.choices[0].message.content


    print()
    print("AI ÇIKTISI")
    print(sonuc)


    # JSON temizleme

    sonuc = sonuc.replace("```json","")
    sonuc = sonuc.replace("```","")

    data=json.loads(sonuc)


    # BURASI ÖNEMLİ
    # AI bazen liste bazen sözlük döndürüyor

    if isinstance(data, dict):

        data = data.get("iddialar", [])


    print()
    print("Üretilen iddia:",len(data))


    iddia_no=1


    for i in data:


        cursor.execute("""

        INSERT INTO karar_iddialari

        (
        karar_no,
        iddia_no,
        konu,
        uzman_soru,
        kurul_degerlendirmesi,
        sonuc,
        emsal_ilke,
        kaynak,
        tarih
        )

        VALUES (?,?,?,?,?,?,?,?,?)

        """,

        (

        karar_no,

        iddia_no,

        i.get("konu",""),

        i.get("uzman_soru",""),

        i.get("kurul_degerlendirmesi",""),

        i.get("sonuc",""),

        i.get("emsal_ilke",""),

        karar_no,

        datetime.now().strftime("%Y-%m-%d")

        ))


        iddia_no += 1



    conn.commit()



except Exception as e:

    print()
    print("AI HATA:")
    print(e)



print()
print("="*70)
print("TAMAMLANDI")
print("="*70)