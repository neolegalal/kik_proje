# -*- coding: utf-8 -*-
import json, subprocess, sys
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY_DIR = BASE / "production_state" / "platform_summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
COMMANDS = [
    ("400", "Production OS SDK", [sys.executable, str(BASE / ".py" / "400_Production_OS_SDK.py")]),
    ("401", "Production Console", [sys.executable, str(BASE / ".py" / "401_production_console.py")]),
    ("402", "Production Launcher", [sys.executable, str(BASE / ".py" / "402_production_launcher.py")]),
    ("403", "Configuration Center", [sys.executable, str(BASE / ".py" / "403_configuration_center.py")]),
    ("404", "Production Monitor", [sys.executable, str(BASE / ".py" / "404_production_monitor.py")]),
    ("405", "Production Dashboard", [sys.executable, str(BASE / ".py" / "405_production_dashboard.py")]),
    ("406", "Production API", [sys.executable, str(BASE / ".py" / "406_production_api.py")]),
    ("407", "Production CLI", [sys.executable, str(BASE / ".py" / "407_production_cli.py")]),
    ("408", "Production Installer", [sys.executable, str(BASE / ".py" / "408_production_installer.py")]),
    ("409", "Auto Updater", [sys.executable, str(BASE / ".py" / "409_auto_updater.py")]),
    ("410", "Production Manager", [sys.executable, str(BASE / ".py" / "410_production_manager.py")]),
]
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
    print('='*80); print('400 NEOLEGAL PRODUCTION OS RUN ALL BASLADI'); print('='*80)
    rows=[]; passed=0; failed=0
    for module_id, name, cmd in COMMANDS:
        print('\n>>> ' + ' '.join(cmd))
        result = subprocess.run(cmd, cwd=str(BASE))
        status = 'PASS' if result.returncode == 0 else 'FAIL'
        if status == 'PASS': passed += 1
        else: failed += 1
        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})
    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'
    payload={'created_at':now_text(),'program':'400 NeoLegal Production OS','modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}
    summary_path=SUMMARY_DIR/'400_production_os_summary.json'
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print('\n'+'='*80); print('400 NEOLEGAL PRODUCTION OS SUMMARY'); print('='*80)
    for row in rows: print(row['module_id'] + ' ' + row['name'].ljust(35) + ' ' + row['status'])
    print('-'*80); print('Modules Passed    : ' + str(passed) + ' / ' + str(total)); print('Modules Failed    : ' + str(failed)); print('Program Score     : ' + str(score) + ' / 100'); print('FINAL RESULT      : ' + decision); print('Production Ready  : ' + ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)
    raise SystemExit(0 if decision == 'PASS' else 1)
if __name__ == '__main__': main()
