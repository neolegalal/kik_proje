# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
RUNTIME_DIR = STATE / "production_factory_runtime"
SOURCE_CHECKS = [('production_os', 'production_os'), ('data_factory', 'production_data_factory'), ('readiness', 'production_readiness'), ('scheduler', 'scheduler'), ('execution', 'execution'), ('automation', 'automation'), ('self_healing', 'self_healing'), ('runtime_monitor', 'runtime_monitor'), ('platform_summary', 'platform_summary')]

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

class ProductionFactoryRuntimeSDK:
    def __init__(self, name='550 Production Factory Runtime SDK'):
        self.name = name
    def discover_sources(self):
        rows=[]
        for key, folder in SOURCE_CHECKS:
            folder_path = STATE / folder
            exists = folder_path.exists()
            files = [i for i in folder_path.glob('**/*') if i.is_file()] if exists else []
            rows.append({'key':key,'folder':str(folder_path),'exists':exists,'file_count':len(files),'json_count':len([i for i in files if i.suffix.lower()=='.json'])})
        return rows
    def discover_runtime_inputs(self):
        candidates=[]
        for p in [BASE/'kik.db', BASE/'kik_proje.db', STATE/'platform_summary'/'500_production_data_factory_summary.json', STATE/'platform_summary'/'400_production_os_summary.json']:
            candidates.append({'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0})
        return candidates
    def validate(self, sources, inputs):
        found=sum(1 for i in sources if i['exists'])
        total=len(sources)
        source_score=round((found/total)*100,2) if total else 100
        input_found=sum(1 for i in inputs if i['exists'])
        input_score=100 if input_found>=2 else 85 if input_found==1 else 70
        score=round(source_score*0.7 + input_score*0.3, 2)
        errors=[]; warnings=[]
        if source_score < 60: errors.append('Runtime kaynaklarının çoğu bulunamadı.')
        if input_found == 0: warnings.append('Runtime input bulunamadı; iskelet kurulabilir ancak gerçek üretim için input gerekli.')
        decision='PRODUCTION FACTORY RUNTIME CONTEXT READY' if not errors else 'PRODUCTION FACTORY RUNTIME CONTEXT BLOCKED'
        return {'score':score,'source_score':source_score,'input_score':input_score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, sources, inputs, validation):
        operations=[]
        for src in sources:
            operations.append({'operation':'BIND_'+src['key'].upper(),'status':'READY' if src['exists'] else 'MISSING','file_count':src['file_count'],'json_count':src['json_count']})
        operations.append({'operation':'BUILD_RUNTIME_QUEUE','status':'PLANNED'})
        operations.append({'operation':'ALLOCATE_WORKER_POOL','status':'PLANNED'})
        operations.append({'operation':'ENABLE_RESUME_RUNTIME','status':'PLANNED'})
        operations.append({'operation':'ENABLE_COST_GUARD','status':'PLANNED'})
        mode='RUNTIME_CONTROLLED' if not validation['errors'] else 'PAUSED'
        return {'mode':mode,'operations':operations,'message':str(len(operations))+' Production Factory Runtime operation planned.'}
    def run(self):
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
        sources=self.discover_sources(); inputs=self.discover_runtime_inputs(); validation=self.validate(sources, inputs); plan=self.plan(sources, inputs, validation)
        payload={'module':self.name,'created_at':now_text(),'sources':sources,'inputs':inputs,'validation':validation,'plan':plan}
        ts=now_stamp()
        snapshot=RUNTIME_DIR/'550_production_factory_runtime_snapshot.json'
        dashboard=RUNTIME_DIR/'550_production_factory_runtime_dashboard.json'
        state=RUNTIME_DIR/('550_production_factory_runtime_state_'+ts+'.json')
        report=REPORTS/('550_production_factory_runtime_sdk_raporu_'+ts+'.txt')
        write_json(snapshot,payload); write_json(state,payload)
        write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'mode':plan['mode'],'operation_count':len(plan['operations']),'errors':len(validation['errors']),'warnings':len(validation['warnings'])})
        lines=['='*80,'550 PRODUCTION FACTORY RUNTIME SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Mode       : '+str(plan['mode']),'Operations : '+str(len(plan['operations'])),'','Dosyalar:',str(snapshot),str(dashboard),str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'state':str(state),'report':str(report)}}
