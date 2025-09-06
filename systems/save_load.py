import json
from pathlib import Path

SAVES_DIR = Path('saves')
SAVES_DIR.mkdir(exist_ok=True)

def _slot_path(slot: int) -> Path:
    slot = max(1, min(3, int(slot)))
    return SAVES_DIR / f'save_{slot}.json'

def list_saves():
    return [str(_slot_path(s)) for s in (1,2,3) if _slot_path(s).exists()]

def save_game(data: dict, slot: int = 1):
    path = _slot_path(slot)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(path)

def load_game(slot_or_path):
    path = _slot_path(slot_or_path) if isinstance(slot_or_path, int) else Path(slot_or_path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None

def delete_save(slot_or_path) -> bool:
    path = _slot_path(slot_or_path) if isinstance(slot_or_path, int) else Path(slot_or_path)
    if path.exists():
        path.unlink(missing_ok=True)
        return True
    return False

def has_save_any() -> bool:
    return any(_slot_path(s).exists() for s in (1,2,3))