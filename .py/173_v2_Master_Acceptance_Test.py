# -*- coding: utf-8 -*-
"""
173 v2 - MASTER ACCEPTANCE TEST

Amaç:
- Büyük üretime geçmeden önce 168→171→172→169→170 zincirinin son kabul testini yapar.
- v2 farkı: Önceki 173'e göre state anahtar adlarını daha esnek okur.
- Teknik üretim, kural tabanlı kalite, AI hakem kalite, DB import ve export aşamalarını birlikte değerlendirir.
- Büyük üretime hazır / hazır değil sertifikası üretir.

Kullanım:
  python ".py\\173_v2_Master_Acceptance_Test.py"

Not:
- Bu dosya API çağrısı yapmaz.
- DB'ye yazmaz.
- Sadece mevcut state ve rapor çıktılarını değerlendirir.
"""

import os
import glob
import json
import sqlite3
from datetime import datetime


# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
TABLE_NAME = "hukuki_kartlar"

os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)


# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def read_json(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def yesno(v):
    return "EVET" if bool(v) else "HAYIR"


def get_any(d, keys, default=None):
    if not isinstance(d, dict):
        return default
    for k in keys:
        if k in d:
            return d.get(k)
    return default


def as_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def as_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def jsonl_count(path):
    if not path or not os.path.exists(path):
        return 0
    c = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip():
                c += 1
    return c


def csv_data_count(path):
    if not path or not os.path.exists(path):
        return 0
    c = 0
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            if line.strip():
                c += 1
    return c


def db_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def db_active_count(conn, cols):
    where = ""
    if "aktif" in cols:
        where = "WHERE COALESCE(aktif, 1) = 1"
    elif "is_active" in cols:
        where = "WHERE COALESCE(is_active, 1) = 1"
    elif "durum" in cols:
        where = "WHERE COALESCE(durum, 'aktif') NOT IN ('pasif', 'PASIF', 'inactive', 'INACTIVE')"
    return conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} {where}").fetchone()[0]


