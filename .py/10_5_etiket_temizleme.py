import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR,"kik.db")


conn = sqlite3.connect(DB)
cursor = conn.cursor()


print("="*60)
print(" ETİKET TEMİZLEME MOTORU")
print("="*60)



etiketler = {

"yaklaşık maliyet": [
"yaklaşık maliyet",
"maliyet",
"birim fiyat"
],

"fiyat dışı unsurlar":[
"fiyat dışı unsur",
"puanlama"
],

"aşırı düşük teklif":[
"aşırı düşük teklif",
"açıklama"
],

"iş deneyimi belgesi":[
"iş deneyimi",
"belge"
],

"vergi ve sgk borcu":[
"vergi",
"sgk",
"sosyal güvenlik"
],

"itirazen şikayet":[
"itirazen şikayet",
"başvuru"
],

"teklif değerlendirme":[
"teklif",
"değerlendirme"
],

"ihale dokümanı":[
"doküman",
"şartname"
]

}




cursor.execute("""
SELECT id,
karar_ozeti,
karar_sonucu
FROM karar_konulari
""")


kayitlar = cursor.fetchall()



sayac=0


for id,ozet,sonuc in kayitlar:


    metin = (
        str(ozet)+" "+
        str(sonuc)
    ).lower()


    bulunan=[]


    for anahtar, kelimeler in etiketler.items():

        for kelime in kelimeler:

            if kelime in metin:

                bulunan.append(anahtar)
                break



    bulunan=list(set(bulunan))


    yeni=",".join(bulunan)



    cursor.execute("""
    UPDATE karar_konulari
    SET etiketler=?
    WHERE id=?
    """,
    (yeni,id)
    )


    sayac+=1


conn.commit()
conn.close()



print("Güncellenen kayıt:",sayac)

print("="*60)
print(" ETİKET TEMİZLEME TAMAMLANDI")
print("="*60)