# -*- coding: utf-8 -*-
# 207.1-207.10 Execution Batch Builder
# NeoLegal Production Platform

from pathlib import Path
import py_compile
import sys

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "207"

sys.path.insert(0, str(PKG))
from generators.module_generator import create_module

MODULES = [
    ("207.1", "Batch Executor", "207_1_Batch_Executor.py"),
    ("207.2", "Worker Dispatcher", "207_2_Worker_Dispatcher.py"),
    ("207.3", "Queue Executor", "207_3_Queue_Executor.py"),
    ("207.4", "Retry Executor", "207_4_Retry_Executor.py"),
    ("207.5", "Recovery Executor", "207_5_Recovery_Executor.py"),
    ("207.6", "Parallel Engine", "207_6_Parallel_Engine.py"),
    ("207.7", "Pipeline Engine", "207_7_Pipeline_Engine.py"),
    ("207.8", "Execution Dashboard", "207_8_Execution_Dashboard.py"),
    ("207.9", "Execution Decision Engine", "207_9_Execution_Decision_Engine.py"),
    ("207.10", "Execution Auditor", "207_10_Execution_Auditor.py"),
]

RUN_ALL = '# -*- coding: utf-8 -*-\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nBASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")\n\nCOMMANDS = [\n    [sys.executable, str(BASE / ".py" / "207_Execution_SDK.py"), "--test"],\n    [sys.executable, str(BASE / ".py" / "207_1_Batch_Executor.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_2_Worker_Dispatcher.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_3_Queue_Executor.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_4_Retry_Executor.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_5_Recovery_Executor.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_6_Parallel_Engine.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_7_Pipeline_Engine.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_8_Execution_Dashboard.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_9_Execution_Decision_Engine.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "207_10_Execution_Auditor.py"), "--run"],\n]\n\ndef main():\n    print("=" * 80)\n    print("207 EXECUTION RUN ALL BAŞLADI")\n    print("=" * 80)\n\n    for cmd in COMMANDS:\n        print("\\n>>> " + " ".join(cmd))\n        result = subprocess.run(cmd, cwd=str(BASE))\n        if result.returncode != 0:\n            print("HATA:", " ".join(cmd))\n            sys.exit(result.returncode)\n\n    print("\\n" + "=" * 80)\n    print("207 EXECUTION RUN ALL TAMAMLANDI")\n    print("=" * 80)\n\nif __name__ == "__main__":\n    main()\n'

def main():
    if not (PKG / "core").exists():
        raise SystemExit("207 Execution SDK bulunamadı. Önce 207_0_Execution_SDK_Installer.py çalıştırılmalı.")
    if not (PKG / "generators" / "module_generator.py").exists():
        raise SystemExit("207 Module Generator bulunamadı. Önce 207_0_Module_Generator_Installer.py çalıştırılmalı.")

    results = []
    for module_id, name, bridge in MODULES:
        res = create_module(module_id, name, bridge_name=bridge, overwrite=True)
        results.append(res["payload"])

    run_all_path = PY / "207_Run_All.py"
    run_all_path.write_text(RUN_ALL, encoding="utf-8")
    py_compile.compile(str(run_all_path), doraise=True)

    errors = []
    for r in results:
        errors.extend(r.get("errors", []))

    print("=" * 80)
    print("207.1-207.10 EXECUTION BATCH BUILDER TAMAMLANDI")
    print("=" * 80)
    print("Üretilen modül sayısı :", len(results))
    print("Errors               :", len(errors))
    print("Run All              :", run_all_path)
    print("")
    print("Modüller:")
    for r in results:
        print("- " + r["target_module"] + " -> " + r["decision"])
    print("")
    print("Şimdi çalıştır:")
    print(r'python ".py\207_Run_All.py"')

if __name__ == "__main__":
    main()
