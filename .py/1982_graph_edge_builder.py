# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1970_1990"
sys.path.insert(0, str(PACKAGE_DIR))
from core.case_graph_trainer_sdk import CaseGraphTrainerSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "case_graph_trainer" / "1982_graph_edge_builder"
MODULE_ID = "1982"
MODULE_NAME = "Graph Edge Builder"
def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-record", default=None)
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = CaseGraphTrainerSDK(name=MODULE_ID + " " + MODULE_NAME, master_record_path=args.master_record, case_text=args.case_text, execute=args.execute).run()
    val = res["payload"]["validation"]
    ci = res["payload"]["case_intelligence"]
    graph = res["payload"]["legal_graph"]
    ds = res["payload"]["ai_datasets"]
    audit = res["payload"]["audit"]
    decision = "GRAPH EDGE BUILDER READY" if not val["errors"] else "GRAPH EDGE BUILDER BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "main_issue": ci["main_issue"]["topic"] if ci.get("main_issue") else None, "topics": ci["topic_count"], "graph_nodes": graph["node_count"], "rag_chunks": ds["counts"]["rag"], "audit": audit["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "1982_graph_edge_builder.json"
    state = MODULE_DIR / ("1982_graph_edge_builder_state_" + ts + ".json")
    report = REPORTS / ("1982_graph_edge_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score       : " + str(analysis["score"]) + " / 100", "Decision    : " + str(analysis["decision"]), "Main Issue  : " + str(analysis["main_issue"]), "Topics      : " + str(analysis["topics"]), "Graph Nodes : " + str(analysis["graph_nodes"]), "RAG Chunks  : " + str(analysis["rag_chunks"]), "Audit       : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
