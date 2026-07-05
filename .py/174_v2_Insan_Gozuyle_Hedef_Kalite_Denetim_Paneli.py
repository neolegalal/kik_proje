# -*- coding: utf-8 -*-
"""
174 v2 - INSAN GOZUYLE HEDEF 1 / HEDEF 2 KALITE DENETIM PANELI

Kullanım:
  python ".py\\174_v2_Insan_Gozuyle_Hedef_Kalite_Denetim_Paneli.py" 10

Amaç:
- DB'de konu_ozeti ve anahtar alanı dolu olan yeni model kartlarından örnek seçer.
- Hedef 1 WEB ve Hedef 2 AI/RAG açısından insan gözüyle kontrol edilebilecek HTML + TXT rapor üretir.
- API kullanmaz, DB'ye yazmaz.
"""

import os
import re
import sys
import json
import sqlite3
import webbrowser
from datetime import datetime
from html import escape

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
TABLE_NAME = "hukuki_kartlar"

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now_tr():
    return datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def get_limit():
    if len(sys.argv) >= 2:
        try:
            return max(1, int(sys.argv[1]))
        except Exception:
            return 10
    return 10


def safe(v):
    return "" if v is None else str(v).strip()


def norm(s):
    return re.sub(r"\s+", " ", safe(s)).strip()


def words(s):
    s = norm(s)
    return len(s.split()) if s else 0


def parse_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s:
        return []
    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return [str(x).strip() for x in obj if str(x).strip()]
    except Exception:
        pass
    if s.startswith("[") and s.endswith("]"):
        try:
            import ast
            obj = ast.literal_eval(s)
            if isinstance(obj, list):
                return [str(x).strip() for x in obj if str(x).strip()]
        except Exception:
            pass
    return [p.strip(" -•\t\r\n") for p in s.replace(";", ",").split(",") if p.strip(" -•\t\r\n")]


def list_text(items):
    return ", ".join(parse_list(items))


def clamp(n):
    return max(0, min(100, int(round(n))))


def bar(score):
    score = clamp(score)
    filled = int(round(score / 10))
    return "█" * filled + "░" * (10 - filled)


def status(score):
    score = clamp(score)
    if score >= 90:
        return "YEŞİL"
    if score >= 75:
        return "SARI"
    return "KIRMIZI"


def css_status(score):
    score = clamp(score)
    if score >= 90:
        return "green"
    if score >= 75:
        return "yellow"
    return "red"


def overlap_ratio(a, b):
    aw = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{3,}", norm(a).lower()))
    bw = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{3,}", norm(b).lower()))
    if not aw or not bw:
        return 0
    return len(aw & bw) / max(1, min(len(aw), len(bw)))


NAME_HINTS = [
    " ltd", " ltd.", " limited", " a.ş", " aş", " anonim", " şirket",
    " belediyesi", " bakanlığı", " müdürlüğü", " üniversitesi", " valiliği",
    " genel müdürlüğü", " il müdürlüğü", " tic.", " san.", " inş.", " turizm"
]
RESULT_HINTS = ["kurul", "tespit", "sonucuna", "karar", "düzeltici", "redd", "iptal", "mevzuata aykırı", "uygun olmadığı", "yerinde"]


def has_name_hint(s):
    ss = " " + norm(s).lower()
    return any(h in ss for h in NAME_HINTS)


def has_question(s):
    ss = norm(s).lower()
    return "?" in ss or any(x in ss for x in [" mı", " mi", " mu", " mü"])


def read_columns(conn):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({TABLE_NAME})")
    return [r[1] for r in cur.fetchall()]


