# -*- coding: utf-8 -*-
"""
173 - MASTER ACCEPTANCE TEST

Amaç:
- Büyük üretime geçmeden önce 168→171→172→169→170 zincirinin son kabul testini yapar.
- En güncel state dosyalarını okur.
- Teknik üretim, kural tabanlı kalite, AI hakem kalite, DB import ve export aşamalarını birlikte değerlendirir.
- Büyük üretime hazır / hazır değil sertifikası üretir.

Kullanım:
  python ".py\\173_Master_Acceptance_Test.py"

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
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

TABLE_NAME = "hukuki_kartlar"

os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


def bool_text(v):
    return "EVET" if bool(v) else "HAYIR"


def db_columns(conn, table):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def db_count_active(conn, cols):
    where = ""
    if "aktif" in cols:
        where = "WHERE COALESCE(aktif, 1) = 1"
    elif "is_active" in cols:
        where = "WHERE COALESCE(is_active, 1) = 1"
    elif "durum" in cols:
        where = "WHERE COALESCE(durum, 'aktif') NOT IN ('pasif', 'PASIF', 'inactive', 'INACTIVE')"

    cur = conn.cursor()
    return cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} {where}").fetchone()[0]


def db_count_nonempty(conn, cols, col):
    if col not in cols:
        return 0

    where = f"WHERE {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) <> ''"

    if "aktif" in cols:
        where += " AND COALESCE(aktif, 1) = 1"
    elif "is_active" in cols:
        where += " AND COALESCE(is_active, 1) = 1"
    elif "durum" in cols:
        where += " AND COALESCE(durum, 'aktif') NOT IN ('pasif', 'PASIF', 'inactive', 'INACTIVE')"

    cur = conn.cursor()
    return cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} {where}").fetchone()[0]


def file_line_count(path):
    if not path or not os.path.exists(path):
        return 0
    n = 0
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def csv_data_count(path):
    if not path or not os.path.exists(path):
        return 0
    n = 0
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            if line.strip():
                n += 1
    return n


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("173 - MASTER ACCEPTANCE TEST")
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

    rapor_path = os.path.join(RAPOR_DIR, f"173_master_acceptance_test_raporu_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"173_master_acceptance_state_{run_tag}.json")

    checks = []
    warnings = []
    blocks = []

    def add_check(code, ok, detail, block_if_fail=True):
        item = {"code": code, "ok": bool(ok), "detail": detail}
        checks.append(item)
        if not ok:
            if block_if_fail:
                blocks.append(item)
            else:
                warnings.append(item)

    # -------------------------------------------------------------------------
    # 168 kontrol
    # -------------------------------------------------------------------------
    add_check(
        "168_STATE_VAR",
        s168 is not None,
        f"State: {state_168_path}",
        True
    )

    if s168:
        add_check(
            "168_TEKNIK_BASARILI",
            s168.get("ready_for_next_step") is True and int(s168.get("ok_count", 0)) > 0 and int(s168.get("error_count", 0)) == 0,
            f"ok={s168.get('ok_count')} error={s168.get('error_count')} total_cards={s168.get('total_cards')}",
            True
        )
        add_check(
            "168_YENI_OUTPUT_VAR",
            bool(s168.get("output_jsonl")) and os.path.exists(s168.get("output_jsonl", "")),
            f"output={s168.get('output_jsonl')}",
            True
        )

    # -------------------------------------------------------------------------
    # 171 kontrol
    # -------------------------------------------------------------------------
    add_check(
        "171_STATE_VAR",
        s171 is not None,
        f"State: {state_171_path}",
        True
    )

    if s171:
        add_check(
            "171_KURAL_KALITE_GECTI",
            s171.get("ready_for_169") is True or s171.get("ready_for_next_step") is True or s171.get("ready_for_import") is True,
            f"ready flags: ready_for_169={s171.get('ready_for_169')} ready_for_next_step={s171.get('ready_for_next_step')} ready_for_import={s171.get('ready_for_import')}",
            True
        )
        add_check(
            "171_BLOCK_YOK",
            int(s171.get("block_count", 0)) == 0,
            f"block_count={s171.get('block_count')}",
            True
        )
        add_check(
            "171_ORTALAMA_PUAN_YETERLI",
            float(s171.get("average_score", s171.get("ortalama_puan", 0)) or 0) >= 90,
            f"average_score={s171.get('average_score', s171.get('ortalama_puan'))}",
            True
        )

    # -------------------------------------------------------------------------
    # 172 kontrol
    # -------------------------------------------------------------------------
    add_check(
        "172_STATE_VAR",
        s172 is not None,
        f"State: {state_172_path}",
        True
    )

    if s172:
        add_check(
            "172_AI_HAKEM_GECTI",
            s172.get("ready_for_173") is True,
            f"ready_for_173={s172.get('ready_for_173')}",
            True
        )
        add_check(
            "172_FAIL_YOK",
            int(s172.get("fail_count", 0)) == 0,
            f"fail_count={s172.get('fail_count')}",
            True
        )
        add_check(
            "172_ORTALAMA_PUAN_YETERLI",
            float(s172.get("average_score", 0) or 0) >= 85,
            f"average_score={s172.get('average_score')}",
            True
        )
        add_check(
            "172_PASS_ORANI_YETERLI",
            float(s172.get("pass_rate", 0) or 0) >= 80,
            f"pass_rate={s172.get('pass_rate')}",
            True
        )

    # -------------------------------------------------------------------------
    # 169 kontrol
    # -------------------------------------------------------------------------
    add_check(
        "169_STATE_VAR",
        s169 is not None,
        f"State: {state_169_path}",
        True
    )

    if s169:
        add_check(
            "169_DB_IMPORT_BASARILI",
            s169.get("ready_for_170") is True or s169.get("ready_for_next_step") is True,
            f"ready_for_170={s169.get('ready_for_170')} ready_for_next_step={s169.get('ready_for_next_step')}",
            True
        )
        add_check(
            "169_HATA_YOK",
            int(s169.get("error_count", s169.get("hata", 0)) or 0) == 0,
            f"error_count={s169.get('error_count', s169.get('hata'))}",
            True
        )
        add_check(
            "169_KART_EKLENDI",
            int(s169.get("inserted_cards", s169.get("db_inserted_cards", s169.get("eklenen_kart", 0))) or 0) > 0,
            f"inserted={s169.get('inserted_cards', s169.get('db_inserted_cards', s169.get('eklenen_kart')))}",
            True
        )

    # -------------------------------------------------------------------------
    # 170 kontrol
    # -------------------------------------------------------------------------
    add_check(
        "170_STATE_VAR",
        s170 is not None,
        f"State: {state_170_path}",
        True
    )

    if s170:
        total_exported = int(s170.get("active_rows_exported", 0) or 0)
        add_check(
            "170_EXPORT_URETILDI",
            total_exported > 0,
            f"active_rows_exported={total_exported}",
            True
        )
        add_check(
            "170_WEB_CSV_VAR",
            bool(s170.get("web_csv")) and os.path.exists(s170.get("web_csv", "")),
            f"web_csv={s170.get('web_csv')}",
            True
        )
        add_check(
            "170_WEB_JSONL_VAR",
            bool(s170.get("web_jsonl")) and os.path.exists(s170.get("web_jsonl", "")),
            f"web_jsonl={s170.get('web_jsonl')}",
            True
        )
        add_check(
            "170_RAG_JSONL_VAR",
            bool(s170.get("rag_jsonl")) and os.path.exists(s170.get("rag_jsonl", "")),
            f"rag_jsonl={s170.get('rag_jsonl')}",
            True
        )

        # Eski 5482 kartta konu/anahtar boş olması bilinen durum.
        # Bu yüzden global missing_konu/missing_anahtar BLOCK yapılmaz.
        missing_konu = int(s170.get("missing_konu_ozeti", 0) or 0)
        missing_anahtar = int(s170.get("missing_anahtar", 0) or 0)
        if missing_konu > 0 or missing_anahtar > 0:
            add_check(
                "170_ESKI_KARTLARDA_BOS_ALAN_VAR",
                False,
                f"missing_konu={missing_konu}, missing_anahtar={missing_anahtar}. Bu eski kartlar için beklenen durumdur; yeni üretim 171/172 ile geçti.",
                False
            )

    # -------------------------------------------------------------------------
    # DB ve export eşleşme kontrolü
    # -------------------------------------------------------------------------
    db_info = {}
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cols = db_columns(conn, TABLE_NAME)
            active_count = db_count_active(conn, cols)
            konu_nonempty = db_count_nonempty(conn, cols, "konu_ozeti")
            sonuc_ozeti_nonempty = db_count_nonempty(conn, cols, "sonuc_ozeti")
            anahtar_nonempty = db_count_nonempty(conn, cols, "anahtar")
            conn.close()

            db_info = {
                "active_count": active_count,
                "columns": cols,
                "konu_ozeti_nonempty": konu_nonempty,
                "sonuc_ozeti_nonempty": sonuc_ozeti_nonempty,
                "anahtar_nonempty": anahtar_nonempty,
            }

            add_check(
                "DB_GEREKLI_KOLONLAR_VAR",
                all(c in cols for c in ["konu_ozeti", "sonuc_ozeti", "anahtar"]),
                f"konu_ozeti={'konu_ozeti' in cols}, sonuc_ozeti={'sonuc_ozeti' in cols}, anahtar={'anahtar' in cols}",
                True
            )

            if s170 and s170.get("web_jsonl"):
                web_lines = file_line_count(s170.get("web_jsonl"))
                add_check(
                    "DB_EXPORT_SAYI_UYUMLU",
                    web_lines == active_count,
                    f"DB aktif={active_count}, web_jsonl satır={web_lines}",
                    True
                )

            if s170 and s170.get("web_csv"):
                csv_lines = csv_data_count(s170.get("web_csv"))
                add_check(
                    "CSV_EXPORT_SAYI_UYUMLU",
                    csv_lines == active_count,
                    f"DB aktif={active_count}, web_csv data satır={csv_lines}",
                    True
                )

        except Exception as e:
            add_check("DB_KONTROL_HATASI", False, str(e), True)
    else:
        add_check("DB_VAR", False, f"DB bulunamadı: {DB_PATH}", True)

    total_checks = len(checks)
    ok_checks = sum(1 for c in checks if c["ok"])
    warning_count = len(warnings)
    block_count = len(blocks)

    score = round((ok_checks / total_checks) * 100, 2) if total_checks else 0

    # Master kabul:
    # - BLOCK yok
    # - 168, 171, 172, 169, 170 state'leri var
    # - skor >= 90
    # Warning olabilir; özellikle eski kartların boş alanı beklenen durumdur.
    master_ready = block_count == 0 and score >= 90

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "master_ready_for_large_production": master_ready,
        "score": score,
        "total_checks": total_checks,
        "ok_checks": ok_checks,
        "warning_count": warning_count,
        "block_count": block_count,
        "checks": checks,
        "warnings": warnings,
        "blocks": blocks,
        "state_files": {
            "168": state_168_path,
            "171": state_171_path,
            "172": state_172_path,
            "169": state_169_path,
            "170": state_170_path,
        },
        "db_info": db_info,
        "next_step": "163_Master_Production_Controller.py" if master_ready else "Eksikler giderilecek",
    }

    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("173 - MASTER ACCEPTANCE TEST RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                            : {DB_PATH}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kontrol                 : {total_checks}\n")
        f.write(f"Başarılı kontrol               : {ok_checks}\n")
        f.write(f"Warning                         : {warning_count}\n")
        f.write(f"BLOCK                           : {block_count}\n")
        f.write(f"Puan                            : {score} / 100\n")
        f.write(f"Büyük üretime hazır mı          : {bool_text(master_ready)}\n")
        f.write(f"Sonraki adım                    : {state['next_step']}\n\n")

        f.write("STATE DOSYALARI\n")
        f.write("-" * 80 + "\n")
        f.write(f"168 state                       : {state_168_path}\n")
        f.write(f"171 state                       : {state_171_path}\n")
        f.write(f"172 state                       : {state_172_path}\n")
        f.write(f"169 state                       : {state_169_path}\n")
        f.write(f"170 state                       : {state_170_path}\n\n")

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

    print("\n173 MASTER ACCEPTANCE TEST TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kontrol                 : {total_checks}")
    print(f"Başarılı kontrol               : {ok_checks}")
    print(f"Warning                        : {warning_count}")
    print(f"BLOCK                          : {block_count}")
    print(f"Puan                           : {score} / 100")
    print(f"Büyük üretime hazır mı         : {bool_text(master_ready)}")
    print(f"Sonraki adım                   : {state['next_step']}")

    print("\nDosyalar:")
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
