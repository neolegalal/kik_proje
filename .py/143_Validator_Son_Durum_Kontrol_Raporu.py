import os, json, sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
DB_PATH = os.path.join(PY_DIR, "kik.db")

RISK_JSONL = os.path.join(
    RAPOR_DIR,
    "139_batch_kart_validator_riskli_kartlar_20260628_111720.jsonl"
)

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def has_column(cur, table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def detect_current_risk(row):
    aktif = row.get("aktif", 1)
    if aktif == 0:
        return "PASIF"

    sonuc_tipi = (row.get("sonuc_tipi") or "").upper()
    sonuc = (row.get("sonuc") or "").lower()
    emsal = (row.get("emsal_ilke") or "").lower()
    kalite_etiketi = (row.get("kalite_etiketi") or "")

    risks = []

    if sonuc_tipi == "RET":
        if any(x in sonuc for x in ["yerindedir", "mevzuata aykırıdır", "hukuka aykırıdır", "iptali talebi yerindedir"]):
            risks.append("ÇELİŞKİ")

    if sonuc_tipi in ["KABUL", "DÜZELTİCİ İŞLEM", "İPTAL"]:
        if any(x in sonuc for x in ["yerinde değildir", "reddedilmiştir", "reddine karar verilmiştir"]):
            risks.append("ÇELİŞKİ")

    if "YAN_KART_MUKERRER" in kalite_etiketi:
        risks.append("MÜKERRER")

    if len(emsal.strip()) < 25:
        risks.append("EMSAL")

    return ", ".join(sorted(set(risks))) if risks else "YOK"

def main():
    print("=" * 80)
    print("143 - VALIDATOR SON DURUM KONTROL RAPORU")
    print("=" * 80)

    os.makedirs(RAPOR_DIR, exist_ok=True)

    risks = read_jsonl(RISK_JSONL)

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    has_aktif = has_column(cur, "hukuki_kartlar", "aktif")
    has_kalite_etiketi = has_column(cur, "hukuki_kartlar", "kalite_etiketi")
    has_kalite_notu = has_column(cur, "hukuki_kartlar", "kalite_notu")

    select_cols = [
        "id", "karar_no", "baslik", "hukuki_soru", "sonuc_tipi",
        "sonuc", "emsal_ilke", "guven"
    ]

    if has_aktif:
        select_cols.append("aktif")
    else:
        select_cols.append("1 AS aktif")

    if has_kalite_etiketi:
        select_cols.append("kalite_etiketi")
    else:
        select_cols.append("'' AS kalite_etiketi")

    if has_kalite_notu:
        select_cols.append("kalite_notu")
    else:
        select_cols.append("'' AS kalite_notu")

    risk_giderilen = 0
    risk_devam = 0
    kart_bulunamayan = 0
    pasif_giderilen = 0

    detaylar = []
    ozet_rows = []

    for r in risks:
        kart_id = r.get("kart_id")
        karar_no = r.get("karar_no")
        eski_risk = r.get("risk") or r.get("riskler") or r.get("risk_tipi") or ""

        cur.execute(
            f"SELECT {', '.join(select_cols)} FROM hukuki_kartlar WHERE id = ?",
            (kart_id,)
        )
        dbrow = cur.fetchone()

        if not dbrow:
            kart_bulunamayan += 1
            durum = "KART_BULUNAMADI"
            mevcut_risk = "BULUNAMADI"

            detaylar.append(f"\n[{durum}] karar={karar_no} kart_id={kart_id}")
            ozet_rows.append({
                "karar_no": karar_no,
                "kart_id": kart_id,
                "durum": durum,
                "mevcut_risk": mevcut_risk
            })
            continue

        row = dict(dbrow)
        mevcut_risk = detect_current_risk(row)

        if mevcut_risk == "YOK":
            risk_giderilen += 1
            durum = "RİSK_GİDERİLMİŞ"
        elif mevcut_risk == "PASIF":
            risk_giderilen += 1
            pasif_giderilen += 1
            durum = "RİSK_GİDERİLMİŞ_PASİF"
            mevcut_risk = "PASİF KART - AKTİF RİSK SAYILMADI"
        else:
            risk_devam += 1
            durum = "RİSK_DEVAM"

        detaylar.append(
            f"\n[{durum}] karar={row.get('karar_no')} kart_id={row.get('id')} match=ID:1.0\n"
            f"Başlık          : {row.get('baslik')}\n"
            f"139 Risk        : {eski_risk}\n"
            f"Mevcut Risk     : {mevcut_risk}\n"
            f"Aktif           : {row.get('aktif')}\n"
            f"Kalite Etiketi  : {row.get('kalite_etiketi')}\n"
            f"Sonuç Tipi      : {row.get('sonuc_tipi')}\n"
            f"Güven           : {row.get('guven')}\n"
            f"Sonuç           : {row.get('sonuc')}\n"
            f"Emsal İlke      : {row.get('emsal_ilke')}"
        )

        ozet_rows.append({
            "karar_no": row.get("karar_no"),
            "kart_id": row.get("id"),
            "durum": durum,
            "aktif": row.get("aktif"),
            "kalite_etiketi": row.get("kalite_etiketi"),
            "mevcut_risk": mevcut_risk
        })

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar")
    db_total = cur.fetchone()[0]

    ts = now_stamp()
    rapor_path = os.path.join(RAPOR_DIR, f"143_validator_son_durum_kontrol_raporu_{ts}.txt")
    ozet_path = os.path.join(RAPOR_DIR, f"143_validator_son_durum_kontrol_ozet_{ts}.jsonl")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("143 - VALIDATOR SON DURUM KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"139 Risk JSONL     : {RISK_JSONL}\n")
        f.write(f"139 Risk kayıt     : {len(risks)}\n")
        f.write(f"Risk giderilen     : {risk_giderilen}\n")
        f.write(f"Pasif giderilen    : {pasif_giderilen}\n")
        f.write(f"Risk devam eden    : {risk_devam}\n")
        f.write(f"Kart bulunamayan   : {kart_bulunamayan}\n")
        f.write(f"DB kart toplam     : {db_total}\n\n")
        f.write("DETAYLAR\n")
        f.write("-" * 80 + "\n")
        f.write("\n".join(detaylar))

    with open(ozet_path, "w", encoding="utf-8") as f:
        for row in ozet_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    con.close()

    print("\nSON DURUM RAPORU OLUŞTURULDU")
    print("-" * 80)
    print(f"139 Risk kayıt   : {len(risks)}")
    print(f"Risk giderilen   : {risk_giderilen}")
    print(f"Pasif giderilen  : {pasif_giderilen}")
    print(f"Risk devam eden  : {risk_devam}")
    print(f"Kart bulunamayan : {kart_bulunamayan}")
    print("\nDosyalar:")
    print(rapor_path)
    print(ozet_path)
    print("\nNOT: DB'ye yazılmadı.")

if __name__ == "__main__":
    main()