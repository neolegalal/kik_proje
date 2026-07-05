import sqlite3
from collections import Counter


DB="kik.db"


conn=sqlite3.connect(DB)
c=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - AI SORU CEVAP HAZIRLIK MOTORU")
print("="*70)



rows=c.execute("""
SELECT

k.karar_no,

kk.soru_basligi,
kk.karar_ozeti,
kk.karar_sonucu,

kk.ana_kategori,
kk.anahtar_kelimeler,

k.kanun_maddeleri


FROM kararlar k

LEFT JOIN karar_konulari kk

ON k.id=kk.karar_id


""").fetchall()



print()
print("TOPLAM AI KAYNAK KAYDI")
print("-"*40)

print(len(rows))



print()
print("="*70)
print(" AI KATEGORİ ANALİZİ")
print("="*70)



kategori=Counter()


for r in rows:

    if r[4]:
        kategori[r[4]]+=1



for k,v in kategori.items():

    print(k,":",v)



print()
print("="*70)
print(" AI EĞİTİM VERİLERİ")
print("="*70)



for r in rows:


    print()
    print("-"*60)


    print("Karar No:")
    print(r[0])


    print()
    print("Soru:")
    print(r[1])


    print()
    print("Özet:")
    print(r[2])


    print()
    print("Sonuç:")
    print(r[3])


    print()
    print("Kategori:")
    print(r[4])


    print()
    print("Anahtar:")
    print(r[5])


    print()
    print("Kanun:")
    print(r[6])



print()
print("="*70)
print(" AI HAZIRLIK TAMAMLANDI")
print("="*70)



conn.close()