import sqlite3
import json
from datetime import datetime


DB="kik.db"

CIKTI="kararlar.json"


print("="*70)
print("KAMU IHALE KARAR AI - WEBSITE JSON EXPORT MOTORU")
print("="*70)



conn=sqlite3.connect(DB)

cursor=conn.cursor()



cursor.execute("""

SELECT

karar_no,
ai_soru_basligi,
ai_kisa_ozet,
ai_sonuc,
ai_emsal_ilke,
ai_anahtar_kelimeler,
ai_uzman_notu,
ai_guven_orani,
ai_mevzuat_dayanak,
ai_hukuki_dikkat,
ai_emsal_gucu

FROM kararlar


""")


kayitlar=cursor.fetchall()



print()
print("Aktarılacak karar:")
print(len(kayitlar))
print()



veriler=[]



for k in kayitlar:


    veri={


    "karar_no":k[0],


    "soru_basligi":k[1],


    "kisa_ozet":k[2],


    "sonuc":k[3],


    "emsal_ilke":k[4],


    "anahtar_kelimeler":k[5],


    "uzman_notu":k[6],


    "guven_orani":k[7],


    "mevzuat_dayanak":k[8],


    "hukuki_dikkat":k[9],


    "emsal_gucu":k[10],


    "export_tarihi":
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")



    }



    veriler.append(veri)



with open(
CIKTI,
"w",
encoding="utf-8"
) as f:


    json.dump(
    veriler,
    f,
    ensure_ascii=False,
    indent=4
    )



print("="*70)

print("JSON EXPORT TAMAMLANDI")

print()

print("Dosya:")
print(CIKTI)

print()

print("Kayıt:")
print(len(veriler))

print("="*70)



conn.close()