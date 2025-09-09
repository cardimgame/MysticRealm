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
    'scale_mode': 'fit',  # 'fit' or 'cover'
    # PostFX (HD-2D-lite)
    'fx_bloom': True,
    'fx_dof': True,
    'fx_quality': 'half',  # 'half' or 'quarter'
}

def _sanitize(data: dict) -> dict:
    out = DEFAULTS.copy(); out.update({k: v for k, v in data.items()})
    if out.get('scale_mode') not in ('fit','cover'):
        out['scale_mode'] = 'fit'
    if out.get('fx_quality') not in ('half','quarter'):
        out['fx_quality'] = 'half'
    out['fx_bloom'] = bool(out.get('fx_bloom', True))
    out['fx_dof'] = bool(out.get('fx_dof', True))
    return out

def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
            return _sanitize(data)
        except Exception:
            pass
    save_settings(DEFAULTS)
    return DEFAULTS.copy()

def save_settings(data: dict):
    SETTINGS_PATH.write_text(json.dumps(_sanitize(data), indent=2, ensure_ascii=False), encoding='utf-8')
