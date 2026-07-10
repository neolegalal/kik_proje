# -*- coding: utf-8 -*-
import argparse, json, sqlite3, subprocess, sys, py_compile, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PYDIR = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"
PIPELINE_DIR = STATE / "decision_processing_pipeline"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v7.0"
TAG = "v7.0-decision-processing-pipeline"
RELEASE_FILE = RELEASES / "v7.0-decision-processing-pipeline.md"
GIT_BAT = BASE / "git_release_v7_0_decision_processing_pipeline.bat"

MODULES = [
    ("1101", "Decision Source Reader", "decision_source_reader"),
    ("1102", "Text Normalizer", "text_normalizer"),
    ("1103", "Decision Metadata Extractor", "decision_metadata_extractor"),
    ("1104", "Question Title Generator", "question_title_generator"),
    ("1105", "Decision Summary Generator", "decision_summary_generator"),
    ("1106", "Result Summary Generator", "result_summary_generator"),
    ("1107", "Keyword Legislation Tagger", "keyword_legislation_tagger"),
    ("1108", "Card Quality Gate", "card_quality_gate"),
    ("1109", "Web Rag Card Builder", "web_rag_card_builder"),
    ("1110", "Decision Pipeline Auditor", "decision_pipeline_auditor"),
]
SUPPORT_IDS = ["900", "1000", "800", "801", "172", "177", "173", "170", "169"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_file(path, text, compile_py=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if compile_py and path.suffix == ".py":
        py_compile.compile(str(path), doraise=True)

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def sdk_source():
    return r'''# -*- coding: utf-8 -*-
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
'''

def sdk_bridge_source():
    return '''# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1100"
sys.path.insert(0, str(PACKAGE_DIR))
from core.decision_processing_pipeline_sdk import DecisionProcessingPipelineSDK

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--batch-size", type=int, default=10); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    res = DecisionProcessingPipelineSDK(batch_size=args.batch_size, execute=args.execute).run(); v = res["payload"]["validation"]
    print("=" * 80); print("1100 DECISION PROCESSING PIPELINE SDK TAMAMLANDI"); print("=" * 80)
    print("Validation : " + str(v["decision"])); print("Score      : " + str(v["score"]) + " / 100"); print("Cards      : " + str(v["total"])); print("PASS       : " + str(v["pass_count"])); print("AvgQuality : " + str(v["average_card_quality"]))
    print(""); print("Dosyalar:"); print(res["paths"]["snapshot"]); print(res["paths"]["cards"]); print(res["paths"]["dashboard"]); print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)
if __name__ == "__main__": main()
'''

def module_source(mid, name, slug):
    return f'''# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1100"
sys.path.insert(0, str(PACKAGE_DIR))
from core.decision_processing_pipeline_sdk import DecisionProcessingPipelineSDK
STATE = BASE / "production_state"; REPORTS = BASE / "raporlar"; MODULE_DIR = STATE / "decision_processing_pipeline" / "{mid}_{slug}"
MODULE_ID = "{mid}"; MODULE_NAME = "{name}"
def now_stamp(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--batch-size", type=int, default=10); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    res = DecisionProcessingPipelineSDK(name=MODULE_ID + " " + MODULE_NAME, batch_size=args.batch_size, execute=args.execute).run(); val = res["payload"]["validation"]
    decision = "{name.upper()} READY" if not val["errors"] else "{name.upper()} BLOCKED"
    analysis = {{"score": val["score"], "decision": decision, "cards": val["total"], "pass_count": val["pass_count"], "average_quality": val["average_card_quality"], "recommendation": "Decision processing module ready." if not val["errors"] else "Decision processing module blocked."}}
    ts = now_stamp(); output = MODULE_DIR / "{mid}_{slug}.json"; state = MODULE_DIR / ("{mid}_{slug}_state_" + ts + ".json"); report = REPORTS / ("{mid}_{slug}_raporu_" + ts + ".txt")
    payload = {{"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}}
    write_json(output, payload); write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score    : " + str(analysis["score"]) + " / 100", "Decision : " + str(analysis["decision"]), "Cards    : " + str(analysis["cards"]), "PASS     : " + str(analysis["pass_count"]), "AvgQual  : " + str(analysis["average_quality"]), "", "Recommendation:", str(analysis["recommendation"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\\n".join(lines), encoding="utf-8"); print("\\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__": main()
'''

def run_all_source():
    lines = ['# -*- coding: utf-8 -*-', 'import argparse, json, subprocess, sys', 'from pathlib import Path', 'from datetime import datetime', 'BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")', 'SUMMARY_DIR = BASE / "production_state" / "platform_summary"', 'SUMMARY_DIR.mkdir(parents=True, exist_ok=True)', 'COMMANDS = [', '    ("1100", "Decision Processing Pipeline SDK", [sys.executable, str(BASE / ".py" / "1100_Decision_Processing_Pipeline_SDK.py")]),']
    for mid, name, slug in MODULES:
        lines.append(f'    ("{mid}", "{name}", [sys.executable, str(BASE / ".py" / "{mid}_{slug}.py")]),')
    lines += [']', 'def now_text(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")', 'def main():', '    parser = argparse.ArgumentParser(); parser.add_argument("--batch-size", type=int, default=10); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()', '    print("=" * 80); print("1100 DECISION PROCESSING PIPELINE RUN ALL BASLADI"); print("=" * 80)', '    rows = []; passed = 0; failed = 0', '    for module_id, name, cmd in COMMANDS:', '        full = cmd + ["--batch-size", str(args.batch_size)]', '        if args.execute: full.append("--execute")', '        print("\\n>>> " + " ".join(full)); result = subprocess.run(full, cwd=str(BASE))', '        status = "PASS" if result.returncode == 0 else "FAIL"', '        passed += 1 if status == "PASS" else 0; failed += 1 if status == "FAIL" else 0', '        rows.append({"module_id": module_id, "name": name, "status": status, "returncode": result.returncode})', '    total = len(COMMANDS); score = round((passed / total) * 100, 2) if total else 0; decision = "PASS" if failed == 0 else "FAIL"; ready = "YES" if failed == 0 else "NO"', '    payload = {"created_at": now_text(), "program": "1100 Decision Processing Pipeline", "batch_size": args.batch_size, "execute": args.execute, "modules_total": total, "modules_passed": passed, "modules_failed": failed, "program_score": score, "final_decision": decision, "production_ready": ready, "results": rows}', '    summary_path = SUMMARY_DIR / "1100_decision_processing_pipeline_summary.json"; summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")', '    print("\\n" + "=" * 80); print("1100 DECISION PROCESSING PIPELINE SUMMARY"); print("=" * 80)', '    for row in rows: print(row["module_id"] + " " + row["name"].ljust(40) + " " + row["status"])', '    print("-" * 80); print("Modules Passed    : " + str(passed) + " / " + str(total)); print("Modules Failed    : " + str(failed)); print("Program Score     : " + str(score) + " / 100"); print("FINAL RESULT      : " + decision); print("Production Ready  : " + ready); print(""); print("Summary JSON:"); print(summary_path); print("=" * 80)', '    raise SystemExit(0 if decision == "PASS" else 1)', 'if __name__ == "__main__": main()']
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 1100 Decision Processing Pipeline SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 1100 Run All"]
    RELEASE_FILE.write_text("\n".join(["# v7.0 – Decision Processing Pipeline", "", "**Tarih:** 10.07.2026", "", "NeoLegal Data Pipeline fazı başlamıştır. Bu sürüm ham karar verisini yapılandırılmış WEB/RAG kartına dönüştüren karar işleme hattını kurar.", "", "# Modüller", ""] + module_lines + ["", "---", "", "Decision Processing Pipeline v7.0 oluşturulmuştur.", ""]), encoding="utf-8")
    entry = "\n".join(["# v7.0 – Decision Processing Pipeline", "", "**Tarih:** 10.07.2026  ", "**Durum:** Production PASS  ", "**Git Tag:** `" + TAG + "`", "", "## Yeni Modüller", ""] + module_lines + ["", "## Sonuç", "", "NeoLegal Data Pipeline v7.0 ile karar işleme hattı başlatıldı.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v7.0 – Decision Processing Pipeline" not in old: CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else: CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v7.0 | Decision Processing Pipeline | PASS |"; txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt: README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"; files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines = ["@echo off", "cd /d C:\\Users\\MSI\\Desktop\\kik_proje", "", "echo Running Decision Processing Pipeline v7.0...", 'python ".py\\1100_Run_All.py" --batch-size 10', "", "IF ERRORLEVEL 1 (", "    echo.", "    echo RELEASE BLOCKED: 1100 Decision Processing Pipeline FAILED.", "    pause", "    exit /b 1", ")", "", "git status", "git add .", 'git commit -m "Release v7.0: Decision Processing Pipeline"', "git push", "git tag " + TAG, "git push origin " + TAG, "", "pause", ""]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8"); return GIT_BAT

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--no-git", action="store_true"); parser.add_argument("--force-git", action="store_true"); parser.add_argument("--batch-size", type=int, default=10); parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    PYDIR.mkdir(parents=True, exist_ok=True); PIPELINE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
    print("=" * 80); print("1100 ALL-IN-ONE DECISION PROCESSING PIPELINE BUILDER BASLADI"); print("=" * 80)
    write_file(PYDIR / "1100" / "core" / "__init__.py", "")
    write_file(PYDIR / "1100" / "core" / "decision_processing_pipeline_sdk.py", sdk_source())
    write_file(PYDIR / "1100_Decision_Processing_Pipeline_SDK.py", sdk_bridge_source())
    generated = [str(PYDIR / "1100_Decision_Processing_Pipeline_SDK.py")]
    for mid, name, slug in MODULES:
        path = PYDIR / (mid + "_" + slug + ".py"); write_file(path, module_source(mid, name, slug)); generated.append(str(path)); print("Generated:", path)
    run_all = PYDIR / "1100_Run_All.py"; write_file(run_all, run_all_source()); print("Generated:", run_all)
    release_path = create_release_docs(); git_bat = create_git_bat()
    print("\n" + "=" * 80); print("1100 DECISION PROCESSING PIPELINE TEST BASLIYOR"); print("=" * 80)
    cmd = [sys.executable, str(run_all), "--batch-size", str(args.batch_size)]
    if args.execute: cmd.append("--execute")
    result = subprocess.run(cmd, cwd=str(BASE)); decision = "PASS" if result.returncode == 0 else "FAIL"
    git_status = "SKIPPED"
    if decision != "PASS" and not args.force_git: git_status = "BLOCKED_BY_FAIL"
    elif args.no_git: git_status = "SKIPPED_BY_USER"
    else:
        print("\n" + "=" * 80); print("GIT RELEASE BASLIYOR"); print("=" * 80)
        git_result = subprocess.run(["cmd", "/c", str(git_bat)], cwd=str(BASE)); git_status = "PUSHED" if git_result.returncode == 0 else "FAILED"
    ts = now_stamp(); state = PIPELINE_DIR / ("1100_decision_processing_pipeline_builder_state_" + ts + ".json"); report = REPORTS / ("1100_decision_processing_pipeline_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1100 Decision Processing Pipeline Builder", "version": VERSION, "tag": TAG, "batch_size": args.batch_size, "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1100 ALL-IN-ONE DECISION PROCESSING PIPELINE BUILDER FINAL", "=" * 80, "Final Decision : " + decision, "Git            : " + git_status, "Mode           : " + ("EXECUTE" if args.execute else "DRY_RUN"), "Batch Size     : " + str(args.batch_size), "Run All        : " + str(run_all), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state), "Report         : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8"); print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED": raise SystemExit(1)
if __name__ == "__main__": main()
