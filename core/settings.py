
import json
from core.config import SETTINGS_PATH
DEFAULTS = {
  'volume': 100,
  'mute': False,
  'resolution': [1280, 720],
  'fps': 60,
  'difficulty': 'normal',
  'language': 'en-US',
  'show_missing': False,
}

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
            out = DEFAULTS.copy()
            out.update({k: v for k, v in data.items()})
            return out
        except Exception:
            pass
    save_settings(DEFAULTS)
    return DEFAULTS.copy()

def save_settings(data: dict):
    SETTINGS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
