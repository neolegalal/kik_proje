"""
ADIM 2: Tum regex alanlarini doldur (1-15)
Karar No, Tarih, Yil, Toplanti, Gundem, Basvuru Sahibi, Idare,
IKN, Konu, Tur, Usul, Il, Karar Sonucu, Oylama, Ilgili Mevzuat

Kullanim: python 2_regex_alanlar.py
"""

import sqlite3
import re

DB_DOSYASI = "./kik.db"


def normalize(m):
    if not m:
        return ""
    return m.translate(str.maketrans(
        "çğıiöşüÇĞIİÖŞÜâîûÂÎÛ", "cgiiosuCGIIOSUaiuAIU")).lower()


def temizle(s):
    if not s:
        return None
    s = re.sub(r'\s+', ' ', s.replace('\n', ' ')).strip().rstrip(',').strip()
    return s if s else None


# ── 1-5: Temel ──
def karar_no(m):
    x = re.search(r'Karar\s+No\s*[:\s]+(\d{4}/[A-Z]+\.[A-Z0-9]+[-\u2013]\d+)', m)
    return x.group(1).strip() if x else None

def karar_tarihi(m):
    x = re.search(r'Karar\s+Tarihi\s*[:\s]+(\d{1,2}\.\d{1,2}\.\d{4})', m)
    return x.group(1).strip() if x else None

def karar_yili(tarih):
    if tarih:
        try: return int(tarih.split('.')[-1])
        except: return None
    return None

def toplanti_no(m):
    x = re.search(r'Toplant[ıi]\s+No\s*[:\s]+(\d{4}/\d+)', m)
    return x.group(1).strip() if x else None

def gundem_no(m):
    x = re.search(r'G[uü]ndem\s+No\s*[:\s]+(\d+)', m)
    return x.group(1).strip() if x else None

# ── 6-7: Taraflar ──
def basvuru_sahibi(m):
    x = re.search(r'BA[SŞ]VURU\s+SAH[İI]B[İI]\s*[:\n]+\s*(.+?)(?:\n\s*\n|\n[İI]HALEY[İI])',
                  m, re.DOTALL | re.IGNORECASE)
    return temizle(x.group(1)) if x else None

def idare_adi(m):
    x = re.search(r'[İI]HALEY[İI]\s+YAPAN\s+[İI]DARE\s*[:\n]+\s*(.+?)(?:\n\s*\n|\nBA[SŞ]VURUYA)',
                  m, re.DOTALL | re.IGNORECASE)
    return temizle(x.group(1)) if x else None

# ── 8-9: Ihale ──
def ihale_kayit_no(m):
    x = re.search(r'(\d{4}/\d{1,7})\s+[İi]hale\s+Kay[ıi]t', m)
    if x: return x.group(1)
    x = re.search(r'[İi]hale\s+Kay[ıi]t\s+Numaral[ıi]\s+["\u201c]?(\d{4}/\d{1,7})', m, re.IGNORECASE)
    return x.group(1) if x else None

def ihale_konusu(m):
    x = re.search(r'BA[SŞ]VURUYA\s+KONU\s+[İi]HALE\s*[:\n]+.{0,80}?["\u201c\u201d\u0022](.+?)["\u201c\u201d\u0022]',
                  m, re.DOTALL | re.IGNORECASE)
    return temizle(x.group(1)) if x else None

# ── 10-11: Tur/Usul ──
def ihale_turu(m):
    n = normalize(m)
    x = re.search(r'b\)\s*T[uü]r[uü]\s*[:\s]+([^\n\r]{3,40})', m, re.IGNORECASE)
    if x:
        t = normalize(x.group(1))
        if 'yapim' in t or 'yapin' in t: return "Yapım işi"
        if 'hizmet' in t: return "Hizmet alımı"
        if 'mal' in t: return "Mal alımı"
    if 'yapim isleri ihaleleri uygulama' in n: return "Yapım işi"
    if 'hizmet alimi ihaleleri uygulama' in n: return "Hizmet alımı"
    if 'mal alimi ihaleleri uygulama' in n: return "Mal alımı"
    x = re.search(r'BA[SŞ]VURUYA\s+KONU.{0,300}', m, re.DOTALL | re.IGNORECASE)
    if x:
        a = normalize(x.group(0))
        if 'hizmet alim' in a or 'hizmeti alim' in a: return "Hizmet alımı"
        if 'yapim' in a or 'insaat' in a or 'yapilmasi' in a: return "Yapım işi"
        if 'mal alim' in a or 'satin alim' in a or 'temini' in a: return "Mal alımı"
    return None

def ihale_usulu(m):
    n = normalize(m)
    if 'acik ihale usul' in n: return "Açık ihale usulü"
    if 'belli istekliler' in n: return "Belli istekliler arasında ihale usulü"
    if 'pazarlik usul' in n: return "Pazarlık usulü"
    if 'dogrudan temin' in n: return "Doğrudan temin"
    return None

# ── 12: Il ──
def ihale_ili(m):
    # "İşin yapılacağı/malın teslim edileceği yer: XXX" satirindan
    x = re.search(r'teslim\s+edilece[gğ]i\s+yer\s*[:\s]+([^\n\r]{2,50})', m, re.IGNORECASE)
    if x:
        yer = temizle(x.group(1))
        if yer:
            # Ilk il adini al (virgul/bosluktan once)
            il = re.split(r'[,\s]+', yer)[0]
            return il.title() if il else yer
    # d) Isin yapilacagi yer
    x = re.search(r'd\)\s*[İi][sş]in\s+yap[ıi]laca[gğ][ıi].{0,40}?yer\s*[:\s]+([^\n\r]{2,40})', m, re.IGNORECASE)
    if x:
        return temizle(x.group(1))
    return None

