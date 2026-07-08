# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
OS_DIR = STATE / "production_os"
SUMMARY_DIR = STATE / "platform_summary"
SOURCE_CHECKS = [('310_maturity', 'platform_maturity'), ('311_320_readiness', 'production_readiness'), ('platform_summary', 'platform_summary'), ('runtime', 'neolegal_ai_runtime'), ('api_gateway', 'neolegal_api_gateway'), ('kernel', 'neolegal_kernel'), ('enterprise_services', 'neolegal_enterprise_services')]

def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def safe_read(path):
    path = Path(path)
    if not path.exists(): return ''
    for enc in ('utf-8','utf-8-sig','cp1254','latin-1'):
        try: return path.read_text(encoding=enc, errors='ignore')
        except Exception: pass
    return ''
def safe_json(path):
    try: return json.loads(safe_read(path))
    except Exception: return None
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

class ProductionOSSDK:
    def __init__(self, name='400 Production OS SDK'):
        self.name = name
    def discover_sources(self):
        rows = []
        for key, folder in SOURCE_CHECKS:
            folder_path = STATE / folder
            exists = folder_path.exists()
            file_count = 0
            json_count = 0
            if exists:
                files = [i for i in folder_path.glob('**/*') if i.is_file()]
                file_count = len(files)
                json_count = len([i for i in files if i.suffix.lower() == '.json'])
            rows.append({'key': key, 'folder': str(folder_path), 'exists': exists, 'file_count': file_count, 'json_count': json_count})
        return rows
    def validate(self, sources):
        found = sum(1 for i in sources if i['exists'])
        total = len(sources)
        score = round((found / total) * 100, 2) if total else 100
        errors = []
        warnings = []
        if score < 60: errors.append('Production OS kaynaklarının çoğu bulunamadı.')
        elif score < 85: warnings.append('Bazı Production OS kaynakları eksik.')
        decision = 'PRODUCTION OS CONTEXT READY' if not errors else 'PRODUCTION OS CONTEXT BLOCKED'
        return {'score': score, 'decision': decision, 'errors': errors, 'warnings': warnings}
    def plan(self, sources, validation):
        operations = []
        for source in sources:
            operations.append({'operation': 'BIND_' + source['key'].upper(), 'status': 'READY' if source['exists'] else 'MISSING', 'file_count': source['file_count'], 'json_count': source['json_count']})
        mode = 'PRODUCTION_OS_CONTROLLED' if not validation['errors'] else 'PAUSED'
        return {'mode': mode, 'operations': operations, 'message': str(len(operations)) + ' Production OS binding planned.'}
    def run(self):
        OS_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        sources = self.discover_sources()
        validation = self.validate(sources)
        plan = self.plan(sources, validation)
        payload = {'module': self.name, 'created_at': now_text(), 'sources': sources, 'validation': validation, 'plan': plan}
        ts = now_stamp()
        snapshot = OS_DIR / '400_production_os_snapshot.json'
        dashboard = OS_DIR / '400_production_os_dashboard.json'
        state = OS_DIR / ('400_production_os_state_' + ts + '.json')
        report = REPORTS / ('400_production_os_sdk_raporu_' + ts + '.txt')
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {'status': validation['decision'], 'score': validation['score'], 'mode': plan['mode'], 'operation_count': len(plan['operations']), 'errors': len(validation['errors']), 'warnings': len(validation['warnings'])})
        lines = ['='*80, '400 PRODUCTION OS SDK', '='*80, 'Validation : ' + str(validation['decision']), 'Score      : ' + str(validation['score']) + ' / 100', 'Mode       : ' + str(plan['mode']), 'Operations : ' + str(len(plan['operations'])), '', 'Dosyalar:', str(snapshot), str(dashboard), str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload': payload, 'paths': {'snapshot': str(snapshot), 'dashboard': str(dashboard), 'state': str(state), 'report': str(report)}}
