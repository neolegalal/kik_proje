from core.sdk import NeolegalApiGatewaySDK
from core.config import STATE_DIR, REPORT_DIR, NEOLEGAL_API_GATEWAY_DIR
from core.utils import ensure_dirs, now_stamp, now_text, write_json
MODULE_DIR = NEOLEGAL_API_GATEWAY_DIR / "308_4_neolegal_api_gateway_planner"
OUTPUT_FILE = MODULE_DIR / "308_4_neolegal_api_gateway_planner.json"

class NeolegalApiGatewayPlannerModule:
    def __init__(self): self.sdk=NeolegalApiGatewaySDK(name="308.4 NeoLegal API Gateway Planner")
    def run(self):
        ensure_dirs(STATE_DIR, REPORT_DIR, MODULE_DIR); ts=now_stamp(); sdk_result=self.sdk.run(); context=sdk_result['payload']['context']; plan=sdk_result['payload']['plan']; validation=sdk_result['payload']['validation']
        result={'score':validation['score'],'decision':'NEOLEGAL API GATEWAY PLANNER READY' if not validation['errors'] else 'NEOLEGAL API GATEWAY PLANNER REVIEW','risk':context.get('risk'),'recommendation':plan.get('message')}
        payload={'module':'308.4 NeoLegal API Gateway Planner','created_at':now_text(),'analysis':{'context':context,'plan':plan},'result':result,'sdk_reference':sdk_result['paths']}
        state=STATE_DIR/f'308_4_neolegal_api_gateway_planner_state_{ts}.json'; report=REPORT_DIR/f'308_4_neolegal_api_gateway_planner_raporu_{ts}.txt'
        write_json(OUTPUT_FILE,payload); write_json(state,payload)
        lines=['='*80,'308.4 NeoLegal API Gateway Planner'.upper(),'='*80,'Score    : '+str(result['score'])+' / 100','Decision : '+str(result['decision']),'Risk     : '+str(result['risk']),'','Recommendation:',str(result['recommendation']),'','Dosyalar:',str(OUTPUT_FILE),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'result':result,'paths':{'output':str(OUTPUT_FILE),'state':str(state),'report':str(report)}}
