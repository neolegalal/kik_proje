# -*- coding: utf-8 -*-
import sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "500"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_data_factory_sdk import ProductionDataFactorySDK
def main():
    res=ProductionDataFactorySDK().run(); v=res['payload']['validation']; p=res['payload']['plan']
    print('='*80); print('500 PRODUCTION DATA FACTORY SDK TAMAMLANDI'); print('='*80)
    print('Validation : '+str(v['decision']))
    print('Score      : '+str(v['score'])+' / 100')
    print('Errors     : '+str(len(v['errors'])))
    print('Warnings   : '+str(len(v['warnings'])))
    print('Mode       : '+str(p['mode']))
    print('Operations : '+str(len(p['operations'])))
    print('')
    print('Dosyalar:')
    print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])
if __name__=='__main__': main()
