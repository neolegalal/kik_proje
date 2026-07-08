from core.sdk import LargeScaleProductionSDK
from core.config import STATE_DIR, REPORT_DIR, LARGE_SCALE_PRODUCTION_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json
MODULE_DIR = LARGE_SCALE_PRODUCTION_DIR / "217_10_production_completion_manager"
OUTPUT_FILE = MODULE_DIR / "217_10_production_completion_manager.json"
class ProductionCompletionManagerModule:
    def __init__(self): self.sdk=LargeScaleProductionSDK(name='217.10 Production Completion Manager')
    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR); ts=now_stamp(); sdk_result=self.sdk.run(); context=sdk_result['payload']['context']; plan=sdk_result['payload']['plan']; validation=sdk_result['payload']['validation']
        result={'score':validation['score'],'decision':'PRODUCTION COMPLETION MANAGER READY' if not validation['errors'] else 'PRODUCTION COMPLETION MANAGER REVIEW','risk':context.get('risk'),'recommendation':plan.get('message')}
        payload={'module':'217.10 Production Completion Manager','created_at':now_text(),'analysis':{'context':context,'plan':plan},'result':result,'sdk_reference':sdk_result['paths']}
        state=STATE_DIR/f'217_10_production_completion_manager_state_{ts}.json'; report=REPORT_DIR/f'217_10_production_completion_manager_raporu_{ts}.txt'
        write_json(OUTPUT_FILE,payload); write_json(state,payload)
        lines=['='*80,'217.10 Production Completion Manager'.upper(),'='*80,'Score    : '+str(result['score'])+' / 100','Decision : '+str(result['decision']),'Risk     : '+str(result['risk']),'','Recommendation:',str(result['recommendation']),'','Dosyalar:',str(OUTPUT_FILE),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'result':result,'paths':{'output':str(OUTPUT_FILE),'state':str(state),'report':str(report)}}
