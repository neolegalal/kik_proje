# -*- coding: utf-8 -*-
"""
137 - BATCH GÜVENLİ KARTLARI DB YÜKLEME MOTORU

Amaç:
- 136E güvenli sadeleme çıktısını okur.
- Pilot kararlara ait mevcut hukuki_kartlar kayıtlarını yedek tabloya alır.
- Eski pilot kartları siler.
- 136E güvenli Batch kartlarını hukuki_kartlar tablosuna yazar.
- Geri dönüş için yedekleme yapar.
"""

import os
import re
import json
import glob
import sqlite3
from datetime import datetime
from pathlib import Path

# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
RAPOR_DIR = BASE_DIR / "raporlar"
DB_PATH = PY_DIR / "kik.db"

INPUT_PATTERN = str(RAPOR_DIR / "136E_batch_guvenli_sadelesmis_*.jsonl")

# Güvenlik: True olursa DB'ye yazar. False olursa sadece simülasyon yapar.
DB_YAZ = True

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def now_str():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_file(pattern: str) -> Path:
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"Dosya bulunamadı: {pattern}")
    return Path(max(files, key=os.path.getmtime))


def normalize_text(v):
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v).strip()


def read_jsonl(path: Path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                raise ValueError(f"JSONL okunamadı. Satır: {line_no} | Hata: {e}")
    return rows


def extract_cards(rows):
    """
    136E çıktısı şu yapılardan biri olabilir:
    1) {"karar_no": "...", "kartlar": [...]}
    2) {"custom_id": "...", "karar_no": "...", "kartlar": [...]}
    3) {"response": {"body": {"...": ...}}} Batch ham yapısına yakın yapı
    """
    all_cards = []

    for row in rows:
        karar_no = row.get("karar_no") or row.get("kararNo") or row.get("karar")

        # Doğrudan kartlar
        cards = row.get("kartlar") or row.get("cards")

        # Batch response gömülü olabilir
        if not cards and isinstance(row.get("response"), dict):
            body = row["response"].get("body")
            if isinstance(body, dict):
                karar_no = karar_no or body.get("karar_no") or body.get("kararNo")
                cards = body.get("kartlar") or body.get("cards")
            elif isinstance(body, str):
                try:
                    body_json = json.loads(body)
                    karar_no = karar_no or body_json.get("karar_no") or body_json.get("kararNo")
                    cards = body_json.get("kartlar") or body_json.get("cards")
                except Exception:
                    pass

        # Bazı çıktılarda result/output alanı olabilir
        if not cards and isinstance(row.get("output"), dict):
            out = row["output"]
            karar_no = karar_no or out.get("karar_no") or out.get("kararNo")
            cards = out.get("kartlar") or out.get("cards")

        if not cards:
            continue

        if not karar_no:
            # custom_id içinden karar no yakalamaya çalış
            cid = row.get("custom_id", "")
            m = re.search(r"20\d{2}[_/][A-ZÇĞİÖŞÜ.]+[_/-]\d+", cid)
            if m:
                karar_no = m.group(0).replace("_", "/")
            else:
                karar_no = ""

        for idx, card in enumerate(cards, start=1):
            if not isinstance(card, dict):
                continue

            card_karar_no = (
                card.get("karar_no")
                or card.get("kararNo")
                or karar_no
            )

            all_cards.append({
                "karar_no": normalize_text(card_karar_no),
                "iddia_no": card.get("iddia_no") or card.get("iddiaNo") or idx,
                "baslik": normalize_text(card.get("baslik") or card.get("başlık")),
                "hukuki_soru": normalize_text(card.get("hukuki_soru") or card.get("hukukiSoru")),
                "kurul_degerlendirmesi": normalize_text(
                    card.get("kurul_degerlendirmesi")
                    or card.get("kurulDeğerlendirmesi")
                    or card.get("degerlendirme")
                    or card.get("değerlendirme")
                ),
                "sonuc": normalize_text(card.get("sonuc") or card.get("sonuç")),
                "emsal_ilke": normalize_text(card.get("emsal_ilke") or card.get("emsalİlke") or card.get("ilke")),
                "anahtar_kelime": normalize_text(
                    card.get("anahtar_kelime")
                    or card.get("anahtar_kelimeler")
                    or card.get("anahtar")
                ),
                "mevzuat": normalize_text(card.get("mevzuat")),
                "guven": normalize_text(card.get("guven") or card.get("güven") or "Yüksek"),
                "sonuc_tipi": normalize_text(card.get("sonuc_tipi") or card.get("sonuç_tipi") or card.get("sonucTipi")),
            })

    return all_cards


def ensure_columns(cur):
    existing = [r[1] for r in cur.execute("PRAGMA table_info(hukuki_kartlar)").fetchall()]

    needed = {
        "sonuc_tipi": "TEXT",
        "konu_dogrulama": "TEXT",
        "konu_kalite_puani": "INTEGER",
        "konu_dogrulama_notu": "TEXT",
        "supheli_kart": "TEXT",
        "duzeltme_tarihi": "TEXT",
        "kaynak_yontem": "TEXT",
    }

    added = []
    for col, typ in needed.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE hukuki_kartlar ADD COLUMN {col} {typ}")
            added.append(col)

    return added


def ensure_backup_table(cur, backup_table_name):
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {backup_table_name} AS
        SELECT *
        FROM hukuki_kartlar
        WHERE 1=0
    """)


def insert_card(cur, card, tarih):
    cur.execute("""
        INSERT INTO hukuki_kartlar (
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            kurul_degerlendirmesi,
            sonuc,
            emsal_ilke,
            anahtar_kelime,
            kart_tarihi,
            iddia_ozeti,
            mevzuat,
            guven,
            olusturma_tarihi,
            sonuc_tipi,
            konu_dogrulama,
            konu_kalite_puani,
            konu_dogrulama_notu,
            supheli_kart,
            duzeltme_tarihi,
            kaynak_yontem
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        card["karar_no"],
        int(card["iddia_no"]) if str(card["iddia_no"]).isdigit() else None,
        card["baslik"],
        card["hukuki_soru"],
        card["kurul_degerlendirmesi"],
        card["sonuc"],
        card["emsal_ilke"],
        card["anahtar_kelime"],
        tarih,
        "",
        card["mevzuat"],
        card["guven"],
        tarih,
        card["sonuc_tipi"],
        "BATCH GÜVENLİ SADELEME",
        100,
        "136E güvenli sadeleme çıktısından yüklendi.",
        "HAYIR",
        tarih,
        "BATCH_136E"
    ))


