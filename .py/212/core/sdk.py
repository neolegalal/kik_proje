from .config import *
from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl
class AIOrchestratorSDK:
    def __init__(self, name='212.0 AI Orchestrator SDK'): self.name=name
    def load(self):
        return {'learning_snapshot':safe_json(LEARNING_SNAPSHOT),'learning_dashboard':safe_json(LEARNING_DASHBOARD),'healing_dashboard':safe_json(HEALING_DASHBOARD),'autonomous_dashboard':safe_json(AUTONOMOUS_DASHBOARD),'automation_dashboard':safe_json(AUTOMATION_DASHBOARD),'execution_dashboard':safe_json(EXECUTION_DASHBOARD)}
    def build_context(self, raw):
        learning=raw.get('learning_snapshot',{}) or {}; learning_dash=raw.get('learning_dashboard',{}) or {}; healing=raw.get('healing_dashboard',{}) or {}; autonomous=raw.get('autonomous_dashboard',{}) or {}; automation=raw.get('automation_dashboard',{}) or {}; execution=raw.get('execution_dashboard',{}) or {}
        validation=learning.get('validation',{}) or {}; plan=learning.get('plan',{}) or {}; patterns=plan.get('patterns',[]) or []
        risk=learning_dash.get('risk') or healing.get('risk') or autonomous.get('risk') or automation.get('risk') or execution.get('risk')
        tasks=[]
        if patterns: tasks.append({'task':'ROUTE_LEARNING_PATTERNS','weight':len(patterns)})
        if learning_dash.get('pattern_count') is not None: tasks.append({'task':'OPTIMIZE_RECOMMENDATIONS','weight':learning_dash.get('pattern_count')})
        if healing.get('action_count') is not None: tasks.append({'task':'SUPERVISE_HEALING_CONTEXT','weight':healing.get('action_count')})
        if autonomous.get('operation_count') is not None: tasks.append({'task':'ASSESS_AUTONOMOUS_CONTEXT','weight':autonomous.get('operation_count')})
        return {'created_at':now_text(),'risk':risk,'learning_score':validation.get('score'),'task_count':len(tasks),'tasks':tasks,'models':DEFAULT_MODELS,'orchestration_ready':len(tasks)>0 and risk in (None,'LOW')}
    def validate(self, context):
        errors=[]; warnings=[]
        if context.get('task_count',0)==0: warnings.append('AI orchestration için task bulunamadı.')
        if context.get('risk')=='HIGH': errors.append('Risk HIGH; AI orchestration kontrollü moda alınmalı.')
        if not context.get('orchestration_ready'): warnings.append('AI orchestration ready durumu tam değil.')
        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)
        decision='AI ORCHESTRATION CONTEXT READY' if not errors else 'AI ORCHESTRATION CONTEXT BLOCKED'
        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, context, validation):
        if validation['errors']: return {'ai_mode':'PAUSED','routes':[],'message':'AI orchestration blocked by validation errors.'}
        routes=[]
        models=context.get('models',[]) or []
        for i, task in enumerate(context.get('tasks',[])): routes.append({'task':task['task'],'model':models[i % len(models)] if models else 'DEFAULT','status':'ROUTED'})
        if not routes: routes.append({'task':'NO_AI_TASK_AVAILABLE','model':'NONE','status':'PLANNED'})
        routes.append({'task':'CONSENSUS_CHECK','model':'MULTI_MODEL','status':'PLANNED'})
        routes.append({'task':'AI_AUDIT_LOG','model':'AUDITOR','status':'PLANNED'})
        return {'ai_mode':'CONTROLLED_AI_ORCHESTRATION','routes':routes,'message':str(len(routes))+' AI orchestration route planned.'}
    def export(self,payload,name='212_0_ai_orchestrator_sdk'):
        ensure_dirs(AI_DIR, REPORT_DIR, STATE_DIR); ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'
        write_json(AI_SNAPSHOT,payload); write_json(state,payload); append_jsonl(AI_HISTORY,payload)
        dash={'ai_status':payload['validation']['decision'],'ai_mode':payload['plan']['ai_mode'],'route_count':len(payload['plan']['routes']),'risk':payload['context'].get('risk'),'task_count':payload['context'].get('task_count')}
        write_json(AI_DASHBOARD,dash)
        lines=['='*80,'212.0 AI ORCHESTRATOR SDK','='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['ai_mode']),'Routes     : '+str(len(payload['plan']['routes'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(AI_SNAPSHOT),str(AI_DASHBOARD),str(state),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'snapshot':str(AI_SNAPSHOT),'dashboard':str(AI_DASHBOARD),'state':str(state),'report':str(report)}
    def run(self):
        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation); payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}; return {'payload':payload,'paths':self.export(payload)}
