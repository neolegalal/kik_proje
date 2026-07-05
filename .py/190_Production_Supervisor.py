# -*- coding: utf-8 -*-
"""
190 - PRODUCTION SUPERVISOR

Amaç:
- 181/188/189/177/171/178/179/180/169/170/173/182/184 state dosyalarını tek raporda toplar.
- Son üretim hattının genel sağlığını ölçer.
- 100/250/500/1000 ölçek büyütme için karar önerisi üretir.
- API kullanmaz.
- DB'ye yazmaz.

Kullanım:
  python ".py\\190_Production_Supervisor.py"
"""

import os
import json
import glob
import sqlite3
from datetime import datetime


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")
TABLE_NAME = "hukuki_kartlar"

STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
SUPERVISOR_DIR = os.path.join(BASE_DIR, "supervisor")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(SUPERVISOR_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_tr():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def read_json(path):
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


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


def pct(n, d):
    try:
        return round((float(n) / float(d)) * 100, 2) if d else 0
    except Exception:
        return 0


def latest_state(prefix):
    path = latest_file(os.path.join(STATE_DIR, f"{prefix}*.json"))
    return path, read_json(path)


def db_summary():
    out = {
        "db_exists": os.path.exists(DB_PATH),
        "table_exists": False,
        "total_cards": 0,
        "active_cards": 0,
        "konu_ozeti_dolu": 0,
        "sonuc_ozeti_dolu": 0,
        "anahtar_dolu": 0,
    }

    if not out["db_exists"]:
        return out

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()]
        if not cols:
            return out

        out["table_exists"] = True

        if "aktif" in cols:
            active_where = "WHERE COALESCE(aktif, 1) = 1"
        elif "is_active" in cols:
            active_where = "WHERE COALESCE(is_active, 1) = 1"
        else:
            active_where = ""

        out["total_cards"] = cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        out["active_cards"] = cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} {active_where}").fetchone()[0]

        def nonempty(col):
            if col not in cols:
                return 0
            if active_where:
                sql = (
                    f"SELECT COUNT(*) FROM {TABLE_NAME} {active_where} "
                    f"AND {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) <> ''"
                )
            else:
                sql = (
                    f"SELECT COUNT(*) FROM {TABLE_NAME} "
                    f"WHERE {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) <> ''"
                )
            return cur.execute(sql).fetchone()[0]

        out["konu_ozeti_dolu"] = nonempty("konu_ozeti")
        out["sonuc_ozeti_dolu"] = nonempty("sonuc_ozeti")
        out["anahtar_dolu"] = nonempty("anahtar")
        return out
    finally:
        conn.close()


def find_step(steps, name):
    if not isinstance(steps, list):
        return {}
    for s in steps:
        if s.get("step") == name:
            return s
    return {}


def compute_health(states, db):
    score = 100
    notes = []

    s181 = states.get("181", {})
    if not s181.get("final_ready_for_large_production"):
        score -= 25
        notes.append("181 final ready değil.")

    s171 = states.get("171", {})
    block = as_int(s171.get("block_cards") or s171.get("block_count") or 0)
    if block > 0:
        score -= min(20, block)
        notes.append(f"171 BLOCK kart var: {block}")

    s177 = states.get("177", {})
    fail_cards = as_int(s177.get("fail_cards", 0))
    halluc = as_int(s177.get("high_hallucination_cards", 0))
    overgen = as_int(s177.get("high_overgeneralization_cards", 0))
    if fail_cards > 0:
        score -= min(25, fail_cards * 5)
        notes.append(f"177 FAIL kart var: {fail_cards}")
    if halluc > 0:
        score -= min(25, halluc * 10)
        notes.append(f"High hallucination var: {halluc}")
    if overgen > 0:
        score -= min(20, overgen * 10)
        notes.append(f"High overgeneralization var: {overgen}")

    s182 = states.get("182", {})
    drift = s182.get("final_decision")
    if drift == "FAIL":
        score -= 20
        notes.append("Drift FAIL.")
    elif drift == "WARNING":
        score -= 5
        notes.append("Drift WARNING.")

    s188 = states.get("188", {})
    if s188 and not s188.get("final_ok"):
        score -= 15
        notes.append("188 Auto Cleaner final OK değil.")

    s189 = states.get("189", {})
    if s189 and not s189.get("ready_for_190"):
        score -= 5
        notes.append("189 ready_for_190 değil.")

    if db.get("active_cards", 0) <= 0:
        score -= 20
        notes.append("DB aktif kart yok.")

    score = max(0, min(100, score))
    return score, notes