# =============================================================================
# ANA AKIŞ
# =============================================================================

def main():
    print("=" * 80)
    print("137 - BATCH GÜVENLİ KARTLARI DB YÜKLEME MOTORU")
    print("=" * 80)

    RAPOR_DIR.mkdir(parents=True, exist_ok=True)

    ts = now_str()
    tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    input_file = latest_file(INPUT_PATTERN)
    print(f"\nOkunan dosya:\n{input_file}")

    rows = read_jsonl(input_file)
    cards = extract_cards(rows)

    if not cards:
        raise RuntimeError("Yüklenecek kart bulunamadı.")

    karar_nolari = sorted(set(c["karar_no"] for c in cards if c["karar_no"]))

    if not karar_nolari:
        raise RuntimeError("Kartlarda karar_no bulunamadı.")

    print("\nYÜKLEME ÖN KONTROL")
    print("-" * 80)
    print(f"Karar sayısı : {len(karar_nolari)}")
    print(f"Yeni kart    : {len(cards)}")
    print(f"DB yaz       : {DB_YAZ}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    try:
        added_cols = ensure_columns(cur)

        placeholders = ",".join(["?"] * len(karar_nolari))
        old_count = cur.execute(
            f"SELECT COUNT(*) FROM hukuki_kartlar WHERE karar_no IN ({placeholders})",
            karar_nolari
        ).fetchone()[0]

        backup_table = f"hukuki_kartlar_yedek_137_{ts}"
        ensure_backup_table(cur, backup_table)

        if DB_YAZ:
            cur.execute(f"""
                INSERT INTO {backup_table}
                SELECT *
                FROM hukuki_kartlar
                WHERE karar_no IN ({placeholders})
            """, karar_nolari)

            cur.execute(
                f"DELETE FROM hukuki_kartlar WHERE karar_no IN ({placeholders})",
                karar_nolari
            )

            for card in cards:
                insert_card(cur, card, tarih)

            con.commit()
        else:
            con.rollback()

        new_count = cur.execute(
            f"SELECT COUNT(*) FROM hukuki_kartlar WHERE karar_no IN ({placeholders})",
            karar_nolari
        ).fetchone()[0] if DB_YAZ else len(cards)

    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    rapor_txt = RAPOR_DIR / f"137_batch_guvenli_kart_db_yukleme_raporu_{ts}.txt"

    with open(rapor_txt, "w", encoding="utf-8") as f:
        f.write("137 - BATCH GÜVENLİ KARTLARI DB YÜKLEME RAPORU\n")
        f.write("=" * 80 + "\n")
        f.write(f"Tarih             : {tarih}\n")
        f.write(f"Input             : {input_file}\n")
        f.write(f"DB                : {DB_PATH}\n")
        f.write(f"DB yazıldı mı     : {DB_YAZ}\n")
        f.write(f"Eklenen sütunlar  : {', '.join(added_cols) if added_cols else 'Yok'}\n")
        f.write(f"Yedek tablo       : {backup_table}\n")
        f.write(f"Karar sayısı      : {len(karar_nolari)}\n")
        f.write(f"Eski kart sayısı  : {old_count}\n")
        f.write(f"Yeni kart sayısı  : {len(cards)}\n")
        f.write(f"DB yeni kart      : {new_count}\n\n")
        f.write("KARARLAR\n")
        f.write("-" * 80 + "\n")
        for k in karar_nolari:
            adet = sum(1 for c in cards if c["karar_no"] == k)
            f.write(f"{k}: {adet} kart\n")

    print("\nYÜKLEME TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı     : {len(karar_nolari)}")
    print(f"Eski kart        : {old_count}")
    print(f"Yeni kart        : {len(cards)}")
    print(f"Yedek tablo      : {backup_table}")
    print(f"Rapor            : {rapor_txt}")

    if DB_YAZ:
        print("\nDB'ye yazıldı.")
    else:
        print("\nSimülasyon yapıldı. DB'ye yazılmadı.")


if __name__ == "__main__":
    main()