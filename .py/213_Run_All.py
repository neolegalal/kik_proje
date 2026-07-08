import subprocess, sys
from pathlib import Path
BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
COMMANDS = [
    [sys.executable, str(BASE / ".py" / "213_Knowledge_Graph_SDK.py"), "--test"],
    [sys.executable, str(BASE / ".py" / "213_1_GraphBuilder.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_2_RelationExtractor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_3_EntityResolver.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_4_KnowledgeStore.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_5_SemanticSearch.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_6_ContextBuilder.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_7_GraphDashboard.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_8_GraphDecisionEngine.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_9_GraphAuditor.py"), "--run"],
    [sys.executable, str(BASE / ".py" / "213_10_GraphOptimizer.py"), "--run"],
]
def main():
    print('='*80); print('213 KNOWLEDGE GRAPH RUN ALL BAŞLADI'); print('='*80)
    for cmd in COMMANDS:
        print('\n>>> '+' '.join(cmd)); result=subprocess.run(cmd, cwd=str(BASE))
        if result.returncode != 0: print('HATA:', ' '.join(cmd)); sys.exit(result.returncode)
    print('\n'+'='*80); print('213 KNOWLEDGE GRAPH RUN ALL TAMAMLANDI'); print('='*80)
if __name__=='__main__': main()
