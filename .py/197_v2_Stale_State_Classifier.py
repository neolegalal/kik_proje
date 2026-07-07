# -*- coding: utf-8 -*-
r"""
197 v2 - Stale State Classifier

Amaç:
- production_state içindeki state dosyalarını sınıflandırmak.
- Eski (stale), aktif (active) ve inceleme gerektiren (review) kayıtları ayırmak.
- Hiçbir dosyayı silmez.
"""

from pathlib import Path
from datetime import datetime, timedelta
import json

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
STATE = BASE / "production_state"
REPORT = BASE / "raporlar"
REPORT.mkdir(exist_ok=True)

cutoff = datetime.now() - timedelta(days=2)

summary = {
    "active": [],
    "stale": [],
    "review": []
}

for f in sorted(STATE.glob("*")):
    if not f.is_file():
        continue
    try:
        m = datetime.fromtimestamp(f.stat().st_mtime)
        rec = {"file": str(f), "modified": m.isoformat()}
        if m < cutoff:
            summary["stale"].append(rec)
        else:
            txt = ""
            if f.suffix.lower()==".json":
                try:
                    txt = f.read_text(encoding="utf-8", errors="ignore").lower()
                except:
                    pass
            if "running" in txt:
                summary["review"].append(rec)
            else:
                summary["active"].append(rec)
    except Exception:
        pass

out = REPORT / f"197_v2_stale_state_classifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
lines = []
lines.append("="*70)
lines.append("197 v2 STALE STATE CLASSIFIER")
lines.append("="*70)
lines.append(f"Active : {len(summary['active'])}")
lines.append(f"Stale  : {len(summary['stale'])}")
lines.append(f"Review : {len(summary['review'])}")
lines.append("")
if summary["review"]:
    lines.append("REVIEW FILES")
    for r in summary["review"][:20]:
        lines.append(r["file"])
if summary["stale"]:
    lines.append("")
    lines.append("STALE FILES (ilk 20)")
    for r in summary["stale"][:20]:
        lines.append(r["file"])
out.write_text("\n".join(lines), encoding="utf-8")
print("="*70)
print("197 v2 STALE STATE CLASSIFIER TAMAMLANDI")
print(f"Active : {len(summary['active'])}")
print(f"Stale  : {len(summary['stale'])}")
print(f"Review : {len(summary['review'])}")
print()
print(out)
