# -*- coding: utf-8 -*-
# 206.1-206.9 Scheduler Batch Builder
# NeoLegal Production Platform

from pathlib import Path
import py_compile
import sys

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
PKG = PY / "206"

sys.path.insert(0, str(PKG))
from generators.module_generator import create_module

MODULES = [
    ("206.1", "Scheduler Engine", "206_1_Scheduler_Engine.py"),
    ("206.2", "Job Planner", "206_2_Job_Planner.py"),
    ("206.3", "Priority Queue", "206_3_Priority_Queue.py"),
    ("206.4", "Dependency Resolver", "206_4_Dependency_Resolver.py"),
    ("206.5", "Retry Scheduler", "206_5_Retry_Scheduler.py"),
    ("206.6", "Cron Manager", "206_6_Cron_Manager.py"),
    ("206.7", "Batch Planner", "206_7_Batch_Planner.py"),
    ("206.8", "Scheduler Dashboard", "206_8_Scheduler_Dashboard.py"),
    ("206.9", "Scheduler Decision Engine", "206_9_Scheduler_Decision_Engine.py"),
]

RUN_ALL = '# -*- coding: utf-8 -*-\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nBASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")\n\nCOMMANDS = [\n    [sys.executable, str(BASE / ".py" / "206_Scheduler_SDK.py"), "--test"],\n    [sys.executable, str(BASE / ".py" / "206_1_Scheduler_Engine.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_2_Job_Planner.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_3_Priority_Queue.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_4_Dependency_Resolver.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_5_Retry_Scheduler.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_6_Cron_Manager.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_7_Batch_Planner.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_8_Scheduler_Dashboard.py"), "--run"],\n    [sys.executable, str(BASE / ".py" / "206_9_Scheduler_Decision_Engine.py"), "--run"],\n]\n\ndef main():\n    print("=" * 80)\n    print("206 SCHEDULER RUN ALL BAŞLADI")\n    print("=" * 80)\n\n    for cmd in COMMANDS:\n        print("\\n>>> " + " ".join(cmd))\n        result = subprocess.run(cmd, cwd=str(BASE))\n        if result.returncode != 0:\n            print("HATA:", " ".join(cmd))\n            sys.exit(result.returncode)\n\n    print("\\n" + "=" * 80)\n    print("206 SCHEDULER RUN ALL TAMAMLANDI")\n    print("=" * 80)\n\nif __name__ == "__main__":\n    main()\n'

def main():
    if not (PKG / "core").exists():
        raise SystemExit("206 Scheduler SDK bulunamadı. Önce 206_0_Scheduler_SDK_Installer.py çalıştırılmalı.")
    if not (PKG / "generators" / "module_generator.py").exists():
        raise SystemExit("206 Module Generator bulunamadı. Önce 206_0_Module_Generator_Installer.py çalıştırılmalı.")

    results = []
    for module_id, name, bridge in MODULES:
        res = create_module(module_id, name, bridge_name=bridge, overwrite=True)
        results.append(res["payload"])

    run_all_path = PY / "206_Run_All.py"
    run_all_path.write_text(RUN_ALL, encoding="utf-8")
    py_compile.compile(str(run_all_path), doraise=True)

    errors = []
    for r in results:
        errors.extend(r.get("errors", []))

    print("=" * 80)
    print("206.1-206.9 SCHEDULER BATCH BUILDER TAMAMLANDI")
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
    print(r'python ".py\206_Run_All.py"')

if __name__ == "__main__":
    main()
