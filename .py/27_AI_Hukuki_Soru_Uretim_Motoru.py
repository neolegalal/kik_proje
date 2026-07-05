import sqlite3
from collections import Counter


DB = "kik.db"


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - AI HUKUKİ SORU ÜRETİM MOTORU")
print("="*70)


konu = input("\nKonu giriniz: ")


conn = sqlite3.connect(DB)
c = conn.cursor()



rows = c.execute("""
SELECT
karar_no,
soru,
ozet,
sonuc,
kategori,
anahtar,
kanun

FROM ai_hazirlik

WHERE
soru LIKE ?
OR ozet LIKE ?
OR anahtar LIKE ?
OR kategori LIKE ?

""",
(
"%"+konu+"%",
"%"+konu+"%",
"%"+konu+"%",
"%"+konu+"%"
)).fetchall()



if not rows:

    print("\nKonu bulunamadı.")
    exit()



print("\n")
print("="*70)
print(" AI HUKUKİ SORU - CEVAP VERİLERİ")
print("="*70)



for r in rows:


    karar_no = r[0]
    eski_soru = r[1]
    ozet = r[2]
    sonuc = r[3]
    kategori = r[4]
    kanun = r[6]



    # SORU ÜRETİM MOTORU


    if "aşırı düşük" in konu.lower():


        yeni_soru = (
        "Aşırı düşük teklif açıklaması kapsamında "
        "sunulan açıklamaların mevzuata uygun olmaması "
        "halinde isteklinin teklifi değerlendirme dışı bırakılır mı?"
        )


    elif "iş deneyim" in konu.lower():


        yeni_soru = (
        "İş deneyim belgelerinin ihale mevzuatına uygun "
        "olmaması halinde idare tarafından nasıl işlem yapılmalıdır?"
        )


    elif "yaklaşık maliyet" in konu.lower():


        yeni_soru = (
        "Yaklaşık maliyetin hatalı veya eksik belirlenmesi "
        "ihale sonucunu etkilerse hangi hukuki sonuç doğar?"
        )


    elif "fiyat dışı" in konu.lower():


        yeni_soru = (
        "Fiyat dışı unsur puanlamasının hatalı yapılması "
        "ihale kararının düzeltilmesini gerektirir mi?"
        )


    else:


        yeni_soru = (
        f"{konu} konusunda Kamu İhale Kurulu uygulaması nasıldır?"
        )



    # CEVAP ÜRETİMİ


    cevap = f"""
Kamu İhale Kurulu kararlarında {konu} konusundaki değerlendirmelerde,
işlemlerin ihale dokümanı ve ilgili mevzuat hükümlerine uygun olması
gerektiği kabul edilmektedir.

Somut olayda yapılan inceleme sonucunda;

{sonuc}

şeklinde karar verilmiştir.

Bu nedenle idarelerin ve isteklilerin {konu}
konusunda mevzuata uygun işlem tesis etmeleri gerekmektedir.
"""



    print("\n")
    print("-"*70)


    print("Karar:")
    print(karar_no)


    print("\nSORU:")
    print(yeni_soru)


    print("\nCEVAP:")
    print(cevap)


    print("\nKATEGORİ:")
    print(kategori)


    print("\nMEVZUAT:")
    print(kanun)



print("\n")
print("="*70)
print(" AI HUKUKİ SORU ÜRETİM TAMAMLANDI")
print("="*70)



conn.close()