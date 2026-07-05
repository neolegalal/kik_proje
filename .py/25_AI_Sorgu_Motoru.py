import sqlite3


DB="kik.db"


conn=sqlite3.connect(DB)
c=conn.cursor()



print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - AI SORGU MOTORU")
print("="*70)



soru=input("\nSorunuz: ")



kelimeler=soru.lower().split()



aranacak="%"+ "%".join(kelimeler)+"%"



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


LIMIT 5


""",

(aranacak,aranacak,aranacak)

).fetchall()



print("\n")
print("="*70)
print(" AI BULGULARI")
print("="*70)



if not rows:

    print("Uygun karar bulunamadı.")


else:


    for r in rows:


        print("\n--------------------------------")


        print("Karar:",r[0])


        print("\nKonu:")
        print(r[1])


        print("\nÖzet:")
        print(r[2])


        print("\nSonuç:")
        print(r[3])


        print("\nKategori:")
        print(r[4])


        print("\nMevzuat:")
        print(r[6])



print("\n")
print("="*70)
print(" AI ANALİZ TAMAMLANDI")
print("="*70)



conn.close()