def pick(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    return None


def active_where(cols):
    if "aktif" in cols:
        return "AND COALESCE(aktif, 1) = 1"
    if "is_active" in cols:
        return "AND COALESCE(is_active, 1) = 1"
    if "durum" in cols:
        return "AND COALESCE(durum, 'aktif') NOT IN ('pasif', 'PASIF', 'inactive', 'INACTIVE')"
    return ""


def read_cards(limit):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cols = read_columns(conn)

    c_id = pick(cols, ["id", "kart_id"])
    c_karar = pick(cols, ["karar_no"])
    c_baslik = pick(cols, ["baslik"])
    c_soru = pick(cols, ["hukuki_soru"])
    c_konu = pick(cols, ["konu_ozeti"])
    c_sonuc_ozeti = pick(cols, ["sonuc_ozeti"])
    c_sonuc = pick(cols, ["sonuc"])
    c_sonuc_tipi = pick(cols, ["sonuc_tipi"])
    c_emsal = pick(cols, ["emsal_ilke"])
    c_mevzuat = pick(cols, ["mevzuat"])
    c_anahtar = pick(cols, ["anahtar"])
    c_guven = pick(cols, ["guven"])
    c_created = pick(cols, ["created_at"])
    c_updated = pick(cols, ["updated_at"])

    aw = active_where(cols)
    order_col = c_updated or c_created or c_id or c_karar
    order_sql = f"ORDER BY {order_col} DESC" if order_col else ""

    rows = conn.execute(f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE konu_ozeti IS NOT NULL AND TRIM(CAST(konu_ozeti AS TEXT)) <> ''
          AND anahtar IS NOT NULL AND TRIM(CAST(anahtar AS TEXT)) <> ''
          {aw}
        {order_sql}
        LIMIT ?
    """, (limit,)).fetchall()

    cards = []
    for r in rows:
        sonuc = safe(r[c_sonuc]) if c_sonuc else ""
        sonuc_ozeti = safe(r[c_sonuc_ozeti]) if c_sonuc_ozeti else sonuc
        cards.append({
            "id": safe(r[c_id]) if c_id else "",
            "karar_no": safe(r[c_karar]) if c_karar else "",
            "baslik": safe(r[c_baslik]) if c_baslik else "",
            "hukuki_soru": safe(r[c_soru]) if c_soru else "",
            "konu_ozeti": safe(r[c_konu]) if c_konu else "",
            "sonuc_ozeti": sonuc_ozeti or sonuc,
            "sonuc": sonuc,
            "sonuc_tipi": safe(r[c_sonuc_tipi]) if c_sonuc_tipi else "",
            "emsal_ilke": safe(r[c_emsal]) if c_emsal else "",
            "mevzuat": parse_list(r[c_mevzuat]) if c_mevzuat else [],
            "anahtar": parse_list(r[c_anahtar]) if c_anahtar else [],
            "guven": safe(r[c_guven]) if c_guven else "",
        })

    total_active = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE 1=1 {aw}").fetchone()[0]
    total_new = conn.execute(f"""
        SELECT COUNT(*)
        FROM {TABLE_NAME}
        WHERE konu_ozeti IS NOT NULL AND TRIM(CAST(konu_ozeti AS TEXT)) <> ''
          AND anahtar IS NOT NULL AND TRIM(CAST(anahtar AS TEXT)) <> ''
          {aw}
    """).fetchone()[0]
    conn.close()
    return cards, total_active, total_new


def score_card(c):
    issues = []
    positives = []

    baslik_score = 100
    bw = words(c["baslik"])
    if bw < 3:
        baslik_score -= 35; issues.append("Başlık çok kısa.")
    if bw > 16:
        baslik_score -= 15; issues.append("Başlık uzun olabilir.")
    if has_name_hint(c["baslik"]):
        baslik_score -= 20; issues.append("Başlıkta kurum/şirket adı olabilir.")
    if baslik_score >= 90:
        positives.append("Başlık web için uygun görünüyor.")

    soru_score = 100
    if not has_question(c["hukuki_soru"]):
        soru_score -= 25; issues.append("Hukuki soru soru cümlesi gibi görünmüyor.")
    if words(c["hukuki_soru"]) < 6:
        soru_score -= 20; issues.append("Hukuki soru kısa kalabilir.")
    if has_name_hint(c["hukuki_soru"]):
        soru_score -= 25; issues.append("Hukuki soru olaya/kuruma özel olabilir.")
    if soru_score >= 90:
        positives.append("Hukuki soru danışmanlıkta kullanılabilir görünüyor.")

    konu_score = 100
    if words(c["konu_ozeti"]) < 25:
        konu_score -= 30; issues.append("Konu özeti kısa.")
    if words(c["konu_ozeti"]) > 130:
        konu_score -= 10; issues.append("Konu özeti uzun olabilir.")
    if sum(1 for h in RESULT_HINTS if h in c["konu_ozeti"].lower()) >= 4:
        konu_score -= 15; issues.append("Konu özeti sonuca fazla yaklaşmış olabilir.")
    if konu_score >= 90:
        positives.append("Konu özeti olay ve inceleme meselesini anlatıyor.")

    sonuc_score = 100
    if words(c["sonuc_ozeti"]) < 20:
        sonuc_score -= 30; issues.append("Sonuç özeti kısa.")
    if words(c["sonuc_ozeti"]) > 120:
        sonuc_score -= 10; issues.append("Sonuç özeti uzun olabilir.")
    if not any(h in c["sonuc_ozeti"].lower() for h in RESULT_HINTS):
        sonuc_score -= 20; issues.append("Sonuç özeti Kurul sonucunu net göstermiyor olabilir.")
    if sonuc_score >= 90:
        positives.append("Sonuç özeti Kurul sonucunu gösteriyor.")

    ayrim_score = 100
    ov = overlap_ratio(c["konu_ozeti"], c["sonuc_ozeti"])
    if ov > 0.75:
        ayrim_score -= 40; issues.append("Konu ve sonuç özeti birbirine fazla benziyor.")
    elif ov > 0.55:
        ayrim_score -= 15; issues.append("Konu/sonuç ayrımı insan gözüyle kontrol edilmeli.")
    if ayrim_score >= 90:
        positives.append("Konu ve sonuç ayrımı yeterli görünüyor.")

    emsal_score = 100
    if words(c["emsal_ilke"]) < 8:
        emsal_score -= 25; issues.append("Emsal ilke kısa olabilir.")
    if overlap_ratio(c["emsal_ilke"], c["sonuc_ozeti"]) > 0.7:
        emsal_score -= 20; issues.append("Emsal ilke sonuç özetini tekrar ediyor olabilir.")
    if has_name_hint(c["emsal_ilke"]):
        emsal_score -= 20; issues.append("Emsal ilke olaya özel kalmış olabilir.")
    if emsal_score >= 90:
        positives.append("Emsal ilke genellenebilir görünüyor.")

    anahtar_score = 100
    if len(c["anahtar"]) < 5:
        anahtar_score -= 35; issues.append("Anahtar sayısı az.")
    if len(c["anahtar"]) > 12:
        anahtar_score -= 10; issues.append("Anahtar sayısı fazla olabilir.")
    if anahtar_score >= 90:
        positives.append("Anahtarlar arama/RAG için yeterli görünüyor.")

    mevzuat_score = 100
    if len(c["mevzuat"]) == 0:
        mevzuat_score -= 35; issues.append("Mevzuat listesi boş.")
    if len(c["mevzuat"]) > 8:
        mevzuat_score -= 10; issues.append("Mevzuat listesi kalabalık olabilir.")
    if mevzuat_score >= 90:
        positives.append("Mevzuat ilişkisi makul görünüyor.")

    web_score = clamp(baslik_score*0.22 + konu_score*0.28 + sonuc_score*0.25 + anahtar_score*0.15 + ayrim_score*0.10)
    rag_score = clamp(soru_score*0.25 + konu_score*0.18 + sonuc_score*0.18 + emsal_score*0.20 + anahtar_score*0.10 + mevzuat_score*0.09)
    general_score = clamp((web_score + rag_score) / 2)

    if general_score >= 90:
        verdict = "Bu kart Hedef 1 WEB ve Hedef 2 AI/RAG için kullanılabilir kaliteye yakın görünüyor."
    elif general_score >= 75:
        verdict = "Bu kart kullanılabilir; ancak işaretli alanlar insan gözüyle kontrol edilmeli."
    else:
        verdict = "Bu kart riskli görünüyor; yeniden üretim veya manuel düzeltme gerekebilir."

    return {
        "scores": {
            "baslik": clamp(baslik_score),
            "hukuki_soru": clamp(soru_score),
            "konu_ozeti": clamp(konu_score),
            "sonuc_ozeti": clamp(sonuc_score),
            "konu_sonuc_ayrimi": clamp(ayrim_score),
            "emsal_ilke": clamp(emsal_score),
            "anahtar": clamp(anahtar_score),
            "mevzuat": clamp(mevzuat_score),
            "web": web_score,
            "rag": rag_score,
            "general": general_score,
        },
        "issues": issues,
        "positives": positives,
        "verdict": verdict,
        "status": status(general_score),
    }


def chips(items):
    items = parse_list(items)
    if not items:
        return '<span class="muted">Yok</span>'
    return " ".join(f'<span class="chip">{escape(x)}</span>' for x in items)


def metric(label, score):
    sc = clamp(score)
    return f'<div class="metric {css_status(sc)}"><div class="ml">{escape(label)}</div><div class="ms">{sc}/100</div><div class="mb">{bar(sc)}</div></div>'


def render_html(cards, evals, total_active, total_new, html_path):
    avg_web = clamp(sum(e["scores"]["web"] for e in evals) / len(evals)) if evals else 0
    avg_rag = clamp(sum(e["scores"]["rag"] for e in evals) / len(evals)) if evals else 0
    avg_gen = clamp(sum(e["scores"]["general"] for e in evals) / len(evals)) if evals else 0

    blocks = []
    for i, (c, e) in enumerate(zip(cards, evals), start=1):
        s = e["scores"]
        issues = "".join(f"<li>{escape(x)}</li>" for x in e["issues"]) if e["issues"] else "<li>Belirgin sorun yok.</li>"
        positives = "".join(f"<li>{escape(x)}</li>" for x in e["positives"]) if e["positives"] else "<li>Otomatik olumlu not yok; insan kontrolü önerilir.</li>"
        blocks.append(f"""
<section class="card">
  <div class="head">
    <div><div class="small">Örnek {i} • Karar No: <b>{escape(c['karar_no'])}</b> • DB ID: {escape(c['id'])}</div><h2>{escape(c['baslik'])}</h2></div>
    <div class="status {css_status(s['general'])}"><div>{escape(e['status'])}</div><b>{s['general']}/100</b></div>
  </div>
  <div class="scoregrid">{metric("WEB", s["web"])}{metric("AI/RAG", s["rag"])}{metric("GENEL", s["general"])}</div>
  <div class="twocol">
    <div class="box h1">
      <h3>HEDEF 1 — WEB</h3>
      <p class="label">Başlık</p><p class="title">{escape(c['baslik'])}</p>{metric("Başlık", s["baslik"])}
      <p class="label">Konu Özeti</p><p>{escape(c['konu_ozeti'])}</p>{metric("Konu Özeti", s["konu_ozeti"])}
      <p class="label">Sonuç Özeti</p><p>{escape(c['sonuc_ozeti'])}</p>{metric("Sonuç Özeti", s["sonuc_ozeti"])}
      <p class="label">Anahtar</p><p>{chips(c['anahtar'])}</p>{metric("Anahtar", s["anahtar"])}
    </div>
    <div class="box h2">
      <h3>HEDEF 2 — AI Danışmanlık / RAG</h3>
      <p class="label">Hukuki Soru</p><p class="question">{escape(c['hukuki_soru'])}</p>{metric("Hukuki Soru", s["hukuki_soru"])}
      <p class="label">Emsal İlke</p><p>{escape(c['emsal_ilke'])}</p>{metric("Emsal İlke", s["emsal_ilke"])}
      <p class="label">Mevzuat</p><p>{chips(c['mevzuat'])}</p>{metric("Mevzuat", s["mevzuat"])}
      <p class="label">Konu/Sonuç Ayrımı</p>{metric("Ayrım", s["konu_sonuc_ayrimi"])}
    </div>
  </div>
  <div class="verdict"><h3>Panel Yorumu</h3><p>{escape(e['verdict'])}</p></div>
  <div class="reviewgrid">
    <div class="review good"><h3>Olumlu Notlar</h3><ul>{positives}</ul></div>
    <div class="review warn"><h3>Kontrol Edilecek Noktalar</h3><ul>{issues}</ul></div>
  </div>
  <div class="manual"><h3>Manuel Kontrol Kutuları</h3>
    <div class="checks">
      <label>☐ WEB: Başlık yayınlanabilir.</label><label>☐ WEB: Konu özeti doğru.</label>
      <label>☐ WEB: Sonuç özeti doğru.</label><label>☐ RAG: Hukuki soru genelleştirilmiş.</label>
      <label>☐ RAG: Emsal ilke uygulanabilir.</label><label>☐ RAG: Mevzuat ilişkisi makul.</label>
      <label>☐ RAG: Anahtarlar uygun.</label><label>☐ Genel: Kart kullanılabilir.</label>
    </div>
  </div>
</section>
""")

    html = f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>174 v2 Kalite Denetim Paneli</title>
<style>
body{{font-family:Arial,sans-serif;background:#f3f5f8;color:#18202a;margin:0;padding:24px}}
.header{{background:#0E1A33;color:white;padding:24px;border-radius:16px;margin-bottom:22px}}
.header h1{{margin:0 0 10px}}.summary{{display:flex;flex-wrap:wrap;gap:12px;margin-top:16px}}
.stat{{background:rgba(255,255,255,.12);padding:12px 14px;border-radius:12px}}.stat b{{color:#F4C542}}
.overall,.scoregrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}}
.card{{background:white;border-radius:16px;padding:22px;margin-bottom:24px;box-shadow:0 3px 14px rgba(0,0,0,.08)}}
.head{{display:flex;justify-content:space-between;gap:18px;border-bottom:1px solid #e3e8ef;padding-bottom:14px;margin-bottom:16px}}
h2{{margin:8px 0 0;color:#0E1A33}}h3{{margin-top:0;color:#0E1A33}}.small{{color:#647084;font-size:13px}}
.status{{min-width:90px;text-align:center;border-radius:14px;padding:10px 12px;font-size:13px}}.status b{{display:block;font-size:22px;margin-top:4px}}
.green{{background:#e6f6ec;color:#126c36;border:1px solid #a8ddb9}}.yellow{{background:#fff7df;color:#805d00;border:1px solid #f1d17a}}.red{{background:#ffe8e8;color:#9c1a1a;border:1px solid #efaaaa}}
.metric{{border:1px solid #dde3ec;border-radius:12px;padding:10px;margin:8px 0}}.ml{{font-size:12px;color:#596579;font-weight:bold}}.ms{{font-size:20px;font-weight:bold;margin:4px 0}}.mb{{font-family:Consolas,monospace;letter-spacing:1px}}
.twocol{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.box{{border:1px solid #e3e8ef;border-radius:14px;padding:16px}}.h1{{border-top:6px solid #0E1A33}}.h2{{border-top:6px solid #F4C542}}
.label{{font-size:12px;color:#657080;text-transform:uppercase;font-weight:bold;margin-bottom:4px}}.title,.question{{font-weight:bold;color:#0E1A33}}.question{{font-size:18px}}
.chip{{display:inline-block;background:#eef2f7;border:1px solid #dce2ea;border-radius:999px;padding:5px 9px;margin:3px;font-size:13px}}.muted{{color:#8a94a3}}
.verdict{{margin-top:16px;background:#f8fafc;border-left:5px solid #0E1A33;border-radius:12px;padding:14px}}
.reviewgrid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:16px}}.review{{border-radius:12px;padding:14px;border:1px solid #e0e6ef}}.good{{background:#f3fbf6}}.warn{{background:#fffaf0}}
.manual{{margin-top:16px;border:1px dashed #b9c2d0;border-radius:12px;padding:14px;background:#fbfcfe}}.checks{{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}}.checks label{{background:white;border:1px solid #e3e8ef;border-radius:8px;padding:8px}}
@media(max-width:950px){{.twocol,.reviewgrid,.scoregrid,.overall,.checks{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="header"><h1>174 v2 İnsan Gözüyle Hedef 1 / Hedef 2 Kalite Denetim Paneli</h1>
<div>Tarih: {escape(now_tr())}</div><div class="summary">
<div class="stat">DB aktif kart: <b>{total_active}</b></div><div class="stat">Yeni model dolu kart: <b>{total_new}</b></div><div class="stat">Bu rapordaki örnek: <b>{len(cards)}</b></div></div>
<div class="overall">{metric("Ortalama WEB", avg_web)}{metric("Ortalama AI/RAG", avg_rag)}{metric("Ortalama GENEL", avg_gen)}</div></div>
{''.join(blocks)}
</body></html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


def render_txt(cards, evals, total_active, total_new, txt_path):
    avg_web = clamp(sum(e["scores"]["web"] for e in evals) / len(evals)) if evals else 0
    avg_rag = clamp(sum(e["scores"]["rag"] for e in evals) / len(evals)) if evals else 0
    avg_gen = clamp(sum(e["scores"]["general"] for e in evals) / len(evals)) if evals else 0

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("174 v2 - INSAN GOZUYLE HEDEF 1 / HEDEF 2 KALITE DENETIM PANELI\n")
        f.write("="*80 + "\n\n")
        f.write(f"Tarih                  : {now_tr()}\n")
        f.write(f"DB aktif kart           : {total_active}\n")
        f.write(f"Yeni model dolu kart    : {total_new}\n")
        f.write(f"Bu rapordaki örnek      : {len(cards)}\n")
        f.write(f"Ortalama WEB puanı      : {avg_web}/100 {bar(avg_web)}\n")
        f.write(f"Ortalama AI/RAG puanı   : {avg_rag}/100 {bar(avg_rag)}\n")
        f.write(f"Ortalama GENEL puanı    : {avg_gen}/100 {bar(avg_gen)}\n\n")

        for i, (c, e) in enumerate(zip(cards, evals), start=1):
            s = e["scores"]
            f.write("="*80 + "\n")
            f.write(f"ÖRNEK {i} | {e['status']} | GENEL {s['general']}/100\n")
            f.write("="*80 + "\n")
            f.write(f"Karar No       : {c['karar_no']}\nDB ID          : {c['id']}\nBaşlık         : {c['baslik']}\nSonuç Tipi     : {c['sonuc_tipi']}\nGüven          : {c['guven']}\n")
            f.write(f"WEB Puanı      : {s['web']}/100 {bar(s['web'])}\nAI/RAG Puanı   : {s['rag']}/100 {bar(s['rag'])}\n\n")
            f.write("HEDEF 1 - WEB\n" + "-"*80 + "\n")
            f.write(f"Konu Özeti:\n{c['konu_ozeti']}\n\nSonuç Özeti:\n{c['sonuc_ozeti']}\n\nAnahtar:\n{list_text(c['anahtar'])}\n\n")
            f.write("HEDEF 2 - AI DANISMANLIK / RAG\n" + "-"*80 + "\n")
            f.write(f"Hukuki Soru:\n{c['hukuki_soru']}\n\nEmsal İlke:\n{c['emsal_ilke']}\n\nMevzuat:\n{list_text(c['mevzuat'])}\n\n")
            f.write("PANEL YORUMU\n" + "-"*80 + "\n" + e["verdict"] + "\n\n")
            f.write("KONTROL EDILECEK NOKTALAR\n" + "-"*80 + "\n")
            if e["issues"]:
                for x in e["issues"]:
                    f.write(f"- {x}\n")
            else:
                f.write("- Belirgin sorun yok.\n")
            f.write("\nMANUEL KONTROL\n" + "-"*80 + "\n")
            f.write("[ ] WEB: Başlık yayınlanabilir.\n[ ] WEB: Konu özeti doğru.\n[ ] WEB: Sonuç özeti doğru.\n[ ] RAG: Hukuki soru genelleştirilmiş.\n[ ] RAG: Emsal ilke uygulanabilir.\n[ ] RAG: Mevzuat ilişkisi makul.\n[ ] RAG: Anahtarlar uygun.\n[ ] Genel: Kart kullanılabilir.\n\n")


def main():
    print("="*80)
    print("174 v2 - INSAN GOZUYLE HEDEF 1 / HEDEF 2 KALITE DENETIM PANELI")
    print("="*80)

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB bulunamadı: {DB_PATH}")

    limit = get_limit()
    run_tag = tag()

    cards, total_active, total_new = read_cards(limit)
    evals = [score_card(c) for c in cards]

    html_path = os.path.join(RAPOR_DIR, f"174_v2_insan_gozuyle_hedef_kalite_paneli_{run_tag}.html")
    txt_path = os.path.join(RAPOR_DIR, f"174_v2_insan_gozuyle_hedef_kalite_paneli_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"174_v2_insan_gozuyle_hedef_kalite_paneli_state_{run_tag}.json")

    render_html(cards, evals, total_active, total_new, html_path)
    render_txt(cards, evals, total_active, total_new, txt_path)

    avg_web = clamp(sum(e["scores"]["web"] for e in evals) / len(evals)) if evals else 0
    avg_rag = clamp(sum(e["scores"]["rag"] for e in evals) / len(evals)) if evals else 0
    avg_gen = clamp(sum(e["scores"]["general"] for e in evals) / len(evals)) if evals else 0

    write_json(state_path, {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "limit": limit,
        "db_active_cards": total_active,
        "new_model_nonempty_cards": total_new,
        "sample_cards": len(cards),
        "avg_web_score": avg_web,
        "avg_rag_score": avg_rag,
        "avg_general_score": avg_gen,
        "html_path": html_path,
        "txt_path": txt_path,
        "state_path": state_path,
        "ready_for_manual_review": len(cards) > 0,
    })

    print("\n174 v2 KALITE DENETIM PANELI TAMAMLANDI")
    print("-"*80)
    print(f"DB aktif kart           : {total_active}")
    print(f"Yeni model dolu kart    : {total_new}")
    print(f"Örnek kart              : {len(cards)}")
    print(f"Ortalama WEB puanı      : {avg_web}/100 {bar(avg_web)}")
    print(f"Ortalama AI/RAG puanı   : {avg_rag}/100 {bar(avg_rag)}")
    print(f"Ortalama GENEL puanı    : {avg_gen}/100 {bar(avg_gen)}")
    print(f"Manuel kontrole hazır   : {'EVET' if cards else 'HAYIR'}")
    print("\nDosyalar:")
    print(html_path)
    print(txt_path)
    print(state_path)

    try:
        webbrowser.open(html_path)
    except Exception:
        pass


if __name__ == "__main__":
    main()
