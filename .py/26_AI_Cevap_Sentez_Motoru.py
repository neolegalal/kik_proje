import sqlite3
from collections import Counter


DB="kik.db"


conn=sqlite3.connect(DB)
c=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - AI CEVAP SENTEZ MOTORU")
print("="*70)



soru=input("\nSorunuz: ").lower()



kelimeler=soru.split()



arama="%"+ "%".join(kelimeler)+"%"



rows=c.execute("""

SELECT

k.karar_no,
kk.soru_basligi,
kk.karar_ozeti,
kk.karar_sonucu,
kk.ana_kategori,
kk.anahtar_kelimeler,
k.kanun_maddeleri


FROM karar_konulari kk


JOIN kararlar k

ON kk.karar_id=k.id


WHERE

lower(kk.soru_basligi) LIKE ?

OR

lower(kk.karar_ozeti) LIKE ?

OR

lower(kk.anahtar_kelimeler) LIKE ?


""",

(arama,arama,arama)

).fetchall()



print("\n")
print("="*70)
print(" AI HUKUKİ ANALİZ")
print("="*70)



if not rows:

    print("\nUygun karar bulunamadı.")



else:


    print("\nİlgili karar sayısı:",len(rows))


    print("\nGENEL DEĞERLENDİRME")
    print("-"*50)


    kategoriler=[]

    sonuclar=[]

    kanunlar=[]


    for r in rows:

        kategoriler.append(r[4])
        sonuclar.append(r[3])
        kanunlar.extend(
            r[6].split(",")
        )


    print("\nKonu başlıkları:")

    for x,y in Counter(kategoriler).most_common():

        print("-",x,":",y,"karar")



    print("\nKurul sonuç eğilimi:")

    for x,y in Counter(sonuclar).most_common():

        print("-",x,":",y)



    print("\nDayanak mevzuatlar:")

    for x,y in Counter(kanunlar).most_common():

        print("-",x.strip(),":",y)



    print("\n")
    print("="*70)
    print(" EMSAL KARAR ÖZETLERİ")
    print("="*70)



    for r in rows[:5]:


        print("\n--------------------------------")


        print("Karar:",r[0])


        print("\nUyuşmazlık:")
        print(r[1])


        print("\nDeğerlendirme:")
        print(r[2])


        print("\nSonuç:")
        print(r[3])



    print("\n")
    print("="*70)
    print(" AI CEVAP SENTEZİ TAMAMLANDI")
    print("="*70)



conn.close()