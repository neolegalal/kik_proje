# -*- coding: utf-8 -*-
"""
184 - PRODUCTION DASHBOARD

Amaç:
- Üretim hattının son durumunu tek raporda toplar.
- 181, 182, 183, 170, 169, 177, 175, 178, 179, 180 state dosyalarını okur.
- HTML + TXT dashboard üretir.
- API kullanmaz.
- DB'ye yazmaz.

Kullanım:
  python ".py\\184_Production_Dashboard.py"

Not:
- En güncel state dosyalarını otomatik bulur.
- Tarayıcıda HTML dashboard açmaya çalışır.
"""

import os
import json
import glob
import sqlite3
import webbrowser
from datetime import datetime
from html import escape


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboards")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

TABLE_NAME = "hukuki_kartlar"

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(DASHBOARD_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_tr():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def latest_file(pattern):
def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def read_json(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def latest_state(prefix):
    path = latest_file(os.path.join(STATE_DIR, f"{prefix}*.json"))
    return path, read_json(path)


def safe(v, default=""):
    return default if v is None else str(v)


def as_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def as_float(v, default=0):
    try:
        return float(v)
    except Exception:
        return default


def db_counts():
    if not os.path.exists(DB_PATH):
        return {"db_exists": False}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cols = [r[1] for r in cur.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()]
        if not cols:
            return {"db_exists": True, "table_exists": False}

        if "aktif" in cols:
            active_where = "WHERE COALESCE(aktif, 1) = 1"
        elif "is_active" in cols:
            active_where = "WHERE COALESCE(is_active, 1) = 1"
        else:
            active_where = ""

        total = cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
        active = cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} {active_where}").fetchone()[0]

        def count_nonempty(col):
            if col not in cols:
                return None
            return cur.execute(
                f"SELECT COUNT(*) FROM {TABLE_NAME} {active_where} "
                f"AND {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) <> ''"
                if active_where else
                f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE {col} IS NOT NULL AND TRIM(CAST({col} AS TEXT)) <> ''"
            ).fetchone()[0]

        out = {
            "db_exists": True,
            "table_exists": True,
            "total_cards": total,
            "active_cards": active,
            "konu_ozeti_dolu": count_nonempty("konu_ozeti"),
            "sonuc_ozeti_dolu": count_nonempty("sonuc_ozeti"),
            "anahtar_dolu": count_nonempty("anahtar"),
            "columns": cols,
        }
        return out
    finally:
        conn.close()


def pct(n, d):
    try:
        return round((float(n) / float(d)) * 100, 2) if d else 0
    except Exception:
        return 0


def status_class(ok=None, warning=False):
    if ok is True and not warning:
        return "ok"
    if warning:
        return "warn"
    if ok is False:
        return "bad"
    return "neutral"


def metric_html(label, value, sub="", ok=None, warning=False):
    cls = status_class(ok, warning)
    return f"""
<div class="metric {cls}">
  <div class="label">{escape(label)}</div>
  <div class="value">{escape(str(value))}</div>
  <div class="sub">{escape(str(sub))}</div>
</div>
"""


def section(title, body):
    return f"""
<section class="card">
  <h2>{escape(title)}</h2>
  {body}
</section>
"""


def table_rows(rows):
    out = []
    for name, value, note in rows:
        out.append(f"<tr><td>{escape(str(name))}</td><td>{escape(str(value))}</td><td>{escape(str(note))}</td></tr>")
    return "<table><tr><th>Alan</th><th>Değer</th><th>Not</th></tr>" + "".join(out) + "</table>"


def build_dashboard():
    run_tag = tag()

    states = {}
    for key, prefix in {
        "181": "181_v3_final_master_controller_state_",
        "182": "182_v2_production_drift_state_",
        "183": "183_sampling_qa_state_",
        "170": "170_export_state_",
        "169": "169_db_importer_state_",
        "177": "177_hukuki_dogruluk_state_",
        "175": "175_v2_ai_kapsam_state_",
        "176": "176_onceliklendirme_state_",
        "178": "178_birlestirme_hakemi_state_",
        "179": "179_kart_optimizasyon_state_",
        "180": "180_v2_karmasiklik_state_",
        "173": "173_v2_master_acceptance_state_",
    }.items():
        p, s = latest_state(prefix)
        states[key] = {"path": p, "state": s}

    db = db_counts()

    s181 = states["181"]["state"] or {}
    s182 = states["182"]["state"] or {}
    s183 = states["183"]["state"] or {}
    s170 = states["170"]["state"] or {}
    s177 = states["177"]["state"] or {}
    s175 = states["175"]["state"] or {}
    s180 = states["180"]["state"] or {}

    final_ready = bool(s181.get("final_ready_for_large_production"))
    drift_decision = s182.get("final_decision", "YOK")
    drift_score = s182.get("final_drift_score", "YOK")
    new_model_cards = s182.get("new_model_cards", "YOK")
    legacy_cards = s182.get("legacy_cards", "YOK")
    active_export = s170.get("active_rows_exported", "YOK")
    sampling_ready = s183.get("ready_for_ai_qa", False)
    sample_count = s183.get("sample_count_created", "YOK")

    # Overall status
    warnings = []
    if drift_decision == "WARNING":
        warnings.append("Drift analizi WARNING verdi; yeni model örnek sayısı henüz düşük olabilir.")
    if not sampling_ready:
        warnings.append("Sampling QA kısmen hazır; bazı örneklerin production row'u bulunamadı.")
    if s180 and as_float(s180.get("avg_planning_score", 0)) < 70:
        warnings.append("180 planlama puanı düşük; ancak eksik kart/fail yoksa üretimi bloklamaz.")

    overall_ok = final_ready and drift_decision in {"PASS", "WARNING"} and bool(s183.get("ready_for_184", True))

    html_path = os.path.join(DASHBOARD_DIR, f"184_production_dashboard_{run_tag}.html")
    txt_path = os.path.join(RAPOR_DIR, f"184_production_dashboard_raporu_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"184_production_dashboard_state_{run_tag}.json")

    metrics = ""
    metrics += metric_html("Final Üretim Durumu", "EVET" if final_ready else "HAYIR", "181 v3 sonucu", ok=final_ready)
    metrics += metric_html("Aktif Export Kart", active_export, "170 Web/RAG export", ok=as_int(active_export) > 0)
    metrics += metric_html("Drift Skoru", f"{drift_score}/100", f"Karar: {drift_decision}", ok=drift_decision == "PASS", warning=drift_decision == "WARNING")
    metrics += metric_html("Yeni Model Kart", new_model_cards, f"Eski model: {legacy_cards}", ok=as_int(new_model_cards) > 0, warning=as_int(new_model_cards) < 100)
    metrics += metric_html("Sampling QA", sample_count, "Hazır: EVET" if sampling_ready else "Hazır: KISMEN", ok=sampling_ready, warning=not sampling_ready)
    metrics += metric_html("DB Aktif Kart", db.get("active_cards", "YOK"), "SQLite", ok=db.get("active_cards", 0) > 0)

    db_section = table_rows([
        ("DB toplam kart", db.get("total_cards", "YOK"), ""),
        ("DB aktif kart", db.get("active_cards", "YOK"), ""),
        ("Konu özeti dolu", db.get("konu_ozeti_dolu", "YOK"), f"%{pct(db.get('konu_ozeti_dolu',0), db.get('active_cards',0))}"),
        ("Sonuç özeti dolu", db.get("sonuc_ozeti_dolu", "YOK"), f"%{pct(db.get('sonuc_ozeti_dolu',0), db.get('active_cards',0))}"),
        ("Anahtar dolu", db.get("anahtar_dolu", "YOK"), f"%{pct(db.get('anahtar_dolu',0), db.get('active_cards',0))}"),
    ])

    quality_rows = [
        ("175 Coverage", s175.get("avg_coverage_score", "YOK"), f"ready={s175.get('ready_for_176')}"),
        ("176 Priority", (states["176"]["state"] or {}).get("avg_priority_coverage", "YOK"), f"ready={(states['176']['state'] or {}).get('ready_for_177')}"),
        ("177 Hukuki Doğruluk", s177.get("avg_legal_accuracy_score", "YOK"), f"fail_cards={s177.get('fail_cards')}"),
        ("178 Merge", (states["178"]["state"] or {}).get("reduction_rate", "YOK"), f"merge={(states['178']['state'] or {}).get('merge_recommended_count')}"),
        ("179 Optimizasyon", (states["179"]["state"] or {}).get("reduction_rate", "YOK"), f"ready={(states['179']['state'] or {}).get('ready_for_180')}"),
        ("180 Karmaşıklık", s180.get("avg_planning_score", "YOK"), f"too_few={s180.get('too_few_count')}"),
        ("173 Acceptance", (states["173"]["state"] or {}).get("score", "YOK"), f"ready={(states['173']['state'] or {}).get('master_ready_for_large_production')}"),
    ]

    warnings_html = "<ul>" + "".join(f"<li>{escape(w)}</li>" for w in warnings) + "</ul>" if warnings else "<p>Uyarı yok.</p>"

    state_rows = []
    for k, obj in states.items():
        state_rows.append((k, obj["path"] or "YOK", ""))

    html = f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<title>184 Production Dashboard</title>
<style>
body{{font-family:Arial,sans-serif;background:#f3f5f8;color:#17202a;margin:0;padding:24px}}
.header{{background:#0E1A33;color:white;padding:24px;border-radius:16px;margin-bottom:22px}}
.header h1{{margin:0 0 8px}}.badge{{display:inline-block;border-radius:999px;padding:7px 12px;margin-top:8px;background:#F4C542;color:#0E1A33;font-weight:bold}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:22px}}
.metric{{background:white;border-radius:14px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,.06);border-top:6px solid #94a3b8}}
.metric.ok{{border-top-color:#16a34a}}.metric.warn{{border-top-color:#f59e0b}}.metric.bad{{border-top-color:#dc2626}}
.label{{color:#64748b;font-size:13px;font-weight:bold}}.value{{font-size:28px;font-weight:bold;margin:8px 0;color:#0E1A33}}.sub{{font-size:13px;color:#64748b}}
.card{{background:white;border-radius:16px;padding:20px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.06)}}
h2{{margin-top:0;color:#0E1A33}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #e5e7eb;text-align:left;padding:9px}}th{{background:#f8fafc;color:#334155}}
.status-ok{{color:#16a34a;font-weight:bold}}.status-warn{{color:#f59e0b;font-weight:bold}}.status-bad{{color:#dc2626;font-weight:bold}}
@media(max-width:950px){{.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="header">
  <h1>184 Production Dashboard</h1>
  <div>Tarih: {escape(now_tr())}</div>
  <div class="badge">Genel Durum: {'ÜRETİME HAZIR' if overall_ok else 'KONTROL GEREKİR'}</div>
</div>

<div class="grid">
{metrics}
</div>

{section("Kalite Katmanları", table_rows(quality_rows))}
{section("DB / Export Durumu", db_section)}
{section("Uyarılar", warnings_html)}
{section("State Dosyaları", table_rows(state_rows))}
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("184 - PRODUCTION DASHBOARD RAPORU\n")
        f.write("="*80 + "\n\n")
        f.write(f"Tarih                         : {now_tr()}\n")
        f.write(f"Genel durum                   : {'ÜRETİME HAZIR' if overall_ok else 'KONTROL GEREKİR'}\n")
        f.write(f"Final üretim hazır            : {'EVET' if final_ready else 'HAYIR'}\n")
        f.write(f"Aktif export kart             : {active_export}\n")
        f.write(f"Drift skoru                   : {drift_score}/100\n")
        f.write(f"Drift kararı                  : {drift_decision}\n")
        f.write(f"Yeni model kart               : {new_model_cards}\n")
        f.write(f"Eski model kart               : {legacy_cards}\n")
        f.write(f"Sampling QA                   : {'EVET' if sampling_ready else 'KISMEN'}\n\n")

        f.write("KALITE KATMANLARI\n")
        f.write("-"*80 + "\n")
        for name, value, note in quality_rows:
            f.write(f"{name:<28}: {value} | {note}\n")

        f.write("\nUYARILAR\n")
        f.write("-"*80 + "\n")
        if warnings:
            for w in warnings:
                f.write(f"- {w}\n")
        else:
            f.write("- Yok\n")

        f.write("\nDOSYALAR\n")
        f.write("-"*80 + "\n")
        f.write(f"HTML Dashboard                : {html_path}\n")
        f.write(f"TXT Rapor                     : {txt_path}\n")
        f.write(f"State                         : {state_path}\n")

    dashboard_state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "overall_ready": overall_ok,
        "final_ready_181": final_ready,
        "drift_decision": drift_decision,
        "drift_score": drift_score,
        "new_model_cards": new_model_cards,
        "legacy_cards": legacy_cards,
        "active_export_cards": active_export,
        "sampling_ready": sampling_ready,
        "warnings": warnings,
        "html_path": html_path,
        "txt_path": txt_path,
        "ready_for_185": True,
        "next_step": "185_Auto_Recovery_Engine.py",
        "state_files": {k: v["path"] for k, v in states.items()},
    }
    write_json(state_path, dashboard_state)

    try:
        webbrowser.open(html_path)
    except Exception:
        pass

    return html_path, txt_path, state_path, dashboard_state


def main():
    print("=" * 80)
    print("184 - PRODUCTION DASHBOARD")
    print("=" * 80)

    html_path, txt_path, state_path, st = build_dashboard()

    print("\n184 PRODUCTION DASHBOARD TAMAMLANDI")
    print("-" * 80)
    print(f"Genel durum                   : {'ÜRETİME HAZIR' if st['overall_ready'] else 'KONTROL GEREKİR'}")
    print(f"Final 181 hazır               : {'EVET' if st['final_ready_181'] else 'HAYIR'}")
    print(f"Drift                         : {st['drift_decision']} ({st['drift_score']}/100)")
    print(f"Yeni model kart               : {st['new_model_cards']}")
    print(f"Sampling QA                   : {'EVET' if st['sampling_ready'] else 'KISMEN'}")
    print(f"185'e geçilebilir mi           : EVET")

    print("\nDosyalar:")
    print(html_path)
    print(txt_path)
    print(state_path)


if __name__ == "__main__":
    main()
