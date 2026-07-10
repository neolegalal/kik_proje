# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "801"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_safety_gate_sdk import ProductionSafetyGateSDK
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); args=parser.parse_args()
    res=ProductionSafetyGateSDK(batch_size=args.batch_size).run(); f=res['payload']['final']
    print('='*80); print('801 PRODUCTION SAFETY GATE SDK TAMAMLANDI'); print('='*80)
    print('Safety Score : '+str(f['score'])+' / 100'); print('FINAL        : '+str(f['decision'])); print('Ready        : '+str(f['production_ready'])); print('Warnings     : '+str(f['warnings']))
    print(''); print('Dosyalar:'); print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])
    raise SystemExit(1 if f['decision']=='FAIL' else 0)
if __name__=='__main__': main()
