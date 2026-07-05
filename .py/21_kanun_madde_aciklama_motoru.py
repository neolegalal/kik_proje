import sqlite3
from collections import Counter


DB = "kik.db"


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - KANUN ANALİZ MOTORU")
print("="*70)


conn = sqlite3.connect(DB)
cur = conn.cursor()


# --------------------------------------------------
# Kanun maddesi açıklama sözlüğü
# --------------------------------------------------

kanun_aciklama = {

"4734/5":"Temel İlkeler",
"4734/8":"Eşik Değerler",
"4734/10":"İhaleye Katılımda Yeterlik Kuralları",
"4734/18":"Tekliflerin Alınması ve Açılması",
"4734/21":"Pazarlık Usulü",
"4734/38":"Aşırı Düşük Teklifler",
"4734/39":"Bütün Tekliflerin Reddedilmesi ve İhalenin İptali",
"4734/40":"İhalenin Karara Bağlanması",
"4734/41":"Kesinleşen İhale Kararının Bildirilmesi",
"4734/53":"Kamu İhale Kurumu",
"4734/54":"Başvurular Hakkında Genel Hükümler",
"4734/55":"Şikayet Başvurusu",
"4734/56":"İtirazen Şikayet Başvurusu",
"4734/65":"Dava Yolu"

}



# --------------------------------------------------
# Veri çek
# --------------------------------------------------

rows = cur.execute("""

SELECT 
kanun_maddeleri,
karar_sonucu,
ana_kategori

FROM kararlar

""").fetchall()



madde_veri = {}


for kanun, sonuc, kategori in rows:

    if not kanun:
        continue


    maddeler = kanun.split(",")


    for m in maddeler:

        m=m.strip()


        if m not in madde_veri:

            madde_veri[m]={
                "adet":0,
                "sonuc":[],
                "kategori":[]
            }


        madde_veri[m]["adet"] += 1


        if sonuc:
            madde_veri[m]["sonuc"].append(sonuc)


        if kategori:
            madde_veri[m]["kategori"].append(kategori)





# --------------------------------------------------
# Rapor
# --------------------------------------------------


for madde,data in sorted(
    madde_veri.items(),
    key=lambda x:x[1]["adet"],
    reverse=True
):


    print("\n----------------------------------------")

    print(
        madde,
        "-",
        kanun_aciklama.get(
            madde,
            "Açıklama bulunamadı"
        )
    )


    print(
        "Kullanım:",
        data["adet"],
        "karar"
    )


    print(
        "Sonuçlar:",
        Counter(data["sonuc"])
    )


    print(
        "Kategoriler:",
        Counter(data["kategori"])
    )



print("\n")
print("="*70)
print(" KANUN ANALİZ TAMAMLANDI")
print("="*70)


conn.close()