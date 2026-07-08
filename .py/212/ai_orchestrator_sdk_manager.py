import argparse
from core.sdk import AIOrchestratorSDK
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--test', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()
    res=AIOrchestratorSDK().run(); v=res['payload']['validation']; p=res['payload']['plan']
    print('='*80); print('212.0 AI ORCHESTRATOR SDK TAMAMLANDI'); print('='*80)
    print('Validation : '+str(v['decision'])); print('Score      : '+str(v['score'])+' / 100'); print('Errors     : '+str(len(v['errors']))); print('Warnings   : '+str(len(v['warnings']))); print('Mode       : '+str(p['ai_mode'])); print('Routes     : '+str(len(p['routes']))); print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])
if __name__=='__main__': main()
