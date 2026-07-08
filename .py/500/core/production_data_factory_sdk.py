# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
FACTORY_DIR = STATE / "production_data_factory"
SUMMARY_DIR = STATE / "platform_summary"
SOURCE_CHECKS = [('production_os', 'production_os'), ('production_readiness', 'production_readiness'), ('platform_summary', 'platform_summary'), ('scheduler', 'scheduler'), ('execution', 'execution'), ('automation', 'automation'), ('self_healing', 'self_healing'), ('learning', 'learning'), ('ai_orchestrator', 'ai_orchestrator')]

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

class ProductionDataFactorySDK:
    def __init__(self, name='500 Production Data Factory SDK'):
        self.name = name
    def discover_sources(self):
        rows = []
        for key, folder in SOURCE_CHECKS:
            folder_path = STATE / folder
            exists = folder_path.exists()
            files = [i for i in folder_path.glob('**/*') if i.is_file()] if exists else []
            rows.append({'key': key, 'folder': str(folder_path), 'exists': exists, 'file_count': len(files), 'json_count': len([i for i in files if i.suffix.lower()=='.json'])})
        return rows
    def discover_db(self):
        candidates = []
        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):
            p = BASE / name
            candidates.append({'path': str(p), 'exists': p.exists(), 'size_bytes': p.stat().st_size if p.exists() else 0})
        return candidates
    def validate(self, sources, dbs):
        found = sum(1 for i in sources if i['exists'])
        total = len(sources)
        source_score = round((found/total)*100,2) if total else 100
        db_found = any(i['exists'] for i in dbs)
        db_score = 100 if db_found else 70
        score = round(source_score*0.75 + db_score*0.25, 2)
        errors=[]; warnings=[]
        if source_score < 60: errors.append('Data Factory kaynaklarının çoğu bulunamadı.')
        if not db_found: warnings.append('Ana DB dosyası bulunamadı; ancak factory iskeleti kurulabilir.')
        decision = 'PRODUCTION DATA FACTORY CONTEXT READY' if not errors else 'PRODUCTION DATA FACTORY CONTEXT BLOCKED'
        return {'score':score,'source_score':source_score,'db_score':db_score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, sources, dbs, validation):
        operations=[]
        for source in sources:
            operations.append({'operation':'BIND_'+source['key'].upper(),'status':'READY' if source['exists'] else 'MISSING','file_count':source['file_count'],'json_count':source['json_count']})
        operations.append({'operation':'DISCOVER_DECISION_DATABASE','status':'READY' if any(i['exists'] for i in dbs) else 'OPTIONAL_MISSING'})
        operations.append({'operation':'PLAN_100K_PRODUCTION','status':'PLANNED'})
        mode='DATA_FACTORY_CONTROLLED' if not validation['errors'] else 'PAUSED'
        return {'mode':mode,'operations':operations,'message':str(len(operations))+' Data Factory operation planned.'}
    def run(self):
        FACTORY_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        sources=self.discover_sources(); dbs=self.discover_db(); validation=self.validate(sources, dbs); plan=self.plan(sources, dbs, validation)
        payload={'module':self.name,'created_at':now_text(),'sources':sources,'databases':dbs,'validation':validation,'plan':plan}
        ts=now_stamp()
        snapshot=FACTORY_DIR/'500_production_data_factory_snapshot.json'
        dashboard=FACTORY_DIR/'500_production_data_factory_dashboard.json'
        state=FACTORY_DIR/('500_production_data_factory_state_'+ts+'.json')
        report=REPORTS/('500_production_data_factory_sdk_raporu_'+ts+'.txt')
        write_json(snapshot,payload); write_json(state,payload)
        write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'mode':plan['mode'],'operation_count':len(plan['operations']),'errors':len(validation['errors']),'warnings':len(validation['warnings'])})
        lines=['='*80,'500 PRODUCTION DATA FACTORY SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Mode       : '+str(plan['mode']),'Operations : '+str(len(plan['operations'])),'','Dosyalar:',str(snapshot),str(dashboard),str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'state':str(state),'report':str(report)}}
