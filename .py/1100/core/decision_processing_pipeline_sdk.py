# -*- coding: utf-8 -*-
import json, sqlite3, re
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PYDIR = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
PIPELINE_DIR = STATE / "decision_processing_pipeline"
SUPPORT_IDS = ["900", "1000", "800", "801", "172", "177", "173", "170", "169"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class DecisionProcessingPipelineSDK:
    def __init__(self, name="1100 Decision Processing Pipeline SDK", batch_size=10, execute=False):
        self.name = name
        self.batch_size = int(batch_size)
        self.execute = bool(execute)

    def modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PYDIR.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def dbs(self):
        out = []
        for name in ("kik.db", "kik_proje.db", "hukuki_kartlar.db"):
            p = BASE / name
            item = {"path": str(p), "exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0, "tables": []}
            if p.exists():
                try:
                    con = sqlite3.connect(str(p)); cur = con.cursor()
                    tables = cur.execute("select name from sqlite_master where type='table'").fetchall()
                    for (t,) in tables[:30]:
                        try: c = cur.execute("select count(*) from " + t).fetchone()[0]
                        except Exception: c = None
                        item["tables"].append({"table": t, "count": c})
                    con.close()
                except Exception as e:
                    item["error"] = str(e)
            out.append(item)
        return out

    def sources(self, dbs):
        db = next((d["path"] for d in dbs if d["exists"]), None)
        if not db:
            return [{"source_id": i + 1, "source": "synthetic", "raw_text": "Kamu İhale Kurulu kararı örnek metni. İhale süreci, yeterlik kriteri, teklif değerlendirmesi ve mevzuata uygunluk incelenmiştir. Kurul başvuru hakkında karar vermiştir."} for i in range(self.batch_size)]
        try:
            con = sqlite3.connect(db); cur = con.cursor()
            tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table'").fetchall()]
            table = next((t for t in ("hukuki_kartlar", "kararlar", "decisions", "kik_kararlari") if t in tables), tables[0] if tables else None)
            if not table: raise RuntimeError("table not found")
            rows = cur.execute("select rowid,* from " + table + " limit ?", (self.batch_size,)).fetchall()
            cols = [d[0] for d in cur.description]; con.close()
            res = []
            for i, row in enumerate(rows, 1):
                data = dict(zip(cols, row)); raw = " ".join(str(v) for v in data.values() if v is not None)[:8000]
                res.append({"source_id": i, "source_table": table, "rowid": data.get("rowid"), "raw_text": raw})
            if res: return res
        except Exception as e:
            return [{"source_id": i + 1, "source": "synthetic", "error": str(e), "raw_text": "Kamu İhale Kurulu kararı örnek metni. İhale işlemleri ve hukuki sonuç incelenmiştir."} for i in range(self.batch_size)]
        return [{"source_id": i + 1, "source": "synthetic", "raw_text": "Kamu İhale Kurulu kararı örnek metni."} for i in range(self.batch_size)]

    def norm(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def meta(self, text):
        no = re.search(r"(\d{4}/[A-ZÇĞİÖŞÜ\.\-]+-?\d+|\d{4}/[A-Z]{1,3}\.[IVX]+-\d+)", text)
        dt = re.search(r"(\d{2}\.\d{2}\.\d{4}|\d{2}/\d{2}/\d{4})", text)
        return {"karar_no": no.group(1) if no else None, "karar_tarihi": dt.group(1) if dt else None}

    def title(self, text):
        low = text.lower()
        if "aşırı düşük" in low: return "Aşırı düşük teklif açıklaması hangi durumda uygun kabul edilir?"
        if "iş deneyim" in low: return "İş deneyim belgesi yeterlik değerlendirmesinde nasıl dikkate alınır?"
        if "yaklaşık maliyet" in low: return "Yaklaşık maliyet üzerindeki teklif ihale sonucunu nasıl etkiler?"
        if "şikayet" in low or "itirazen" in low: return "Şikâyet ve itirazen şikâyet başvurusu hangi şartlarda incelenir?"
        return "İhale sürecindeki değerlendirme işlemleri hangi hukuki ölçütlere göre incelenir?"

    def decision_summary(self, text):
        text = self.norm(text)
        return text if len(text) <= 500 else text[:500].rsplit(" ", 1)[0] + "..."

    def result_summary(self, text):
        low = text.lower()
        if "düzeltici işlem" in low: return "Kurul, aykırılığın düzeltici işlemle giderilmesine karar vermiştir."
        if "iptal" in low: return "Kararda ihale süreci veya ilgili işlem yönünden iptal sonucu değerlendirilmiştir."
        if "redd" in low or "red" in low: return "Başvuru iddiaları yerinde görülmeyerek başvurunun reddi sonucuna ulaşılmıştır."
        return "Kurul, somut olay ve ilgili mevzuat çerçevesinde başvuru konusu işlemin hukuki sonucunu belirlemiştir."

    def tags(self, text):
        low = text.lower(); keywords = []; legislation = []
        mapping = {"aşırı düşük":"Aşırı düşük teklif", "iş deneyim":"İş deneyimi", "yaklaşık maliyet":"Yaklaşık maliyet", "şikayet":"Şikâyet", "itirazen":"İtirazen şikâyet", "yeterlik":"Yeterlik kriteri", "4734":"4734 sayılı Kanun", "4735":"4735 sayılı Kanun"}
        for k, v in mapping.items():
            if k in low:
                (legislation if "Kanun" in v else keywords).append(v)
        return {"keywords": keywords[:10], "legislation": legislation[:10]}

    def quality(self, card):
        score = 100; warnings = []
        for field in ("question_title", "decision_summary", "result_summary"):
            if not card.get(field): score -= 25; warnings.append(field + " missing")
        if card.get("raw_length", 0) < 50: score -= 15; warnings.append("raw text short")
        return {"score": max(score, 0), "status": "PASS" if score >= 80 else "WARN" if score >= 60 else "FAIL", "warnings": warnings}

    def card(self, item):
        text = self.norm(item.get("raw_text", "")); metadata = self.meta(text); tags = self.tags(text)
        card = {"source_id": item.get("source_id"), "source_table": item.get("source_table"), "rowid": item.get("rowid"), "karar_no": metadata["karar_no"], "karar_tarihi": metadata["karar_tarihi"], "question_title": self.title(text), "decision_summary": self.decision_summary(text), "result_summary": self.result_summary(text), "keywords": tags["keywords"], "legislation": tags["legislation"], "raw_length": len(text), "status": "CARD_BUILT"}
        card["quality"] = self.quality(card)
        return card

    def validate(self, modules, cards):
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        total = len(cards); pass_count = sum(1 for c in cards if c["quality"]["status"] == "PASS")
        card_score = round(pass_count / total * 100, 2) if total else 0
        avg = round(sum(c["quality"]["score"] for c in cards) / total, 2) if total else 0
        score = round(support_score * 0.35 + card_score * 0.35 + avg * 0.30, 2)
        errors = []; warnings = []
        if support_score < 60: errors.append("Support modules are incomplete.")
        if card_score < 80: warnings.append("Some cards need quality review.")
        if not self.execute: warnings.append("Dry-run mode: DB write/publish not executed.")
        return {"score": score, "support_score": support_score, "card_score": card_score, "average_card_quality": avg, "pass_count": pass_count, "total": total, "decision": "DECISION PIPELINE READY" if not errors else "DECISION PIPELINE BLOCKED", "errors": errors, "warnings": warnings}

    def run(self):
        PIPELINE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.modules(); dbs = self.dbs(); sources = self.sources(dbs); cards = [self.card(i) for i in sources]; validation = self.validate(modules, cards)
        ts = now_stamp(); snapshot = PIPELINE_DIR / "1100_decision_processing_pipeline_snapshot.json"; cards_file = PIPELINE_DIR / ("1100_cards_" + ts + ".json"); dashboard = PIPELINE_DIR / "1100_decision_processing_pipeline_dashboard.json"; state = PIPELINE_DIR / ("1100_decision_processing_pipeline_state_" + ts + ".json"); report = REPORTS / ("1100_decision_processing_pipeline_sdk_raporu_" + ts + ".txt")
        payload = {"module": self.name, "created_at": now_text(), "batch_size": self.batch_size, "execute": self.execute, "modules": modules, "databases": dbs, "sources_count": len(sources), "cards": cards, "validation": validation}
        write_json(snapshot, payload); write_json(state, payload); write_json(cards_file, cards); write_json(dashboard, {"status": validation["decision"], "score": validation["score"], "cards": len(cards), "pass_count": validation["pass_count"], "average_quality": validation["average_card_quality"], "execute": self.execute, "warnings": len(validation["warnings"]), "errors": len(validation["errors"])})
        lines = ["=" * 80, "1100 DECISION PROCESSING PIPELINE SDK", "=" * 80, "Validation : " + str(validation["decision"]), "Score      : " + str(validation["score"]) + " / 100", "Cards      : " + str(len(cards)), "PASS       : " + str(validation["pass_count"]), "AvgQuality : " + str(validation["average_card_quality"]), "Mode       : " + ("EXECUTE" if self.execute else "DRY_RUN"), "", "Dosyalar:", str(snapshot), str(cards_file), str(dashboard), str(report)]
        report.write_text("\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "cards": str(cards_file), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
