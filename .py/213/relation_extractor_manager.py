import argparse
from modules.relation_extractor.engine import RelationExtractorModule
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()
    res=RelationExtractorModule().run(); r=res['result']
    print('='*80); print('213.2 Relation Extractor'.upper()+' TAMAMLANDI'); print('='*80)
    print('Score    : '+str(r['score'])+' / 100'); print('Decision : '+str(r['decision'])); print('Risk     : '+str(r['risk'])); print(''); print('Recommendation:'); print(r['recommendation']); print(''); print('Dosyalar:'); print(res['paths']['output']); print(res['paths']['report'])
if __name__=='__main__': main()