def recommendation(health_score, states):
    s177 = states.get("177", {})
    s171 = states.get("171", {})
    s181 = states.get("181", {})

    fail_cards = as_int(s177.get("fail_cards", 0))
    block = as_int(s171.get("block_cards") or s171.get("block_count") or 0)
    ready181 = bool(s181.get("final_ready_for_large_production"))

    if not ready181:
        return "181 son üretim hazır değil. Önce 181 v7 ile 188 + 185 akışı tam otomatik entegre edilmeli."
    if fail_cards > 0:
        return "177 FAIL kart var. 185/185v2 temizliği sonrası tekrar denenmeli."
    if block > 0:
        return "171 BLOCK var. 188 Auto Cleaner ile temizlenmeli."
    if health_score >= 90:
        return "250 karar kontrollü batch testine geçilebilir."
    if health_score >= 80:
        return "100 karar tekrar testi ve dashboard kontrolü önerilir."
    return "Önce kalite sorunları giderilmeli; büyük batch'e geçilmemeli."


def main():
    print("=" * 80)
    print("190 - PRODUCTION SUPERVISOR")
    print("=" * 80)

    run_tag = tag()

    prefixes = {
        "181": "181_v6_final_master_controller_state_",
        "188": "188_auto_cleaner_state_",
        "189": "189_adaptive_prompt_learning_state_",
        "171": "171_v2_mini_kalite_state_",
        "177": "177_hukuki_dogruluk_state_",
        "178": "178_birlestirme_hakemi_state_",
        "179": "179_kart_optimizasyon_state_",
        "180": "180_v2_karmasiklik_state_",
        "169": "169_db_importer_state_",
        "170": "170_export_state_",
        "173": "173_v2_master_acceptance_state_",
        "182": "182_v2_production_drift_state_",
        "184": "184_v3_production_dashboard_state_",
    }

    states = {}
    state_paths = {}

    for key, prefix in prefixes.items():
        path, st = latest_state(prefix)
        states[key] = st
        state_paths[key] = path

    # fallback older 181 if no v6
    if not states["181"]:
        path, st = latest_state("181_v5_final_master_controller_state_")
        states["181"] = st
        state_paths["181"] = path

    db = db_summary()
    health_score, health_notes = compute_health(states, db)
    next_action = recommendation(health_score, states)

    s181 = states.get("181", {})
    s171 = states.get("171", {})
    s177 = states.get("177", {})
    s178 = states.get("178", {})
    s179 = states.get("179", {})
    s180 = states.get("180", {})
    s169 = states.get("169", {})
    s170 = states.get("170", {})
    s182 = states.get("182", {})
    s188 = states.get("188", {})
    s189 = states.get("189", {})

    txt_path = os.path.join(RAPOR_DIR, f"190_production_supervisor_raporu_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"190_production_supervisor_state_{run_tag}.json")
    summary_path = os.path.join(SUPERVISOR_DIR, f"190_supervisor_summary_{run_tag}.json")

    supervisor_state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "health_score": health_score,
        "health_notes": health_notes,
        "next_action": next_action,
        "db": db,
        "state_paths": state_paths,
        "key_metrics": {
            "181_final_ready": s181.get("final_ready_for_large_production"),
            "181_limit": s181.get("limit"),
            "171_total": s171.get("total_cards") or s171.get("toplam_kart"),
            "171_block": s171.get("block_cards") or s171.get("block_count"),
            "171_avg": s171.get("avg_score") or s171.get("average_score"),
            "177_avg": s177.get("avg_legal_accuracy_score"),
            "177_fail_cards": s177.get("fail_cards"),
            "177_high_hallucination": s177.get("high_hallucination_cards"),
            "177_high_overgeneralization": s177.get("high_overgeneralization_cards"),
            "178_merge": s178.get("merge_recommended_count"),
            "178_reduction": s178.get("reduction_rate"),
            "179_reduction": s179.get("reduction_rate"),
            "180_avg": s180.get("avg_planning_score"),
            "169_inserted": s169.get("inserted") or s169.get("inserted_cards") or s169.get("db_inserted_cards"),
            "170_exported": s170.get("active_rows_exported"),
            "182_drift": s182.get("final_decision"),
            "182_score": s182.get("final_drift_score"),
            "188_final_ok": s188.get("final_ok"),
            "188_cleaner_used": s188.get("cleaner_used"),
            "189_ready": s189.get("ready_for_190"),
        },
        "ready_for_next_batch": health_score >= 90 and bool(s181.get("final_ready_for_large_production")),
        "recommended_next_batch": 250 if health_score >= 90 else 100,
    }

    write_json(state_path, supervisor_state)
    write_json(summary_path, supervisor_state)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("190 - PRODUCTION SUPERVISOR RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {now_tr()}\n")
        f.write(f"Production Health Score        : {health_score} / 100\n")
        f.write(f"Sonraki öneri                  : {next_action}\n")
        f.write(f"Sonraki batch önerisi          : {supervisor_state['recommended_next_batch']}\n\n")

        f.write("ANA METRIKLER\n")
        f.write("-" * 80 + "\n")
        for k, v in supervisor_state["key_metrics"].items():
            f.write(f"{k:<35}: {v}\n")

        f.write("\nDB DURUMU\n")
        f.write("-" * 80 + "\n")
        f.write(f"DB toplam kart                 : {db.get('total_cards')}\n")
        f.write(f"DB aktif kart                  : {db.get('active_cards')}\n")
        f.write(f"Konu özeti dolu                : {db.get('konu_ozeti_dolu')} (%{pct(db.get('konu_ozeti_dolu'), db.get('active_cards'))})\n")
        f.write(f"Sonuç özeti dolu               : {db.get('sonuc_ozeti_dolu')} (%{pct(db.get('sonuc_ozeti_dolu'), db.get('active_cards'))})\n")
        f.write(f"Anahtar dolu                   : {db.get('anahtar_dolu')} (%{pct(db.get('anahtar_dolu'), db.get('active_cards'))})\n")

        f.write("\nSAĞLIK NOTLARI\n")
        f.write("-" * 80 + "\n")
        if health_notes:
            for n in health_notes:
                f.write(f"- {n}\n")
        else:
            f.write("- Kritik uyarı yok.\n")

        f.write("\nSTATE DOSYALARI\n")
        f.write("-" * 80 + "\n")
        for k, p in state_paths.items():
            f.write(f"{k:<10}: {p}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State                         : {state_path}\n")
        f.write(f"Summary JSON                  : {summary_path}\n")
        f.write(f"Rapor                         : {txt_path}\n")

    print("\n190 PRODUCTION SUPERVISOR TAMAMLANDI")
    print("-" * 80)
    print(f"Production Health Score        : {health_score} / 100")
    print(f"Sonraki öneri                  : {next_action}")
    print(f"Sonraki batch önerisi          : {supervisor_state['recommended_next_batch']}")
    print(f"191'e geçilebilir mi           : EVET" if health_score >= 80 else "191'e geçilebilir mi           : HAYIR")

    print("\nDosyalar:")
    print(state_path)
    print(summary_path)
    print(txt_path)


if __name__ == "__main__":
    main()
