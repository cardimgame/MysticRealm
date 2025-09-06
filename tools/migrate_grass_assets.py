# tools/migrate_grass_assets.py
"""
Move grass PNGs from assets/tiles/ground -> assets/tiles/grass and report actions.
Usage: python tools/migrate_grass_assets.py [--apply]
"""
from pathlib import Path
import shutil, sys

BASE = Path(__file__).resolve().parents[1]
SRC = BASE / 'assets' / 'tiles' / 'ground'
DST = BASE / 'assets' / 'tiles' / 'grass'

APPLY = '--apply' in sys.argv

moved = []
DST.mkdir(parents=True, exist_ok=True)
if SRC.exists():
    for p in sorted(SRC.glob('grass_*.png')):
        target = DST / p.name
        if APPLY:
            shutil.move(str(p), str(target))
        moved.append((p, target))

print('[MIGRATE] grass assets:')
for src, dst in moved:
    print(('MOVE ' if APPLY else 'WILL MOVE ') + f"{src} -> {dst}")
if not moved:
    print('No grass_*.png found in assets/tiles/ground')
