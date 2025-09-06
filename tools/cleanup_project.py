# tools/cleanup_project.py
"""
Project cleanup helper.
- Remove empty directories.
- Handle duplicate modules (prefers systems/inventory.py over gameplay/inventory.py).
Usage:
  python tools/cleanup_project.py --dry-run
  python tools/cleanup_project.py --apply
"""
from pathlib import Path
import shutil, sys

APPLY = '--apply' in sys.argv
BASE = Path(__file__).resolve().parents[1]

# 1) Remove empty directories (depth-first)
removed_dirs = []
for d in sorted([p for p in BASE.rglob('*') if p.is_dir()], key=lambda p: len(p.parts), reverse=True):
    try:
        if not any(d.iterdir()):
            if APPLY:
                d.rmdir()
            removed_dirs.append(d)
    except Exception:
        pass

# 2) Duplicates: prefer systems/inventory.py over gameplay/inventory.py
kept = []; deleted = []
keep = BASE / 'systems' / 'inventory.py'
dupe = BASE / 'gameplay' / 'inventory.py'
if keep.exists() and dupe.exists():
    if APPLY:
        dupe.unlink(missing_ok=True)
    deleted.append(dupe)
    kept.append(keep)

print('CLEANUP SUMMARY')
print('----------------')
print(f"Removed empty dirs: {len(removed_dirs)}")
for p in removed_dirs:
    print('  -', p)
print(f"Deleted duplicates: {len(deleted)}")
for p in deleted:
    print('  -', p)
if kept:
    print('Kept canonical:')
    for p in kept:
        print('  -', p)
print('\nRun with --apply to make changes; default is dry-run.')
