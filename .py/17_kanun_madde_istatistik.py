import sqlite3
from collections import Counter


DB="kik.db"


conn=sqlite3.connect(DB)
cursor=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - KANUN MADDE İSTATİSTİK")
print("="*70)



veriler=cursor.execute("""
SELECT kanun_maddeleri
FROM kararlar
""").fetchall()



sayac=Counter()



for v in veriler:

    maddeler=v[0]

    if maddeler:

        liste=maddeler.split(",")

        for m in liste:

            m=m.strip()

            if m:
                sayac[m]+=1



print()

print("KANUN MADDELERİ")
print("-"*40)



if sayac:

    for k,v in sayac.most_common():

        print(k,":",v)

else:

    print("Henüz veri yok")



print()
print("="*70)
print(" KANUN İSTATİSTİK TAMAMLANDI")
print("="*70)



conn.close()