from core.sdk import NeolegalKernelSDK
from core.config import STATE_DIR, REPORT_DIR, NEOLEGAL_KERNEL_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json
MODULE_DIR = NEOLEGAL_KERNEL_DIR / "305_3_neolegal_kernel_policy_engine"
OUTPUT_FILE = MODULE_DIR / "305_3_neolegal_kernel_policy_engine.json"

class NeolegalKernelPolicyEngineModule:
    def __init__(self): self.sdk=NeolegalKernelSDK(name="305.3 NeoLegal Kernel Policy Engine")
    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR); ts=now_stamp(); sdk_result=self.sdk.run(); context=sdk_result['payload']['context']; plan=sdk_result['payload']['plan']; validation=sdk_result['payload']['validation']
        result={'score':validation['score'],'decision':'NEOLEGAL KERNEL POLICY ENGINE READY' if not validation['errors'] else 'NEOLEGAL KERNEL POLICY ENGINE REVIEW','risk':context.get('risk'),'recommendation':plan.get('message')}
        payload={'module':'305.3 NeoLegal Kernel Policy Engine','created_at':now_text(),'analysis':{'context':context,'plan':plan},'result':result,'sdk_reference':sdk_result['paths']}
        state=STATE_DIR/f'305_3_neolegal_kernel_policy_engine_state_{ts}.json'; report=REPORT_DIR/f'305_3_neolegal_kernel_policy_engine_raporu_{ts}.txt'
        write_json(OUTPUT_FILE,payload); write_json(state,payload)
        lines=['='*80,'305.3 NeoLegal Kernel Policy Engine'.upper(),'='*80,'Score    : '+str(result['score'])+' / 100','Decision : '+str(result['decision']),'Risk     : '+str(result['risk']),'','Recommendation:',str(result['recommendation']),'','Dosyalar:',str(OUTPUT_FILE),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'result':result,'paths':{'output':str(OUTPUT_FILE),'state':str(state),'report':str(report)}}
