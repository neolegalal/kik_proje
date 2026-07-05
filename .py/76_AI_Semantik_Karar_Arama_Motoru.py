import sqlite3


DB="kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - SEMANTIK ARAMA MOTORU V3")
print("="*70)



conn=sqlite3.connect(DB)

cursor=conn.cursor()



soru=input("\nUzman sorusu: ")



print("\nAI kavram analizi yapılıyor...")



# hukuk kavram genişletme

kavramlar={

"ortak":[
"ortak",
"ortaklık",
"hisse",
"pay sahibi",
"aynı kişi",
"aynı şahıs"
],


"şirket":[
"şirket",
"firma",
"istekli",
"tüzel kişi"
],


"teklif":[
"teklif",
"sunmak",
"vermek",
"başvuru"
],


"yasak":[
"yasak",
"17/d",
"birden fazla teklif",
"birden fazla"
]


}



arama=[]



for ana, liste in kavramlar.items():

    for kelime in liste:

        if kelime.lower() in soru.lower():

            arama.extend(liste)



arama=list(set(arama))



print("Aranan kavramlar:")

print(arama)





cursor.execute("""


SELECT

karar_no,
ai_soru_basligi,
ai_kisa_ozet,
ai_sonuc,
ai_emsal_ilke,
ai_anahtar_kelimeler


FROM kararlar


""")


kararlar=cursor.fetchall()





sonuclar=[]



for k in kararlar:


    metin=" ".join([

        str(k[0]),
        str(k[1]),
        str(k[2]),
        str(k[3]),
        str(k[4]),
        str(k[5])

    ]).lower()



    skor=0



    for kelime in arama:


        if kelime.lower() in metin:

            skor += 10



    for kelime in soru.lower().split():

        if len(kelime)>3 and kelime in metin:

            skor +=5



    if skor>0:

        sonuclar.append(
            (
            skor,
            k
            )
        )





sonuclar.sort(
    key=lambda x:x[0],
    reverse=True
)





print()

print("="*70)

print("EN İLGİLİ KARARLAR")

print("="*70)





for skor,k in sonuclar[:10]:


    print()

    print("Karar No:",k[0])

    print("Soru:",k[1])

    print("Skor:",skor)

    print("-"*60)




conn.close()