# ── 13: Karar Sonucu (etiket) ──
def karar_sonucu(m):
    x = re.search(r'(Açıklanan\s+nedenlerle.+)', m, re.DOTALL | re.IGNORECASE)
    son = x.group(1)[:3000] if x else m[-3000:]
    n = normalize(son)
    if re.search(r'ihalenin\s+iptali\s+kararin.{0,5}n\s+iptaline', n):
        return "İptal (İhalenin iptali kararının iptali)"
    if re.search(r'ihalenin\s+iptaline', n): return "İptal"
    if 'duzeltici islem belirlenmesine' in n: return "Düzeltici İşlem"
    if 'duzeltici islem' in n: return "Düzeltici İşlem"
    if 'basvurunun kabul' in n: return "Kabul"
    if 'itirazen sikayet basvurusunun reddine' in n: return "Reddedildi"
    if 'basvurunun reddine' in n: return "Reddedildi"
    if 'reddine' in n: return "Reddedildi"
    if 'iptaline' in n: return "İptal"
    return None

# ── 14: Oylama ──
def oylama(m):
    n = normalize(m)
    if 'oybirligi ile' in n: return "Oybirliği"
    if 'oycoklu' in n: return "Oyçokluğu"
    return None

# ── 15: Ilgili Mevzuat ──
def ilgili_mevzuat(m):
    bulunan = set()
    # 4734 sayili Kanun maddeleri: "4734 ... 38'inci madde"
    for mt in re.finditer(r"(\d{4})\s+say[ıi]l[ıi]\s+Kanun[\u2019'\u02bc]?un?\s+(\d{1,3})['\u2019\u02bc]?\s*[ıi]nci", m):
        bulunan.add(f"{mt.group(1)}/{mt.group(2)}")
    # Teblig maddeleri: "Teblig'in 45'inci madde"
    for mt in re.finditer(r"Tebli[gğ][\u2019'\u02bc]?in?\s+(\d{1,3}(?:\.\d+)*)['\u2019\u02bc]?\s*[ıi]nci", m):
        bulunan.add(f"Tebliğ {mt.group(1)}")
    if bulunan:
        return ", ".join(sorted(bulunan))
    return None


def main():
    baglanti = sqlite3.connect(DB_DOSYASI)
    baglanti.row_factory = sqlite3.Row
    kayitlar = baglanti.execute("SELECT id, tam_metin FROM kararlar").fetchall()
    print(f"Islenecek: {len(kayitlar)} karar\n")

    guncel = []
    for k in kayitlar:
        m = k["tam_metin"] or ""
        tarih = karar_tarihi(m)
        guncel.append((
            karar_no(m), tarih, karar_yili(tarih), toplanti_no(m), gundem_no(m),
            basvuru_sahibi(m), idare_adi(m), ihale_kayit_no(m), ihale_konusu(m),
            ihale_turu(m), ihale_usulu(m), ihale_ili(m), karar_sonucu(m),
            oylama(m), ilgili_mevzuat(m), k["id"]
        ))

    baglanti.executemany("""
        UPDATE kararlar SET
            karar_no=?, karar_tarihi=?, karar_yili=?, toplanti_no=?, gundem_no=?,
            basvuru_sahibi=?, idare_adi=?, ihale_kayit_no=?, ihale_konusu=?,
            ihale_turu=?, ihale_usulu=?, ihale_ili=?, karar_sonucu=?,
            oylama=?, ilgili_mevzuat=?
        WHERE id=?
    """, guncel)
    baglanti.commit()

    # Sonuclari goster
    print("=== SONUCLAR ===")
    for r in baglanti.execute("""SELECT karar_no, karar_tarihi, idare_adi, ihale_turu,
                                 ihale_ili, karar_sonucu, oylama, ilgili_mevzuat
                                 FROM kararlar ORDER BY id"""):
        print(f"\n[{r['karar_no']}] {r['karar_tarihi']}")
        print(f"  Idare : {r['idare_adi']}")
        print(f"  Tur:{r['ihale_turu']} | Il:{r['ihale_ili']} | Sonuc:{r['karar_sonucu']} | {r['oylama']}")
        print(f"  Mevzuat: {r['ilgili_mevzuat']}")

    print("\n=== BOS KONTROL ===")
    alanlar = ["karar_no","karar_tarihi","karar_yili","toplanti_no","gundem_no",
               "basvuru_sahibi","idare_adi","ihale_kayit_no","ihale_konusu",
               "ihale_turu","ihale_usulu","ihale_ili","karar_sonucu","oylama","ilgili_mevzuat"]
    for a in alanlar:
        bos = baglanti.execute(f"SELECT COUNT(*) FROM kararlar WHERE {a} IS NULL").fetchone()[0]
        print(f"  {a:18s}: {'TAMAM' if bos==0 else f'{bos} BOS'}")

    baglanti.close()
    print("\nBitti. Sonraki adim: yapay zeka ozetleri (Ollama).")


if __name__ == "__main__":
    main()
