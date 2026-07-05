# -*- coding: utf-8 -*-
"""
170 - RAG / WEB EXPORT MOTORU REVIZYONU

Amaç:
- SQLite DB'deki aktif hukuki kartları dışa aktarır.
- 168/169 revizyonu ile gelen yeni alanları export'a dahil eder:
  * konu_ozeti
  * sonuc_ozeti
  * anahtar
- Web için CSV ve JSONL üretir.
- RAG / AI danışmanlık için JSONL üretir.
- DB'de alan farklılığı varsa esnek çalışır.

Kullanım:
  python ".py\\170_RAG_Web_Export_Motoru_Revizyonu.py"

Not:
- Bu dosya DB'ye yazmaz.
- Sadece export üretir.
"""

import os
import csv
import json
import sqlite3
from datetime import datetime


# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

EXPORT_DIR = os.path.join(BASE_DIR, "exports")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

TABLE_NAME = "hukuki_kartlar"

os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def has_col(cols, name):
    return name in cols


def first_col(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    return None


def safe_get(row, col, default=""):
    if not col:
        return default
    try:
        v = row[col]
    except Exception:
        return default
    if v is None:
        return default
    return v


def normalize_text(v):
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v).strip()


def parse_list(value):
    """
    DB'deki anahtar/mevzuat alanı JSON liste, Python liste stringi veya düz metin olabilir.
    Her durumda temiz liste döndürür.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    s = str(value).strip()
    if not s:
        return []

    # JSON liste dene
    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return [str(x).strip() for x in obj if str(x).strip()]
        if isinstance(obj, str):
            return [obj.strip()] if obj.strip() else []
    except Exception:
        pass

    # Python liste görünümü: ['a', 'b']
    if s.startswith("[") and s.endswith("]"):
        try:
            import ast
            obj = ast.literal_eval(s)
            if isinstance(obj, list):
                return [str(x).strip() for x in obj if str(x).strip()]
        except Exception:
            pass

    # Virgül / noktalı virgül ayrılmış metin
    parts = []
    for p in s.replace(";", ",").split(","):
        p = p.strip(" \t\r\n-•")
        if p:
            parts.append(p)

    return parts if parts else [s]


def list_to_text(items):
    items = parse_list(items)
    return ", ".join(items)


def build_where(cols):
    """
    Aktif kartları seçmek için esnek WHERE üretir.
    Mevcut DB'de aktif/pasif alan adı farklı olabilir.
    """
    if "aktif" in cols:
        return "WHERE COALESCE(aktif, 1) = 1"
    if "is_active" in cols:
        return "WHERE COALESCE(is_active, 1) = 1"
    if "durum" in cols:
        return "WHERE COALESCE(durum, 'aktif') NOT IN ('pasif', 'PASIF', 'inactive', 'INACTIVE')"
    return ""


def row_to_card(row, cols):
    id_col = first_col(cols, ["id", "kart_id"])
    karar_no_col = first_col(cols, ["karar_no", "karar", "decision_no"])
    baslik_col = first_col(cols, ["baslik", "başlık", "title"])
    hukuki_soru_col = first_col(cols, ["hukuki_soru", "soru"])
    konu_ozeti_col = first_col(cols, ["konu_ozeti", "konu"])
    sonuc_ozeti_col = first_col(cols, ["sonuc_ozeti"])
    sonuc_col = first_col(cols, ["sonuc", "sonuç"])
    sonuc_tipi_col = first_col(cols, ["sonuc_tipi", "sonuç_tipi"])
    emsal_ilke_col = first_col(cols, ["emsal_ilke", "ilke"])
    mevzuat_col = first_col(cols, ["mevzuat"])
    anahtar_col = first_col(cols, ["anahtar", "anahtarlar", "keywords"])
    guven_col = first_col(cols, ["guven", "güven", "guven_skoru", "kalite_puani"])
    kalite_col = first_col(cols, ["kalite_etiketi"])
    kaynak_col = first_col(cols, ["kaynak_yontem", "source"])
    created_col = first_col(cols, ["created_at", "olusturma_tarihi"])
    updated_col = first_col(cols, ["updated_at"])

    sonuc_ozeti = normalize_text(safe_get(row, sonuc_ozeti_col))
    sonuc = normalize_text(safe_get(row, sonuc_col))

    # Eski kartlarda sonuc_ozeti yoksa sonuc alanından doldur.
    if not sonuc_ozeti:
        sonuc_ozeti = sonuc

    if not sonuc:
        sonuc = sonuc_ozeti

    mevzuat_list = parse_list(safe_get(row, mevzuat_col))
    anahtar_list = parse_list(safe_get(row, anahtar_col))

    card = {
        "id": safe_get(row, id_col),
        "karar_no": normalize_text(safe_get(row, karar_no_col)),
        "baslik": normalize_text(safe_get(row, baslik_col)),
        "hukuki_soru": normalize_text(safe_get(row, hukuki_soru_col)),
        "konu_ozeti": normalize_text(safe_get(row, konu_ozeti_col)),
        "sonuc_ozeti": sonuc_ozeti,
        "sonuc": sonuc,
        "sonuc_tipi": normalize_text(safe_get(row, sonuc_tipi_col)),
        "emsal_ilke": normalize_text(safe_get(row, emsal_ilke_col)),
        "mevzuat": mevzuat_list,
        "anahtar": anahtar_list,
        "guven": normalize_text(safe_get(row, guven_col)),
        "kalite_etiketi": normalize_text(safe_get(row, kalite_col)),
        "kaynak_yontem": normalize_text(safe_get(row, kaynak_col)),
        "created_at": normalize_text(safe_get(row, created_col)),
        "updated_at": normalize_text(safe_get(row, updated_col)),
    }

    return card


def build_rag_text(card):
    parts = [
        f"Karar No: {card.get('karar_no', '')}",
        f"Başlık: {card.get('baslik', '')}",
        f"Hukuki Soru: {card.get('hukuki_soru', '')}",
        f"Konu Özeti: {card.get('konu_ozeti', '')}",
        f"Sonuç Özeti: {card.get('sonuc_ozeti', '')}",
        f"Sonuç Tipi: {card.get('sonuc_tipi', '')}",
        f"Emsal İlke: {card.get('emsal_ilke', '')}",
        f"Mevzuat: {list_to_text(card.get('mevzuat', []))}",
        f"Anahtar: {list_to_text(card.get('anahtar', []))}",
    ]
    return "\n".join([p for p in parts if p and not p.endswith(": ")]).strip()


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("170 - RAG / WEB EXPORT MOTORU REVIZYONU")
    print("=" * 80)

    run_tag = tag()

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB bulunamadı: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cols = read_columns(conn, TABLE_NAME)
    if not cols:
        raise RuntimeError(f"Tablo bulunamadı veya kolon okunamadı: {TABLE_NAME}")

    where_sql = build_where(cols)
    sql = f"SELECT * FROM {TABLE_NAME} {where_sql}"
    rows = conn.execute(sql).fetchall()

    web_csv = os.path.join(EXPORT_DIR, f"web_export_170_{run_tag}.csv")
    web_jsonl = os.path.join(EXPORT_DIR, f"web_export_170_{run_tag}.jsonl")
    rag_jsonl = os.path.join(EXPORT_DIR, f"rag_export_170_{run_tag}.jsonl")

    # Güncel sabit isimli kopyalar
    web_csv_latest = os.path.join(EXPORT_DIR, "web_export_latest.csv")
    web_jsonl_latest = os.path.join(EXPORT_DIR, "web_export_latest.jsonl")
    rag_jsonl_latest = os.path.join(EXPORT_DIR, "rag_export_latest.jsonl")

    log_path = os.path.join(LOG_DIR, f"170_export_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"170_export_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"170_rag_web_export_motoru_revizyonu_raporu_{run_tag}.txt")

    export_fields = [
        "id",
        "karar_no",
        "baslik",
        "hukuki_soru",
        "konu_ozeti",
        "sonuc_ozeti",
        "sonuc",
        "sonuc_tipi",
        "emsal_ilke",
        "mevzuat",
        "anahtar",
        "guven",
        "kalite_etiketi",
        "kaynak_yontem",
        "created_at",
        "updated_at",
    ]

    cards = []
    missing_konu = 0
    missing_sonuc_ozeti = 0
    missing_anahtar = 0
    missing_mevzuat = 0

    for row in rows:
        card = row_to_card(row, cols)

        if not card["konu_ozeti"]:
            missing_konu += 1
        if not card["sonuc_ozeti"]:
            missing_sonuc_ozeti += 1
        if not card["anahtar"]:
            missing_anahtar += 1
        if not card["mevzuat"]:
            missing_mevzuat += 1

        cards.append(card)

    # WEB CSV
    with open(web_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=export_fields, extrasaction="ignore")
        writer.writeheader()
        for card in cards:
            row = dict(card)
            row["mevzuat"] = list_to_text(card.get("mevzuat", []))
            row["anahtar"] = list_to_text(card.get("anahtar", []))
            writer.writerow(row)

    # WEB JSONL
    open(web_jsonl, "w", encoding="utf-8").close()
    for card in cards:
        append_jsonl(web_jsonl, card)

    # RAG JSONL
    open(rag_jsonl, "w", encoding="utf-8").close()
    for card in cards:
        rag_row = {
            "id": card.get("id"),
            "karar_no": card.get("karar_no"),
            "title": card.get("baslik"),
            "text": build_rag_text(card),
            "metadata": {
                "karar_no": card.get("karar_no"),
                "baslik": card.get("baslik"),
                "hukuki_soru": card.get("hukuki_soru"),
                "konu_ozeti": card.get("konu_ozeti"),
                "sonuc_ozeti": card.get("sonuc_ozeti"),
                "sonuc_tipi": card.get("sonuc_tipi"),
                "emsal_ilke": card.get("emsal_ilke"),
                "mevzuat": card.get("mevzuat", []),
                "anahtar": card.get("anahtar", []),
                "guven": card.get("guven"),
                "kalite_etiketi": card.get("kalite_etiketi"),
                "kaynak_yontem": card.get("kaynak_yontem"),
            }
        }
        append_jsonl(rag_jsonl, rag_row)

    # latest kopyalarını üret
    for src, dst in [
        (web_csv, web_csv_latest),
        (web_jsonl, web_jsonl_latest),
        (rag_jsonl, rag_jsonl_latest),
    ]:
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            fdst.write(fsrc.read())

    for card in cards:
        append_jsonl(log_path, {
            "run_id": run_tag,
            "time": now(),
            "karar_no": card.get("karar_no"),
            "id": card.get("id"),
            "has_konu_ozeti": bool(card.get("konu_ozeti")),
            "has_sonuc_ozeti": bool(card.get("sonuc_ozeti")),
            "anahtar_count": len(card.get("anahtar", [])),
            "mevzuat_count": len(card.get("mevzuat", [])),
        })

    total = len(cards)
    ready_for_165 = total > 0 and missing_konu == 0 and missing_anahtar == 0

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "db_path": DB_PATH,
        "table": TABLE_NAME,
        "active_rows_exported": total,
        "missing_konu_ozeti": missing_konu,
        "missing_sonuc_ozeti": missing_sonuc_ozeti,
        "missing_anahtar": missing_anahtar,
        "missing_mevzuat": missing_mevzuat,
        "web_csv": web_csv,
        "web_jsonl": web_jsonl,
        "rag_jsonl": rag_jsonl,
        "web_csv_latest": web_csv_latest,
        "web_jsonl_latest": web_jsonl_latest,
        "rag_jsonl_latest": rag_jsonl_latest,
        "log_path": log_path,
        "ready_for_165": ready_for_165,
        "next_step": "165_Hedef1_Web_Kalite_Test_Motoru.py",
    }

    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("170 - RAG / WEB EXPORT MOTORU REVIZYONU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                     : {DB_PATH}\n")
        f.write(f"Tablo                  : {TABLE_NAME}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Export edilen kart      : {total}\n")
        f.write(f"Konu özeti boş          : {missing_konu}\n")
        f.write(f"Sonuç özeti boş         : {missing_sonuc_ozeti}\n")
        f.write(f"Anahtar boş             : {missing_anahtar}\n")
        f.write(f"Mevzuat boş             : {missing_mevzuat}\n")
        f.write(f"165'e geçilebilir mi    : {'EVET' if ready_for_165 else 'HAYIR'}\n\n")

        f.write("EXPORT DOSYALARI\n")
        f.write("-" * 80 + "\n")
        f.write(f"Web CSV                 : {web_csv}\n")
        f.write(f"Web JSONL               : {web_jsonl}\n")
        f.write(f"RAG JSONL               : {rag_jsonl}\n")
        f.write(f"Web CSV latest          : {web_csv_latest}\n")
        f.write(f"Web JSONL latest        : {web_jsonl_latest}\n")
        f.write(f"RAG JSONL latest        : {rag_jsonl_latest}\n\n")

        f.write("SISTEM DOSYALARI\n")
        f.write("-" * 80 + "\n")
        f.write(f"Log JSONL               : {log_path}\n")
        f.write(f"State JSON              : {state_path}\n")
        f.write(f"Rapor                   : {rapor_path}\n")

    conn.close()

    print("\n170 EXPORT TAMAMLANDI")
    print("-" * 80)
    print(f"Export edilen kart      : {total}")
    print(f"Konu özeti boş          : {missing_konu}")
    print(f"Sonuç özeti boş         : {missing_sonuc_ozeti}")
    print(f"Anahtar boş             : {missing_anahtar}")
    print(f"Mevzuat boş             : {missing_mevzuat}")
    print(f"165'e geçilebilir mi    : {'EVET' if ready_for_165 else 'HAYIR'}")

    print("\nDosyalar:")
    print(web_csv)
    print(web_jsonl)
    print(rag_jsonl)
    print(log_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
