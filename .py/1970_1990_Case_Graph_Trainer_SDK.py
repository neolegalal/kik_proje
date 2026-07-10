# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1970_1990"
sys.path.insert(0, str(PACKAGE_DIR))
from core.case_graph_trainer_sdk import CaseGraphTrainerSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-record", default=None)
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = CaseGraphTrainerSDK(master_record_path=args.master_record, case_text=args.case_text, execute=args.execute).run()
    v = res["payload"]["validation"]
    ci = res["payload"]["case_intelligence"]
    graph = res["payload"]["legal_graph"]
    ds = res["payload"]["ai_datasets"]
    print("=" * 80)
    print("1970-1990 CASE GRAPH TRAINER SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation       : " + str(v["decision"]))
    print("Score            : " + str(v["score"]) + " / 100")
    print("Main Issue       : " + str(ci["main_issue"]["topic"] if ci.get("main_issue") else None))
    print("Topics           : " + str(ci["topic_count"]))
    print("Graph Nodes      : " + str(graph["node_count"]))
    print("Graph Edges      : " + str(graph["edge_count"]))
    print("RAG Chunks       : " + str(ds["counts"]["rag"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["intelligence"])
    print(res["paths"]["graph"])
    print(res["paths"]["dataset"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