def db_nonempty_count(conn, cols, col):
    if col not in cols:
        return 0
    where = f"WHERE {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) <> ''"
    if "aktif" in cols:
        where += " AND COALESCE(aktif, 1) = 1"
    elif "is_active" in cols:
        where += " AND COALESCE(is_active, 1) = 1"
    elif "durum" in cols:
        where += " AND COALESCE(durum, 'aktif') NOT IN ('pasif', 'PASIF', 'inactive', 'INACTIVE')"
    return conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} {where}").fetchone()[0]


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("173 v2 - MASTER ACCEPTANCE TEST")
    print("=" * 80)

    run_tag = tag()

    state_168_path = latest_file(os.path.join(STATE_DIR, "168_production_runner_state_*.json"))
    state_171_path = latest_file(os.path.join(STATE_DIR, "171_v2_mini_kalite_state_*.json"))
    state_172_path = latest_file(os.path.join(STATE_DIR, "172_ai_kalite_hakemi_state_*.json"))
    state_169_path = latest_file(os.path.join(STATE_DIR, "169_db_importer_state_*.json"))
    state_170_path = latest_file(os.path.join(STATE_DIR, "170_export_state_*.json"))

    s168 = read_json(state_168_path)
    s171 = read_json(state_171_path)
    s172 = read_json(state_172_path)
    s169 = read_json(state_169_path)
    s170 = read_json(state_170_path)

    checks = []
    warnings = []
    blocks = []

    def add(code, ok, detail, block=True):
        item = {"code": code, "ok": bool(ok), "detail": str(detail)}
        checks.append(item)
        if not ok:
            if block:
                blocks.append(item)
            else:
                warnings.append(item)

    # 168
    add("168_STATE_VAR", s168 is not None, state_168_path, True)
    if s168:
        add(
            "168_RUNNER_BASARILI",
            bool(get_any(s168, ["ready_for_next_step", "ready_for_159"], False))
            and as_int(get_any(s168, ["ok_count", "successful", "basarili"], 0)) > 0
            and as_int(get_any(s168, ["error_count", "err_count", "hatali"], 0)) == 0,
            f"ok={get_any(s168, ['ok_count'])}, error={get_any(s168, ['error_count'])}, cards={get_any(s168, ['total_cards'])}",
            True
        )
        out168 = get_any(s168, ["output_jsonl"])
        add("168_OUTPUT_VAR", bool(out168) and os.path.exists(str(out168)), out168, True)

    # 171
    add("171_STATE_VAR", s171 is not None, state_171_path, True)
    if s171:
        add(
            "171_KURAL_KALITE_GECTI",
            bool(get_any(s171, ["can_go_169", "ready_for_169", "ready_for_next_step"], False)),
            f"can_go_169={get_any(s171, ['can_go_169'])}",
            True
        )
        block_cards = as_int(get_any(s171, ["block_cards", "block_count"], 0))
        avg171 = as_float(get_any(s171, ["avg_score", "average_score", "ortalama_puan"], 0))
        add("171_BLOCK_YOK", block_cards == 0, f"block_cards={block_cards}", True)
        add("171_PUAN_YETERLI", avg171 >= 90, f"avg_score={avg171}", True)

    # 172
    add("172_STATE_VAR", s172 is not None, state_172_path, True)
    if s172:
        add("172_AI_HAKEM_GECTI", bool(get_any(s172, ["ready_for_173"], False)), f"ready_for_173={get_any(s172, ['ready_for_173'])}", True)
        fail172 = as_int(get_any(s172, ["fail_count"], 0))
        avg172 = as_float(get_any(s172, ["average_score"], 0))
        pass_rate = as_float(get_any(s172, ["pass_rate"], 0))
        add("172_FAIL_YOK", fail172 == 0, f"fail_count={fail172}", True)
        add("172_PUAN_YETERLI", avg172 >= 85, f"average_score={avg172}", True)
        add("172_PASS_ORANI_YETERLI", pass_rate >= 80, f"pass_rate={pass_rate}", True)

    # 169
    add("169_STATE_VAR", s169 is not None, state_169_path, True)
    if s169:
        add(
            "169_IMPORT_GECTI",
            bool(get_any(s169, ["ready_for_next_step", "ready_for_170"], False)),
            f"ready_for_next_step={get_any(s169, ['ready_for_next_step'])}",
            True
        )
        err169 = as_int(get_any(s169, ["error_count", "hata"], 0))
        inserted169 = as_int(get_any(s169, ["inserted", "inserted_cards", "db_inserted_cards"], 0))
        add("169_HATA_YOK", err169 == 0, f"error_count={err169}", True)
        add("169_KART_EKLENDI", inserted169 > 0, f"inserted={inserted169}", True)

    # 170
    add("170_STATE_VAR", s170 is not None, state_170_path, True)
    if s170:
        exported170 = as_int(get_any(s170, ["active_rows_exported", "exported_rows"], 0))
        add("170_EXPORT_URETILDI", exported170 > 0, f"active_rows_exported={exported170}", True)

        web_csv = get_any(s170, ["web_csv"])
        web_jsonl = get_any(s170, ["web_jsonl"])
        rag_jsonl = get_any(s170, ["rag_jsonl"])

        add("170_WEB_CSV_VAR", bool(web_csv) and os.path.exists(str(web_csv)), web_csv, True)
        add("170_WEB_JSONL_VAR", bool(web_jsonl) and os.path.exists(str(web_jsonl)), web_jsonl, True)
        add("170_RAG_JSONL_VAR", bool(rag_jsonl) and os.path.exists(str(rag_jsonl)), rag_jsonl, True)

        missing_konu = as_int(get_any(s170, ["missing_konu_ozeti"], 0))
        missing_anahtar = as_int(get_any(s170, ["missing_anahtar"], 0))
        if missing_konu or missing_anahtar:
            add(
                "170_ESKI_KARTLARDA_BOS_ALAN_VAR",
                False,
                f"missing_konu={missing_konu}, missing_anahtar={missing_anahtar}. Bu eski 5482 kart için beklenen durumdur; yeni 16 kart 171/172'den geçti.",
                False
            )

    # DB / Export
    db_info = {}
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cols = db_columns(conn, TABLE_NAME)
            active = db_active_count(conn, cols)
            konu_nonempty = db_nonempty_count(conn, cols, "konu_ozeti")
            sonuc_ozeti_nonempty = db_nonempty_count(conn, cols, "sonuc_ozeti")
            anahtar_nonempty = db_nonempty_count(conn, cols, "anahtar")
            conn.close()

            db_info = {
                "active_count": active,
                "konu_ozeti_nonempty": konu_nonempty,
                "sonuc_ozeti_nonempty": sonuc_ozeti_nonempty,
                "anahtar_nonempty": anahtar_nonempty,
            }

            add(
                "DB_GEREKLI_KOLONLAR_VAR",
                all(c in cols for c in ["konu_ozeti", "sonuc_ozeti", "anahtar"]),
                f"konu_ozeti={'konu_ozeti' in cols}, sonuc_ozeti={'sonuc_ozeti' in cols}, anahtar={'anahtar' in cols}",
                True
            )

            if s170:
                web_jsonl = get_any(s170, ["web_jsonl"])
                web_csv = get_any(s170, ["web_csv"])
                if web_jsonl:
                    add("DB_WEB_JSONL_SAYI_UYUMLU", jsonl_count(web_jsonl) == active, f"DB={active}, web_jsonl={jsonl_count(web_jsonl)}", True)
                if web_csv:
                    add("DB_WEB_CSV_SAYI_UYUMLU", csv_data_count(web_csv) == active, f"DB={active}, web_csv={csv_data_count(web_csv)}", True)

            add(
                "YENI_ALANLAR_DBDE_DOLU",
                konu_nonempty > 0 and sonuc_ozeti_nonempty > 0 and anahtar_nonempty > 0,
                f"konu_dolu={konu_nonempty}, sonuc_ozeti_dolu={sonuc_ozeti_nonempty}, anahtar_dolu={anahtar_nonempty}",
                True
            )

        except Exception as e:
            add("DB_KONTROL_HATASI", False, str(e), True)
    else:
        add("DB_VAR", False, DB_PATH, True)

    total = len(checks)
    ok = sum(1 for c in checks if c["ok"])
    block_count = len(blocks)
    warning_count = len(warnings)

    # Warning'ler skoru düşürmesin; çünkü eski kartların konu_ozeti/anahtar boş olması bilinen durum.
    hard_checks = [c for c in checks if c not in warnings]
    hard_ok = sum(1 for c in hard_checks if c["ok"])
    score = round((hard_ok / len(hard_checks)) * 100, 2) if hard_checks else 0

    master_ready = block_count == 0 and score >= 90

    state = {
        "run_id": run_tag,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "master_ready_for_large_production": master_ready,
        "score": score,
        "total_checks": total,
        "ok_checks": ok,
        "warning_count": warning_count,
        "block_count": block_count,
        "checks": checks,
        "warnings": warnings,
        "blocks": blocks,
        "db_info": db_info,
        "state_files": {
            "168": state_168_path,
            "171": state_171_path,
            "172": state_172_path,
            "169": state_169_path,
            "170": state_170_path,
        },
        "next_step": "163_Master_Production_Controller.py" if master_ready else "Eksikler giderilecek",
    }

    state_path = os.path.join(STATE_DIR, f"173_v2_master_acceptance_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"173_v2_master_acceptance_test_raporu_{run_tag}.txt")
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("173 v2 - MASTER ACCEPTANCE TEST RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                            : {DB_PATH}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kontrol                 : {total}\n")
        f.write(f"Başarılı kontrol               : {ok}\n")
        f.write(f"Warning                         : {warning_count}\n")
        f.write(f"BLOCK                           : {block_count}\n")
        f.write(f"Puan                            : {score} / 100\n")
        f.write(f"Büyük üretime hazır mı          : {yesno(master_ready)}\n")
        f.write(f"Sonraki adım                    : {state['next_step']}\n\n")

        f.write("KONTROLLER\n")
        f.write("-" * 80 + "\n")
        for c in checks:
            f.write(f"[{'OK' if c['ok'] else 'FAIL'}] {c['code']} - {c['detail']}\n")

        f.write("\nWARNINGLER\n")
        f.write("-" * 80 + "\n")
        if warnings:
            for w in warnings:
                f.write(f"{w['code']} - {w['detail']}\n")
        else:
            f.write("Yok\n")

        f.write("\nBLOCKLAR\n")
        f.write("-" * 80 + "\n")
        if blocks:
            for b in blocks:
                f.write(f"{b['code']} - {b['detail']}\n")
        else:
            f.write("Yok\n")

        f.write("\nDB BILGISI\n")
        f.write("-" * 80 + "\n")
        if db_info:
            f.write(f"DB aktif kart                   : {db_info.get('active_count')}\n")
            f.write(f"Konu özeti dolu                 : {db_info.get('konu_ozeti_nonempty')}\n")
            f.write(f"Sonuç özeti dolu                : {db_info.get('sonuc_ozeti_nonempty')}\n")
            f.write(f"Anahtar dolu                    : {db_info.get('anahtar_nonempty')}\n")
        else:
            f.write("DB bilgisi alınamadı.\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON                      : {state_path}\n")
        f.write(f"Rapor                           : {rapor_path}\n")

    print("\n173 v2 MASTER ACCEPTANCE TEST TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kontrol                 : {total}")
    print(f"Başarılı kontrol               : {ok}")
    print(f"Warning                        : {warning_count}")
    print(f"BLOCK                          : {block_count}")
    print(f"Puan                           : {score} / 100")
    print(f"Büyük üretime hazır mı         : {yesno(master_ready)}")
    print(f"Sonraki adım                   : {state['next_step']}")

    print("\nDosyalar:")
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
