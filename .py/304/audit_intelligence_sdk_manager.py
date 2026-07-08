import argparse
from core.sdk import AuditIntelligenceSDK
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--test', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()
    res=AuditIntelligenceSDK().run(); v=res['payload']['validation']; p=res['payload']['plan']
    print('='*80); print('304.0 Audit Intelligence SDK TAMAMLANDI'.upper()); print('='*80)
    print('Validation : '+str(v['decision'])); print('Score      : '+str(v['score'])+' / 100'); print('Errors     : '+str(len(v['errors']))); print('Warnings   : '+str(len(v['warnings']))); print('Mode       : '+str(p['mode'])); print('Operations : '+str(len(p['operations']))); print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])
if __name__=='__main__': main()
